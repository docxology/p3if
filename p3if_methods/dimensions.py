"""
P3IF Dimension-Specific Methods

This module provides specialized methods for working with individual P3IF dimensions:
Properties, Processes, and Perspectives.
"""

from typing import Dict, List, Any, Optional, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict
import logging


class PropertyType(str, Enum):
    """Types of properties."""
    SECURITY = "security"
    QUALITY = "quality"
    BUSINESS = "business"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"


class ProcessType(str, Enum):
    """Types of processes."""
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    GOVERNANCE = "governance"
    SUPPORT = "support"
    INTEGRATION = "integration"


class PerspectiveType(str, Enum):
    """Types of perspectives."""
    STAKEHOLDER = "stakeholder"
    DOMAIN = "domain"
    TEMPORAL = "temporal"
    ANALYTICAL = "analytical"
    RISK = "risk"


@dataclass
class PropertyManager:
    """Manages properties and their relationships."""

    properties: Dict[str, Any] = field(default_factory=dict)
    property_types: Dict[str, PropertyType] = field(default_factory=dict)

    def add_property(self, name: str, prop_type: PropertyType = PropertyType.TECHNICAL,
                    description: str = "", attributes: Dict[str, Any] = None) -> Any:
        """Add a new property."""
        property_obj = {
            "name": name,
            "type": prop_type,
            "description": description,
            "attributes": attributes or {},
            "created_at": datetime.now().isoformat()
        }
        self.properties[name] = property_obj
        self.property_types[name] = prop_type
        return property_obj

    def categorize_properties(self) -> Dict[PropertyType, List[str]]:
        """Categorize properties by type."""
        categories = defaultdict(list)
        for name, prop_type in self.property_types.items():
            categories[prop_type].append(name)
        return dict(categories)

    def find_similar_properties(self, name: str, threshold: float = 0.7) -> List[str]:
        """Find properties with similar names."""
        similar = []
        name_lower = name.lower()

        for prop_name in self.properties.keys():
            # Simple similarity check based on common words
            prop_lower = prop_name.lower()
            words1 = set(name_lower.split())
            words2 = set(prop_lower.split())
            common = words1.intersection(words2)

            if common and len(common) / max(len(words1), len(words2)) >= threshold:
                similar.append(prop_name)

        return similar

    def validate_property_dependencies(self, property_name: str,
                                     required_props: List[str]) -> Dict[str, bool]:
        """Validate that required properties exist."""
        validation = {}
        for req_prop in required_props:
            validation[req_prop] = req_prop in self.properties
        return validation


@dataclass
class ProcessManager:
    """Manages processes and their sequences."""

    processes: Dict[str, Any] = field(default_factory=dict)
    process_types: Dict[str, ProcessType] = field(default_factory=dict)
    process_sequences: Dict[str, List[str]] = field(default_factory=dict)

    def add_process(self, name: str, proc_type: ProcessType = ProcessType.OPERATIONAL,
                   description: str = "", inputs: List[str] = None,
                   outputs: List[str] = None) -> Any:
        """Add a new process."""
        process_obj = {
            "name": name,
            "type": proc_type,
            "description": description,
            "inputs": inputs or [],
            "outputs": outputs or [],
            "created_at": datetime.now().isoformat()
        }
        self.processes[name] = process_obj
        self.process_types[name] = proc_type
        return process_obj

    def define_process_sequence(self, sequence_name: str, process_list: List[str]):
        """Define a sequence of processes."""
        self.process_sequences[sequence_name] = process_list

    def get_process_dependencies(self, process_name: str) -> Dict[str, List[str]]:
        """Get dependencies for a process."""
        if process_name not in self.processes:
            return {}

        process = self.processes[process_name]
        return {
            "inputs": process["inputs"],
            "outputs": process["outputs"]
        }

    def validate_process_chain(self, process_list: List[str]) -> Dict[str, Any]:
        """Validate that a process chain is complete and consistent."""
        validation = {
            "valid": True,
            "missing_processes": [],
            "broken_links": [],
            "warnings": []
        }

        # Check that all processes exist
        for process_name in process_list:
            if process_name not in self.processes:
                validation["missing_processes"].append(process_name)
                validation["valid"] = False

        # Check for broken input/output links
        for i, process_name in enumerate(process_list[:-1]):
            next_process = process_list[i + 1]
            current_outputs = self.processes[process_name]["outputs"]
            next_inputs = self.processes[next_process]["inputs"]

            # Check if any output from current matches input to next
            if not any(output in next_inputs for output in current_outputs):
                validation["broken_links"].append({
                    "from": process_name,
                    "to": next_process,
                    "missing_links": [output for output in current_outputs if output not in next_inputs]
                })

        return validation


@dataclass
class PerspectiveManager:
    """Manages perspectives and their viewpoints."""

    perspectives: Dict[str, Any] = field(default_factory=dict)
    perspective_types: Dict[str, PerspectiveType] = field(default_factory=dict)
    viewpoint_hierarchies: Dict[str, List[str]] = field(default_factory=dict)

    def add_perspective(self, name: str, pers_type: PerspectiveType = PerspectiveType.STAKEHOLDER,
                       description: str = "", viewpoint: str = "default") -> Any:
        """Add a new perspective."""
        perspective_obj = {
            "name": name,
            "type": pers_type,
            "description": description,
            "viewpoint": viewpoint,
            "created_at": datetime.now().isoformat()
        }
        self.perspectives[name] = perspective_obj
        self.perspective_types[name] = pers_type
        return perspective_obj

    def define_viewpoint_hierarchy(self, hierarchy_name: str, viewpoints: List[str]):
        """Define a hierarchy of viewpoints."""
        self.viewpoint_hierarchies[hierarchy_name] = viewpoints

    def get_perspectives_by_type(self, pers_type: PerspectiveType) -> List[str]:
        """Get all perspectives of a specific type."""
        return [name for name, ptype in self.perspective_types.items() if ptype == pers_type]

    def analyze_perspective_coverage(self, elements: List[Any]) -> Dict[str, Any]:
        """Analyze how well perspectives cover different elements."""
        coverage = {
            "total_elements": len(elements),
            "covered_elements": 0,
            "perspective_effectiveness": {},
            "coverage_gaps": []
        }

        for perspective_name, perspective in self.perspectives.items():
            covered = 0
            for element in elements:
                # Simple heuristic: check if perspective name appears in element attributes
                if self._perspective_covers_element(perspective, element):
                    covered += 1

            coverage["perspective_effectiveness"][perspective_name] = {
                "coverage": covered,
                "coverage_ratio": covered / len(elements) if elements else 0
            }

            if covered > 0:
                coverage["covered_elements"] += 1

        # Find gaps
        for element in elements:
            covering_perspectives = [
                name for name, perspective in self.perspectives.items()
                if self._perspective_covers_element(perspective, element)
            ]
            if not covering_perspectives:
                coverage["coverage_gaps"].append({
                    "element": getattr(element, 'name', str(element)),
                    "suggested_perspective": self._suggest_perspective_for_element(element)
                })

        return coverage

    def _perspective_covers_element(self, perspective: Dict, element: Any) -> bool:
        """Check if a perspective covers a specific element."""
        perspective_keywords = set(perspective["name"].lower().split())
        element_keywords = set()

        # Extract keywords from element attributes
        for attr_name, attr_value in element.__dict__.items():
            if attr_value and isinstance(attr_value, str):
                element_keywords.update(attr_value.lower().split())

        # Check for keyword overlap
        common_keywords = perspective_keywords.intersection(element_keywords)
        return len(common_keywords) > 0

    def _suggest_perspective_for_element(self, element: Any) -> str:
        """Suggest an appropriate perspective for an element."""
        # Simple heuristic based on element type and attributes
        element_type = type(element).__name__.lower()

        if "security" in element_type or hasattr(element, "security"):
            return "Security Perspective"
        elif "business" in element_type or hasattr(element, "business"):
            return "Business Perspective"
        elif "technical" in element_type or hasattr(element, "technical"):
            return "Technical Perspective"
        else:
            return "General Perspective"
