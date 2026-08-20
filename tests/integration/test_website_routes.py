"""
Integration tests for all website HTML and template routes (P11).
"""
import pytest
from website.app import create_app


@pytest.fixture
def web_client():
    """Create a Flask test client for website route integration tests."""
    app = create_app(testing=True)
    return app.test_client()


class TestWebsiteTemplateRoutes:
    """Test all website template routes render with 200 OK and valid links."""

    def test_home_page(self, web_client):
        response = web_client.get("/")
        assert response.status_code == 200
        assert b"P3IF" in response.data

    def test_about_page(self, web_client):
        response = web_client.get("/about")
        assert response.status_code == 200
        assert b"About" in response.data or b"P3IF" in response.data

    def test_domains_index(self, web_client):
        response = web_client.get("/domains/")
        assert response.status_code == 200
        assert b"Domains" in response.data

    def test_domain_detail_page(self, web_client):
        response = web_client.get("/domains/healthcare")
        assert response.status_code == 200
        assert b"Health" in response.data or b"healthcare" in response.data

    def test_domain_patterns_page(self, web_client):
        response = web_client.get("/domains/healthcare/patterns")
        assert response.status_code == 200
        assert b"Patterns" in response.data

    def test_visualizations_index(self, web_client):
        response = web_client.get("/visualizations/")
        assert response.status_code == 200
        assert b"Visualizations" in response.data or b"Gallery" in response.data

    def test_visualization_generate_form(self, web_client):
        response = web_client.get("/visualizations/generate")
        assert response.status_code == 200
        assert b"Generate" in response.data

    def test_docs_index(self, web_client):
        response = web_client.get("/docs/")
        assert response.status_code == 200
        assert b"Documentation" in response.data

    def test_docs_subpage(self, web_client):
        response = web_client.get("/docs/api/README")
        assert response.status_code == 200

    def test_dashboard_page(self, web_client):
        response = web_client.get("/visualizations/dashboard")
        assert response.status_code == 200
        assert b"P3IF" in response.data
