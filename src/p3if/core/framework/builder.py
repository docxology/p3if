"""
P3IF Framework Builder

A fluent builder API for constructing P3IF frameworks with method chaining.
Extracted from the framework module to keep ``framework/core.py`` focused on
the core framework class.
"""
from typing import Optional, Any

from p3if.core.framework.core import P3IFFramework
from p3if.core.models import (
    Property,
    Process,
    Perspective,
    Relationship,
    BasePattern,
    RelationshipStrength,
    ConfidenceScore,
)


class FrameworkBuilder:
    """Fluent builder API for constructing P3IF frameworks with method chaining.

    Usage:
        fw = (FrameworkBuilder()
              .add_property(name="Security", description="...", domain="cybersec")
              .add_process(name="Authentication", description="...", domain="cybersec")
              .add_perspective(name="Technical", description="...", domain="cybersec", viewpoint="dev")
              .build())
    """

    def __init__(self, framework: Optional[P3IFFramework] = None):
        self._framework = framework or P3IFFramework()

    def add_property(
        self, name: str, description: str, domain: str, **kwargs: Any
    ) -> "FrameworkBuilder":
        """Add a Property pattern and return self for chaining."""
        self._framework.add_pattern(
            Property(name=name, description=description, domain=domain, **kwargs)
        )
        return self

    def add_process(
        self, name: str, description: str, domain: str, **kwargs: Any
    ) -> "FrameworkBuilder":
        """Add a Process pattern and return self for chaining."""
        self._framework.add_pattern(
            Process(name=name, description=description, domain=domain, **kwargs)
        )
        return self

    def add_perspective(
        self, name: str, description: str, domain: str, viewpoint: str = "default", **kwargs: Any
    ) -> "FrameworkBuilder":
        """Add a Perspective pattern and return self for chaining."""
        self._framework.add_pattern(
            Perspective(
                name=name, description=description, domain=domain, viewpoint=viewpoint, **kwargs
            )
        )
        return self

    def add_relationship(
        self,
        property_id: Optional[str] = None,
        process_id: Optional[str] = None,
        perspective_id: Optional[str] = None,
        strength: float = 0.5,
        confidence: float = 1.0,
        relationship_type: str = "general",
    ) -> "FrameworkBuilder":
        """Add a Relationship and return self for chaining."""
        self._framework.add_relationship(
            Relationship(
                property_id=property_id,
                process_id=process_id,
                perspective_id=perspective_id,
                strength=RelationshipStrength(strength),  # type: ignore[arg-type]
                confidence=ConfidenceScore(confidence),  # type: ignore[arg-type]
                relationship_type=relationship_type,
            )
        )
        return self

    def add_pattern(self, pattern: BasePattern) -> "FrameworkBuilder":
        """Add any pattern and return self for chaining."""
        self._framework.add_pattern(pattern)
        return self

    def build(self) -> P3IFFramework:
        """Return the constructed framework."""
        return self._framework

    def __repr__(self) -> str:
        return f"FrameworkBuilder(framework={self._framework!r})"
