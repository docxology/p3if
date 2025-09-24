"""
P3IF Validation Methods

This module provides validation and constraint checking methods for P3IF frameworks.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
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
                 description: str = ""):
        self.name = name
        self.check_function = check_function
        self.severity = severity
        self.description = description

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

        # Run all applicable rules
        for rule_name, rule in self.rules.items():
            issues = rule.validate(framework)
            validation_result["issues"].extend(issues)

            for issue in issues:
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
        """Validate a single element."""
        issues = []

        # Basic validation rules
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
        if not hasattr(element, 'name') or not element.name:
            return {"valid": False, "details": {"missing": "name"}}
        return {"valid": True}

    rules["has_name"] = ValidationRule(
        "has_name",
        check_name,
        ValidationSeverity.ERROR,
        "Element must have a non-empty name"
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
        "Element should have a meaningful description (at least 10 characters)"
    )

    # Rule: Framework should have minimum elements
    def check_minimum_elements(framework):
        total_elements = 0
        for dimension in ['properties', 'processes', 'perspectives']:
            elements = getattr(framework, dimension, [])
            total_elements += len(elements)

        if total_elements < 3:
            return {"valid": False, "details": {"total": total_elements}}
        return {"valid": True}

    rules["minimum_elements"] = ValidationRule(
        "minimum_elements",
        check_minimum_elements,
        ValidationSeverity.WARNING,
        "Framework should have at least 3 elements total"
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
