#!/usr/bin/env python3
"""
Quick fix for html.Style error - remove inline CSS injection
"""

def fix_html_style_error():
    """Fix the html.Style error in app_modular.py"""
    
    fixed_app_content = '''# app_modular.py - FIXED html.Style error
"""
Modular Dash application with logo and enforced dark theme
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

# IMPORT EXISTING STYLING
from ui.themes.style_config import COLORS, SPACING, BORDER_RADIUS, LAYOUT_CONFIG

def create_modular_app():
    """Create Dash application with logo and enforced dark theme"""
    
    # Create app with NO Bootstrap theme to avoid conflicts
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder="assets",
        external_stylesheets=['/assets/custom.css']  # Only our custom CSS
    )
    
    # Configure services
    configure_services()
    
    # Register components
    register_modular_upload_component()
    register_modular_mapping_component()
    register_modular_enhanced_stats_component()
    register_modular_graph_component()
    
    # Set layout with logo and dark styling
    app.layout = create_dark_layout()
    
    return app

def create_dark_layout():
    """Create layout with logo and enforced dark theme"""
    registry = get_registry()
    
    return html.Div([
        # Main application container
        html.Div([
            # Header WITH LOGO
            create_header_with_logo(),
            
            # Main content with dark background
            html.Div([
                # Upload Section
                create_dark_section("File Upload", 
                    create_dark_component_wrapper(registry.render('upload_modular', 'main-upload'))
                ),

                # Mapping Section  
                create_dark_section("Column Mapping", 
                    create_dark_component_wrapper(registry.render('mapping_modular', 'main-mapping'))
                ),

                # Stats Section
                create_dark_section("Statistics", 
                    create_dark_component_wrapper(registry.render('enhanced_stats_modular', 'main-stats'))
                ),

                # Graph Section
                create_dark_section("Graph Visualization", 
                    create_dark_component_wrapper(registry.render('graph_modular', 'main-graph'))
                )
                
            ], style=get_main_content_style())
            
        ], style=get_app_container_style())
        
    ], style=get_root_style())

def create_dark_component_wrapper(component):
    """Wrap component with aggressive dark styling"""
    return html.Div([
        component
    ], style={
        'backgroundColor': COLORS['surface'],
        'color': COLORS['text_primary'],
        'borderRadius': BORDER_RADIUS['lg'],
        'padding': SPACING['lg'],
        'border': f'1px solid {COLORS["border"]}',
        'minHeight': '200px'
    }, className="dark-component-wrapper")

def create_header_with_logo():
    """Create header with Yosai logo"""
    return html.Div([
        html.Div([
            html.Div([
                # YOSAI LOGO
                html.Img(
                    src='/assets/logo_white.png',  
                    alt="Yōsai Logo",
                    style={
                        'height': '32px',
                        'width': 'auto',
                        'marginRight': SPACING['lg']
                    }
                ),
                # TITLE TEXT
                html.Div([
                    html.H1("Yōsai Dashboard", style={
                        'margin': '0',
                        'fontSize': '1.875rem',
                        'fontWeight': '700',
                        'color': COLORS['text_on_accent'],
                        'letterSpacing': '-0.025em'
                    }),
                    html.P("Security Analytics Platform", style={
                        'margin': '0',
                        'fontSize': '0.875rem',
                        'color': f"{COLORS['text_on_accent']}cc",
                        'opacity': '0.9'
                    })
                ])
            ], style={
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'display': 'flex',
            'justifyContent': 'flex-start',
            'alignItems': 'center',
            'padding': f'{SPACING["lg"]} {SPACING["xl"]}'
        })
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, #1e3a5f 100%)',
        'borderBottom': f'1px solid {COLORS["border"]}',
        'boxShadow': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    })

def create_dark_section(title, content):
    """Create section with dark styling"""
    return html.Div([
        html.H2(title, style={
            'color': COLORS['text_primary'],
            'fontSize': '1.5rem',
            'fontWeight': '600',
            'marginBottom': SPACING['lg'],
            'borderBottom': f'2px solid {COLORS["accent"]}',
            'paddingBottom': SPACING['sm'],
            'display': 'inline-block'
        }),
        content
    ], style={
        'marginBottom': SPACING['2xl'],
        'backgroundColor': COLORS['background']
    })

def get_root_style():
    """Root styling"""
    return {
        'minHeight': '100vh',
        'backgroundColor': COLORS['background'],
        'fontFamily': "'Inter', sans-serif",
        'color': COLORS['text_primary'],
        'margin': '0',
        'padding': '0'
    }

def get_app_container_style():
    """App container styling"""
    return {
        'minHeight': '100vh', 
        'backgroundColor': COLORS['background']
    }

def get_main_content_style():
    """Main content styling"""
    return {
        'maxWidth': LAYOUT_CONFIG['max_width'],
        'margin': '0 auto',
        'padding': f'0 {SPACING["xl"]} {SPACING["2xl"]} {SPACING["xl"]}',
        'backgroundColor': COLORS['background']
    }

if __name__ == '__main__':
    app = create_modular_app()
    print("🎨 Starting Yōsai Dashboard with logo and dark theme...")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True)
'''
    
    with open('app_modular.py', 'w') as f:
        f.write(fixed_app_content)
    
    print("✅ Fixed html.Style error in app_modular.py")

if __name__ == '__main__':
    print("🔧 Fixing html.Style error...")
    fix_html_style_error()
    print("✅ Error fixed - removed inline CSS injection")
    print("🎨 Dark theme will now rely on custom.css")
    print("🧪 Test with: python3 run.py")
    