# ui/pages/main_page.py - FIXED VERSION - Removes UI Conflicts

"""
Main page layout - STREAMLINED AND CONFLICT-FREE
All callbacks are handled by unified handler in app.py
"""

from dash import html, dcc
from ui.components.classification import create_classification_component

from ui.themes.style_config import COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS
from ui.themes.helpers import (
    get_button_style,
    get_card_style,
    get_card_container_style,
    get_section_header_style,
)

# Fallback constants
REQUIRED_INTERNAL_COLUMNS = {
    'Timestamp': 'Timestamp (Event Time)',
    'UserID': 'UserID (Person Identifier)',
    'DoorID': 'DoorID (Device Name)',
    'EventType': 'EventType (Access Result)'
}


# Instantiate the reusable classification component for entrance verification
classification_component = create_classification_component()

def create_main_layout(app_instance, main_logo_path, icon_upload_default):
    """
    Creates the main application layout - STREAMLINED VERSION
    """
    
    layout = html.Div(
        children=[
            # Main Header Bar
            create_main_header(main_logo_path),

            # Upload Section - SIMPLIFIED
            create_upload_section(icon_upload_default),

            # Interactive Setup Container - SIMPLIFIED
            create_interactive_setup_container(),

            # Processing Status
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

            # Results Section - HIDDEN until processing
            create_results_section(),

            # Data Stores
            create_data_stores(),
        ],
        style={
            'backgroundColor': COLORS['background'],
            'padding': SPACING['md'],
            'minHeight': '100vh',
            'fontFamily': 'Inter, system-ui, sans-serif'
        }
    )

    return layout

def create_main_header(main_logo_path):
    """Creates the main header bar"""
    header_style = get_card_style()
    header_style.update({
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'flex-start',
        'padding': f"{SPACING['md']} {SPACING['xl']}",
        'marginBottom': SPACING['xl'],
    })
    return html.Div(
        style=header_style,
        children=[
            html.Img(src=main_logo_path, style={'height': '40px', 'marginRight': SPACING['base']}),
            html.H1(
                "Yōsai Intel Enhanced Analytics Dashboard",
                style={
                    'fontSize': TYPOGRAPHY['text_4xl'],
                    'margin': '0',
                    'color': COLORS['text_primary'],
                    'fontWeight': TYPOGRAPHY['font_semibold']
                }
            )
        ]
    )

def create_upload_section(icon_upload_default):
    """Upload section - SIMPLIFIED"""
    return html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                html.Img(
                    id='upload-icon',
                    src=icon_upload_default,
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
            accept='.csv,.json'
        )
    ])

def create_interactive_setup_container():
    """Interactive setup container - SIMPLIFIED"""
    return html.Div(
        id='interactive-setup-container',
        style={'display': 'none'},
        children=[
            # Step 1: CSV Header Mapping
            create_mapping_section(),

            # Step 2 & 3: Entrance Verification Section (facility setup and classification)
            classification_component.create_entrance_verification_section(),

            # Generate Button
            html.Button(
                'Confirm Selections & Generate Analysis',
                id='confirm-and-generate-button',
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

def create_mapping_section():
    """Step 1: Map CSV Headers (wrapped in mapping-ui-section for callback control)"""
    return html.Div(
        id='mapping-ui-section',  # ✅ Enables callback to toggle visibility
        style={**get_card_container_style(padding=SPACING['lg'], margin_bottom=SPACING['md']), 'display': 'none'},
        children=[
            html.H4(
                "Step 1: Map CSV Headers",
                style=get_section_header_style()
            ),
            html.P(
                "Map your CSV columns to the required fields below:",
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': '0.9rem',
                    'marginBottom': SPACING['md'],
                    'textAlign': 'center'
                }
            ),

            # Dropdown area
            html.Div(id='dropdown-mapping-area'),

            # Confirm button
            html.Button(
                'Confirm Header Mapping',
                id='confirm-header-map-button',
                n_clicks=0,
                style={
                    **get_button_style('success'),
                    'display': 'none',  # Hidden until dropdowns are created
                    'margin': f"{SPACING['md']} auto"
                }
            )
        ]
    )

def create_facility_setup():
    """Step 2: Facility Setup"""
    return html.Div([
        html.H4(
            "Step 2: Facility Setup",
            style=get_section_header_style()
        ),
        
        # Number of floors
        html.Div([
            html.Label(
                "How many floors are in the facility?",
                style={
                    'color': COLORS['text_primary'],
                    'fontWeight': TYPOGRAPHY['font_semibold'],
                    'fontSize': '1rem',
                    'marginBottom': SPACING['sm'],
                    'display': 'block',
                    'textAlign': 'center'
                }
            ),
            dcc.Slider(
                id="floor-slider",
                min=1,
                max=20,
                step=1,
                value=4,
                marks={i: str(i) for i in range(0, 101, 5)},
                tooltip={"always_visible": False, "placement": "bottom"}
            ),
            html.Div(
                id="floor-slider-value",
                children="4 floors",
                style={
                    "fontSize": "0.9rem",
                    "color": COLORS['text_secondary'],
                    "marginTop": SPACING['sm'],
                    "textAlign": "center",
                    "fontWeight": TYPOGRAPHY['font_semibold']
                }
            ),
        ], style={'marginBottom': SPACING['md']}),
        
        # Manual classification toggle
        html.Div([
            html.Label(
                "Enable Manual Door Classification?",
                style={
                    'color': COLORS['text_primary'],
                    'fontWeight': TYPOGRAPHY['font_semibold'],
                    'fontSize': '1rem',
                    'marginBottom': SPACING['base'],
                    'display': 'block',
                    'textAlign': 'center'
                }
            ),
            dcc.RadioItems(
                id='manual-map-toggle',
                options=[
                    {'label': ' No (Automatic)', 'value': 'no'},
                    {'label': ' Yes (Manual)', 'value': 'yes'}
                ],
                value='no',
                inline=True,
                style={'textAlign': 'center'},
                labelStyle={
                    'display': 'inline-block',
                    'marginRight': SPACING['md'],
                    'padding': f"{SPACING['sm']} {SPACING['lg']}",
                    'backgroundColor': COLORS['border'],
                    'color': COLORS['text_secondary'],
                    'borderRadius': BORDER_RADIUS['full'],
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease'
                }
            ),
        ])
    ], style=get_card_container_style(padding=SPACING['lg'], margin_bottom=SPACING['md']))

def create_classification_section():
    """Step 3: Door Classification (conditional)"""
    return html.Div(
        id="door-classification-table-container",
        style={'display': 'none'},
        children=[
            html.Div([
                html.H4(
                    "Step 3: Door Classification",
                    style=get_section_header_style()
                ),
                html.P(
                    "Classify each door below:",
                    style={
                        'color': COLORS['text_secondary'],
                        'marginBottom': SPACING['md'],
                        'textAlign': 'center'
                    }
                ),
                html.Div(id="door-classification-table")
            ], style=get_card_container_style(padding=SPACING['lg'], margin_bottom='0'))
        ]
    )

def create_results_section():
    """Results section - hidden until processing complete"""
    return html.Div([
        # Custom Header (hidden)
        html.Div(
            id='yosai-custom-header',
            style={'display': 'none'},
            children=[
                html.Div([
                    html.H2(
                        "📊 Analysis Results",
                        style={
                            'color': COLORS['text_primary'],
                            'textAlign': 'center',
                            'margin': '0',
                            'fontSize': TYPOGRAPHY['text_2xl']
                        }
                    )
                ], style=get_card_container_style(padding=SPACING['lg'], margin_bottom=SPACING['md']))
            ]
        ),

        # Statistics Panels (hidden)
        create_stats_panels(),

        # Graph Container (hidden)
        # Removed duplicate onion graph component. The graph
        # container from ``ui.components.graph`` will be added
        # by the application layout.

        # Analytics Section (initially hidden)
        html.Div(
            id='analytics-section',
            style={'display': 'none'},
            children=[
                html.H2("📈 Advanced Analytics", style={'textAlign': 'center'}),
                html.Div(id='analytics-detailed-breakdown')
            ]
        ),

        # Charts Section (hidden until data is ready)
        html.Div(
            id='charts-section',
            style={'display': 'none'},
            children=[
                html.H2("📊 Data Visualization", style={'textAlign': 'center'})
            ]
        ),

        # Export Section (hidden until data is ready)
        html.Div(
            id='export-section',
            style={'display': 'none'},
            children=[
                html.H2("📤 Export & Reports", style={'textAlign': 'center'})
            ]
        )
    ])


def create_stats_panels():
    """Statistics panels"""
    panel_style = get_card_container_style(padding=SPACING['lg'], margin_bottom='0')
    panel_style.update({
        'flex': '1',
        'margin': f"0 {SPACING['sm']}",
        'textAlign': 'center',
        'minWidth': '200px'
    })

    return html.Div(
        id='stats-panels-container',
        style={'display': 'none'},
        children=[
            # Access Events Panel
            html.Div([
                html.H3("Access Events", style={'color': COLORS['text_primary'], 'marginBottom': SPACING['sm']}),
                html.H1(id="total-access-events-H1", style={'color': COLORS['accent'], 'margin': f"{SPACING['sm']} 0"}),
                html.P(id="event-date-range-P", style={'color': COLORS['text_secondary'], 'fontSize': '0.9rem'}),
                html.Table([html.Tbody(id='most-active-devices-table-body')])
            ], style=panel_style),

            # User Analytics Panel
            html.Div([
                html.H3("User Analytics", style={'color': COLORS['text_primary'], 'marginBottom': SPACING['sm']}),
                html.P(id="stats-unique-users", style={'color': COLORS['text_secondary']}),
                html.P(id="stats-avg-events-per-user", style={'color': COLORS['text_secondary']}),
                html.P(id="stats-most-active-user", style={'color': COLORS['text_secondary']}),
                html.P(id="stats-devices-per-user", style={'color': COLORS['text_secondary']}),
                html.P(id="stats-peak-hour", style={'color': COLORS['text_secondary']}),
                html.P(id="total-devices-count", style={'color': COLORS['text_secondary']}),
                html.P(id="entrance-devices-count", style={'color': COLORS['text_secondary']}),
                html.P(id="high-security-devices", style={'color': COLORS['text_secondary']})
            ], style=panel_style),

            # Activity & Security Panel
            html.Div([
                html.H3("Activity & Security", style={'color': COLORS['text_primary'], 'marginBottom': SPACING['sm']}),
                html.P(id="peak-hour-display", style={'color': COLORS['text_secondary']}),
                html.P(id="peak-day-display", style={'color': COLORS['text_secondary']}),
                html.P(id="busiest-floor", style={'color': COLORS['text_secondary']}),
                html.P(id="entry-exit-ratio", style={'color': COLORS['text_secondary']}),
                html.P(id="weekend-vs-weekday", style={'color': COLORS['text_secondary']}),
                html.Div(id="security-level-breakdown", style={'color': COLORS['text_secondary']}),
                html.P(id="compliance-score", style={'color': COLORS['text_secondary']}),
                html.P(id="anomaly-alerts", style={'color': COLORS['text_secondary']})
            ], style=panel_style)
        ]
    )


def create_data_stores():
    """Create all data store components"""
    return html.Div([
        dcc.Store(id='uploaded-file-store'),
        dcc.Store(id='csv-headers-store'),
        dcc.Store(id='column-mapping-store', storage_type='local'),
        dcc.Store(id='all-doors-from-csv-store'),
        dcc.Store(id='manual-door-classifications-store', storage_type='local'),
        dcc.Store(id='num-floors-store', data=1),
        # Store for processing status messages so a single callback can
        # update the visible status component
        dcc.Store(id='status-message-store'),
    ])
