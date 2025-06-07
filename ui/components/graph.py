# ui/components/graph.py
"""
Graph visualization component for Cytoscape network display
Extracted from core_layout.py and graph_callbacks.py
"""

from dash import html, dcc
import dash_cytoscape as cyto
from ui.themes.style_config import COLORS
from ui.themes.graph_styles import (
    centered_graph_box_style,
    cytoscape_inside_box_style,
    tap_node_data_centered_style,
    actual_default_stylesheet_for_graph
)


class GraphComponent:
    """Centralized graph component with all visualization elements"""
    
    def __init__(self):
        self.default_layout = {
            'name': 'cose',
            'idealEdgeLength': 100,
            'nodeOverlap': 20,
            'refresh': 20,
            'fit': True,
            'padding': 30,
            'randomize': False,
            'componentSpacing': 100,
            'nodeRepulsion': 400000,
            'edgeElasticity': 100,
            'nestingFactor': 5,
            'gravity': 80,
            'numIter': 1000,
            'coolingFactor': 0.95,
            'minTemp': 1.0
        }
    
    def create_graph_container(self):
        """Creates the complete graph visualization container"""
        return html.Div(
            id='graph-output-container',
            style={'display': 'none'},
            children=[
                self.create_graph_title(),
                self.create_graph_area(),
                self.create_node_info_display()
            ]
        )
    
    def create_graph_title(self):
        """Creates the graph title"""
        return html.H2(
            "Area Layout Model",
            id="area-layout-model-title",
            style={
                'textAlign': 'center',
                'color': COLORS['text_primary'],
                'marginBottom': '20px',
                'fontSize': '1.8rem'
            }
        )
    
    def create_graph_area(self):
        """Creates the main Cytoscape graph area"""
        return html.Div(
            id='cytoscape-graphs-area',
            style=centered_graph_box_style,
            children=[
                self.create_cytoscape_graph()
            ]
        )
    
    def create_cytoscape_graph(self):
        """Creates the Cytoscape graph component"""
        return cyto.Cytoscape(
            id='onion-graph',
            layout=self.default_layout,
            style=cytoscape_inside_box_style,
            elements=[],
            stylesheet=actual_default_stylesheet_for_graph
        )
    
    def create_node_info_display(self):
        """Creates the node information display area"""
        return html.Pre(
            id='tap-node-data-output',
            style=tap_node_data_centered_style,
            children="Upload CSV, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
        )
    
    def create_graph_controls(self):
        """Creates graph control panel (for future enhancements)"""
        return html.Div([
            html.H4("Graph Controls", style={'color': COLORS['text_primary']}),
            self.create_layout_selector(),
            self.create_filter_controls(),
            self.create_export_controls()
        ], style={
            'padding': '15px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'margin': '10px 0'
        })
    
    def create_layout_selector(self):
        """Creates layout algorithm selector"""
        return html.Div([
            html.Label("Layout Algorithm:", style={'color': COLORS['text_primary'], 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='graph-layout-selector',
                options=[
                    {'label': 'COSE (Force-directed)', 'value': 'cose'},
                    {'label': 'Circle', 'value': 'circle'},
                    {'label': 'Grid', 'value': 'grid'},
                    {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                    {'label': 'Concentric', 'value': 'concentric'}
                ],
                value='cose',
                style={'backgroundColor': COLORS['background'], 'color': COLORS['text_primary']}
            )
        ], style={'marginBottom': '15px'})
    
    def create_filter_controls(self):
        """Creates graph filtering controls"""
        return html.Div([
            html.Label("Filters:", style={'color': COLORS['text_primary'], 'marginBottom': '5px'}),
            dcc.Checklist(
                id='graph-filters',
                options=[
                    {'label': ' Show Entrances Only', 'value': 'entrances_only'},
                    {'label': ' Show Critical Paths', 'value': 'critical_paths'},
                    {'label': ' Hide Low Security', 'value': 'hide_low_security'}
                ],
                value=[],
                labelStyle={'display': 'block', 'color': COLORS['text_primary'], 'marginBottom': '5px'}
            )
        ], style={'marginBottom': '15px'})
    
    def create_export_controls(self):
        """Creates graph export controls"""
        return html.Div([
            html.Button(
                "Export Graph as PNG",
                id='export-graph-png',
                style={
                    'backgroundColor': COLORS['accent'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '8px 16px',
                    'borderRadius': '4px',
                    'marginRight': '10px'
                }
            ),
            html.Button(
                "Export Data as JSON",
                id='export-graph-json',
                style={
                    'backgroundColor': COLORS['success'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '8px 16px',
                    'borderRadius': '4px'
                }
            )
        ])
    
    def create_graph_legend(self):
        """Creates a legend for the graph visualization"""
        return html.Div([
            html.H5("Legend", style={'color': COLORS['text_primary'], 'marginBottom': '10px'}),
            html.Div([
                self.create_legend_item("🟢", "Green - Public Access", COLORS['success']),
                self.create_legend_item("🟠", "Orange - Semi-Restricted", COLORS['warning']),
                self.create_legend_item("🔴", "Red - Restricted", COLORS['critical']),
                self.create_legend_item("⬜️", "Unclassified", COLORS['border']),
                html.Hr(style={'borderColor': COLORS['border']}),
                self.create_legend_item("🚪", "Entry/Exit Point", COLORS['accent']),
                self.create_legend_item("🏢", "Stairway", COLORS['text_secondary']),
                self.create_legend_item("⭐", "Critical Device", COLORS['warning'])
            ])
        ], style={
            'padding': '15px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'border': f'1px solid {COLORS["border"]}',
            'margin': '10px 0'
        })
    
    def create_legend_item(self, icon, description, color):
        """Creates a single legend item"""
        return html.Div([
            html.Span(icon, style={'marginRight': '8px', 'fontSize': '1.2em'}),
            html.Span(description, style={'color': color, 'fontWeight': '500'})
        ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'})
    
    def get_layout_options(self):
        """Returns available layout options"""
        return {
            'cose': {
                'name': 'cose',
                'idealEdgeLength': 100,
                'nodeOverlap': 20,
                'refresh': 20,
                'fit': True,
                'padding': 30,
                'randomize': False,
                'componentSpacing': 100,
                'nodeRepulsion': 400000,
                'edgeElasticity': 100,
                'nestingFactor': 5,
                'gravity': 80,
                'numIter': 1000,
                'coolingFactor': 0.95,
                'minTemp': 1.0
            },
            'circle': {
                'name': 'circle',
                'fit': True,
                'padding': 30,
                'boundingBox': {'x1': 0, 'y1': 0, 'w': 1, 'h': 1},
                'avoidOverlap': True,
                'nodeDimensionsIncludeLabels': False,
                'spacingFactor': 1.75,
                'radius': 200
            },
            'grid': {
                'name': 'grid',
                'fit': True,
                'padding': 30,
                'boundingBox': {'x1': 0, 'y1': 0, 'w': 1, 'h': 1},
                'avoidOverlap': True,
                'avoidOverlapPadding': 10,
                'nodeDimensionsIncludeLabels': False,
                'spacingFactor': 1.75,
                'condense': False,
                'rows': 3,
                'cols': 3
            },
            'breadthfirst': {
                'name': 'breadthfirst',
                'fit': True,
                'directed': False,
                'padding': 30,
                'circle': False,
                'grid': False,
                'spacingFactor': 1.75,
                'boundingBox': {'x1': 0, 'y1': 0, 'w': 1, 'h': 1},
                'avoidOverlap': True,
                'nodeDimensionsIncludeLabels': False
            },
            'concentric': {
                'name': 'concentric',
                'fit': True,
                'padding': 30,
                'startAngle': 3.141592653589793 / 4,
                'sweep': None,
                'clockwise': True,
                'equidistant': False,
                'minNodeSpacing': 10,
                'boundingBox': {'x1': 0, 'y1': 0, 'w': 1, 'h': 1},
                'avoidOverlap': True,
                'nodeDimensionsIncludeLabels': False,
                'height': None,
                'width': None,
                'spacingFactor': None,
                'concentric': lambda node: node['layer'] if 'layer' in node else 1,
                'levelWidth': lambda nodes: 2
            }
        }
    
    def format_node_details(self, node_data):
        """Formats node data for display"""
        if not node_data or node_data.get('is_layer_parent'):
            return "Upload CSV, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
        
        details = [f"Tapped: {node_data.get('label', node_data.get('id'))}"]
        
        if 'layer' in node_data:
            details.append(f"Layer: {node_data['layer']}")
        if 'floor' in node_data:
            details.append(f"Floor: {node_data['floor']}")
        if node_data.get('is_entrance'):
            details.append("Type: Entrance/Exit")
        if node_data.get('is_stair'):
            details.append("Type: Staircase")
        if 'security_level' in node_data:
            details.append(f"Security: {node_data['security_level']}")
        if node_data.get('is_critical'):
            details.append("Status: Critical Device")
        if 'most_common_next' in node_data:
            details.append(f"Most Common Next: {node_data['most_common_next']}")
        
        return " | ".join(details)


# Factory function for easy component creation
def create_graph_component():
    """Factory function to create graph component instance"""
    return GraphComponent()

# Convenience functions for individual elements (backward compatibility)
def create_graph_container():
    """Create the graph container"""
    component = GraphComponent()
    return component.create_graph_container()

def create_cytoscape_graph():
    """Create just the Cytoscape graph"""
    component = GraphComponent()
    return component.create_cytoscape_graph()