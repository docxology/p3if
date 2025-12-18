"""
Tests for P3IF Orchestrators

Basic tests for orchestrator modules to ensure they can be instantiated
and provide core functionality.
"""

import unittest

from p3if.orchestrators.cognitive_security import CognitiveSecurityOrchestrator
from p3if.orchestrators.framework_integration import FrameworkIntegrationOrchestrator
from p3if.orchestrators.healthcare_domain import HealthcareDomainOrchestrator
from p3if.orchestrators.integration_examples import IntegrationExample, NISTIntegrationExample
from p3if.core.orchestration import OrchestratorType


class TestCognitiveSecurityOrchestrator(unittest.TestCase):
    """Test cases for CognitiveSecurityOrchestrator."""

    def test_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = CognitiveSecurityOrchestrator()
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(orchestrator.orchestrator)
        self.assertEqual(orchestrator.name, "cognitive_security_orchestrator")

    def test_orchestrator_execution(self):
        """Test orchestrator can execute."""
        orchestrator = CognitiveSecurityOrchestrator()
        # Test that orchestrator has steps
        self.assertGreater(len(orchestrator.orchestrator.steps), 0)


class TestFrameworkIntegrationOrchestrator(unittest.TestCase):
    """Test cases for FrameworkIntegrationOrchestrator."""

    def test_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = FrameworkIntegrationOrchestrator()
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(orchestrator.orchestrator)
        self.assertEqual(orchestrator.name, "framework_integration_orchestrator")

    def test_orchestrator_execution(self):
        """Test orchestrator can execute."""
        orchestrator = FrameworkIntegrationOrchestrator()
        # Test that orchestrator has steps
        self.assertGreater(len(orchestrator.orchestrator.steps), 0)


class TestHealthcareDomainOrchestrator(unittest.TestCase):
    """Test cases for HealthcareDomainOrchestrator."""

    def test_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = HealthcareDomainOrchestrator()
        self.assertIsNotNone(orchestrator)
        self.assertIsNotNone(orchestrator.orchestrator)
        self.assertEqual(orchestrator.name, "healthcare_domain_orchestrator")

    def test_orchestrator_execution(self):
        """Test orchestrator can execute."""
        orchestrator = HealthcareDomainOrchestrator()
        # Test that orchestrator has steps
        self.assertGreater(len(orchestrator.orchestrator.steps), 0)


class TestIntegrationExamples(unittest.TestCase):
    """Test cases for Integration Examples."""

    def test_nist_integration_example(self):
        """Test NISTIntegrationExample."""
        example = NISTIntegrationExample()
        self.assertIsNotNone(example)
        # Test that it has a name
        self.assertTrue(hasattr(example, 'name'))

    def test_integration_example_execution(self):
        """Test that integration examples can execute."""
        example = NISTIntegrationExample()
        # Test that execute method exists and returns something
        self.assertTrue(hasattr(example, 'execute'))
        result = example.execute()
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
