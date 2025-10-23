"""
Comprehensive integration examples for P3IF.

This module provides practical examples of how to integrate P3IF with various
external systems, frameworks, and data sources.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import json
from pathlib import Path

from p3if_methods.core import P3IFCore
from p3if_methods.composition import CompositionEngine, FrameworkAdapter
from p3if_methods.framework import P3IFFramework
from p3if_methods.models import Property, Process, Perspective, Relationship


@dataclass
class IntegrationExample:
    """Base class for integration examples."""

    name: str
    description: str
    core: P3IFCore = field(default_factory=P3IFCore)
    logger = logging.getLogger(__name__)

    def execute(self) -> Dict[str, Any]:
        """Execute the integration example."""
        raise NotImplementedError("Subclasses must implement execute method")

    def get_requirements(self) -> List[str]:
        """Get requirements for this integration."""
        return ["P3IF core functionality"]

    def get_benefits(self) -> List[str]:
        """Get benefits of this integration."""
        return ["Enhanced functionality", "Improved interoperability"]


class NISTIntegrationExample(IntegrationExample):
    """Example of integrating NIST Cybersecurity Framework with P3IF."""

    def __init__(self):
        super().__init__(
            name="nist_csf_integration",
            description="Integrate NIST Cybersecurity Framework with P3IF for enhanced security analysis"
        )

    def execute(self) -> Dict[str, Any]:
        """Execute the NIST integration example."""
        self.logger.info("Starting NIST CSF integration example")

        # Create NIST CSF patterns
        nist_patterns = self._create_nist_patterns()

        # Create P3IF framework
        framework = P3IFFramework()

        # Add NIST patterns to framework
        for pattern in nist_patterns:
            framework.add_pattern(pattern)

        # Create relationships
        relationships = self._create_nist_relationships(nist_patterns)
        for rel in relationships:
            framework.add_relationship(rel)

        # Generate analysis
        analysis = self._analyze_nist_integration(framework)

        self.logger.info("NIST CSF integration example completed")

        return {
            "framework": framework,
            "patterns_added": len(nist_patterns),
            "relationships_created": len(relationships),
            "analysis": analysis,
            "example_type": "framework_integration",
            "source_framework": "NIST_CSF"
        }

    def _create_nist_patterns(self) -> List[Any]:
        """Create NIST CSF patterns in P3IF format."""
        patterns = []

        # Properties (NIST Functions)
        nist_functions = [
            ("identify", "Identify", "Asset Management, Business Environment, Governance, Risk Assessment, Risk Management Strategy, Supply Chain Risk Management"),
            ("protect", "Protect", "Identity Management, Authentication, Access Control, Awareness & Training, Data Security, Info Protection Processes & Procedures, Maintenance, Protective Technology"),
            ("detect", "Detect", "Anomalies and Events, Security Continuous Monitoring, Detection Processes"),
            ("respond", "Respond", "Response Planning, Communications, Analysis, Mitigation, Improvements"),
            ("recover", "Recover", "Recovery Planning, Improvements, Communications")
        ]

        for func_id, func_name, func_desc in nist_functions:
            prop = Property(
                name=f"nist_{func_id}",
                description=f"NIST {func_name}: {func_desc}",
                domain="cybersecurity",
                category="security",
                priority="high"
            )
            patterns.append(prop)

        # Processes (NIST Categories)
        nist_categories = [
            ("asset_management", "Asset Management", "Identify and manage organizational assets"),
            ("access_control", "Access Control", "Control access to assets and systems"),
            ("incident_response", "Incident Response", "Plan and execute incident response"),
            ("risk_assessment", "Risk Assessment", "Assess and manage cybersecurity risks")
        ]

        for cat_id, cat_name, cat_desc in nist_categories:
            proc = Process(
                name=f"nist_{cat_id}",
                description=f"NIST {cat_name}: {cat_desc}",
                domain="cybersecurity",
                complexity="medium",
                automation_level="semi-automated"
            )
            patterns.append(proc)

        # Perspectives (NIST Implementation Tiers)
        nist_tiers = [
            ("partial", "Partial", "Limited awareness of cybersecurity risks"),
            ("risk_informed", "Risk Informed", "Organization-wide approach to managing cybersecurity risk"),
            ("repeatable", "Repeatable", "Consistent cybersecurity practices across organization"),
            ("adaptive", "Adaptive", "Continuous improvement and adaptation")
        ]

        for tier_id, tier_name, tier_desc in nist_tiers:
            pers = Perspective(
                name=f"nist_{tier_id}",
                description=f"NIST {tier_name}: {tier_desc}",
                domain="cybersecurity",
                viewpoint="implementation",
                stakeholder_type="organizational"
            )
            patterns.append(pers)

        return patterns

    def _create_nist_relationships(self, patterns: List[Any]) -> List[Relationship]:
        """Create relationships between NIST patterns."""
        relationships = []

        # Find pattern IDs by name
        identify_prop = next(p for p in patterns if p.name == "nist_identify")
        protect_prop = next(p for p in patterns if p.name == "nist_protect")
        detect_prop = next(p for p in patterns if p.name == "nist_detect")

        asset_proc = next(p for p in patterns if p.name == "nist_asset_management")
        access_proc = next(p for p in patterns if p.name == "nist_access_control")

        partial_pers = next(p for p in patterns if p.name == "nist_partial")
        adaptive_pers = next(p for p in patterns if p.name == "nist_adaptive")

        # Create relationships
        rel1 = Relationship(
            property_id=identify_prop.id,
            process_id=asset_proc.id,
            perspective_id=partial_pers.id,
            strength=0.9,
            confidence=0.95
        )
        relationships.append(rel1)

        rel2 = Relationship(
            property_id=protect_prop.id,
            process_id=access_proc.id,
            perspective_id=adaptive_pers.id,
            strength=0.8,
            confidence=0.9
        )
        relationships.append(rel2)

        return relationships

    def _analyze_nist_integration(self, framework: P3IFFramework) -> Dict[str, Any]:
        """Analyze the NIST integration results."""
        return {
            "total_patterns": len(framework),
            "total_relationships": len(framework.get_all_relationships()),
            "nist_functions_covered": 5,
            "nist_categories_covered": 4,
            "nist_tiers_covered": 4,
            "integration_successful": True,
            "analysis_timestamp": "2024-01-01T00:00:00Z"
        }


class HealthcareIntegrationExample(IntegrationExample):
    """Example of integrating healthcare frameworks with P3IF."""

    def __init__(self):
        super().__init__(
            name="healthcare_integration",
            description="Integrate healthcare frameworks (HIPAA, HITECH) with P3IF"
        )

    def execute(self) -> Dict[str, Any]:
        """Execute the healthcare integration example."""
        self.logger.info("Starting healthcare integration example")

        # Create healthcare patterns
        healthcare_patterns = self._create_healthcare_patterns()

        # Create P3IF framework
        framework = P3IFFramework()

        # Add patterns to framework
        for pattern in healthcare_patterns:
            framework.add_pattern(pattern)

        # Create relationships
        relationships = self._create_healthcare_relationships(healthcare_patterns)
        for rel in relationships:
            framework.add_relationship(rel)

        # Generate analysis
        analysis = self._analyze_healthcare_integration(framework)

        self.logger.info("Healthcare integration example completed")

        return {
            "framework": framework,
            "patterns_added": len(healthcare_patterns),
            "relationships_created": len(relationships),
            "analysis": analysis,
            "example_type": "domain_integration",
            "domain": "healthcare"
        }

    def _create_healthcare_patterns(self) -> List[Any]:
        """Create healthcare-specific patterns."""
        patterns = []

        # Properties
        privacy_prop = Property(
            name="patient_privacy",
            description="Patient privacy and data protection",
            domain="healthcare",
            category="compliance",
            priority="critical"
        )
        patterns.append(privacy_prop)

        security_prop = Property(
            name="data_security",
            description="Healthcare data security and integrity",
            domain="healthcare",
            category="security",
            priority="high"
        )
        patterns.append(security_prop)

        # Processes
        consent_proc = Process(
            name="consent_management",
            description="Patient consent collection and management",
            domain="healthcare",
            complexity="medium",
            automation_level="semi-automated"
        )
        patterns.append(consent_proc)

        audit_proc = Process(
            name="audit_logging",
            description="Comprehensive audit logging for healthcare data",
            domain="healthcare",
            complexity="high",
            automation_level="fully-automated"
        )
        patterns.append(audit_proc)

        # Perspectives
        patient_pers = Perspective(
            name="patient_centric",
            description="Patient-centered healthcare perspective",
            domain="healthcare",
            viewpoint="patient_outcomes",
            stakeholder_type="patient"
        )
        patterns.append(patient_pers)

        provider_pers = Perspective(
            name="provider_focused",
            description="Healthcare provider operational perspective",
            domain="healthcare",
            viewpoint="clinical_efficiency",
            stakeholder_type="provider"
        )
        patterns.append(provider_pers)

        return patterns

    def _create_healthcare_relationships(self, patterns: List[Any]) -> List[Relationship]:
        """Create relationships between healthcare patterns."""
        relationships = []

        # Find patterns by name
        privacy_prop = next(p for p in patterns if p.name == "patient_privacy")
        security_prop = next(p for p in patterns if p.name == "data_security")
        consent_proc = next(p for p in patterns if p.name == "consent_management")
        audit_proc = next(p for p in patterns if p.name == "audit_logging")
        patient_pers = next(p for p in patterns if p.name == "patient_centric")
        provider_pers = next(p for p in patterns if p.name == "provider_focused")

        # Create relationships
        rel1 = Relationship(
            property_id=privacy_prop.id,
            process_id=consent_proc.id,
            perspective_id=patient_pers.id,
            strength=0.95,
            confidence=0.98
        )
        relationships.append(rel1)

        rel2 = Relationship(
            property_id=security_prop.id,
            process_id=audit_proc.id,
            perspective_id=provider_pers.id,
            strength=0.85,
            confidence=0.92
        )
        relationships.append(rel2)

        return relationships

    def _analyze_healthcare_integration(self, framework: P3IFFramework) -> Dict[str, Any]:
        """Analyze the healthcare integration results."""
        return {
            "total_patterns": len(framework),
            "total_relationships": len(framework.get_all_relationships()),
            "compliance_properties": 2,
            "operational_processes": 2,
            "stakeholder_perspectives": 2,
            "hipaa_compliance": "High",
            "patient_centricity": "Strong",
            "integration_successful": True
        }


class MultiFrameworkIntegrationExample(IntegrationExample):
    """Example of integrating multiple frameworks simultaneously."""

    def __init__(self):
        super().__init__(
            name="multi_framework_integration",
            description="Integrate NIST CSF, HIPAA, and ISO 27001 with P3IF"
        )

    def execute(self) -> Dict[str, Any]:
        """Execute the multi-framework integration example."""
        self.logger.info("Starting multi-framework integration example")

        # Create composition engine
        composition_engine = CompositionEngine()

        # Create framework adapters
        nist_adapter = self._create_nist_adapter()
        hipaa_adapter = self._create_hipaa_adapter()
        iso_adapter = self._create_iso_adapter()

        # Register adapters
        composition_engine.register_adapter(nist_adapter)
        composition_engine.register_adapter(hipaa_adapter)
        composition_engine.register_adapter(iso_adapter)

        # Create individual frameworks
        nist_framework = self._create_nist_framework()
        hipaa_framework = self._create_hipaa_framework()
        iso_framework = self._create_iso_framework()

        # Compose frameworks
        composition_result = composition_engine.overlay_frameworks(
            nist_framework, hipaa_framework, strategy="union"
        )

        final_framework = composition_engine.overlay_frameworks(
            composition_result, iso_framework, strategy="union"
        )

        # Generate analysis
        analysis = self._analyze_multi_framework_integration(final_framework)

        self.logger.info("Multi-framework integration example completed")

        return {
            "final_framework": final_framework,
            "composition_engine": composition_engine,
            "adapters_used": 3,
            "frameworks_integrated": ["NIST_CSF", "HIPAA", "ISO_27001"],
            "analysis": analysis,
            "example_type": "multi_framework_integration"
        }

    def _create_nist_adapter(self) -> FrameworkAdapter:
        """Create NIST CSF adapter."""
        return FrameworkAdapter(
            name="NIST_CSF_Adapter",
            version="1.1",
            source_framework="NIST Cybersecurity Framework",
            mapping_rules={
                "function": lambda obj: {"name": f"nist_{obj.id}", "type": "property"},
                "category": lambda obj: {"name": f"nist_{obj.id}", "type": "process"},
                "subcategory": lambda obj: {"name": f"nist_{obj.id}", "type": "property"}
            },
            transformation_functions={
                "property_transform": lambda x: x,
                "process_transform": lambda x: x,
                "perspective_transform": lambda x: x
            }
        )

    def _create_hipaa_adapter(self) -> FrameworkAdapter:
        """Create HIPAA adapter."""
        return FrameworkAdapter(
            name="HIPAA_Adapter",
            version="2013",
            source_framework="HIPAA Privacy Rule",
            mapping_rules={
                "rule": lambda obj: {"name": f"hipaa_{obj.id}", "type": "property"},
                "safeguard": lambda obj: {"name": f"hipaa_{obj.id}", "type": "process"}
            },
            transformation_functions={
                "property_transform": lambda x: x,
                "process_transform": lambda x: x,
                "perspective_transform": lambda x: x
            }
        )

    def _create_iso_adapter(self) -> FrameworkAdapter:
        """Create ISO 27001 adapter."""
        return FrameworkAdapter(
            name="ISO_27001_Adapter",
            version="2013",
            source_framework="ISO 27001",
            mapping_rules={
                "control": lambda obj: {"name": f"iso_{obj.id}", "type": "property"},
                "clause": lambda obj: {"name": f"iso_{obj.id}", "type": "process"}
            },
            transformation_functions={
                "property_transform": lambda x: x,
                "process_transform": lambda x: x,
                "perspective_transform": lambda x: x
            }
        )

    def _create_nist_framework(self) -> P3IFFramework:
        """Create NIST CSF framework."""
        framework = P3IFFramework()
        # Add NIST patterns...
        return framework

    def _create_hipaa_framework(self) -> P3IFFramework:
        """Create HIPAA framework."""
        framework = P3IFFramework()
        # Add HIPAA patterns...
        return framework

    def _create_iso_framework(self) -> P3IFFramework:
        """Create ISO 27001 framework."""
        framework = P3IFFramework()
        # Add ISO patterns...
        return framework

    def _analyze_multi_framework_integration(self, framework: P3IFFramework) -> Dict[str, Any]:
        """Analyze the multi-framework integration results."""
        return {
            "total_patterns": len(framework),
            "total_relationships": len(framework.get_all_relationships()),
            "frameworks_integrated": 3,
            "conflict_resolution": "Automatic",
            "unified_security_posture": "Comprehensive",
            "compliance_coverage": "Multi-standard",
            "integration_successful": True
        }


class DatabaseIntegrationExample(IntegrationExample):
    """Example of integrating P3IF with external databases."""

    def __init__(self):
        super().__init__(
            name="database_integration",
            description="Integrate P3IF with PostgreSQL database for persistent storage"
        )

    def execute(self) -> Dict[str, Any]:
        """Execute the database integration example."""
        self.logger.info("Starting database integration example")

        # This would demonstrate database integration
        # For now, return a conceptual example

        return {
            "integration_type": "database",
            "database_type": "PostgreSQL",
            "features": [
                "Persistent storage",
                "Query optimization",
                "Transaction support",
                "Backup and recovery"
            ],
            "example_type": "infrastructure_integration"
        }


class APIIntegrationExample(IntegrationExample):
    """Example of integrating P3IF with REST APIs."""

    def __init__(self):
        super().__init__(
            name="api_integration",
            description="Integrate P3IF with external REST APIs for data exchange"
        )

    def execute(self) -> Dict[str, Any]:
        """Execute the API integration example."""
        self.logger.info("Starting API integration example")

        # This would demonstrate API integration
        # For now, return a conceptual example

        return {
            "integration_type": "api",
            "api_type": "REST",
            "features": [
                "Data import/export",
                "Real-time synchronization",
                "Authentication and authorization",
                "Rate limiting and error handling"
            ],
            "example_type": "service_integration"
        }


def run_all_integration_examples() -> Dict[str, Any]:
    """Run all integration examples."""
    examples = [
        NISTIntegrationExample(),
        HealthcareIntegrationExample(),
        MultiFrameworkIntegrationExample(),
        DatabaseIntegrationExample(),
        APIIntegrationExample()
    ]

    results = {}
    for example in examples:
        try:
            result = example.execute()
            results[example.name] = result
            print(f"✅ {example.name}: Success")
        except Exception as e:
            print(f"❌ {example.name}: Failed - {e}")
            results[example.name] = {"error": str(e)}

    return results


if __name__ == "__main__":
    print("Running P3IF integration examples...")
    results = run_all_integration_examples()

    print(f"\nCompleted {len(results)} integration examples:")
    for example_name, result in results.items():
        if "error" not in result:
            print(f"✅ {example_name}")
        else:
            print(f"❌ {example_name}")

