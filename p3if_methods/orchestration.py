"""
P3IF Thin Orchestrators

This module provides thin orchestrators for flexible composition of P3IF methods,
enabling lightweight, reusable workflow patterns.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from abc import ABC, abstractmethod


class OrchestratorType(str, Enum):
    """Types of thin orchestrators."""
    LINEAR = "linear"
    BRANCHING = "branching"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    COMPOSITE = "composite"


@dataclass
class OrchestrationStep:
    """A single step in an orchestration."""
    name: str
    method: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    error_handling: str = "continue"  # continue, stop, retry
    description: str = ""


@dataclass
class ThinOrchestrator:
    """A thin orchestrator for flexible P3IF composition."""

    name: str
    orchestrator_type: OrchestratorType
    steps: List[OrchestrationStep] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    max_concurrent: int = 5

    def add_step(self, step: OrchestrationStep):
        """Add a step to the orchestrator."""
        self.steps.append(step)

    def add_dependency(self, step_name: str, depends_on: str):
        """Add a dependency relationship between steps."""
        for step in self.steps:
            if step.name == step_name:
                if depends_on not in step.dependencies:
                    step.dependencies.append(depends_on)
                break

    def add_output_mapping(self, step_name: str, output_name: str):
        """Add an output mapping for a step."""
        for step in self.steps:
            if step.name == step_name:
                if output_name not in step.outputs:
                    step.outputs.append(output_name)
                break

    async def execute_async(self) -> Dict[str, Any]:
        """Execute the orchestrator asynchronously."""
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.name}")

        if self.orchestrator_type == OrchestratorType.LINEAR:
            return await self._execute_linear()
        elif self.orchestrator_type == OrchestratorType.PARALLEL:
            return await self._execute_parallel()
        elif self.orchestrator_type == OrchestratorType.CONDITIONAL:
            return await self._execute_conditional()
        else:
            raise NotImplementedError(f"Orchestrator type {self.orchestrator_type} not implemented")

    def execute_sync(self) -> Dict[str, Any]:
        """Execute the orchestrator synchronously."""
        # Simple synchronous wrapper for async execution
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._run_in_new_loop)
                return future.result()
        else:
            return loop.run_until_complete(self.execute_async())

    def _run_in_new_loop(self):
        """Run the orchestrator in a new event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.execute_async())
        finally:
            loop.close()

    async def _execute_linear(self) -> Dict[str, Any]:
        """Execute steps in linear sequence."""
        results = {}
        completed_steps = set()

        for step in self.steps:
            # Check dependencies
            if not self._check_dependencies(step.dependencies, completed_steps):
                self.logger.warning(f"Skipping step {step.name} due to unmet dependencies")
                continue

            try:
                self.logger.info(f"Executing step: {step.name}")
                step_result = await self._execute_step_async(step)
                results[step.name] = step_result

                # Mark step as completed
                completed_steps.add(step.name)

                # Store outputs in context
                for output in step.outputs:
                    self.context[output] = step_result

            except Exception as e:
                self.logger.error(f"Step {step.name} failed: {e}")
                if step.error_handling == "stop":
                    raise
                elif step.error_handling == "retry":
                    # Simple retry logic
                    retry_result = await self._execute_step_async(step)
                    results[step.name] = retry_result
                    completed_steps.add(step.name)

        return results

    async def _execute_parallel(self) -> Dict[str, Any]:
        """Execute independent steps in parallel."""
        results = {}

        # Group steps by dependency level
        dependency_levels = self._build_dependency_levels()

        for level in dependency_levels:
            # Execute steps in this level concurrently
            tasks = []
            for step_name in level:
                step = next(s for s in self.steps if s.name == step_name)
                task = asyncio.create_task(self._execute_step_async(step))
                tasks.append((step_name, task))

            # Wait for all tasks in this level to complete
            for step_name, task in tasks:
                try:
                    result = await task
                    results[step_name] = result
                except Exception as e:
                    self.logger.error(f"Parallel step {step_name} failed: {e}")
                    # For parallel execution, we continue with other steps

        return results

    async def _execute_conditional(self) -> Dict[str, Any]:
        """Execute steps based on conditions."""
        results = {}

        for step in self.steps:
            # Evaluate condition
            if not self._evaluate_condition(step):
                self.logger.info(f"Skipping conditional step: {step.name}")
                continue

            try:
                result = await self._execute_step_async(step)
                results[step.name] = result
            except Exception as e:
                self.logger.error(f"Conditional step {step.name} failed: {e}")

        return results

    async def _execute_step_async(self, step: OrchestrationStep) -> Any:
        """Execute a single step asynchronously."""
        try:
            # Prepare parameters - include result from previous step if dependencies exist
            params = step.parameters.copy()

            # For steps with dependencies, pass the result from the last dependency
            if step.dependencies:
                last_dependency = step.dependencies[-1]  # Get the most recent dependency
                if last_dependency in self.context:
                    # Add the result from the previous step as the first parameter
                    # The method signature should expect this as its first parameter after 'self'
                    method_sig = step.method.__code__.co_varnames[:step.method.__code__.co_argcount]
                    if len(method_sig) > 1 and method_sig[1] not in params:  # Skip 'self' parameter
                        # Use the dependency name as the parameter name
                        result_key = method_sig[1]  # Second parameter after 'self'
                        params[result_key] = self.context[last_dependency]
                        print(f"DEBUG: Passing {last_dependency} result to {result_key}")
                    else:
                        print(f"DEBUG: Parameter {method_sig[1]} already in params or not found in method signature")

            # For methods that expect orchestrator_context, pass the entire context
            method_sig = step.method.__code__.co_varnames[:step.method.__code__.co_argcount]
            if len(method_sig) > 1 and method_sig[1] == 'orchestrator_context':
                params['orchestrator_context'] = self.context

            if asyncio.iscoroutinefunction(step.method):
                return await step.method(**params)
            else:
                # For methods that expect orchestrator_context, pass the entire context
                method_sig = step.method.__code__.co_varnames[:step.method.__code__.co_argcount]
                if len(method_sig) > 1 and method_sig[1] == 'orchestrator_context':
                    params['orchestrator_context'] = self.context

                # Create a wrapper function that accepts positional args for run_in_executor
                def execute_with_params():
                    return step.method(**params)

                return await asyncio.get_event_loop().run_in_executor(
                    None, execute_with_params
                )
        except Exception as e:
            self.logger.error(f"Step execution failed: {e}")
            raise

    def _check_dependencies(self, dependencies: List[str], completed_steps: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_steps for dep in dependencies)

    def _build_dependency_levels(self) -> List[List[str]]:
        """Build dependency levels for parallel execution."""
        levels = []
        processed = set()

        while len(processed) < len(self.steps):
            current_level = []

            for step in self.steps:
                if step.name in processed:
                    continue

                if self._check_dependencies(step.dependencies, processed):
                    current_level.append(step.name)

            if not current_level:
                # Handle circular dependencies or missing dependencies
                remaining = [s.name for s in self.steps if s.name not in processed]
                self.logger.warning(f"Could not process remaining steps: {remaining}")
                break

            levels.append(current_level)
            processed.update(current_level)

        return levels

    def _evaluate_condition(self, step: OrchestrationStep) -> bool:
        """Evaluate whether a step's condition is met."""
        # Simple condition evaluation based on context
        # In a real implementation, this would support complex expressions
        if "condition" in step.parameters:
            condition = step.parameters["condition"]
            if isinstance(condition, str):
                # Simple string-based conditions
                if condition.startswith("context."):
                    key = condition[8:]  # Remove "context." prefix
                    return self.context.get(key, False)
                elif condition == "always":
                    return True
                elif condition == "never":
                    return False

        return True  # Default to execute if no condition specified


class WorkflowEngine:
    """Advanced workflow engine for complex orchestrations."""

    def __init__(self):
        self.orchestrators: Dict[str, ThinOrchestrator] = {}
        self.global_context: Dict[str, Any] = {}

    def create_orchestrator(self, name: str,
                           orchestrator_type: OrchestratorType) -> ThinOrchestrator:
        """Create a new orchestrator."""
        orchestrator = ThinOrchestrator(name, orchestrator_type)
        self.orchestrators[name] = orchestrator
        return orchestrator

    def compose_orchestrators(self, orchestrators: List[str],
                             composition_type: str = "sequence") -> ThinOrchestrator:
        """Compose multiple orchestrators into a single workflow."""
        if composition_type == "sequence":
            # Chain orchestrators in sequence
            composite = ThinOrchestrator("composite", OrchestratorType.COMPOSITE)

            for orch_name in orchestrators:
                orchestrator = self.orchestrators[orch_name]
                for step in orchestrator.steps:
                    # Add dependency on previous orchestrator's last step
                    if composite.steps:
                        step.dependencies.append(composite.steps[-1].name)
                    composite.add_step(step)

            return composite

        elif composition_type == "parallel":
            # Run orchestrators in parallel
            composite = ThinOrchestrator("composite_parallel", OrchestratorType.PARALLEL)

            for orch_name in orchestrators:
                orchestrator = self.orchestrators[orch_name]
                for step in orchestrator.steps:
                    composite.add_step(step)

            return composite

        else:
            raise ValueError(f"Unsupported composition type: {composition_type}")


# Pre-built orchestrators for common patterns
def create_cognitive_security_orchestrator() -> ThinOrchestrator:
    """Create an orchestrator focused on cognitive security."""
    orchestrator = ThinOrchestrator("cognitive_security", OrchestratorType.LINEAR)

    # This would be implemented with actual methods
    # For now, just showing the structure
    orchestrator.add_step(OrchestrationStep(
        name="analyze_information_pipeline",
        method=lambda: None,  # Would be actual method
        description="Analyze the information supply chain for vulnerabilities"
    ))

    orchestrator.add_step(OrchestrationStep(
        name="identify_cognitive_biases",
        method=lambda: None,  # Would be actual method
        dependencies=["analyze_information_pipeline"],
        description="Identify potential cognitive biases in decision processes"
    ))

    return orchestrator


def create_framework_integration_orchestrator() -> ThinOrchestrator:
    """Create an orchestrator for integrating multiple frameworks."""
    orchestrator = ThinOrchestrator("framework_integration", OrchestratorType.LINEAR)

    orchestrator.add_step(OrchestrationStep(
        name="map_framework_elements",
        method=lambda: None,
        description="Map elements from different frameworks to P3IF dimensions"
    ))

    orchestrator.add_step(OrchestrationStep(
        name="identify_conflicts",
        method=lambda: None,
        dependencies=["map_framework_elements"],
        description="Identify conflicts and overlaps between frameworks"
    ))

    orchestrator.add_step(OrchestrationStep(
        name="create_unified_model",
        method=lambda: None,
        dependencies=["identify_conflicts"],
        description="Create unified model with resolved conflicts"
    ))

    return orchestrator
