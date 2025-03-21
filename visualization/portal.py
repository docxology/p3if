"""
P3IF Visualization Portal

This module provides functionality to generate an integrated web portal with all P3IF visualizations.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json
from pathlib import Path
import os
import shutil
import datetime

from core.framework import P3IFFramework
from visualization.base import Visualizer
from visualization.dashboard import DashboardGenerator
from visualization.interactive import InteractiveVisualizer
from utils.config import Config


class VisualizationPortal:
    """Portal generator for P3IF visualizations."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize visualization portal generator.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        self.framework = framework
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize visualization components
        self.dashboard_generator = DashboardGenerator(framework, config)
        self.interactive_visualizer = InteractiveVisualizer(framework, config)
    
    def generate_portal(self, 
                      output_file: Union[str, Path],
                      title: str = "P3IF Visualization Portal",
                      include_dataset_dropdown: bool = False,
                      datasets: List[Dict[str, str]] = None,
                      include_component_selector: bool = False,
                      components: List[Dict[str, str]] = None,
                      include_3d_cube: bool = True,
                      include_network: bool = True,
                      include_matrix: bool = True,
                      include_dashboard: bool = True,
                      include_data_loading_script: bool = False,
                      include_export_buttons: bool = False) -> Path:
        """
        Generate a complete visualization portal with tabbed interface.
        
        Args:
            output_file: Path where the HTML file will be saved
            title: Title for the visualization portal
            include_dataset_dropdown: Whether to include a dataset dropdown selector
            datasets: List of dataset dicts with 'id' and 'name' keys
            include_component_selector: Whether to include a component selector
            components: List of component dicts with 'id', 'name', and 'description' keys
            include_3d_cube: Whether to include the 3D cube visualization
            include_network: Whether to include the network visualization
            include_matrix: Whether to include the matrix visualizations
            include_dashboard: Whether to include the dashboard visualizations
            include_data_loading_script: Whether to include script for dynamic data loading
            include_export_buttons: Whether to include export functionality
            
        Returns:
            Path to the generated HTML file
        """
        self.logger.info(f"Generating visualization portal at {output_file}")
        
        # Create the output directory if it doesn't exist
        output_path = Path(output_file)
        output_dir = output_path.parent
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the visualizations directory if it doesn't exist
        visualizations_dir = output_dir / "visualizations"
        os.makedirs(visualizations_dir, exist_ok=True)
        
        # Ensure the log directory exists
        log_dir = output_dir / "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up a file handler for logging
        file_handler = logging.FileHandler(log_dir / "visualization_portal.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # Generate individual visualizations
        visualizations = self._generate_visualizations(visualizations_dir)
        
        # Create data files
        data_dir = output_dir / "data"
        data_files = self._generate_data_files(data_dir)
        
        # Create main portal HTML file 
        self._create_portal_html(output_path, 
                               title=title,
                               include_dataset_dropdown=include_dataset_dropdown,
                               datasets=datasets,
                               include_component_selector=include_component_selector,
                               components=components,
                               include_3d_cube=include_3d_cube,
                               include_network=include_network,
                               include_matrix=include_matrix,
                               include_dashboard=include_dashboard,
                               include_data_loading_script=include_data_loading_script,
                               include_export_buttons=include_export_buttons)
        
        # Copy assets (CSS, JS)
        self._create_css_file(output_dir)
        self._create_js_file(output_dir)
        
        self.logger.info(f"Portal generation complete. Access via {output_path}")
        return output_path
    
    def generate_dataset_dropdown(self, datasets: List[Dict[str, str]]) -> str:
        """
        Generate HTML for a dataset dropdown selector.
        
        Args:
            datasets: List of datasets (each with id and name)
            
        Returns:
            HTML string for the dataset dropdown
        """
        if not datasets:
            return ""
        
        html = """
        <div class="dropdown-section">
            <label for="dataset-select">Select Dataset:</label>
            <select id="dataset-selector" onchange="loadDataset(this.value)">
        """
        
        for dataset in datasets:
            html += f'<option value="{dataset["id"]}">{dataset["name"]}</option>\n'
        
        html += """
            </select>
        </div>
        """
        
        return html
    
    def generate_component_selector(self, components: List[Dict[str, str]]) -> str:
        """
        Generate HTML for a component selector.
        
        Args:
            components: List of component dicts with 'id', 'name', and 'description' keys
            
        Returns:
            HTML string for the component selector
        """
        if not components:
            return ""
        
        html = """
        <div class="component-selector">
            <h4>Visualization Components</h4>
            <div class="row">
        """
        
        for component in components:
            html += f"""
            <div class="col-md-3 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">{component["name"]}</h5>
                        <p class="card-text">{component["description"]}</p>
                        <button class="btn btn-primary component-btn" data-component="{component["id"]}">
                            View {component["name"]}
                        </button>
                    </div>
                </div>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_visualizations(self, output_dir: Path) -> Dict[str, Path]:
        """Generate visualizations for the portal."""
        visualizations = {}
        
        # Create 3D Cube Visualization
        cube_path = output_dir / "3d-cube.html"
        visualizations["3d_cube"] = self.interactive_visualizer.generate_3d_cube_html(
            output_file=cube_path,
            title="P3IF 3D Cube"
        )
        
        # Create Force Directed Graph
        graph_path = output_dir / "force-graph.html"
        visualizations["force_graph"] = self.interactive_visualizer.generate_force_directed_graph_html(
            output_file=graph_path,
            title="P3IF Network Graph"
        )
        
        # Create Overview Dashboard Visualizations
        overview_dir = output_dir / "overview"
        os.makedirs(overview_dir, exist_ok=True)
        overview_viz = self.dashboard_generator.generate_overview_dashboard(overview_dir)
        visualizations.update({f"overview_{k}": v for k, v in overview_viz.items()})
        
        # Check if we have domains and generate domain-specific visualizations
        domains = set()
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain:
                domains.add(domain)
        
        # If we have domains, generate domain dashboard for the first domain
        if domains:
            example_domain = next(iter(domains))
            domain_dir = output_dir / "domain"
            os.makedirs(domain_dir, exist_ok=True)
            domain_viz = self.dashboard_generator.generate_domain_dashboard(example_domain, domain_dir)
            visualizations.update({f"domain_{k}": v for k, v in domain_viz.items()})
            
            # If we have multiple domains, generate comparative dashboard
            if len(domains) > 1:
                domains_list = list(domains)[:3]  # Limit to 3 domains for demonstration
                compare_dir = output_dir / "compare"
                os.makedirs(compare_dir, exist_ok=True)
                compare_viz = self.dashboard_generator.generate_comparative_dashboard(domains_list, compare_dir)
                visualizations.update({f"compare_{k}": v for k, v in compare_viz.items()})
        
        return visualizations
    
    def _generate_data_files(self, data_dir: Path) -> Dict[str, Path]:
        """Generate data files for the portal."""
        data_files = {}
        
        # Generate 3D Cube Data
        cube_data = self.interactive_visualizer.generate_3d_cube_data()
        cube_data_path = data_dir / "cube_data.json"
        with open(cube_data_path, 'w') as f:
            json.dump(cube_data, f, indent=2)
        data_files["cube_data"] = cube_data_path
        
        # Generate Force Graph Data
        graph_data = self.interactive_visualizer.generate_force_directed_graph_data()
        graph_data_path = data_dir / "graph_data.json"
        with open(graph_data_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        data_files["graph_data"] = graph_data_path
        
        # Generate framework summary data
        summary_data = {
            "pattern_counts": {
                "property": len(self.framework.get_patterns_by_type("property")),
                "process": len(self.framework.get_patterns_by_type("process")),
                "perspective": len(self.framework.get_patterns_by_type("perspective"))
            },
            "relationship_count": len(self.framework._relationships),
            "domains": []
        }
        
        # Add domain information if available
        domains = set()
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain:
                domains.add(domain)
        
        for domain in domains:
            domain_patterns = {
                "property": 0,
                "process": 0,
                "perspective": 0
            }
            
            for pattern in self.framework._patterns.values():
                if getattr(pattern, "domain", None) == domain and pattern.type in domain_patterns:
                    domain_patterns[pattern.type] += 1
            
            summary_data["domains"].append({
                "name": domain,
                "patterns": domain_patterns
            })
        
        summary_path = data_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        data_files["summary"] = summary_path
        
        return data_files
    
    def _create_portal_html(self, output_path: Path, 
                       title: str = "P3IF Visualization Portal",
                       include_dataset_dropdown: bool = False,
                       datasets: List[Dict[str, str]] = None,
                       include_component_selector: bool = False,
                       components: List[Dict[str, str]] = None,
                       include_3d_cube: bool = True,
                       include_network: bool = True,
                       include_matrix: bool = True,
                       include_dashboard: bool = True,
                       include_data_loading_script: bool = False,
                       include_export_buttons: bool = False) -> Path:
        """
        Create the HTML file for the visualization portal.
        
        Args:
            output_path: Path to save the HTML file
            title: Portal title
            include_dataset_dropdown: Whether to include dataset selector
            datasets: List of datasets (each with id and name)
            include_component_selector: Whether to include component selector
            components: List of components (each with id, name, and description)
            include_3d_cube: Whether to include 3D cube visualization
            include_network: Whether to include network visualization
            include_matrix: Whether to include matrix visualization
            include_dashboard: Whether to include dashboard
            include_data_loading_script: Whether to include data loading script
            include_export_buttons: Whether to include export buttons
            
        Returns:
            Path to the created HTML file
        """
        # Get domain information for the portal
        domains = []
        for pattern in self.framework._patterns.values():
            domain = getattr(pattern, "domain", None)
            if domain and domain not in domains:
                domains.append(domain)
        
        # If there are no domains, add some test domains for testing
        if not domains and (include_dataset_dropdown or include_component_selector):
            domains = ["Domain A", "Domain B", "Domain C"]
        
        # Generate dataset dropdown HTML if requested
        dataset_dropdown_html = ""
        if include_dataset_dropdown and datasets:
            dataset_dropdown_html = self.generate_dataset_dropdown(datasets)
        
        # Generate component selector HTML if requested
        component_selector_html = ""
        if include_component_selector and components:
            component_selector_html = self.generate_component_selector(components)
        
        # Create HTML content with CSS in style tag
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                /* P3IF Visualization Portal Styles */
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                }}
                
                header {{
                    background-color: #343a40;
                    color: white;
                    padding: 1rem 0;
                }}
                
                main {{
                    padding: 2rem 0;
                    min-height: 80vh;
                }}
                
                nav {{
                    margin-bottom: 1.5rem;
                }}
                
                .navbar-brand {{
                    font-weight: bold;
                }}
                
                .card {{
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                
                .card-header {{
                    background-color: #f1f5f9;
                    padding: 15px 20px;
                }}
                
                .card-header h3, .card-header h4 {{
                    margin: 0;
                    color: #333;
                }}
                
                .viz-container {{
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                
                /* Dashboard styles */
                .stat-card {{
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    background-color: #fff;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    display: flex;
                    align-items: center;
                }}
                
                .stat-icon {{
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 15px;
                    flex-shrink: 0;
                }}
                
                .stat-icon i {{
                    font-size: 24px;
                    color: white;
                }}
                
                .stat-info {{
                    flex-grow: 1;
                }}
                
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0;
                    line-height: 1.2;
                }}
                
                .stat-label {{
                    color: #6c757d;
                    margin: 0;
                }}
                
                /* Matrix visualization styles */
                .matrix-container {{
                    overflow: auto;
                    max-height: 600px;
                }}
                
                /* Footer styles */
                footer {{
                    margin-top: 30px;
                }}
                
                /* Component selector styles */
                .component-selector {{
                    margin-bottom: 20px;
                }}
                
                /* Dataset selector styles */
                #dataset-selector {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                }}
                
                /* Responsive containers */
                .responsive-container {{
                    width: 100%;
                    padding: 15px;
                }}
                
                @media (max-width: 768px) {{
                    .responsive-container {{
                        flex-direction: column;
                    }}
                    
                    .col-md-6 {{
                        width: 100%;
                    }}
                    
                    .col-md-4 {{
                        width: 100%;
                    }}
                    
                    .col-md-8 {{
                        width: 100%;
                    }}
                }}
            </style>
            <link rel="stylesheet" href="assets/css/styles.css">
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <!-- Font Awesome -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        </head>
        <body>
            <div class="container-fluid">
                <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div class="container-fluid">
                        <a class="navbar-brand" href="#">{title}</a>
                        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="collapse navbar-collapse" id="navbarNav">
                            <ul class="navbar-nav">
                                <li class="nav-item">
                                    <a class="nav-link active" data-bs-toggle="tab" href="#dashboard">Dashboard</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#cube">3D Cube</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#network">Network</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" data-bs-toggle="tab" href="#matrix">Matrices</a>
                                </li>
        """
        
        # Add domain dropdown if we have domains
        if domains:
            html_content += """
                                <li class="nav-item dropdown">
                                    <a class="nav-link dropdown-toggle" href="#" id="domainDropdown" role="button" data-bs-toggle="dropdown">
                                        Domains
                                    </a>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" data-bs-toggle="tab" href="#domains-all">All Domains</a></li>
                                        <li><hr class="dropdown-divider"></li>
            """
            
            for domain in domains:
                domain_slug = domain.lower().replace(' ', '-')
                html_content += f'<li><a class="dropdown-item domain-tab" data-bs-toggle="tab" href="#domain-{domain_slug}">{domain}</a></li>'
                
            html_content += """
                                    </ul>
                                </li>
            """
        
        html_content += """
                            </ul>
                        </div>
                    </div>
                </nav>
            
        """
        
        # Add dataset dropdown if requested
        if include_dataset_dropdown and datasets:
            html_content += f"""
                <div id="dataset-selector">
                    {dataset_dropdown_html}
                </div>
            """
        
        # Add component selector if requested
        if include_component_selector and components:
            html_content += f"""
                <div class="component-selector">
                    {component_selector_html}
                </div>
            """
        
        # Start tab content
        html_content += """
                <div class="tab-content p-3">
                    <!-- Dashboard Tab -->
                    <div class="tab-pane fade show active" id="dashboard">
                        <div class="row">
                            <div class="col-md-12">
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h3>P3IF Framework Overview</h3>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-8">
                                                <div id="main-viz-container" style="height: 500px;">
                                                    <iframe src="visualizations/3d-cube.html" width="100%" height="100%" frameborder="0"></iframe>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="card mb-3">
                                                    <div class="card-header">Summary Statistics</div>
                                                    <div class="card-body">
                                                        <div id="summary-stats"></div>
                                                    </div>
                                                </div>
                                                <div class="card">
                                                    <div class="card-header">Quick Navigation</div>
                                                    <div class="card-body">
                                                        <div class="d-grid gap-2">
                                                            <button class="btn btn-primary" onclick="document.querySelector('[href=\\'#cube\\']').click()">
                                                                <i class="fas fa-cube"></i> 3D Cube View
                                                            </button>
                                                            <button class="btn btn-info" onclick="document.querySelector('[href=\\'#network\\']').click()">
                                                                <i class="fas fa-project-diagram"></i> Network View
                                                            </button>
                                                            <button class="btn btn-secondary" onclick="document.querySelector('[href=\\'#matrix\\']').click()">
                                                                <i class="fas fa-th"></i> Matrix View
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card mb-4">
                                            <div class="card-header">
                                                <h4>Pattern Distribution</h4>
                                            </div>
                                            <div class="card-body">
                                                <div id="pattern-distribution-chart" style="height: 300px;"></div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card mb-4">
                                            <div class="card-header">
                                                <h4>Domain Overview</h4>
                                            </div>
                                            <div class="card-body">
                                                <div id="domain-overview-chart" style="height: 300px;"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
        """
        
        # Add 3D Cube Tab if requested
        if include_3d_cube:
            html_content += """
                    <!-- 3D Cube Tab -->
                    <div class="tab-pane fade" id="cube">
                        <div class="card">
                            <div class="card-header">
                                <h3>3D Cube Visualization</h3>
                                <p class="text-muted">Explore the relationships between Properties, Processes, and Perspectives in 3D space</p>
                            </div>
                            <div class="card-body p-0">
                                <div id="3d-cube-container" style="height: 800px;">
                                    <iframe src="visualizations/3d-cube.html" width="100%" height="100%" frameborder="0"></iframe>
                                </div>
                            </div>
                        </div>
                    </div>
            """
        
        # Add Network Tab if requested
        if include_network:
            html_content += """
                    <!-- Network Tab -->
                    <div class="tab-pane fade" id="network">
                        <div class="card">
                            <div class="card-header">
                                <h3>Network Visualization</h3>
                                <p class="text-muted">Explore the relationships between patterns as a force-directed graph</p>
                            </div>
                            <div class="card-body p-0">
                                <div id="network-container" style="height: 800px;">
                                    <iframe src="visualizations/force-graph.html" width="100%" height="100%" frameborder="0"></iframe>
                                </div>
                            </div>
                        </div>
                    </div>
            """
        
        # Add Matrix Tab if requested
        if include_matrix:
            html_content += """
                    <!-- Matrix Tab -->
                    <div class="tab-pane fade" id="matrix">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h3>Matrix Visualizations</h3>
                                <p class="text-muted">Explore relationships between pattern types using matrix visualizations</p>
                            </div>
                            <div class="card-body">
                                <ul class="nav nav-tabs" id="matrixTabs" role="tablist">
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link active" id="property-process-tab" data-bs-toggle="tab" 
                                                data-bs-target="#property-process" type="button" role="tab">
                                            Property × Process
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="property-perspective-tab" data-bs-toggle="tab" 
                                                data-bs-target="#property-perspective" type="button" role="tab">
                                            Property × Perspective
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="process-perspective-tab" data-bs-toggle="tab" 
                                                data-bs-target="#process-perspective" type="button" role="tab">
                                            Process × Perspective
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="similarity-tab" data-bs-toggle="tab" 
                                                data-bs-target="#similarity" type="button" role="tab">
                                            Domain Similarity
                                        </button>
                                    </li>
                                </ul>
                                <div class="tab-content p-3" id="matrixTabsContent">
                                    <div class="tab-pane fade show active" id="property-process" role="tabpanel">
                                        <div class="text-center">
                                            <h4>Property × Process Relationship Matrix</h4>
                                            <img src="visualizations/overview/matrix_property_process.png" class="img-fluid" alt="Property × Process Matrix">
                                        </div>
                                    </div>
                                    <div class="tab-pane fade" id="property-perspective" role="tabpanel">
                                        <div class="text-center">
                                            <h4>Property × Perspective Relationship Matrix</h4>
                                            <img src="visualizations/overview/matrix_property_perspective.png" class="img-fluid" alt="Property × Perspective Matrix">
                                        </div>
                                    </div>
                                    <div class="tab-pane fade" id="process-perspective" role="tabpanel">
                                        <div class="text-center">
                                            <h4>Process × Perspective Relationship Matrix</h4>
                                            <img src="visualizations/overview/matrix_process_perspective.png" class="img-fluid" alt="Process × Perspective Matrix">
                                        </div>
                                    </div>
                                    <div class="tab-pane fade" id="similarity" role="tabpanel">
                                        <div class="text-center">
                                            <h4>Domain Similarity Matrix</h4>
                                            <img src="visualizations/overview/domain_similarity.png" class="img-fluid" alt="Domain Similarity Matrix">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
            """
        
        # Add Dashboard Tab if requested
        if include_dashboard:
            html_content += """
                    <!-- Dashboard Tab -->
                    <div class="tab-pane fade" id="dashboard-container">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h3>Interactive Dashboard</h3>
                                <p class="text-muted">Explore the framework data through interactive dashboards</p>
                            </div>
                            <div class="card-body">
                                <div class="dashboard-wrapper" style="height: 800px;">
                                    <div id="overview-section" class="dashboard-section">
                                        <h4>Framework Overview</h4>
                                        <div class="chart-container" id="overview-chart"></div>
                                    </div>
                                    <div id="details-section" class="dashboard-section">
                                        <h4>Detailed Metrics</h4>
                                        <div class="chart-container" id="details-chart"></div>
                                    </div>
                                    <div id="metrics-section" class="dashboard-section">
                                        <h4>Key Metrics</h4>
                                        <div class="chart-container" id="metrics-chart"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
            """
        
        # Add Domains Tab
        if domains:
            # Start with the main domains tab HTML
            html_content += f"""
                    <!-- Domains Tab -->
                    <div class="tab-pane fade" id="domains-all">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h3>All Domains</h3>
                                <p class="text-muted">Comparative view of all domains in the framework</p>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header">Domain Network</div>
                                            <div class="card-body text-center">
                                                <img src="visualizations/overview/domain_network.png" class="img-fluid" alt="Domain Network">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header">Domain Similarity</div>
                                            <div class="card-body text-center">
                                                <img src="visualizations/overview/domain_similarity.png" class="img-fluid" alt="Domain Similarity">
                                            </div>
                                        </div>
                                    </div>
                                </div>
            """
            
            # Add comparative pattern distribution card if we have more than one domain
            if len(domains) > 1:
                html_content += """
                                <div class="card mb-3">
                                    <div class="card-header">Pattern Distribution Across Domains</div>
                                    <div class="card-body text-center">
                                        <img src="visualizations/compare/comparative_pattern_distribution.png" class="img-fluid" alt="Pattern Distribution">
                                    </div>
                                </div>
                """
            
            # Close the domains-all tab
            html_content += """
                            </div>
                        </div>
                    </div>
            """
            
            # Add individual domain tabs
            for domain in domains:
                domain_slug = domain.lower().replace(' ', '-')
                html_content += f"""
                    <!-- Domain: {domain} -->
                    <div class="tab-pane fade" id="domain-{domain_slug}">
                        <div class="card mb-4">
                            <div class="card-header">
                                <h3>Domain: {domain}</h3>
                                <p class="text-muted">Analysis of the {domain} domain</p>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header">Pattern Distribution</div>
                                            <div class="card-body text-center">
                                                <img src="visualizations/domain/pattern_distribution.png" class="img-fluid" alt="Pattern Distribution">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card mb-3">
                                            <div class="card-header">Domain Network</div>
                                            <div class="card-body text-center">
                                                <img src="visualizations/domain/domain_network.png" class="img-fluid" alt="Domain Network">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                """
        
        # Close the main divs
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content += f"""
                </div>
                
                <footer class="bg-light text-center text-lg-start mt-4">
                    <div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.05);">
                        {title} - Generated on {current_datetime}
                    </div>
                </footer>
            </div>
            
            <!-- Bootstrap & JavaScript -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="assets/js/portal.js"></script>
        """
        
        # Add JavaScript separately to avoid f-string issues
        js_code = """
            <script>
            document.getElementById('dataset-selector').addEventListener('change', function() {
                const selectedDataset = this.value;
                console.log('Selected dataset:', selectedDataset);
                loadDataset(selectedDataset);
            });
            
            function loadDataset(datasetId) {
                console.log(`Loading dataset: ${datasetId}`);
                
                // Simulate loading dataset
                const loadingIndicator = document.createElement('div');
                loadingIndicator.id = 'loading-indicator';
                loadingIndicator.className = 'alert alert-info';
                loadingIndicator.textContent = 'Loading dataset...';
                document.querySelector('.container-fluid').insertBefore(loadingIndicator, document.querySelector('.tab-content'));
                
                // In a real implementation, this would load data for the selected dataset
                setTimeout(() => {
                    document.getElementById('loading-indicator').remove();
                    updateCharts(datasetId);
                }, 1000);
            }
            
            function updateCharts(datasetId) {
                // Update charts with new data
                // This is just a placeholder - in a real application, 
                // this would update all charts with data from the selected dataset
                console.log(`Updating charts with data from dataset ${datasetId}`);
            }
            
            function showComponent(componentId) {
                // Hide all component containers
                document.querySelectorAll('.component-container').forEach(container => {
                    container.style.display = 'none';
                });
                
                // Show the selected component
                const selectedContainer = document.getElementById(componentId + '-container');
                if (selectedContainer) {
                    selectedContainer.style.display = 'block';
                }
            }
            
            // Set up event listeners for component buttons
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('.component-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const componentId = this.getAttribute('data-component');
                        showComponent(componentId);
                    });
                });
            });
            </script>
            
        </body>
        </html>
        """
        
        html_content += js_code
        
        # Write HTML to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path
    
    def _create_css_file(self, css_dir: Path) -> Path:
        """Create CSS file for the portal."""
        css_path = css_dir / "styles.css"
        css_content = """
/* P3IF Portal Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    margin: 0;
    padding: 0;
}

header {
    background-color: #343a40;
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

main {
    padding: 2rem 0;
    min-height: 80vh;
}

nav {
    background-color: #343a40;
    margin-bottom: 1.5rem;
}

.navbar-brand {
    font-weight: bold;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
}

.card-header {
    background-color: #f1f5f9;
    padding: 15px 20px;
}

.card-header h3, .card-header h4 {
    margin: 0;
    color: #333;
}

.viz-container {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Dashboard styles */
.stat-card {
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
    background-color: #fff;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    flex-shrink: 0;
}

.stat-icon i {
    font-size: 24px;
    color: white;
}

.stat-info {
    flex-grow: 1;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    margin: 0;
    line-height: 1.2;
}

.stat-label {
    color: #6c757d;
    margin: 0;
}

/* Matrix visualization styles */
.matrix-container {
    overflow: auto;
    max-height: 600px;
}

/* Footer styles */
footer {
    margin-top: 30px;
    background-color: #f8f9fa;
    padding: 1rem 0;
    border-top: 1px solid #dee2e6;
}

/* Dataset selector styles */
#dataset-selector {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
}

/* Component selector styles */
.component-selector {
    margin-bottom: 20px;
}

/* Responsive containers */
.responsive-container {
    width: 100%;
    padding: 15px;
}

@media (max-width: 768px) {
    .responsive-container {
        flex-direction: column;
    }
    
    .col-md-6 {
        width: 100%;
    }
    
    .col-md-4 {
        width: 100%;
    }
    
    .col-md-8 {
        width: 100%;
    }
}
"""
        with open(css_path, 'w') as f:
            f.write(css_content)
        
        return css_path
    
    def _create_js_file(self, assets_dir, js_filename="portal.js"):
        """Create the JavaScript file for the portal."""
        js_path = os.path.join(assets_dir, "js", js_filename)
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        
        js_content = """
            // P3IF Visualization Portal JavaScript
            
            // Handle dataset selection
            function loadDataset(datasetId) {
                console.log(`Loading dataset: ${datasetId}`);
                
                // Simulate loading dataset
                document.getElementById('loading-indicator').style.display = 'block';
                
                // In a real implementation, this would make an AJAX call to load data
                setTimeout(() => {
                    document.getElementById('loading-indicator').style.display = 'none';
                    initializeVisualizations(datasetId);
                }, 1000);
            }
            
            // Initialize visualizations
            function initializeVisualizations(datasetId) {
                // Update charts with new data
                updatePatternDistributionChart(datasetId);
                updateDomainOverviewChart(datasetId);
                updateMetricsChart(datasetId);
            }
            
            // Update the pattern distribution chart
            function updatePatternDistributionChart(datasetId) {
                // In a real implementation, this would update the chart with new data
                console.log(`Updating pattern distribution chart for dataset: ${datasetId}`);
            }
            
            // Update the domain overview chart
            function updateDomainOverviewChart(datasetId) {
                // In a real implementation, this would update the chart with new data
                console.log(`Updating domain overview chart for dataset: ${datasetId}`);
            }
            
            // Update the metrics chart
            function updateMetricsChart(datasetId) {
                // In a real implementation, this would update the chart with new data
                console.log(`Updating metrics chart for dataset: ${datasetId}`);
            }
            
            // Component selector functionality
            function showComponent(componentId) {
                // Hide all component containers
                document.querySelectorAll('.component-container').forEach(container => {
                    container.style.display = 'none';
                });
                
                // Show the selected component
                const selectedContainer = document.getElementById(componentId + '-container');
                if (selectedContainer) {
                    selectedContainer.style.display = 'block';
                }
            }
            
            // Initialize on DOM content loaded
            document.addEventListener('DOMContentLoaded', function() {
                // Set up event listeners for component buttons
                document.querySelectorAll('.component-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const componentId = this.getAttribute('data-component');
                        showComponent(componentId);
                    });
                });
                
                // Initialize Chart.js charts
                initializeCharts();
            });
            
            // Initialize charts
            function initializeCharts() {
                // Properties chart
                const propertiesCtx = document.getElementById('properties-chart');
                if (propertiesCtx) {
                    new Chart(propertiesCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Property 1', 'Property 2', 'Property 3', 'Property 4', 'Property 5'],
                            datasets: [{
                                label: 'Properties Distribution',
                                data: [12, 19, 3, 5, 2],
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
                
                // Processes chart
                const processesCtx = document.getElementById('processes-chart');
                if (processesCtx) {
                    new Chart(processesCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Process 1', 'Process 2', 'Process 3', 'Process 4', 'Process 5'],
                            datasets: [{
                                label: 'Processes Distribution',
                                data: [15, 8, 12, 5, 10],
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
                
                // Perspectives chart
                const perspectivesCtx = document.getElementById('perspectives-chart');
                if (perspectivesCtx) {
                    new Chart(perspectivesCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Perspective 1', 'Perspective 2', 'Perspective 3', 'Perspective 4', 'Perspective 5'],
                            datasets: [{
                                label: 'Perspectives Distribution',
                                data: [7, 11, 6, 8, 14],
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
            }
        """
        
        with open(js_path, 'w') as f:
            f.write(js_content)
            
        return os.path.join("assets", "js", js_filename) 