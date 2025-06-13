# app_modular.py - FIXED TO MATCH ORIGINAL LAYOUT EXACTLY
"""
Modular Dash application with ORIGINAL layout structure
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

# Core infrastructure
from ui.core.dependency_injection import configure_services
from ui.core.component_registry import get_registry

# Component registrations
from ui.components.upload_modular import register_modular_upload_component
from ui.components.mapping_modular import register_modular_mapping_component
from ui.components.enhanced_stats_modular import register_modular_enhanced_stats_component
from ui.components.graph_modular import register_modular_graph_component

# Import original styling and helpers
from ui.themes.style_config import COLORS, SPACING, BORDER_RADIUS, TYPOGRAPHY
from ui.themes.helpers import get_button_style, get_card_style, get_section_header_style

# Import original components for workflow
from ui.components.classification import create_classification_component
from ui.components.enhanced_stats import create_enhanced_stats_component

def create_modular_app():
    """Create Dash application matching original layout exactly"""
    
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder="assets",
        external_stylesheets=['/assets/custom.css']
    )
    
    # Configure services
    configure_services()
    
    # Register modular components (for future use)
    register_modular_upload_component()
    register_modular_mapping_component()
    register_modular_enhanced_stats_component()
    register_modular_graph_component()
    
    # Use ORIGINAL layout structure
    app.layout = create_original_layout()
    
    return app

def create_original_layout():
    """Create the EXACT original layout structure"""
    
    # Get the original classification component
    classification_component = create_classification_component()
    
    return html.Div([
        # Main Header Bar (ORIGINAL)
        create_main_header_original(),

        # Upload Section (ORIGINAL with proper upload functionality)
        create_upload_section_original(),

        # Interactive Setup Container (ORIGINAL - initially hidden)
        create_interactive_setup_container_original(classification_component),

        # Processing Status (ORIGINAL)
        html.Div(
            id='processing-status',
            style={
                'marginTop': SPACING['md'],
                'color': COLORS['accent'],
                'textAlign': 'center',
                'fontSize': TYPOGRAPHY['text_base'],
                'fontWeight': TYPOGRAPHY['font_medium']
            }
        ),

        # Results Section (ORIGINAL - hidden until processing)
        create_results_section_original(),

        # Data Stores (ORIGINAL)
        create_data_stores_original(),
        
    ], style={
        'backgroundColor': COLORS['background'],
        'padding': SPACING['md'],
        'minHeight': '100vh',
        'fontFamily': 'Inter, system-ui, sans-serif'
    })

def create_main_header_original():
    """Create the ORIGINAL main header with logo"""
    header_style = get_card_style()
    header_style.update({
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'flex-start',
        'padding': f"{SPACING['md']} {SPACING['xl']}",
        'marginBottom': SPACING['xl'],
    })
    
    return html.Div([
        # YOSAI LOGO
        html.Img(
            src='/assets/logo_white.png',  # Original logo path
            style={'height': '40px', 'marginRight': SPACING['base']}
        ),
        # ORIGINAL TITLE
        html.H1(
            "Yōsai Intel Enhanced Analytics Dashboard",
            style={
                'fontSize': TYPOGRAPHY['text_4xl'],
                'margin': '0',
                'color': COLORS['text_primary'],
                'fontWeight': TYPOGRAPHY['font_semibold']
            }
        )
    ], style=header_style)

def create_upload_section_original():
    """Create the ORIGINAL upload section with proper CSV/JSON functionality"""
    return html.Div([
        dcc.Upload(
            id='upload-data',  # ORIGINAL ID - critical for callbacks
            children=html.Div([
                html.Img(
                    id='upload-icon',  # ORIGINAL ID
                    src='/assets/upload_file_csv_icon.png',  # ORIGINAL icon path
                    style={
                        'width': '96px',
                        'height': '96px',
                        'marginBottom': SPACING['base'],
                        'opacity': '0.8'
                    }
                ),
                html.H3(
                    "Drop your CSV or JSON file here",
                    style={
                        'margin': '0',
                        'fontSize': '1.2rem',
                        'fontWeight': TYPOGRAPHY['font_semibold'],
                        'color': COLORS['text_primary'],
                        'marginBottom': SPACING['xs']
                    }
                ),
                html.P(
                    "or click to browse",
                    style={
                        'margin': '0',
                        'fontSize': '0.9rem',
                        'color': COLORS['text_secondary'],
                    }
                ),
            ], style={'textAlign': 'center', 'padding': SPACING['md']}),
            style={
                'width': '70%',
                'maxWidth': '600px',
                'minHeight': '180px',
                'borderRadius': BORDER_RADIUS['xl'],
                'textAlign': 'center',
                'margin': f"0 auto {SPACING['xl']} auto",
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease',
                'border': f'2px dashed {COLORS["border"]}',
                'backgroundColor': COLORS['surface'],
            },
            multiple=False,
            accept='.csv,.json'  # ORIGINAL file types
        )
    ])

def create_interactive_setup_container_original(classification_component):
    """Create the ORIGINAL interactive setup container - initially hidden"""
    return html.Div(
        id='interactive-setup-container',  # ORIGINAL ID
        style={'display': 'none'},  # ORIGINAL - hidden initially
        children=[
            # Step 1: CSV Header Mapping (ORIGINAL)
            create_mapping_section_original(),

            # Step 2 & 3: Entrance Verification Section (ORIGINAL)
            classification_component.create_entrance_verification_section(),

            # Generate Button (ORIGINAL)
            html.Button(
                'Confirm Selections & Generate Analysis',  # ORIGINAL text
                id='confirm-and-generate-button',  # ORIGINAL ID
                n_clicks=0,
                style={
                    **get_button_style(),
                    'width': '100%',
                    'maxWidth': '400px',
                    'margin': f"{SPACING['xl']} auto",
                    'display': 'block',
                    'fontSize': TYPOGRAPHY['text_lg']
                }
            )
        ]
    )

def create_mapping_section_original():
    """Create the ORIGINAL Step 1: Map CSV Headers section"""
    return html.Div(
        id='mapping-ui-section',  # ORIGINAL ID - critical for callbacks
        style={
            'padding': SPACING['lg'],
            'margin': f"0 auto {SPACING['md']} auto",
            'backgroundColor': COLORS['surface'],
            'borderRadius': BORDER_RADIUS['lg'],
            'border': f"1px solid {COLORS['border']}",
            'display': 'none'  # ORIGINAL - hidden until upload
        },
        children=[
            html.H4(
                "Step 1: Map CSV Headers",  # ORIGINAL text
                style=get_section_header_style()
            ),
            html.P(
                "Map your CSV columns to the required fields below:",  # ORIGINAL text
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': '0.9rem',
                    'marginBottom': SPACING['md'],
                    'textAlign': 'center'
                }
            ),

            # Dropdown area (ORIGINAL)
            html.Div(id='dropdown-mapping-area'),  # ORIGINAL ID

            # Confirm button (ORIGINAL)
            html.Button(
                'Confirm Header Mapping',  # ORIGINAL text
                id='confirm-header-map-button',  # ORIGINAL ID
                n_clicks=0,
                style={
                    **get_button_style('success'),
                    'display': 'none',  # ORIGINAL - hidden until dropdowns created
                    'margin': f"{SPACING['md']} auto"
                }
            )
        ]
    )

def create_results_section_original():
    """Create the ORIGINAL results section with actual components - SIMPLIFIED VERSION"""
    
    # Create the enhanced stats component
    stats_component = create_enhanced_stats_component()
    
    return html.Div([
        # Graph Output Container (ORIGINAL with SIMPLE graph components for testing)
        html.Div(
            id='graph-output-container',
            style={'display': 'none'},
            children=[
                # Graph title
                html.H2(
                    "Area Layout Model",
                    id="area-layout-model-title",
                    style={
                        'textAlign': 'center',
                        'color': COLORS['text_primary'],
                        'marginBottom': '20px',
                        'fontSize': '1.8rem'
                    }
                ),
                # SIMPLE graph area for testing
                html.Div(
                    id='cytoscape-graphs-area',
                    style={
                        'width': '100%',
                        'height': '600px',
                        'backgroundColor': COLORS['surface'],
                        'border': f"1px solid {COLORS['border']}",
                        'borderRadius': BORDER_RADIUS['lg'],
                        'margin': f"{SPACING['lg']} auto"
                    },
                    children=[
                        # Basic cytoscape component with minimal config
                        cyto.Cytoscape(
                            id='onion-graph',
                            layout={'name': 'cose'},
                            style={'width': '100%', 'height': '100%'},
                            elements=[],
                            stylesheet=[
                                {
                                    'selector': 'node',
                                    'style': {
                                        'background-color': '#666',
                                        'label': 'data(label)'
                                    }
                                }
                            ]
                        )
                    ]
                ),
                # Node info display
                html.Pre(
                    id='tap-node-data-output',
                    style={
                        'border': f"1px solid {COLORS['border']}",
                        'padding': SPACING['base'],
                        'margin': f"{SPACING['base']} auto",
                        'backgroundColor': COLORS['surface'],
                        'textAlign': 'center',
                        'maxWidth': '800px'
                    },
                    children="Upload a file, map headers, (optionally classify doors), then Confirm & Generate. Tap a node for its details."
                )
            ]
        ),
        
        # Stats Panels Container (ORIGINAL with actual stats)
        html.Div(
            id='stats-panels-container',
            style={'display': 'none'},
            children=[
                stats_component.create_enhanced_stats_container()
            ]
        ),
        
        # Custom Header (ORIGINAL)
        html.Div(
            id='yosai-custom-header',
            style={'display': 'none'}
        )
    ])

def create_data_stores_original():
    """Create the ORIGINAL data stores with correct IDs"""
    return html.Div([
        # Core data stores that callbacks expect
        dcc.Store(id='uploaded-file-store'),  # FIXED: Was 'file-upload-store'
        dcc.Store(id='csv-headers-store'),    # ADDED: Missing store
        dcc.Store(id='column-mapping-store', storage_type='local'),
        dcc.Store(id='all-doors-from-csv-store'),
        dcc.Store(id='manual-door-classifications-store', storage_type='local'),  # ADDED: Missing store
        dcc.Store(id='num-floors-store', data=1),  # ADDED: Missing store
        dcc.Store(id='processed-data-store'),
        dcc.Store(id='status-message-store'),
        dcc.Store(id='device-attributes-store'),
        dcc.Store(id='enhanced-stats-data-store')
    ])

if __name__ == '__main__':
    app = create_modular_app()
    print("🎨 Starting Yōsai Dashboard with ORIGINAL layout...")
    print("📊 CSV/JSON upload functionality restored")
    print("Visit: http://localhost:8050")
    app.run_server(debug=True)