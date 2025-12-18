# P3IF Web Interface

## Overview

The `website/` directory contains the P3IF web portal, a Flask-based application that provides an interactive web interface for exploring, visualizing, and analyzing P3IF frameworks across multiple domains.

## Architecture

```
website/
├── app.py                     # Main Flask application and routing
├── run.py                     # Enhanced development server startup
├── run_stable.py              # Production server configuration
├── routes/                    # Blueprint-based route modules
│   ├── __init__.py           # Route package initialization
│   ├── api.py                # RESTful API endpoints (v2)
│   ├── docs.py               # Documentation browsing routes
│   ├── domains.py            # Domain exploration interface
│   ├── visualizations.py     # Visualization gallery and tools
│   └── viz_generate.py       # Dynamic visualization generation
├── static/                   # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── styles.css        # Main stylesheet
│   ├── js/
│   │   └── main.js           # Client-side JavaScript
│   └── img/                  # Static images and icons
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Home page
│   ├── about.html            # About page
│   ├── docs/                 # Documentation templates
│   ├── domains/              # Domain exploration templates
│   └── visualizations/       # Visualization interface templates
└── logs/                     # Application logs
```

## Core Components

### Main Application (`app.py`)

The central Flask application that coordinates all web functionality:

```python
from website.app import app

# Run development server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

**Key Features:**
- Blueprint-based modular routing
- Markdown rendering for documentation
- Static file serving with caching
- Comprehensive logging and error handling
- Cross-origin resource sharing (CORS) support

### Enhanced API (`routes/api.py`)

Modern RESTful API with comprehensive P3IF functionality:

```python
# Get framework domains
curl http://localhost:5000/api/v2/domains

# Generate visualization
curl -X POST http://localhost:5000/api/v2/visualizations/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "3d_cube", "domain_id": "cybersecurity"}'
```

**Key Features:**
- OpenAPI-compliant endpoints
- Comprehensive error handling with proper HTTP status codes
- Input validation and sanitization
- Rate limiting and request logging
- CORS support for cross-origin requests

### Route Modules

#### Documentation Routes (`routes/docs.py`)
- Browse and render markdown documentation
- Table of contents generation
- Search functionality across docs
- Version-specific documentation access

#### Domain Routes (`routes/domains.py`)
- Interactive domain exploration
- Pattern browsing by domain
- Cross-domain relationship visualization
- Domain comparison tools

#### Visualization Routes (`routes/visualizations.py`)
- Gallery of available visualizations
- Interactive visualization viewers
- Export functionality for static assets
- Real-time visualization generation

#### Generation Routes (`routes/viz_generate.py`)
- Dynamic visualization creation
- Parameter-based customization
- Background processing for complex visualizations
- Result caching and retrieval

## User Interface

### Templates Structure

The web interface uses Jinja2 templates with a consistent design:

- **Base Template**: Common navigation, footer, and styling
- **Documentation**: Markdown rendering with syntax highlighting
- **Domain Explorer**: Interactive pattern browsing and filtering
- **Visualization Gallery**: Grid layout with preview thumbnails
- **API Documentation**: Interactive endpoint testing

### Static Assets

- **CSS**: Modern, responsive styling with dark/light themes
- **JavaScript**: Client-side interactivity and visualization controls
- **Images**: Icons, logos, and visualization previews

## API Endpoints

### Framework Operations

```
GET    /api/v2/frameworks              # List available frameworks
POST   /api/v2/frameworks              # Create new framework
GET    /api/v2/frameworks/{id}         # Get framework details
PUT    /api/v2/frameworks/{id}         # Update framework
DELETE /api/v2/frameworks/{id}         # Delete framework
```

### Domain Management

```
GET    /api/v2/domains                  # List all domains
GET    /api/v2/domains/{id}             # Get domain details
GET    /api/v2/domains/{id}/patterns    # Get domain patterns
POST   /api/v2/domains/{id}/patterns    # Add pattern to domain
```

### Visualization Generation

```
POST   /api/v2/visualizations/generate   # Generate visualization
GET    /api/v2/visualizations/{id}       # Get visualization status
GET    /api/v2/visualizations/{id}/download # Download visualization
GET    /api/v2/visualizations/types      # List visualization types
```

## Development and Deployment

### Development Server

```bash
# Using the enhanced run script
cd website
./run.py

# Or using standard Flask
python app.py
```

### Production Deployment

```bash
# Using production server
cd website
./run_stable.py
```

### Docker Support

The website is designed to work with containerized deployment:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "website/run_stable.py"]
```

## Configuration

### Environment Variables

- `FLASK_SECRET_KEY`: Session management secret
- `FLASK_ENV`: Environment (development/production)
- `P3IF_DATA_DIR`: Custom data directory path
- `P3IF_CACHE_DIR`: Cache directory for generated content

### Application Configuration

```python
# In app.py or config file
app.config.update(
    SECRET_KEY="your-secret-key",
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True
)
```

## Security Features

### Authentication and Authorization
- API key authentication for sensitive endpoints
- Session management with secure cookies
- Rate limiting to prevent abuse
- Input validation and sanitization

### Data Protection
- HTTPS enforcement in production
- Secure headers (CSP, HSTS, etc.)
- SQL injection prevention
- XSS protection through template escaping

## Performance Optimization

### Caching Strategies
- Static asset caching with versioning
- Generated visualization caching
- Database query result caching
- CDN integration for static assets

### Scalability Features
- Asynchronous task processing
- Database connection pooling
- Memory-efficient data structures
- Background job processing

## Testing

Run website tests:

```bash
# API tests
python -m pytest p3if_tests/website/test_api.py -v

# Integration tests
python -m pytest p3if_tests/visualization/test_integrated_website.py -v
```

## Monitoring and Logging

### Application Logs

Logs are stored in `website/logs/` with rotation:

- `website.log`: Main application log
- `error.log`: Error-only log
- `access.log`: HTTP access log

### Health Checks

```
GET /api/v2/health          # Application health status
GET /api/v2/metrics         # Performance metrics
GET /api/v2/status          # System status information
```

## Integration with P3IF Core

The web interface integrates with all P3IF components:

- **Core Framework**: Direct integration with `P3IFFramework`
- **Visualization System**: Uses `p3if_visualization` modules
- **Analysis Tools**: Exposes analysis capabilities via API
- **Domain Management**: Works with domain data and synthetic generators

## Browser Compatibility

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Support**: Responsive design for tablets and phones
- **Accessibility**: WCAG 2.1 AA compliance
- **Progressive Enhancement**: Works without JavaScript

## Contributing

When contributing to the web interface:

1. Follow Flask best practices and security guidelines
2. Include comprehensive API documentation
3. Add client-side and server-side validation
4. Test across multiple browsers and devices
5. Follow the established template and styling patterns
6. Update this documentation for new features

The P3IF web interface provides a user-friendly gateway to the powerful capabilities of the P3IF framework, enabling interactive exploration and analysis of complex multi-domain systems.





