#!/usr/bin/env python
"""
Test script for modular upload component
"""
import dash
from dash import html
from ui.core.dependency_injection import configure_services
from ui.core.component_registry import get_registry
from ui.components.upload_modular import register_modular_upload_component

def test_modular_upload():
    """Test the modular upload component"""
    
    # Create app
    app = dash.Dash(__name__)
    
    # Configure services
    configure_services()
    
    # Register component
    register_modular_upload_component()
    
    # Get registry
    registry = get_registry()
    
    # Create layout
    app.layout = html.Div([
        html.H1("Test Modular Upload Component"),
        registry.render('upload_modular', 'test-upload')
    ])
    
    return app

if __name__ == '__main__':
    app = test_modular_upload()
    print("Testing modular upload component...")
    print("Visit: http://localhost:8051")
    app.run_server(debug=True, port=8051)
