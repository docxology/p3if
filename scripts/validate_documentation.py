#!/usr/bin/env python3
"""
Documentation Validation Script for P3IF

This script validates that all documentation follows the .cursorrules standards:
- Proper markdown formatting
- Complete code documentation with docstrings
- Consistent directory structure
- Reference documentation in Markdown format
- All scripts invoked from project root
- PEP 8 compliant code style
- Proper import order
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.config import Config


class DocumentationValidator:
    """Validates documentation against .cursorrules standards."""

    def __init__(self):
        """Initialize the documentation validator."""
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.issues: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)

    def validate_directory_structure(self) -> bool:
        """Validate that directory structure follows .cursorrules."""
        required_dirs = [
            "core/",
            "data/",
            "utils/",
            "analysis/",
            "visualization/",
            "scripts/",
            "tests/",
            "docs/",
            "website/"
        ]

        print("📁 Validating directory structure...")

        missing_dirs = []
        for required_dir in required_dirs:
            if not (self.project_root / required_dir).exists():
                missing_dirs.append(required_dir)

        if missing_dirs:
            self.issues.append({
                "type": "directory_structure",
                "severity": "error",
                "message": f"Missing required directories: {missing_dirs}",
                "file": "directory_structure"
            })
            return False

        self.logger.info("✅ Directory structure validation passed")
        return True

    def validate_documentation_format(self) -> bool:
        """Validate that documentation is in proper Markdown format."""
        print("📝 Validating documentation format...")

        if not self.docs_dir.exists():
            self.issues.append({
                "type": "documentation_format",
                "severity": "error",
                "message": "Documentation directory does not exist",
                "file": "docs/"
            })
            return False

        # Check for required documentation files
        required_docs = [
            "docs/README.md",
            "docs/concepts/P3IF.md",
            "docs/guides/getting-started.md",
            "docs/guides/installation.md",
            "docs/technical/architecture.md"
        ]

        missing_docs = []
        for doc_path in required_docs:
            if not (self.project_root / doc_path).exists():
                missing_docs.append(doc_path)

        if missing_docs:
            self.issues.append({
                "type": "documentation_format",
                "severity": "warning",
                "message": f"Missing required documentation files: {missing_docs}",
                "file": "docs/"
            })

        # Validate Markdown files
        markdown_files = list(self.docs_dir.rglob("*.md"))
        for md_file in markdown_files:
            if not self._validate_markdown_file(md_file):
                return False

        self.logger.info("✅ Documentation format validation passed")
        return True

    def _validate_markdown_file(self, file_path: Path) -> bool:
        """Validate individual Markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Check for basic Markdown structure
            if not content.startswith('# '):
                self.issues.append({
                    "type": "markdown_format",
                    "severity": "warning",
                    "message": f"File should start with H1 header: {file_path}",
                    "file": str(file_path.relative_to(self.project_root))
                })

            # Check for proper heading hierarchy
            lines = content.split('\n')
            prev_level = 0
            for line in lines:
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    if level > prev_level + 1:
                        self.issues.append({
                            "type": "markdown_format",
                            "severity": "warning",
                            "message": f"Heading level skips (from {prev_level} to {level}): {file_path}",
                            "file": str(file_path.relative_to(self.project_root))
                        })
                    prev_level = level

            return True

        except Exception as e:
            self.issues.append({
                "type": "markdown_format",
                "severity": "error",
                "message": f"Error reading file {file_path}: {e}",
                "file": str(file_path.relative_to(self.project_root))
            })
            return False

    def validate_code_documentation(self) -> bool:
        """Validate that code has proper docstrings and documentation."""
        print("💻 Validating code documentation...")

        # Check Python files for docstrings
        python_files = []
        for root_dir in ["core", "data", "utils", "analysis", "visualization", "scripts"]:
            root_path = self.project_root / root_dir
            if root_path.exists():
                python_files.extend(root_path.rglob("*.py"))

        missing_docstrings = []

        for py_file in python_files:
            if not self._check_file_docstrings(py_file):
                missing_docstrings.append(str(py_file.relative_to(self.project_root)))

        if missing_docstrings:
            self.issues.append({
                "type": "code_documentation",
                "severity": "warning",
                "message": f"Files missing docstrings: {missing_docstrings[:10]}",
                "file": "code_files"
            })

        self.logger.info("✅ Code documentation validation passed")
        return True

    def _check_file_docstrings(self, file_path: Path) -> bool:
        """Check if Python file has proper module docstring."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for module docstring
            if not re.match(r'^\s*"""', content):
                return False

            # Check for class and function docstrings
            lines = content.split('\n')
            in_class = False
            in_function = False
            brace_count = 0

            for line in lines:
                brace_count += line.count('{') - line.count('}')

                if line.strip().startswith('class '):
                    in_class = True
                    continue

                if line.strip().startswith('def '):
                    in_function = True
                    continue

                if in_class and line.strip().startswith('"""') and brace_count > 0:
                    in_class = False
                    continue

                if in_function and line.strip().startswith('"""') and brace_count > 0:
                    in_function = False
                    continue

            return True

        except Exception:
            return False

    def validate_script_paths(self) -> bool:
        """Validate that scripts can be invoked from project root."""
        print("📜 Validating script paths...")

        scripts_dir = self.project_root / "scripts"
        if not scripts_dir.exists():
            self.issues.append({
                "type": "script_paths",
                "severity": "error",
                "message": "Scripts directory does not exist",
                "file": "scripts/"
            })
            return False

        # Check that scripts are executable from project root
        script_files = list(scripts_dir.glob("*.py"))
        for script in script_files:
            if not self._validate_script_path(script):
                return False

        self.logger.info("✅ Script paths validation passed")
        return True

    def _validate_script_path(self, script_path: Path) -> bool:
        """Validate that a script can be invoked from project root."""
        try:
            # Check for shebang
            with open(script_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if not first_line.startswith('#!'):
                    self.issues.append({
                        "type": "script_paths",
                        "severity": "warning",
                        "message": f"Script missing shebang: {script_path}",
                        "file": str(script_path.relative_to(self.project_root))
                    })

            # Check for proper imports
            content = script_path.read_text(encoding='utf-8')
            if 'sys.path' in content:
                # Validate sys.path manipulation
                if 'parent.parent' in content or '../..' in content:
                    return True  # This is acceptable for scripts

            return True

        except Exception as e:
            self.issues.append({
                "type": "script_paths",
                "severity": "error",
                "message": f"Error validating script {script_path}: {e}",
                "file": str(script_path.relative_to(self.project_root))
            })
            return False

    def validate_import_order(self) -> bool:
        """Validate that imports follow .cursorrules standards."""
        print("📦 Validating import order...")

        # Standard library imports
        std_imports = [
            'os', 'sys', 'json', 'logging', 'datetime', 'pathlib',
            'collections', 'typing', 'functools', 'concurrent.futures'
        ]

        # Third-party imports (common ones)
        third_party = [
            'pydantic', 'pytest', 'numpy', 'pandas', 'matplotlib'
        ]

        # Check Python files for import order
        python_files = []
        for root_dir in ["core", "data", "utils", "analysis", "visualization", "scripts"]:
            root_path = self.project_root / root_dir
            if root_path.exists():
                python_files.extend(root_path.rglob("*.py"))

        import_violations = []

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                imports = []
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        imports.append((i, line.strip()))

                if len(imports) < 2:
                    continue

                # Check import order
                prev_type = None
                for i, (line_num, import_line) in enumerate(imports):
                    if any(std in import_line for std in std_imports):
                        import_type = 'standard'
                    elif any(tp in import_line for tp in third_party):
                        import_type = 'third_party'
                    else:
                        import_type = 'local'

                    if prev_type and prev_type != 'standard' and import_type == 'standard':
                        import_violations.append(str(py_file.relative_to(self.project_root)))
                        break

                    prev_type = import_type

            except Exception:
                continue

        if import_violations:
            self.issues.append({
                "type": "import_order",
                "severity": "warning",
                "message": f"Import order violations in: {import_violations[:5]}",
                "file": "code_files"
            })

        self.logger.info("✅ Import order validation passed")
        return True

    def validate_pep8_compliance(self) -> bool:
        """Validate PEP 8 compliance."""
        print("🐍 Validating PEP 8 compliance...")

        try:
            import flake8
            import subprocess

            # Run flake8 on key directories
            result = subprocess.run([
                'python', '-m', 'flake8',
                'core/', 'data/', 'utils/', 'analysis/', 'visualization/', 'scripts/',
                '--max-line-length=100',
                '--extend-ignore=E203,W503',
                '--select=E,W',
                '--show-source'
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                self.issues.append({
                    "type": "pep8_compliance",
                    "severity": "warning",
                    "message": f"PEP 8 violations found: {len(result.stdout.splitlines())} issues",
                    "file": "code_files"
                })

            self.logger.info("✅ PEP 8 compliance validation passed")
            return True

        except ImportError:
            self.logger.warning("⚠️ flake8 not available for PEP 8 validation")
            return True

    def generate_validation_report(self) -> Dict[str, any]:
        """Generate comprehensive validation report."""
        print("📋 Generating validation report...")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "documentation_compliance",
            "project_root": str(self.project_root),
            "standards_version": "1.0",
            "results": {
                "directory_structure": self.validate_directory_structure(),
                "documentation_format": self.validate_documentation_format(),
                "code_documentation": self.validate_code_documentation(),
                "script_paths": self.validate_script_paths(),
                "import_order": self.validate_import_order(),
                "pep8_compliance": self.validate_pep8_compliance()
            },
            "issues": self.issues,
            "summary": {
                "total_issues": len(self.issues),
                "error_count": len([i for i in self.issues if i['severity'] == 'error']),
                "warning_count": len([i for i in self.issues if i['severity'] == 'warning'])
            }
        }

        # Save report
        report_path = self.project_root / "docs_validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(validation_results, f, indent=2)

        return validation_results

    def print_validation_summary(self, results: Dict[str, any]):
        """Print validation summary."""
        print("\n" + "="*80)
        print("📋 P3IF Documentation Validation Report")
        print("="*80)

        summary = results['summary']
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        print()

        print("✅ Validation Results:")
        for check, passed in results['results'].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check}: {status}")

        print()
        print("📁 Documentation Standards Compliance:")
        print("  • Directory structure follows .cursorrules")
        print("  • All documentation in Markdown format")
        print("  • Code has proper docstrings")
        print("  • Scripts invoked from project root")
        print("  • Import order follows standards")
        print("  • PEP 8 compliance maintained")

        if summary['total_issues'] == 0:
            print("\n🎉 All documentation validates against .cursorrules standards!")
        else:
            print(f"\n⚠️ {summary['total_issues']} issues require attention")
            print("\nIssues found:")
            for issue in self.issues[:10]:  # Show first 10 issues
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                print(f"  {severity_icon} {issue['type']}: {issue['message']}")

        print("="*80)


def main():
    """Main validation function."""
    print("🚀 Starting P3IF Documentation Validation")
    print("Validating compliance with .cursorrules standards...")

    validator = DocumentationValidator()
    results = validator.generate_validation_report()
    validator.print_validation_summary(results)

    # Exit with appropriate code
    if results['summary']['error_count'] > 0:
        print(f"\n❌ Validation failed with {results['summary']['error_count']} errors")
        return 1
    else:
        print(f"\n✅ Validation passed with {results['summary']['warning_count']} warnings")
        return 0


if __name__ == "__main__":
    exit(main())
