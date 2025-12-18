"""
P3IF Core Exceptions

Custom exceptions for the P3IF core framework to provide more specific error handling
and better error messages throughout the system.
"""

from typing import Any, Optional, Dict


class P3IFError(Exception):
    """Base exception for all P3IF-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class PatternError(P3IFError):
    """Base class for pattern-related errors."""
    pass


class PatternNotFoundError(PatternError):
    """Raised when a pattern cannot be found."""

    def __init__(self, pattern_id: str, pattern_type: Optional[str] = None):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type
        message = f"Pattern not found: {pattern_id}"
        details = {"pattern_id": pattern_id}
        if pattern_type:
            details["pattern_type"] = pattern_type
        super().__init__(message, details)


class PatternValidationError(PatternError):
    """Raised when pattern validation fails."""

    def __init__(self, pattern_id: str, validation_errors: list[str]):
        message = f"Pattern validation failed: {', '.join(validation_errors)}"
        details = {
            "pattern_id": pattern_id,
            "validation_errors": validation_errors
        }
        super().__init__(message, details)


class PatternTypeError(PatternError):
    """Raised when pattern type is invalid."""

    def __init__(self, expected_type: str, actual_type: str):
        self.expected_type = expected_type
        self.actual_type = actual_type
        message = f"Expected pattern type '{expected_type}', got '{actual_type}'"
        details = {
            "expected_type": expected_type,
            "actual_type": actual_type
        }
        super().__init__(message, details)


class RelationshipError(P3IFError):
    """Base class for relationship-related errors."""
    pass


class RelationshipValidationError(RelationshipError):
    """Raised when relationship validation fails."""

    def __init__(self, validation_errors: list[str], pattern_ids: Optional[list[str]] = None):
        message = f"Relationship validation failed: {', '.join(validation_errors)}"
        details = {"validation_errors": validation_errors}
        if pattern_ids:
            details["pattern_ids"] = pattern_ids
        super().__init__(message, details)


class RelationshipNotFoundError(RelationshipError):
    """Raised when a relationship cannot be found."""

    def __init__(self, relationship_id: str):
        message = f"Relationship not found: {relationship_id}"
        details = {"relationship_id": relationship_id}
        super().__init__(message, details)


class FrameworkError(P3IFError):
    """Base class for framework-related errors."""
    pass


class FrameworkValidationError(FrameworkError):
    """Raised when framework validation fails."""

    def __init__(self, validation_errors: list[str]):
        self.validation_errors = validation_errors
        message = f"Framework validation failed: {', '.join(validation_errors)}"
        details = {"validation_errors": validation_errors}
        super().__init__(message, details)


class OperationError(P3IFError):
    """Base class for operation-related errors."""

    def __init__(self, operation_type: str, operation_id: str, message: str):
        self.operation_type = operation_type
        self.operation_id = operation_id
        self.error_message = message
        full_message = f"Operation {operation_type} ({operation_id}) failed: {message}"
        details = {
            "operation_type": operation_type,
            "operation_id": operation_id,
            "error_message": message
        }
        super().__init__(full_message, details)


class OperationFailedError(OperationError):
    """Raised when an operation fails to complete."""

    def __init__(self, operation_type: str, operation_id: str, error_message: str):
        self.operation_type = operation_type
        self.operation_id = operation_id
        self.error_message = error_message
        message = f"Operation failed: {operation_type} ({operation_id}) - {error_message}"
        details = {
            "operation_type": operation_type,
            "operation_id": operation_id,
            "error_message": error_message
        }
        super().__init__(message, details)

