# app_modular.py - New modular application bootstrap
"""
Modular Dash application using the new component system
"""
import dash
from dash import html
import dash_bootstrap_components as dbc

# Core infrastructure
from ui.core.dependency_injection import configure_services
from ui.core.component_registry import get_registry

# Component registrations
from ui.components.upload_modular import register_modular_upload_component
from ui.components.mapping_modular import register_modular_mapping_component
from ui.components.enhanced_stats_modular import register_modular_enhanced_stats_component
from ui.components.graph_modular import register_modular_graph_component

def create_modular_app():
    """Create Dash application with modular components"""
    
    # Create app
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder="assets",
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Configure services
    configure_services()
    
    # Register components
    register_modular_upload_component()
    register_modular_mapping_component()
    register_modular_enhanced_stats_component()
    register_modular_graph_component()
    
    # Set layout
    app.layout = create_modular_layout()
    
    return app

def create_modular_layout():
    """Create main application layout using component registry"""
    registry = get_registry()
    
    return html.Div([
        # Header
        html.Div([
            html.H1("Modular Dashboard", style={'textAlign': 'center', 'margin': '20px 0'})
        ]),
        
        # Upload Section
        html.Div([
            html.H2("File Upload"),
            registry.render('upload_modular', 'main-upload')
        ], style={'margin': '20px 0'}),

        # Mapping Section
        html.Div([
            html.H2("Column Mapping"),
            registry.render('mapping_modular', 'main-mapping')
        ], style={'margin': '20px 0'}),

        # Stats Section
        html.Div([
            html.H2("Statistics"),
            registry.render('enhanced_stats_modular', 'main-stats')
        ], style={'margin': '20px 0'}),

        # Graph Section
        html.Div([
            html.H2("Graph Visualization"),
            registry.render('graph_modular', 'main-graph')
        ], style={'margin': '20px 0'})
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})

if __name__ == '__main__':
    app = create_modular_app()
    print("🚀 Starting modular application...")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True)
