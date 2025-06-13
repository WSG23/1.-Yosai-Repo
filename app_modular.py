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
    # TODO: Register other components as they are migrated
    
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
        
        # Upload Section (using modular component)
        html.Div([
            html.H2("File Upload"),
            registry.render('upload_modular', 'main-upload')
        ], style={'margin': '20px 0'}),
        
        # Placeholder for other sections
        html.Div([
            html.H2("Other Components"),
            html.P("Other components will be added here as they are migrated...")
        ], style={'margin': '20px 0', 'padding': '20px', 'backgroundColor': '#f8f9fa'})
        
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})

if __name__ == '__main__':
    app = create_modular_app()
    print("🚀 Starting modular application...")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True)