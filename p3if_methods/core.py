"""
P3IF Core Methods

This module provides the core functionality for P3IF framework operations,
including pattern management, relationship analysis, and basic framework operations.
"""

import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging

from .models import BasePattern, Property, Process, Perspective, Relationship
from .framework import P3IFFramework


class OperationType(str, Enum):
    """Types of P3IF operations."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    COMPOSE = "compose"
    ANALYZE = "analyze"
    VISUALIZE = "visualize"


@dataclass
class P3IFOperation:
    """Represents a P3IF operation with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: OperationType = OperationType.CREATE
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class P3IFCore:
    """Core P3IF functionality with modular operations."""

    def __init__(self):
        self.framework = P3IFFramework()
        self.operations: List[P3IFOperation] = []
        self.logger = logging.getLogger(__name__)

    def create_pattern(self, pattern_type: str, name: str, domain: str = None,
                      description: str = None, **attributes) -> BasePattern:
        """Create a new pattern with specified attributes and validation."""
        # Input validation
        if not name or not name.strip():
            raise ValueError("Pattern name cannot be empty")

        if not pattern_type:
            raise ValueError("Pattern type must be specified")

        valid_types = ["property", "process", "perspective"]
        if pattern_type.lower() not in valid_types:
            raise ValueError(f"Pattern type must be one of: {valid_types}")

        operation = P3IFOperation(
            operation_type=OperationType.CREATE,
            description=f"Create {pattern_type}: {name}",
            parameters={"type": pattern_type, "name": name, "domain": domain,
                       "description": description, "attributes": attributes}
        )

        try:
            # Validate domain if provided
            if domain and len(domain) > 100:
                raise ValueError("Domain name too long (max 100 characters)")

            # Validate description if provided
            if description and len(description) > 2000:
                raise ValueError("Description too long (max 2000 characters)")

            # Create pattern based on type with proper validation
            if pattern_type.lower() == "property":
                pattern = Property(
                    name=name.strip(),
                    domain=domain or "default",
                    description=description or "",
                    **attributes
                )
            elif pattern_type.lower() == "process":
                pattern = Process(
                    name=name.strip(),
                    domain=domain or "default",
                    description=description or "",
                    **attributes
                )
            elif pattern_type.lower() == "perspective":
                # Handle viewpoint parameter specially for perspectives
                perspective_attributes = attributes.copy()
                viewpoint = perspective_attributes.pop("viewpoint", "default")
                pattern = Perspective(
                    name=name.strip(),
                    domain=domain or "default",
                    description=description or "",
                    viewpoint=viewpoint,
                    **perspective_attributes
                )

            # Validate the created pattern
            self._validate_pattern(pattern)

            # Add to framework
            self.framework.add_pattern(pattern)

            operation.status = "completed"
            operation.result = pattern

            self.operations.append(operation)
            self.logger.info(f"Created pattern: {pattern.name} (ID: {pattern.id})")

            return pattern

        except Exception as e:
            operation.status = "failed"
            operation.result = str(e)
            self.logger.error(f"Failed to create pattern '{name}': {e}")
            raise

    def _validate_pattern(self, pattern: BasePattern) -> None:
        """Validate a pattern for consistency and required fields."""
        errors = []

        # Check required fields
        if not pattern.name or not pattern.name.strip():
            errors.append("Pattern name is required")

        if not pattern.type:
            errors.append("Pattern type is required")

        # Type-specific validation
        if pattern.type == "property":
            if hasattr(pattern, 'category') and pattern.category:
                valid_categories = ['security', 'quality', 'business', 'technical', 'compliance']
                if pattern.category not in valid_categories:
                    errors.append(f"Invalid property category: {pattern.category}")

        elif pattern.type == "process":
            if hasattr(pattern, 'complexity') and pattern.complexity:
                valid_complexities = ['low', 'medium', 'high']
                if pattern.complexity not in valid_complexities:
                    errors.append(f"Invalid process complexity: {pattern.complexity}")

        elif pattern.type == "perspective":
            if hasattr(pattern, 'viewpoint') and not pattern.viewpoint:
                errors.append("Perspective viewpoint is required")

        if errors:
            raise ValueError(f"Pattern validation failed: {'; '.join(errors)}")

    def create_pattern_bulk(self, patterns_data: List[Dict[str, Any]]) -> List[BasePattern]:
        """Create multiple patterns in bulk with validation."""
        created_patterns = []

        for pattern_data in patterns_data:
            try:
                pattern = self.create_pattern(**pattern_data)
                created_patterns.append(pattern)
            except Exception as e:
                self.logger.warning(f"Failed to create pattern: {e}")
                # Continue with other patterns

        return created_patterns

    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> BasePattern:
        """Update an existing pattern with validation."""
        operation = P3IFOperation(
            operation_type=OperationType.UPDATE,
            description=f"Update pattern: {pattern_id}",
            parameters={"pattern_id": pattern_id, "updates": updates}
        )

        try:
            # Get existing pattern
            pattern = self.framework.get_pattern(pattern_id)
            if not pattern:
                raise ValueError(f"Pattern not found: {pattern_id}")

            # Validate updates
            self._validate_pattern_updates(pattern, updates)

            # Apply updates
            for key, value in updates.items():
                if hasattr(pattern, key):
                    setattr(pattern, key, value)

            # Update timestamp
            pattern.updated_at = datetime.now()

            operation.status = "completed"
            operation.result = pattern

            self.operations.append(operation)
            self.logger.info(f"Updated pattern: {pattern.name}")

            return pattern

        except Exception as e:
            operation.status = "failed"
            operation.result = str(e)
            self.logger.error(f"Failed to update pattern: {e}")
            raise

    def _validate_pattern_updates(self, pattern: BasePattern, updates: Dict[str, Any]) -> None:
        """Validate pattern updates."""
        errors = []

        # Check name update
        if "name" in updates:
            new_name = updates["name"]
            if not new_name or not new_name.strip():
                errors.append("Updated name cannot be empty")
            elif len(new_name) > 200:
                errors.append("Updated name too long (max 200 characters)")

        # Check description update
        if "description" in updates:
            new_desc = updates["description"]
            if new_desc and len(new_desc) > 2000:
                errors.append("Updated description too long (max 2000 characters)")

        # Type-specific validation
        if "category" in updates and pattern.type == "property":
            valid_categories = ['security', 'quality', 'business', 'technical', 'compliance']
            if updates["category"] not in valid_categories:
                errors.append(f"Invalid property category: {updates['category']}")

        if errors:
            raise ValueError(f"Pattern update validation failed: {'; '.join(errors)}")

    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern and its relationships."""
        operation = P3IFOperation(
            operation_type=OperationType.DELETE,
            description=f"Delete pattern: {pattern_id}",
            parameters={"pattern_id": pattern_id}
        )

        try:
            # Check if pattern exists
            pattern = self.framework.get_pattern(pattern_id)
            if not pattern:
                raise ValueError(f"Pattern not found: {pattern_id}")

            # Remove relationships first
            relationships = self.framework.get_relationships_by_pattern(pattern_id)
            for rel in relationships:
                self.framework.remove_relationship(rel.id)

            # Remove pattern
            success = self.framework.remove_pattern(pattern_id)

            operation.status = "completed"
            operation.result = success

            self.operations.append(operation)
            self.logger.info(f"Deleted pattern: {pattern.name}")

            return success

        except Exception as e:
            operation.status = "failed"
            operation.result = str(e)
            self.logger.error(f"Failed to delete pattern: {e}")
            raise

    def find_patterns(self, criteria: Dict[str, Any]) -> List[BasePattern]:
        """Find patterns matching specified criteria."""
        matching_patterns = []

        for pattern_id, pattern in self.framework._patterns.items():
            match = True
            for key, value in criteria.items():
                if not hasattr(pattern, key):
                    match = False
                    break
                
                pattern_value = getattr(pattern, key)
                
                # Special handling for name field - substring matching
                if key == "name" and isinstance(value, str) and isinstance(pattern_value, str):
                    if value.lower() not in pattern_value.lower():
                        match = False
                        break
                else:
                    # Exact matching for other fields
                    if pattern_value != value:
                        match = False
                        break

            if match:
                matching_patterns.append(pattern)

        return matching_patterns

    def create_relationship(self, property_id: str = None, process_id: str = None, 
                          perspective_id: str = None, strength: float = 1.0, 
                          confidence: float = 1.0, relationship_type: str = "general") -> Relationship:
        """Create relationship between patterns using their IDs or pattern objects."""
        # Handle pattern objects passed as first two arguments (legacy support)
        if hasattr(property_id, 'id') and hasattr(process_id, 'id'):
            # Legacy call: create_relationship(pattern1, pattern2, ...)
            if property_id.type == "property" and process_id.type == "process":
                actual_property_id = property_id.id
                actual_process_id = process_id.id
                actual_perspective_id = perspective_id.id if hasattr(perspective_id, 'id') else perspective_id
            elif property_id.type == "process" and process_id.type == "perspective":
                actual_property_id = None
                actual_process_id = property_id.id
                actual_perspective_id = process_id.id
            elif property_id.type == "property" and process_id.type == "perspective":
                actual_property_id = property_id.id
                actual_process_id = None
                actual_perspective_id = process_id.id
            else:
                raise ValueError("Invalid pattern type combination")
        else:
            # New call: create_relationship(property_id, process_id, perspective_id, ...)
            actual_property_id = property_id
            actual_process_id = process_id
            actual_perspective_id = perspective_id

        # Validate that at least two dimensions are provided
        provided_dims = sum(1 for dim_id in [actual_property_id, actual_process_id, actual_perspective_id] if dim_id is not None)
        if provided_dims < 2:
            raise ValueError("At least two pattern IDs must be provided")

        # Validate pattern existence
        if actual_property_id and not self.framework.get_pattern(actual_property_id):
            raise ValueError(f"Property with ID {actual_property_id} not found")
        if actual_process_id and not self.framework.get_pattern(actual_process_id):
            raise ValueError(f"Process with ID {actual_process_id} not found")
        if actual_perspective_id and not self.framework.get_pattern(actual_perspective_id):
            raise ValueError(f"Perspective with ID {actual_perspective_id} not found")

        # Create relationship with the provided IDs
        relationship = Relationship(
            strength=strength,
            confidence=confidence,
            property_id=actual_property_id,
            process_id=actual_process_id,
            perspective_id=actual_perspective_id,
            metadata={"type": relationship_type}
        )

        self.framework.add_relationship(relationship)
        return relationship

    def analyze_patterns(self, domain: str = None) -> Dict[str, Any]:
        """Analyze patterns and relationships."""
        analysis = {
            "total_patterns": len(self.framework._patterns),
            "total_relationships": len(self.framework._relationships),
            "domains": {},
            "pattern_types": {},
            "relationships_by_type": {}
        }

        # Analyze by domain
        for pattern in self.framework._patterns.values():
            domain_name = pattern.domain or "default"
            if domain_name not in analysis["domains"]:
                analysis["domains"][domain_name] = {"count": 0, "types": {}}
            analysis["domains"][domain_name]["count"] += 1

            pattern_type = pattern.type.value
            if pattern_type not in analysis["domains"][domain_name]["types"]:
                analysis["domains"][domain_name]["types"][pattern_type] = 0
            analysis["domains"][domain_name]["types"][pattern_type] += 1

        # Analyze pattern types
        for pattern in self.framework._patterns.values():
            pattern_type = pattern.type.value
            analysis["pattern_types"][pattern_type] = analysis["pattern_types"].get(pattern_type, 0) + 1

        return analysis

    def get_operation_history(self) -> List[P3IFOperation]:
        """Get history of operations performed."""
        return self.operations.copy()

    def export_framework(self, format: str = "json", path: Optional[str] = None) -> str:
        """Export framework in specified format."""
        if format.lower() == "json":
            export_data = {
                "patterns": {pid: pattern.dict() for pid, pattern in self.framework._patterns.items()},
                "relationships": {rid: rel.dict() for rid, rel in self.framework._relationships.items()},
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }

            if path:
                from utils.json import dump
                with open(path, 'w') as f:
                    dump(export_data, f, indent=2)
                return path
            else:
                from utils.json import dumps
                return dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
