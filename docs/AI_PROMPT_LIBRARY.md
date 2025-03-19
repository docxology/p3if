# P3IF AI Prompt Library

This document contains a collection of prompts that can be used when working with LLMs (Large Language Models) on the P3IF codebase. These prompts are designed to generate high-quality, consistent code and documentation that follows P3IF standards.

## Code Generation Prompts

### Create a New Module

```
Generate a new P3IF module with the following specifications:

Module name: {module_name}
Purpose: {brief description}
Core functionality: {list of key functions/classes}

The module should follow P3IF standards with proper type hints, Google-style docstrings, error handling, and necessary unit tests. Ensure it follows the Property-Process-Perspective framework pattern where applicable.
```

### Define a New Pattern Type

```
Create a new pattern type for the P3IF framework:

Pattern name: {pattern_name}
Pattern category: [Property|Process|Perspective]
Domain: {domain_name}
Description: {detailed description}

Include type definitions, relationship handling, and serialization/deserialization methods. Ensure the implementation follows P3IF coding standards with appropriate error handling.
```

### Implement a Visualization Component

```
Implement a visualization component for P3IF with these specifications:

Visualization type: {type, e.g., "3D Cube", "Network Graph", etc.}
Data requirements: {what data this visualization needs}
Interactive features: {list of user interactions}
Responsive considerations: {how it should adapt to different screen sizes}

Separate data processing from rendering code and make parameters configurable. Include documentation on how to use and extend this component.
```

## Documentation Prompts

### Module Documentation

```
Create comprehensive documentation for the following P3IF module:

Module name: {module_name}
Source code:
```python
{paste module code here}
```

The documentation should include:
1. Overview of purpose and functionality
2. Detailed explanation of key classes and functions
3. Usage examples
4. Integration with other P3IF components
5. Any special considerations or limitations
```

### API Documentation

```
Generate API documentation for the following P3IF function/class:

```python
{paste function or class definition here}
```

Include:
- Detailed description
- Parameter explanations with types and constraints
- Return value details
- Exception information
- Multiple usage examples
- Common pitfalls or edge cases
- Performance considerations
```

### Tutorial Creation

```
Create a step-by-step tutorial for {specific P3IF task}:

The tutorial should:
1. Explain the purpose and expected outcome
2. List prerequisites and setup
3. Provide concrete step-by-step instructions
4. Include complete code examples
5. Explain key concepts along the way
6. Cover common errors and troubleshooting
7. Conclude with next steps or related features
```

## Testing Prompts

### Unit Test Generation

```
Generate comprehensive unit tests for the following P3IF function:

```python
{paste function here}
```

Include tests for:
- Normal operation with various valid inputs
- Edge cases and boundary conditions
- Error handling and exception cases
- Any performance concerns or considerations

Use pytest conventions with appropriate fixtures and mocks.
```

### Integration Test Design

```
Design integration tests for the following P3IF components working together:

Components:
- {component 1}
- {component 2}
- {component 3}

The tests should verify:
- Correct data flow between components
- Proper error propagation
- End-to-end functionality
- Performance under realistic conditions
```

## Code Improvement Prompts

### Code Review

```
Review the following P3IF code for adherence to best practices:

```python
{paste code here}
```

Evaluate:
1. PEP 8 compliance
2. Type hint completeness and correctness
3. Docstring quality and completeness
4. Error handling robustness
5. Testability
6. Performance considerations
7. Alignment with P3IF architectural patterns

Provide specific improvement suggestions with code examples.
```

### Refactoring

```
Refactor the following P3IF code to improve maintainability and readability:

```python
{paste code here}
```

The refactored code should:
- Follow single responsibility principle
- Improve naming for clarity
- Extract complex logic into well-named functions
- Enhance error handling
- Add or improve type hints and docstrings
- Optimize performance where appropriate

Explain your refactoring decisions.
```

## Domain-Specific Prompts

### Domain Model Creation

```
Create a P3IF domain model for {domain name}:

The model should include:
1. 15-20 key properties relevant to this domain
2. 15-20 important processes in this domain
3. 10-15 different perspectives that would view this domain
4. Example relationships between properties, processes, and perspectives

Each item should include a clear name and brief description. Format the output as a JSON structure compatible with P3IF domain files.
```

### Relationship Analysis

```
Analyze the relationships between the following P3IF patterns:

Properties:
- {property 1}
- {property 2}
...

Processes:
- {process 1}
- {process 2}
...

Perspectives:
- {perspective 1}
- {perspective 2}
...

Identify potential meaningful relationships between these elements, assigning appropriate strength and confidence values on a scale of 0.0-1.0. Explain the reasoning for each significant relationship.
```

## Visualization Prompts

### Visualization Interpretation

```
Interpret the following P3IF visualization results:

{visualization data or description}

Provide:
1. Overview of what patterns are visible
2. Identification of clusters or strong relationships
3. Outliers or unexpected relationships
4. Potential insights that might be derived
5. Suggestions for further exploration
```

### Visualization Enhancement

```
Suggest enhancements for the following P3IF visualization:

{visualization description or code}

Consider:
1. Usability improvements
2. Additional interaction capabilities
3. Performance optimizations
4. Accessibility considerations
5. New features that would add analytical value
```

## Guidelines for Using Prompts

1. **Customize for Specificity**: Replace the placeholders in curly braces `{like this}` with specific details relevant to your task.

2. **Provide Context**: When working on existing code, include relevant context like imports, related functions, or module structure.

3. **Iterative Refinement**: Use follow-up prompts to refine initial outputs until they meet P3IF standards.

4. **Verification**: Always verify generated code against P3IF standards and test thoroughly before integration.

5. **Documentation**: Remember to update documentation when implementing changes suggested by AI.

---

Feel free to extend this library with additional prompts as new patterns and best practices emerge in P3IF development. 