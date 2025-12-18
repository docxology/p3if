# P3IF Orchestrators

Thin orchestrator implementations demonstrating flexible composition patterns for the P3IF framework.

## Available Orchestrators

### Cognitive Security Orchestrator
Secure information processing workflows with risk assessment and compliance monitoring.

```python
from p3if.orchestrators.cognitive_security import CognitiveSecurityOrchestrator

orchestrator = CognitiveSecurityOrchestrator()
result = orchestrator.analyze_information_pipeline(data_pipeline)
```

### Framework Integration Orchestrator
Combine multiple frameworks with conflict resolution and seamless integration.

```python
from p3if.orchestrators.framework_integration import FrameworkIntegrationOrchestrator

orchestrator = FrameworkIntegrationOrchestrator()
result = orchestrator.integrate_frameworks([framework1, framework2])
```

### Healthcare Domain Orchestrator
Medical domain workflows with patient data management and regulatory compliance.

```python
from p3if.orchestrators.healthcare_domain import HealthcareDomainOrchestrator

orchestrator = HealthcareDomainOrchestrator()
result = orchestrator.process_patient_data(patient_record)
```

## Orchestrator Pattern

All orchestrators follow the thin orchestrator pattern:

1. **Setup**: Define workflow steps and dependencies
2. **Validation**: Validate inputs and prerequisites
3. **Execution**: Coordinate step execution
4. **Reporting**: Generate structured results

## Creating Custom Orchestrators

```python
from p3if.core.orchestration import ThinOrchestrator
from dataclasses import dataclass, field

@dataclass
class CustomOrchestrator:
    name: str = "custom_orchestrator"
    orchestrator: ThinOrchestrator = field(init=False)

    def __post_init__(self):
        self.orchestrator = ThinOrchestrator(self.name)
        self._setup_orchestrator()

    def _setup_orchestrator(self):
        self.orchestrator.add_step("validate", self._validate)
        self.orchestrator.add_step("process", self._process)
        self.orchestrator.add_step("report", self._report)
```

## Testing

```bash
python -m pytest tests/unit/test_orchestrators.py
```





