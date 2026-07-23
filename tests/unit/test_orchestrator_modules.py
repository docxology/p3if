"""
Tests for orchestrators: CognitiveSecurityOrchestrator, FrameworkIntegrationOrchestrator.
"""

import unittest

from p3if.orchestrators.cognitive_security import CognitiveSecurityOrchestrator
from p3if.orchestrators.framework_integration import FrameworkIntegrationOrchestrator
from p3if.orchestrators.healthcare_domain import HealthcareDomainOrchestrator
from p3if.core.composition import FrameworkAdapter


class TestCognitiveSecurityOrchestrator(unittest.TestCase):
    """Test CognitiveSecurityOrchestrator."""

    def setUp(self):
        self.orchestrator = CognitiveSecurityOrchestrator()

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator.orchestrator)
        self.assertGreater(len(self.orchestrator.orchestrator.steps), 0)

    def test_execute_analysis(self):
        result = self.orchestrator.execute_analysis(domain_context="general")
        self.assertIn("analysis_timestamp", result)
        self.assertIn("domain_context", result)
        self.assertIn("step_results", result)
        self.assertIn("summary", result)
        self.assertIn("recommendations", result)

    def test_analysis_has_supply_chain(self):
        result = self.orchestrator.execute_analysis()
        self.assertIn("analyze_supply_chain", result["step_results"])

    def test_analysis_has_biases(self):
        result = self.orchestrator.execute_analysis()
        self.assertIn("identify_biases", result["step_results"])

    def test_analysis_has_manipulation_risks(self):
        result = self.orchestrator.execute_analysis()
        self.assertIn("assess_manipulation_risks", result["step_results"])

    def test_analysis_has_protection(self):
        result = self.orchestrator.execute_analysis()
        self.assertIn("design_protection", result["step_results"])

    def test_recommendations_generated(self):
        result = self.orchestrator.execute_analysis()
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_repr(self):
        r = repr(self.orchestrator)
        self.assertIn("CognitiveSecurityOrchestrator", r)


class TestFrameworkIntegrationOrchestrator(unittest.TestCase):
    """Test FrameworkIntegrationOrchestrator."""

    def setUp(self):
        self.orchestrator = FrameworkIntegrationOrchestrator()

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator.orchestrator)
        self.assertGreater(len(self.orchestrator.orchestrator.steps), 0)

    def test_add_framework_adapter(self):
        adapter = FrameworkAdapter(
            name="test_adapter",
            version="1.0",
            source_framework="Test Framework",
            mapping_rules={},
            transformation_functions={}
        )
        self.orchestrator.add_framework_adapter(adapter)
        self.assertIn("Test Framework", self.orchestrator.integrated_frameworks)

    def test_execute_integration_empty(self):
        """Integration with no adapters should complete without error."""
        result = self.orchestrator.execute_integration(framework_names=[])
        self.assertIn("integration_timestamp", result)
        self.assertIn("step_results", result)
        self.assertIn("summary", result)

    def test_execute_integration_with_cia(self):
        adapter = FrameworkAdapter(
            name="cia_adapter",
            version="1.0",
            source_framework="CIA Triad",
            mapping_rules={},
            transformation_functions={}
        )
        self.orchestrator.add_framework_adapter(adapter)
        result = self.orchestrator.execute_integration(framework_names=["CIA Triad"])
        self.assertIn("unified_model", result)
        self.assertIn("validation_results", result)

    def test_repr(self):
        r = repr(self.orchestrator)
        self.assertIn("FrameworkIntegrationOrchestrator", r)


class TestHealthcareDomainOrchestrator(unittest.TestCase):
    """Test HealthcareDomainOrchestrator."""

    def setUp(self):
        self.orchestrator = HealthcareDomainOrchestrator()

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator.orchestrator)
        self.assertGreater(len(self.orchestrator.orchestrator.steps), 0)

    def test_execute_analysis(self):
        result = self.orchestrator.execute_healthcare_analysis(organization_type="hospital")
        self.assertIn("analysis_timestamp", result)
        self.assertIn("organization_type", result)
        self.assertIn("step_results", result)
        self.assertIn("summary", result)
        self.assertIn("recommendations", result)

    def test_has_data_requirements_step(self):
        result = self.orchestrator.execute_healthcare_analysis()
        self.assertIn("analyze_data_requirements", result["step_results"])

    def test_has_compliance_step(self):
        result = self.orchestrator.execute_healthcare_analysis()
        self.assertIn("map_regulatory_compliance", result["step_results"])

    def test_has_privacy_step(self):
        result = self.orchestrator.execute_healthcare_analysis()
        self.assertIn("design_privacy_protection", result["step_results"])

    def test_has_workflow_step(self):
        result = self.orchestrator.execute_healthcare_analysis()
        self.assertIn("optimize_clinical_workflows", result["step_results"])

    def test_recommendations_generated(self):
        result = self.orchestrator.execute_healthcare_analysis()
        self.assertIsInstance(result["recommendations"], list)
        self.assertGreater(len(result["recommendations"]), 0)


if __name__ == '__main__':
    unittest.main()
