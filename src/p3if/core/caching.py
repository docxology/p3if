"""
P3IF Caching and Performance Optimization

This module provides caching and performance optimization methods for P3IF operations.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Hashable
from dataclasses import dataclass, field
from enum import Enum
import time
import hashlib
from collections import OrderedDict
import logging
import functools


class CacheStrategy(str, Enum):
    """Caching strategies."""
    LRU = "lru"
    TTL = "ttl"
    SIZE_LIMITED = "size_limited"
    NO_CACHE = "no_cache"


@dataclass
class CacheEntry:
    """A single cache entry."""
    key: str
    value: Any
    timestamp: float
    ttl: Optional[float] = None
    access_count: int = 0
    size: int = 0

    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def access(self):
        """Record an access to this entry."""
        self.access_count += 1
        self.timestamp = time.time()


class CacheManager:
    """Manages caching for P3IF operations."""

    def __init__(self, strategy: CacheStrategy = CacheStrategy.LRU,
                 max_size: int = 1000, default_ttl: Optional[float] = None):
        self.strategy = strategy
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.logger = logging.getLogger(__name__)

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function call information."""
        # Create a hash of the function name and arguments
        key_data = {
            "function": func_name,
            "args": str(args),
            "kwargs": str(sorted(kwargs.items()))
        }
        key_string = str(key_data)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        # Check TTL
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None

        # Update access information
        entry.access()

        # For LRU, move to end
        if self.strategy == CacheStrategy.LRU:
            self.cache.move_to_end(key)

        self.hits += 1
        return entry.value

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put a value in cache."""
        # Check size limits
        if len(self.cache) >= self.max_size:
            if self.strategy == CacheStrategy.SIZE_LIMITED:
                # Remove oldest entry
                oldest_key, oldest_entry = next(iter(self.cache.items()))
                del self.cache[oldest_key]
            elif self.strategy == CacheStrategy.LRU:
                # Remove least recently used
                oldest_key, _ = self.cache.popitem(last=False)
            else:
                # Simple removal of oldest
                oldest_key, _ = self.cache.popitem(last=False)

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl,
            size=len(str(value)) if value else 0
        )

        self.cache[key] = entry

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "strategy": self.strategy.value,
            "max_size": self.max_size,
            "current_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


def cached(cache_manager: Optional[CacheManager] = None,
           ttl: Optional[float] = None, cache_key: Optional[str] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache manager or global default
            cm = cache_manager or _global_cache_manager

            # Generate cache key
            if cache_key:
                key = cache_key
            else:
                key = cm._generate_key(func.__name__, args, kwargs)

            # Try to get from cache
            cached_result = cm.get(key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache the result
            cm.put(key, result, ttl)

            return result
        return wrapper
    return decorator


class PerformanceOptimizer:
    """Optimizes P3IF operations for better performance."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)

    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return PerformanceTimer(self, operation_name)

    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric."""
        self.metrics[metric_name].append(value)
        self.logger.debug(f"Recorded {metric_name}: {value}")

    def get_average_metric(self, metric_name: str) -> float:
        """Get the average value of a metric."""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return 0.0
        return sum(self.metrics[metric_name]) / len(self.metrics[metric_name])

    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get a summary of all metrics."""
        summary = {}
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "total": sum(values)
                }
        return summary

    def optimize_query(self, query_func: Callable, data: List[Any],
                      optimization_hints: Dict[str, Any] = None) -> Any:
        """Optimize a query operation based on data characteristics."""
        optimization_hints = optimization_hints or {}

        data_size = len(data)
        self.record_metric("query_data_size", data_size)

        # Choose optimization strategy based on data size and hints
        if data_size < 100:
            # Small dataset: no optimization needed
            return query_func(data)
        elif data_size < 1000:
            # Medium dataset: basic indexing
            return self._optimized_query_small(query_func, data)
        else:
            # Large dataset: advanced optimization
            return self._optimized_query_large(query_func, data, optimization_hints)

    def _optimized_query_small(self, query_func: Callable, data: List[Any]) -> Any:
        """Optimized query for small datasets."""
        start_time = time.time()
        result = query_func(data)
        execution_time = time.time() - start_time

        self.record_metric("small_query_time", execution_time)
        return result

    def _optimized_query_large(self, query_func: Callable, data: List[Any],
                              hints: Dict[str, Any]) -> Any:
        """Optimized query for large datasets."""
        start_time = time.time()

        # Apply optimizations based on hints
        if hints.get("sort_first", False):
            data = sorted(data, key=lambda x: getattr(x, hints.get("sort_key", "name"), ""))

        if hints.get("use_index", False):
            # Create index if beneficial
            index = {}
            for item in data:
                key_value = getattr(item, hints.get("index_key", "name"), "")
                if key_value not in index:
                    index[key_value] = []
                index[key_value].append(item)
            data = index  # Replace with indexed structure

        result = query_func(data)
        execution_time = time.time() - start_time

        self.record_metric("large_query_time", execution_time)
        return result

    def suggest_optimizations(self, operation_history: List[Dict[str, Any]]) -> List[str]:
        """Suggest optimizations based on operation history."""
        suggestions = []

        if not operation_history:
            return suggestions

        # Analyze patterns in operation history
        operation_times = [op.get("execution_time", 0) for op in operation_history]
        avg_time = sum(operation_times) / len(operation_times) if operation_times else 0

        if avg_time > 1.0:  # Operations taking more than 1 second
            suggestions.append("Consider implementing caching for expensive operations")

        if len(operation_history) > 100:
            suggestions.append("High operation volume detected - consider batch processing")

        # Check for repeated operations
        operation_names = [op.get("operation", "") for op in operation_history]
        if len(set(operation_names)) < len(operation_names) * 0.3:  # Low diversity
            suggestions.append("High operation repetition - implement result caching")

        return suggestions


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, optimizer: PerformanceOptimizer, operation_name: str):
        self.optimizer = optimizer
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            execution_time = time.time() - self.start_time
            self.optimizer.record_metric(f"{self.operation_name}_time", execution_time)


# Global cache manager instance
_global_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _global_cache_manager


def configure_global_cache(strategy: CacheStrategy = CacheStrategy.LRU,
                          max_size: int = 1000, ttl: Optional[float] = None):
    """Configure the global cache manager."""
    global _global_cache_manager
    _global_cache_manager = CacheManager(strategy, max_size, ttl)
