"""
P3IF Core Models

This module defines the core data models for the P3IF framework with
validation, metadata support, and performance optimizations.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union, Set, Literal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from dataclasses import dataclass
import json
from p3if.utils.logging import get_logger, logged_method


class PatternType(str, Enum):
    """Enumeration of valid pattern types."""
    PROPERTY = "property"
    PROCESS = "process"
    PERSPECTIVE = "perspective"


class RelationshipStrength(float):
    """Custom type for relationship strength with validation."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from pydantic_core import core_schema

        def validate_strength(v: Any) -> float:
            if not isinstance(v, (int, float)):
                raise TypeError('strength must be a number')
            if not (0.0 <= v <= 1.0):
                raise ValueError('strength must be between 0.0 and 1.0')
            return float(v)

        return core_schema.no_info_plain_validator_function(
            validate_strength,
            serialization=core_schema.plain_serializer_function_ser_schema(
                float,
                return_schema=core_schema.str_schema(),
                when_used='always'
            )
        )


class ConfidenceScore(float):
    """Custom type for confidence scores with validation."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from pydantic_core import core_schema

        def validate_confidence(v: Any) -> float:
            if not isinstance(v, (int, float)):
                raise TypeError('confidence must be a number')
            if not (0.0 <= v <= 1.0):
                raise ValueError('confidence must be between 0.0 and 1.0')
            return float(v)

        return core_schema.no_info_plain_validator_function(
            validate_confidence,
            serialization=core_schema.plain_serializer_function_ser_schema(
                float,
                return_schema=core_schema.str_schema(),
                when_used='always'
            )
        )


class MetadataMixin:
    """Mixin class providing metadata functionality.

    Expects the host class to have a 'metadata' dict field and an 'updated_at' datetime field.
    When used with Pydantic BaseModel, these are declared on the concrete model.
    """

    metadata: Dict[str, Any]
    updated_at: datetime
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata field."""
        self.metadata[key] = value
        self.updated_at = datetime.now(timezone.utc)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with default."""
        return self.metadata.get(key, default)

    def has_metadata(self, key: str) -> bool:
        """Check if metadata key exists."""
        return key in self.metadata


class BasePattern(BaseModel, MetadataMixin):
    """Enhanced base class for all P3IF patterns with improved functionality."""

    # Core fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    type: PatternType
    domain: str = Field(..., min_length=1, max_length=100)

    # Metadata and tracking
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Versioning
    version: str = Field(default="1.0.0")
    parent_id: Optional[str] = None  # For pattern hierarchies

    # Validation and quality
    validation_status: str = Field(default="draft")  # draft, validated, deprecated
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # References
    references: List[str] = Field(default_factory=list)  # URLs, citations, etc.
    related_patterns: List[str] = Field(default_factory=list)  # IDs of related patterns

    model_config = {
        "validate_assignment": True,
    }

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Ensure tags are valid."""
        if not all(isinstance(tag, str) and tag.strip() for tag in v):
            raise ValueError('All tags must be non-empty strings')
        return [tag.strip().lower() for tag in v]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is properly formatted."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @logged_method()
    def add_tag(self, tag: str) -> None:
        """Add a tag to the pattern."""
        tag = tag.strip().lower()
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the pattern."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)

    def is_deprecated(self) -> bool:
        """Check if pattern is deprecated."""
        return self.validation_status == "deprecated"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields."""
        return self.model_dump(by_alias=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(by_alias=True, indent=2)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, domain={self.domain!r}, id={self.id})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasePattern):
            return False
        return self.name == other.name and self.domain == other.domain and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.name, self.domain, self.type))


class Property(BasePattern):
    """Enhanced property pattern with additional functionality."""
    type: PatternType = PatternType.PROPERTY

    # Property-specific attributes
    data_type: Optional[str] = None  # string, number, boolean, etc.
    unit: Optional[str] = None  # measurement unit
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    allowed_values: List[str] = Field(default_factory=list)

    # Categorization
    category: Optional[str] = None  # security, performance, usability, etc.
    priority: str = Field(default="medium")  # low, medium, high, critical

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority values."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v


class Process(BasePattern):
    """Enhanced process pattern with workflow capabilities."""
    type: PatternType = PatternType.PROCESS

    # Process-specific attributes
    steps: List[Dict[str, Any]] = Field(default_factory=list)  # Process steps
    inputs: List[str] = Field(default_factory=list)  # Input requirements
    outputs: List[str] = Field(default_factory=list)  # Output specifications

    # Process characteristics
    duration: Optional[str] = None  # estimated duration
    complexity: str = Field(default="medium")  # low, medium, high
    automation_level: str = Field(default="manual")  # manual, semi-automated, fully-automated

    # Dependencies
    prerequisites: List[str] = Field(default_factory=list)  # Required patterns
    dependencies: List[str] = Field(default_factory=list)  # Dependent patterns

    @field_validator('complexity')
    @classmethod
    def validate_complexity_level(cls, v: str) -> str:
        """Validate complexity level values."""
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            raise ValueError(f'Complexity must be one of: {valid_levels}')
        return v

    @field_validator('automation_level')
    @classmethod
    def validate_automation_level(cls, v: str) -> str:
        """Validate automation level values."""
        valid_levels = ['manual', 'semi-automated', 'fully-automated']
        if v not in valid_levels:
            raise ValueError(f'Automation level must be one of: {valid_levels}')
        return v


class Perspective(BasePattern):
    """Enhanced perspective pattern with viewpoint modeling."""
    type: PatternType = PatternType.PERSPECTIVE

    # Perspective-specific attributes
    viewpoint: str = Field(..., max_length=100)  # stakeholder viewpoint
    concerns: List[str] = Field(default_factory=list)  # Areas of concern
    constraints: List[str] = Field(default_factory=list)  # Limiting factors

    # Perspective characteristics
    scope: str = Field(default="general")  # general, specific, detailed
    bias_factor: float = Field(default=0.0, ge=0.0, le=1.0)  # Potential bias indicator

    # Stakeholder information
    stakeholder_type: Optional[str] = None  # internal, external, customer, etc.
    expertise_level: str = Field(default="intermediate")  # novice, intermediate, expert

    @field_validator('scope')
    @classmethod
    def validate_scope(cls, v: str) -> str:
        """Validate scope values."""
        valid_scopes = ['general', 'specific', 'detailed']
        if v not in valid_scopes:
            raise ValueError(f'Scope must be one of: {valid_scopes}')
        return v

    @field_validator('expertise_level')
    @classmethod
    def validate_expertise_level(cls, v: str) -> str:
        """Validate expertise level values."""
        valid_levels = ['novice', 'intermediate', 'expert']
        if v not in valid_levels:
            raise ValueError(f'Expertise level must be one of: {valid_levels}')
        return v


class Relationship(BaseModel, MetadataMixin):
    """Enhanced relationship model with comprehensive metadata support."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Core relationship connections
    property_id: Optional[str] = None
    process_id: Optional[str] = None
    perspective_id: Optional[str] = None

    # Relationship metrics
    strength: RelationshipStrength = RelationshipStrength(0.5)
    confidence: ConfidenceScore = ConfidenceScore(1.0)

    # Relationship characteristics
    bidirectional: bool = True
    relationship_type: str = Field(default="general")  # general, causal, dependency, etc.
    direction: Optional[str] = None  # forward, backward, bidirectional

    # Temporal aspects
    temporal_context: Optional[str] = None  # current, future, historical
    validity_period: Optional[Dict[str, datetime]] = None  # start_date, end_date

    # Evidence and validation
    evidence_sources: List[str] = Field(default_factory=list)  # URLs, documents, etc.
    validation_method: Optional[str] = None  # manual, automated, expert_review
    assumptions: List[str] = Field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Quality and status
    status: str = Field(default="active")  # active, deprecated, experimental
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)

    model_config = {
        "validate_assignment": True,
    }

    @model_validator(mode='before')
    @classmethod
    def validate_connections(cls, values: Any) -> Any:
        """Ensure at least two dimensions are connected."""
        if isinstance(values, dict):
            connections = [
                values.get('property_id'),
                values.get('process_id'),
                values.get('perspective_id')
            ]
        else:
            connections = [
                getattr(values, 'property_id', None),
                getattr(values, 'process_id', None),
                getattr(values, 'perspective_id', None)
            ]
        connected_dims = sum(1 for conn in connections if conn is not None)
        if connected_dims < 2:
            raise ValueError("A relationship must connect at least two dimensions")
        return values

    @field_validator('relationship_type')
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        """Validate relationship type."""
        valid_types = ['general', 'causal', 'dependency', 'composition', 'aggregation', 'specialization']
        if v not in valid_types:
            raise ValueError(f'Relationship type must be one of: {valid_types}')
        return v

    def get_connected_patterns(self) -> List[str]:
        """Get list of connected pattern IDs."""
        return [pid for pid in [self.property_id, self.process_id, self.perspective_id] if pid]

    def is_bidirectional(self) -> bool:
        """Check if relationship is bidirectional."""
        return self.bidirectional or self.direction == 'bidirectional'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields."""
        return self.model_dump(by_alias=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(by_alias=True, indent=2)

    def __repr__(self) -> str:
        connected = self.get_connected_patterns()
        return (f"Relationship(id={self.id}, type={self.relationship_type}, "
                f"strength={float(self.strength):.2f}, connected={connected})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relationship):
            return False
        return (self.property_id == other.property_id and
                self.process_id == other.process_id and
                self.perspective_id == other.perspective_id and
                self.relationship_type == other.relationship_type)

    def __hash__(self) -> int:
        return hash((self.property_id, self.process_id, self.perspective_id, self.relationship_type))


# Utility classes for enhanced functionality
@dataclass
class PatternCollection:
    """Collection of patterns with utility methods."""
    properties: List[Property]
    processes: List[Process]
    perspectives: List[Perspective]

    def all_patterns(self) -> List[BasePattern]:
        """Get all patterns as a single list."""
        result: List[BasePattern] = []
        result.extend(self.properties)
        result.extend(self.processes)
        result.extend(self.perspectives)
        return result

    def get_by_id(self, pattern_id: str) -> Optional[BasePattern]:
        """Find pattern by ID across all types."""
        for pattern in self.all_patterns():
            if pattern.id == pattern_id:
                return pattern
        return None

    def get_by_domain(self, domain: str) -> 'PatternCollection':
        """Filter collection by domain."""
        return PatternCollection(
            properties=[p for p in self.properties if p.domain == domain],
            processes=[p for p in self.processes if p.domain == domain],
            perspectives=[p for p in self.perspectives if p.domain == domain]
        )


@dataclass
class RelationshipAnalysis:
    """Analysis results for relationships."""
    total_relationships: int
    average_strength: float
    average_confidence: float
    relationship_types: Dict[str, int]
    domains_involved: Set[str]
    orphaned_patterns: List[str]  # Patterns with no relationships 