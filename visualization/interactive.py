"""
P3IF Interactive Visualizations

This module provides interactive visualization capabilities for P3IF data,
including 3D visualizations and web-based interactive elements.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json
from pathlib import Path
import os
import numpy as np

from core.framework import P3IFFramework
from visualization.base import Visualizer
from utils.config import Config


class InteractiveVisualizer(Visualizer):
    """Interactive visualizer for P3IF data."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize interactive visualizer.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        super().__init__(framework, config)
    
    def generate_3d_cube_data(self) -> Dict[str, Any]:
        """
        Generate data for a 3D interactive cube visualization.
        
        The cube represents the three dimensions of P3IF:
        - Properties (X-axis)
        - Processes (Y-axis)
        - Perspectives (Z-axis)
        
        Returns:
            Dictionary containing data for 3D cube visualization
        """
        # Get all patterns
        properties = self.framework.get_patterns_by_type("property")
        processes = self.framework.get_patterns_by_type("process")
        perspectives = self.framework.get_patterns_by_type("perspective")
        
        # Create mappings from pattern IDs to indices
        property_map = {p.id: i for i, p in enumerate(properties)}
        process_map = {p.id: i for i, p in enumerate(processes)}
        perspective_map = {p.id: i for i, p in enumerate(perspectives)}
        
        # Prepare data structure for cube
        cube_data = {
            "dimensions": {
                "property": [{"id": p.id, "name": p.name, "domain": getattr(p, "domain", None)} for p in properties],
                "process": [{"id": p.id, "name": p.name, "domain": getattr(p, "domain", None)} for p in processes],
                "perspective": [{"id": p.id, "name": p.name, "domain": getattr(p, "domain", None)} for p in perspectives]
            },
            "connections": []
        }
        
        # Add relationship data
        for rel in self.framework._relationships.values():
            # Only include relationships that connect all three dimensions
            if rel.property_id and rel.process_id and rel.perspective_id:
                # Check if they exist in our mappings
                if (rel.property_id in property_map and 
                    rel.process_id in process_map and 
                    rel.perspective_id in perspective_map):
                    
                    connection = {
                        "id": rel.id,
                        "property_id": rel.property_id,
                        "process_id": rel.process_id,
                        "perspective_id": rel.perspective_id,
                        "strength": rel.strength,
                        "confidence": rel.confidence,
                        "x": property_map[rel.property_id],
                        "y": process_map[rel.process_id],
                        "z": perspective_map[rel.perspective_id]
                    }
                    cube_data["connections"].append(connection)
        
        return cube_data
    
    def generate_3d_cube_html(self, output_file: Union[str, Path], 
                             cube_data: Optional[Dict[str, Any]] = None,
                             title: str = "P3IF 3D Cube Visualization",
                             include_dataset_selector: bool = False,
                             datasets: Optional[List[Dict[str, str]]] = None) -> Path:
        """
        Generate an HTML file with an interactive 3D cube visualization.
        
        Args:
            output_file: Path to save the HTML file
            cube_data: Optional pre-generated cube data (if None, will generate)
            title: Title for the visualization
            include_dataset_selector: Whether to include a dataset selector dropdown
            datasets: List of dataset information with 'id' and 'name' keys
            
        Returns:
            Path to the generated HTML file
        """
        if cube_data is None:
            cube_data = self.generate_3d_cube_data()
        
        output_path = Path(output_file)
        os.makedirs(output_path.parent, exist_ok=True)
        
        # Convert the data to JSON for embedding in JavaScript
        data_json = json.dumps(cube_data)
        
        # Prepare dataset selector HTML if needed
        dataset_selector_html = ""
        dataset_selector_js = ""
        
        if include_dataset_selector and datasets:
            # Create dataset dropdown HTML
            dataset_options = ""
            for dataset in datasets:
                dataset_options += f'<option value="{dataset["id"]}">{dataset["name"]}</option>\n'
            
            dataset_selector_html = f"""
            <div class="dataset-selector-container">
                <label for="dataset-selector">Select Dataset:</label>
                <select id="dataset-selector" class="form-control">
                    {dataset_options}
                </select>
            </div>
            """
            
            # Create dataset loading JavaScript
            dataset_selector_js = """
            // Dataset selection handling
            function loadDataset(datasetId) {
                // In a real implementation, this would fetch data for the selected dataset
                console.log('Loading dataset: ' + datasetId);
                
                // Simulate data loading with a timeout
                setTimeout(function() {
                    // For demonstration, we're just using the same data
                    // In a real implementation, this would update the visualization with new data
                    console.log('Dataset loaded');
                }, 500);
            }
            
            // Add event listener to dataset selector
            document.addEventListener('DOMContentLoaded', function() {
                const selector = document.getElementById('dataset-selector');
                if (selector) {
                    selector.addEventListener('change', function() {
                        loadDataset(this.value);
                    });
                    
                    // Load initial dataset
                    if (selector.value) {
                        loadDataset(selector.value);
                    }
                }
            });
            """
        
        # Generate the HTML with embedded Three.js visualization
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0;
                    overflow: hidden;
                    font-family: Arial, sans-serif;
                }}
                #info {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    max-width: 300px;
                    z-index: 100;
                }}
                #canvas-container {{
                    width: 100%;
                    height: 100vh;
                }}
                #legend {{
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    background: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    z-index: 100;
                }}
                .axis-label {{
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .property-color {{ color: #1f77b4; }}
                .process-color {{ color: #ff7f0e; }}
                .perspective-color {{ color: #2ca02c; }}
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
        </head>
        <body>
            <div id="info">
                <h2>{title}</h2>
                <p>This visualization represents the P3IF framework as a 3D cube with three dimensions:</p>
                <p><span class="property-color">X-axis: Properties</span></p>
                <p><span class="process-color">Y-axis: Processes</span></p>
                <p><span class="perspective-color">Z-axis: Perspectives</span></p>
                <p>Each point in the cube represents a relationship between specific property, process, and perspective.</p>
                <p>Click and drag to rotate. Scroll to zoom. Right-click and drag to pan.</p>
                <div id="selection-info"></div>
            </div>
            
            <div id="canvas-container"></div>
            
            <div id="legend">
                <div class="axis-label property-color">X-axis: Properties</div>
                <div class="axis-label process-color">Y-axis: Processes</div>
                <div class="axis-label perspective-color">Z-axis: Perspectives</div>
                <div>Point size indicates relationship strength</div>
            </div>
            
            {dataset_selector_html}
            
            <script>
                // P3IF data
                const p3ifData = {data_json};
                
                // Setup
                const container = document.getElementById('canvas-container');
                const width = container.clientWidth;
                const height = container.clientHeight;
                
                // Scene
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0xf0f0f0);
                
                // Camera
                const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
                camera.position.set(2, 2, 2);
                
                // Renderer
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(width, height);
                container.appendChild(renderer.domElement);
                
                // Controls
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.25;
                
                // Lighting
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);
                
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
                directionalLight.position.set(1, 1, 1);
                scene.add(directionalLight);
                
                // Axes helper
                const axesHelper = new THREE.AxesHelper(1);
                scene.add(axesHelper);
                
                // Create cube frame
                const cubeSize = 1;
                const cubeGeometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
                const edgesMaterial = new THREE.LineBasicMaterial({{ color: 0x000000, transparent: true, opacity: 0.2 }});
                const cubeEdges = new THREE.LineSegments(
                    new THREE.EdgesGeometry(cubeGeometry),
                    edgesMaterial
                );
                scene.add(cubeEdges);
                
                // Axis labels
                const createTextSprite = (text, color, position) => {{
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.width = 256;
                    canvas.height = 128;
                    
                    context.font = "Bold 36px Arial";
                    context.fillStyle = "rgba(255, 255, 255, 0.95)";
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    
                    context.fillStyle = color;
                    context.fillText(text, 10, 64);
                    
                    const texture = new THREE.Texture(canvas);
                    texture.needsUpdate = true;
                    
                    const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
                    const sprite = new THREE.Sprite(spriteMaterial);
                    sprite.position.copy(position);
                    sprite.scale.set(0.2, 0.1, 1);
                    
                    return sprite;
                }};
                
                // Add axis labels
                scene.add(createTextSprite("Properties (X)", "#1f77b4", new THREE.Vector3(1.2, 0, 0)));
                scene.add(createTextSprite("Processes (Y)", "#ff7f0e", new THREE.Vector3(0, 1.2, 0)));
                scene.add(createTextSprite("Perspectives (Z)", "#2ca02c", new THREE.Vector3(0, 0, 1.2)));
                
                // Add points for relationships
                const pointsMaterial = new THREE.PointsMaterial({{
                    size: 0.05,
                    vertexColors: true,
                    sizeAttenuation: true
                }});
                
                const pointsGeometry = new THREE.BufferGeometry();
                const positions = [];
                const colors = [];
                const pointData = [];
                
                // Normalize positions
                const numProperties = p3ifData.dimensions.property.length;
                const numProcesses = p3ifData.dimensions.process.length;
                const numPerspectives = p3ifData.dimensions.perspective.length;
                
                p3ifData.connections.forEach(conn => {{
                    // Normalize to 0-1 range and then scale to cube size
                    const x = (conn.x / Math.max(1, numProperties - 1)) * cubeSize;
                    const y = (conn.y / Math.max(1, numProcesses - 1)) * cubeSize;
                    const z = (conn.z / Math.max(1, numPerspectives - 1)) * cubeSize;
                    
                    // Center the cube by subtracting half the size
                    positions.push(x - cubeSize/2, y - cubeSize/2, z - cubeSize/2);
                    
                    // Use strength to determine color intensity
                    const r = 0.5 + conn.strength * 0.5;
                    const g = 0.5 * (1 - conn.strength);
                    const b = 0.5 + conn.confidence * 0.5;
                    
                    colors.push(r, g, b);
                    
                    // Store the original data for interaction
                    pointData.push({{
                        id: conn.id,
                        property: p3ifData.dimensions.property[conn.x],
                        process: p3ifData.dimensions.process[conn.y],
                        perspective: p3ifData.dimensions.perspective[conn.z],
                        strength: conn.strength,
                        confidence: conn.confidence
                    }});
                }});
                
                pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                pointsGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
                
                const points = new THREE.Points(pointsGeometry, pointsMaterial);
                scene.add(points);
                
                // Handle resizing
                window.addEventListener('resize', () => {{
                    const newWidth = container.clientWidth;
                    const newHeight = container.clientHeight;
                    
                    camera.aspect = newWidth / newHeight;
                    camera.updateProjectionMatrix();
                    
                    renderer.setSize(newWidth, newHeight);
                }});
                
                // Handle point selection
                const raycaster = new THREE.Raycaster();
                raycaster.params.Points.threshold = 0.05;
                
                const mouse = new THREE.Vector2();
                
                container.addEventListener('mousemove', (event) => {{
                    // Calculate mouse position in normalized device coordinates
                    mouse.x = (event.clientX / width) * 2 - 1;
                    mouse.y = -(event.clientY / height) * 2 + 1;
                }});
                
                container.addEventListener('click', () => {{
                    // Cast a ray from the camera
                    raycaster.setFromCamera(mouse, camera);
                    
                    // Check for intersections with points
                    const intersects = raycaster.intersectObject(points);
                    
                    if (intersects.length > 0) {{
                        const index = intersects[0].index;
                        const selectedPoint = pointData[index];
                        
                        // Display information about the selected point
                        const infoDiv = document.getElementById('selection-info');
                        infoDiv.innerHTML = `
                            <h3>Selected Relationship</h3>
                            <p><strong>Property:</strong> ${{selectedPoint.property.name}}</p>
                            <p><strong>Process:</strong> ${{selectedPoint.process.name}}</p>
                            <p><strong>Perspective:</strong> ${{selectedPoint.perspective.name}}</p>
                            <p><strong>Strength:</strong> ${{selectedPoint.strength.toFixed(2)}}</p>
                            <p><strong>Confidence:</strong> ${{selectedPoint.confidence.toFixed(2)}}</p>
                        `;
                    }}
                }});
                
                // Animation loop
                function animate() {{
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }}
                
                animate();
            </script>
            
            <script>
                {dataset_selector_js}
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"3D cube visualization generated at {output_path}")
        return output_path
    
    def generate_force_directed_graph_data(self) -> Dict[str, Any]:
        """
        Generate data for a force-directed graph visualization.
        
        Returns:
            Dictionary containing data for force-directed graph
        """
        # Get all patterns
        all_patterns = list(self.framework._patterns.values())
        
        # Prepare nodes and links
        nodes = []
        for pattern in all_patterns:
            nodes.append({
                "id": pattern.id,
                "name": pattern.name,
                "type": pattern.type,
                "domain": getattr(pattern, "domain", None),
            })
        
        links = []
        for rel in self.framework._relationships.values():
            # Create links for each valid pair in the relationship
            if rel.property_id and rel.process_id:
                links.append({
                    "source": rel.property_id,
                    "target": rel.process_id,
                    "strength": rel.strength,
                    "type": "property-process"
                })
            
            if rel.property_id and rel.perspective_id:
                links.append({
                    "source": rel.property_id,
                    "target": rel.perspective_id,
                    "strength": rel.strength,
                    "type": "property-perspective"
                })
            
            if rel.process_id and rel.perspective_id:
                links.append({
                    "source": rel.process_id,
                    "target": rel.perspective_id,
                    "strength": rel.strength,
                    "type": "process-perspective"
                })
        
        return {
            "nodes": nodes,
            "links": links
        }
    
    def generate_force_directed_graph_html(self, output_file: Union[str, Path],
                                         graph_data: Optional[Dict[str, Any]] = None,
                                         title: str = "P3IF Force-Directed Graph") -> Path:
        """
        Generate an HTML file with an interactive force-directed graph.
        
        Args:
            output_file: Path to save the HTML file
            graph_data: Optional pre-generated graph data (if None, will generate)
            title: Title for the visualization
            
        Returns:
            Path to the generated HTML file
        """
        if graph_data is None:
            graph_data = self.generate_force_directed_graph_data()
        
        output_path = Path(output_file)
        os.makedirs(output_path.parent, exist_ok=True)
        
        # Convert the data to JSON for embedding in JavaScript
        data_json = json.dumps(graph_data)
        
        # Generate the HTML with embedded D3.js visualization
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0;
                    font-family: Arial, sans-serif;
                    overflow: hidden;
                }}
                #info {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    max-width: 300px;
                    z-index: 100;
                }}
                #canvas-container {{
                    width: 100%;
                    height: 100vh;
                }}
                .node {{
                    stroke: #fff;
                    stroke-width: 1.5px;
                }}
                .link {{
                    stroke: #999;
                    stroke-opacity: 0.6;
                }}
                .property {{ fill: #1f77b4; }}
                .process {{ fill: #ff7f0e; }}
                .perspective {{ fill: #2ca02c; }}
                #legend {{
                    position: absolute;
                    bottom: 20px;
                    right: 20px;
                    background: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    z-index: 100;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 5px;
                }}
                .legend-color {{
                    width: 15px;
                    height: 15px;
                    margin-right: 5px;
                    border-radius: 50%;
                }}
                .search-container {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    z-index: 100;
                }}
                #search {{
                    padding: 5px;
                    width: 200px;
                    border-radius: 3px;
                    border: 1px solid #ccc;
                }}
            </style>
            <script src="https://d3js.org/d3.v7.min.js"></script>
        </head>
        <body>
            <div id="info">
                <h2>{title}</h2>
                <p>This visualization represents the relationships between P3IF patterns as a force-directed graph.</p>
                <p>Nodes are color-coded by pattern type, and link thickness represents relationship strength.</p>
                <p>Drag nodes to reposition them. Click on a node to see its details.</p>
                <div id="selection-info"></div>
            </div>
            
            <div class="search-container">
                <input type="text" id="search" placeholder="Search nodes...">
            </div>
            
            <div id="canvas-container"></div>
            
            <div id="legend">
                <h3>Legend</h3>
                <div class="legend-item">
                    <div class="legend-color property"></div>
                    <div>Property</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color process"></div>
                    <div>Process</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color perspective"></div>
                    <div>Perspective</div>
                </div>
            </div>
            
            <script>
                // P3IF data
                const graphData = {data_json};
                
                // Setup
                const container = document.getElementById('canvas-container');
                const width = container.clientWidth;
                const height = container.clientHeight;
                
                // Create SVG
                const svg = d3.select("#canvas-container")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                // Define arrow marker for directed links
                svg.append("defs").append("marker")
                    .attr("id", "arrowhead")
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 20)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "#999");
                
                // Create the force simulation
                const simulation = d3.forceSimulation(graphData.nodes)
                    .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collide", d3.forceCollide().radius(30));
                
                // Draw the links
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(graphData.links)
                    .enter().append("line")
                    .attr("class", "link")
                    .attr("stroke-width", d => Math.max(1, d.strength * 5));
                
                // Draw the nodes
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(graphData.nodes)
                    .enter().append("circle")
                    .attr("class", d => `node ${{d.type}}`)
                    .attr("r", 7)
                    .attr("title", d => d.name)
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                // Add node labels
                const label = svg.append("g")
                    .attr("class", "labels")
                    .selectAll("text")
                    .data(graphData.nodes)
                    .enter().append("text")
                    .attr("dx", 12)
                    .attr("dy", ".35em")
                    .text(d => d.name)
                    .style("font-size", "10px")
                    .style("pointer-events", "none");
                
                // Add tooltips and interaction
                node.on("click", function(event, d) {{
                    const infoDiv = document.getElementById('selection-info');
                    infoDiv.innerHTML = `
                        <h3>Selected Pattern</h3>
                        <p><strong>Name:</strong> ${{d.name}}</p>
                        <p><strong>Type:</strong> ${{d.type.charAt(0).toUpperCase() + d.type.slice(1)}}</p>
                        <p><strong>Domain:</strong> ${{d.domain || "None"}}</p>
                    `;
                    
                    // Highlight connected links and nodes
                    link.style("stroke", l => 
                        (l.source.id === d.id || l.target.id === d.id) ? "#000" : "#999");
                    link.style("stroke-width", l => 
                        (l.source.id === d.id || l.target.id === d.id) ? 
                        Math.max(2, l.strength * 6) : Math.max(1, l.strength * 5));
                    
                    node.style("stroke-width", n => 
                        (n.id === d.id) ? 3 : 1.5);
                }});
                
                // Search functionality
                const searchBox = document.getElementById('search');
                searchBox.addEventListener('input', function() {{
                    const searchTerm = this.value.toLowerCase();
                    
                    if (searchTerm === '') {{
                        // Reset visualization
                        node.style("opacity", 1);
                        link.style("opacity", 0.6);
                        label.style("opacity", 1);
                        return;
                    }}
                    
                    // Find matching nodes
                    const matchingNodes = graphData.nodes.filter(n => 
                        n.name.toLowerCase().includes(searchTerm));
                    const matchingIds = new Set(matchingNodes.map(n => n.id));
                    
                    // Highlight matching nodes and their connections
                    node.style("opacity", n => matchingIds.has(n.id) ? 1 : 0.2);
                    link.style("opacity", l => 
                        (matchingIds.has(l.source.id) || matchingIds.has(l.target.id)) ? 0.8 : 0.1);
                    label.style("opacity", l => matchingIds.has(l.id) ? 1 : 0.2);
                }});
                
                // Update positions on each simulation tick
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                
                    label
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);
                }});
                
                // Drag functions
                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}
                
                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}
                
                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"Force-directed graph visualization generated at {output_path}")
        return output_path 