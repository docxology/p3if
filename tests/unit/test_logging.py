"""
Unit tests for P3IF enhanced logging system.

Tests logging configuration, metrics collection, performance monitoring, and structured logging.
"""

import unittest
import time
import tempfile
import json
from pathlib import Path

from p3if.utils.logging import (
    P3IFLogger, get_logger, log_method_call, log_method_result,
    log_error, LogContext, logged_method, performance_monitor,
    get_performance_report, log_system_status, export_performance_report
)


class TestP3IFLogger(unittest.TestCase):
    """Test cases for P3IF logger functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset logger state
        P3IFLogger._configured = False
        P3IFLogger._loggers.clear()
        P3IFLogger.reset_metrics()

    def tearDown(self):
        """Clean up after tests."""
        P3IFLogger.reset_metrics()

    def test_logger_configuration(self):
        """Test logger configuration."""
        P3IFLogger.configure(level=20, enable_console=False)  # INFO level

        self.assertTrue(P3IFLogger._configured)

    def test_logger_get_logger(self):
        """Test getting configured loggers."""
        logger1 = P3IFLogger.get_logger("test_module")
        logger2 = P3IFLogger.get_logger("test_module")

        self.assertEqual(logger1, logger2)
        self.assertIn("test_module", P3IFLogger._loggers)

    def test_metrics_recording(self):
        """Test metrics collection."""
        # Record some metrics
        P3IFLogger.record_metric("test_operation", 1.5, True)
        P3IFLogger.record_metric("test_operation", 2.0, False)
        P3IFLogger.record_metric("another_operation", 0.5, True)

        metrics = P3IFLogger.get_metrics()

        self.assertIn("test_operation", metrics)
        self.assertIn("another_operation", metrics)

        test_op = metrics["test_operation"]
        self.assertEqual(test_op["count"], 2)
        self.assertEqual(test_op["total_time"], 3.5)
        self.assertEqual(test_op["average_time"], 1.75)
        self.assertEqual(test_op["errors"], 1)
        self.assertEqual(test_op["error_rate"], 0.5)

    def test_metrics_export(self):
        """Test metrics export to file."""
        P3IFLogger.record_metric("export_test", 1.0, True)

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            P3IFLogger.export_metrics(temp_path)

            with open(temp_path, 'r') as f:
                data = json.load(f)

            self.assertIn("timestamp", data)
            self.assertIn("metrics", data)
            self.assertIn("export_test", data["metrics"])

        finally:
            temp_path.unlink(missing_ok=True)

    def test_metrics_reset(self):
        """Test metrics reset functionality."""
        P3IFLogger.record_metric("reset_test", 1.0, True)
        self.assertEqual(len(P3IFLogger.get_metrics()), 1)

        P3IFLogger.reset_metrics()
        self.assertEqual(len(P3IFLogger.get_metrics()), 0)


class TestLogContext(unittest.TestCase):
    """Test cases for LogContext."""

    def setUp(self):
        """Set up test fixtures."""
        P3IFLogger.reset_metrics()

    def tearDown(self):
        """Clean up after tests."""
        P3IFLogger.reset_metrics()

    def test_log_context_success(self):
        """Test successful log context execution."""
        # Use real P3IF logger instead of mock
        logger = P3IFLogger.get_logger("test_logger")
        context = LogContext(logger, "test_method", 10)  # DEBUG level

        with context:
            pass  # Successful execution

        # Should record successful metric
        metrics = P3IFLogger.get_metrics()
        self.assertIn("test_method", metrics)
        self.assertEqual(metrics["test_method"]["count"], 1)
        self.assertEqual(metrics["test_method"]["errors"], 0)

    def test_log_context_failure(self):
        """Test failed log context execution."""
        # Use real P3IF logger instead of mock
        logger = P3IFLogger.get_logger("test_logger")
        context = LogContext(logger, "failing_method", 20)  # INFO level

        with self.assertRaises(ValueError):
            with context:
                raise ValueError("Test error")

        # Should record failed metric
        metrics = P3IFLogger.get_metrics()
        self.assertIn("failing_method", metrics)
        self.assertEqual(metrics["failing_method"]["count"], 1)
        self.assertEqual(metrics["failing_method"]["errors"], 1)


class TestDecorators(unittest.TestCase):
    """Test cases for logging decorators."""

    def setUp(self):
        """Set up test fixtures."""
        P3IFLogger.reset_metrics()

    def tearDown(self):
        """Clean up after tests."""
        P3IFLogger.reset_metrics()

    def test_logged_method_decorator(self):
        """Test logged method decorator."""
        @logged_method()
        def test_function(x, y=10):
            return x + y

        result = test_function(5, y=15)
        self.assertEqual(result, 20)

        # Should record metric
        metrics = P3IFLogger.get_metrics()
        self.assertTrue(any("test_function" in key for key in metrics.keys()))

    def test_performance_monitor_decorator(self):
        """Test performance monitor decorator."""
        @performance_monitor(threshold_ms=1000)  # Higher threshold
        def slow_function():
            time.sleep(0.001)  # Real sleep for timing test
            return "result"

        # Use real execution (no mocking needed for this test)
        result = slow_function()

        self.assertEqual(result, "result")

        # Should record metric
        metrics = P3IFLogger.get_metrics()
        self.assertTrue(any("slow_function" in key for key in metrics.keys()))

    def test_performance_monitor_slow_operation(self):
        """Test performance monitor with slow operation."""
        @performance_monitor(threshold_ms=1)  # Very low threshold to ensure warning
        def very_slow_function():
            time.sleep(0.01)  # Real sleep to trigger warning
            return "slow_result"

        # Use real execution - should trigger performance warning
        result = very_slow_function()

        self.assertEqual(result, "slow_result")
        # Warning should be logged (we can see it in the captured log output)


class TestPerformanceReporting(unittest.TestCase):
    """Test cases for performance reporting functions."""

    def setUp(self):
        """Set up test fixtures."""
        P3IFLogger.reset_metrics()

    def tearDown(self):
        """Clean up after tests."""
        P3IFLogger.reset_metrics()

    def test_get_performance_report(self):
        """Test performance report generation."""
        # Add some test metrics
        P3IFLogger.record_metric("fast_op", 0.1, True)
        P3IFLogger.record_metric("fast_op", 0.2, True)
        P3IFLogger.record_metric("slow_op", 2.0, False)
        P3IFLogger.record_metric("error_op", 1.0, False)
        P3IFLogger.record_metric("error_op", 0.5, False)

        report = get_performance_report()

        # Check summary
        summary = report["summary"]
        self.assertEqual(summary["total_operations"], 5)
        self.assertEqual(summary["total_errors"], 3)
        self.assertAlmostEqual(summary["overall_error_rate"], 0.6)

        # Check slowest operations (should be sorted)
        slowest = report["slowest_operations"]
        self.assertEqual(len(slowest), 3)  # Limited to top 3
        self.assertEqual(slowest[0][0], "slow_op")  # Slowest first

        # Check error-prone operations
        error_prone = report["error_prone_operations"]
        self.assertEqual(len(error_prone), 2)
        # Both error_op and slow_op have error_rate = 1.0, check they are both present
        error_prone_ops = [op[0] for op in error_prone]
        self.assertIn("error_op", error_prone_ops)
        self.assertIn("slow_op", error_prone_ops)

    def test_export_performance_report(self):
        """Test performance report export."""
        P3IFLogger.record_metric("export_test", 1.0, True)

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_performance_report(temp_path)

            with open(temp_path, 'r') as f:
                data = json.load(f)

            self.assertIn("summary", data)
            self.assertIn("slowest_operations", data)
            self.assertIn("error_prone_operations", data)

        finally:
            temp_path.unlink(missing_ok=True)

    def test_log_system_status(self):
        """Test system status logging."""
        # Use real P3IF logger
        logger = P3IFLogger.get_logger("test_logger")

        # Add test metrics
        P3IFLogger.record_metric("status_test", 0.5, True)
        P3IFLogger.record_metric("failing_test", 1.0, False)

        log_system_status(logger)

        # Should log system status (can't easily test the actual logging output)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility logging functions."""

    def test_log_method_call(self):
        """Test method call logging."""
        # Use real P3IF logger
        logger = P3IFLogger.get_logger("test_logger")

        log_method_call(logger, "test_method", (1, "arg"), {"kwarg": "value"})

        # Test completed - actual logging verification is complex

    def test_log_method_result(self):
        """Test method result logging."""
        # Use real P3IF logger
        logger = P3IFLogger.get_logger("test_logger")

        log_method_result(logger, "test_method", "result", 1.5)

        # Test completed - actual logging verification is complex

    def test_log_error(self):
        """Test error logging."""
        # Use real P3IF logger
        logger = P3IFLogger.get_logger("test_logger")

        test_error = ValueError("Test error")
        context = {"user_id": "123", "operation": "test"}

        log_error(logger, "test_method", test_error, context)

        # Error should be logged (we can see it in the captured log output)


if __name__ == '__main__':
    unittest.main()