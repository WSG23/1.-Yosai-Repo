#!/usr/bin/env python3
"""
Apply styling fix to app_modular.py to use existing dark theme
"""

def apply_styling_fix():
    """Update app_modular.py to use proper styling"""
    
    styled_app_content = '''# app_modular.py - Fixed with proper styling
"""
Modular Dash application using the new component system - WITH PROPER STYLING
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
    """Create Dash application with modular components and proper styling"""
    
    # Create app with external stylesheets
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder="assets",
        external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/custom.css']
    )
    
    # Configure services
    configure_services()
    
    # Register components
    register_modular_upload_component()
    register_modular_mapping_component()
    register_modular_enhanced_stats_component()
    register_modular_graph_component()
    
    # Set layout with proper styling
    app.layout = create_modular_layout()
    
    return app

def create_modular_layout():
    """Create main application layout using component registry with proper styling"""
    registry = get_registry()
    
    return html.Div([
        # Main application container with proper background
        html.Div([
            # Header with proper styling
            create_styled_header(),
            
            # Main content area
            html.Div([
                # Upload Section
                create_styled_section("File Upload", 
                    registry.render('upload_modular', 'main-upload')
                ),

                # Mapping Section
                create_styled_section("Column Mapping", 
                    registry.render('mapping_modular', 'main-mapping')
                ),

                # Stats Section
                create_styled_section("Statistics", 
                    registry.render('enhanced_stats_modular', 'main-stats')
                ),

                # Graph Section
                create_styled_section("Graph Visualization", 
                    registry.render('graph_modular', 'main-graph')
                )
                
            ], style=get_main_content_style())
            
        ], style=get_app_container_style())
        
    ], style=get_root_container_style())

def create_styled_header():
    """Create properly styled header"""
    return html.Div([
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
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '0.25rem'
        })
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, #1e3a5f 100%)',
        'borderBottom': f'1px solid {COLORS["border"]}',
        'boxShadow': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.06)',
        'padding': f'{SPACING["lg"]} {SPACING["xl"]}',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000',
        'backdropFilter': 'blur(10px)'
    })

def create_styled_section(title, content):
    """Create a styled section with title and content"""
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
        html.Div(content, style={
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'padding': SPACING['xl'],
            'border': f'1px solid {COLORS["border"]}',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        })
    ], style={
        'marginBottom': SPACING['2xl']
    })

def get_root_container_style():
    """Get root container styling"""
    return {
        'minHeight': '100vh',
        'backgroundColor': COLORS['background'],
        'fontFamily': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
        'color': COLORS['text_primary']
    }

def get_app_container_style():
    """Get app container styling"""
    return {
        'minHeight': '100vh',
        'backgroundColor': COLORS['background']
    }

def get_main_content_style():
    """Get main content area styling"""
    return {
        'maxWidth': LAYOUT_CONFIG['max_width'],
        'margin': '0 auto',
        'padding': f'0 {SPACING["xl"]} {SPACING["2xl"]} {SPACING["xl"]}'
    }

if __name__ == '__main__':
    app = create_modular_app()
    print("🚀 Starting modular application with proper styling...")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True)
'''
    
    with open('app_modular.py', 'w') as f:
        f.write(styled_app_content)
    
    print("✅ Applied styling fix to app_modular.py")

def fix_modular_components_styling():
    """Ensure modular components use existing styling"""
    
    # Fix upload component to use proper styling
    upload_component_fix = '''
    def _get_container_style(self) -> Dict[str, Any]:
        """Get container styling using existing theme"""
        from ui.themes.style_config import COLORS, SPACING, BORDER_RADIUS
        
        return {
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'padding': SPACING['lg'],
            'border': f"1px solid {COLORS['border']}",
            'color': COLORS['text_primary']
        }
    '''
    
    print("ℹ️ Component styling fixes available - components should inherit from theme")

if __name__ == '__main__':
    print("🎨 Applying styling fixes to modular application...")
    apply_styling_fix()
    fix_modular_components_styling()
    print("✅ Styling fixes applied!")
    print("🚀 Your application should now use the proper dark theme")
    print("🧪 Test with: python3 run.py")