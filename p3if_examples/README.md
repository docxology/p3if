# P3IF Examples Package

This package provides thin orchestrator examples demonstrating flexible composition of P3IF methods for common use cases and domain-specific applications.

## Overview

The `p3if_examples` package contains practical examples of how to use P3IF's modular architecture to build sophisticated analysis workflows:

- **Cognitive Security Orchestrator**: Information pipeline protection and bias detection
- **Framework Integration Orchestrator**: Multi-framework integration and conflict resolution
- **Healthcare Domain Orchestrator**: Healthcare-specific analysis and compliance mapping

## Architecture

```
p3if_examples/
├── __init__.py                          # Package initialization
├── cognitive_security_orchestrator.py   # Information pipeline security
├── framework_integration_orchestrator.py # Multi-framework integration
└── healthcare_domain_orchestrator.py    # Healthcare domain analysis
```

## Example Orchestrators

### Cognitive Security Orchestrator

Analyzes and protects cognitive security across information pipelines:

```python
from p3if_examples import CognitiveSecurityOrchestrator

orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis("healthcare")
print(results["summary"])
```

**Key Features:**
- Information supply chain vulnerability analysis
- Cognitive bias identification and mitigation
- Manipulation risk assessment
- Protective measure design and prioritization

### Framework Integration Orchestrator

Integrates multiple existing frameworks into unified P3IF models:

```python
from p3if_examples import FrameworkIntegrationOrchestrator

orchestrator = FrameworkIntegrationOrchestrator()
results = orchestrator.execute_integration(["NIST_CSF", "ISO_27001", "COBIT"])
unified_model = results["unified_model"]
```

**Key Features:**
- Framework element mapping and translation
- Conflict identification and resolution
- Unified model creation with validation
- Cross-framework relationship analysis

### Healthcare Domain Orchestrator

Specialized orchestrator for healthcare domain analysis:

```python
from p3if_examples import HealthcareDomainOrchestrator

orchestrator = HealthcareDomainOrchestrator()
results = orchestrator.execute_healthcare_analysis("hospital")
recommendations = results["recommendations"]
```

**Key Features:**
- Healthcare data requirements analysis
- Regulatory compliance mapping (HIPAA, HITECH, GDPR)
- Privacy protection mechanism design
- Clinical workflow optimization with privacy constraints

## Usage Patterns

### Basic Orchestration

```python
# Create and execute any orchestrator
orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis()

# Access step results
supply_chain_analysis = results["step_results"]["analyze_supply_chain"]
bias_analysis = results["step_results"]["identify_biases"]
```

### Custom Orchestration

```python
# Extend existing orchestrators
class CustomOrchestrator(CognitiveSecurityOrchestrator):
    def __init__(self):
        super().__init__()
        # Add custom steps
        self.orchestrator.add_step(OrchestrationStep(
            name="custom_analysis",
            method=self._custom_analysis_method,
            outputs=["custom_results"]
        ))

    def _custom_analysis_method(self) -> Dict[str, Any]:
        # Custom analysis logic
        return {"custom_insights": "analysis_results"}
```

### Orchestrator Composition

```python
# Combine multiple orchestrators
from p3if_methods.orchestration import WorkflowEngine

engine = WorkflowEngine()
engine.register_orchestrator("security", CognitiveSecurityOrchestrator())
engine.register_orchestrator("healthcare", HealthcareDomainOrchestrator())

# Create composite workflow
composite = engine.compose_orchestrators(
    ["security", "healthcare"],
    composition_type="sequence"
)
```

## Running Examples

```bash
# Run all example orchestrators
python scripts/run_examples.py

# Run specific example
python -c "from p3if_examples import CognitiveSecurityOrchestrator; print(CognitiveSecurityOrchestrator().execute_analysis())"
```

## Extending Examples

### Adding New Orchestrators

1. Create a new orchestrator class extending the base pattern
2. Define orchestration steps with clear dependencies
3. Implement step methods with proper error handling
4. Add comprehensive docstrings and examples
5. Include unit tests

### Example Template

```python
@dataclass
class NewDomainOrchestrator:
    """Thin orchestrator for new domain analysis."""

    name: str = "new_domain_orchestrator"
    orchestrator: ThinOrchestrator = field(init=False)

    def __post_init__(self):
        self.orchestrator = ThinOrchestrator(self.name, OrchestratorType.LINEAR)
        self._setup_orchestrator()

    def _setup_orchestrator(self):
        # Define orchestration steps
        pass

    def execute_analysis(self, context: str = "default") -> Dict[str, Any]:
        # Execute analysis and return results
        pass
```

## Testing

```bash
# Run example tests
python -m pytest p3if_tests/test_examples.py -v

# Test specific orchestrator
python -c "
from p3if_examples import CognitiveSecurityOrchestrator
orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis()
assert 'summary' in results
print('All tests passed!')
"
```

## Integration with Core P3IF

Examples integrate seamlessly with core P3IF components:

- Use `P3IFFramework` for data management
- Leverage `CompositionEngine` for framework integration
- Utilize `ValidationEngine` for result validation
- Apply `CacheManager` for performance optimization

## Best Practices

### Orchestration Design
1. Keep orchestrators thin and focused
2. Use clear, descriptive step names
3. Define explicit dependencies between steps
4. Include comprehensive error handling
5. Document expected inputs and outputs

### Error Handling
1. Implement graceful failure recovery
2. Provide meaningful error messages
3. Log important events and decisions
4. Include rollback capabilities when needed

### Performance
1. Use caching for expensive operations
2. Implement async processing for I/O operations
3. Monitor resource usage
4. Optimize for large datasets

## Contributing

When adding new examples:

1. Follow the established thin orchestrator pattern
2. Include comprehensive docstrings and usage examples
3. Add unit tests covering all functionality
4. Update this README with new example descriptions
5. Ensure backward compatibility

See the [main contribution guidelines](../CONTRIBUTING.md) for more details.

