#!/usr/bin/env python3
"""
FINAL COMPLETE FIX: Dark theme + logo + eliminate ALL white backgrounds
"""

def apply_final_complete_fix():
    """Apply the comprehensive fix for dark theme and logo"""
    
    print("🎨 Applying FINAL complete dark theme + logo fix...")
    
    # 1. Update app_modular.py with logo and dark wrappers
    apply_app_modular_fix()
    
    # 2. Update custom.css with aggressive overrides
    apply_aggressive_css_fix()
    
    print("✅ FINAL COMPLETE FIX APPLIED!")
    print("🏛️ Yosai logo added to header")
    print("🎨 ALL white backgrounds eliminated")
    print("🧪 Test with: python3 run.py")

def apply_app_modular_fix():
    """Apply app_modular.py fix with logo and dark wrappers"""
    
    fixed_app_content = '''# app_modular.py - FINAL COMPLETE FIX
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
        # Force dark background on everything
        html.Div([
            # Inject aggressive CSS
            html.Style(children=get_aggressive_dark_css()),
            
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

def get_aggressive_dark_css():
    """Aggressive CSS to eliminate ALL white backgrounds"""
    return f"""
    /* ELIMINATE ALL WHITE BACKGROUNDS */
    html, body, #_dash-app-content {{
        background-color: {COLORS['background']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Force dark on ALL component containers */
    div, span {{
        background-color: inherit !important;
    }}
    
    .dark-component-wrapper, .dark-component-wrapper * {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    /* Override any white backgrounds */
    [style*="background-color: white"], 
    [style*="background-color: #fff"],
    [style*="background: white"] {{
        background-color: {COLORS['surface']} !important;
    }}
    
    /* Force dark on specific components */
    [id*="upload"], [id*="mapping"], [id*="stats"], [id*="graph"] {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    .dash-upload, .dash-upload-area {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text_primary']} !important;
        border-color: {COLORS['border']} !important;
    }}
    """

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
    
    print("✅ Updated app_modular.py with logo and dark wrappers")

def apply_aggressive_css_fix():
    """Apply aggressive CSS fix to eliminate white backgrounds"""
    
    # Read current custom.css
    try:
        with open('assets/custom.css', 'r') as f:
            current_css = f.read()
    except FileNotFoundError:
        current_css = ""
    
    # Aggressive CSS overrides
    aggressive_css = """
/* AGGRESSIVE DARK THEME ENFORCEMENT - ELIMINATE ALL WHITE */

/* Force dark on everything */
html, body, #_dash-app-content, ._dash-app-content, .dash-app-content {
  background-color: #0F1419 !important;
  color: #F7FAFC !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Force dark on ALL divs and containers */
div, span, section, article, main {
  background-color: inherit !important;
}

/* Force dark on ALL component wrappers */
.dark-component-wrapper {
  background-color: #1A2332 !important;
  color: #F7FAFC !important;
}

.dark-component-wrapper * {
  background-color: inherit !important;
  color: inherit !important;
}

/* Override any component that might be white */
[class*="component"], [id*="component"], 
[class*="upload"], [id*="upload"],
[class*="mapping"], [id*="mapping"],
[class*="stats"], [id*="stats"],
[class*="graph"], [id*="graph"] {
  background-color: #1A2332 !important;
  color: #F7FAFC !important;
}

/* Force dark on Dash Upload components */
.dash-upload, .dash-upload-area, .dash-upload-content {
  background-color: #1A2332 !important;
  color: #F7FAFC !important;
  border-color: #2D3748 !important;
}

/* Force dark on forms */
input, textarea, select, .form-control, .form-select {
  background-color: #1A2332 !important;
  color: #F7FAFC !important;
  border-color: #2D3748 !important;
}

/* Force dark on Bootstrap */
.container, .container-fluid, .row, .col {
  background-color: #0F1419 !important;
}

.card, .card-body, .card-header {
  background-color: #1A2332 !important;
  border-color: #2D3748 !important;
  color: #F7FAFC !important;
}

.btn {
  border-color: #2D3748 !important;
  color: #F7FAFC !important;
}

.btn-primary {
  background-color: #2196F3 !important;
  border-color: #2196F3 !important;
}

.alert {
  border-color: #2D3748 !important;
  background-color: #1A2332 !important;
  color: #F7FAFC !important;
}

/* Override any inline white backgrounds */
[style*="background-color: white"], 
[style*="background-color: #fff"],
[style*="background-color: #ffffff"],
[style*="background: white"],
[style*="background: #fff"],
[style*="background: #ffffff"] {
  background-color: #1A2332 !important;
}

""" + current_css
    
    with open('assets/custom.css', 'w') as f:
        f.write(aggressive_css)
    
    print("✅ Updated custom.css with aggressive dark theme overrides")

if __name__ == '__main__':
    apply_final_complete_fix()