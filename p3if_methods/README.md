# P3IF Methods Package

This package contains the core modular methods for P3IF (Properties, Processes, and Perspectives Inter-Framework) operations, organized by functionality for maximum composability and flexibility.

## Overview

The `p3if_methods` package provides the foundational components for building and working with P3IF frameworks:

- **Core functionality** for framework operations and pattern management
- **Composition methods** for integrating multiple frameworks
- **Dimension management** for Properties, Processes, and Perspectives
- **Orchestration tools** for workflow automation
- **Validation framework** for ensuring data integrity
- **Caching and performance optimization** utilities
- **Analysis tools** for pattern recognition and insights

## Architecture

```
p3if_methods/
├── core.py              # Core P3IF operations
├── composition.py       # Framework composition and integration
├── dimensions.py        # Property, Process, Perspective managers
├── orchestration.py     # Thin orchestrators and workflow engine
├── validation.py        # Validation framework and constraints
├── caching.py           # Caching and performance optimization
├── framework.py         # Main P3IFFramework class
├── models.py            # Data models and Pydantic schemas
└── analysis/            # Analysis tools
    ├── basic.py         # Basic pattern analysis
    ├── meta.py          # Meta-analysis capabilities
    ├── network.py       # Network analysis tools
    └── report.py        # Report generation
```

## Core Components

### P3IFCore
The main entry point for P3IF operations, providing pattern and relationship management.

```python
from p3if_methods.core import P3IFCore

core = P3IFCore()
pattern = core.create_pattern("property", "Security", "Cybersecurity domain")
relationship = core.create_relationship(pattern.id, process_id, perspective_id)
```

### Framework Composition
Tools for integrating multiple frameworks and managing cross-domain relationships.

```python
from p3if_methods.composition import CompositionEngine, FrameworkAdapter

engine = CompositionEngine()
adapter = FrameworkAdapter("NIST_CSF", "1.0", "NIST Cybersecurity Framework", mapping_rules)
engine.register_adapter(adapter)
```

### Dimension Management
Specialized managers for handling Properties, Processes, and Perspectives.

```python
from p3if_methods.dimensions import PropertyManager, ProcessManager, PerspectiveManager

property_manager = PropertyManager()
process_manager = ProcessManager()
perspective_manager = PerspectiveManager()
```

### Orchestration
Thin orchestrators for flexible workflow composition.

```python
from p3if_methods.orchestration import ThinOrchestrator, OrchestratorType

orchestrator = ThinOrchestrator("my_workflow", OrchestratorType.LINEAR)
orchestrator.add_step(OrchestrationStep("analyze", analyze_function))
```

## Analysis Tools

### Basic Analysis
Pattern detection, similarity analysis, and basic metrics.

### Network Analysis
Graph-based analysis of pattern relationships and connectivity.

### Meta-Analysis
Advanced analysis combining multiple analytical approaches.

### Report Generation
Comprehensive reporting and visualization of analysis results.

## Validation Framework

### ValidationEngine
Core validation system for ensuring framework integrity.

```python
from p3if_methods.validation import ValidationEngine, ValidationRule

engine = ValidationEngine()
rule = ValidationRule("name_required", lambda x: bool(x.name), "error", "Name is required")
engine.add_rule(rule)
results = engine.validate_framework(framework)
```

### ConstraintManager
Management of constraints and business rules.

## Performance Optimization

### CacheManager
LRU caching with TTL support for improved performance.

```python
from p3if_methods.caching import CacheManager, CacheStrategy

cache = CacheManager(CacheStrategy.LRU, max_size=1000, default_ttl=3600)
```

### PerformanceOptimizer
Monitoring and optimization of P3IF operations.

## Usage Examples

### Creating a Framework

```python
from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective, Relationship

# Create framework
framework = P3IFFramework()

# Add patterns
security_prop = Property(
    name="confidentiality",
    description="Data Confidentiality",
    domain="cybersecurity",
    category="security",
    priority="high"
)
encryption_proc = Process(
    name="encryption",
    description="Data Encryption",
    domain="cybersecurity",
    complexity="medium",
    automation_level="semi-automated"
)
technical_pers = Perspective(
    name="technical",
    description="Technical View",
    domain="cybersecurity",
    viewpoint="implementation",
    stakeholder_type="internal"
)

framework.add_pattern(security_prop)
framework.add_pattern(encryption_proc)
framework.add_pattern(technical_pers)

# Create relationships
relationship = Relationship(
    property_id=security_prop.id,
    process_id=encryption_proc.id,
    perspective_id=technical_pers.id,
    strength=0.9,
    confidence=0.95
)
framework.add_relationship(relationship)
```

### Framework Integration

```python
from p3if_methods.composition import CompositionEngine, MultiplexingStrategy

engine = CompositionEngine()
result = engine.overlay_frameworks(
    framework1, framework2,
    strategy=MultiplexingStrategy.UNION
)
```

## Testing

Run the test suite:

```bash
python -m pytest p3if_tests/test_core.py -v
python -m pytest p3if_tests/test_composition.py -v
```

## Performance Considerations

- Use caching for frequently accessed data
- Leverage async operations for I/O-bound tasks
- Monitor memory usage for large frameworks
- Consider data structure choices for optimal performance

## Extension Points

The modular design allows for easy extension:

1. **Custom Adapters**: Add support for new framework types
2. **Analysis Methods**: Implement new analytical approaches
3. **Validation Rules**: Add domain-specific validation logic
4. **Visualization Types**: Create new visualization components
5. **Storage Backends**: Support additional data storage options

## Dependencies

Core dependencies include:
- `pydantic>=2.0.0` for data validation
- `networkx>=3.0` for graph operations
- `numpy>=1.26.0` for numerical computations
- `pandas>=2.2.2` for data manipulation

## Contributing

When contributing to this package:

1. Follow the established patterns and interfaces
2. Add comprehensive tests for new functionality
3. Update documentation for public APIs
4. Ensure backward compatibility when possible
5. Follow PEP 8 style guidelines

See the [main contribution guidelines](../CONTRIBUTING.md) for more details.
