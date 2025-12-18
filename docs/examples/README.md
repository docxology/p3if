# P3IF Examples

This directory provides documentation for P3IF examples and practical implementations.

## Available Examples

### Orchestrator Examples (`p3if_examples/`)

The main examples are implemented as thin orchestrators in the `p3if_examples/` package:

#### Cognitive Security Orchestrator
Analyzes information pipelines for cognitive security vulnerabilities:

```python
from p3if_examples.cognitive_security_orchestrator import CognitiveSecurityOrchestrator

orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis("healthcare")
```

**Features:**
- Information supply chain analysis
- Cognitive bias detection
- Manipulation risk assessment
- Protective measure design

#### Framework Integration Orchestrator
Integrates multiple frameworks into unified P3IF models:

```python
from p3if_examples.framework_integration_orchestrator import FrameworkIntegrationOrchestrator

orchestrator = FrameworkIntegrationOrchestrator()
results = orchestrator.execute_integration(["NIST_CSF", "ISO_27001", "COBIT"])
```

**Features:**
- Framework mapping and translation
- Conflict identification and resolution
- Unified model creation
- Cross-framework relationship analysis

#### Healthcare Domain Orchestrator
Healthcare-specific analysis and compliance mapping:

```python
from p3if_examples.healthcare_domain_orchestrator import HealthcareDomainOrchestrator

orchestrator = HealthcareDomainOrchestrator()
results = orchestrator.execute_healthcare_analysis("hospital")
```

**Features:**
- Healthcare data requirements analysis
- Regulatory compliance mapping (HIPAA, HITECH, GDPR)
- Privacy protection mechanisms
- Clinical workflow optimization

### Running Examples

Execute all orchestrator examples:

```bash
python scripts/run_examples.py
```

This will run all three orchestrators and validate their outputs.

## Getting Started with Examples

### Run All Examples

Execute the complete example suite:

```bash
python scripts/run_examples.py
```

This runs all orchestrators and validates their outputs.

### Individual Example Execution

Run specific orchestrators:

```bash
# Cognitive security analysis
python -c "
from p3if_examples.cognitive_security_orchestrator import CognitiveSecurityOrchestrator
orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis()
print('Cognitive security analysis completed')
"

# Framework integration
python -c "
from p3if_examples.framework_integration_orchestrator import FrameworkIntegrationOrchestrator
orchestrator = FrameworkIntegrationOrchestrator()
results = orchestrator.execute_integration(['NIST_CSF', 'ISO_27001'])
print('Framework integration completed')
"

# Healthcare domain analysis
python -c "
from p3if_examples.healthcare_domain_orchestrator import HealthcareDomainOrchestrator
orchestrator = HealthcareDomainOrchestrator()
results = orchestrator.execute_healthcare_analysis()
print('Healthcare analysis completed')
"
```

## Example Architecture

The P3IF examples follow a consistent thin orchestrator pattern:

```python
@dataclass
class ExampleOrchestrator:
    """Thin orchestrator for specific domain analysis."""

    name: str = "example_orchestrator"
    orchestrator: ThinOrchestrator = field(init=False)

    def __post_init__(self):
        self.orchestrator = ThinOrchestrator(self.name, OrchestratorType.LINEAR)
        self._setup_orchestrator()

    def _setup_orchestrator(self):
        """Define orchestration steps."""
        # Add steps with dependencies
        pass

    def execute_analysis(self, context: str = "default") -> Dict[str, Any]:
        """Execute analysis and return results."""
        return asyncio.run(self.orchestrator.execute_async())
```

## Integration with P3IF Core

Examples integrate with all P3IF components:

- **Framework**: Use `P3IFFramework` for data management
- **Analysis**: Leverage analysis tools for insights
- **Visualization**: Generate visual outputs
- **Validation**: Apply validation rules
- **Storage**: Persist results using storage interfaces

## Testing Examples

Run example validation:

```bash
# Test all examples
python -m pytest p3if_tests/ -k "orchestrator" -v

# Validate example outputs
python scripts/run_examples.py --validate
```

## Extending Examples

To create new examples:

1. Extend the base orchestrator pattern
2. Define domain-specific analysis steps
3. Include comprehensive error handling
4. Add usage documentation
5. Create unit tests

## Resources

- [Orchestrator Documentation](../../p3if_methods/orchestration.py)
- [Framework Guide](../../p3if_methods/framework.py)
- [Analysis Tools](../../p3if_methods/analysis/)
- [Visualization Examples](../../p3if_visualization/) 