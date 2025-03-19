"""
Tests for P3IF domains module.

This module contains tests for the domain-related functionality in P3IF.
"""
import pytest
from pathlib import Path

from p3if.data.synthetic import SyntheticDataGenerator
from p3if.core.framework import P3IFFramework


class TestDomains:
    """Tests for the domains functionality."""
    
    def test_get_available_domains(self):
        """Test retrieving available domains."""
        # Create a generator
        generator = SyntheticDataGenerator()
        
        # Get available domains
        domains = generator.get_available_domains()
        
        # Verify that domains are returned
        assert isinstance(domains, list)
        assert len(domains) > 0
        assert all(isinstance(d, str) for d in domains)
    
    def test_load_domain_data(self):
        """Test loading domain data."""
        # Create a generator and framework
        generator = SyntheticDataGenerator()
        framework = P3IFFramework()
        
        # Get available domains
        domains = generator.get_available_domains()
        
        if domains:
            # Test with the first available domain
            domain_name = domains[0]
            generator.generate_for_domain(framework, domain_name)
            
            # Verify that domain data was loaded
            assert len(framework._patterns) > 0
            
            # Check that there are properties, processes, and perspectives
            properties = framework.get_patterns_by_type("property")
            processes = framework.get_patterns_by_type("process")
            perspectives = framework.get_patterns_by_type("perspective")
            
            assert len(properties) > 0
            assert len(processes) > 0
            assert len(perspectives) > 0
            
            # By default, generate_for_domain creates relationships
            assert len(framework._relationships) > 0 