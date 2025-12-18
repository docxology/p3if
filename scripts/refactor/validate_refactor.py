#!/usr/bin/env python3
"""
P3IF Refactoring Validation Script

Validates that the P3IF 2.0 refactoring was successful by:
- Checking that all imports resolve correctly
- Running smoke tests on core functionality
- Detecting circular import issues
- Validating package structure
"""

import os
import sys
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_name: str
    passed: bool
    message: str
    details: Optional[str] = None


class RefactoringValidator:
    """Validates the P3IF 2.0 refactoring."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.results: List[ValidationResult] = []

    def validate_imports(self) -> List[ValidationResult]:
        """Validate that all expected imports work."""
        results = []

        # Core package imports to test
        core_imports = [
            ('p3if', 'Basic package import'),
            ('p3if.core', 'Core module import'),
            ('p3if.core.framework', 'Framework import'),
            ('p3if.core.models', 'Models import'),
            ('p3if.orchestrators', 'Orchestrators import'),
            ('p3if.visualization', 'Visualization import'),
            ('p3if.utils', 'Utils import'),
        ]

        for module_name, description in core_imports:
            try:
                module = importlib.import_module(module_name)
                results.append(ValidationResult(
                    check_name=f"Import: {module_name}",
                    passed=True,
                    message=f"✅ {description} works",
                    details=f"Module loaded successfully: {module}"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"Import: {module_name}",
                    passed=False,
                    message=f"❌ {description} failed",
                    details=f"Error: {e}\n{traceback.format_exc()}"
                ))

        return results

    def validate_class_instantiation(self) -> List[ValidationResult]:
        """Validate that key classes can be instantiated."""
        results = []

        instantiation_tests = [
            ('P3IFFramework', 'from p3if.core import P3IFFramework', 'P3IFFramework()'),
            ('Property', 'from p3if.core.models import Property', 'Property(name="test", domain="test")'),
            ('Process', 'from p3if.core.models import Process', 'Process(name="test", domain="test")'),
            ('CognitiveSecurityOrchestrator', 'from p3if.orchestrators import CognitiveSecurityOrchestrator', 'CognitiveSecurityOrchestrator()'),
        ]

        for class_name, import_stmt, instantiation_code in instantiation_tests:
            try:
                # Execute import
                exec(import_stmt, globals())

                # Execute instantiation
                instance = eval(instantiation_code)

                results.append(ValidationResult(
                    check_name=f"Instantiation: {class_name}",
                    passed=True,
                    message=f"✅ {class_name} can be instantiated",
                    details=f"Created instance: {instance}"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"Instantiation: {class_name}",
                    passed=False,
                    message=f"❌ {class_name} instantiation failed",
                    details=f"Import: {import_stmt}\nInstantiation: {instantiation_code}\nError: {e}\n{traceback.format_exc()}"
                ))

        return results

    def validate_circular_imports(self) -> List[ValidationResult]:
        """Check for circular import issues."""
        results = []

        # Test import chains that might have circular dependencies
        import_chains = [
            ['p3if.core', 'p3if.orchestrators', 'p3if.visualization', 'p3if.utils'],
            ['p3if.core.framework', 'p3if.core.models', 'p3if.core.orchestration'],
        ]

        for chain in import_chains:
            try:
                imported_modules = []
                for module_name in chain:
                    module = importlib.import_module(module_name)
                    imported_modules.append(str(module))

                results.append(ValidationResult(
                    check_name=f"Circular imports: {chain[0]} → ... → {chain[-1]}",
                    passed=True,
                    message=f"✅ Import chain works: {' → '.join(chain)}",
                    details=f"Modules: {imported_modules}"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"Circular imports: {' → '.join(chain)}",
                    passed=False,
                    message=f"❌ Import chain failed",
                    details=f"Error: {e}\n{traceback.format_exc()}"
                ))

        return results

    def validate_package_structure(self) -> List[ValidationResult]:
        """Validate that the new package structure exists."""
        results = []

        expected_dirs = [
            'src/p3if',
            'src/p3if/core',
            'src/p3if/core/analysis',
            'src/p3if/orchestrators',
            'src/p3if/visualization',
            'src/p3if/visualization/interactive',
            'src/p3if/visualization/static',
            'src/p3if/visualization/animated',
            'src/p3if/visualization/portals',
            'src/p3if/utils',
            'tests',
            'tests/unit',
            'tests/integration',
            'tests/visualization',
            'examples'
        ]

        for dir_path in expected_dirs:
            full_path = self.root_dir / dir_path
            if full_path.exists() and full_path.is_dir():
                results.append(ValidationResult(
                    check_name=f"Directory: {dir_path}",
                    passed=True,
                    message=f"✅ Directory exists: {dir_path}"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"Directory: {dir_path}",
                    passed=False,
                    message=f"❌ Directory missing: {dir_path}"
                ))

        # Check for __init__.py files
        expected_init_files = [
            'src/p3if/__init__.py',
            'src/p3if/core/__init__.py',
            'src/p3if/orchestrators/__init__.py',
            'src/p3if/visualization/__init__.py',
            'src/p3if/utils/__init__.py',
            'tests/__init__.py'
        ]

        for init_file in expected_init_files:
            full_path = self.root_dir / init_file
            if full_path.exists() and full_path.is_file():
                results.append(ValidationResult(
                    check_name=f"Init file: {init_file}",
                    passed=True,
                    message=f"✅ Init file exists: {init_file}"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"Init file: {init_file}",
                    passed=False,
                    message=f"❌ Init file missing: {init_file}"
                ))

        return results

    def validate_smoke_tests(self) -> List[ValidationResult]:
        """Run basic smoke tests."""
        results = []

        smoke_tests = [
            ('Basic framework creation', '''
from p3if.core import P3IFFramework
framework = P3IFFramework()
assert framework is not None
assert len(framework._patterns) == 0
'''),
            ('Pattern creation', '''
from p3if.core import P3IFFramework
from p3if.core.models import Property
framework = P3IFFramework()
prop = Property(name="Test", domain="test")
framework.add_pattern(prop)
assert len(framework._patterns) == 1
'''),
            ('Orchestrator creation', '''
from p3if.orchestrators import CognitiveSecurityOrchestrator
orch = CognitiveSecurityOrchestrator()
assert orch is not None
assert hasattr(orch, 'execute_analysis')
'''),
        ]

        for test_name, test_code in smoke_tests:
            try:
                # Create a fresh namespace for each test
                namespace = {}
                exec(test_code, namespace)

                results.append(ValidationResult(
                    check_name=f"Smoke test: {test_name}",
                    passed=True,
                    message=f"✅ Smoke test passed: {test_name}"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    check_name=f"Smoke test: {test_name}",
                    passed=False,
                    message=f"❌ Smoke test failed: {test_name}",
                    details=f"Code:\n{test_code}\n\nError: {e}\n{traceback.format_exc()}"
                ))

        return results

    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validation checks."""
        all_results = []

        print("🔍 Running P3IF 2.0 refactoring validation...")
        print("=" * 60)

        # Package structure validation
        print("📁 Checking package structure...")
        all_results.extend(self.validate_package_structure())

        # Import validation
        print("📦 Checking imports...")
        all_results.extend(self.validate_imports())

        # Circular import check
        print("🔄 Checking for circular imports...")
        all_results.extend(self.validate_circular_imports())

        # Class instantiation
        print("🏗️  Checking class instantiation...")
        all_results.extend(self.validate_class_instantiation())

        # Smoke tests
        print("🚭 Running smoke tests...")
        all_results.extend(self.validate_smoke_tests())

        self.results = all_results
        return all_results

    def generate_report(self) -> Dict:
        """Generate a validation report."""
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r.passed])
        failed_checks = total_checks - passed_checks

        report = {
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'success_rate': f"{passed_checks/total_checks*100:.1f}%" if total_checks > 0 else "0%"
            },
            'results': [
                {
                    'check_name': r.check_name,
                    'passed': r.passed,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.results
            ]
        }

        return report

    def print_report(self):
        """Print a formatted validation report."""
        report = self.generate_report()

        print("\n📊 VALIDATION REPORT")
        print("=" * 60)
        print(f"Total checks: {report['summary']['total_checks']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success rate: {report['summary']['success_rate']}")

        if report['summary']['failed'] > 0:
            print("\n❌ FAILED CHECKS:")
            for result in report['results']:
                if not result['passed']:
                    print(f"  • {result['check_name']}")
                    print(f"    {result['message']}")
                    if result['details']:
                        print(f"    Details: {result['details'][:200]}...")
                    print()
        else:
            print("\n✅ ALL CHECKS PASSED!")
            print("🎉 P3IF 2.0 refactoring validation successful!")

    def save_report(self, output_file: Path):
        """Save validation report to file."""
        import json
        report = self.generate_report()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"💾 Detailed report saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate P3IF 2.0 refactoring")
    parser.add_argument("--output", "-o", type=Path,
                       help="Save detailed report to JSON file")

    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent.parent  # Go up to project root

    # Temporarily add src to Python path for validation
    src_path = root_dir / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    validator = RefactoringValidator(root_dir)
    validator.run_all_validations()
    validator.print_report()

    if args.output:
        validator.save_report(args.output)

    # Return exit code based on success
    report = validator.generate_report()
    if report['summary']['failed'] > 0:
        print("❌ Validation failed - check the errors above")
        sys.exit(1)
    else:
        print("✅ Validation successful - ready for next phase!")
        sys.exit(0)


if __name__ == '__main__':
    main()





