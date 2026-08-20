"""
Common decorators and helpers for P3IF API routes.
"""
from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable
from flask import jsonify, request

logger = logging.getLogger(__name__)

API_VERSION = "v2"
API_BASE_URL = f"/{API_VERSION}"
API_AVAILABLE = True


def handle_api_errors(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle API errors consistently."""
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"API validation error: {e}")
            return jsonify({
                "status": "error",
                "error": "Validation Error",
                "message": str(e),
                "status_code": 400
            }), 400
        except FileNotFoundError as e:
            logger.error(f"API file not found: {e}")
            return jsonify({
                "status": "error",
                "error": "Resource Not Found",
                "message": "The requested resource was not found",
                "status_code": 404
            }), 404
        except Exception as e:
            logger.error(f"API internal error: {e}")
            return jsonify({
                "status": "error",
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "status_code": 500
            }), 500
    return wrapper


def validate_json(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to validate JSON request data."""
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            if not request.is_json:
                return jsonify({
                    "status": "error",
                    "error": "Invalid Content Type",
                    "message": "Request must have Content-Type: application/json",
                    "status_code": 400
                }), 400
            return f(*args, **kwargs)
        except Exception:
            return jsonify({
                "status": "error",
                "error": "Invalid JSON",
                "message": "Request contains invalid JSON",
                "status_code": 400
            }), 400
    return wrapper
