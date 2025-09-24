#!/usr/bin/env python3
"""
P3IF Examples Runner

A comprehensive script to run all P3IF examples with validation and output confirmation.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure p3if package is importable
p3if_package_path = project_root
sys.path.insert(0, str(p3if_package_path))

# Also add the current directory to handle relative imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

import logging
from p3if_examples.cognitive_security_orchestrator import CognitiveSecurityOrchestrator
from p3if_examples.healthcare_domain_orchestrator import HealthcareDomainOrchestrator
from p3if_examples.framework_integration_orchestrator import FrameworkIntegrationOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/examples_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ExamplesRunner:
    """Runner for all P3IF examples with comprehensive validation."""

    def __init__(self):
        """Initialize the examples runner."""
        self.output_dir = Path("output/examples")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

    def run_cognitive_security_example(self) -> Dict[str, Any]:
        """Run the cognitive security orchestrator example."""
        logger.info("🧠 Running Cognitive Security Orchestrator...")

        try:
            orchestrator = CognitiveSecurityOrchestrator()
            result = orchestrator.execute_analysis('cybersecurity')

            # Validate results
            validation = {
                'steps_completed': len(result.get('step_results', {})),
                'recommendations_count': len(result.get('recommendations', [])),
                'summary_present': 'summary' in result,
                'domain_context': result.get('domain_context'),
                'execution_time': time.time()
            }

            logger.info(f"✅ Cognitive Security: {validation['steps_completed']}/4 steps completed")
            logger.info(f"   Recommendations: {validation['recommendations_count']}")
            logger.info(f"   Domain: {validation['domain_context']}")

            return {
                'status': 'success',
                'validation': validation,
                'result': result
            }

        except Exception as e:
            logger.error(f"❌ Cognitive Security Orchestrator failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'validation': None
            }

    def run_healthcare_example(self) -> Dict[str, Any]:
        """Run the healthcare domain orchestrator example."""
        logger.info("🏥 Running Healthcare Domain Orchestrator...")

        try:
            orchestrator = HealthcareDomainOrchestrator()
            result = orchestrator.execute_healthcare_analysis('hospital')

            # Validate results
            summary = result.get('summary', {})
            validation = {
                'steps_completed': len(result.get('step_results', {})),
                'recommendations_count': len(result.get('recommendations', [])),
                'data_types_analyzed': summary.get('data_types_analyzed', 0),
                'compliance_frameworks': summary.get('compliance_frameworks_mapped', 0),
                'organization_type': result.get('organization_type'),
                'execution_time': time.time()
            }

            logger.info(f"✅ Healthcare Domain: {validation['steps_completed']}/4 steps completed")
            logger.info(f"   Recommendations: {validation['recommendations_count']}")
            logger.info(f"   Data Types: {validation['data_types_analyzed']}")
            logger.info(f"   Organization: {validation['organization_type']}")

            return {
                'status': 'success',
                'validation': validation,
                'result': result
            }

        except Exception as e:
            logger.error(f"❌ Healthcare Domain Orchestrator failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'validation': None
            }

    def run_framework_integration_example(self) -> Dict[str, Any]:
        """Run the framework integration orchestrator example."""
        logger.info("🔧 Running Framework Integration Orchestrator...")

        try:
            orchestrator = FrameworkIntegrationOrchestrator()
            result = orchestrator.execute_integration(['CIA Triad', 'NIST CSF'])

            # Validate results
            summary = result.get('summary', {})
            unified_model = result.get('unified_model', {})
            validation_results = result.get('validation_results', {})

            validation = {
                'steps_completed': len(result.get('step_results', {})),
                'frameworks_integrated': summary.get('frameworks_integrated', 0),
                'conflicts_resolved': summary.get('conflicts_resolved', 0),
                'validation_passed': summary.get('validation_passed', False),
                'properties_count': len(unified_model.get('properties', [])),
                'processes_count': len(unified_model.get('processes', [])),
                'perspectives_count': len(unified_model.get('perspectives', [])),
                'execution_time': time.time()
            }

            logger.info(f"✅ Framework Integration: {validation['steps_completed']}/5 steps completed")
            logger.info(f"   Validation Passed: {validation['validation_passed']}")
            logger.info(f"   Properties: {validation['properties_count']}")
            logger.info(f"   Processes: {validation['processes_count']}")
            logger.info(f"   Perspectives: {validation['perspectives_count']}")

            return {
                'status': 'success',
                'validation': validation,
                'result': result
            }

        except Exception as e:
            logger.error(f"❌ Framework Integration Orchestrator failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'validation': None
            }

    def run_all_examples(self) -> Dict[str, Any]:
        """Run all examples and return comprehensive results."""
        logger.info("🚀 Starting P3IF Examples Execution")
        logger.info("=" * 60)

        start_time = time.time()

        # Run all examples
        results = {
            'cognitive_security': self.run_cognitive_security_example(),
            'healthcare': self.run_healthcare_example(),
            'framework_integration': self.run_framework_integration_example(),
            'execution_summary': {
                'start_time': datetime.now().isoformat(),
                'total_execution_time': None,
                'overall_status': None
            }
        }

        end_time = time.time()
        results['execution_summary']['total_execution_time'] = end_time - start_time

        # Calculate overall status
        successful_examples = sum(1 for r in results.values()
                                if isinstance(r, dict) and r.get('status') == 'success')
        total_examples = len([r for r in results.values()
                            if isinstance(r, dict) and 'status' in r])

        results['execution_summary']['overall_status'] = (
            'success' if successful_examples == total_examples else 'partial'
        )

        # Generate summary report
        self.generate_summary_report(results)

        # Save detailed results
        results_file = self.output_dir / "examples_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("=" * 60)
        logger.info("🎉 Examples Execution Complete")
        logger.info(f"📊 Overall Status: {results['execution_summary']['overall_status']}")
        logger.info(f"⏱️  Total Time: {results['execution_summary']['total_execution_time']:.2f}s")
        logger.info(f"📁 Results saved to: {results_file}")

        return results

    def generate_summary_report(self, results: Dict[str, Any]):
        """Generate a human-readable summary report."""
        report_file = self.output_dir / "examples_summary.md"

        with open(report_file, 'w') as f:
            f.write("# P3IF Examples Execution Summary\n\n")
            f.write(f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            summary = results['execution_summary']
            f.write(f"**Overall Status:** {summary['overall_status'].upper()}\n")
            f.write(f"**Total Execution Time:** {summary['total_execution_time']:.2f} seconds\n\n")

            f.write("## Example Results\n\n")

            for example_name, result in results.items():
                if example_name == 'execution_summary':
                    continue

                f.write(f"### {example_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Status:** {result['status'].upper()}\n\n")

                if result['status'] == 'success':
                    validation = result['validation']
                    f.write("**Validation Details:**\n")
                    for key, value in validation.items():
                        if key != 'execution_time':
                            f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
                    f.write("\n")

                f.write("---\n\n")

            f.write("## Files Generated\n\n")
            f.write("- `examples_results.json` - Detailed execution results\n")
            f.write("- `examples_summary.md` - Human-readable summary\n")
            f.write("- `examples_execution.log` - Detailed execution logs\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review the generated JSON results for detailed analysis\n")
            f.write("2. Check the execution logs for any warnings or errors\n")
            f.write("3. Use the summary to understand example capabilities\n")
            f.write("4. Explore the P3IF framework with your own data\n")


def main():
    """Main function to run all examples."""
    print("P3IF Examples Runner")
    print("====================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    runner = ExamplesRunner()
    results = runner.run_all_examples()

    # Exit with appropriate code
    exit_code = 0 if results['execution_summary']['overall_status'] == 'success' else 1

    print()
    print("=" * 50)
    if exit_code == 0:
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("🎉 Check the output/examples/ directory for results.")
    else:
        print("⚠️  SOME EXAMPLES FAILED!")
        print("🔧 Check the output/examples/ directory for details.")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
