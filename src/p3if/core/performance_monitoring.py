"""
Performance monitoring and optimization utilities for P3IF.

This module provides comprehensive performance monitoring, profiling, and optimization
capabilities for P3IF operations and frameworks.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
import threading
import logging
from collections import defaultdict, deque
from contextlib import contextmanager

from .caching import CacheManager, CacheStrategy
from .framework import P3IFFramework


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific operation."""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_usage: int = 0  # bytes
    cpu_usage: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self):
        """Mark the operation as finished and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "error_count": self.error_count,
            "metadata": self.metadata
        }


class PerformanceMonitor:
    """Comprehensive performance monitoring for P3IF operations."""

    def __init__(self, max_history: int = 1000, enable_system_metrics: bool = True):
        self.max_history = max_history
        self.enable_system_metrics = enable_system_metrics
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, PerformanceMetrics] = {}
        self.aggregates: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)

        # System monitoring
        self.process = psutil.Process() if PSUTIL_AVAILABLE else None
        self.system_start_time = time.time()

    def start_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start monitoring an operation."""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            metadata=metadata or {}
        )

        self.active_operations[operation_id] = metrics
        return operation_id

    def end_operation(self, operation_id: str, error: Optional[Exception] = None) -> Optional[PerformanceMetrics]:
        """End monitoring an operation."""
        if operation_id not in self.active_operations:
            self.logger.warning(f"Operation {operation_id} not found in active operations")
            return None

        metrics = self.active_operations[operation_id]

        # Get current system metrics
        if self.enable_system_metrics and self.process:
            try:
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()
                metrics.memory_usage = memory_info.rss
                metrics.cpu_usage = cpu_percent
            except Exception as e:
                self.logger.warning(f"Failed to get system metrics: {e}")

        # Update error count
        if error:
            metrics.error_count += 1

        # Finish the operation
        metrics.finish()

        # Add to history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)

        # Update aggregates
        self._update_aggregates(metrics)

        # Remove from active operations
        del self.active_operations[operation_id]

        return metrics

    def get_operation_metrics(self, operation_name: str, limit: Optional[int] = None) -> List[PerformanceMetrics]:
        """Get metrics for a specific operation."""
        matching_metrics = [
            m for m in self.metrics_history
            if m.operation_name == operation_name
        ]

        if limit:
            return matching_metrics[-limit:]
        return matching_metrics

    def get_aggregate_metrics(self, operation_name: str) -> Dict[str, float]:
        """Get aggregated metrics for an operation."""
        return self.aggregates.get(operation_name, {})

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        if not PSUTIL_AVAILABLE:
            return {"uptime_seconds": time.time() - self.system_start_time}
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk_usage = psutil.disk_usage('/')

            return {
                "memory_total": memory.total,
                "memory_used": memory.used,
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
                "disk_total": disk_usage.total,
                "disk_used": disk_usage.used,
                "disk_percent": disk_usage.percent,
                "uptime_seconds": time.time() - self.system_start_time
            }
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary."""
        if not self.metrics_history:
            return {"message": "No performance data available"}

        total_operations = len(self.metrics_history)
        total_duration = sum(m.duration for m in self.metrics_history if m.duration)
        avg_duration = total_duration / total_operations if total_operations > 0 else 0

        error_operations = sum(1 for m in self.metrics_history if m.error_count > 0)
        error_rate = error_operations / total_operations if total_operations > 0 else 0

        return {
            "total_operations": total_operations,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "error_count": error_operations,
            "error_rate": error_rate,
            "active_operations": len(self.active_operations),
            "system_metrics": self.get_system_metrics()
        }

    def _update_aggregates(self, metrics: PerformanceMetrics):
        """Update aggregate statistics for an operation."""
        op_name = metrics.operation_name
        current_agg = self.aggregates[op_name]

        # Update counters
        current_agg["count"] = current_agg.get("count", 0) + 1
        current_agg["total_duration"] = current_agg.get("total_duration", 0) + (metrics.duration or 0)
        current_agg["total_memory"] = current_agg.get("total_memory", 0) + metrics.memory_usage
        current_agg["total_errors"] = current_agg.get("total_errors", 0) + metrics.error_count

        # Update averages
        count = current_agg["count"]
        current_agg["avg_duration"] = current_agg["total_duration"] / count
        current_agg["avg_memory"] = current_agg["total_memory"] / count
        current_agg["error_rate"] = current_agg["total_errors"] / count

        # Update min/max
        if "min_duration" not in current_agg or metrics.duration < current_agg["min_duration"]:
            current_agg["min_duration"] = metrics.duration
        if "max_duration" not in current_agg or metrics.duration > current_agg["max_duration"]:
            current_agg["max_duration"] = metrics.duration

    def clear_history(self):
        """Clear performance history."""
        self.metrics_history.clear()
        self.aggregates.clear()


@contextmanager
def monitor_operation(operation_name: str, monitor: Optional[PerformanceMonitor] = None,
                     metadata: Optional[Dict[str, Any]] = None):
    """Context manager for monitoring operations."""
    if monitor is None:
        monitor = get_global_performance_monitor()

    operation_id = monitor.start_operation(operation_name, metadata)

    try:
        yield operation_id
    except Exception as e:
        monitor.end_operation(operation_id, e)
        raise
    else:
        monitor.end_operation(operation_id)


class P3IFPerformanceOptimizer:
    """Performance optimization utilities for P3IF frameworks."""

    def __init__(self, framework: P3IFFramework, monitor: Optional[PerformanceMonitor] = None):
        self.framework = framework
        self.monitor = monitor or PerformanceMonitor()
        self.optimization_cache: Dict[str, Any] = {}

    def optimize_pattern_queries(self, query_patterns: List[str]) -> Dict[str, Any]:
        """Optimize pattern queries for better performance."""
        cache_key = f"pattern_query_{hash(tuple(query_patterns))}"

        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]

        with monitor_operation("pattern_query_optimization", self.monitor):
            optimization = {
                "query_patterns": query_patterns,
                "estimated_cost": len(query_patterns) * 10,  # Simple cost model
                "suggested_indexing": [],
                "caching_strategy": "lru"
            }

            # Analyze query patterns and suggest optimizations
            if len(query_patterns) > 100:
                optimization["suggested_indexing"].append("domain_index")
                optimization["caching_strategy"] = "ttl"

            self.optimization_cache[cache_key] = optimization
            return optimization

    def optimize_relationship_queries(self, relationship_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize relationship queries."""
        cache_key = f"relationship_query_{hash(str(relationship_criteria))}"

        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]

        with monitor_operation("relationship_query_optimization", self.monitor):
            optimization = {
                "criteria": relationship_criteria,
                "estimated_cost": sum(len(str(v)) if hasattr(v, '__len__') else 1 for v in relationship_criteria.values()) * 5,
                "suggested_filters": [],
                "caching_strategy": "lru"
            }

            # Analyze criteria and suggest optimizations
            if "strength_threshold" in relationship_criteria:
                optimization["suggested_filters"].append("strength_index")

            if "domain" in relationship_criteria:
                optimization["suggested_filters"].append("domain_filter")

            self.optimization_cache[cache_key] = optimization
            return optimization

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on usage patterns."""
        recommendations = []

        # Analyze operation patterns
        operation_counts = defaultdict(int)
        for metrics in self.monitor.metrics_history:
            operation_counts[metrics.operation_name] += 1

        # Recommend optimizations based on usage
        if operation_counts.get("pattern_query", 0) > 100:
            recommendations.append("Consider implementing pattern indexing for frequent queries")

        if operation_counts.get("relationship_query", 0) > 50:
            recommendations.append("Consider relationship caching for improved performance")

        if self.monitor.get_system_metrics().get("memory_percent", 0) > 80:
            recommendations.append("High memory usage detected - consider data sampling or pagination")

        return recommendations

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        return {
            "framework_stats": {
                "total_patterns": len(self.framework),
                "total_relationships": len(self.framework.get_all_relationships()),
                "domains": len(set(p.domain for p in self.framework if hasattr(p, 'domain') and p.domain))
            },
            "performance_summary": self.monitor.get_performance_summary(),
            "optimization_recommendations": self.get_optimization_recommendations(),
            "cache_stats": self._get_cache_statistics(),
            "timestamp": datetime.now().isoformat()
        }

    def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "cache_enabled": True,
            "cache_size": len(self.optimization_cache),
            "cache_memory_usage": sum(len(str(v)) for v in self.optimization_cache.values()),
            "recommendations": "Consider cache size limits for large datasets"
        }


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_performance_monitor() -> PerformanceMonitor:
    """Get or create the global performance monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def configure_global_monitoring(max_history: int = 1000, enable_system_metrics: bool = True):
    """Configure the global performance monitor."""
    global _global_monitor
    _global_monitor = PerformanceMonitor(max_history, enable_system_metrics)


def reset_global_monitoring():
    """Reset the global performance monitor."""
    global _global_monitor
    if _global_monitor:
        _global_monitor.clear_history()
    _global_monitor = None


@contextmanager
def performance_monitored(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for automatic performance monitoring."""
    monitor = get_global_performance_monitor()

    with monitor_operation(operation_name, monitor, metadata):
        yield

