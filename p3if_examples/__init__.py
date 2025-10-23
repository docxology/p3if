"""
P3IF Thin Orchestrator Examples

This package provides thin orchestrator examples demonstrating flexible composition
of P3IF methods for common use cases.
"""

from p3if_examples.cognitive_security_orchestrator import CognitiveSecurityOrchestrator
from p3if_examples.framework_integration_orchestrator import FrameworkIntegrationOrchestrator
from p3if_examples.healthcare_domain_orchestrator import HealthcareDomainOrchestrator
from p3if_examples.integration_examples import (
    NISTIntegrationExample,
    HealthcareIntegrationExample,
    MultiFrameworkIntegrationExample,
    DatabaseIntegrationExample,
    APIIntegrationExample,
    run_all_integration_examples
)

__all__ = [
    'CognitiveSecurityOrchestrator',
    'FrameworkIntegrationOrchestrator',
    'HealthcareDomainOrchestrator',
    'NISTIntegrationExample',
    'HealthcareIntegrationExample',
    'MultiFrameworkIntegrationExample',
    'DatabaseIntegrationExample',
    'APIIntegrationExample',
    'run_all_integration_examples'
]
