"""
Multi-Domain Portal for P3IF

This module provides a unified portal for visualizing and exploring multiple domains
within the P3IF framework, enabling cross-domain analysis and comparison.
"""

import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import logging
from datetime import datetime
from collections import defaultdict

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as py
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available. Portal features will be limited.")


@dataclass
class MultiDomainPortal:
    """Portal for multi-domain P3IF visualization and analysis."""

    name: str = "multi_domain_portal"
    domains: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    portal_config: Dict[str, Any] = field(default_factory=dict)
    logger = logging.getLogger(__name__)

    def __post_init__(self):
        if not PLOTLY_AVAILABLE:
            self.logger.warning("Plotly not available. Some portal features will be limited.")

        # Default portal configuration
        self.portal_config = {
            "layout": {
                "type": "dashboard",
                "columns": 3,
                "rows": 2,
                "responsive": True
            },
            "visualizations": {
                "domain_comparison": True,
                "cross_domain_relationships": True,
                "pattern_analysis": True,
                "metric_summary": True
            },
            "interaction": {
                "enable_filtering": True,
                "enable_drilling": True,
                "enable_export": True
            }
        }

    def add_domain(self, domain_name: str, domain_data: Dict[str, Any]):
        """Add a domain to the portal."""
        self.domains[domain_name] = domain_data
        self.logger.info(f"Added domain to portal: {domain_name}")

    def load_domains_from_file(self, filepath: str):
        """Load domains from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.domains.update(data)
                self.logger.info(f"Loaded domains from {filepath}")
        except Exception as e:
            self.logger.error(f"Error loading domains from {filepath}: {e}")

    def create_portal_dashboard(self) -> Any:
        """Create the main portal dashboard."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_portal()

        try:
            # Create subplot layout
            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=(
                    'Domain Overview',
                    'Property Distribution',
                    'Cross-Domain Relationships',
                    'Process Analysis',
                    'Perspective Coverage',
                    'Pattern Metrics',
                    'Domain Comparison',
                    'Relationship Matrix',
                    'Summary Dashboard'
                ),
                specs=[
                    [{'type': 'domain'}, {'type': 'bar'}, {'type': 'scatter'}],
                    [{'type': 'bar'}, {'type': 'pie'}, {'type': 'heatmap'}],
                    [{'type': 'scatter3d'}, {'type': 'scatter'}, {'type': 'domain'}]
                ]
            )

            # Add visualizations for each domain
            domain_names = list(self.domains.keys())

            for i, domain_name in enumerate(domain_names):
                domain_data = self.domains[domain_name]
                row = i // 3 + 1
                col = i % 3 + 1

                self._add_domain_visualization(fig, domain_name, domain_data, row, col)

            # Update layout
            fig.update_layout(
                title="P3IF Multi-Domain Portal",
                height=1200,
                showlegend=True
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating portal dashboard: {e}")
            return self._create_ascii_portal()

    def _add_domain_visualization(self, fig, domain_name: str, domain_data: Dict[str, Any],
                                 row: int, col: int):
        """Add visualization for a specific domain."""
        if not PLOTLY_AVAILABLE:
            return

        try:
            # Extract domain metrics
            properties = domain_data.get('properties', [])
            processes = domain_data.get('processes', [])
            perspectives = domain_data.get('perspectives', [])
            relationships = domain_data.get('relationships', [])

            # Create domain overview pie chart
            if row == 1 and col == 1:
                labels = ['Properties', 'Processes', 'Perspectives']
                values = [len(properties), len(processes), len(perspectives)]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

                fig.add_trace(
                    go.Pie(
                        labels=labels,
                        values=values,
                        name=domain_name,
                        marker_colors=colors,
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Domain: ' + domain_name + '<extra></extra>'
                    ),
                    row=row, col=col
                )

            # Add property distribution
            elif row == 1 and col == 2:
                prop_types = defaultdict(int)
                for prop in properties:
                    prop_type = prop.get('type', 'unknown')
                    prop_types[prop_type] += 1

                fig.add_trace(
                    go.Bar(
                        x=list(prop_types.keys()),
                        y=list(prop_types.values()),
                        name=f'{domain_name} Properties',
                        marker_color='#FF6B6B'
                    ),
                    row=row, col=col
                )

            # Add process analysis
            elif row == 2 and col == 1:
                proc_types = defaultdict(int)
                for proc in processes:
                    proc_type = proc.get('type', 'unknown')
                    proc_types[proc_type] += 1

                fig.add_trace(
                    go.Bar(
                        x=list(proc_types.keys()),
                        y=list(proc_types.values()),
                        name=f'{domain_name} Processes',
                        marker_color='#4ECDC4',
                        orientation='h'
                    ),
                    row=row, col=col
                )

            # Add perspective coverage
            elif row == 2 and col == 2:
                pers_types = defaultdict(int)
                for pers in perspectives:
                    pers_type = pers.get('type', 'unknown')
                    pers_types[pers_type] += 1

                fig.add_trace(
                    go.Pie(
                        labels=list(pers_types.keys()),
                        values=list(pers_types.values()),
                        name=f'{domain_name} Perspectives',
                        marker_colors=['#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                    ),
                    row=row, col=col
                )

        except Exception as e:
            self.logger.error(f"Error adding domain visualization for {domain_name}: {e}")

    def create_cross_domain_comparison(self) -> Any:
        """Create cross-domain comparison visualization."""
        if not PLOTLY_AVAILABLE:
            return self._create_ascii_comparison()

        try:
            # Create comparison data
            comparison_data = self._prepare_comparison_data()

            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=comparison_data['similarity_matrix'],
                x=comparison_data['domain_names'],
                y=comparison_data['domain_names'],
                colorscale='Viridis',
                text=comparison_data['similarity_labels'],
                texttemplate="%{text}",
                textfont={"size": 12},
                hoverongaps=False
            ))

            fig.update_layout(
                title="Cross-Domain Similarity Matrix",
                xaxis_title="Domain",
                yaxis_title="Domain",
                height=600
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating cross-domain comparison: {e}")
            return self._create_ascii_comparison()

    def _prepare_comparison_data(self) -> Dict[str, Any]:
        """Prepare data for cross-domain comparison."""
        domain_names = list(self.domains.keys())
        n_domains = len(domain_names)

        # Initialize similarity matrix
        similarity_matrix = [[0.0 for _ in range(n_domains)] for _ in range(n_domains)]
        similarity_labels = [["" for _ in range(n_domains)] for _ in range(n_domains)]

        # Calculate similarities
        for i, domain1 in enumerate(domain_names):
            for j, domain2 in enumerate(domain_names):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                    similarity_labels[i][j] = "Same Domain"
                else:
                    similarity = self._calculate_domain_similarity(domain1, domain2)
                    similarity_matrix[i][j] = similarity
                    similarity_labels[i][j] = f"{similarity:.2f}"

        return {
            'domain_names': domain_names,
            'similarity_matrix': similarity_matrix,
            'similarity_labels': similarity_labels
        }

    def _calculate_domain_similarity(self, domain1: str, domain2: str) -> float:
        """Calculate similarity between two domains."""
        data1 = self.domains[domain1]
        data2 = self.domains[domain2]

        # Simple similarity based on element counts
        props1 = len(data1.get('properties', []))
        props2 = len(data2.get('properties', []))
        procs1 = len(data1.get('processes', []))
        procs2 = len(data2.get('processes', []))
        pers1 = len(data1.get('perspectives', []))
        pers2 = len(data2.get('perspectives', []))

        # Calculate similarity score
        total1 = props1 + procs1 + pers1
        total2 = props2 + procs2 + pers2

        if total1 == 0 or total2 == 0:
            return 0.0

        # Weighted similarity based on relative sizes
        prop_sim = min(props1, props2) / max(props1, props2) if max(props1, props2) > 0 else 1.0
        proc_sim = min(procs1, procs2) / max(procs1, procs2) if max(procs1, procs2) > 0 else 1.0
        pers_sim = min(pers1, pers2) / max(pers1, pers2) if max(pers1, pers2) > 0 else 1.0

        return (prop_sim + proc_sim + pers_sim) / 3.0

    def generate_portal_html(self, output_file: str = "p3if_portal.html") -> str:
        """Generate HTML portal file."""
        if not PLOTLY_AVAILABLE:
            return self._generate_ascii_portal_html(output_file)

        try:
            # Create dashboard
            dashboard = self.create_portal_dashboard()

            # Generate HTML
            html_content = py.plot(
                dashboard,
                output_type='div',
                include_plotlyjs='cdn',
                show_link=False,
                link_text=""
            )

            # Add custom CSS and JavaScript
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>P3IF Multi-Domain Portal</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .dashboard-container {{
                        max-width: 1400px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .controls {{
                        margin: 20px 0;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                    }}
                    .domain-selector {{
                        margin: 10px 0;
                    }}
                    .legend {{
                        display: flex;
                        justify-content: center;
                        gap: 20px;
                        margin: 20px 0;
                    }}
                    .legend-item {{
                        display: flex;
                        align-items: center;
                        gap: 5px;
                    }}
                    .color-box {{
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>P3IF Multi-Domain Portal</h1>
                    <p>Interactive visualization and analysis of multiple P3IF domains</p>
                </div>

                <div class="dashboard-container">
                    <div class="controls">
                        <div class="domain-selector">
                            <h3>Domain Controls</h3>
                            <p>Select domains to analyze: {', '.join(self.domains.keys())}</p>
                        </div>
                    </div>

                    <div class="legend">
                        <div class="legend-item">
                            <div class="color-box" style="background-color: #FF6B6B;"></div>
                            <span>Properties</span>
                        </div>
                        <div class="legend-item">
                            <div class="color-box" style="background-color: #4ECDC4;"></div>
                            <span>Processes</span>
                        </div>
                        <div class="legend-item">
                            <div class="color-box" style="background-color: #45B7D1;"></div>
                            <span>Perspectives</span>
                        </div>
                    </div>

                    {html_content}
                </div>

                <script>
                    // Add interactive functionality
                    console.log('P3IF Portal loaded with domains: {', '.join(self.domains.keys())}');
                </script>
            </body>
            </html>
            """

            with open(output_file, 'w') as f:
                f.write(full_html)

            self.logger.info(f"Portal HTML generated: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error generating portal HTML: {e}")
            return self._generate_ascii_portal_html(output_file)

    def _create_ascii_portal(self) -> str:
        """Create ASCII representation of the portal."""
        return f"""
        P3IF Multi-Domain Portal (ASCII Representation)

        ┌─────────────────────────────────────────────────────────────────┐
        │                    P3IF MULTI-DOMAIN PORTAL                     │
        │                                                                 │
        │  Domains: {', '.join(self.domains.keys())}                     │
        │                                                                 │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
        │  │   Domain    │  │   Cross-    │  │  Pattern    │            │
        │  │ Overview    │  │  Domain     │  │ Analysis    │            │
        │  │             │  │ Relations   │  │             │            │
        │  └─────────────┘  └─────────────┘  └─────────────┘            │
        │                                                                 │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
        │  │  Property   │  │ Perspective │  │ Relationship│            │
        │  │ Distri-     │  │  Coverage   │  │    Matrix   │            │
        │  │ bution      │  │             │  │             │            │
        │  └─────────────┘  └─────────────┘  └─────────────┘            │
        │                                                                 │
        │  ┌─────────────────────────────────────────────────────────────┐  │
        │  │                   Summary Dashboard                         │  │
        │  │  • Total Domains: {len(self.domains)}                         │  │
        │  │  • Total Properties: {sum(len(d.get('properties', [])) for d in self.domains.values())} │  │
        │  │  • Total Processes: {sum(len(d.get('processes', [])) for d in self.domains.values())} │  │
        │  │  • Total Perspectives: {sum(len(d.get('perspectives', [])) for d in self.domains.values())} │  │
        │  └─────────────────────────────────────────────────────────────┘  │
        └─────────────────────────────────────────────────────────────────┘
        """

    def _generate_ascii_portal_html(self, output_file: str) -> str:
        """Generate ASCII-based HTML portal."""
        ascii_portal = self._create_ascii_portal()

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>P3IF Multi-Domain Portal (ASCII)</title>
            <style>
                body {{
                    font-family: monospace;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    white-space: pre;
                }}
                .portal-container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-width: 1200px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div class="portal-container">
                {ascii_portal.replace('<', '&lt;').replace('>', '&gt;')}
            </div>
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file

    def _create_ascii_comparison(self) -> str:
        """Create ASCII representation of cross-domain comparison."""
        domain_names = list(self.domains.keys())
        n = len(domain_names)

        ascii_comp = """
        Cross-Domain Similarity Matrix (ASCII)

        """

        # Header
        ascii_comp += "     " + "    ".join(f"{name[:4]:<4}" for name in domain_names) + "\n"
        ascii_comp += "    " + "─" * (5 * len(domain_names)) + "\n"

        # Matrix rows
        for i, row_domain in enumerate(domain_names):
            ascii_comp += f"{row_domain[:4]:<4}│"

            for j, col_domain in enumerate(domain_names):
                if i == j:
                    similarity = "1.00"
                else:
                    similarity = f"{self._calculate_domain_similarity(row_domain, col_domain):.2f}"

                ascii_comp += f" {similarity:<4}│"

            ascii_comp += "\n"

        return ascii_comp
