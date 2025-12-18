#!/usr/bin/env python3
"""
P3IF Import Analysis Script

Scans all Python files in the repository for imports that need to be updated
for the P3IF 2.0 refactoring. Generates a comprehensive migration report.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ImportInfo:
    """Information about an import statement."""
    file_path: str
    line_number: int
    import_statement: str
    old_import: str
    new_import: str
    import_type: str  # 'from', 'import', 'relative'


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    file_path: str
    imports: List[ImportInfo] = field(default_factory=list)
    needs_update: bool = False


@dataclass
class MigrationReport:
    """Comprehensive migration report."""
    total_files: int = 0
    files_needing_update: int = 0
    total_imports: int = 0
    imports_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    files_by_module: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    detailed_analysis: List[FileAnalysis] = field(default_factory=list)


class ImportAnalyzer:
    """Analyzes Python imports for P3IF refactoring."""

    # Import patterns that need to be updated
    IMPORT_PATTERNS = {
        # Old → New mappings
        'from p3if_methods': 'from p3if.core',
        'from p3if_methods.core': 'from p3if.core',
        'from p3if_methods.models': 'from p3if.core.models',
        'from p3if_methods.orchestration': 'from p3if.core.orchestration',
        'from p3if_methods.analysis': 'from p3if.core.analysis',
        'from p3if_methods.composition': 'from p3if.core.composition',
        'from p3if_methods.validation': 'from p3if.core.validation',
        'from p3if_methods.caching': 'from p3if.core.caching',
        'from p3if_methods.dimensions': 'from p3if.core.dimensions',
        'from p3if_methods.performance_monitoring': 'from p3if.core.performance_monitoring',
        'from p3if_methods.framework': 'from p3if.core.framework',

        'from p3if_examples': 'from p3if.orchestrators',
        'from p3if_examples.cognitive_security_orchestrator': 'from p3if.orchestrators.cognitive_security',
        'from p3if_examples.framework_integration_orchestrator': 'from p3if.orchestrators.framework_integration',
        'from p3if_examples.healthcare_domain_orchestrator': 'from p3if.orchestrators.healthcare_domain',

        'from p3if_visualization': 'from p3if.visualization',
        'from p3if_visualization.interactive': 'from p3if.visualization.interactive',
        'from p3if_visualization.base': 'from p3if.visualization.base',
        'from p3if_visualization.portal': 'from p3if.visualization.portals',
        'from p3if_visualization.multi_domain_portal': 'from p3if.visualization.portals',
        'from p3if_visualization.dashboard': 'from p3if.visualization.portals',
        'from p3if_visualization.orchestrator': 'from p3if.visualization.portals',

        'from utils': 'from p3if.utils',
        'from utils.config': 'from p3if.utils.config',
        'from utils.json': 'from p3if.utils.json',
        'from utils.storage': 'from p3if.utils.storage',
        'from utils.performance': 'from p3if.utils.performance',
        'from utils.output_organizer': 'from p3if.utils.output_organizer',

        # Direct imports
        'import p3if_methods': 'import p3if.core',
        'import p3if_examples': 'import p3if.orchestrators',
        'import p3if_visualization': 'import p3if.visualization',
        'import utils': 'import p3if.utils',
    }

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.exclude_dirs = {
            '__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules',
            '.pytest_cache', 'build', 'dist', '.eggs', '*.egg-info'
        }

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file for imports that need updating."""
        analysis = FileAnalysis(str(file_path.relative_to(self.root_dir)))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Check for import statements
                if self._is_import_line(line):
                    import_info = self._analyze_import_line(line, file_path, line_num)
                    if import_info:
                        analysis.imports.append(import_info)
                        analysis.needs_update = True

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

        return analysis

    def _is_import_line(self, line: str) -> bool:
        """Check if a line contains an import statement."""
        line = line.strip()
        return (
            line.startswith('from ') or
            line.startswith('import ') or
            line.startswith('from .') or
            line.startswith('from ..')
        ) and not line.startswith('#')

    def _analyze_import_line(self, line: str, file_path: Path, line_num: int) -> ImportInfo | None:
        """Analyze a single import line to see if it needs updating."""
        original_line = line

        # Remove comments
        if '#' in line:
            line = line.split('#')[0].strip()

        # Check each pattern
        for old_pattern, new_pattern in self.IMPORT_PATTERNS.items():
            if old_pattern in line:
                return ImportInfo(
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=line_num,
                    import_statement=original_line,
                    old_import=old_pattern,
                    new_import=new_pattern,
                    import_type=self._get_import_type(line)
                )

        return None

    def _get_import_type(self, line: str) -> str:
        """Determine the type of import statement."""
        if line.startswith('from '):
            return 'from'
        elif line.startswith('import '):
            return 'import'
        elif line.startswith('from .') or line.startswith('from ..'):
            return 'relative'
        else:
            return 'unknown'

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the repository."""
        python_files = []

        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def generate_report(self) -> MigrationReport:
        """Generate a comprehensive migration report."""
        report = MigrationReport()
        python_files = self.find_python_files()

        print(f"Analyzing {len(python_files)} Python files...")

        for file_path in python_files:
            analysis = self.analyze_file(file_path)
            report.total_files += 1

            if analysis.needs_update:
                report.files_needing_update += 1
                report.detailed_analysis.append(analysis)

                # Categorize by module
                for import_info in analysis.imports:
                    module_category = self._categorize_module(import_info.old_import)
                    report.files_by_module[module_category].append(analysis.file_path)

            report.total_imports += len(analysis.imports)

            # Count import types
            for import_info in analysis.imports:
                report.imports_by_type[import_info.import_type] += 1

        return report

    def _categorize_module(self, old_import: str) -> str:
        """Categorize an import by its module."""
        if old_import.startswith('from p3if_methods') or old_import.startswith('import p3if_methods'):
            return 'p3if_methods'
        elif old_import.startswith('from p3if_examples') or old_import.startswith('import p3if_examples'):
            return 'p3if_examples'
        elif old_import.startswith('from p3if_visualization') or old_import.startswith('import p3if_visualization'):
            return 'p3if_visualization'
        elif old_import.startswith('from utils') or old_import.startswith('import utils'):
            return 'utils'
        else:
            return 'other'

    def save_report(self, report: MigrationReport, output_file: Path):
        """Save the migration report to a JSON file."""
        report_data = {
            'summary': {
                'total_files': report.total_files,
                'files_needing_update': report.files_needing_update,
                'total_imports': report.total_imports,
                'imports_by_type': dict(report.imports_by_type),
                'files_by_module': dict(report.files_by_module)
            },
            'detailed_analysis': [
                {
                    'file_path': analysis.file_path,
                    'needs_update': analysis.needs_update,
                    'import_count': len(analysis.imports),
                    'imports': [
                        {
                            'line_number': imp.line_number,
                            'import_statement': imp.import_statement,
                            'old_import': imp.old_import,
                            'new_import': imp.new_import,
                            'import_type': imp.import_type
                        }
                        for imp in analysis.imports
                    ]
                }
                for analysis in report.detailed_analysis
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"Migration report saved to: {output_file}")


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent.parent.parent  # Go up to project root
    analyzer = ImportAnalyzer(root_dir)

    print("🔍 Analyzing Python imports for P3IF 2.0 migration...")
    print(f"📁 Root directory: {root_dir}")

    report = analyzer.generate_report()

    # Print summary
    print("\n📊 ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total Python files: {report.total_files}")
    print(f"Files needing updates: {report.files_needing_update}")
    print(f"Total imports to update: {report.total_imports}")
    print(f"Import types: {dict(report.imports_by_type)}")

    print("\n📂 FILES BY MODULE:")
    for module, files in report.files_by_module.items():
        print(f"  {module}: {len(files)} files")

    # Save detailed report
    output_file = root_dir / "migration_report.json"
    analyzer.save_report(report, output_file)

    print(f"\n✅ Analysis complete! Detailed report saved to {output_file}")
    print("\nNext steps:")
    print("1. Review the migration_report.json file")
    print("2. Run the migration script: python scripts/refactor/migrate_imports.py")
    print("3. Validate changes: python scripts/refactor/validate_refactor.py")


if __name__ == '__main__':
    main()





