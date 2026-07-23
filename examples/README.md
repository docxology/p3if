# P3IF Examples

This directory contains example usage and integration demonstrations for P3IF.

## Where Examples Live

Practical examples are in the `src/p3if/orchestrators/` package:

| Module | Description |
|--------|-------------|
| `cognitive_security.py` | Cognitive security analysis orchestrator |
| `framework_integration.py` | Multi-framework integration with conflict resolution |
| `healthcare_domain.py` | Healthcare domain analysis (HIPAA, HITECH, GDPR) |
| `integration_examples.py` | NIST CSF, Healthcare, and multi-framework integration examples |

## Running Examples

```bash
# Run all example orchestrators
python scripts/run_examples.py

# Run via the master orchestrator
python scripts/run_all.py --examples
```

## Quick Start

```python
from p3if import P3IFFramework, Property, Process, Perspective

fw = P3IFFramework()
fw.add_pattern(Property(name="Security", description="Security property", domain="cybersec"))
fw.add_pattern(Process(name="Authentication", description="Auth process", domain="cybersec"))
fw.add_pattern(Perspective(name="Technical", description="Tech perspective", domain="cybersec", viewpoint="developer"))
print(f"Framework: {fw}")
```
