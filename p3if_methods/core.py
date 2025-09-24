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
        """Create a new pattern with specified attributes."""
        operation = P3IFOperation(
            operation_type=OperationType.CREATE,
            description=f"Create {pattern_type}: {name}",
            parameters={"type": pattern_type, "name": name, "domain": domain,
                       "description": description, "attributes": attributes}
        )

        try:
            # Create pattern based on type
            if pattern_type.lower() == "property":
                pattern = Property(name=name, domain=domain or "default",
                                 description=description or "", **attributes)
            elif pattern_type.lower() == "process":
                pattern = Process(name=name, domain=domain or "default",
                                description=description or "", **attributes)
            elif pattern_type.lower() == "perspective":
                # Remove viewpoint from attributes to avoid duplicate parameter
                perspective_attributes = attributes.copy()
                viewpoint = perspective_attributes.pop("viewpoint", "default")
                pattern = Perspective(name=name, domain=domain or "default",
                                    description=description or "",
                                    viewpoint=viewpoint,
                                    **perspective_attributes)
            else:
                raise ValueError(f"Unknown pattern type: {pattern_type}")

            # Add to framework
            self.framework.add_pattern(pattern)

            operation.status = "completed"
            operation.result = pattern

            self.operations.append(operation)
            self.logger.info(f"Created pattern: {pattern.name}")

            return pattern

        except Exception as e:
            operation.status = "failed"
            operation.result = str(e)
            self.logger.error(f"Failed to create pattern: {e}")
            raise

    def find_patterns(self, criteria: Dict[str, Any]) -> List[BasePattern]:
        """Find patterns matching specified criteria."""
        matching_patterns = []

        for pattern_id, pattern in self.framework._patterns.items():
            match = True
            for key, value in criteria.items():
                if not hasattr(pattern, key) or getattr(pattern, key) != value:
                    match = False
                    break

            if match:
                matching_patterns.append(pattern)

        return matching_patterns

    def create_relationship(self, source_pattern: Union[str, BasePattern],
                          target_pattern: Union[str, BasePattern],
                          strength: float = 1.0, confidence: float = 1.0,
                          relationship_type: str = "general") -> Relationship:
        """Create relationship between two patterns."""
        # Resolve pattern IDs if needed
        source_id = source_pattern.id if hasattr(source_pattern, 'id') else str(source_pattern)
        target_id = target_pattern.id if hasattr(target_pattern, 'id') else str(target_pattern)

        # Find the actual patterns
        source = self.framework._patterns.get(source_id)
        target = self.framework._patterns.get(target_id)

        if not source or not target:
            raise ValueError(f"Could not find patterns: {source_id}, {target_id}")

        # Determine IDs based on pattern types first
        property_id = None
        process_id = None
        perspective_id = None

        if hasattr(source, 'type') and hasattr(target, 'type'):
            if source.type == "property" and target.type == "process":
                property_id = source.id
                process_id = target.id
            elif source.type == "process" and target.type == "perspective":
                process_id = source.id
                perspective_id = target.id
            elif source.type == "property" and target.type == "perspective":
                property_id = source.id
                perspective_id = target.id

        # Create relationship with the determined IDs
        relationship = Relationship(
            strength=strength,
            confidence=confidence,
            property_id=property_id,
            process_id=process_id,
            perspective_id=perspective_id,
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
