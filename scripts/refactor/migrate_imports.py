#!/usr/bin/env python3
"""
P3IF Import Migration Script

Automatically updates import statements across the codebase for P3IF 2.0 refactoring.
Supports dry-run mode for safety and can process individual files or entire directories.
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class MigrationConfig:
    """Configuration for import migration."""
    dry_run: bool = True
    backup_files: bool = True
    verbose: bool = False
    input_file: Optional[Path] = None
    output_report: Optional[Path] = None


class ImportMigrator:
    """Handles automated import migration for P3IF 2.0."""

    # Import patterns that need to be updated
    IMPORT_MAPPINGS = {
        # p3if_methods → p3if.core
        r'\bfrom p3if_methods\b': 'from p3if.core',
        r'\bfrom p3if_methods\.core\b': 'from p3if.core',
        r'\bfrom p3if_methods\.models\b': 'from p3if.core.models',
        r'\bfrom p3if_methods\.orchestration\b': 'from p3if.core.orchestration',
        r'\bfrom p3if_methods\.analysis\b': 'from p3if.core.analysis',
        r'\bfrom p3if_methods\.composition\b': 'from p3if.core.composition',
        r'\bfrom p3if_methods\.validation\b': 'from p3if.core.validation',
        r'\bfrom p3if_methods\.caching\b': 'from p3if.core.caching',
        r'\bfrom p3if_methods\.dimensions\b': 'from p3if.core.dimensions',
        r'\bfrom p3if_methods\.performance_monitoring\b': 'from p3if.core.performance_monitoring',
        r'\bfrom p3if_methods\.framework\b': 'from p3if.core.framework',

        # p3if_examples → p3if.orchestrators
        r'\bfrom p3if_examples\b': 'from p3if.orchestrators',
        r'\bfrom p3if_examples\.cognitive_security_orchestrator\b': 'from p3if.orchestrators.cognitive_security',
        r'\bfrom p3if_examples\.framework_integration_orchestrator\b': 'from p3if.orchestrators.framework_integration',
        r'\bfrom p3if_examples\.healthcare_domain_orchestrator\b': 'from p3if.orchestrators.healthcare_domain',

        # p3if_visualization → p3if.visualization
        r'\bfrom p3if_visualization\b': 'from p3if.visualization',
        r'\bfrom p3if_visualization\.interactive\b': 'from p3if.visualization.interactive',
        r'\bfrom p3if_visualization\.base\b': 'from p3if.visualization.base',
        r'\bfrom p3if_visualization\.portal\b': 'from p3if.visualization.portals',
        r'\bfrom p3if_visualization\.multi_domain_portal\b': 'from p3if.visualization.portals',
        r'\bfrom p3if_visualization\.dashboard\b': 'from p3if.visualization.portals',
        r'\bfrom p3if_visualization\.orchestrator\b': 'from p3if.visualization.portals',

        # utils → p3if.utils
        r'\bfrom utils\b': 'from p3if.utils',
        r'\bfrom utils\.config\b': 'from p3if.utils.config',
        r'\bfrom utils\.json\b': 'from p3if.utils.json',
        r'\bfrom utils\.storage\b': 'from p3if.utils.storage',
        r'\bfrom utils\.performance\b': 'from p3if.utils.performance',
        r'\bfrom utils\.output_organizer\b': 'from p3if.utils.output_organizer',

        # Direct imports
        r'\bimport p3if_methods\b': 'import p3if.core',
        r'\bimport p3if_examples\b': 'import p3if.orchestrators',
        r'\bimport p3if_visualization\b': 'import p3if.visualization',
        r'\bimport utils\b': 'import p3if.utils',
    }

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.exclude_dirs = {
            '__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules',
            '.pytest_cache', 'build', 'dist', '.eggs', '*.egg-info'
        }
        self.stats = {
            'files_processed': 0,
            'files_changed': 0,
            'total_changes': 0,
            'errors': []
        }

    def migrate_file(self, file_path: Path) -> bool:
        """Migrate imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            modified_content = original_content
            changes_made = 0

            # Apply each mapping
            for pattern, replacement in self.IMPORT_MAPPINGS.items():
                # Use word boundaries to avoid partial matches
                new_content, count = re.subn(pattern, replacement, modified_content)
                if count > 0:
                    modified_content = new_content
                    changes_made += count
                    if self.config.verbose:
                        print(f"  {pattern} → {replacement} ({count} times)")

            # Only write if changes were made
            if changes_made > 0:
                if self.config.backup_files and not self.config.dry_run:
                    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                    shutil.copy2(file_path, backup_path)
                    if self.config.verbose:
                        print(f"  Backup created: {backup_path}")

                if not self.config.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)

                self.stats['files_changed'] += 1
                self.stats['total_changes'] += changes_made

                if self.config.verbose:
                    print(f"  Made {changes_made} changes")
                return True

            return False

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def find_files_to_migrate(self, root_dir: Path) -> List[Path]:
        """Find all Python files that need migration."""
        files_to_migrate = []

        # If input file is specified, only process that file
        if self.config.input_file:
            if self.config.input_file.exists() and self.config.input_file.suffix == '.py':
                files_to_migrate.append(self.config.input_file)
            else:
                print(f"❌ Input file not found or not a Python file: {self.config.input_file}")
            return files_to_migrate

        # Otherwise, find all Python files in the project
        for root, dirs, files in os.walk(root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    files_to_migrate.append(file_path)

        return files_to_migrate

    def load_migration_report(self, report_file: Path) -> Optional[Dict]:
        """Load migration report to know which files to process."""
        if not report_file.exists():
            print(f"⚠️  Migration report not found: {report_file}")
            print("   Will scan all Python files. This may take longer.")
            return None

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            # Extract files that need updating
            files_needing_update = []
            for analysis in report.get('detailed_analysis', []):
                if analysis.get('needs_update', False):
                    files_needing_update.append(analysis['file_path'])

            print(f"📋 Loaded migration report: {len(files_needing_update)} files need updating")
            return {'files_needing_update': files_needing_update}

        except Exception as e:
            print(f"❌ Error loading migration report: {e}")
            return None

    def migrate_project(self, root_dir: Path):
        """Migrate all imports in the project."""
        print("🚀 Starting P3IF 2.0 import migration...")
        print(f"📁 Root directory: {root_dir}")
        print(f"🔍 Dry run: {self.config.dry_run}")
        print(f"💾 Backup files: {self.config.backup_files}")

        # Try to load migration report
        report_file = root_dir / "migration_report.json"
        report_data = self.load_migration_report(report_file)

        # Find files to process
        if self.config.input_file:
            files_to_process = self.find_files_to_migrate(root_dir)
        elif report_data:
            # Use files from report
            files_to_process = [
                root_dir / file_path for file_path in report_data['files_needing_update']
            ]
        else:
            # Scan all files
            files_to_process = self.find_files_to_migrate(root_dir)

        print(f"📝 Processing {len(files_to_process)} files...")

        # Process each file
        for file_path in files_to_process:
            self.stats['files_processed'] += 1

            if self.config.verbose:
                print(f"\n📄 Processing: {file_path.relative_to(root_dir)}")

            changed = self.migrate_file(file_path)

            if changed and not self.config.verbose:
                print(f"✅ Updated: {file_path.relative_to(root_dir)}")

        # Generate report
        self.generate_report(root_dir)

    def generate_report(self, root_dir: Path):
        """Generate a migration report."""
        print("\n📊 MIGRATION REPORT")
        print("=" * 50)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files changed: {self.stats['files_changed']}")
        print(f"Total changes: {self.stats['total_changes']}")
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\n❌ ERRORS:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"  {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

        if self.config.output_report:
            report_data = {
                'summary': self.stats,
                'configuration': {
                    'dry_run': self.config.dry_run,
                    'backup_files': self.config.backup_files,
                    'verbose': self.config.verbose
                }
            }

            with open(self.config.output_report, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Detailed report saved to: {self.config.output_report}")

        # Success message
        if not self.config.dry_run and self.stats['files_changed'] > 0:
            print("\n✅ Migration completed successfully!")
            print("Next steps:")
            print("1. Run tests: python scripts/refactor/validate_refactor.py")
            print("2. Check imports: python -c 'import p3if; print(\"Basic import works!\")'")
            print("3. Proceed to Phase 2: Create new directory structure")
        elif self.config.dry_run:
            print("\n🔍 Dry run completed!")
            print("Review the changes above and run again without --dry-run to apply them.")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate P3IF imports to 2.0 structure")
    parser.add_argument("--dry-run", action="store_true", default=False,
                       help="Show changes without applying them (default: False)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup files")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--file", type=Path,
                       help="Process only this specific file")
    parser.add_argument("--report", type=Path,
                       help="Save detailed report to this file")

    args = parser.parse_args()

    # Determine if dry run
    dry_run = args.dry_run
    if not dry_run:
        # Ask for confirmation when not in dry-run mode
        print("⚠️  You are about to modify files!")
        response = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("Migration cancelled.")
            return

    config = MigrationConfig(
        dry_run=dry_run,
        backup_files=not args.no_backup,
        verbose=args.verbose,
        input_file=args.file,
        output_report=args.report
    )

    root_dir = Path(__file__).parent.parent.parent  # Go up to project root
    migrator = ImportMigrator(config)
    migrator.migrate_project(root_dir)


if __name__ == '__main__':
    main()
