#!/usr/bin/env python3
"""
Performance benchmarking script for P3IF framework.

Thin orchestrator: parses CLI arguments and delegates to the
PerformanceBenchmark suite in src/p3if/utils/benchmark.py, which owns all
measurement, statistics, and reporting logic (2026-09 audit).
"""
import argparse
from pathlib import Path
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from p3if.utils.benchmark import PerformanceBenchmark


def main():
    """Main function to run benchmarks."""
    parser = argparse.ArgumentParser(description='Run P3IF performance benchmarks')
    parser.add_argument('--output', '-o', type=str, help='Output file for results')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark (smaller sizes)')
    parser.add_argument('--full', action='store_true', help='Run full benchmark (larger sizes)')

    args = parser.parse_args()

    # Initialize benchmark suite
    benchmark = PerformanceBenchmark(output_file=args.output)

    try:
        # Run comprehensive benchmark
        benchmark.run_comprehensive_benchmark()

        # Print results
        benchmark.print_results()

        # Save if output file specified
        benchmark.save_results()

        print("\n🎉 Benchmark completed successfully!")

    except Exception as e:
        print(f"❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
