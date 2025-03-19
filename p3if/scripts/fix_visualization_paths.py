#!/usr/bin/env python3
"""
Fix visualization paths script for P3IF Website.

This script ensures that all generated visualization outputs are correctly 
placed in the website/dist directory according to the expected file structure.
"""
import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

class VisualizationFixer:
    """Class to fix visualization file paths."""
    
    def __init__(self):
        """Initialize the path fixer."""
        # Setup paths
        self.base_dir = Path(os.getcwd())
        self.output_dir = self.base_dir / 'output'
        self.portal_output_dir = self.output_dir / 'portal'
        self.website_dir = self.base_dir / 'website'
        self.dist_dir = self.website_dir / 'dist'
        self.visualizations_dir = self.dist_dir / 'visualizations'
        
        # Create directories if they don't exist
        self.visualizations_dir.mkdir(parents=True, exist_ok=True)
        
    def create_directory_structure(self):
        """Create the expected directory structure in the dist folder."""
        # Create visualization type directories
        for viz_type in ['3d-cube', 'network', 'dashboard', 'matrix']:
            viz_dir = self.visualizations_dir / viz_type
            viz_dir.mkdir(parents=True, exist_ok=True)
            
            # Create an index.html file in each visualization directory if it doesn't exist
            index_file = viz_dir / 'index.html'
            if not index_file.exists():
                self._create_placeholder_html(index_file, viz_type)
                
        # Create assets directories
        assets_dir = self.dist_dir / 'assets'
        for asset_type in ['css', 'js', 'images', 'data']:
            (assets_dir / asset_type).mkdir(parents=True, exist_ok=True)
            
        logger.info("Created directory structure")
        
    def copy_portal_visualizations(self):
        """Copy visualizations from the portal output to the correct locations."""
        if not self.portal_output_dir.exists():
            logger.warning(f"Portal output directory not found: {self.portal_output_dir}")
            return
            
        # Copy main visualizations
        viz_mappings = {
            '3d-cube.html': self.visualizations_dir / '3d-cube' / 'index.html',
            'force-graph.html': self.visualizations_dir / 'network' / 'index.html'
        }
        
        # If the portal_output_dir/visualizations exists, look for visualization files there
        portal_viz_dir = self.portal_output_dir / 'visualizations'
        if portal_viz_dir.exists():
            for src_name, dest_path in viz_mappings.items():
                src_path = portal_viz_dir / src_name
                if src_path.exists():
                    shutil.copy2(src_path, dest_path)
                    logger.info(f"Copied {src_path} to {dest_path}")
                else:
                    logger.warning(f"Source file not found: {src_path}")
                
        # Copy overview dashboard if it exists
        overview_dir = portal_viz_dir / 'overview' if portal_viz_dir.exists() else None
        if overview_dir and overview_dir.exists():
            dashboard_dir = self.visualizations_dir / 'dashboard'
            # Copy all files from overview to dashboard
            for item in overview_dir.glob('*'):
                if item.is_file():
                    shutil.copy2(item, dashboard_dir / item.name)
                    logger.info(f"Copied {item} to {dashboard_dir / item.name}")
            
            # Create index.html that references these files
            index_path = dashboard_dir / 'index.html'
            self._create_dashboard_html(index_path, [f.name for f in overview_dir.glob('*.png')])
        else:
            # Create a default dashboard if one doesn't exist yet
            dashboard_dir = self.visualizations_dir / 'dashboard'
            index_path = dashboard_dir / 'index.html'
            if not index_path.exists() or os.path.getsize(index_path) < 100:
                self._create_dashboard_html(index_path, [])
            
        # Create matrix visualization if doesn't exist
        matrix_index = self.visualizations_dir / 'matrix' / 'index.html'
        if not matrix_index.exists() or os.path.getsize(matrix_index) < 100:
            self._create_matrix_html(matrix_index)
            
    def _create_placeholder_html(self, path, viz_type):
        """Create a placeholder HTML file for a visualization."""
        title_map = {
            '3d-cube': '3D Cube Visualization',
            'network': 'Network Visualization',
            'dashboard': 'Dashboard Visualization',
            'matrix': 'Matrix Visualization'
        }
        
        title = title_map.get(viz_type, f"{viz_type.capitalize()} Visualization")
        
        with open(path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - P3IF</title>
    <link rel="stylesheet" href="/assets/css/styles.css">
    <link rel="stylesheet" href="/assets/css/visualizations.css">
</head>
<body>
    <div class="visualization-container">
        <h1>{title}</h1>
        <p>Loading visualization...</p>
        
        <div class="visualization-placeholder" id="{viz_type}-container">
            <!-- Visualization will be loaded here -->
        </div>
    </div>
    
    <script src="/assets/js/visualizations.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Initialize visualization
            console.log('Loading {viz_type} visualization...');
        }});
    </script>
</body>
</html>""")
        logger.info(f"Created placeholder HTML: {path}")
            
    def _create_dashboard_html(self, path, image_files):
        """Create a dashboard HTML file that includes the images."""
        with open(path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Visualization - P3IF</title>
    <link rel="stylesheet" href="/assets/css/styles.css">
    <link rel="stylesheet" href="/assets/css/visualizations.css">
    <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .dashboard-item {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        .dashboard-item img {
            width: 100%;
            height: auto;
            display: block;
        }
        .dashboard-caption {
            padding: 10px;
            background: #f5f5f5;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="visualization-container">
        <h1>Dashboard Visualization</h1>
""")
            
            # If we have images, show them in the dashboard
            if image_files:
                f.write("""        <div class="dashboard-grid">
""")
                # Add each image to the dashboard
                for img_file in image_files:
                    name = os.path.splitext(img_file)[0].replace('_', ' ').title()
                    f.write(f"""            <div class="dashboard-item">
                <img src="{img_file}" alt="{name}">
                <div class="dashboard-caption">{name}</div>
            </div>
""")
                f.write("""        </div>
""")
            # If no images, show a placeholder
            else:
                f.write("""        <div class="dashboard-placeholder">
            <h2>No dashboard data available</h2>
            <p>Please run the P3IF visualization scripts to generate dashboard data.</p>
        </div>
""")
                
            f.write("""    </div>
</body>
</html>""")
        logger.info(f"Created dashboard HTML: {path}")
            
    def _create_matrix_html(self, path):
        """Create a matrix visualization HTML file."""
        with open(path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matrix Visualization - P3IF Framework</title>
    <link rel="stylesheet" href="/assets/css/styles.css">
    <link rel="stylesheet" href="/assets/css/visualizations.css">
    <style>
        .matrix-container {
            width: 100%;
            height: 100%;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        .controls {
            margin-bottom: 20px;
        }
        select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        .matrix-view {
            flex: 1;
            overflow: auto;
        }
        .matrix-view svg {
            display: block;
            margin: 0 auto;
        }
        .legend {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
        }
        .legend h3 {
            margin-top: 0;
            margin-bottom: 10px;
        }
        .legend-gradient {
            width: 200px;
            height: 20px;
            margin-bottom: 5px;
            background: linear-gradient(to right, #f8f9fa, #4285F4);
        }
        .legend-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
    </style>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div class="matrix-container">
        <div class="controls">
            <select id="matrix-type">
                <option value="property-process">Property-Process Matrix</option>
                <option value="property-perspective">Property-Perspective Matrix</option>
                <option value="process-perspective">Process-Perspective Matrix</option>
            </select>
        </div>
        <div class="matrix-view" id="matrix-view"></div>
        
        <div class="legend">
            <h3>Relationship Strength</h3>
            <div class="legend-gradient"></div>
            <div class="legend-labels">
                <span>Weak</span>
                <span>Strong</span>
            </div>
        </div>
    </div>

    <script>
        // This would be loaded from actual data
        const data = {
            "property-process": {
                rows: ["Data Integrity", "Security", "Scalability", "Usability", "Reliability"],
                columns: ["Data Processing", "Authentication", "Deployment", "Testing", "Monitoring"],
                values: [
                    [0.9, 0.5, 0.2, 0.7, 0.6],
                    [0.3, 0.9, 0.4, 0.6, 0.5],
                    [0.4, 0.2, 0.8, 0.3, 0.7],
                    [0.7, 0.6, 0.5, 0.3, 0.2],
                    [0.5, 0.4, 0.6, 0.8, 0.9]
                ]
            },
            "property-perspective": {
                rows: ["Data Integrity", "Security", "Scalability", "Usability", "Reliability"],
                columns: ["User Experience", "Developer Experience", "System Administration", "Business", "Security"],
                values: [
                    [0.7, 0.4, 0.5, 0.8, 0.9],
                    [0.6, 0.3, 0.4, 0.5, 0.9],
                    [0.5, 0.7, 0.8, 0.6, 0.2],
                    [0.9, 0.6, 0.2, 0.7, 0.4],
                    [0.4, 0.5, 0.7, 0.3, 0.8]
                ]
            },
            "process-perspective": {
                rows: ["Data Processing", "Authentication", "Deployment", "Testing", "Monitoring"],
                columns: ["User Experience", "Developer Experience", "System Administration", "Business", "Security"],
                values: [
                    [0.8, 0.7, 0.4, 0.6, 0.5],
                    [0.7, 0.3, 0.5, 0.4, 0.9],
                    [0.3, 0.8, 0.7, 0.5, 0.4],
                    [0.5, 0.9, 0.6, 0.3, 0.4],
                    [0.4, 0.5, 0.9, 0.2, 0.8]
                ]
            }
        };

        // Create matrix visualization
        function createMatrix(matrixType) {
            // Clear existing visualization
            d3.select("#matrix-view").html("");
            
            const matrixData = data[matrixType];
            
            // Set dimensions
            const margin = { top: 80, right: 50, bottom: 50, left: 120 };
            const containerWidth = document.getElementById("matrix-view").clientWidth;
            const containerHeight = document.getElementById("matrix-view").clientHeight || 500;
            const width = Math.min(containerWidth - margin.left - margin.right, 800);
            const height = Math.min(containerHeight - margin.top - margin.bottom, 600);
            
            // Calculate cell size
            const cellSize = Math.min(
                width / matrixData.columns.length,
                height / matrixData.rows.length
            );
            
            // Create SVG
            const svg = d3.select("#matrix-view")
                .append("svg")
                .attr("width", cellSize * matrixData.columns.length + margin.left + margin.right)
                .attr("height", cellSize * matrixData.rows.length + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);
            
            // Color scale
            const colorScale = d3.scaleLinear()
                .domain([0, 1])
                .range(["#f8f9fa", "#4285F4"]);
            
            // Create rows
            svg.selectAll(".row")
                .data(matrixData.rows)
                .enter()
                .append("text")
                .attr("class", "row-label")
                .attr("x", -10)
                .attr("y", (d, i) => i * cellSize + cellSize / 2)
                .attr("text-anchor", "end")
                .attr("dominant-baseline", "middle")
                .text(d => d);
            
            // Create columns
            svg.selectAll(".column")
                .data(matrixData.columns)
                .enter()
                .append("text")
                .attr("class", "column-label")
                .attr("x", (d, i) => i * cellSize + cellSize / 2)
                .attr("y", -10)
                .attr("text-anchor", "middle")
                .attr("dominant-baseline", "middle")
                .attr("transform", (d, i) => `rotate(-45, ${i * cellSize + cellSize / 2}, -10)`)
                .text(d => d);
            
            // Create cells
            matrixData.rows.forEach((row, i) => {
                matrixData.columns.forEach((col, j) => {
                    svg.append("rect")
                        .attr("x", j * cellSize)
                        .attr("y", i * cellSize)
                        .attr("width", cellSize)
                        .attr("height", cellSize)
                        .attr("fill", colorScale(matrixData.values[i][j]))
                        .attr("stroke", "#fff")
                        .on("mouseover", function() {
                            d3.select(this).attr("stroke", "#000");
                            svg.append("text")
                                .attr("class", "tooltip")
                                .attr("x", j * cellSize + cellSize / 2)
                                .attr("y", i * cellSize + cellSize / 2)
                                .attr("text-anchor", "middle")
                                .attr("dominant-baseline", "middle")
                                .text(matrixData.values[i][j].toFixed(2));
                        })
                        .on("mouseout", function() {
                            d3.select(this).attr("stroke", "#fff");
                            svg.selectAll(".tooltip").remove();
                        });
                });
            });
            
            // Add title
            svg.append("text")
                .attr("x", (cellSize * matrixData.columns.length) / 2)
                .attr("y", -50)
                .attr("text-anchor", "middle")
                .style("font-size", "18px")
                .style("font-weight", "bold")
                .text(`${matrixType.split("-").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join("-")} Relationship Matrix`);
        }

        // Initialize with default matrix type
        document.addEventListener('DOMContentLoaded', function() {
            createMatrix("property-process");
            
            // Handle matrix type change
            document.getElementById("matrix-type").addEventListener("change", function() {
                createMatrix(this.value);
            });
            
            // Handle window resize
            window.addEventListener("resize", function() {
                const currentType = document.getElementById("matrix-type").value;
                createMatrix(currentType);
            });
        });
    </script>
</body>
</html>""")
        logger.info(f"Created matrix HTML: {path}")
            
    def copy_data_files(self):
        """Copy data files to the assets directory."""
        data_dir = self.portal_output_dir / 'data'
        if not data_dir.exists():
            logger.warning(f"Data directory not found: {data_dir}")
            return
            
        dest_data_dir = self.dist_dir / 'assets' / 'data'
        dest_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all data files
        for item in data_dir.glob('**/*'):
            if item.is_file():
                # Preserve directory structure
                rel_path = item.relative_to(data_dir)
                dest_path = dest_data_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
                logger.info(f"Copied {item} to {dest_path}")
                
    def fix_website(self):
        """Main method to fix the website file structure."""
        logger.info("Starting visualization path fix process...")
        
        # Create the directory structure
        self.create_directory_structure()
        
        # Copy visualizations
        self.copy_portal_visualizations()
        
        # Copy data files
        self.copy_data_files()
        
        logger.info("Website visualization paths fixed successfully!")
        
        return True

def main():
    """Main entry point."""
    try:
        fixer = VisualizationFixer()
        success = fixer.fix_website()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error fixing website: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code) 