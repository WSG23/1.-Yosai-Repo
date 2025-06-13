# ui/components/graph_modular.py
"""
Modular graph visualization component using the new architecture
"""
from typing import Dict, Any, Optional
from dash import html, dcc, no_update, Input, Output, State
import dash
import dash_cytoscape as cyto

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.config_manager import get_component_config
from ui.themes.graph_styles import (
    centered_graph_box_style,
    cytoscape_inside_box_style,
    tap_node_data_centered_style,
    actual_default_stylesheet_for_graph,
)

class ModularGraphComponent(StatefulComponent):
    """Modular graph component with dynamic IDs"""

    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.graph_id = f"{self.component_id}-graph"
        self.info_id = f"{self.component_id}-info"
        self.layout_id = f"{self.component_id}-layout"
        self.filter_id = f"{self.component_id}-filters"
        self.export_png_id = f"{self.component_id}-export-png"
        self.download_png_id = f"{self.component_id}-download-png"
        self.export_json_id = f"{self.component_id}-export-json"
        self.download_json_id = f"{self.component_id}-download-json"
        self.props = kwargs
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

        def _validate_config(self) -> None:


            """Validate required configuration - Fixed to handle missing settings gracefully"""


            required_settings = ['default_layout', 'show_labels', 'interactive', 'node_size']
        


            for setting in required_settings:


                if self.get_setting(setting) is None:


                    print(f"Warning: Missing setting '{setting}', using defaults")


                    # Set default values instead of raising errors


                    defaults = {'default_layout': 'cose', 'show_labels': True, 'interactive': True, 'node_size': 20}


                    if setting in defaults:


                        self.config.settings[setting] = defaults[setting]

    def render(self, **props) -> html.Div:
        """Render the graph component"""
        return html.Div([
            html.H3("Network Graph", style={'margin': '16px 0', 'color': '#2c3e50'}),
            self._create_controls(),
            self._create_graph_area(),
            self._create_node_info_display(),
        ], id=self.component_id, style=self._get_container_style())

    def _create_controls(self) -> html.Div:
        return html.Div([
            html.Label("Layout Algorithm:", style={'marginRight': '8px'}),
            dcc.Dropdown(
                id=self.layout_id,
                options=[
                    {'label': 'COSE (Force-directed)', 'value': 'cose'},
                    {'label': 'Circle', 'value': 'circle'},
                    {'label': 'Grid', 'value': 'grid'},
                    {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                    {'label': 'Concentric', 'value': 'concentric'},
                ],
                value=self.get_setting('layout_algorithm', 'cose'),
                style={'width': '200px', 'display': 'inline-block', 'marginRight': '12px'}
            ),
            dcc.Checklist(
                id=self.filter_id,
                options=[
                    {'label': ' Show Entrances Only', 'value': 'entrances_only'},
                    {'label': ' Show Critical Paths', 'value': 'critical_paths'},
                    {'label': ' Hide Low Security', 'value': 'hide_low_security'}
                ],
                value=[],
                style={'display': 'inline-block'}
            ),
            html.Button("Export PNG", id=self.export_png_id, style={'marginLeft': '12px'}),
            dcc.Download(id=self.download_png_id),
            html.Button("Export JSON", id=self.export_json_id, style={'marginLeft': '8px'}),
            dcc.Download(id=self.download_json_id)
        ], style={'margin': '16px 0'})

    def _create_graph_area(self) -> html.Div:
        return html.Div([
            cyto.Cytoscape(
                id=self.graph_id,
                layout=self.default_layout,
                style=cytoscape_inside_box_style,
                elements=[],
                stylesheet=actual_default_stylesheet_for_graph,
                wheelSensitivity=1,
            )
        ], style=centered_graph_box_style)

    def _create_node_info_display(self) -> html.Pre:
        return html.Pre(
            id=self.info_id,
            style=tap_node_data_centered_style,
            children="Upload a file, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
        )

    def _get_container_style(self) -> Dict[str, Any]:
        base_style = {
            'margin': '20px 0',
            'padding': '20px',
            'borderRadius': '8px',
            'backgroundColor': '#ffffff',
            'border': '1px solid #e5e7eb',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
        return {**base_style, **self.get_style('container')}

    def register_callbacks(self, app: dash.Dash) -> None:
        @app.callback(
            Output(self.info_id, 'children'),
            Input(self.graph_id, 'tapNodeData'),
            prevent_initial_call=True
        )
        def display_node_data(data):
            if not data:
                return no_update
            return self.format_node_details(data)

    def get_layout_options(self) -> Dict[str, Any]:
        return {
            'cose': self.default_layout,
            'circle': {'name': 'circle'},
            'grid': {'name': 'grid'},
            'breadthfirst': {'name': 'breadthfirst'},
            'concentric': {'name': 'concentric'},
        }

    def format_node_details(self, node_data):
        if not node_data or node_data.get('is_layer_parent'):
            return "Upload a file, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
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


def create_modular_graph_component(component_id: Optional[str] = None, **props):
    config = get_component_config('graph')
    return ModularGraphComponent(config, component_id, **props)


def register_modular_graph_component():
    from ui.core.component_registry import register_component
    register_component('graph_modular', ModularGraphComponent)
