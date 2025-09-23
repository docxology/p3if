"""
Performance monitoring and optimization utilities for P3IF.

This module provides comprehensive performance monitoring, profiling, caching,
and optimization utilities for the P3IF framework.
"""
import time
import psutil
import functools
import threading
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import logging
import json
from pathlib import Path
import cProfile
import pstats
import io
import tracemalloc

from utils.config import Config


@dataclass
class PerformanceMetrics:
    """Data class for storing performance metrics."""
    execution_time: float = 0.0
    memory_usage: int = 0  # bytes
    cpu_usage: float = 0.0
    function_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    io_operations: int = 0
    network_requests: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'function_calls': self.function_calls,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'io_operations': self.io_operations,
            'network_requests': self.network_requests,
            'timestamp': self.timestamp
        }


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[float] = None  # Time to live in seconds

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class LRUCache:
    """Least Recently Used (LRU) cache with size and TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default time to live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None

            entry.touch()
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return entry.value

    def put(self, key: str, value: Any, ttl: Optional[float] = None):
        """Put value in cache."""
        with self.lock:
            # Calculate size if possible
            size_bytes = 0
            try:
                if isinstance(value, (str, bytes)):
                    size_bytes = len(value)
                elif isinstance(value, (list, tuple, dict)):
                    size_bytes = len(str(value).encode())
            except:
                size_bytes = 64  # Default size estimate

            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                size_bytes=size_bytes,
                ttl=ttl or self.default_ttl
            )

            # Remove expired entries
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for exp_key in expired_keys:
                del self.cache[exp_key]

            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key, _ = self.cache.popitem(last=False)
                if oldest_key == key:
                    return  # Don't add if we just removed the same key

            self.cache[key] = entry
            self.cache.move_to_end(key)

    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
                'total_size_bytes': total_size
            }


class PerformanceMonitor:
    """Performance monitoring and profiling utility."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        self.active_timers: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.enabled = True
        self.logger = logging.getLogger(__name__)

    def start_timer(self, name: str):
        """Start a performance timer."""
        if not self.enabled:
            return

        with self.lock:
            if name in self.active_timers:
                self.logger.warning(f"Timer {name} already exists")
                return
            self.active_timers[name] = time.time()

    def end_timer(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[PerformanceMetrics]:
        """End a performance timer and record metrics."""
        if not self.enabled:
            return None

        with self.lock:
            if name not in self.active_timers:
                self.logger.warning(f"Timer {name} not found")
                return None

            start_time = self.active_timers[name]
            del self.active_timers[name]

            # Collect system metrics
            execution_time = time.time() - start_time
            memory_usage = psutil.Process().memory_info().rss
            cpu_usage = psutil.cpu_percent(interval=0.1)

            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage
            )

            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    setattr(metrics, key, value)

            self.metrics[name].append(metrics)
            return metrics

    def get_metrics(self, name: str) -> List[PerformanceMetrics]:
        """Get performance metrics for a specific timer."""
        return self.metrics.get(name, [])

    def get_summary_stats(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a timer."""
        metrics = self.get_metrics(name)

        if not metrics:
            return {}

        execution_times = [m.execution_time for m in metrics]
        memory_usage = [m.memory_usage for m in metrics]
        cpu_usage = [m.cpu_usage for m in metrics]

        return {
            'count': len(metrics),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_memory_usage': sum(memory_usage) / len(memory_usage),
            'max_memory_usage': max(memory_usage),
            'avg_cpu_usage': sum(cpu_usage) / len(cpu_usage),
            'total_time': sum(execution_times)
        }

    def profile_function(self, func: Callable, *args, **kwargs) -> Any:
        """Profile a function execution."""
        profiler = cProfile.Profile()
        profiler.enable()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')

            # Save stats to string buffer
            buffer = io.StringIO()
            stats.print_stats(20)  # Top 20 functions
            profile_data = buffer.getvalue()
            buffer.close()

            self.logger.info(f"Profile for {func.__name__}:\n{profile_data}")

    @contextmanager
    def memory_tracing(self, name: str = "memory_trace"):
        """Context manager for memory tracing."""
        if not self.enabled:
            yield
            return

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        try:
            yield
        finally:
            snapshot2 = tracemalloc.take_snapshot()
            tracemalloc.stop()

            # Analyze memory differences
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')[:10]

            self.logger.info(f"Memory trace for {name}:")
            for stat in top_stats:
                self.logger.info(f"  {stat}")

    def reset(self):
        """Reset all metrics."""
        with self.lock:
            self.metrics.clear()
            self.active_timers.clear()


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()

# Global cache instances
_global_cache = LRUCache(max_size=1000, default_ttl=300)  # 5 minutes default TTL
_framework_cache = LRUCache(max_size=500, default_ttl=600)  # 10 minutes default TTL
_visualization_cache = LRUCache(max_size=100, default_ttl=1800)  # 30 minutes default TTL


def performance_timer(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for timing function execution."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            monitor.start_timer(name)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.end_timer(name, metadata)

        return wrapper
    return decorator


def cached(cache_key: str = None, ttl: Optional[float] = None):
    """Decorator for caching function results."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key:
                key = cache_key
            else:
                key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Try to get from cache
            cache = get_cache()
            cached_result = cache.get(key)

            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.put(key, result, ttl)
            return result

        return wrapper
    return decorator


def memoize(func: Callable):
    """Memoization decorator using LRU cache."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key_parts = [func.__name__]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)

        # Use global cache
        cache = get_cache()
        cached_result = cache.get(key)

        if cached_result is not None:
            return cached_result

        result = func(*args, **kwargs)
        cache.put(key, result)
        return result

    return wrapper


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor


def get_cache(cache_type: str = 'global') -> LRUCache:
    """Get cache instance by type."""
    caches = {
        'global': _global_cache,
        'framework': _framework_cache,
        'visualization': _visualization_cache
    }
    return caches.get(cache_type, _global_cache)


def clear_cache(cache_type: str = 'global'):
    """Clear cache by type."""
    cache = get_cache(cache_type)
    cache.clear()


def clear_all_caches():
    """Clear all caches."""
    _global_cache.clear()
    _framework_cache.clear()
    _visualization_cache.clear()


@contextmanager
def performance_context(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_timer(name)
    try:
        yield
    finally:
        monitor.end_timer(name, metadata)


async def async_performance_timer(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Async context manager for performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_timer(name)
    try:
        return await asyncio.coroutine(lambda: None)()
    finally:
        monitor.end_timer(name, metadata)


def optimize_dataframe_operations():
    """Optimize pandas DataFrame operations for better performance."""
    try:
        import pandas as pd

        # Set performance-oriented options
        pd.set_option('mode.chained_assignment', None)  # Disable chained assignment warnings
        pd.set_option('mode.use_inf_as_na', True)  # Handle inf as NaN

        # Use more efficient dtypes where possible
        # This would be applied in data processing functions

    except ImportError:
        pass  # pandas not available


def optimize_memory_usage():
    """Optimize memory usage for the application."""
    try:
        import gc

        # Force garbage collection
        gc.collect()

        # Get memory usage info
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent()
        }

    except ImportError:
        return {'error': 'psutil not available'}


def get_system_resources():
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            'cpu_percent': cpu_percent,
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'free': disk.free,
                'percent': disk.percent,
                'used': disk.used
            }
        }

    except ImportError:
        return {'error': 'psutil not available'}


def create_performance_report(output_file: Optional[str] = None) -> Dict[str, Any]:
    """Create a comprehensive performance report.

    Args:
        output_file: Optional file path to save the report

    Returns:
        Dictionary containing performance report
    """
    monitor = get_performance_monitor()

    report = {
        'timestamp': datetime.now().isoformat(),
        'system_resources': get_system_resources(),
        'memory_usage': optimize_memory_usage(),
        'cache_stats': {},
        'performance_metrics': {},
        'summary': {}
    }

    # Cache statistics
    for cache_type in ['global', 'framework', 'visualization']:
        cache = get_cache(cache_type)
        report['cache_stats'][cache_type] = cache.stats()

    # Performance metrics summary
    total_timers = 0
    total_measurements = 0
    total_time = 0.0

    for timer_name, metrics_list in monitor.metrics.items():
        if metrics_list:
            total_timers += 1
            total_measurements += len(metrics_list)
            total_time += sum(m.execution_time for m in metrics_list)

            report['performance_metrics'][timer_name] = monitor.get_summary_stats(timer_name)

    report['summary'] = {
        'total_timers': total_timers,
        'total_measurements': total_measurements,
        'total_execution_time': total_time,
        'average_execution_time': total_time / max(total_measurements, 1)
    }

    # Save to file if specified
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    return report


# Initialize performance optimizations
optimize_dataframe_operations()
