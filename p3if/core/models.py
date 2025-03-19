"""
P3IF Core Models

This module defines the core data models for the P3IF framework.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class Pattern(BaseModel):
    """Base class for all P3IF patterns."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    type: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_assignment = True


class Property(Pattern):
    """A property or characteristic in the P3IF framework."""
    type: str = "property"
    domain: Optional[str] = None


class Process(Pattern):
    """A process or action in the P3IF framework."""
    type: str = "process"
    domain: Optional[str] = None


class Perspective(Pattern):
    """A perspective or viewpoint in the P3IF framework."""
    type: str = "perspective"
    domain: Optional[str] = None


class Relationship(BaseModel):
    """Represents a relationship between patterns in the P3IF framework."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: Optional[str] = None
    process_id: Optional[str] = None 
    perspective_id: Optional[str] = None
    strength: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bidirectional: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        validate_assignment = True 