"""
P3IF Validation Methods

This module provides validation and constraint checking methods for P3IF frameworks.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import time
from collections import defaultdict
import logging


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationRule:
    """A validation rule with associated checks."""

    def __init__(self, name: str, check_function: Callable,
                 severity: ValidationSeverity = ValidationSeverity.ERROR,
                 description: str = "",
                 applies_to: Optional[str] = None):
        self.name = name
        self.check_function = check_function
        self.severity = severity
        self.description = description
        # applies_to: 'pattern', 'relationship', 'framework', or None for all
        self.applies_to = applies_to

    def validate(self, target: Any) -> List[Dict[str, Any]]:
        """Run validation check and return issues."""
        issues = []
        try:
            result = self.check_function(target)
            if not result["valid"]:
                issues.append({
                    "rule": self.name,
                    "severity": self.severity.value,
                    "description": self.description,
                    "details": result.get("details", {}),
                    "suggestions": result.get("suggestions", [])
                })
        except Exception as e:
            issues.append({
                "rule": self.name,
                "severity": "error",
                "description": f"Validation check failed: {str(e)}",
                "details": {},
                "suggestions": []
            })
        return issues


@dataclass
class ValidationEngine:
    """Engine for validating P3IF frameworks and components."""

    rules: Dict[str, ValidationRule] = field(default_factory=dict)
    validation_history: List[Dict[str, Any]] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"ValidationEngine(rules={len(self.rules)}, history={len(self.validation_history)})"

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules[rule.name] = rule

    def validate_framework(self, framework: Any) -> Dict[str, Any]:
        """Validate an entire P3IF framework."""
        validation_result = {
            "framework": getattr(framework, 'name', 'unknown'),
            "timestamp": datetime.now().isoformat(),
            "overall_valid": True,
            "issues": [],
            "summary": {
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0
            }
        }

        # Validate all patterns in the framework
        try:
            collection = getattr(framework, 'get_pattern_collection', lambda: None)()
            if collection:
                # Validate all properties, processes, perspectives with pattern rules
                all_patterns = collection.properties + collection.processes + collection.perspectives
                for pattern in all_patterns:
                    for rule_name, rule in self.rules.items():
                        if rule.applies_to in (None, 'pattern'):
                            issues = rule.validate(pattern)
                            validation_result["issues"].extend(issues)

                # Validate all relationships with relationship rules
                relationships = getattr(framework, 'get_all_relationships', lambda: [])()
                for rel in relationships:
                    for rule_name, rule in self.rules.items():
                        if rule.applies_to in (None, 'relationship'):
                            issues = rule.validate(rel)
                            validation_result["issues"].extend(issues)

            # Run framework-level rules
            for rule_name, rule in self.rules.items():
                if rule.applies_to in (None, 'framework'):
                    issues = rule.validate(framework)
                    validation_result["issues"].extend(issues)

        except Exception as e:
            validation_result["issues"].append({
                "rule": "framework_validation",
                "severity": "error",
                "description": f"Framework validation failed: {str(e)}",
                "details": {},
                "suggestions": []
            })
            validation_result["overall_valid"] = False
            validation_result["summary"]["error_count"] += 1

        # Count final summary
        for issue in validation_result["issues"]:
            severity = issue["severity"]
            if severity == "error":
                validation_result["summary"]["error_count"] += 1
                validation_result["overall_valid"] = False
            elif severity == "warning":
                validation_result["summary"]["warning_count"] += 1
            elif severity == "info":
                validation_result["summary"]["info_count"] += 1

        self.validation_history.append(validation_result)
        return validation_result

    def validate_dimension(self, dimension_name: str, elements: List[Any]) -> Dict[str, Any]:
        """Validate a specific dimension."""
        validation_result = {
            "dimension": dimension_name,
            "element_count": len(elements),
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
        }

        for element in elements:
            element_issues = self._validate_element(element)
            validation_result["issues"].extend(element_issues)

        # Count issues by severity
        for issue in validation_result["issues"]:
            severity = issue["severity"]
            if severity == "error":
                validation_result["summary"]["error_count"] += 1
            elif severity == "warning":
                validation_result["summary"]["warning_count"] += 1
            elif severity == "info":
                validation_result["summary"]["info_count"] += 1

        return validation_result

    def _validate_element(self, element: Any) -> List[Dict[str, Any]]:
        """Validate a single element using registered rules."""
        issues = []

        for rule_name, rule in self.rules.items():
            if rule.applies_to in (None, 'pattern'):
                issues.extend(rule.validate(element))

        # If no rules are registered, fall back to basic checks
        if not self.rules:
            if not hasattr(element, 'name') or not element.name:
                issues.append({
                    "element": getattr(element, 'name', 'unknown'),
                    "severity": "error",
                    "description": "Element missing name attribute",
                    "suggestions": ["Add a descriptive name to the element"]
                })

            if hasattr(element, 'description') and (not element.description or len(element.description) < 10):
                issues.append({
                    "element": getattr(element, 'name', 'unknown'),
                    "severity": "warning",
                    "description": "Element has very short or empty description",
                    "suggestions": ["Add a more detailed description (at least 10 characters)"]
                })

        return issues

    def get_validation_report(self, framework: Any) -> str:
        """Generate a human-readable validation report."""
        result = self.validate_framework(framework)

        report = f"""
P3IF Validation Report
======================
Framework: {result['framework']}
Timestamp: {result['timestamp']}
Overall Valid: {'✅ YES' if result['overall_valid'] else '❌ NO'}

Summary:
- Errors: {result['summary']['error_count']}
- Warnings: {result['summary']['warning_count']}
- Info: {result['summary']['info_count']}

Issues Found:
"""

        for issue in result['issues']:
            report += f"""
{issue['severity'].upper()}: {issue['description']}
  Element: {issue.get('element', 'N/A')}
  Suggestions: {', '.join(issue.get('suggestions', []))}
"""

        return report


@dataclass
class ConstraintManager:
    """Manages constraints and rules for P3IF elements."""

    constraints: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def add_constraint(self, element_type: str, constraint: Dict[str, Any]):
        """Add a constraint for an element type."""
        if element_type not in self.constraints:
            self.constraints[element_type] = []
        self.constraints[element_type].append(constraint)

    def check_constraints(self, element: Any) -> List[Dict[str, Any]]:
        """Check all constraints for an element."""
        violations = []
        element_type = type(element).__name__.lower()

        if element_type in self.constraints:
            for constraint in self.constraints[element_type]:
                if not self._check_single_constraint(element, constraint):
                    violations.append({
                        "constraint": constraint.get("name", "unnamed"),
                        "description": constraint.get("description", ""),
                        "element": getattr(element, 'name', str(element)),
                        "severity": constraint.get("severity", "error")
                    })

        return violations

    def _check_single_constraint(self, element: Any, constraint: Dict[str, Any]) -> bool:
        """Check a single constraint against an element."""
        constraint_type = constraint.get("type")

        if constraint_type == "required_attribute":
            attr_name = constraint.get("attribute")
            return hasattr(element, attr_name) and getattr(element, attr_name) is not None

        elif constraint_type == "attribute_format":
            attr_name = constraint.get("attribute")
            pattern = constraint.get("pattern")
            if hasattr(element, attr_name):
                value = getattr(element, attr_name)
                if value and isinstance(value, str):
                    return bool(re.match(pattern, value))
            return False

        elif constraint_type == "attribute_length":
            attr_name = constraint.get("attribute")
            min_len = constraint.get("min_length", 0)
            max_len = constraint.get("max_length", float('inf'))
            if hasattr(element, attr_name):
                value = getattr(element, attr_name)
                if value and isinstance(value, str):
                    return min_len <= len(value) <= max_len
            return False

        elif constraint_type == "dependency":
            dep_attr = constraint.get("depends_on")
            if hasattr(element, dep_attr):
                dep_value = getattr(element, dep_attr)
                expected_value = constraint.get("value")
                return dep_value == expected_value
            return False

        return True  # Default to valid if constraint type unknown


# Pre-defined validation rules
def create_default_validation_rules() -> Dict[str, ValidationRule]:
    """Create a set of default validation rules for P3IF."""

    rules = {}

    # Rule: Element must have a name
    def check_name(element):
        try:
            # Try to access the name field from Pydantic model
            if hasattr(element, 'name') and element.name:
                return {"valid": True}
            # Try to access as a dictionary (for JSON data)
            elif isinstance(element, dict) and 'name' in element and element['name']:
                return {"valid": True}
            else:
                return {"valid": False, "details": {"missing": "name"}}
        except (AttributeError, KeyError, TypeError) as e:
            return {"valid": False, "details": {"error": "cannot_access_name", "exception": str(e)}}

    rules["has_name"] = ValidationRule(
        "has_name",
        check_name,
        ValidationSeverity.ERROR,
        "Element must have a non-empty name",
        applies_to='pattern'
    )

    # Rule: Description should be meaningful
    def check_description(element):
        if hasattr(element, 'description'):
            desc = element.description or ""
            if len(desc) < 10:
                return {"valid": False, "details": {"length": len(desc)}}
        return {"valid": True}

    rules["meaningful_description"] = ValidationRule(
        "meaningful_description",
        check_description,
        ValidationSeverity.WARNING,
        "Element should have a meaningful description (at least 10 characters)",
        applies_to='pattern'
    )

    # Rule: Framework should have minimum elements
    def check_minimum_elements(framework):
        try:
            collection = getattr(framework, 'get_pattern_collection', lambda: None)()
            if collection is None:
                return {"valid": False, "details": {"error": "cannot_access_pattern_collection"}}

            total_elements = len(collection.properties) + len(collection.processes) + len(collection.perspectives)

            if total_elements < 3:
                return {"valid": False, "details": {"total": total_elements}}
            return {"valid": True}
        except (AttributeError, TypeError) as e:
            return {"valid": False, "details": {"error": "cannot_access_dimensions", "exception": str(e)}}

    rules["minimum_elements"] = ValidationRule(
        "minimum_elements",
        check_minimum_elements,
        ValidationSeverity.WARNING,
        "Framework should have at least 3 elements total",
        applies_to='framework'
    )

    # Rule: Relationship must connect at least two dimensions
    def check_relationship_validity(relationship):
        try:
            # Try to access as Pydantic model
            if hasattr(relationship, 'property_id'):
                property_id = relationship.property_id
                process_id = relationship.process_id
                perspective_id = relationship.perspective_id
            # Try to access as dictionary (for JSON data)
            elif isinstance(relationship, dict):
                property_id = relationship.get('property_id')
                process_id = relationship.get('process_id')
                perspective_id = relationship.get('perspective_id')
            else:
                return {"valid": False, "details": {"missing_attributes": True}}

            if property_id is None and process_id is None and perspective_id is None:
                return {"valid": False, "details": {"missing_attributes": True}}

            # Count connected dimensions
            connected_dims = sum(1 for dim_id in [property_id, process_id, perspective_id] if dim_id)
            if connected_dims < 2:
                return {"valid": False, "details": {"connected_dimensions": connected_dims}}

            return {"valid": True}
        except (AttributeError, TypeError) as e:
            return {"valid": False, "details": {"error": "cannot_access_relationship_data", "exception": str(e)}}

    rules["relationship_validity"] = ValidationRule(
        "relationship_validity",
        check_relationship_validity,
        ValidationSeverity.ERROR,
        "Relationship must connect at least two dimensions",
        applies_to='relationship'
    )

    # Rule: Relationship strength should be in valid range
    def check_strength_range(relationship):
        if hasattr(relationship, 'strength'):
            strength = getattr(relationship, 'strength', 0.5)
            if not (0.0 <= strength <= 1.0):
                return {"valid": False, "details": {"strength": strength}}
        return {"valid": True}

    rules["strength_range"] = ValidationRule(
        "strength_range",
        check_strength_range,
        ValidationSeverity.ERROR,
        "Relationship strength must be between 0.0 and 1.0",
        applies_to='relationship'
    )

    # Rule: Relationship confidence should be in valid range
    def check_confidence_range(relationship):
        if hasattr(relationship, 'confidence'):
            confidence = getattr(relationship, 'confidence', 1.0)
            if not (0.0 <= confidence <= 1.0):
                return {"valid": False, "details": {"confidence": confidence}}
        return {"valid": True}

    rules["confidence_range"] = ValidationRule(
        "confidence_range",
        check_confidence_range,
        ValidationSeverity.WARNING,
        "Relationship confidence should be between 0.0 and 1.0",
        applies_to='relationship'
    )

    # Rule: Framework should have balanced dimensions
    def check_dimension_balance(framework):
        prop_count = len(getattr(framework, 'properties', []))
        proc_count = len(getattr(framework, 'processes', []))
        pers_count = len(getattr(framework, 'perspectives', []))

        # Check for severely unbalanced dimensions
        total = prop_count + proc_count + pers_count
        if total == 0:
            return {"valid": False, "details": {"reason": "no_elements"}}

        # Check each dimension ratio
        ratios = []
        if prop_count > 0:
            ratios.append(prop_count / total)
        if proc_count > 0:
            ratios.append(proc_count / total)
        if pers_count > 0:
            ratios.append(pers_count / total)

        max_ratio = max(ratios) if ratios else 0
        min_ratio = min(ratios) if ratios else 0

        # Flag if any dimension dominates (>70% of total)
        if max_ratio > 0.7:
            return {"valid": False, "details": {"max_ratio": max_ratio, "min_ratio": min_ratio}}

        return {"valid": True}

    rules["dimension_balance"] = ValidationRule(
        "dimension_balance",
        check_dimension_balance,
        ValidationSeverity.INFO,
        "Framework dimensions should be reasonably balanced",
        applies_to='framework'
    )

    return rules


# Pre-defined constraints
def create_default_constraints() -> Dict[str, List[Dict[str, Any]]]:
    """Create default constraints for P3IF elements."""

    constraints = {}

    # Property constraints
    constraints["property"] = [
        {
            "name": "has_description",
            "type": "required_attribute",
            "attribute": "description",
            "severity": "warning"
        },
        {
            "name": "name_format",
            "type": "attribute_format",
            "attribute": "name",
            "pattern": r"^[A-Za-z][A-Za-z0-9_\s]*$",
            "severity": "error"
        }
    ]

    # Process constraints
    constraints["process"] = [
        {
            "name": "has_inputs_or_outputs",
            "type": "dependency",
            "depends_on": "inputs",
            "value": [],  # Should not be empty list
            "severity": "info"
        }
    ]

    # Perspective constraints
    constraints["perspective"] = [
        {
            "name": "has_viewpoint",
            "type": "required_attribute",
            "attribute": "viewpoint",
            "severity": "warning"
        }
    ]

    return constraints
