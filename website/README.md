# P3IF Web Interface

The Pattern Portal for Interdisciplinary Frameworks (P3IF) web interface provides a user-friendly way to explore patterns across domains, visualize connections, and access documentation.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Flask and other dependencies (see requirements below)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/p3if.git
   cd p3if
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create necessary directories:
   ```bash
   mkdir -p website/logs output
   ```

### Running the Web Interface

Use the improved run script:

```bash
cd website
./run.py
```

This will start the server with improved logging and route information. The website will be accessible at http://localhost:5000.

Alternatively, you can use the standard Flask method:

```bash
cd website
python app.py
```

## Directory Structure

- `website/` - Main web application directory
  - `app.py` - Main Flask application
  - `run.py` - Improved startup script
  - `routes/` - Blueprint routes for different sections
  - `templates/` - Jinja2 templates for HTML rendering
  - `static/` - Static files (CSS, JS, images)
  - `logs/` - Log files

## Available Routes

- `/` - Home page
- `/about` - About page
- `/docs/` - Documentation browser
- `/domains/` - Domain explorer
- `/visualizations/` - Visualization gallery
- `/api/` - API endpoints

## Troubleshooting

If you encounter issues:

1. Check the log files in `website/logs/`
2. Ensure all templates are properly updated to use the correct endpoint names
3. Make sure the output and data/domains directories exist

## Development

When developing:

1. Use the debug mode (enabled by default)
2. Templates use Jinja2 syntax with inheritance from base.html
3. URL endpoints should reference blueprint names correctly (e.g., 'docs.index' not 'docs_bp.index')
4. Use 'url_for()' for generating URLs to ensure route changes don't break links 