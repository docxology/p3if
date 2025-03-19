#!/bin/bash

# Script to serve the P3IF website locally

echo "Starting P3IF Website server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "Main portals:"
echo "- Portal: http://localhost:8000/output/portal/"
echo "- Website: http://localhost:8000/website/dist/"
echo ""
echo "Key visualization files:"
echo "- Combined Visualization: http://localhost:8000/output/visualizations/combined_visualization.html"
echo "- Cybersecurity Visualization: http://localhost:8000/output/visualizations/cybersecurity_visualization.html"
echo "- AI Visualization: http://localhost:8000/output/visualizations/artificialintelligence_visualization.html"
echo "- Healthcare Visualization: http://localhost:8000/output/visualizations/healthcare_visualization.html"
echo ""

# Change to the project root directory
cd "$(dirname "$0")"

# Start a simple HTTP server (works with Python 3)
python3 -m http.server 