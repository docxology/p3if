"""
P3IF Composition Methods

This module provides methods for composing and multiplexing P3IF frameworks,
enabling flexible combination of different framework elements and dimensions.
"""

from typing import Dict, List, Any, Optional, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from abc import ABC, abstractmethod


class CompositionType(str, Enum):
    """Types of composition operations."""
    OVERLAY = "overlay"
    MERGE = "merge"
    EXTEND = "extend"
    TRANSFORM = "transform"
    FILTER = "filter"
    PROJECT = "project"


class MultiplexingStrategy(str, Enum):
    """Strategies for multiplexing framework elements."""
    UNION = "union"
    INTERSECTION = "intersection"
    COMPLEMENT = "complement"
    CUSTOM = "custom"


@dataclass
class FrameworkAdapter:
    """Adapter for integrating external frameworks with P3IF."""
    name: str
    version: str
    source_framework: str
    mapping_rules: Dict[str, Any]
    transformation_functions: Dict[str, Callable]

    def map_element(self, element: Any, element_type: str) -> Dict[str, Any]:
        """Map an element from the source framework to P3IF format."""
        if element_type in self.mapping_rules:
            mapping = self.mapping_rules[element_type]
            return {p3if_key: getattr(element, source_key, None)
                   for p3if_key, source_key in mapping.items()}
        return {}


class CompositionEngine:
    """Engine for composing and manipulating P3IF frameworks."""

    def __init__(self):
        self.adapters: Dict[str, FrameworkAdapter] = {}
        self.composition_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def register_adapter(self, adapter: FrameworkAdapter):
        """Register a framework adapter."""
        self.adapters[adapter.name] = adapter
        self.logger.info(f"Registered adapter for {adapter.source_framework}")

    def overlay_frameworks(self, base_framework: Any, overlay_framework: Any,
                          strategy: MultiplexingStrategy = MultiplexingStrategy.UNION) -> Any:
        """Overlay one framework on top of another."""
        # Implementation would depend on framework structure
        # This is a conceptual implementation
        result = base_framework.copy()

        for dimension in ['properties', 'processes', 'perspectives']:
            base_elements = getattr(base_framework, dimension, set())
            overlay_elements = getattr(overlay_framework, dimension, set())

            if strategy == MultiplexingStrategy.UNION:
                combined = base_elements | overlay_elements
            elif strategy == MultiplexingStrategy.INTERSECTION:
                combined = base_elements & overlay_elements
            elif strategy == MultiplexingStrategy.COMPLEMENT:
                combined = base_elements - overlay_elements
            else:
                combined = base_elements | overlay_elements  # Default to union

            setattr(result, dimension, combined)

        self._record_composition("overlay", base_framework, overlay_framework, result)
        return result

    def transform_dimension(self, framework: Any, dimension: str,
                          transformation: Callable) -> Any:
        """Transform a specific dimension of a framework."""
        result = framework.copy()
        original_elements = getattr(framework, dimension, [])

        transformed_elements = []
        for element in original_elements:
            transformed = transformation(element)
            if transformed:
                transformed_elements.append(transformed)

        setattr(result, dimension, transformed_elements)
        self._record_composition("transform", framework, None, result)
        return result

    def filter_by_criteria(self, framework: Any,
                          criteria: Dict[str, Any]) -> Any:
        """Filter framework elements by specified criteria."""
        result = framework.copy()

        for dimension in ['properties', 'processes', 'perspectives']:
            elements = getattr(framework, dimension, [])
            filtered_elements = []

            for element in elements:
                if self._matches_criteria(element, criteria):
                    filtered_elements.append(element)

            setattr(result, dimension, filtered_elements)

        self._record_composition("filter", framework, None, result)
        return result

    def project_dimensions(self, framework: Any,
                          dimensions: List[str]) -> Any:
        """Project framework to specified dimensions only."""
        result = framework.copy()

        for dimension in ['properties', 'processes', 'perspectives']:
            if dimension not in dimensions:
                setattr(result, dimension, [])
            else:
                setattr(result, dimension, getattr(framework, dimension, []))

        self._record_composition("project", framework, None, result)
        return result

    def create_composite_framework(self, frameworks: List[Any],
                                 composition_rules: Dict[str, Any]) -> Any:
        """Create a composite framework from multiple frameworks."""
        if not frameworks:
            return None

        base = frameworks[0]
        for framework in frameworks[1:]:
            base = self.overlay_frameworks(base, framework,
                                         composition_rules.get('strategy', MultiplexingStrategy.UNION))

        self._record_composition("composite", frameworks, None, base)
        return base

    def _matches_criteria(self, element: Any, criteria: Dict[str, Any]) -> bool:
        """Check if an element matches specified criteria."""
        for key, value in criteria.items():
            if hasattr(element, key):
                element_value = getattr(element, key)
                if isinstance(value, (list, tuple, set)):
                    if element_value not in value:
                        return False
                else:
                    if element_value != value:
                        return False
        return True

    def _record_composition(self, operation: str, input_data: Any,
                          overlay_data: Any = None, result: Any = None):
        """Record a composition operation for history tracking."""
        operation_record = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "input_type": type(input_data).__name__,
            "input_count": len(input_data) if isinstance(input_data, (list, dict)) else 1,
            "overlay_type": type(overlay_data).__name__ if overlay_data else None,
            "result_type": type(result).__name__ if result else None
        }

        self.composition_history.append(operation_record)
        self.logger.info(f"Recorded composition operation: {operation}")


class Multiplexer:
    """Handles multiplexing of framework elements across dimensions."""

    def __init__(self):
        self.multiplexing_rules: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def add_multiplexing_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add a multiplexing rule."""
        self.multiplexing_rules[rule_name] = rule_config

    def multiplex_properties_to_processes(self, properties: List[Any],
                                        mapping_rules: Dict[str, str]) -> Dict[str, List[Any]]:
        """Multiplex properties into process representations."""
        process_map = {}

        for prop in properties:
            for process_type, prop_attribute in mapping_rules.items():
                if hasattr(prop, prop_attribute):
                    if process_type not in process_map:
                        process_map[process_type] = []
                    process_map[process_type].append(prop)

        return process_map

    def multiplex_processes_to_perspectives(self, processes: List[Any],
                                         mapping_rules: Dict[str, str]) -> Dict[str, List[Any]]:
        """Multiplex processes into perspective representations."""
        perspective_map = {}

        for process in processes:
            for perspective_type, process_attribute in mapping_rules.items():
                if hasattr(process, process_attribute):
                    if perspective_type not in perspective_map:
                        perspective_map[perspective_type] = []
                    perspective_map[perspective_type].append(process)

        return perspective_map

    def create_cross_dimensional_links(self, framework: Any) -> List[Dict[str, Any]]:
        """Create links across dimensions based on common attributes."""
        links = []

        # Get all elements by dimension
        properties = getattr(framework, 'properties', [])
        processes = getattr(framework, 'processes', [])
        perspectives = getattr(framework, 'perspectives', [])

        # Find potential links based on naming patterns or attributes
        for prop in properties:
            for process in processes:
                if self._potentially_related(prop, process):
                    links.append({
                        "source": {"type": "property", "element": prop},
                        "target": {"type": "process", "element": process},
                        "relationship_type": "potential",
                        "confidence": 0.5
                    })

            for perspective in perspectives:
                if self._potentially_related(prop, perspective):
                    links.append({
                        "source": {"type": "property", "element": prop},
                        "target": {"type": "perspective", "element": perspective},
                        "relationship_type": "potential",
                        "confidence": 0.5
                    })

        return links

    def _potentially_related(self, elem1: Any, elem2: Any) -> bool:
        """Determine if two elements are potentially related."""
        # Simple heuristic: check for common words in names
        name1 = getattr(elem1, 'name', '').lower()
        name2 = getattr(elem2, 'name', '').lower()

        words1 = set(name1.split())
        words2 = set(name2.split())

        # If they share common significant words, they might be related
        common_words = words1.intersection(words2)
        significant_words = {w for w in common_words if len(w) > 3}

        return len(significant_words) > 0


class AdapterFactory:
    """Factory for creating framework adapters."""

    @staticmethod
    def create_cia_triad_adapter() -> FrameworkAdapter:
        """Create adapter for CIA Triad framework."""
        return FrameworkAdapter(
            name="cia_triad_adapter",
            version="1.0",
            source_framework="CIA Triad",
            mapping_rules={
                "properties": {
                    "confidentiality": "confidentiality",
                    "integrity": "integrity",
                    "availability": "availability"
                }
            },
            transformation_functions={
                "property_to_process": lambda x: f"ensure_{x.name.lower()}"
            }
        )

    @staticmethod
    def create_nist_csf_adapter() -> FrameworkAdapter:
        """Create adapter for NIST Cybersecurity Framework."""
        return FrameworkAdapter(
            name="nist_csf_adapter",
            version="1.0",
            source_framework="NIST CSF",
            mapping_rules={
                "processes": {
                    "identify": "identify",
                    "protect": "protect",
                    "detect": "detect",
                    "respond": "respond",
                    "recover": "recover"
                }
            },
            transformation_functions={
                "function_to_perspective": lambda x: f"{x.name}_perspective"
            }
        )
