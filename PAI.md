# P3IF - PAI Integration Guide

Personal AI Infrastructure (PAI) integration documentation for P3IF (Properties, Processes, Perspectives Inter-Framework).

## Overview

P3IF is a meta-framework for modeling complex domain relationships through three fundamental dimensions: Properties (what things are), Processes (how things work), and Perspectives (how things are viewed). It supports thin orchestration patterns ideal for PAI workflow integration.

## Quick Integration

```python
from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective
from p3if.orchestrators import CognitiveSecurityOrchestrator

# Create and use framework
framework = P3IFFramework()
framework.add_pattern(Property(name="Security", domain="cyber"))

# Use orchestrators for domain workflows
orchestrator = CognitiveSecurityOrchestrator()
results = orchestrator.execute_analysis()
```

## PAI Skill Integration

P3IF components can be used within PAI skills for:

- **Domain Analysis**: Model relationships between concepts in any domain
- **Cognitive Security**: Analyze information pipelines for manipulation risks
- **Framework Integration**: Combine multiple compliance/governance frameworks
- **Visualization**: Generate interactive 3D visualizations of relationships

## Key Modules for PAI

| Module | Purpose | PAI Use Case |
|--------|---------|--------------|
| `p3if.core.framework` | Core P3IF operations | Domain modeling |
| `p3if.orchestrators` | Thin orchestrators | Workflow automation |
| `p3if.visualization` | Visual outputs | Report generation |
| `p3if.data.synthetic` | Test data generation | Development/testing |

## Thin Orchestrator Pattern

P3IF uses thin orchestrators compatible with PAI's delegation workflow:

```python
from p3if.core.orchestration import ThinOrchestrator, OrchestratorType

# Create custom orchestrator
orchestrator = ThinOrchestrator("my_analysis", OrchestratorType.LINEAR)
orchestrator.add_step("load_data", load_function)
orchestrator.add_step("analyze", analyze_function, dependencies=["load_data"])
results = await orchestrator.execute_async()
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/p3if --cov-report=html
```

## File Structure

```
src/p3if/
├── core/           # Framework, models, orchestration
├── orchestrators/  # Domain-specific thin orchestrators
├── visualization/  # Static, interactive, animated visualizations
├── data/           # Data management and synthetic generation
└── utils/          # Configuration, storage, performance
```

## Links

- [AGENTS.md](./AGENTS.md) - AI agent development guidelines
- [README.md](./README.md) - Full project documentation
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
