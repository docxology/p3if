#!/usr/bin/env python3
"""
Performance benchmarking script for P3IF framework.

This script measures and compares performance of various P3IF operations
to identify bottlenecks and validate optimizations.
"""
import time
import psutil
import tracemalloc
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import sys

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.framework import P3IFFramework
from visualization.interactive import InteractiveVisualizer
from utils.performance import (
    get_performance_monitor, clear_all_caches,
    create_performance_report, optimize_memory_usage
)
from tests.utils import (
    create_test_patterns_with_relationships,
    create_multi_domain_test_framework,
    create_large_test_framework
)


class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite."""

    def __init__(self, output_file: Optional[str] = None):
        """Initialize the benchmark suite.

        Args:
            output_file: Optional file to save results
        """
        self.output_file = output_file
        self.results: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': {},
            'summary': {}
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for the benchmark."""
        try:
            import platform
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available
            }
        except ImportError:
            return {'error': 'psutil not available'}

    def _time_operation(self, operation_name: str, func, *args, **kwargs) -> Dict[str, Any]:
        """Time a single operation and collect metrics.

        Args:
            operation_name: Name of the operation
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Dictionary with timing and performance metrics
        """
        # Start memory tracing
        tracemalloc.start()
        start_memory = psutil.Process().memory_info().rss
        start_time = time.time()

        # Execute the operation
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False

        # End timing
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        # Get memory snapshots
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            'operation': operation_name,
            'success': success,
            'execution_time': end_time - start_time,
            'memory_start': start_memory,
            'memory_end': end_memory,
            'memory_delta': end_memory - start_memory,
            'memory_current': current,
            'memory_peak': peak,
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'result_size': self._get_object_size(result) if result else 0
        }

    def _get_object_size(self, obj) -> int:
        """Get approximate size of an object in bytes."""
        try:
            return len(str(obj).encode('utf-8'))
        except:
            return 0

    def benchmark_framework_creation(self, sizes: List[int]) -> Dict[str, Any]:
        """Benchmark framework creation with different sizes."""
        results = {}

        for size in sizes:
            patterns_per_type = size // 3
            relationships = size * 2

            result = self._time_operation(
                f"create_framework_{size}",
                create_test_patterns_with_relationships,
                num_patterns=patterns_per_type,
                num_relationships=relationships
            )

            results[f"size_{size}"] = result

        return results

    def benchmark_metrics_calculation(self, framework: P3IFFramework, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark metrics calculation performance."""
        results = []

        # Warm up the cache
        framework.get_metrics()

        for i in range(iterations):
            result = self._time_operation(
                f"calculate_metrics_{i}",
                framework.get_metrics,
                force_refresh=True
            )
            results.append(result)

        # Calculate statistics
        avg_time = sum(r['execution_time'] for r in results) / len(results)
        min_time = min(r['execution_time'] for r in results)
        max_time = max(r['execution_time'] for r in results)

        return {
            'individual_results': results,
            'statistics': {
                'iterations': iterations,
                'average_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'variance': sum((r['execution_time'] - avg_time) ** 2 for r in results) / len(results)
            }
        }

    def benchmark_pattern_queries(self, framework: P3IFFramework, num_queries: int = 50) -> Dict[str, Any]:
        """Benchmark pattern query performance."""
        all_patterns = list(framework._patterns.values())
        query_results = {}

        # Benchmark different query types
        query_types = [
            ('by_type', lambda: framework.get_patterns_by_type_optimized("property")),
            ('by_domain', lambda: framework.get_patterns_by_domain_optimized("test_domain")),
            ('search', lambda: framework.search_patterns_optimized("Test", limit=10)),
            ('collection', lambda: framework.get_pattern_collection()),
        ]

        for query_name, query_func in query_types:
            results = []
            for _ in range(num_queries):
                result = self._time_operation(f"{query_name}_query", query_func)
                results.append(result)

            avg_time = sum(r['execution_time'] for r in results) / len(results)
            query_results[query_name] = {
                'individual_results': results,
                'average_time': avg_time,
                'num_queries': num_queries
            }

        return query_results

    def benchmark_visualization_generation(self, framework: P3IFFramework) -> Dict[str, Any]:
        """Benchmark visualization generation performance."""
        visualizer = InteractiveVisualizer(framework)

        visualization_types = [
            ('3d_cube', lambda: visualizer.generate_3d_cube_data()),
            ('3d_cube_domain', lambda: visualizer.generate_3d_cube_data(domains=["test_domain"])),
            ('force_graph', lambda: visualizer.generate_force_directed_graph_data()),
            ('dashboard', lambda: visualizer.generate_modern_dashboard()),
        ]

        results = {}
        for viz_name, viz_func in visualization_types:
            result = self._time_operation(f"generate_{viz_name}", viz_func)
            results[viz_name] = result

        return results

    def benchmark_concurrent_operations(self, framework: P3IFFramework, num_threads: int = 4) -> Dict[str, Any]:
        """Benchmark concurrent operations performance."""
        import concurrent.futures

        def add_pattern_operation(pattern_id: int):
            from core.models import Property
            pattern = Property(
                name=f"Benchmark Property {pattern_id}",
                description=f"Test property {pattern_id}",
                domain="benchmark_domain"
            )
            framework.add_pattern(pattern)
            return pattern.id

        def query_operation():
            return len(framework.get_patterns_by_type_optimized("property"))

        # Test concurrent pattern addition
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            pattern_ids = list(executor.map(add_pattern_operation, range(100)))

        add_time = time.time() - start_time

        # Test concurrent queries
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            query_results = list(executor.map(lambda x: query_operation(), range(50)))

        query_time = time.time() - start_time

        return {
            'concurrent_add': {
                'num_threads': num_threads,
                'patterns_added': len(pattern_ids),
                'total_time': add_time,
                'time_per_pattern': add_time / len(pattern_ids)
            },
            'concurrent_query': {
                'num_threads': num_threads,
                'queries_executed': len(query_results),
                'total_time': query_time,
                'time_per_query': query_time / len(query_results)
            }
        }

    def benchmark_memory_usage(self, framework: P3IFFramework) -> Dict[str, Any]:
        """Benchmark memory usage patterns."""
        memory_results = {}

        # Test memory usage with different operations
        operations = [
            ('empty', lambda: None),
            ('load_patterns', lambda: len(framework._patterns)),
            ('load_relationships', lambda: len(framework._relationships)),
            ('calculate_metrics', lambda: framework.get_metrics()),
            ('create_visualization', lambda: InteractiveVisualizer(framework).generate_3d_cube_data()),
        ]

        for op_name, op_func in operations:
            # Force garbage collection
            import gc
            gc.collect()

            initial_memory = psutil.Process().memory_info().rss

            # Execute operation
            result = op_func()

            # Force garbage collection again
            gc.collect()

            final_memory = psutil.Process().memory_info().rss
            memory_delta = final_memory - initial_memory

            memory_results[op_name] = {
                'memory_before': initial_memory,
                'memory_after': final_memory,
                'memory_delta': memory_delta,
                'result_size': self._get_object_size(result) if result else 0
            }

        return memory_results

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run a comprehensive performance benchmark."""
        print("🚀 Starting P3IF Performance Benchmark Suite")
        print("=" * 60)

        # Clear caches for fair benchmarking
        clear_all_caches()

        # Test different framework sizes
        print("\n📊 Benchmarking Framework Creation")
        framework_sizes = [100, 500, 1000, 2000]
        creation_results = self.benchmark_framework_creation(framework_sizes)

        # Create a medium-sized framework for other tests
        print("\n🏗️ Creating Test Framework (1000 patterns)")
        framework = create_test_patterns_with_relationships(
            num_patterns=1000,
            num_relationships=2000
        )

        # Benchmark metrics calculation
        print("\n📈 Benchmarking Metrics Calculation")
        metrics_results = self.benchmark_metrics_calculation(framework, iterations=20)

        # Benchmark pattern queries
        print("\n🔍 Benchmarking Pattern Queries")
        query_results = self.benchmark_pattern_queries(framework, num_queries=100)

        # Benchmark visualization generation
        print("\n🎨 Benchmarking Visualization Generation")
        viz_results = self.benchmark_visualization_generation(framework)

        # Benchmark concurrent operations
        print("\n⚡ Benchmarking Concurrent Operations")
        concurrent_results = self.benchmark_concurrent_operations(framework, num_threads=4)

        # Benchmark memory usage
        print("\n🧠 Benchmarking Memory Usage")
        memory_results = self.benchmark_memory_usage(framework)

        # Compile results
        self.results['benchmarks'] = {
            'framework_creation': creation_results,
            'metrics_calculation': metrics_results,
            'pattern_queries': query_results,
            'visualization_generation': viz_results,
            'concurrent_operations': concurrent_results,
            'memory_usage': memory_results
        }

        # Calculate summary statistics
        self._calculate_summary()

        return self.results

    def _calculate_summary(self):
        """Calculate summary statistics from benchmark results."""
        benchmarks = self.results['benchmarks']

        # Extract key metrics
        summary = {
            'total_operations': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'memory_efficiency': {},
            'performance_scores': {}
        }

        # Count operations and calculate totals
        for category, results in benchmarks.items():
            if isinstance(results, dict) and 'individual_results' in results:
                # Metrics calculation results
                individual_results = results['individual_results']
                summary['total_operations'] += len(individual_results)
                summary['total_execution_time'] += sum(r['execution_time'] for r in individual_results)

        if summary['total_operations'] > 0:
            summary['average_execution_time'] = summary['total_execution_time'] / summary['total_operations']

        # Memory efficiency analysis
        if 'memory_usage' in benchmarks:
            memory_ops = benchmarks['memory_usage']

            # Find most memory-efficient operations
            memory_deltas = {k: v['memory_delta'] for k, v in memory_ops.items()}
            min_memory_op = min(memory_deltas, key=memory_deltas.get)
            max_memory_op = max(memory_deltas, key=memory_deltas.get)

            summary['memory_efficiency'] = {
                'most_efficient': min_memory_op,
                'least_efficient': max_memory_op,
                'average_memory_delta': sum(memory_deltas.values()) / len(memory_deltas)
            }

        # Performance scores (lower is better)
        if 'metrics_calculation' in benchmarks:
            metrics_stats = benchmarks['metrics_calculation']['statistics']
            summary['performance_scores'] = {
                'metrics_calculation_avg': metrics_stats['average_time'],
                'metrics_calculation_consistency': metrics_stats['variance']
            }

        self.results['summary'] = summary

    def print_results(self):
        """Print formatted benchmark results."""
        print("\n" + "=" * 80)
        print("📋 P3IF PERFORMANCE BENCHMARK RESULTS")
        print("=" * 80)

        if not self.results['benchmarks']:
            print("❌ No benchmark results available")
            return

        # System information
        print("🖥️ SYSTEM INFORMATION")
        sys_info = self.results['system_info']
        for key, value in sys_info.items():
            print(f"  {key}: {value}")
        print()

        # Summary
        summary = self.results['summary']
        print("📊 SUMMARY")
        print(f"  Total Operations: {summary['total_operations']}")
        print(f"  Total Execution Time: {summary['total_execution_time']".4f"}s")
        print(f"  Average Execution Time: {summary['average_execution_time']".4f"}s")
        print()

        # Detailed results by category
        for category, results in self.results['benchmarks'].items():
            print(f"🔧 {category.upper().replace('_', ' ')}")
            print("-" * 40)

            if category == 'framework_creation':
                for size_key, result in results.items():
                    print(f"  Size {size_key}: {result['execution_time']".4f"}s "
                          f"({result['memory_delta'] / 1024 / 1024".1f"} MB)")

            elif 'individual_results' in results:
                avg_time = results['statistics']['average_time']
                min_time = results['statistics']['min_time']
                max_time = results['statistics']['max_time']
                print(f"  Average: {avg_time".4f"}s")
                print(f"  Range: {min_time".4f"}s - {max_time".4f"}s")

            elif category == 'memory_usage':
                for op_name, mem_data in results.items():
                    print(f"  {op_name}: {mem_data['memory_delta'] / 1024 / 1024".1f"} MB")

            elif category == 'concurrent_operations':
                add_stats = results['concurrent_add']
                query_stats = results['concurrent_query']
                print(f"  Pattern Addition: {add_stats['time_per_pattern']".4f"}s/pattern")
                print(f"  Query Performance: {query_stats['time_per_query']".4f"}s/query")

            print()

        # Performance recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 40)

        if summary['average_execution_time'] > 1.0:
            print("⚠️ Consider optimizing slow operations for better performance")
        else:
            print("✅ Overall performance is good")

        if 'memory_efficiency' in summary:
            mem_eff = summary['memory_efficiency']
            if mem_eff['average_memory_delta'] > 50 * 1024 * 1024:  # 50MB
                print("⚠️ High memory usage detected - consider memory optimization")
            else:
                print("✅ Memory usage is within acceptable limits")

        print("=" * 80)

    def save_results(self):
        """Save benchmark results to file."""
        if self.output_file:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"💾 Results saved to: {self.output_file}")


def main():
    """Main function to run benchmarks."""
    parser = argparse.ArgumentParser(description='Run P3IF performance benchmarks')
    parser.add_argument('--output', '-o', type=str, help='Output file for results')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark (smaller sizes)')
    parser.add_argument('--full', action='store_true', help='Run full benchmark (larger sizes)')

    args = parser.parse_args()

    # Determine benchmark size
    if args.quick:
        framework_sizes = [50, 100, 200]
        iterations = 5
    elif args.full:
        framework_sizes = [500, 1000, 2000, 5000]
        iterations = 20
    else:
        framework_sizes = [100, 500, 1000]
        iterations = 10

    # Initialize benchmark suite
    benchmark = PerformanceBenchmark(output_file=args.output)

    try:
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()

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
