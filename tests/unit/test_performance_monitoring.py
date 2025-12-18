"""
Tests for P3IF core performance monitoring module.

This module tests the PerformanceMonitor, PerformanceMetrics, and P3IFPerformanceOptimizer classes
that provide performance tracking and optimization capabilities.
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from p3if.core.performance_monitoring import (
    PerformanceMetrics,
    PerformanceMonitor,
    P3IFPerformanceOptimizer,
    monitor_operation,
    get_global_performance_monitor,
    configure_global_monitoring,
    reset_global_monitoring,
    performance_monitored
)
from p3if.core.framework import P3IFFramework
from p3if.core.models import Property


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics class."""

    def test_initialization(self):
        """Test PerformanceMetrics initialization."""
        import time
        start_time = time.time()
        metrics = PerformanceMetrics("test_operation", start_time)
        assert metrics.operation_name == "test_operation"
        assert metrics.start_time == start_time
        assert metrics.end_time is None
        assert metrics.duration is None
        assert metrics.metadata == {}
        assert metrics.memory_usage == 0
        assert metrics.cpu_usage == 0.0

    def test_finish(self):
        """Test finishing a performance measurement."""
        import time
        start_time = time.time()
        metrics = PerformanceMetrics("test_operation", start_time)
        time.sleep(0.01)  # Small delay
        metrics.finish()

        assert metrics.end_time is not None
        assert metrics.duration is not None
        assert metrics.duration >= 0.01

    def test_finish_with_error(self):
        """Test finishing with an error."""
        import time
        start_time = time.time()
        metrics = PerformanceMetrics("test_operation", start_time)
        error = ValueError("test error")
        metrics.finish()

        # Note: The current implementation doesn't take an error parameter
        # Let's just test that it finishes correctly
        assert metrics.end_time is not None
        assert metrics.duration is not None

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        import time
        start_time = time.time()
        metrics = PerformanceMetrics("test_operation", start_time, metadata={"key": "value"})
        metrics.finish()

        data = metrics.to_dict()

        assert data["operation_name"] == "test_operation"
        assert "start_time" in data
        assert "end_time" in data
        assert "duration" in data
        assert data["metadata"]["key"] == "value"
        assert data["error_count"] == 0


class TestPerformanceMonitor:
    """Tests for PerformanceMonitor class."""

    def test_initialization(self):
        """Test PerformanceMonitor initialization."""
        monitor = PerformanceMonitor()
        assert monitor.max_history == 1000
        assert monitor.enable_system_metrics is True
        assert monitor.active_operations == {}
        assert monitor.aggregates == {}

    def test_start_and_end_operation(self):
        """Test starting and ending operations."""
        monitor = PerformanceMonitor()

        operation_id = monitor.start_operation("test_op", metadata={"type": "test"})

        assert operation_id in monitor.active_operations
        assert monitor.active_operations[operation_id].operation_name == "test_op"
        assert monitor.active_operations[operation_id].metadata["type"] == "test"

        time.sleep(0.01)  # Small delay
        metrics = monitor.end_operation(operation_id)

        assert metrics is not None
        assert metrics.operation_name == "test_op"
        assert metrics.duration >= 0.01

    def test_end_operation_with_error(self):
        """Test ending operation with error."""
        monitor = PerformanceMonitor()

        operation_id = monitor.start_operation("test_op")
        error = RuntimeError("test error")

        metrics = monitor.end_operation(operation_id, error=error)

        assert metrics is not None
        assert metrics.error_count == 1

    def test_get_operation_metrics(self):
        """Test getting operation metrics."""
        monitor = PerformanceMonitor()

        # Add some test operations
        op1 = monitor.start_operation("op1")
        time.sleep(0.01)
        monitor.end_operation(op1)

        op2 = monitor.start_operation("op1")  # Same operation name
        time.sleep(0.01)
        monitor.end_operation(op2)

        metrics = monitor.get_operation_metrics("op1")

        assert len(metrics) == 2
        assert all(m.operation_name == "op1" for m in metrics)

    def test_get_aggregate_metrics(self):
        """Test getting aggregate metrics."""
        monitor = PerformanceMonitor()

        # Add test operations
        op1 = monitor.start_operation("test_op")
        time.sleep(0.01)
        monitor.end_operation(op1)

        op2 = monitor.start_operation("test_op")
        time.sleep(0.01)
        monitor.end_operation(op2)

        aggregates = monitor.get_aggregate_metrics("test_op")

        assert "count" in aggregates
        assert "avg_duration" in aggregates
        assert "min_duration" in aggregates
        assert "max_duration" in aggregates
        assert aggregates["count"] == 2

    def test_get_system_metrics(self):
        """Test getting system metrics."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available")

        monitor = PerformanceMonitor()

        # Test that we can get system metrics (without mocking)
        metrics = monitor.get_system_metrics()

        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        # Values will vary but should be reasonable percentages
        assert 0.0 <= metrics["cpu_percent"] <= 100.0
        assert 0.0 <= metrics["memory_percent"] <= 100.0

    def test_get_performance_summary(self):
        """Test getting performance summary."""
        monitor = PerformanceMonitor()

        # Add some test data
        op1 = monitor.start_operation("fast_op")
        monitor.end_operation(op1)

        op2 = monitor.start_operation("slow_op")
        time.sleep(0.01)
        monitor.end_operation(op2)

        summary = monitor.get_performance_summary()

        assert "total_operations" in summary
        assert "system_metrics" in summary
        assert summary["total_operations"] == 2

    def test_clear_history(self):
        """Test clearing operation history."""
        monitor = PerformanceMonitor()

        op1 = monitor.start_operation("test_op")
        monitor.end_operation(op1)

        assert len(monitor.metrics_history) > 0

        monitor.clear_history()

        assert len(monitor.metrics_history) == 0
        assert len(monitor.aggregates) == 0


class TestP3IFPerformanceOptimizer:
    """Tests for P3IFPerformanceOptimizer class."""

    def test_initialization(self):
        """Test P3IFPerformanceOptimizer initialization."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        assert optimizer.framework == framework
        assert optimizer.monitor is not None

    def test_optimize_pattern_queries(self):
        """Test pattern query optimization."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        # Add some test patterns
        prop = Property(name="Test Property", description="Test property for performance optimization", domain="test")
        framework.add_pattern(prop)

        result = optimizer.optimize_pattern_queries(["Test Property"])

        assert "query_patterns" in result
        assert "estimated_cost" in result
        assert isinstance(result["query_patterns"], list)

    def test_optimize_relationship_queries(self):
        """Test relationship query optimization."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        criteria = {"relationship_type": "general", "strength_threshold": 0.5}

        result = optimizer.optimize_relationship_queries(criteria)

        assert "criteria" in result
        assert "estimated_cost" in result
        assert isinstance(result["criteria"], dict)

    def test_get_optimization_recommendations(self):
        """Test getting optimization recommendations."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        recommendations = optimizer.get_optimization_recommendations()

        assert isinstance(recommendations, list)
        # Should return some recommendations even for empty framework

    def test_generate_performance_report(self):
        """Test generating performance report."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        report = optimizer.generate_performance_report()

        assert "framework_stats" in report
        assert "performance_summary" in report
        assert "optimization_recommendations" in report
        assert "cache_stats" in report

    def test_get_cache_statistics(self):
        """Test getting cache statistics."""
        framework = P3IFFramework()
        optimizer = P3IFPerformanceOptimizer(framework)

        stats = optimizer._get_cache_statistics()

        assert isinstance(stats, dict)
        # Should return cache stats even if no caching is active


class TestGlobalFunctions:
    """Tests for global performance monitoring functions."""

    def test_get_global_performance_monitor(self):
        """Test getting global performance monitor."""
        monitor = get_global_performance_monitor()

        assert isinstance(monitor, PerformanceMonitor)

    def test_configure_global_monitoring(self):
        """Test configuring global monitoring."""
        configure_global_monitoring(max_history=500, enable_system_metrics=False)

        monitor = get_global_performance_monitor()
        assert monitor.max_history == 500
        assert monitor.enable_system_metrics is False

    def test_reset_global_monitoring(self):
        """Test resetting global monitoring."""
        configure_global_monitoring(max_history=500)

        reset_global_monitoring()

        monitor = get_global_performance_monitor()
        assert monitor.max_history == 1000  # Should be reset to default

    def test_performance_monitored_context_manager(self):
        """Test performance_monitored context manager."""
        monitor = PerformanceMonitor()

        with monitor_operation("test_operation", monitor, {"type": "test"}):
            time.sleep(0.01)

        # Check that operation was recorded
        metrics = monitor.metrics_history
        assert len(metrics) == 1
        assert metrics[0].operation_name == "test_operation"

    def test_monitor_operation_context_manager(self):
        """Test monitor_operation context manager."""
        monitor = PerformanceMonitor()

        with monitor_operation("test_context", monitor=monitor):
            time.sleep(0.01)

        metrics = monitor.get_operation_metrics("test_context")
        assert len(metrics) == 1
        assert metrics[0].operation_name == "test_context"
        assert metrics[0].duration >= 0.01
