"""
P3IF Enhanced Interactive Visualizations

This module provides modern, high-performance interactive visualization capabilities
for P3IF data, including 3D visualizations, network graphs, and web-based interactive elements
with enhanced user experience and performance optimizations.
"""
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import logging
import json
import asyncio
from pathlib import Path
import os
import numpy as np
from dataclasses import dataclass
from enum import Enum
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time

from p3if_methods.framework import P3IFFramework
from p3if_methods.models import BasePattern
from .base import Visualizer
from utils.config import Config
from utils.performance import (
    get_performance_monitor, get_cache, performance_timer,
    cached, memoize, performance_context
)
from utils.output_organizer import (
    get_output_organizer, organize_visualization_output,
    organize_animation_output, create_standard_output_structure
)


class VisualizationType(str, Enum):
    """Types of visualizations available."""
    CUBE_3D = "cube_3d"
    NETWORK_GRAPH = "network_graph"
    MATRIX_VIEW = "matrix_view"
    DASHBOARD = "dashboard"
    FORCE_DIRECTED = "force_directed"
    TIMELINE = "timeline"
    HIERARCHICAL = "hierarchical"
    SCATTER_PLOT = "scatter_plot"


class InteractionMode(str, Enum):
    """Different interaction modes for visualizations."""
    VIEW_ONLY = "view_only"
    SELECT = "select"
    EDIT = "edit"
    FILTER = "filter"
    ANNOTATE = "annotate"


@dataclass
class VisualizationConfig:
    """Configuration for visualization generation."""
    width: int = 1200
    height: int = 800
    theme: str = "default"  # default, dark, light, blue
    interactive: bool = True
    show_labels: bool = True
    show_legend: bool = True
    animation_duration: int = 1000  # ms
    max_elements: int = 1000
    quality: str = "high"  # low, medium, high, ultra
    cache_enabled: bool = True
    compression_level: int = 6  # 0-9 for PNG compression


class InteractiveVisualizer(Visualizer):
    """Enhanced interactive visualizer with modern capabilities."""
    
    def __init__(self, framework: P3IFFramework, config: Optional[Config] = None):
        """
        Initialize enhanced interactive visualizer.
        
        Args:
            framework: P3IF framework instance
            config: Optional configuration
        """
        super().__init__(framework, config)
    
        # Enhanced caching with LRU and TTL support
        self._cache = get_cache('visualization')  # Use global cache
        self._local_cache: Dict[str, Dict[str, Any]] = {}  # Local cache for session data
        self._cache_expiry: Dict[str, float] = {}
        self._max_cache_size = 100  # Maximum local cache entries

        # Performance monitoring and optimization
        self._performance_monitor = get_performance_monitor()
        self._render_times: List[float] = []
        self._memory_usage: List[int] = []

        # Concurrent rendering support (optimized)
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="viz")

        # Data preprocessing optimization
        self._preprocessed_data: Optional[Dict[str, Any]] = None
        self._last_preprocess_time: float = 0
        self._preprocess_interval = 300  # 5 minutes

        # Theme configurations
        self._themes = {
            "default": {
                "background": "#ffffff",
                "primary": "#1f77b4",
                "secondary": "#ff7f0e",
                "tertiary": "#2ca02c",
                "text": "#333333",
                "grid": "#e0e0e0"
            },
            "dark": {
                "background": "#1a1a1a",
                "primary": "#4a90e2",
                "secondary": "#ff9500",
                "tertiary": "#34c759",
                "text": "#ffffff",
                "grid": "#333333"
            },
            "light": {
                "background": "#f8f9fa",
                "primary": "#007bff",
                "secondary": "#fd7e14",
                "tertiary": "#28a745",
                "text": "#212529",
                "grid": "#dee2e6"
            },
            "blue": {
                "background": "#e3f2fd",
                "primary": "#1976d2",
                "secondary": "#ff8f00",
                "tertiary": "#388e3c",
                "text": "#1565c0",
                "grid": "#bbdefb"
            }
        }
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Generate a cache key for visualization data."""
        key_data = f"{method_name}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached visualization data if available and not expired."""
        if cache_key in self._cache:
            if time.time() - self._cache_expiry.get(cache_key, 0) < 3600:  # 1 hour expiry
                return self._cache[cache_key]
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
                del self._cache_expiry[cache_key]
        return None

    def _cache_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache visualization data."""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entries
            oldest_key = min(self._cache_expiry.keys(), key=self._cache_expiry.get)
            del self._cache[oldest_key]
            del self._cache_expiry[oldest_key]

        self._cache[cache_key] = data
        self._cache_expiry[cache_key] = time.time()

    def _sample_patterns(self, patterns: List[BasePattern], max_elements: int) -> List[BasePattern]:
        """Intelligently sample patterns for better performance."""
        if len(patterns) <= max_elements:
            return patterns

        # Use stratified sampling based on quality scores
        patterns_with_scores = [(p, p.quality_score) for p in patterns if p.quality_score > 0]
        if not patterns_with_scores:
            return patterns[:max_elements]

        # Sort by quality score and take top elements
        patterns_with_scores.sort(key=lambda x: x[1], reverse=True)
        high_quality_patterns = [p for p, _ in patterns_with_scores[:max_elements // 2]]

        # Fill remaining slots with random sampling
        remaining_slots = max_elements - len(high_quality_patterns)
        remaining_patterns = [p for p in patterns if p not in high_quality_patterns]

        if remaining_patterns:
            import random
            sampled_remaining = random.sample(
                remaining_patterns,
                min(remaining_slots, len(remaining_patterns))
            )
        else:
            sampled_remaining = []

        return high_quality_patterns + sampled_remaining

    def _preprocess_data(self) -> Dict[str, Any]:
        """Preprocess data for better rendering performance."""
        now = time.time()

        # Check if preprocessing is still valid
        if (self._preprocessed_data and
            (now - self._last_preprocess_time) < self._preprocess_interval):
            return self._preprocessed_data

        # Preprocess pattern data
        all_patterns = list(self.framework._patterns.values())
        pattern_types = {}
        domains = set()

        for pattern in all_patterns:
            pattern_type = pattern.pattern_type.value
            if pattern_type not in pattern_types:
                pattern_types[pattern_type] = []
            pattern_types[pattern_type].append(pattern)

            if pattern.domain:
                domains.add(pattern.domain)

        # Preprocess relationship data
        all_relationships = list(self.framework._relationships.values())
        relationship_stats = {
            'total': len(all_relationships),
            'avg_strength': sum(r.strength for r in all_relationships) / len(all_relationships) if all_relationships else 0,
            'avg_confidence': sum(r.confidence for r in all_relationships) / len(all_relationships) if all_relationships else 0
        }

        self._preprocessed_data = {
            'patterns': pattern_types,
            'domains': list(domains),
            'relationship_stats': relationship_stats,
            'timestamp': now
        }

        self._last_preprocess_time = now
        return self._preprocessed_data

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get visualization performance statistics."""
        cache_stats = self._cache.stats() if hasattr(self._cache, 'stats') else {}

        return {
            'cache_stats': cache_stats,
            'render_times': {
                'count': len(self._render_times),
                'average': sum(self._render_times) / len(self._render_times) if self._render_times else 0,
                'min': min(self._render_times) if self._render_times else 0,
                'max': max(self._render_times) if self._render_times else 0
            },
            'memory_usage': self._memory_usage[-10:] if self._memory_usage else [],
            'preprocessed_data_age': time.time() - self._last_preprocess_time if self._preprocessed_data else None
        }

    @performance_timer("generate_3d_cube_data")
    def generate_3d_cube_data(self, domains: Optional[List[str]] = None,
                            max_elements: int = 1000) -> Dict[str, Any]:
        """
        Generate enhanced data for a 3D interactive cube visualization with performance optimizations.
        
        The cube represents the three dimensions of P3IF:
        - Properties (X-axis)
        - Processes (Y-axis)
        - Perspectives (Z-axis)
        
        Args:
            domains: Optional list of domains to include
            max_elements: Maximum number of elements to include

        Returns:
            Dictionary containing enhanced data for 3D cube visualization
        """
        # Check cache first (enhanced caching)
        cache_key = self._get_cache_key("cube_data", domains=domains, max_elements=max_elements)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Use optimized framework methods for better performance
        if domains:
            properties = self.framework.get_patterns_by_domain_optimized(domains)
            processes = self.framework.get_patterns_by_domain_optimized(domains)
            perspectives = self.framework.get_patterns_by_domain_optimized(domains)
        else:
            properties = self.framework.get_patterns_by_type_optimized("property")
            processes = self.framework.get_patterns_by_type_optimized("process")
            perspectives = self.framework.get_patterns_by_type_optimized("perspective")

        # Limit elements for performance with intelligent sampling
        properties = self._sample_patterns(properties, max_elements)
        processes = self._sample_patterns(processes, max_elements)
        perspectives = self._sample_patterns(perspectives, max_elements)

        # Create enhanced mappings
        property_map = {p.id: i for i, p in enumerate(properties)}
        process_map = {p.id: i for i, p in enumerate(processes)}
        perspective_map = {p.id: i for i, p in enumerate(perspectives)}
        
        # Prepare enhanced data structure
        cube_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_properties": len(properties),
                "total_processes": len(processes),
                "total_perspectives": len(perspectives),
                "domains": domains or "all",
                "max_elements": max_elements
            },
            "dimensions": {
                "property": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "domain": p.domain,
                        "tags": p.tags,
                        "quality_score": p.quality_score,
                        "validation_status": p.validation_status
                    } for p in properties
                ],
                "process": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "domain": p.domain,
                        "complexity": getattr(p, "complexity", "medium"),
                        "automation_level": getattr(p, "automation_level", "manual"),
                        "quality_score": p.quality_score
                    } for p in processes
                ],
                "perspective": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "domain": p.domain,
                        "viewpoint": getattr(p, "viewpoint", ""),
                        "stakeholder_type": getattr(p, "stakeholder_type", ""),
                        "quality_score": p.quality_score
                    } for p in perspectives
                ]
            },
            "connections": []
        }
        
        # Add enhanced relationship data
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
                        "strength": float(rel.strength),
                        "confidence": float(rel.confidence),
                        "relationship_type": rel.relationship_type,
                        "bidirectional": rel.bidirectional,
                        "status": rel.status,
                        "position": {
                        "x": property_map[rel.property_id],
                        "y": process_map[rel.process_id],
                        "z": perspective_map[rel.perspective_id]
                        }
                    }
                    cube_data["connections"].append(connection)
        
        # Cache the result
        self._cache_data(cache_key, cube_data)
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

        # Use output organizer for consistent directory structure
        organizer = get_output_organizer()
        output_path = organizer.get_visualization_path("3d_cube", Path(output_file).name)
        
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

    def generate_modern_dashboard(self, output_file: Union[str, Path],
                                 config: Optional[VisualizationConfig] = None,
                                 title: str = "P3IF Modern Dashboard") -> Path:
        """
        Generate a modern, responsive dashboard with multiple visualization types.

        Args:
            output_file: Path to save the HTML file
            config: Visualization configuration
            title: Title for the dashboard

        Returns:
            Path to the generated HTML file
        """
        start_time = time.time()

        if config is None:
            config = VisualizationConfig()

        output_path = Path(output_file)
        os.makedirs(output_path.parent, exist_ok=True)

        # Get theme colors
        theme = self._themes.get(config.theme, self._themes["default"])

        # Generate multiple data views
        cube_data = self.generate_3d_cube_data()
        network_data = self.generate_force_directed_graph_data()

        # Calculate statistics
        total_patterns = (len(cube_data.get("dimensions", {}).get("property", [])) +
                         len(cube_data.get("dimensions", {}).get("process", [])) +
                         len(cube_data.get("dimensions", {}).get("perspective", [])))

        total_relationships = len(cube_data.get("connections", []))
        avg_strength = sum(c.get("strength", 0) for c in cube_data.get("connections", [])) / max(1, total_relationships)

        # Enhanced HTML dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>

            <!-- Modern CSS Framework -->
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/chart.js" rel="stylesheet">

            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                :root {{
                    --primary-color: {theme['primary']};
                    --secondary-color: {theme['secondary']};
                    --tertiary-color: {theme['tertiary']};
                    --background: {theme['background']};
                    --text: {theme['text']};
                    --grid: {theme['grid']};
                }}

                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: var(--background);
                    color: var(--text);
                    overflow-x: hidden;
                }}

                .dashboard-container {{
                    display: flex;
                    flex-direction: column;
                    min-height: 100vh;
                }}

                .header {{
                    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                    color: white;
                    padding: 1rem 2rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}

                .header h1 {{
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin: 0;
                }}

                .nav-tabs {{
                    display: flex;
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 0.5rem;
                    margin-top: 1rem;
                }}

                .tab-btn {{
                    flex: 1;
                    padding: 0.75rem 1rem;
                    background: transparent;
                    border: none;
                    color: rgba(255,255,255,0.7);
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-size: 0.9rem;
                }}

                .tab-btn:hover {{
                    background: rgba(255,255,255,0.1);
                    color: white;
                }}

                .tab-btn.active {{
                    background: white;
                    color: var(--primary-color);
                    font-weight: 600;
                }}

                .main-content {{
                    flex: 1;
                    padding: 2rem;
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    gap: 2rem;
                    max-width: 1600px;
                    margin: 0 auto;
                    width: 100%;
                }}

                .sidebar {{
                    background: white;
                    border-radius: 12px;
                    padding: 1.5rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    height: fit-content;
                    position: sticky;
                    top: 2rem;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                }}

                .stat-card {{
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                }}

                .stat-number {{
                    font-size: 2rem;
                    font-weight: bold;
                    margin-bottom: 0.25rem;
                }}

                .stat-label {{
                    font-size: 0.8rem;
                    opacity: 0.9;
                }}

                .control-panel h3 {{
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                    font-size: 1.1rem;
                }}

                .filter-group {{
                    margin-bottom: 1rem;
                }}

                .filter-group label {{
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: 500;
                }}

                .filter-options {{
                    display: flex;
                    gap: 0.5rem;
                    flex-wrap: wrap;
                }}

                .filter-chip {{
                    padding: 0.25rem 0.75rem;
                    background: var(--grid);
                    border: 1px solid var(--grid);
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 0.8rem;
                    transition: all 0.2s;
                }}

                .filter-chip:hover {{
                    background: var(--primary-color);
                    color: white;
                }}

                .filter-chip.active {{
                    background: var(--primary-color);
                    color: white;
                }}

                .slider-group {{
                    margin-bottom: 1rem;
                }}

                .slider-group label {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                }}

                .slider {{
                    width: 100%;
                    height: 6px;
                    border-radius: 3px;
                    background: var(--grid);
                    outline: none;
                    -webkit-appearance: none;
                }}

                .slider::-webkit-slider-thumb {{
                    -webkit-appearance: none;
                    width: 18px;
                    height: 18px;
                    border-radius: 50%;
                    background: var(--primary-color);
                    cursor: pointer;
                }}

                .content-area {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}

                .visualization-container {{
                    width: 100%;
                    height: 600px;
                    position: relative;
                }}

                .placeholder {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: #666;
                    font-size: 1.1rem;
                }}

                .footer {{
                    background: var(--grid);
                    padding: 1rem 2rem;
                    text-align: center;
                    font-size: 0.9rem;
                    color: #666;
                }}

                @media (max-width: 1200px) {{
                    .main-content {{
                        grid-template-columns: 1fr;
                        padding: 1rem;
                    }}

                    .sidebar {{
                        position: static;
                    }}
                }}

                @media (max-width: 768px) {{
                    .header {{
                        padding: 1rem;
                    }}

                    .header h1 {{
                        font-size: 1.2rem;
                    }}

                    .nav-tabs {{
                        flex-wrap: wrap;
                    }}

                    .tab-btn {{
                        flex: 1 1 45%;
                        margin-bottom: 0.5rem;
                    }}

                    .main-content {{
                        padding: 1rem 0.5rem;
                    }}

                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>

            <!-- Chart.js for analytics -->
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <!-- D3.js for network visualization -->
            <script src="https://d3js.org/d3.v7.min.js"></script>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="header">
                    <h1><i class="fas fa-chart-line"></i> {title}</h1>
                    <div class="nav-tabs">
                        <button class="tab-btn active" data-tab="overview">Overview</button>
                        <button class="tab-btn" data-tab="cube">3D Cube</button>
                        <button class="tab-btn" data-tab="network">Network</button>
                        <button class="tab-btn" data-tab="analytics">Analytics</button>
                    </div>
                </div>

                <div class="main-content">
                    <div class="sidebar">
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">{total_patterns}</div>
                                <div class="stat-label">Total Patterns</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{total_relationships}</div>
                                <div class="stat-label">Relationships</div>
                            </div>
                        </div>

                        <div class="control-panel">
                            <h3><i class="fas fa-filter"></i> Filters</h3>

                            <div class="filter-group">
                                <label>Relationship Strength</label>
                                <div class="filter-options">
                                    <button class="filter-chip active" data-strength="all">All</button>
                                    <button class="filter-chip" data-strength="strong">Strong (0.7+)</button>
                                    <button class="filter-chip" data-strength="medium">Medium (0.4-0.7)</button>
                                    <button class="filter-chip" data-strength="weak">Weak (0-0.4)</button>
                                </div>
                            </div>

                            <div class="slider-group">
                                <label>
                                    Min Strength: <span id="strength-value">0.0</span>
                                    <input type="range" id="strength-slider" class="slider" min="0" max="1" step="0.1" value="0">
                                </label>
                            </div>

                            <div class="slider-group">
                                <label>
                                    Min Confidence: <span id="confidence-value">0.0</span>
                                    <input type="range" id="confidence-slider" class="slider" min="0" max="1" step="0.1" value="0">
                                </label>
                            </div>
                        </div>
                    </div>

                    <div class="content-area">
                        <div id="overview-tab" class="visualization-container">
                            <div class="placeholder">
                                <div>
                                    <i class="fas fa-chart-bar" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                    <h3>Overview Dashboard</h3>
                                    <p>Interactive overview of P3IF framework data</p>
                                </div>
                            </div>
                        </div>

                        <div id="cube-tab" class="visualization-container" style="display: none;">
                            <div class="placeholder">
                                <div>
                                    <i class="fas fa-cube" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                    <h3>3D Cube Visualization</h3>
                                    <p>Interactive 3D representation of P3IF dimensions</p>
                                </div>
                            </div>
                        </div>

                        <div id="network-tab" class="visualization-container" style="display: none;">
                            <div class="placeholder">
                                <div>
                                    <i class="fas fa-project-diagram" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                    <h3>Network Graph</h3>
                                    <p>Force-directed graph of pattern relationships</p>
                                </div>
                            </div>
                        </div>

                        <div id="analytics-tab" class="visualization-container" style="display: none;">
                            <div class="placeholder">
                                <div>
                                    <i class="fas fa-analytics" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                                    <h3>Analytics Dashboard</h3>
                                    <p>Statistical analysis and insights</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>&copy; 2024 P3IF Framework - Enhanced Interactive Dashboard</p>
                </div>
            </div>

            <script>
                // P3IF Dashboard Data
                const p3ifData = {json.dumps(cube_data, indent=2)};
                const networkData = {json.dumps(network_data, indent=2)};

                // Tab switching
                document.querySelectorAll('.tab-btn').forEach(btn => {{
                    btn.addEventListener('click', function() {{
                        // Remove active class from all tabs
                        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                        document.querySelectorAll('[id$="-tab"]').forEach(t => t.style.display = 'none');

                        // Add active class to clicked tab
                        this.classList.add('active');

                        // Show corresponding content
                        const tabId = this.dataset.tab + '-tab';
                        document.getElementById(tabId).style.display = 'block';

                        // Initialize visualization if needed
                        if (this.dataset.tab === 'cube') {{
                            initCubeVisualization();
                        }} else if (this.dataset.tab === 'network') {{
                            initNetworkVisualization();
                        }} else if (this.dataset.tab === 'analytics') {{
                            initAnalyticsDashboard();
                        }}
                    }});
                }});

                // Filter functionality
                document.querySelectorAll('.filter-chip').forEach(chip => {{
                    chip.addEventListener('click', function() {{
                        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                        this.classList.add('active');

                        const filterType = this.dataset.strength;
                        applyStrengthFilter(filterType);
                    }});
                }});

                // Slider functionality
                const strengthSlider = document.getElementById('strength-slider');
                const confidenceSlider = document.getElementById('confidence-slider');

                strengthSlider.addEventListener('input', function() {{
                    document.getElementById('strength-value').textContent = this.value;
                    applySliderFilters(parseFloat(this.value), parseFloat(confidenceSlider.value));
                }});

                confidenceSlider.addEventListener('input', function() {{
                    document.getElementById('confidence-value').textContent = this.value;
                    applySliderFilters(parseFloat(strengthSlider.value), parseFloat(this.value));
                }});

                function applyStrengthFilter(filterType) {{
                    // Implementation would filter the data based on strength
                    console.log('Applying strength filter:', filterType);
                }}

                function applySliderFilters(minStrength, minConfidence) {{
                    // Implementation would filter based on slider values
                    console.log('Applying slider filters:', minStrength, minConfidence);
                }}

                function initCubeVisualization() {{
                    // Initialize 3D cube visualization
                    console.log('Initializing 3D cube visualization');
                }}

                function initNetworkVisualization() {{
                    // Initialize network graph
                    console.log('Initializing network visualization');
                }}

                function initAnalyticsDashboard() {{
                    // Initialize analytics with Chart.js
                    console.log('Initializing analytics dashboard');
                    initCharts();
                }}

                function initCharts() {{
                    const ctx = document.createElement('canvas');
                    ctx.id = 'analytics-chart';
                    ctx.width = 800;
                    ctx.height = 400;

                    document.querySelector('#analytics-tab .placeholder').innerHTML = '';
                    document.querySelector('#analytics-tab .visualization-container').appendChild(ctx);

                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: ['Properties', 'Processes', 'Perspectives', 'Relationships'],
                            datasets: [{{
                                label: 'Count',
                                data: [
                                    p3ifData.dimensions.property.length,
                                    p3ifData.dimensions.process.length,
                                    p3ifData.dimensions.perspective.length,
                                    p3ifData.connections.length
                                ],
                                backgroundColor: [
                                    'rgba(31, 119, 180, 0.8)',
                                    'rgba(255, 127, 14, 0.8)',
                                    'rgba(44, 160, 44, 0.8)',
                                    'rgba(214, 39, 40, 0.8)'
                                ]
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                y: {{
                                    beginAtZero: true
                                }}
                            }}
                        }}
                    }});
                }}

                // Initialize overview tab on load
                document.addEventListener('DOMContentLoaded', function() {{
                    initAnalyticsDashboard();
                }});
            </script>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        render_time = time.time() - start_time
        self.logger.info(f"Modern dashboard generated at {output_path} in {render_time:.2f}s")
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

        # Use output organizer for consistent directory structure
        organizer = get_output_organizer()
        output_path = organizer.get_visualization_path("network_graph", Path(output_file).name)
        
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