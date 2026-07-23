"""
P3IF Domain Data Models

Pydantic models for validating domain JSON files loaded from data/domains/.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class DomainData(BaseModel):
    """Schema for a P3IF domain JSON file.

    Validates the structure of domain files like data/domains/healthcare.json:
    {
        "domain": "HealthCare",
        "version": "1.0",
        "properties": ["Patient Safety", ...],
        "processes": ["Patient Intake", ...],
        "perspectives": ["Patient", ...]
    }
    """

    domain: str = Field(..., min_length=1, max_length=200, description="Domain name")
    version: str = Field(default="1.0", description="Domain data version")
    properties: List[str] = Field(default_factory=list, description="Property names")
    processes: List[str] = Field(default_factory=list, description="Process names")
    perspectives: List[str] = Field(default_factory=list, description="Perspective names")

    model_config = {
        "extra": "ignore",
    }

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Domain name cannot be empty")
        return v.strip()

    @field_validator('properties', 'processes', 'perspectives')
    @classmethod
    def validate_lists(cls, v: List[str]) -> List[str]:
        """Ensure all entries are non-empty strings."""
        cleaned = []
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError(f"Invalid entry: {item!r} — must be non-empty string")
            cleaned.append(item.strip())
        return cleaned

    def total_elements(self) -> int:
        """Return total number of properties + processes + perspectives."""
        return len(self.properties) + len(self.processes) + len(self.perspectives)
