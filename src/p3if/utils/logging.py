"""
P3IF Unified Logging System

Provides consistent logging configuration and utilities across all P3IF modules.
All logging follows a standardized format with proper log levels and structured messages.
"""

import logging
import sys
import time
import json
import functools
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class P3IFLogger:
    """Unified logging system for P3IF framework with metrics collection."""

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # Default log format
    DEFAULT_FORMAT = (
        '%(asctime)s | %(levelname)-8s | %(name)-30s | '
        '%(filename)s:%(lineno)d | %(message)s'
    )

    # Structured log format for JSON output
    JSON_FORMAT = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "file": "%(filename)s", '
        '"line": %(lineno)d, "message": "%(message)s"}'
    )

    _configured = False
    _loggers = {}
    _metrics = defaultdict(lambda: {"count": 0, "total_time": 0.0, "errors": 0})

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        log_file: Optional[Path] = None,
        json_format: bool = False,
        enable_console: bool = True
    ) -> None:
        """Configure the global logging system."""
        if cls._configured:
            return

        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Set format
        if json_format:
            formatter = logging.Formatter(cls.JSON_FORMAT)
        else:
            formatter = logging.Formatter(format_string or cls.DEFAULT_FORMAT)

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a configured logger for a module."""
        if not cls._configured:
            cls.configure()

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def set_level(cls, level: int) -> None:
        """Set logging level for all loggers."""
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        for logger in cls._loggers.values():
            logger.setLevel(level)

    @classmethod
    def record_metric(cls, operation: str, duration: float, success: bool = True) -> None:
        """Record performance metric for an operation."""
        cls._metrics[operation]["count"] += 1
        cls._metrics[operation]["total_time"] += duration
        if not success:
            cls._metrics[operation]["errors"] += 1

    @classmethod
    def get_metrics(cls) -> Dict[str, Dict[str, Any]]:
        """Get collected performance metrics."""
        metrics = {}
        for operation, data in cls._metrics.items():
            metrics[operation] = {
                "count": data["count"],
                "total_time": data["total_time"],
                "average_time": data["total_time"] / data["count"] if data["count"] > 0 else 0,
                "error_rate": data["errors"] / data["count"] if data["count"] > 0 else 0,
                "errors": data["errors"]
            }
        return metrics

    @classmethod
    def export_metrics(cls, path: Path) -> None:
        """Export metrics to JSON file."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "metrics": cls.get_metrics()
        }
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2)

    @classmethod
    def reset_metrics(cls) -> None:
        """Reset all collected metrics."""
        cls._metrics.clear()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a P3IF logger."""
    return P3IFLogger.get_logger(name)


def log_method_call(logger: logging.Logger, method_name: str, args: tuple = (), kwargs: dict = None) -> None:
    """Log method entry with parameters."""
    if kwargs is None:
        kwargs = {}

    # Sanitize sensitive information
    safe_args = []
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            safe_args.append(str(arg)[:100])  # Truncate long strings
        else:
            safe_args.append(f"<{type(arg).__name__}>")

    safe_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, (str, int, float, bool)):
            safe_kwargs[key] = str(value)[:100]
        else:
            safe_kwargs[key] = f"<{type(value).__name__}>"

    logger.debug(
        f"Calling {method_name}({', '.join(safe_args)}, "
        f"{', '.join(f'{k}={v}' for k, v in safe_kwargs.items())})"
    )


def log_method_result(logger: logging.Logger, method_name: str, result, duration: float = None) -> None:
    """Log method completion with result."""
    result_str = str(result)[:200] if result is not None else "None"
    duration_str = f" in {duration:.3f}s" if duration else ""

    logger.debug(f"Completed {method_name} -> {result_str}{duration_str}")

    # Log performance metrics for slow operations
    if duration:
        if duration > 5.0:
            logger.error(f"Very slow operation: {method_name} took {duration:.3f}s")
        elif duration > 1.0:
            logger.warning(f"Slow operation: {method_name} took {duration:.3f}s")


def log_error(logger: logging.Logger, method_name: str, error: Exception, context: dict = None) -> None:
    """Log method errors with context."""
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"Error in {method_name}: {error}{context_str}", exc_info=True)


def log_operation(logger: logging.Logger, operation: str, status: str, details: dict = None, duration: float = None) -> None:
    """Log operations with structured data for better observability."""
    details = details or {}
    duration_str = f" | Duration: {duration:.3f}s" if duration else ""

    if status == "success":
        logger.info(f"Operation {operation} completed successfully{details_str(details)}{duration_str}")
    elif status == "failed":
        logger.error(f"Operation {operation} failed{details_str(details)}{duration_str}")
    elif status == "started":
        logger.info(f"Operation {operation} started{details_str(details)}")
    else:
        logger.info(f"Operation {operation} status: {status}{details_str(details)}{duration_str}")


def details_str(details: dict) -> str:
    """Format details dictionary for logging."""
    if not details:
        return ""
    return f" | Details: {', '.join(f'{k}={v}' for k, v in details.items())}"


class LogContext:
    """Context manager for logging method execution with metrics collection."""

    def __init__(self, logger: logging.Logger, method_name: str, log_level: int = logging.DEBUG):
        self.logger = logger
        self.method_name = method_name
        self.log_level = log_level
        self.start_time = None
        self.success = True

    def __enter__(self):
        self.start_time = time.time()
        if self.logger.isEnabledFor(self.log_level):
            self.logger.log(self.log_level, f"Entering {self.method_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type:
            self.success = False
            self.logger.error(
                f"Exception in {self.method_name} after {duration:.3f}s: {exc_val}",
                exc_info=True
            )
        elif self.logger.isEnabledFor(self.log_level):
            self.logger.log(self.log_level, f"Completed {self.method_name} in {duration:.3f}s")

        # Record metrics
        P3IFLogger.record_metric(self.method_name, duration, self.success)


def logged_method(level: int = logging.DEBUG):
    """Decorator to add comprehensive logging and metrics to methods."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            method_name = f"{func.__qualname__}"

            with LogContext(logger, method_name, level):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    log_error(logger, method_name, e, {"args_count": len(args), "kwargs_keys": list(kwargs.keys())})
                    raise

        return wrapper
    return decorator


def performance_monitor(threshold_ms: float = 1000.0):
    """Decorator to monitor method performance and log slow operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            method_name = f"{func.__qualname__}"
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # Convert to milliseconds

                # Log if operation is slow
                if duration > threshold_ms:
                    logger.warning(
                        f"Slow operation: {method_name} took {duration:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )

                # Record metrics
                P3IFLogger.record_metric(method_name, duration / 1000, True)  # Convert back to seconds

                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(
                    f"Failed operation: {method_name} took {duration:.2f}ms - {e}"
                )
                P3IFLogger.record_metric(method_name, duration / 1000, False)
                raise

        return wrapper
    return decorator


def setup_default_logging(log_file: Optional[Path] = None) -> None:
    """Setup default P3IF logging configuration."""
    P3IFLogger.configure(
        level=logging.INFO,
        log_file=log_file,
        enable_console=True
    )


def get_performance_report() -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    metrics = P3IFLogger.get_metrics()

    # Calculate summary statistics
    total_operations = sum(data["count"] for data in metrics.values())
    total_errors = sum(data["errors"] for data in metrics.values())
    total_time = sum(data["total_time"] for data in metrics.values())

    # Find slowest operations
    slowest_ops = sorted(
        [(op, data["average_time"]) for op, data in metrics.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # Find operations with highest error rates
    error_prone_ops = sorted(
        [(op, data["error_rate"]) for op, data in metrics.items() if data["error_rate"] > 0],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return {
        "summary": {
            "total_operations": total_operations,
            "total_errors": total_errors,
            "total_time": total_time,
            "average_time_per_operation": total_time / total_operations if total_operations > 0 else 0,
            "overall_error_rate": total_errors / total_operations if total_operations > 0 else 0
        },
        "slowest_operations": slowest_ops,
        "error_prone_operations": error_prone_ops,
        "detailed_metrics": metrics,
        "generated_at": datetime.now().isoformat()
    }


def log_system_status(logger: logging.Logger) -> None:
    """Log current system status and performance metrics."""
    try:
        report = get_performance_report()

        logger.info("=== P3IF System Performance Report ===")
        logger.info(f"Total Operations: {report['summary']['total_operations']}")
        logger.info(f"Total Errors: {report['summary']['total_errors']}")
        logger.info(f"Overall Error Rate: {report['summary']['overall_error_rate']:.2%}")
        logger.info(f"Average Time per Operation: {report['summary']['average_time_per_operation']:.4f}s")

        if report['slowest_operations']:
            logger.info("Slowest Operations:")
            for op, avg_time in report['slowest_operations'][:3]:
                logger.info(f"  {op}: {avg_time:.4f}s")

        if report['error_prone_operations']:
            logger.warning("Error-Prone Operations:")
            for op, error_rate in report['error_prone_operations'][:3]:
                if error_rate > 0:
                    logger.warning(f"  {op}: {error_rate:.2%} error rate")

    except Exception as e:
        logger.error(f"Failed to generate performance report: {e}")


def export_performance_report(path: Path) -> None:
    """Export detailed performance report to file."""
    try:
        report = get_performance_report()
        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to export performance report: {e}")


# Initialize default logging on import
setup_default_logging()

