"""
P3IF Core Models - Enhanced Version

This module defines the core data models for the P3IF framework with improved
validation, metadata support, and performance optimizations.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union, Set, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator, field_validator, model_validator
from dataclasses import dataclass
import json


class PatternType(str, Enum):
    """Enumeration of valid pattern types."""
    PROPERTY = "property"
    PROCESS = "process"
    PERSPECTIVE = "perspective"


class RelationshipStrength(float):
    """Custom type for relationship strength with validation."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (int, float)):
            raise TypeError('strength must be a number')
        if not (0.0 <= v <= 1.0):
            raise ValueError('strength must be between 0.0 and 1.0')
        return cls(v)


class ConfidenceScore(float):
    """Custom type for confidence scores with validation."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (int, float)):
            raise TypeError('confidence must be a number')
        if not (0.0 <= v <= 1.0):
            raise ValueError('confidence must be between 0.0 and 1.0')
        return cls(v)


class MetadataMixin:
    """Mixin class providing metadata functionality."""
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
    description: Optional[str] = Field(None, max_length=2000)
    type: PatternType
    domain: Optional[str] = Field(None, max_length=100)

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

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            PatternType: lambda v: v.value
        }

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags are valid."""
        if not all(isinstance(tag, str) and tag.strip() for tag in v):
            raise ValueError('All tags must be non-empty strings')
        return [tag.strip().lower() for tag in v]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Ensure name is properly formatted."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

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
        return self.dict(by_alias=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.json(by_alias=True, indent=2)


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
    def validate_priority(cls, v):
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

    @field_validator('complexity', 'automation_level')
    @classmethod
    def validate_complexity_level(cls, v):
        """Validate complexity and automation level values."""
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            raise ValueError(f'Value must be one of: {valid_levels}')
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

    @field_validator('scope', 'expertise_level')
    @classmethod
    def validate_scope_level(cls, v):
        """Validate scope and expertise level values."""
        valid_scopes = ['general', 'specific', 'detailed']
        valid_levels = ['novice', 'intermediate', 'expert']
        if v not in valid_scopes + valid_levels:
            valid_values = valid_scopes + valid_levels
            raise ValueError(f'Value must be one of: {valid_values}')
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

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            RelationshipStrength: lambda v: float(v),
            ConfidenceScore: lambda v: float(v)
        }

    @model_validator(mode='before')
    @classmethod
    def validate_connections(cls, values):
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
    def validate_relationship_type(cls, v):
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
        return self.dict(by_alias=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.json(by_alias=True, indent=2)


# Utility classes for enhanced functionality
@dataclass
class PatternCollection:
    """Collection of patterns with utility methods."""
    properties: List[Property]
    processes: List[Process]
    perspectives: List[Perspective]

    def all_patterns(self) -> List[BasePattern]:
        """Get all patterns as a single list."""
        return self.properties + self.processes + self.perspectives

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