#!/usr/bin/env python3
"""
P3IF Master Orchestrator - run_all.py

Runs all P3IF components and outputs results to organized subfolders in outputs/.

Usage:
    python scripts/run_all.py           # Run everything
    python scripts/run_all.py --tests   # Run only tests
    python scripts/run_all.py --viz     # Run only visualizations
    python scripts/run_all.py --bench   # Run only benchmarks
    python scripts/run_all.py --examples # Run only examples
    python scripts/run_all.py --validate # Run only validation
"""

import sys
import os
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))


class P3IFMasterOrchestrator:
    """Master orchestrator for running all P3IF components."""

    def __init__(self, output_base: Path = None):
        """Initialize the master orchestrator.

        Args:
            output_base: Base directory for all outputs
        """
        self.project_root = project_root
        self.output_base = output_base or self.project_root / "outputs"
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_dir = self.output_base / f"p3if_run_{self.session_id}"
        self.results: Dict[str, Any] = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'components': {},
            'overall_status': 'pending'
        }

        # Create output directories
        self._setup_directories()

    def _setup_directories(self):
        """Create output directory structure."""
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.dirs = {
            'tests': self.session_dir / 'tests',
            'visualizations': self.session_dir / 'visualizations',
            'benchmarks': self.session_dir / 'benchmarks',
            'examples': self.session_dir / 'examples',
            'validation': self.session_dir / 'validation',
            'logs': self.session_dir / 'logs'
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    def _run_command(self, cmd: str, cwd: Path = None, timeout: int = 300) -> Tuple[int, str, str]:
        """Run a shell command and capture output.

        Args:
            cmd: Command to run
            cwd: Working directory
            timeout: Timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Set up environment with PYTHONPATH for p3if module
            env = os.environ.copy()
            src_path = str(self.project_root / 'src')
            existing_path = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = f"{src_path}:{self.project_root}:{existing_path}" if existing_path else f"{src_path}:{self.project_root}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                timeout=timeout,
                env=env
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, '', f'Command timed out after {timeout}s'
        except Exception as e:
            return -1, '', str(e)

    def run_tests(self) -> Dict[str, Any]:
        """Run the test suite and output results."""
        print("\n" + "=" * 60)
        print("🧪 RUNNING TESTS")
        print("=" * 60)

        result = {
            'status': 'pending',
            'output_dir': str(self.dirs['tests']),
            'passed': 0,
            'failed': 0,
            'total': 0
        }

        # Run pytest with junit XML output
        junit_path = self.dirs['tests'] / 'junit.xml'
        coverage_path = self.dirs['tests'] / 'coverage'

        cmd = (
            f"python -m pytest tests/ "
            f"--junit-xml={junit_path} "
            f"--cov=p3if --cov-report=html:{coverage_path} "
            f"--cov-report=term "
            f"-v 2>&1"
        )

        code, stdout, stderr = self._run_command(cmd, timeout=600)

        # Save raw output
        with open(self.dirs['tests'] / 'pytest_output.txt', 'w') as f:
            f.write(stdout)
            if stderr:
                f.write('\n\nSTDERR:\n')
                f.write(stderr)

        # Parse results
        if 'passed' in stdout:
            import re
            match = re.search(r'(\d+) passed', stdout)
            if match:
                result['passed'] = int(match.group(1))
            match = re.search(r'(\d+) failed', stdout)
            if match:
                result['failed'] = int(match.group(1))
            result['total'] = result['passed'] + result['failed']

        result['status'] = 'success' if code == 0 else 'failed'
        result['return_code'] = code

        print(f"✅ Tests: {result['passed']} passed, {result['failed']} failed")
        print(f"📁 Output: {self.dirs['tests']}")

        return result

    def run_visualizations(self) -> Dict[str, Any]:
        """Generate all visualizations."""
        print("\n" + "=" * 60)
        print("🎨 GENERATING VISUALIZATIONS")
        print("=" * 60)

        result = {
            'status': 'pending',
            'output_dir': str(self.dirs['visualizations']),
            'files_generated': 0
        }

        try:
            from p3if.visualization.portals.orchestrator import P3IFVisualizationOrchestrator

            orchestrator = P3IFVisualizationOrchestrator(self.dirs['visualizations'])

            # Generate all visualization types
            print("  Generating network visualizations...")
            orchestrator.generate_network_visualizations()

            print("  Generating list visualizations...")
            orchestrator.generate_list_visualizations()

            print("  Generating heatmap visualizations...")
            orchestrator.generate_heatmap_visualizations()

            print("  Generating 3D cube visualizations...")
            orchestrator.generate_3d_cube_visualizations()

            print("  Generating hierarchical visualizations...")
            orchestrator.generate_hierarchical_visualizations()

            print("  Generating matrix visualizations...")
            orchestrator.generate_matrix_visualizations()

            print("  Generating statistical visualizations...")
            orchestrator.generate_statistical_visualizations()

            print("  Generating grid visualizations...")
            orchestrator.generate_grid_visualizations()

            # Count generated files
            result['files_generated'] = orchestrator.count_generated_files()
            result['status'] = 'success'

            # Generate report
            report_path = orchestrator.generate_comprehensive_report()
            result['report_path'] = str(report_path)

            print(f"✅ Generated {result['files_generated']} visualization files")
            print(f"📁 Output: {self.dirs['visualizations']}")

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            print(f"❌ Visualization generation failed: {e}")

        return result

    def run_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks."""
        print("\n" + "=" * 60)
        print("⚡ RUNNING BENCHMARKS")
        print("=" * 60)

        result = {
            'status': 'pending',
            'output_dir': str(self.dirs['benchmarks'])
        }

        benchmark_output = self.dirs['benchmarks'] / 'benchmark_results.json'

        cmd = (
            f"python scripts/benchmark_performance.py "
            f"--output {benchmark_output} "
            f"--quick 2>&1"
        )

        code, stdout, stderr = self._run_command(cmd, timeout=300)

        # Save raw output
        with open(self.dirs['benchmarks'] / 'benchmark_output.txt', 'w') as f:
            f.write(stdout)
            if stderr:
                f.write('\n\nSTDERR:\n')
                f.write(stderr)

        result['status'] = 'success' if code == 0 else 'failed'
        result['return_code'] = code

        if code == 0:
            print("✅ Benchmarks completed successfully")
        else:
            print("❌ Benchmarks failed")
        print(f"📁 Output: {self.dirs['benchmarks']}")

        return result

    def run_examples(self) -> Dict[str, Any]:
        """Run all example orchestrators."""
        print("\n" + "=" * 60)
        print("📚 RUNNING EXAMPLES")
        print("=" * 60)

        result = {
            'status': 'pending',
            'output_dir': str(self.dirs['examples']),
            'examples_run': 0,
            'examples_passed': 0
        }

        try:
            from p3if.orchestrators.cognitive_security import CognitiveSecurityOrchestrator
            from p3if.orchestrators.healthcare_domain import HealthcareDomainOrchestrator
            from p3if.orchestrators.framework_integration import FrameworkIntegrationOrchestrator

            examples = [
                ('cognitive_security', CognitiveSecurityOrchestrator, 'execute_analysis', ['cybersecurity']),
                ('healthcare_domain', HealthcareDomainOrchestrator, 'execute_healthcare_analysis', ['hospital']),
                ('framework_integration', FrameworkIntegrationOrchestrator, 'execute_integration', [['CIA Triad', 'NIST CSF']])
            ]

            example_results = {}

            for name, OrchestratorClass, method, args in examples:
                print(f"  Running {name}...")
                try:
                    orchestrator = OrchestratorClass()
                    method_func = getattr(orchestrator, method)
                    example_result = method_func(*args)

                    example_results[name] = {
                        'status': 'success',
                        'result': example_result
                    }
                    result['examples_passed'] += 1
                    print(f"    ✅ {name} completed")

                except Exception as e:
                    example_results[name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    print(f"    ❌ {name} failed: {e}")

                result['examples_run'] += 1

            # Save results
            with open(self.dirs['examples'] / 'examples_results.json', 'w') as f:
                json.dump(example_results, f, indent=2, default=str)

            result['status'] = 'success' if result['examples_passed'] == result['examples_run'] else 'partial'

            print(f"✅ Examples: {result['examples_passed']}/{result['examples_run']} passed")
            print(f"📁 Output: {self.dirs['examples']}")

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            print(f"❌ Examples failed: {e}")

        return result

    def run_validation(self) -> Dict[str, Any]:
        """Run system validation."""
        print("\n" + "=" * 60)
        print("🔍 RUNNING VALIDATION")
        print("=" * 60)

        result = {
            'status': 'pending',
            'output_dir': str(self.dirs['validation']),
            'validations': {}
        }

        # Run validate_system.py
        cmd = f"python scripts/validate_system.py 2>&1"
        code, stdout, stderr = self._run_command(cmd)

        # Save output
        with open(self.dirs['validation'] / 'validation_output.txt', 'w') as f:
            f.write(stdout)
            if stderr:
                f.write('\n\nSTDERR:\n')
                f.write(stderr)

        # Parse validation results
        result['validations']['core_functionality'] = 'SUCCESS' in stdout
        result['validations']['api_endpoints'] = 'API' in stdout and 'validated' in stdout.lower()
        result['validations']['test_results'] = 'passed' in stdout

        result['status'] = 'success' if code == 0 else 'failed'
        result['return_code'] = code

        if code == 0:
            print("✅ System validation completed")
        else:
            print("❌ System validation failed")
        print(f"📁 Output: {self.dirs['validation']}")

        return result

    def run_all(self) -> Dict[str, Any]:
        """Run all components."""
        print("\n" + "=" * 70)
        print("🚀 P3IF MASTER ORCHESTRATOR - RUNNING ALL COMPONENTS")
        print("=" * 70)
        print(f"Session ID: {self.session_id}")
        print(f"Output Directory: {self.session_dir}")

        start_time = datetime.now()

        # Run all components
        self.results['components']['tests'] = self.run_tests()
        self.results['components']['visualizations'] = self.run_visualizations()
        self.results['components']['benchmarks'] = self.run_benchmarks()
        self.results['components']['examples'] = self.run_examples()
        self.results['components']['validation'] = self.run_validation()

        # Calculate overall status
        end_time = datetime.now()
        self.results['end_time'] = end_time.isoformat()
        self.results['duration_seconds'] = (end_time - start_time).total_seconds()

        statuses = [c['status'] for c in self.results['components'].values()]
        if all(s == 'success' for s in statuses):
            self.results['overall_status'] = 'success'
        elif any(s == 'failed' for s in statuses):
            self.results['overall_status'] = 'partial'
        else:
            self.results['overall_status'] = 'partial'

        # Save overall results
        with open(self.session_dir / 'run_all_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Print summary
        self._print_summary()

        return self.results

    def _print_summary(self):
        """Print execution summary."""
        print("\n" + "=" * 70)
        print("📋 EXECUTION SUMMARY")
        print("=" * 70)

        for name, component in self.results['components'].items():
            status_icon = '✅' if component['status'] == 'success' else '❌'
            print(f"  {status_icon} {name.title()}: {component['status']}")

        print()
        print(f"⏱️  Total Duration: {self.results['duration_seconds']:.2f}s")
        print(f"📁 All Outputs: {self.session_dir}")
        print(f"📄 Results JSON: {self.session_dir / 'run_all_results.json'}")

        overall_icon = '✅' if self.results['overall_status'] == 'success' else '⚠️'
        print(f"\n{overall_icon} OVERALL STATUS: {self.results['overall_status'].upper()}")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='P3IF Master Orchestrator - Run all P3IF components',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_all.py              # Run everything
    python scripts/run_all.py --tests      # Run only tests
    python scripts/run_all.py --viz        # Run only visualizations
    python scripts/run_all.py --tests --viz  # Run tests and visualizations
        """
    )

    parser.add_argument('--tests', action='store_true', help='Run tests')
    parser.add_argument('--viz', '--visualizations', action='store_true', help='Run visualizations')
    parser.add_argument('--bench', '--benchmarks', action='store_true', help='Run benchmarks')
    parser.add_argument('--examples', action='store_true', help='Run examples')
    parser.add_argument('--validate', action='store_true', help='Run validation')
    parser.add_argument('--output', '-o', type=str, help='Output base directory')

    args = parser.parse_args()

    # If no specific components selected, run all
    run_all = not any([args.tests, args.viz, args.bench, args.examples, args.validate])

    # Initialize orchestrator
    output_base = Path(args.output) if args.output else None
    orchestrator = P3IFMasterOrchestrator(output_base=output_base)

    if run_all:
        results = orchestrator.run_all()
    else:
        start_time = datetime.now()
        print("\n" + "=" * 70)
        print("🚀 P3IF MASTER ORCHESTRATOR - SELECTIVE RUN")
        print("=" * 70)
        print(f"Session ID: {orchestrator.session_id}")
        print(f"Output Directory: {orchestrator.session_dir}")

        if args.tests:
            orchestrator.results['components']['tests'] = orchestrator.run_tests()
        if args.viz:
            orchestrator.results['components']['visualizations'] = orchestrator.run_visualizations()
        if args.bench:
            orchestrator.results['components']['benchmarks'] = orchestrator.run_benchmarks()
        if args.examples:
            orchestrator.results['components']['examples'] = orchestrator.run_examples()
        if args.validate:
            orchestrator.results['components']['validation'] = orchestrator.run_validation()

        # Calculate duration
        end_time = datetime.now()
        orchestrator.results['end_time'] = end_time.isoformat()
        orchestrator.results['duration_seconds'] = (end_time - start_time).total_seconds()

        # Determine overall status
        statuses = [c['status'] for c in orchestrator.results['components'].values()]
        if all(s == 'success' for s in statuses):
            orchestrator.results['overall_status'] = 'success'
        elif any(s == 'success' for s in statuses):
            orchestrator.results['overall_status'] = 'partial'
        else:
            orchestrator.results['overall_status'] = 'failed'

        # Save results
        with open(orchestrator.session_dir / 'run_all_results.json', 'w') as f:
            json.dump(orchestrator.results, f, indent=2, default=str)

        orchestrator._print_summary()
        results = orchestrator.results

    # Exit code based on overall status
    return 0 if results['overall_status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
