"""
ui/pages/main_page.py - PERMANENT FIX VERSION
Main page layout with proper enhanced stats integration
"""

from dash import html, dcc
from ui.themes.style_config import COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS
from ui.themes.helpers import (
    get_button_style,
    get_card_style,
    get_card_container_style,
    get_section_header_style,
)

# Import enhanced stats component
try:
    from ui.components.enhanced_stats import EnhancedStatsComponent
    ENHANCED_STATS_AVAILABLE = True
except ImportError:
    ENHANCED_STATS_AVAILABLE = False

try:
    from ui.components.classification import create_classification_component
    classification_component = create_classification_component()
except ImportError:
    classification_component = None

# Fallback constants
REQUIRED_INTERNAL_COLUMNS = {
    'Timestamp': 'Timestamp (Event Time)',
    'UserID': 'UserID (Person Identifier)',
    'DoorID': 'DoorID (Device Name)',
    'EventType': 'EventType (Access Result)'
}

def create_main_layout(app_instance, main_logo_path, icon_upload_default):
    """
    Creates the main application layout with proper enhanced stats integration
    PERMANENT FIX - includes all required components for callbacks
    """
    
    # Create enhanced stats component if available
    enhanced_stats = None
    if ENHANCED_STATS_AVAILABLE:
        enhanced_stats = EnhancedStatsComponent()
    
    layout = html.Div(
        children=[
            # Main Header Bar
            create_main_header(main_logo_path),

            # Upload Section
            create_upload_section(icon_upload_default),

            # Interactive Setup Container
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

            # PERMANENT FIX: Enhanced Stats Section with all required components
            create_enhanced_stats_section(enhanced_stats),

            # Results Section - HIDDEN until processing
            create_results_section(),

            # Data Stores
            create_data_stores(),
            
            # PERMANENT FIX: Additional required stores for enhanced stats
            create_enhanced_data_stores(),
        ],
        style={
            'backgroundColor': COLORS['background'],
            'minHeight': '100vh',
            'fontFamily': TYPOGRAPHY['font_family']
        }
    )
    
    return layout

def create_enhanced_stats_section(enhanced_stats=None):
    """
    PERMANENT FIX: Create enhanced stats section with all required components
    """
    if enhanced_stats:
        # Use the full enhanced stats component
        return html.Div(
            id='enhanced-stats-section',
            style={'display': 'none'},  # Hidden until data is loaded
            children=[
                enhanced_stats.create_enhanced_stats_container()
            ]
        )
    else:
        # Fallback with all required IDs for callbacks
        return html.Div(
            id='enhanced-stats-section',
            style={'display': 'none'},
            children=[
                # Core row with sidebar (required by callback)
                html.Div(
                    id="core-row-with-sidebar",
                    style={
                        "display": "flex",
                        "width": "90%",
                        "margin": "0 auto 30px auto",
                    },
                    children=[
                        html.Div(
                            id="row1-main-panels",
                            style={"flex": "1"},
                            children=[
                                create_fallback_stats_panels()
                            ]
                        )
                    ]
                ),
                
                # Advanced analytics container (required by callback)
                html.Div(
                    id="advanced-analytics-panels-container",
                    style={
                        "display": "flex",
                        "justifyContent": "space-around",
                        "marginBottom": "30px",
                        "width": "90%",
                        "margin": "0 auto 30px auto",
                    },
                    children=[
                        create_fallback_peak_activity_panel(),
                        create_fallback_security_panel(),
                        create_fallback_charts_section(),
                    ]
                )
            ]
        )

def create_fallback_stats_panels():
    """Create fallback stats panels with all required IDs"""
    panel_style = get_card_container_style(padding=SPACING['lg'], margin_bottom='0')
    panel_style.update({
        'flex': '1',
        'margin': f"0 {SPACING['sm']}",
        'textAlign': 'center',
        'minWidth': '200px'
    })

    return html.Div([
        # Access Events Panel
        html.Div([
            html.H3("Access Events", style={'color': COLORS['text_primary']}),
            html.H1(id="total-access-events-H1", children="0", style={'color': COLORS['accent']}),
            html.H1(id="enhanced-total-access-events-H1", children="0", style={'color': COLORS['accent']}),
            html.P(id="event-date-range-P", children="No data", style={'color': COLORS['text_secondary']}),
            html.P(id="enhanced-event-date-range-P", children="No data", style={'color': COLORS['text_secondary']}),
            html.Div(id="events-trend-indicator", children=""),
            html.P(id="avg-events-per-day", children=""),
            html.Table([html.Tbody(id='most-active-devices-table-body')])
        ], style=panel_style),

        # User Analytics Panel
        html.Div([
            html.H3("User Analytics", style={'color': COLORS['text_primary']}),
            html.P(id="stats-unique-users", children="Users: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="unique-users-today", children="Users Today: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-avg-events-per-user", children="Avg: 0 events/user", style={'color': COLORS['text_secondary']}),
            html.P(id="avg-user-activity", children="Avg Activity: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-most-active-user", children="Most Active: N/A", style={'color': COLORS['text_secondary']}),
            html.P(id="most-active-user", children="Most Active: N/A", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-devices-per-user", children="Devices/User: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-peak-hour", children="Peak: N/A", style={'color': COLORS['text_secondary']}),
        ], style=panel_style),

        # Device Panel
        html.Div([
            html.H3("Device Analytics", style={'color': COLORS['text_primary']}),
            html.P(id="total-devices-count", children="Total: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="entrance-devices-count", children="Entrances: 0", style={'color': COLORS['text_secondary']}),
            html.P(id="high-security-devices", children="High Security: 0", style={'color': COLORS['text_secondary']}),
        ], style=panel_style)
    ], style={'display': 'flex', 'justifyContent': 'space-around'})

def create_fallback_peak_activity_panel():
    """Create fallback peak activity panel with all required IDs"""
    panel_style = get_card_container_style(padding=SPACING['lg'])
    panel_style.update({
        'flex': '1',
        'margin': f"0 {SPACING['sm']}",
        'textAlign': 'center'
    })
    
    return html.Div([
        html.H3("Peak Activity", style={'color': COLORS['text_primary']}),
        html.P(id="peak-hour-display", children="Peak Hour: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="peak-day-display", children="Peak Day: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="peak-activity-events", children="Peak Activity: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="busiest-floor", children="Busiest Floor: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="entry-exit-ratio", children="Entry/Exit: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="weekend-vs-weekday", children="Weekend vs Weekday: N/A", style={'color': COLORS['text_secondary']})
    ], style=panel_style)

def create_fallback_security_panel():
    """Create fallback security panel"""
    panel_style = get_card_container_style(padding=SPACING['lg'])
    panel_style.update({
        'flex': '1',
        'margin': f"0 {SPACING['sm']}",
        'textAlign': 'center'
    })
    
    return html.Div([
        html.H3("Security Overview", style={'color': COLORS['text_primary']}),
        html.Div(id="security-level-breakdown", children=[
            html.P("Security analysis loading...", style={'color': COLORS['text_secondary']})
        ]),
        html.P(id="compliance-score", children="Compliance: N/A", style={'color': COLORS['text_secondary']}),
        html.P(id="anomaly-alerts", children="Anomalies: 0", style={'color': COLORS['text_secondary']})
    ], style=panel_style)

def create_fallback_charts_section():
    """Create fallback charts section"""
    panel_style = get_card_container_style(padding=SPACING['lg'])
    panel_style.update({
        'flex': '1',
        'margin': f"0 {SPACING['sm']}",
        'textAlign': 'center'
    })
    
    return html.Div([
        html.H3("Analytics", style={'color': COLORS['text_primary']}),
        html.Div(id="main-analytics-chart", children="Charts loading..."),
        html.Div(id="security-pie-chart"),
        html.Div(id="heatmap-chart"),
        dcc.Dropdown(
            id="chart-type-selector",
            options=[
                {'label': 'Activity Timeline', 'value': 'timeline'},
                {'label': 'Device Usage', 'value': 'device_usage'},
                {'label': 'Security Distribution', 'value': 'security'}
            ],
            value='timeline',
            style={'marginTop': '10px', 'color': '#000'}
        )
    ], style=panel_style)

def create_enhanced_data_stores():
    """Create additional data stores required for enhanced stats"""
    return html.Div([
        dcc.Store(id='enhanced-stats-data-store'),
        dcc.Store(id='chart-data-store'),
        dcc.Store(id='status-message-store'),
        dcc.Interval(
            id='stats-refresh-interval',
            interval=30*1000,  # 30 seconds
            n_intervals=0,
            disabled=True
        )
    ])

def create_main_header(main_logo_path):
    """Create main header with logo"""
    return html.Div(
        id='yosai-custom-header',
        children=[
            html.Img(
                src=main_logo_path,
                style={
                    'height': '50px',
                    'marginRight': SPACING['md']
                }
            ),
            html.H1(
                'Yōsai Enhanced Analytics Dashboard',
                style={
                    'color': COLORS['text_primary'],
                    'margin': '0',
                    'fontSize': TYPOGRAPHY['text_2xl'],
                    'fontWeight': TYPOGRAPHY['font_bold']
                }
            ),
            # Enhanced stats header controls
            html.Div(
                id="enhanced-stats-header",
                children=[
                    html.Button("Export Stats", id="export-stats-btn", className="btn btn-primary", style={'marginRight': '10px'}),
                    html.Button("Refresh", id="refresh-stats-btn", className="btn btn-secondary", style={'marginRight': '10px'}),
                    dcc.Checklist(
                        id="real-time-toggle",
                        options=[{"label": " Real-time", "value": "enabled"}],
                        value=[],
                        style={'color': COLORS['text_primary']}
                    )
                ],
                style={'display': 'flex', 'alignItems': 'center'}
            )
        ],
        style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'padding': f"{SPACING['lg']} {SPACING['xl']}",
            'backgroundColor': COLORS['surface'],
            'borderBottom': f"1px solid {COLORS['border']}"
        }
    )

def create_upload_section(icon_upload_default):
    """Create upload section"""
    return html.Div(
        children=[
            html.H2(
                "📊 Upload Your Access Control Data",
                style=get_section_header_style()
            ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.Img(
                        id='upload-icon',
                        src=icon_upload_default,
                        style={'height': '50px', 'marginRight': SPACING['md']}
                    ),
                    html.Div([
                        html.P("Drag and Drop or Click to Select Files", style={'margin': '0', 'fontWeight': 'bold'}),
                        html.P("Supported: CSV files", style={'margin': '0', 'fontSize': '0.9rem', 'color': COLORS['text_secondary']})
                    ])
                ]),
                style=get_card_style(),
                multiple=False
            )
        ],
        style={'textAlign': 'center', 'margin': f"{SPACING['xl']} 0"}
    )

def create_interactive_setup_container():
    """Create interactive setup container"""
    return html.Div(
        id='interactive-setup-container',
        style={'display': 'none'},
        children=[
            # Column Mapping Section
            html.Div(
                id='mapping-ui-section',
                style={'display': 'none'},
                children=[
                    html.H3("🔗 Map Your CSV Columns", style=get_section_header_style()),
                    html.Div(id='dropdown-mapping-area'),
                    html.Button(
                        'Confirm Column Mapping',
                        id='confirm-header-map-button',
                        n_clicks=0,
                        className='btn btn-primary',
                        style=get_button_style()
                    )
                ]
            ),
            
            # Entrance Verification Section
            html.Div(
                id='entrance-verification-ui-section',
                style={'display': 'none'},
                children=[
                    html.H3("🚪 Configure Building Layout", style=get_section_header_style()),
                    html.Div([
                        html.Label("Number of Floors:", style={'fontWeight': 'bold', 'color': COLORS['text_primary']}),
                        dcc.Slider(
                            id='floor-slider',
                            min=1,
                            max=10,
                            value=1,
                            marks={i: str(i) for i in range(1, 11)},
                            step=1
                        ),
                        html.Div(id='floor-slider-value', style={'textAlign': 'center', 'marginTop': '10px'})
                    ], style={'margin': f"{SPACING['lg']} 0"}),
                    
                    dcc.Checklist(
                        id='manual-map-toggle',
                        options=[{'label': ' Manual Door Classification', 'value': 'enabled'}],
                        value=[],
                        style={'margin': f"{SPACING['md']} 0"}
                    ),
                    
                    html.Div(id='door-classification-table-container'),
                    
                    html.Button(
                        'Generate Enhanced Analytics',
                        id='confirm-and-generate-button',
                        n_clicks=0,
                        className='btn btn-success',
                        style=get_button_style(),
                        disabled=True
                    )
                ]
            )
        ]
    )

def create_results_section():
    """Create results section with all analytics"""
    return html.Div([
        # Analytics Section
        html.Div(
            id='analytics-section',
            style={'display': 'none'},
            children=[
                html.H2("📈 Advanced Analytics", style={'textAlign': 'center'}),
                html.Div(id='analytics-detailed-breakdown')
            ]
        ),

        # Charts Section
        html.Div(
            id='charts-section',
            style={'display': 'none'},
            children=[
                html.H2("📊 Data Visualization", style={'textAlign': 'center'})
            ]
        ),

        # Export Section
        html.Div(
            id='export-section',
            style={'display': 'none'},
            children=[
                html.H2("📤 Export & Reports", style={'textAlign': 'center'}),
                html.Div([
                    html.Button("Download CSV", id="download-stats-csv", className="btn btn-primary", style={'margin': '5px'}),
                    html.Button("Download Charts", id="download-charts", className="btn btn-secondary", style={'margin': '5px'}),
                    html.Button("Generate Report", id="download-report", className="btn btn-success", style={'margin': '5px'}),
                ], style={'textAlign': 'center'}),
                html.Div(id="export-status", style={'textAlign': 'center', 'marginTop': '10px'})
            ]
        ),

        # Graph Section
        html.Div(
            id='graph-output-container',
            style={'display': 'none'},
            children=[
                html.H2("🌐 Network Visualization", style={'textAlign': 'center'}),
                html.Div(id='area-layout-model-title'),
                html.Div(id='cytoscape-graphs-area'),
                html.Div(id='tap-node-data-output'),
                html.Div(id='mini-graph-container')
            ]
        )
    ])

def create_data_stores():
    """Create all required data stores"""
    return html.Div([
        dcc.Store(id='uploaded-file-store'),
        dcc.Store(id='csv-headers-store'),
        dcc.Store(id='column-mapping-store'),
        dcc.Store(id='all-doors-from-csv-store'),
        dcc.Store(id='processed-data-store'),
        dcc.Store(id='device-attrs-store'),
        dcc.Store(id='manual-door-classifications-store'),
        dcc.Store(id='num-floors-store', data=1),
        dcc.Store(id='stats-data-store')
    ])
