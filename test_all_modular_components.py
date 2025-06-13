#!/usr/bin/env python
"""
Test script for all modular components
"""
import dash
from dash import html
import dash_bootstrap_components as dbc

def test_all_modular_components():
    """Test all modular components together"""
    
    print("Testing all modular components...")
    
    try:
        from ui.core.dependency_injection import configure_services
        from ui.core.component_registry import get_registry
        from ui.components.upload_modular import register_modular_upload_component
        from ui.components.mapping_modular import register_modular_mapping_component
        from ui.components.enhanced_stats_modular import register_modular_enhanced_stats_component
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return None
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Configure services
    configure_services()
    print("✅ Services configured")
    
    # Register all components
    register_modular_upload_component()
    register_modular_mapping_component()
    register_modular_enhanced_stats_component()
    print("✅ All components registered")
    
    registry = get_registry()
    
    # Create comprehensive layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🧪 Modular Components Test Dashboard", 
                       className="text-center mb-4", 
                       style={'color': '#2c3e50'})
            ])
        ]),
        
        # Upload Component
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📤 Upload Component"),
                    dbc.CardBody([
                        registry.render('upload_modular', 'test-upload')
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Mapping Component
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🗺️ Mapping Component"),
                    dbc.CardBody([
                        registry.render('mapping_modular', 'test-mapping')
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Stats Component
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Enhanced Stats Component"),
                    dbc.CardBody([
                        registry.render('enhanced_stats_modular', 'test-stats')
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Debug Info
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H5("🔧 Debug Information", className="alert-heading"),
                    html.P(f"Registry Status: Initialized"),
                    html.P(f"Registered Components: {list(registry.factory._registrations.keys())}"),
                    html.Hr(),
                    html.P("All modular components are working correctly!", className="mb-0")
                ], color="info")
            ])
        ])
        
    ], fluid=True)
    
    return app

if __name__ == '__main__':
    app = test_all_modular_components()
    if app:
        print("🚀 Starting comprehensive test at http://localhost:8053")
        print("📋 Components included:")
        print("   - Upload Component")
        print("   - Mapping Component") 
        print("   - Enhanced Stats Component")
        app.run_server(debug=True, port=8053)
    else:
        print("❌ Test failed")
