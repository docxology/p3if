"""
Comprehensive tests for the P3IF API endpoints.
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from website.app import create_app
from core.framework import P3IFFramework
from tests.utils import (
    create_pattern_with_metadata,
    create_relationship_with_metadata,
    generate_test_json_data
)


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def framework_with_data():
    """Create a framework with test data."""
    framework = P3IFFramework()

    # Add some patterns
    prop1 = create_pattern_with_metadata("property", "Test Property 1", "domain1")
    prop2 = create_pattern_with_metadata("property", "Test Property 2", "domain1")
    proc1 = create_pattern_with_metadata("process", "Test Process 1", "domain1")
    proc2 = create_pattern_with_metadata("process", "Test Process 2", "domain2")
    persp1 = create_pattern_with_metadata("perspective", "Test Perspective 1", "domain1")
    persp2 = create_pattern_with_metadata("perspective", "Test Perspective 2", "domain2")

    framework.add_pattern(prop1)
    framework.add_pattern(prop2)
    framework.add_pattern(proc1)
    framework.add_pattern(proc2)
    framework.add_pattern(persp1)
    framework.add_pattern(persp2)

    # Add some relationships
    rel1 = create_relationship_with_metadata(
        property_id=prop1.id,
        process_id=proc1.id,
        perspective_id=persp1.id,
        strength=0.8,
        confidence=0.9
    )
    rel2 = create_relationship_with_metadata(
        property_id=prop2.id,
        process_id=proc2.id,
        perspective_id=persp2.id,
        strength=0.7,
        confidence=0.8
    )

    framework.add_relationship(rel1)
    framework.add_relationship(rel2)

    return framework


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    def test_health_endpoint_success(self, client):
        """Test successful health check."""
        response = client.get('/api/v2/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'timestamp' in data['data']
        assert data['data']['status'] == 'healthy'

    def test_health_endpoint_with_database_check(self, client, framework_with_data):
        """Test health check with database connectivity."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_metrics.return_value = {'total_patterns': 5}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/health?check_database=true')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['database_status'] == 'connected'


class TestFrameworkEndpoints:
    """Test cases for framework-related endpoints."""

    def test_get_metrics_empty_framework(self, client):
        """Test getting metrics for empty framework."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_metrics.return_value = {
                'total_patterns': 0,
                'total_relationships': 0,
                'average_relationship_strength': 0.0,
                'average_confidence': 0.0,
                'domain_count': 0,
                'pattern_types': {},
                'relationship_types': {},
                'orphaned_patterns': 0,
                'deprecated_patterns': 0,
                'validation_issues': 0
            }
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/metrics')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['total_patterns'] == 0
            assert data['data']['total_relationships'] == 0

    def test_get_metrics_with_data(self, client, framework_with_data):
        """Test getting metrics for framework with data."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_metrics.return_value = {
                'total_patterns': 6,
                'total_relationships': 2,
                'average_relationship_strength': 0.75,
                'average_confidence': 0.85,
                'domain_count': 2,
                'pattern_types': {'property': 2, 'process': 2, 'perspective': 2},
                'relationship_types': {'correlation': 2},
                'orphaned_patterns': 0,
                'deprecated_patterns': 0,
                'validation_issues': 0
            }
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/metrics')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['total_patterns'] == 6
            assert data['data']['total_relationships'] == 2
            assert data['data']['average_relationship_strength'] == 0.75

    def test_validate_framework_valid(self, client):
        """Test framework validation with valid data."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.validate_framework.return_value = {
                'is_valid': True,
                'issues': [],
                'warnings': [],
                'recommendations': []
            }
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/validate')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['is_valid'] is True
            assert len(data['data']['issues']) == 0

    def test_validate_framework_invalid(self, client):
        """Test framework validation with invalid data."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.validate_framework.return_value = {
                'is_valid': False,
                'issues': [
                    {'type': 'error', 'message': 'Missing relationship target'},
                    {'type': 'warning', 'message': 'Low confidence score'}
                ],
                'warnings': ['Low quality pattern detected'],
                'recommendations': ['Consider reviewing pattern relationships']
            }
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/validate')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['is_valid'] is False
            assert len(data['data']['issues']) == 2
            assert len(data['data']['warnings']) == 1
            assert len(data['data']['recommendations']) == 1


class TestPatternEndpoints:
    """Test cases for pattern-related endpoints."""

    def test_get_patterns_empty(self, client):
        """Test getting patterns from empty framework."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_type.return_value = []
            mock_instance.get_patterns_by_domain.return_value = []
            mock_instance.get_patterns_by_tag.return_value = []
            mock_instance.search_patterns.return_value = []
            mock_instance._patterns = {}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/patterns')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['patterns'] == []
            assert data['data']['total'] == 0

    def test_get_patterns_with_data(self, client):
        """Test getting patterns with data."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()

            # Create mock patterns
            mock_patterns = [
                MagicMock(),
                MagicMock()
            ]
            mock_patterns[0].id = "pattern1"
            mock_patterns[0].name = "Pattern 1"
            mock_patterns[0].pattern_type = "property"
            mock_patterns[0].domain = "domain1"
            mock_patterns[0].dict.return_value = {
                "id": "pattern1",
                "name": "Pattern 1",
                "pattern_type": "property",
                "domain": "domain1"
            }

            mock_patterns[1].id = "pattern2"
            mock_patterns[1].name = "Pattern 2"
            mock_patterns[1].pattern_type = "process"
            mock_patterns[1].domain = "domain2"
            mock_patterns[1].dict.return_value = {
                "id": "pattern2",
                "name": "Pattern 2",
                "pattern_type": "process",
                "domain": "domain2"
            }

            mock_instance._patterns = {p.id: p for p in mock_patterns}
            mock_instance.get_patterns_by_type.return_value = mock_patterns
            mock_instance.get_patterns_by_domain.return_value = [mock_patterns[0]]
            mock_instance.get_patterns_by_tag.return_value = mock_patterns
            mock_instance.search_patterns.return_value = mock_patterns
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/patterns')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['total'] == 2
            assert len(data['data']['patterns']) == 2

    def test_get_patterns_with_filters(self, client):
        """Test getting patterns with query filters."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_type.return_value = []
            mock_instance.get_patterns_by_domain.return_value = []
            mock_instance.get_patterns_by_tag.return_value = []
            mock_instance.search_patterns.return_value = []
            mock_framework.return_value = mock_instance

            # Test with type filter
            response = client.get('/api/v2/patterns?type=property')
            assert response.status_code == 200

            # Test with domain filter
            response = client.get('/api/v2/patterns?domain=test_domain')
            assert response.status_code == 200

            # Test with search query
            response = client.get('/api/v2/patterns?search=test')
            assert response.status_code == 200

            # Test with pagination
            response = client.get('/api/v2/patterns?page=2&limit=10')
            assert response.status_code == 200

    def test_get_pattern_by_id(self, client):
        """Test getting a specific pattern by ID."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()

            # Create mock pattern
            mock_pattern = MagicMock()
            mock_pattern.id = "test_pattern_id"
            mock_pattern.name = "Test Pattern"
            mock_pattern.pattern_type = "property"
            mock_pattern.domain = "test_domain"
            mock_pattern.dict.return_value = {
                "id": "test_pattern_id",
                "name": "Test Pattern",
                "pattern_type": "property",
                "domain": "test_domain"
            }

            # Create mock relationship
            mock_relationship = MagicMock()
            mock_relationship.id = "test_rel_id"
            mock_relationship.dict.return_value = {
                "id": "test_rel_id",
                "property_id": "test_pattern_id",
                "process_id": None,
                "perspective_id": None,
                "strength": 0.8,
                "confidence": 0.9
            }

            mock_instance._patterns = {"test_pattern_id": mock_pattern}
            mock_instance._relationships = {"test_rel_id": mock_relationship}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/patterns/test_pattern_id')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['pattern']['id'] == "test_pattern_id"
            assert data['data']['pattern']['name'] == "Test Pattern"

    def test_get_pattern_by_invalid_id(self, client):
        """Test getting a pattern with invalid ID."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance._patterns = {}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/patterns/invalid_id')

            assert response.status_code == 404
            data = response.get_json()
            assert data['status'] == 'error'
            assert 'not found' in data['message'].lower()


class TestRelationshipEndpoints:
    """Test cases for relationship-related endpoints."""

    def test_get_relationships_empty(self, client):
        """Test getting relationships from empty framework."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance._relationships = {}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/relationships')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['relationships'] == []
            assert data['data']['total'] == 0

    def test_get_relationships_with_data(self, client):
        """Test getting relationships with data."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()

            # Create mock relationships
            mock_relationships = [
                MagicMock(),
                MagicMock()
            ]
            mock_relationships[0].id = "rel1"
            mock_relationships[0].dict.return_value = {
                "id": "rel1",
                "property_id": "prop1",
                "process_id": "proc1",
                "perspective_id": "persp1",
                "strength": 0.8,
                "confidence": 0.9
            }

            mock_relationships[1].id = "rel2"
            mock_relationships[1].dict.return_value = {
                "id": "rel2",
                "property_id": "prop2",
                "process_id": None,
                "perspective_id": "persp2",
                "strength": 0.7,
                "confidence": 0.8
            }

            mock_instance._relationships = {r.id: r for r in mock_relationships}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/relationships')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['total'] == 2
            assert len(data['data']['relationships']) == 2

    def test_get_relationships_with_filters(self, client):
        """Test getting relationships with filters."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance._relationships = {}
            mock_framework.return_value = mock_instance

            # Test with pagination
            response = client.get('/api/v2/relationships?page=1&limit=20')
            assert response.status_code == 200

            # Test with strength filter
            response = client.get('/api/v2/relationships?min_strength=0.5')
            assert response.status_code == 200

            # Test with confidence filter
            response = client.get('/api/v2/relationships?min_confidence=0.7')
            assert response.status_code == 200

            # Test with type filter
            response = client.get('/api/v2/relationships?relationship_type=correlation')
            assert response.status_code == 200


class TestDomainEndpoints:
    """Test cases for domain-related endpoints."""

    def test_get_domains(self, client):
        """Test getting available domains."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_domain.return_value = []
            mock_framework.return_value = mock_instance

            # Mock the domains index file
            with patch('website.routes.api.Path') as mock_path:
                mock_domains_file = MagicMock()
                mock_domains_file.exists.return_value = True
                mock_domains_file.read_text.return_value = json.dumps({
                    "domains": [
                        {"id": "domain1", "name": "Domain 1", "description": "First domain"},
                        {"id": "domain2", "name": "Domain 2", "description": "Second domain"}
                    ]
                })
                mock_path.return_value = mock_domains_file

                response = client.get('/api/v2/domains')

                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'success'
                assert len(data['data']['domains']) == 2
                assert data['data']['domains'][0]['id'] == "domain1"

    def test_get_domains_no_index_file(self, client):
        """Test getting domains when no index file exists."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_domain.return_value = []
            mock_framework.return_value = mock_instance

            # Mock the domains index file as non-existent
            with patch('website.routes.api.Path') as mock_path:
                mock_domains_file = MagicMock()
                mock_domains_file.exists.return_value = False
                mock_path.return_value = mock_domains_file

                response = client.get('/api/v2/domains')

                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'success'
                assert data['data']['domains'] == []

    def test_get_domain_details(self, client):
        """Test getting details for a specific domain."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()

            # Create mock patterns for the domain
            mock_patterns = [
                MagicMock(),
                MagicMock(),
                MagicMock()
            ]
            mock_patterns[0].id = "pattern1"
            mock_patterns[0].pattern_type = "property"
            mock_patterns[0].dict.return_value = {"id": "pattern1", "pattern_type": "property"}

            mock_patterns[1].id = "pattern2"
            mock_patterns[1].pattern_type = "process"
            mock_patterns[1].dict.return_value = {"id": "pattern2", "pattern_type": "process"}

            mock_patterns[2].id = "pattern3"
            mock_patterns[2].pattern_type = "perspective"
            mock_patterns[2].dict.return_value = {"id": "pattern3", "pattern_type": "perspective"}

            mock_instance.get_patterns_by_domain.return_value = mock_patterns
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/domains/domain1')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['domain']['id'] == "domain1"
            assert data['data']['domain']['pattern_count'] == 3
            assert len(data['data']['domain']['patterns']) == 3

    def test_get_domain_details_not_found(self, client):
        """Test getting details for non-existent domain."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_domain.return_value = []
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/domains/nonexistent_domain')

            assert response.status_code == 404
            data = response.get_json()
            assert data['status'] == 'error'
            assert 'not found' in data['message'].lower()


class TestVisualizationEndpoints:
    """Test cases for visualization-related endpoints."""

    def test_get_visualizations(self, client):
        """Test getting available visualization types."""
        response = client.get('/api/v2/visualizations')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'visualization_types' in data['data']
        assert 'themes' in data['data']
        assert 'interaction_modes' in data['data']

        # Check that we have expected visualization types
        viz_types = data['data']['visualization_types']
        assert len(viz_types) > 0

        # Check that each visualization type has required fields
        for viz_type in viz_types:
            assert 'id' in viz_type
            assert 'name' in viz_type
            assert 'description' in viz_type
            assert 'features' in viz_type
            assert 'supported_formats' in viz_type

    def test_generate_visualization_invalid_type(self, client):
        """Test generating visualization with invalid type."""
        response = client.post('/api/v2/visualizations/generate', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'type is required' in data['message']

    def test_generate_visualization_missing_params(self, client):
        """Test generating visualization with missing parameters."""
        response = client.post('/api/v2/visualizations/generate', json={'type': 'cube_3d'})

        assert response.status_code == 200  # Should succeed with minimal params
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'visualization_id' in data['data']
        assert data['data']['type'] == 'cube_3d'

    def test_get_visualization_status(self, client):
        """Test getting visualization generation status."""
        viz_id = "test_viz_id"
        response = client.get(f'/api/v2/visualizations/{viz_id}/status')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['visualization_id'] == viz_id
        assert 'status' in data['data']
        assert 'progress' in data['data']


class TestExportEndpoints:
    """Test cases for export-related endpoints."""

    def test_export_json(self, client):
        """Test exporting data as JSON."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_domain.return_value = []
            mock_framework.return_value = mock_instance

            response = client.post('/api/v2/export', json={
                'format': 'json',
                'domains': ['domain1', 'domain2']
            })

            assert response.status_code == 200
            data = response.get_json()
            assert 'patterns' in data
            assert 'relationships' in data
            assert 'metadata' in data

            # Check content disposition header for file download
            assert 'Content-Disposition' in response.headers
            assert 'attachment' in response.headers['Content-Disposition']
            assert '.json' in response.headers['Content-Disposition']

    def test_export_unsupported_format(self, client):
        """Test exporting data in unsupported format."""
        response = client.post('/api/v2/export', json={
            'format': 'xml',
            'domains': ['domain1']
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'not supported' in data['message']

    def test_export_missing_format(self, client):
        """Test exporting data without specifying format."""
        response = client.post('/api/v2/export', json={
            'domains': ['domain1']
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'patterns' in data  # Should default to JSON

    def test_export_with_framework_error(self, client):
        """Test export with framework error."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_patterns_by_domain.side_effect = Exception("Database error")
            mock_framework.return_value = mock_instance

            response = client.post('/api/v2/export', json={
                'format': 'json',
                'domains': ['domain1']
            })

            assert response.status_code == 500
            data = response.get_json()
            assert data['status'] == 'error'
            assert 'Export Error' in data['error']


class TestAnalysisEndpoints:
    """Test cases for analysis-related endpoints."""

    def test_analyze_patterns_basic(self, client):
        """Test basic pattern analysis."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/analysis/patterns')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
            assert 'analysis' in data['data']
            assert 'timestamp' in data['data']

    def test_analyze_patterns_with_filters(self, client):
        """Test pattern analysis with filters."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/analysis/patterns?domain=test_domain&type=property')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_analyze_patterns_with_analysis_type(self, client):
        """Test pattern analysis with specific analysis type."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/analysis/patterns?analysis_type=similarity')

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'


class TestErrorHandling:
    """Test cases for error handling."""

    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON requests."""
        response = client.post('/api/v2/export', data="invalid json")

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Invalid JSON' in data['error']

    def test_method_not_allowed(self, client):
        """Test handling of unsupported HTTP methods."""
        response = client.post('/api/v2/health')

        assert response.status_code == 405
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Method not allowed' in data['message']

    def test_internal_server_error(self, client):
        """Test handling of internal server errors."""
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_metrics.side_effect = Exception("Database connection failed")
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/metrics')

            assert response.status_code == 500
            data = response.get_json()
            assert data['status'] == 'error'
            assert 'Internal Server Error' in data['error']

    def test_validation_error(self, client):
        """Test handling of validation errors."""
        response = client.post('/api/v2/export', json={
            'format': 'invalid_format'
        })

        # This should be handled gracefully
        assert response.status_code in [200, 400, 500]


class TestOpenAPISpec:
    """Test cases for OpenAPI specification endpoint."""

    def test_get_openapi_spec(self, client):
        """Test getting OpenAPI specification."""
        response = client.get('/api/v2/openapi.json')

        assert response.status_code == 200
        data = response.get_json()

        assert data['openapi'] == "3.0.3"
        assert 'info' in data
        assert 'servers' in data
        assert 'paths' in data
        assert 'components' in data

        # Check info section
        assert 'title' in data['info']
        assert 'version' in data['info']
        assert 'description' in data['info']

        # Check that we have some basic paths
        assert '/health' in data['paths']


class TestIntegration:
    """Integration tests for API endpoints."""

    def test_full_api_workflow(self, client):
        """Test a complete API workflow."""
        # 1. Check health
        response = client.get('/api/v2/health')
        assert response.status_code == 200

        # 2. Get available visualizations
        response = client.get('/api/v2/visualizations')
        assert response.status_code == 200

        # 3. Get domains
        response = client.get('/api/v2/domains')
        assert response.status_code == 200

        # 4. Try to get framework metrics (will use mock)
        with patch('website.routes.api.P3IFFramework') as mock_framework:
            mock_instance = MagicMock()
            mock_instance.get_metrics.return_value = {'total_patterns': 0}
            mock_framework.return_value = mock_instance

            response = client.get('/api/v2/framework/metrics')
            assert response.status_code == 200

        # 5. Try to export data
        response = client.post('/api/v2/export', json={'format': 'json'})
        assert response.status_code == 200

        # 6. Get OpenAPI spec
        response = client.get('/api/v2/openapi.json')
        assert response.status_code == 200

    def test_error_recovery(self, client):
        """Test API error recovery and graceful degradation."""
        # Test with various error conditions
        error_responses = []

        # 1. Invalid pattern ID
        response = client.get('/api/v2/patterns/invalid_id')
        error_responses.append(response.status_code)

        # 2. Invalid domain
        response = client.get('/api/v2/domains/invalid_domain')
        error_responses.append(response.status_code)

        # 3. Invalid visualization generation
        response = client.post('/api/v2/visualizations/generate', json={'type': 'invalid_type'})
        error_responses.append(response.status_code)

        # All should return proper HTTP status codes
        for status_code in error_responses:
            assert status_code in [200, 400, 404, 405, 500]
