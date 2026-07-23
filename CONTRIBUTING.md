# Contributing to P3IF

Thank you for your interest in contributing to P3IF (Properties, Processes, and Perspectives Inter-Framework)! We welcome contributions from the community and are committed to fostering an open, inclusive, and collaborative environment.

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Python 3.8+** installed on your system
2. **Git** for version control
3. **A GitHub account** to submit pull requests
4. **Familiarity with the P3IF codebase** (see [Getting Started](docs/guides/getting-started.md))

### Development Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/docxology/p3if.git
   cd p3if
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to ensure everything works:**
   ```bash
   pytest tests/ -v
   ```

## 🤝 How to Contribute

### 1. Find an Issue or Feature

- **Browse existing issues** on [GitHub Issues](https://github.com/p3if/p3if/issues)
- **Check the roadmap** in [P3IF_IMPROVEMENTS_SUMMARY.md](docs/P3IF_IMPROVEMENTS_SUMMARY.md)
- **Propose new features** by creating an issue with the "enhancement" label

### 2. Create a Branch

Create a feature branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Your Changes

- **Follow the established code patterns** (see [AGENTS.md](AGENTS.md) for AI development guidelines)
- **Add comprehensive tests** for new functionality
- **Update documentation** for any new features or changes
- **Ensure code quality** by running tests and linters

### 4. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v

# Check code quality
ruff check src/ tests/
```

### 5. Commit Your Changes

Follow conventional commit messages:

```bash
git add .
git commit -m "feat: add new feature description"

# or for bug fixes
git commit -m "fix: resolve issue description"

# or for documentation
git commit -m "docs: update documentation for feature"
```

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then visit the repository on GitHub and create a pull request from your branch.

## 📋 Contribution Guidelines

### Code Standards

1. **Follow PEP 8** style guidelines
2. **Use type hints** for all function parameters and return values
3. **Include comprehensive docstrings** using Google-style format
4. **Add unit tests** for all new functionality
5. **Handle errors gracefully** with appropriate exception handling

### Documentation Standards

1. **Update relevant documentation** for any code changes
2. **Include usage examples** for new features
3. **Update README files** for new modules or significant changes
4. **Add tutorials** for complex new features

### Testing Requirements

1. **Unit tests** for all new functions and classes
2. **Integration tests** for component interactions
3. **Performance tests** for expensive operations
4. **Error condition tests** for edge cases

### Pull Request Requirements

- [ ] **Clear description** of changes and motivation
- [ ] **Tests pass** on CI/CD pipeline
- [ ] **Documentation updated** for any public API changes
- [ ] **Code follows style guidelines**
- [ ] **Backward compatibility maintained** (unless explicitly breaking)
- [ ] **Reviewers assigned** from the maintainer team

## 🏗️ Development Workflow

### For New Features

1. **Create an issue** describing the feature and its requirements
2. **Discuss design** with the community and maintainers
3. **Implement the feature** following established patterns
4. **Add comprehensive tests**
5. **Update documentation**
6. **Submit pull request**

### For Bug Fixes

1. **Reproduce the bug** and understand the root cause
2. **Write a test** that demonstrates the bug
3. **Fix the bug** with minimal, targeted changes
4. **Verify the fix** resolves the issue
5. **Submit pull request**

### For Documentation

1. **Identify gaps** in current documentation
2. **Write clear, comprehensive content**
3. **Include examples** and usage instructions
4. **Test documentation** with real examples
5. **Submit pull request**

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/p3if --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v

# Run tests for specific component
pytest tests/unit/test_composition.py -v
```

## 🖥️ Interactive Terminal

P3IF includes an interactive terminal for streamlined development workflows:

### Running the Terminal

```bash
./interactive_terminal.sh
```

### Available Options

| Option | Description |
|--------|-------------|
| 1 | Setup Environment (UV, venv, dependencies) |
| 2 | Run All Tests |
| 3 | Run All Examples |
| 4 | Generate Visualizations |
| 5 | Show System Status |
| 6 | Help & Information |
| 7 | **Run All (1-4)** - Complete workflow |
| 0 | Exit |

### Run All Workflow

Option **7 (Run All)** executes the complete development workflow:
1. Sets up the environment (UV, venv, dependencies)
2. Runs all tests with comprehensive reporting
3. Runs all examples with validation
4. Generates all visualizations

This is the recommended way to verify that everything works correctly.

### Command Line Usage

```bash
# Automated workflow (non-interactive)
./interactive_terminal.sh --auto

# Custom commands
./interactive_terminal.sh --commands setup_uv,run_tests,run_examples,gen_viz

# Show status
./interactive_terminal.sh --status
```

## 📁 Output Organization

When using **Run All (Option 7)**, all outputs are organized in a single timestamped session folder:

```
outputs/
└── run_YYYYMMDD_HHMMSS/           # Unified session folder
    ├── tests/                      # Test reports and logs
    │   ├── test_report.json        # Detailed test results
    │   └── test_output.log         # Test execution log
    ├── examples/                   # Example execution results
    │   ├── examples_results.json   # Detailed JSON results
    │   ├── examples_summary.md     # Human-readable summary
    │   └── examples_execution.log  # Execution log
    ├── visualizations/             # Generated visualizations
    │   ├── networks/               # Network graphs
    │   ├── heatmaps/               # Heatmap visualizations
    │   ├── cubes/                  # 3D cube visualizations
    │   ├── hierarchies/            # Hierarchy diagrams
    │   ├── matrices/               # Matrix visualizations
    │   ├── statistics/             # Statistical charts
    │   ├── grids/                  # Grid visualizations
    │   └── reports/                # Comprehensive reports
    ├── logs/                       # Session logs
    │   ├── examples.log
    │   └── visualizations.log
    └── session_metadata.json       # Session tracking info
```

This unified structure ensures all outputs from a single run are organized together for easy access and comparison.

### Writing Tests

Follow the established testing patterns:

```python
import pytest
from tests.fixtures import create_test_framework

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.framework = create_test_framework()

    def test_basic_functionality(self):
        """Test basic functionality of the new feature."""
        result = self.framework.new_feature()
        self.assertEqual(result["status"], "success")

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        with self.assertRaises(ValueError):
            self.framework.new_feature(invalid_input)
```

## 📚 Documentation Guidelines

### When to Update Documentation

- **New features** require documentation
- **API changes** need updated references
- **Bug fixes** may need updated examples
- **Performance improvements** should be documented

### Documentation Structure

```
docs/
├── concepts/          # Core concepts and theory
├── technical/         # Technical specifications
├── guides/           # User guides and tutorials
├── tutorials/        # Step-by-step tutorials
├── examples/         # Example implementations
├── api/              # API documentation
├── visualization/    # Visualization documentation
└── diagrams/         # Architecture and process diagrams
```

### Writing Documentation

1. **Use clear, concise language**
2. **Include code examples** where appropriate
3. **Provide step-by-step instructions**
4. **Include troubleshooting sections**
5. **Cross-reference related documentation**

## 🎯 Areas for Contribution

### Core Framework Development
- New pattern types and relationship types
- Enhanced validation rules
- Performance optimizations
- Storage backend implementations

### Visualization Enhancements
- New visualization types
- Interactive features
- Performance improvements
- Accessibility enhancements

### Documentation Improvements
- Tutorial creation
- Example implementations
- API documentation
- Troubleshooting guides

### Testing and Quality Assurance
- Additional test coverage
- Performance benchmarking
- Integration testing
- Quality assurance automation

### Community and Ecosystem
- Tool integrations
- Package ecosystem
- Community resources
- Educational materials

## 🛠️ Development Tools

### Code Quality Tools

```bash
# Code formatting
python -m black your_file.py

# Import sorting
python -m isort your_file.py

# Linting
python -m flake8 your_file.py

# Type checking
python -m mypy your_file.py
```

### Documentation Tools

```bash
# Validate documentation
python scripts/validate_system.py

# Check documentation accuracy
python scripts/validate_system.py
```

### Testing Tools

```bash
# Run test suite
pytest tests/ -v

# Coverage analysis
pytest tests/ --cov=src/p3if --cov-report=html

# Performance testing
python scripts/benchmark_performance.py
```

## 🤝 Community Guidelines

### Communication

- **Be respectful** and inclusive in all interactions
- **Use constructive language** when providing feedback
- **Ask questions** when something is unclear
- **Share knowledge** and help others learn

### Code Review

- **Be thorough** but kind in code reviews
- **Explain your reasoning** for suggested changes
- **Suggest alternatives** when appropriate
- **Acknowledge good work** and improvements

### Issue Reporting

- **Provide clear descriptions** of issues or feature requests
- **Include reproduction steps** for bugs
- **Suggest solutions** when possible
- **Use appropriate labels** (bug, enhancement, documentation, etc.)

## 📜 License and Copyright

By contributing to P3IF, you agree that:

- Your contributions will be licensed under the MIT License
- You have the right to contribute the code
- You understand that contributions become part of the public codebase
- You will follow the established contribution guidelines

## 🙏 Acknowledgments

Thank you for contributing to P3IF! Your contributions help make the framework better for everyone. We appreciate the time, effort, and expertise you bring to the project.

## 📞 Getting Help

If you need help with contributing:

1. **Check this guide** for common questions
2. **Browse existing issues** for similar problems
3. **Ask in GitHub Discussions** for community help
4. **Contact maintainers** for complex issues

We're here to help you succeed in contributing to P3IF!

