#!/usr/bin/env python
"""
Test script for modular mapping component
"""
import dash
from dash import html

def test_modular_mapping():
    """Test the modular mapping component"""
    
    print("Testing modular mapping component...")
    
    try:
        from ui.core.dependency_injection import configure_services
        from ui.core.component_registry import get_registry
        from ui.components.mapping_modular import register_modular_mapping_component
        print("✅ Imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return None
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    configure_services()
    register_modular_mapping_component()
    registry = get_registry()
    
    app.layout = html.Div([
        html.H1("🗺️ Test Modular Mapping Component", style={'textAlign': 'center', 'margin': '20px 0'}),
        html.Div([
            registry.render('mapping_modular', 'test-mapping')
        ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})
    ])
    
    return app

if __name__ == '__main__':
    app = test_modular_mapping()
    if app:
        print("🚀 Starting mapping component test at http://localhost:8052")
        app.run_server(debug=True, port=8052)
    else:
        print("❌ Test failed")
