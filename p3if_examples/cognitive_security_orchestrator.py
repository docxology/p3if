"""
Cognitive Security Orchestrator

This thin orchestrator demonstrates how to analyze and protect cognitive security
across information pipelines using P3IF composition.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
from datetime import datetime

from p3if_methods.orchestration import ThinOrchestrator, OrchestrationStep, OrchestratorType
from p3if_methods.core import P3IFCore
from p3if_methods.composition import CompositionEngine
from p3if_methods.dimensions import PropertyManager, ProcessManager, PerspectiveManager


@dataclass
class CognitiveSecurityOrchestrator:
    """Thin orchestrator for cognitive security analysis."""

    name: str = "cognitive_security_orchestrator"
    core: P3IFCore = field(default_factory=P3IFCore)
    composition_engine: CompositionEngine = field(default_factory=CompositionEngine)
    orchestrator: ThinOrchestrator = field(init=False)

    def __post_init__(self):
        self.orchestrator = ThinOrchestrator(self.name, OrchestratorType.LINEAR)
        self._setup_orchestrator()
        self.logger = logging.getLogger(__name__)

    def _setup_orchestrator(self):
        """Set up the orchestration steps."""
        # Step 1: Analyze information supply chain
        self.orchestrator.add_step(OrchestrationStep(
            name="analyze_supply_chain",
            method=self._analyze_information_supply_chain,
            outputs=["supply_chain_analysis"],
            description="Analyze the information supply chain for cognitive vulnerabilities"
        ))

        # Step 2: Identify cognitive biases
        self.orchestrator.add_step(OrchestrationStep(
            name="identify_biases",
            method=self._identify_cognitive_biases,
            dependencies=["analyze_supply_chain"],
            outputs=["bias_analysis"],
            description="Identify potential cognitive biases in decision processes"
        ))

        # Step 3: Assess manipulation risks
        self.orchestrator.add_step(OrchestrationStep(
            name="assess_manipulation_risks",
            method=self._assess_manipulation_risks,
            dependencies=["identify_biases"],
            outputs=["manipulation_assessment"],
            description="Assess risks of information manipulation and deception"
        ))

        # Step 4: Design protective measures
        self.orchestrator.add_step(OrchestrationStep(
            name="design_protection",
            method=self._design_cognitive_protection,
            dependencies=["assess_manipulation_risks"],
            outputs=["protection_measures"],
            description="Design protective measures for cognitive security"
        ))

    def _analyze_information_supply_chain(self) -> Dict[str, Any]:
        """Analyze the information supply chain for vulnerabilities."""
        # This would analyze the flow from source to decision
        return {
            "supply_chain": {
                "source": "External data sources",
                "collection": "Data gathering processes",
                "storage": "Information repositories",
                "processing": "Analysis and transformation",
                "dissemination": "Information sharing",
                "decision": "Decision-making processes"
            },
            "vulnerability_points": [
                "Source credibility assessment",
                "Information transformation integrity",
                "Context preservation during processing",
                "Bias introduction in analysis",
                "Manipulation during dissemination"
            ]
        }

    def _identify_cognitive_biases(self, orchestrator_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Identify cognitive biases in the supply chain."""
        # Get the supply chain analysis from the orchestrator context
        supply_chain_analysis = orchestrator_context.get("supply_chain_analysis", {}) if orchestrator_context else {}

        biases = {
            "information_overload": {
                "description": "Volume of information exceeds processing capacity",
                "mitigation": "Implement information triage and prioritization"
            },
            "confirmation_bias": {
                "description": "Seeking information that confirms existing beliefs",
                "mitigation": "Require diverse perspective validation"
            },
            "anchoring_bias": {
                "description": "Over-reliance on first piece of information",
                "mitigation": "Multi-source validation requirements"
            },
            "availability_bias": {
                "description": "Judging based on most readily available information",
                "mitigation": "Systematic comprehensive search protocols"
            }
        }

        return {
            "identified_biases": biases,
            "risk_assessment": self._assess_bias_risks(biases)
        }

    def _assess_bias_risks(self, biases: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with identified biases."""
        risk_levels = {}
        for bias_name, bias_info in biases.items():
            # Simple risk assessment based on bias characteristics
            if "overload" in bias_name or "confirmation" in bias_name:
                risk_levels[bias_name] = "high"
            elif "anchoring" in bias_name or "availability" in bias_name:
                risk_levels[bias_name] = "medium"
            else:
                risk_levels[bias_name] = "low"

        return risk_levels

    def _assess_manipulation_risks(self, orchestrator_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assess risks of information manipulation."""
        # Get the bias analysis from the orchestrator context
        bias_analysis = orchestrator_context.get("bias_analysis", {}) if orchestrator_context else {}

        manipulation_risks = {
            "data_cherry_picking": {
                "risk_level": "high",
                "indicators": ["selective reporting", "omitted context", "favorable comparisons only"],
                "protective_measures": ["require full dataset access", "independent verification"]
            },
            "statistical_manipulation": {
                "risk_level": "high",
                "indicators": ["p-hacking", "inappropriate statistical tests", "selective significance"],
                "protective_measures": ["preregistered analysis plans", "statistical review requirements"]
            },
            "narrative_framing": {
                "risk_level": "medium",
                "indicators": ["loaded language", "false equivalency", "appeal to emotion"],
                "protective_measures": ["multi-perspective analysis", "bias detection algorithms"]
            }
        }

        return {
            "manipulation_risks": manipulation_risks,
            "overall_risk_level": self._calculate_overall_risk(manipulation_risks)
        }

    def _calculate_overall_risk(self, risks: Dict[str, Any]) -> str:
        """Calculate overall risk level from individual risks."""
        risk_levels = [risk["risk_level"] for risk in risks.values()]
        if "high" in risk_levels:
            return "high"
        elif "medium" in risk_levels:
            return "medium"
        else:
            return "low"

    def _design_cognitive_protection(self, orchestrator_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Design protective measures for cognitive security."""
        # Get the manipulation assessment from the orchestrator context
        manipulation_assessment = orchestrator_context.get("manipulation_assessment", {}) if orchestrator_context else {}

        protection_measures = {
            "validation_processes": [
                "Multi-source information verification",
                "Independent fact-checking protocols",
                "Bias detection algorithms",
                "Transparency requirements for data transformations"
            ],
            "decision_support": [
                "Structured decision frameworks",
                "Cognitive bias training",
                "External validation requirements",
                "Decision traceability systems"
            ],
            "monitoring_systems": [
                "Information provenance tracking",
                "Manipulation detection alerts",
                "Quality metrics for information sources",
                "Real-time bias monitoring"
            ]
        }

        return {
            "protection_measures": protection_measures,
            "implementation_priority": self._prioritize_implementation(protection_measures)
        }

    def _prioritize_implementation(self, measures: Dict[str, List[str]]) -> Dict[str, str]:
        """Prioritize implementation of protection measures."""
        priorities = {}
        for category, measure_list in measures.items():
            if "validation" in category:
                priorities[category] = "high"
            elif "monitoring" in category:
                priorities[category] = "medium"
            else:
                priorities[category] = "low"
        return priorities

    def execute_analysis(self, domain_context: str = "general") -> Dict[str, Any]:
        """Execute the cognitive security analysis."""
        self.logger.info(f"Starting cognitive security analysis for domain: {domain_context}")

        # Set domain context
        self.orchestrator.context["domain"] = domain_context

        # Execute the orchestrator
        results = self.orchestrator.execute_sync()

        # Compile final report
        final_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "domain_context": domain_context,
            "step_results": results,
            "summary": self._generate_summary(results),
            "recommendations": self._generate_recommendations(results)
        }

        self.logger.info("Cognitive security analysis completed")
        return final_report

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        return {
            "total_steps_completed": len(results),
            "risk_levels_identified": self._extract_risk_levels(results),
            "protection_measures_count": len(results.get("design_protection", {}))
        }

    def _extract_risk_levels(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Extract risk levels from results."""
        risk_levels = {}

        if "assess_manipulation_risks" in results:
            manipulation_results = results["assess_manipulation_risks"]
            if "manipulation_risks" in manipulation_results:
                for risk_name, risk_data in manipulation_results["manipulation_risks"].items():
                    risk_levels[risk_name] = risk_data.get("risk_level", "unknown")

        if "identify_biases" in results:
            bias_results = results["identify_biases"]
            if "risk_assessment" in bias_results:
                risk_levels.update(bias_results["risk_assessment"])

        return risk_levels

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Extract protection measures from results
        if "design_protection" in results:
            protection_results = results["design_protection"]
            if "protection_measures" in protection_results:
                measures = protection_results["protection_measures"]

                for category, measure_list in measures.items():
                    if category == "validation_processes":
                        recommendations.extend([
                            "Implement multi-source verification protocols",
                            "Establish independent fact-checking procedures",
                            "Deploy bias detection algorithms"
                        ])
                    elif category == "decision_support":
                        recommendations.extend([
                            "Develop structured decision frameworks",
                            "Provide cognitive bias training",
                            "Create decision traceability systems"
                        ])
                    elif category == "monitoring_systems":
                        recommendations.extend([
                            "Implement information provenance tracking",
                            "Set up manipulation detection monitoring",
                            "Establish quality metrics for information sources"
                        ])

        return recommendations
