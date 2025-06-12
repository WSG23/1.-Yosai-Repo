"""Yōsai Enhanced Analytics Dashboard application entry point.

Provides type‑safe helper utilities and registers all Dash callbacks."""

import sys
import os
import dash
from dash import Input, Output, State, html, dcc, no_update, callback, ALL
import dash_bootstrap_components as dbc
import json
import traceback
import numpy as np
import pandas as pd
import base64
import io
from datetime import datetime
import dash_cytoscape as cyto
from typing import Dict, Any, Union, Optional, List, Tuple
import math


# Type-safe JSON serialization
def make_json_serializable(
    data: Any,
) -> Union[Dict[str, Any], List[Any], int, float, str, None]:
    """
    Convert numpy data types to native Python types for JSON serialization.

    Returns: Always returns JSON-serializable Python types
    """
    if data is None:
        return None
    elif isinstance(data, dict):
        # FIXED: Convert all dictionary keys to strings for JSON compatibility
        serialized_dict = {}
        for key, value in data.items():
            # Convert keys to strings
            if isinstance(key, (int, float)):
                str_key = str(key)
            elif isinstance(key, tuple):
                str_key = str(key)  # Convert tuple to string representation
            elif isinstance(key, str):
                str_key = key
            else:
                str_key = str(key)  # Convert any other type to string

            # Recursively serialize values
            serialized_dict[str_key] = make_json_serializable(value)
        return serialized_dict
    elif isinstance(data, (list, tuple)):
        return [make_json_serializable(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        if np.isnan(data):
            return None
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif pd.isna(data):
        return None
    elif isinstance(data, (pd.Timestamp, datetime)):
        return data.isoformat()
    elif hasattr(data, "item"):  # Additional numpy scalar types
        return data.item()
    else:
        return data


# Type-safe helper functions
def safe_dict_access(
    data: Any, default: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Safely ensure data is a dictionary"""
    if isinstance(data, dict):
        return data
    return default or {}


def safe_len(data: Any, default: int = 0) -> int:
    """Safely get length of sized objects"""
    try:
        if hasattr(data, "__len__"):
            return len(data)
    except (TypeError, AttributeError):
        pass
    return default


def safe_get_keys(data: Any, max_keys: int = 6) -> List[str]:
    """Safely get dictionary keys"""
    if isinstance(data, dict):
        return list(data.keys())[:max_keys]
    return []


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.themes.style_config import (
    UI_VISIBILITY,
    COMPONENT_STYLES,
    COLORS,
    TYPOGRAPHY,
    SPACING,
)
from config.settings import DEFAULT_ICONS, REQUIRED_INTERNAL_COLUMNS, FILE_LIMITS

print(
    "🚀 Starting Yōsai Enhanced Analytics Dashboard (COMPLETE FIXED VERSION WITH TYPE SAFETY)..."
)

# ============================================================================
# ENHANCED IMPORTS WITH FALLBACK SUPPORT
# ============================================================================

# Enhanced component availability tracking
components_available = {
    "main_layout": False,
    "cytoscape": False,
}

component_instances = {}

print("🔍 Detecting available components...")

# Enhanced stats component
try:
    from enhanced_stats import (
        create_enhanced_stats_component,
        EnhancedStatsComponent,
        get_consolidated_analytics_layout,
    )

    components_available["enhanced_stats"] = True
    component_instances["enhanced_stats"] = create_enhanced_stats_component()
    print(">> Enhanced stats component imported and instantiated")
except ImportError as e:
    print(f"!! Enhanced stats component not available: {e}")
    create_enhanced_stats_component = None
    component_instances["enhanced_stats"] = None

# Upload component
try:
    from ui.components.upload import create_enhanced_upload_component

    components_available["upload"] = True
    print(">> Upload component imported")
except ImportError as e:
    print(f"!! Upload component not available: {e}")
    create_enhanced_upload_component = None

# Mapping component
try:
    from ui.components.mapping import create_mapping_component

    components_available["mapping"] = True
    print(">> Mapping component imported")
except ImportError as e:
    print(f"!! Mapping component not available: {e}")
    create_mapping_component = None

# Classification component
try:
    from ui.components.classification import create_classification_component

    components_available["classification"] = True
    print(">> Classification component imported")
except ImportError as e:
    print(f"!! Classification component not available: {e}")
    create_classification_component = None

# Handler factories
try:
    from ui.components.upload_handlers import create_upload_handlers
    from ui.components.mapping_handlers import create_mapping_handlers
    from ui.components.classification_handlers import create_classification_handlers
    from ui.components.graph_handlers import create_graph_handlers
    from ui.components.enhanced_stats_handlers import create_enhanced_stats_handlers
    from ui.components.graph import create_graph_container

    print(">> Handler factories imported")
except ImportError as e:
    print(f"!! Handler factories not available: {e}")
    create_upload_handlers = None
    create_mapping_handlers = None
    create_classification_handlers = None
    create_graph_handlers = None
    create_enhanced_stats_handlers = None
    create_graph_container = None

# Cytoscape for graphs
try:
    import dash_cytoscape as cyto

    components_available["cytoscape"] = True
    print(">> Cytoscape available")
except ImportError as e:
    print(f"!! Cytoscape not available: {e}")

# Plotly for charts
try:
    import plotly.express as px
    import plotly.graph_objects as go

    components_available["plotly"] = True
    print(">> Plotly available")
except ImportError as e:
    print(f"!! Plotly not available: {e}")
    px = None
    go = None

# Main layout
try:
    from ui.pages.main_page import create_main_layout
    from ui.themes.style_config import (
        get_enhanced_card_style,
        get_enhanced_button_style,
    )

    components_available["main_layout"] = True
    print(">> Main layout imported")
except ImportError as e:
    print(f"!! Main layout not available: {e}")
    create_main_layout = None

print(f">> Component Detection Complete:")
for component, available in components_available.items():
    status = "[ACTIVE]" if available else "[FALLBACK]"
    print(f"   {component}: {status}")

# ============================================================================
# CREATE DASH APP WITH FIXED LAYOUT
# ============================================================================

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder="assets",
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {
            "name": "description",
            "content": "Yōsai Enhanced Analytics Dashboard - COMPLETE FIXED VERSION WITH TYPE SAFETY",
        },
    ],
)

server = app.server
app.title = "Yōsai Enhanced Analytics Dashboard"

# Asset paths - FIXED: Define these before using them
ICON_UPLOAD_DEFAULT = app.get_asset_url("upload_file_csv_icon.png")
ICON_UPLOAD_SUCCESS = app.get_asset_url("upload_file_csv_icon_success.png")
ICON_UPLOAD_FAIL = app.get_asset_url("upload_file_csv_icon_fail.png")
MAIN_LOGO_PATH = app.get_asset_url("logo_white.png")

print(f">> Assets loaded: {ICON_UPLOAD_DEFAULT}")

# ============================================================================
# HELPER FUNCTIONS - ALL INCLUDED WITH TYPE SAFETY
# ============================================================================


def _create_fallback_stats_container():
    """Create fallback stats container with all required callback elements"""
    return html.Div(
        id="stats-panels-container",
        style={"display": "block", "minHeight": "200px"},
        children=[
            html.Div(
                [
                    html.H3("Access Events"),
                    html.H1(id="total-access-events-H1", children="0"),
                    html.P(id="event-date-range-P", children="No data"),
                    html.Table([html.Tbody(id="most-active-devices-table-body")]),
                ]
            ),
            html.Div(
                [
                    html.P(id="stats-unique-users", children="Users: 0"),
                    html.P(
                        id="stats-avg-events-per-user", children="Avg: 0 events/user"
                    ),
                    html.P(id="stats-most-active-user", children="No data"),
                    html.P(id="stats-devices-per-user", children="Avg: 0 users/device"),
                    html.P(id="stats-peak-hour", children="Peak: N/A"),
                    html.P(id="total-devices-count", children="0 devices"),
                    html.P(id="entrance-devices-count", children="0 entrances"),
                    html.P(id="high-security-devices", children="0 high security"),
                ]
            ),
            html.Div(
                [
                    html.P(id="peak-hour-display", children="Peak: N/A"),
                    html.P(id="peak-day-display", children="Busiest: N/A"),
                    html.P(id="busiest-floor", children="Floor: N/A"),
                    html.P(id="entry-exit-ratio", children="Ratio: N/A"),
                    html.P(id="weekend-vs-weekday", children="Pattern: N/A"),
                    html.Div(id="security-level-breakdown", children="No data"),
                    html.P(id="compliance-score", children="Score: N/A"),
                    html.P(id="anomaly-alerts", children="Alerts: 0"),
                ]
            ),
        ],
    )


def _create_fallback_analytics_section():
    """Create fallback analytics section"""
    return html.Div(
        id="analytics-section",
        style={"display": "none"},
        children=[
            html.H4("Advanced Analytics"),
            html.P(id="traffic-pattern-insight", children="No data"),
            html.P(id="security-score-insight", children="N/A"),
            html.P(id="efficiency-insight", children="N/A"),
            html.P(id="anomaly-insight", children="0 detected"),
        ],
    )


def _create_fallback_charts_section():
    """Create fallback charts section"""
    return html.Div(
        id="charts-section",
        style={"display": "none"},
        children=[
            html.H4("Data Visualization"),
            dcc.Dropdown(
                id="chart-type-selector",
                options=[
                    {"label": "Hourly Activity", "value": "hourly"},
                    {"label": "Security Distribution", "value": "security"},
                ],
                value="hourly",
            ),
            dcc.Graph(id="main-analytics-chart"),
            dcc.Graph(id="security-pie-chart"),
            dcc.Graph(id="heatmap-chart"),
        ],
    )


def _create_fallback_export_section():
    """Create fallback export section"""
    return html.Div(
        id="export-section",
        style={"display": "none"},
        children=[
            html.H4("Export & Reports"),
            html.Button("Export Stats CSV", id="export-stats-csv"),
            html.Button("Download Charts", id="export-charts-png"),
            html.Button("Generate Report", id="generate-pdf-report"),
            html.Button("Refresh Data", id="refresh-analytics"),
            dcc.Download(id="download-stats-csv"),
            dcc.Download(id="download-charts"),
            dcc.Download(id="download-report"),
            html.Div(id="export-status"),
        ],
    )


def _create_fallback_enhanced_header():
    """Create fallback header for enhanced stats"""
    return html.Div(
        id="enhanced-stats-header",
        style={"display": "none"},
        children=[
            html.H3("Enhanced Stats"),
            html.Div(
                [
                    html.Button("Export", id="export-stats-btn"),
                    html.Button("Refresh", id="refresh-stats-btn"),
                    dcc.Checklist(
                        id="real-time-toggle",
                        options=[{"label": "Real-time", "value": "on"}],
                        value=[],
                        style={"display": "inline-block", "marginLeft": "10px"},
                    ),
                ],
                style={"display": "flex", "gap": "10px"},
            ),
        ],
    )


# Add this function to app.py - Create proper advanced analytics container


def _create_advanced_analytics_container():
    """Create advanced analytics panels container with all required elements"""
    from ui.themes.style_config import COLORS

    panel_style = {
        "backgroundColor": COLORS["surface"],
        "padding": "20px",
        "borderRadius": "8px",
        "border": f"1px solid {COLORS['border']}",
        "minWidth": "250px",
        "flex": "1",
    }

    return html.Div(
        id="advanced-analytics-panels-container",
        style={"display": "none"},
        children=[
            # Peak Activity Panel - COMPLETE with all elements
            html.Div(
                [
                    html.H3("Peak Activity", style={"color": COLORS["text_primary"]}),
                    html.P(
                        id="peak-hour-display",
                        children="Peak Hour: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="peak-day-display",
                        children="Peak Day: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="busiest-floor",
                        children="Busiest Floor: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="entry-exit-ratio",
                        children="Entry/Exit: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),  # FIXED: Added this
                    html.P(
                        id="weekend-vs-weekday",
                        children="Weekend vs Weekday: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),  # FIXED: Added this
                ],
                style=panel_style,
            ),
            # Security Overview Panel
            html.Div(
                [
                    html.H3(
                        "Security Overview", style={"color": COLORS["text_primary"]}
                    ),
                    html.Div(
                        id="security-level-breakdown",
                        children="Security analysis loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="security-compliance-score",
                        children="Compliance: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                ],
                style=panel_style,
            ),
            # Additional Analytics Panel
            html.Div(
                [
                    html.H3(
                        "Analytics Insights", style={"color": COLORS["text_primary"]}
                    ),
                    html.P(
                        id="traffic-pattern-insight",
                        children="Pattern: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="security-score-insight",
                        children="Score: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="anomaly-insight",
                        children="Alerts: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                    html.P(
                        id="efficiency-insight",
                        children="Efficiency: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                ],
                style=panel_style,
            ),
        ],
    )


def _create_mini_graph_container():
    """Create mini graph container"""
    mini_graph = html.Div("Mini graph placeholder")
    if components_available["cytoscape"]:
        mini_graph = cyto.Cytoscape(
            id="mini-onion-graph",
            style={"width": "100%", "height": "300px"},
            elements=[],
            wheelSensitivity=1,
        )

    return html.Div(
        id="mini-graph-container", style={"display": "none"}, children=[mini_graph]
    )


def _add_missing_callback_elements(base_children: List[Any], existing_ids: set) -> None:
    """Add missing callback elements as hidden placeholders"""
    callback_targets = [
        "stats-unique-users",
        "stats-avg-events-per-user",
        "stats-most-active-user",
        "stats-devices-per-user",
        "stats-peak-hour",
        "total-devices-count",
        "entrance-devices-count",
        "high-security-devices",
        "traffic-pattern-insight",
        "security-score-insight",
        "efficiency-insight",
        "anomaly-insight",
        "peak-hour-display",
        "peak-day-display",
        "busiest-floor",
        "entry-exit-ratio",
        "weekend-vs-weekday",
        "security-level-breakdown",
        "compliance-score",
        "security-compliance-score",
        "anomaly-alerts",
        "main-analytics-chart",
        "security-pie-chart",
        "heatmap-chart",
        "chart-type-selector",
        "export-stats-csv",
        "export-charts-png",
        "generate-pdf-report",
        "refresh-analytics",
        "download-stats-csv",
        "download-charts",
        "download-report",
        "export-status",
        "stats-refresh-interval",
        "export-graph-png",
        "export-graph-json",
        "download-graph-png",
        "download-graph-json",
        # FIXED: Add Enhanced Stats Handler targets
        "enhanced-total-access-events-H1",
        "enhanced-event-date-range-P",
        "events-trend-indicator",
        "avg-events-per-day",
        "most-active-user",
        "avg-user-activity",
        "unique-users-today",
        # Add IDs referenced by enhanced stats callbacks
        "core-row-with-sidebar",
        "peak-activity-events",
    ]

    for element_id in callback_targets:
        if element_id not in existing_ids:
            print(f">> Adding hidden placeholder for callback target: {element_id}")

            if element_id == "stats-refresh-interval":
                element = dcc.Interval(id=element_id, disabled=True, interval=999999999)
            elif element_id in [
                "export-stats-csv",
                "export-charts-png",
                "generate-pdf-report",
                "refresh-analytics",
                "export-graph-png",
                "export-graph-json",
            ]:
                element = html.Button(id=element_id, style={"display": "none"})
            elif element_id in [
                "main-analytics-chart",
                "security-pie-chart",
                "heatmap-chart",
            ]:
                element = dcc.Graph(id=element_id, style={"display": "none"})
            elif element_id in [
                "download-stats-csv",
                "download-charts",
                "download-report",
                "download-graph-png",
                "download-graph-json",
            ]:
                element = dcc.Download(id=element_id)
            elif "store" in element_id:
                element = dcc.Store(id=element_id)
            elif "chart-type-selector" in element_id:
                element = dcc.Dropdown(id=element_id, style={"display": "none"})
            else:
                element = html.Div(id=element_id, style={"display": "none"})

            base_children.append(element)


def create_debug_panel():
    """Create debug panel to monitor Enhanced Analytics data flow"""
    return html.Div(
        [
            html.H4(
                "DEBUG: Enhanced Analytics",
                style={"color": "#fff", "margin": "0 0 10px 0"},
            ),
            html.P(
                id="debug-metrics-count",
                style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"},
            ),
            html.P(
                id="debug-metrics-keys",
                style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"},
            ),
            html.P(
                id="debug-processed-data",
                style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"},
            ),
            html.P(
                id="debug-calculation-status",
                style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"},
            ),
        ],
        style={
            "position": "fixed",
            "top": "10px",
            "right": "10px",
            "backgroundColor": "#333",
            "padding": "15px",
            "borderRadius": "8px",
            "zIndex": "9999",
            "maxWidth": "300px",
            "border": "1px solid #555",
        },
    )


def _create_complete_fixed_layout(
    app_instance, main_logo_path: str, icon_upload_default: str
):
    """Create complete layout from scratch with all required elements"""

    print(">> Creating complete layout from scratch with all required elements")

    # Choose enhanced stats implementation if available
    if components_available.get("enhanced_stats") and component_instances.get(
        "enhanced_stats"
    ):
        enhanced_stats_layout = [
            component_instances["enhanced_stats"].create_enhanced_stats_container(),
        ]
    else:
        enhanced_stats_layout = [
            _create_fallback_enhanced_header(),
            _create_advanced_analytics_container(),
        ]

    base_children = [
        # FIXED: yosai-custom-header (required by callbacks)
        html.Div(
            id="yosai-custom-header",
            style=UI_VISIBILITY["show_header"],
            children=[
                html.Div(
                    [
                        html.Img(
                            src=main_logo_path,
                            style={"height": "24px", "marginRight": SPACING["sm"]},
                        ),
                        html.Span(
                            "Enhanced Analytics Dashboard",
                            style={
                                "fontSize": TYPOGRAPHY["text_lg"],
                                "color": COLORS["text_primary"],
                                "fontWeight": TYPOGRAPHY["font_normal"],
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "width": "100%",
                    },
                )
            ],
        ),
        # Dashboard title (maintain existing design)
        html.Div(
            id="dashboard-title",
            className="header-section",
            children=[
                html.H1("Yōsai Intel Dashboard", className="main-title"),
                html.Button(
                    "Advanced View",
                    id="advanced-view-button",
                    className="btn-secondary",
                ),
            ],
        ),
        # Top row with upload and controls
        html.Div(
            id="top-row",
            className="row-layout",
            children=[
                # Upload section
                html.Div(
                    id="upload-section",
                    className="upload-container",
                    children=[
                        dcc.Upload(
                            id="upload-data",
                            children=[
                                html.Img(id="upload-icon", src=icon_upload_default),
                                html.P(
                                    "Drop your CSV or JSON file here or click to browse"
                                ),
                            ],
                            className="upload-area",
                            accept=".csv,.json",
                        )
                    ],
                ),
                # Chart controls
                html.Div(
                    id="chart-controls",
                    className="controls-panel",
                    children=[
                        dcc.Dropdown(
                            id="chart-type-selector",
                            options=[
                                {"label": "Timeline", "value": "timeline"},
                                {"label": "Hourly Activity", "value": "hourly"},
                                {"label": "Daily Patterns", "value": "daily"},
                                {"label": "Floor Activity", "value": "floor"},
                                {"label": "Activity Heatmap", "value": "heatmap"},
                            ],
                            value="timeline",
                        ),
                        html.Button("Apply Filters", id="filter-button"),
                        html.Button("Time Range", id="timerange-button"),
                    ],
                ),
            ],
        ),
        # Processing status
        html.Div(
            id="processing-status",
            className="status-message",
            children="Upload a CSV or JSON file to begin analysis",
        ),
        # Interactive setup container
        html.Div(
            id="interactive-setup-container",
            style={"display": "none"},
            children=[
                # FIXED: mapping-ui-section with dropdown-mapping-area
                html.Div(
                    id="mapping-ui-section",
                    style={"display": "none"},
                    children=[
                        html.H4(
                            "Step 1: Map File Headers",
                            style={
                                "color": COLORS["text_primary"],
                                "textAlign": "center",
                                "marginBottom": "20px",
                            },
                        ),
                        html.P(
                            [
                                "Map your file columns to the required fields. ",
                                html.Strong(
                                    "All four fields are required",
                                    style={"color": COLORS["accent"]},
                                ),
                                " for analysis.",
                            ],
                            style={
                                "color": COLORS["text_secondary"],
                                "textAlign": "center",
                                "marginBottom": "20px",
                            },
                        ),
                        html.Div(id="dropdown-mapping-area"),
                        html.Div(
                            id="mapping-validation-message",
                            style={"display": "none"},
                        ),
                        html.Button(
                            "Confirm Header Mapping & Proceed",
                            id="confirm-header-map-button",
                            n_clicks=0,
                            style={"display": "none"},
                        ),
                    ],
                ),
                # Entrance verification section
                html.Div(
                    id="entrance-verification-ui-section",
                    style={"display": "none"},
                    children=[
                        html.H4("Step 2: Facility Setup"),
                        html.Label("Number of floors:"),
                        dcc.Slider(
                            id="floor-slider",
                            min=1,
                            max=48,
                            step=1,
                            value=48,
                            marks={**{i: str(i) for i in range(1, 20, 2)}, 48: "48"},
                        ),
                        html.Div(id="floor-slider-value", children="48 floors"),
                        html.Label("Enable manual door classification?"),
                        dcc.RadioItems(
                            id="manual-map-toggle",
                            options=[
                                {"label": "No", "value": "no"},
                                {"label": "Yes", "value": "yes"},
                            ],
                            value="no",
                            inline=True,
                        ),
                        html.Div(
                            id="door-classification-table-container",
                            style={"display": "none"},
                            children=[html.Div(id="door-classification-table")],
                        ),
                    ],
                ),
                # Generate button
                html.Button(
                    "Confirm Selections & Generate Analysis",
                    id="confirm-and-generate-button",
                    n_clicks=0,
                    className="btn-primary",
                ),
            ],
        ),
        # Tabs container
        html.Div(
            id="tabs-container",
            children=[
                html.Button("Overview", id="tab-overview", className="tab active"),
                html.Button("Advanced", id="tab-advanced", className="tab"),
                html.Button("Export", id="tab-export", className="tab"),
            ],
        ),
        # Tab content
        html.Div(
            id="tab-content",
            children=[
                # Your 3 panels container
                html.Div(
                    id="stats-panels-container",
                    style={"display": "flex", "gap": "20px", "marginBottom": "30px"},
                    children=[
                        # Panel 1: Access Events
                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": COLORS["surface"],
                                "padding": "20px",
                                "borderRadius": "8px",
                                "textAlign": "center",
                            },
                            children=[
                                html.H3("Access Events"),
                                html.H1(id="total-access-events-H1", children="0"),
                                html.P(id="event-date-range-P", children="No data"),
                            ],
                        ),
                        # Panel 2: User Stats
                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": COLORS["surface"],
                                "padding": "20px",
                                "borderRadius": "8px",
                                "textAlign": "center",
                            },
                            children=[
                                html.H3("User Analytics"),
                                html.P(id="stats-unique-users", children="0 users"),
                                html.P(
                                    id="stats-avg-events-per-user",
                                    children="Avg: 0 events/user",
                                ),
                                html.P(id="stats-most-active-user", children="No data"),
                                html.P(
                                    id="stats-devices-per-user",
                                    children="Avg: 0 users/device",
                                ),
                                html.P(id="stats-peak-hour", children="Peak: N/A"),
                                html.P(id="total-devices-count", children="0 devices"),
                                html.P(
                                    id="entrance-devices-count", children="0 entrances"
                                ),
                                html.P(
                                    id="high-security-devices",
                                    children="0 high security",
                                ),
                            ],
                        ),
                        # Panel 3: Activity Insights
                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": COLORS["surface"],
                                "padding": "20px",
                                "borderRadius": "8px",
                                "textAlign": "center",
                            },
                            children=[
                                html.H3("Activity Insights"),
                                html.P(id="peak-hour-display", children="Peak: N/A"),
                                html.P(id="busiest-floor", children="Floor: N/A"),
                                html.P(
                                    id="traffic-pattern-insight",
                                    children="Pattern: N/A",
                                ),
                                html.P(
                                    id="security-score-insight", children="Score: N/A"
                                ),
                                html.P(id="anomaly-insight", children="Alerts: 0"),
                            ],
                        ),
                    ],
                ),
                # All required elements for callbacks (initially hidden)
                *enhanced_stats_layout,
                _create_fallback_analytics_section(),
                _create_fallback_charts_section(),
                _create_fallback_export_section(),
                (
                    create_graph_container()
                    if create_graph_container
                    else html.Div(
                        id="graph-output-container", style={"display": "none"}
                    )
                ),
                _create_mini_graph_container(),
                create_debug_panel(),
            ],
        ),
    ]

    existing_ids: set = set()

    def collect_ids(element):
        if hasattr(element, "id") and element.id:
            existing_ids.add(element.id)
        if hasattr(element, "children"):
            children = (
                element.children
                if isinstance(element.children, list)
                else [element.children] if element.children else []
            )
            for child in children:
                collect_ids(child)

    for child in base_children:
        collect_ids(child)

    _add_missing_callback_elements(base_children, existing_ids)

    return html.Div(
        base_children,
        style={
            "backgroundColor": COLORS["background"],
            "minHeight": "100vh",
            "padding": "20px",
            "fontFamily": "Inter, sans-serif",
        },
    )


# ============================================================================
# FIXED LAYOUT CREATION - MAINTAINS CONSISTENCY + ADDS REQUIRED ELEMENTS
# ============================================================================


def create_fixed_layout_with_required_elements(
    app_instance, main_logo_path: str, icon_upload_default: str
):
    """Create layout that maintains current design but includes all required callback elements"""

    print(">> Creating FIXED layout with all required elements...")

    # First try to use the main layout if available
    base_layout = None
    if components_available["main_layout"] and create_main_layout:
        try:
            # FIXED: Pass all required arguments to create_main_layout
            base_layout = create_main_layout(
                app_instance, main_logo_path, icon_upload_default
            )
            print(">> Base main layout loaded successfully")
        except Exception as e:
            print(f"!! Error loading main layout: {e}")
            base_layout = None

    if base_layout:
        # FIXED: Add missing elements to existing layout
        return _add_missing_elements_to_existing_layout(
            base_layout, main_logo_path, icon_upload_default
        )
    else:
        # Create complete layout from scratch with all required elements
        return _create_complete_fixed_layout(
            app_instance, main_logo_path, icon_upload_default
        )


def _add_missing_elements_to_existing_layout(
    base_layout, main_logo_path: str, icon_upload_default: str
):
    """FIXED: Add missing callback elements to existing layout while preserving design"""

    try:
        # Get base layout children
        base_children = (
            list(base_layout.children) if hasattr(base_layout, "children") else []
        )

        # Track existing IDs to avoid duplicates
        existing_ids = set()

        def collect_ids(element):
            if hasattr(element, "id") and element.id:
                existing_ids.add(element.id)
            if hasattr(element, "children"):
                children = (
                    element.children
                    if isinstance(element.children, list)
                    else [element.children] if element.children else []
                )
                for child in children:
                    collect_ids(child)

        for child in base_children:
            collect_ids(child)

        print(f">> Found existing IDs: {len(existing_ids)} total")

        # FIXED: Add yosai-custom-header if dashboard-title exists but yosai-custom-header doesn't
        if (
            "dashboard-title" in existing_ids
            and "yosai-custom-header" not in existing_ids
        ):
            print(">> Adding yosai-custom-header alias for dashboard-title")
            # Add yosai-custom-header as a hidden element that mirrors dashboard-title styling
            base_children.insert(
                0,
                html.Div(
                    id="yosai-custom-header",
                    style=UI_VISIBILITY["show_header"],
                    children=[
                        html.Div(
                            [
                                html.Img(
                                    src=main_logo_path,
                                    style={
                                        "height": "24px",
                                        "marginRight": SPACING["sm"],
                                    },
                                ),
                                html.Span(
                                    "Enhanced Analytics Dashboard",
                                    style={
                                        "fontSize": TYPOGRAPHY["text_lg"],
                                        "color": COLORS["text_primary"],
                                        "fontWeight": TYPOGRAPHY["font_normal"],
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "width": "100%",
                            },
                        )
                    ],
                ),
            )

        # FIXED: Add dropdown-mapping-area inside mapping-ui-section if it doesn't exist
        def add_missing_mapping_elements(children):
            new_children = []
            for child in children:
                if hasattr(child, "id") and child.id == "mapping-ui-section":
                    # Check if dropdown-mapping-area exists in this section
                    section_children = (
                        child.children if hasattr(child, "children") else []
                    )
                    if isinstance(section_children, list):
                        section_children = list(section_children)
                    else:
                        section_children = (
                            [section_children] if section_children else []
                        )

                    # Look for dropdown-mapping-area in section children
                    has_dropdown_area = False
                    for section_child in section_children:
                        if (
                            hasattr(section_child, "id")
                            and section_child.id == "dropdown-mapping-area"
                        ):
                            has_dropdown_area = True
                            break

                    if not has_dropdown_area:
                        print(
                            ">> Adding missing dropdown-mapping-area to mapping-ui-section"
                        )
                        # Add the missing dropdown-mapping-area
                        section_children.extend(
                            [
                                html.H4(
                                    "Step 1: Map File Headers",
                                    style={
                                        "color": COLORS["text_primary"],
                                        "textAlign": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                html.P(
                                    [
                                        "Map your file columns to the required fields. ",
                                        html.Strong(
                                            "All four fields are required",
                                            style={"color": COLORS["accent"]},
                                        ),
                                        " for analysis.",
                                    ],
                                    style={
                                        "color": COLORS["text_secondary"],
                                        "textAlign": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                html.Div(
                                    id="dropdown-mapping-area"
                                ),  # FIXED: Add missing element
                                html.Div(
                                    id="mapping-validation-message",
                                    style={"display": "none"},
                                ),
                                html.Button(
                                    "Confirm Header Mapping & Proceed",
                                    id="confirm-header-map-button",
                                    n_clicks=0,
                                    style={
                                        "display": "none",
                                        "margin": "25px auto",
                                        "padding": "12px 30px",
                                        "backgroundColor": COLORS["accent"],
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "8px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ]
                        )

                        # Update child with new children
                        child.children = section_children

                    new_children.append(child)
                else:
                    # Recursively process children
                    if hasattr(child, "children") and child.children:
                        child_list = (
                            child.children
                            if isinstance(child.children, list)
                            else [child.children]
                        )
                        child.children = add_missing_mapping_elements(child_list)
                    new_children.append(child)

            return new_children

        base_children = add_missing_mapping_elements(base_children)

        # FIXED: Add other required elements that might be missing
        required_elements = {
            "enhanced-stats-header": _create_fallback_enhanced_header(),
            "stats-panels-container": _create_fallback_stats_container(),
            "advanced-analytics-panels-container": _create_advanced_analytics_container(),
            "analytics-section": _create_fallback_analytics_section(),
            "charts-section": _create_fallback_charts_section(),
            "export-section": _create_fallback_export_section(),
            "graph-output-container": (
                create_graph_container()
                if create_graph_container
                else html.Div(id="graph-output-container", style={"display": "none"})
            ),
            "mini-graph-container": _create_mini_graph_container(),
            "debug-panel": create_debug_panel(),
            "onion-graph": None,  # Will be added to graph-output-container
            "mini-onion-graph": None,  # Will be added to mini-graph-container
        }

        # Collect all IDs again after modifications
        existing_ids.clear()
        for child in base_children:
            collect_ids(child)

        # Add missing required elements (hidden by default to maintain layout)
        for element_id, element_creator in required_elements.items():
            if element_id not in existing_ids and element_creator:
                print(f">> Adding missing element: {element_id}")
                base_children.append(element_creator)

        # FIXED: Ensure all required callback target elements exist
        _add_missing_callback_elements(base_children, existing_ids)

        print(">> Successfully added all missing elements to existing layout")

        return html.Div(
            base_children,
            style=(
                base_layout.style
                if hasattr(base_layout, "style")
                else {
                    "backgroundColor": COLORS["background"],
                    "minHeight": "100vh",
                    "fontFamily": "Inter, sans-serif",
                }
            ),
        )

    except Exception as e:
        print(f"!! Error adding missing elements: {e}")
        traceback.print_exc()
        return _create_complete_fixed_layout(None, main_logo_path, icon_upload_default)


# FIXED: Create layout with all required elements and correct arguments
current_layout = create_fixed_layout_with_required_elements(
    app, MAIN_LOGO_PATH, ICON_UPLOAD_DEFAULT
)

# Create consolidated analytics component
if create_enhanced_stats_component is None:
    raise ImportError("Enhanced stats component not available")
analytics_component = create_enhanced_stats_component()
analytics_container = analytics_component.create_enhanced_stats_container()

# EMERGENCY FIX: Add missing elements directly to layout
missing_elements = [
    html.P(
        id="entry-exit-ratio", children="Entry/Exit: N/A", style={"display": "none"}
    ),
    html.P(
        id="weekend-vs-weekday",
        children="Weekend vs Weekday: N/A",
        style={"display": "none"},
    ),
]
# Add required data stores
app.layout = html.Div(
    [
        # Required data stores
        dcc.Store(id="uploaded-file-store"),
        dcc.Store(id="csv-headers-store"),
        dcc.Store(id="column-mapping-store", storage_type="local"),
        dcc.Store(id="all-doors-from-csv-store"),
        dcc.Store(id="processed-data-store"),
        dcc.Store(id="device-attrs-store"),
        dcc.Store(id="manual-door-classifications-store", storage_type="local"),
        dcc.Store(id="num-floors-store", data=1),
        dcc.Store(id="stats-data-store"),
        # Your existing layout
        current_layout,
        # Consolidated analytics container
        analytics_container,
        # Inject emergency placeholders for callbacks expecting these IDs
        *missing_elements,
    ]
)

print(
    ">> COMPLETE FIXED layout created successfully with all required callback elements"
)

# ============================================================================
# SAFE CALLBACK REGISTRATION
# ============================================================================

CALLBACKS_REGISTERED = False


def register_all_callbacks_safely(app):
    """Register callbacks with conflict prevention"""
    global CALLBACKS_REGISTERED

    if CALLBACKS_REGISTERED:
        print("✅ Callbacks already registered - skipping duplicate registration")
        return

    try:
        print("🔄 Registering callbacks...")

        # ===== UPLOAD HANDLERS - ADD THIS SECTION =====
        from ui.components.upload_handlers import UploadHandlers
        from ui.components.upload import create_enhanced_upload_component

        # Create upload component and handlers
        upload_component = create_enhanced_upload_component(
            ICON_UPLOAD_DEFAULT,
            ICON_UPLOAD_SUCCESS,
            ICON_UPLOAD_FAIL,
        )
        icon_paths = {
            "default": ICON_UPLOAD_DEFAULT,
            "success": ICON_UPLOAD_SUCCESS,
            "fail": ICON_UPLOAD_FAIL,
        }

        upload_handlers = UploadHandlers(app, upload_component, icon_paths)
        upload_handlers.register_callbacks()
        print("   ✅ Upload callbacks registered")
        # ===== END UPLOAD HANDLERS =====

        from ui.orchestrator import main_data_orchestrator  # noqa: F401
        from ui.orchestrator import update_graph_elements  # noqa: F401
        from ui.orchestrator import update_container_visibility  # noqa: F401
        from ui.orchestrator import update_status_display  # noqa: F401
        from ui.components.mapping_handlers import MappingHandlers
        from ui.components.classification_handlers import ClassificationHandlers

        mapping_handlers = MappingHandlers(app)
        mapping_handlers.register_callbacks()
        print("   ✅ Mapping callbacks registered")

        classification_handlers = ClassificationHandlers(app)
        classification_handlers.register_callbacks()
        print("   ✅ Classification callbacks registered (includes floor slider)")

        if create_graph_handlers:
            graph_handlers = create_graph_handlers(app)
            graph_handlers.register_callbacks()
            print("   ✅ Graph callbacks registered")

        if create_enhanced_stats_handlers:
            stats_handlers = create_enhanced_stats_handlers(app)
            stats_handlers.register_callbacks()
            print("   ✅ Enhanced stats callbacks registered")

        CALLBACKS_REGISTERED = True
        print("🎉 All callbacks registered successfully - no conflicts!")

    except Exception as e:
        print(f"❌ Error registering callbacks: {e}")
        CALLBACKS_REGISTERED = False  # Reset flag on error
        raise


# Register callbacks safely
register_all_callbacks_safely(app)

# ============================================================================
# TYPE-SAFE CALLBACK FUNCTIONS
# ============================================================================

# FIXED: Upload callback with no duplicate exception handling


# Advanced view toggle callback
def toggle_advanced_view(
    n_clicks: Optional[int],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], str]:
    """Toggle between basic and advanced analytics view"""

    if not n_clicks:
        return (
            {"display": "flex", "gap": "20px", "marginBottom": "30px"},
            {"display": "none"},
            {"display": "none"},
            "Advanced View",
        )

    if n_clicks % 2 == 1:
        return (
            {"display": "none"},
            {
                "display": "flex",
                "justifyContent": "space-around",
                "marginBottom": "30px",
            },
            {
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
            },
            "Basic View",
        )

    return (
        {"display": "flex", "gap": "20px", "marginBottom": "30px"},
        {"display": "none"},
        {"display": "none"},
        "Advanced View",
    )


# FIXED: Debug callback with complete type safety
def update_debug_info(
    metrics_data: Any, processed_data: Any
) -> Tuple[str, str, str, str]:
    """Update debug information to track data flow - COMPLETELY TYPE-SAFE"""

    # Safe metrics processing
    metrics_dict = safe_dict_access(metrics_data)
    if metrics_dict:
        metrics_count = f"[OK] Metrics: {safe_len(metrics_dict)} items calculated"
        keys = safe_get_keys(metrics_dict, 6)
        metrics_keys = f"Keys: {', '.join(keys)}..." if keys else "Keys: None"

        advanced_keys = [
            "traffic_pattern",
            "security_score",
            "avg_events_per_user",
            "most_active_user",
        ]
        has_advanced = any(key in metrics_dict for key in advanced_keys)
        calculation_status = f"Advanced metrics: {'YES' if has_advanced else 'MISSING'}"
    else:
        metrics_count = "[ERROR] Metrics: No data or invalid format"
        metrics_keys = "Keys: None"
        calculation_status = "Advanced metrics: Not calculated"

    # Safe processed data handling
    processed_dict = safe_dict_access(processed_data)
    if processed_dict and "dataframe" in processed_dict:
        try:
            dataframe_data = processed_dict["dataframe"]
            data_rows = safe_len(dataframe_data)
            processed_info = f"Processed: {data_rows} rows available"
        except (TypeError, KeyError):
            processed_info = "Processed: Invalid data format"
    else:
        processed_info = "Processed: No data"

    return metrics_count, metrics_keys, processed_info, calculation_status


# FIXED: Container sync callback with complete type safety
def sync_containers_with_stats(enhanced_metrics: Any) -> Tuple[Any, Any]:
    """Keep container layouts stable when stats update."""

    metrics_dict = safe_dict_access(enhanced_metrics)
    if not metrics_dict:
        return dash.no_update, dash.no_update

    # Leave the existing layout untouched so that elements like
    # `peak-day-display` remain present for other callbacks.
    return dash.no_update, dash.no_update


# FIXED: Enhanced stats store callback with complete validation
def update_enhanced_stats_store(
    status_message: Any, processed_data: Any, device_classifications: Any
) -> Dict[str, Any]:
    """Update enhanced stats store - COMPLETELY TYPE-SAFE"""

    # Validate inputs
    if not status_message or "Analysis complete" not in str(status_message):
        return {}

    try:
        processed_dict = safe_dict_access(processed_data)
        if not processed_dict or "dataframe" not in processed_dict:
            print("❌ Invalid processed_data format")
            return {}

        # Safely create DataFrame
        dataframe_data = processed_dict["dataframe"]
        if not isinstance(dataframe_data, (list, dict)):
            print("❌ Invalid dataframe data format")
            return {}

        df = pd.DataFrame(dataframe_data)

        # Convert timestamp column if it exists
        timestamp_col = "Timestamp (Event Time)"
        if timestamp_col in df.columns:
            # FIXED: Use correct pandas to_datetime parameters
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

        # Handle device classifications safely
        device_attrs = None
        classifications_dict = safe_dict_access(device_classifications)
        if classifications_dict:
            try:
                device_attrs = pd.DataFrame.from_dict(
                    classifications_dict, orient="index"
                )
                device_attrs.reset_index(inplace=True)
                device_attrs.rename(columns={"index": "Door Number"}, inplace=True)
            except Exception as e:
                print(f"⚠️ Could not process device classifications: {e}")

        # Calculate metrics safely
        enhanced_metrics = process_uploaded_data(df, device_attrs)

        # Ensure result is a dictionary
        metrics_dict = safe_dict_access(enhanced_metrics)
        if not metrics_dict:
            print("❌ process_uploaded_data returned invalid data")
            return {}

        print(f"✅ Enhanced stats updated: {safe_len(metrics_dict)} metrics")
        return metrics_dict

    except Exception as e:
        print(f"❌ Error in enhanced stats store: {e}")
        import traceback

        traceback.print_exc()
        return {}


# Single callback to update the visible processing status message
def display_status_message(message: Any) -> Any:
    """Display the latest processing status message."""
    return message


# Main analysis callback - MODIFIED to avoid conflicts
# Main analysis callback - MODIFIED to avoid conflicts
def generate_enhanced_analysis(
    n_clicks: Optional[int],
    file_data: Any,
    processed_data: Any,
    device_classifications: Any,
) -> Tuple[Dict[str, str], Dict[str, Any], str]:
    """Generate analysis - handle visibility and status only"""
    if not n_clicks or not file_data:
        hide_style = {"display": "none"}
        return (
            hide_style,  # yosai-custom-header
            hide_style,  # stats-panels-container
            "Click generate to start analysis",  # status
        )

    try:
        print("🎉 Generating enhanced analysis...")

        # Show header and stats containers
        show_style = {"display": "block"}
        stats_style = {
            "display": "flex",
            "gap": "20px",
            "marginBottom": "30px",
            "backgroundColor": COLORS["background"],
            "padding": "20px",
            "marginTop": "20px",
        }

        # ACTUALLY PROCESS THE DATA and store it for enhanced stats handlers to use
        processed_dict = safe_dict_access(processed_data)
        if processed_dict and "dataframe" in processed_dict:
            # Convert processed data back to DataFrame
            df = pd.DataFrame(processed_dict["dataframe"])

            # Convert timestamp column to datetime if it exists
            timestamp_col = "Timestamp (Event Time)"
            if timestamp_col in df.columns:
                # FIXED: Use correct pandas to_datetime parameters
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

            # Prepare device attributes DataFrame if available
            device_attrs = None
            classifications_dict = safe_dict_access(device_classifications)
            if classifications_dict:
                device_attrs = pd.DataFrame.from_dict(
                    classifications_dict, orient="index"
                )
                device_attrs.reset_index(inplace=True)
                device_attrs.rename(columns={"index": "Door Number"}, inplace=True)

            # Use your existing process_uploaded_data function
            print("🔍 Calculating enhanced metrics...")
            enhanced_metrics = process_uploaded_data(df, device_attrs)

            metrics_dict = safe_dict_access(enhanced_metrics)
            print(f"✅ Calculated enhanced metrics: {safe_len(metrics_dict)} items")
            print(f"📊 Sample metrics: {safe_get_keys(metrics_dict, 5)}")

            return (
                show_style,  # yosai-custom-header
                stats_style,  # stats-panels-container
                "✅ Analysis complete! Enhanced metrics calculated.",  # status
            )
        else:
            return (
                show_style,  # yosai-custom-header
                {"display": "none"},  # stats-panels-container
                "❌ No processed data available",  # status
            )

    except Exception as e:
        print(f"❌ Error in enhanced analysis: {e}")
        import traceback

        traceback.print_exc()

        return (
            {"display": "block"},  # yosai-custom-header
            {"display": "none"},  # stats-panels-container
            f"❌ Analysis failed: {str(e)}",  # status
        )


def calculate_basic_metrics(df: pd.DataFrame) -> Dict[str, Union[int, str]]:
    """Fallback function to calculate basic metrics if enhanced component fails"""
    if df is None or df.empty:
        return {
            "total_events": 0,
            "date_range": "No data",
            "unique_users": 0,
            "unique_devices": 0,
        }

    timestamp_col = "Timestamp (Event Time)"
    user_col = "UserID (Person Identifier)"
    door_col = "DoorID (Device Name)"

    # FIXED: Properly typed metrics dictionary
    metrics: Dict[str, Union[int, str]] = {
        "total_events": len(df),
        "unique_users": df[user_col].nunique() if user_col in df.columns else 0,
        "unique_devices": df[door_col].nunique() if door_col in df.columns else 0,
        "date_range": "No date data",  # Default value
    }

    # FIXED: Safe assignment to properly typed dictionary
    if timestamp_col in df.columns:
        try:
            min_date = df[timestamp_col].min()
            max_date = df[timestamp_col].max()
            metrics["date_range"] = (
                f"{min_date.strftime('%d-%m-%Y')} - {max_date.strftime('%d-%m-%Y')}"
            )
        except Exception as e:
            print(f"Error formatting dates: {e}")
            metrics["date_range"] = "Date formatting error"
    else:
        metrics["date_range"] = "No date data"

    return metrics


def process_uploaded_data(df: pd.DataFrame, device_attrs: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Enhanced processing with all missing variables - FIXED VERSION"""
    from utils.enhanced_analytics import EnhancedDataProcessorComplete

    try:
        processor = EnhancedDataProcessorComplete()
        enhanced_metrics = processor.process_complete_analytics(df, device_attrs)

        print(f"✅ Complete analytics calculated: {len(enhanced_metrics)} metrics")
        print(f"📊 Key metrics: {list(enhanced_metrics.keys())[:10]}")

        return enhanced_metrics

    except Exception as e:
        print(f"❌ Error in complete analytics: {e}")
        import traceback
        traceback.print_exc()
        return {}


# Chart type selector callback
def update_main_chart(chart_type: str, processed_data: Any, device_attrs: Any):
    """Updated main analytics chart with complete metrics"""
    import pandas as pd
    from utils.enhanced_analytics import EnhancedDataProcessorComplete
    if go is None:
        raise ImportError("Plotly is not available")

    stats_component = component_instances.get("enhanced_stats")
    if not stats_component:
        print("❌ Enhanced stats component not available")
        return dash.no_update

    df = pd.DataFrame()
    if processed_data and isinstance(processed_data, dict) and "dataframe" in processed_data:
        df = pd.DataFrame(processed_data["dataframe"])
        ts_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        if ts_col in df.columns:
            df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

    processor = EnhancedDataProcessorComplete()
    complete_metrics = processor.process_complete_analytics(df, device_attrs)

    attrs_df = None
    if device_attrs and isinstance(device_attrs, dict):
        try:
            attrs_df = pd.DataFrame.from_dict(device_attrs, orient="index")
            attrs_df.reset_index(inplace=True)
            attrs_df.rename(columns={"index": "Door Number"}, inplace=True)
        except Exception:
            attrs_df = None

    if chart_type == "timeline":
        hourly_data = complete_metrics.get('hourly_distribution', {})
        if hourly_data:
            main_fig = go.Figure()
            hours = list(hourly_data.keys())
            counts = list(hourly_data.values())
            main_fig.add_trace(go.Scatter(
                x=hours, y=counts, mode='lines+markers',
                name='Activity Timeline',
                line=dict(color=COLORS["accent"], width=3)
            ))
            main_fig.update_layout(
                title="Activity Timeline",
                xaxis_title="Hour",
                yaxis_title="Events"
            )
            return main_fig

    elif chart_type == "daily":
        return stats_component.create_daily_trends_chart(df)
    elif chart_type == "heatmap":
        return stats_component.create_activity_heatmap(df)
    elif chart_type == "floor":
        floor_data = complete_metrics.get('floor_distribution', {})
        if floor_data:
            main_fig = go.Figure()
            main_fig.add_trace(go.Bar(
                x=list(floor_data.keys()),
                y=list(floor_data.values()),
                marker_color=COLORS["warning"],
                name='Floor Activity'
            ))
            main_fig.update_layout(
                title="Floor Activity",
                xaxis_title="Floor",
                yaxis_title="Events"
            )
            return main_fig

    return stats_component.create_hourly_activity_chart(df)


# Export callback
def handle_export_actions(
    csv_clicks: Optional[int],
    png_clicks: Optional[int],
    pdf_clicks: Optional[int],
    refresh_clicks: Optional[int],
    stats_data: Any,
    chart_fig: Any,
) -> Tuple[Any, Any, Any, str]:
    """Handle export actions and provide downloadable content"""
    from dash import ctx, no_update
    from utils.enhanced_analytics import create_enhanced_export_manager
    import plotly.io as pio

    if not ctx.triggered:
        return no_update, no_update, no_update, ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    manager = create_enhanced_export_manager()

    if button_id == "export-stats-csv":
        report = manager.export_comprehensive_report(stats_data or {}, format="CSV")
        if report.get("download_ready"):
            content = base64.b64decode(report["content"])
            data = dict(content=content, filename=report["filename"])
            return data, no_update, no_update, "📊 CSV export completed!"
    elif button_id == "export-charts-png":
        if chart_fig:
            try:
                img_bytes = pio.to_image(chart_fig, format="png")
                return (
                    no_update,
                    dict(content=img_bytes, filename="charts.png"),
                    no_update,
                    "📈 Charts exported as PNG!",
                )
            except Exception:
                pass
    elif button_id == "generate-pdf-report":
        report = manager.export_comprehensive_report(stats_data or {}, format="PDF")
        if report.get("download_ready"):
            data = dict(content=report["content"], filename=report["filename"])
            return no_update, no_update, data, "📄 PDF report generated!"
    elif button_id == "refresh-analytics":
        return no_update, no_update, no_update, "🔄 Analytics data refreshed!"

    return no_update, no_update, no_update, ""


# Node tap callback
@app.callback(
    Output("tap-node-data-output", "children"),
    Input("onion-graph", "tapNodeData"),
    prevent_initial_call=True,
)
def display_node_data(data: Optional[Dict[str, Any]]) -> str:
    """Display node information when tapped"""
    if not data:
        return "Upload a file and generate analysis. Tap any node for details."

    try:
        node_name = data.get("label", data.get("id", "Unknown"))
        device_type = data.get("type", "regular")

        details = [f"Selected: {node_name}"]

        if device_type == "entrance":
            details.append("🚪 Entrance/Exit Point")
        else:
            details.append("📱 Access Point")

        return " | ".join(details)

    except Exception as e:
        return f"Node information unavailable: {str(e)}"


def build_onion_security_model(
    doors_data: List[str], classifications: Dict[str, Any], processed_data: Any = None
) -> List[Dict]:
    """Build onion security model from access control data"""
    nodes = []
    edges = []

    security_colors = {
        "green": "#4CAF50",
        "yellow": "#FFC107",
        "orange": "#FF9800",
        "red": "#F44336",
    }

    security_levels = {"green": 1, "yellow": 3, "orange": 7, "red": 10}

    print(f"🏗️ Building onion model with {len(doors_data)} doors")

    entrance_nodes = []
    regular_nodes = []
    stair_nodes = []

    for i, door_id in enumerate(doors_data):
        classification = classifications.get(door_id, {})

        security_color = classification.get("security", "green")
        security_level = classification.get(
            "security_level", security_levels.get(security_color, 1)
        )

        is_entrance = classification.get("is_ee", False)
        is_stair = classification.get("is_stair", False)
        floor = classification.get("floor", 1)

        if is_entrance:
            node_type = "entrance"
            color = "#2E7D32"
            shape = "rectangle"
            size = 80
            entrance_nodes.append(door_id)
        elif is_stair:
            node_type = "stair"
            color = "#757575"
            shape = "triangle"
            size = 60
            stair_nodes.append(door_id)
        else:
            node_type = "device"
            color = security_colors.get(security_color, "#2196F3")
            shape = "ellipse"
            size = 50 + (security_level * 3)
            regular_nodes.append(door_id)

        layer = min(security_level // 3, 3)

        nodes_in_layer = len(
            [
                d
                for d in doors_data
                if classifications.get(d, {}).get("security_level", 1) // 3 == layer
            ]
        )
        layer_index = len(
            [
                d
                for d in doors_data[:i]
                if classifications.get(d, {}).get("security_level", 1) // 3 == layer
            ]
        )

        if nodes_in_layer > 0:
            angle = (layer_index * 2 * math.pi) / nodes_in_layer
        else:
            angle = i * 0.5

        radius = 200 - (layer * 50)

        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        if is_entrance:
            entrance_angle = (len(entrance_nodes) * 2 * math.pi) / max(
                len(
                    [
                        d
                        for d in doors_data
                        if classifications.get(d, {}).get("is_ee", False)
                    ]
                ),
                1,
            )
            x = 250 * math.cos(entrance_angle)
            y = 250 * math.sin(entrance_angle)

        node = {
            "data": {
                "id": str(door_id),
                "label": str(door_id)[:8],
                "type": node_type,
                "security_level": security_level,
                "security_color": security_color,
                "floor": floor,
                "is_entrance": is_entrance,
                "is_stair": is_stair,
                "layer": layer,
                "full_label": str(door_id),
            },
            "position": {"x": x, "y": y},
        }

        nodes.append(node)

    print(f"🔗 Creating connections between {len(nodes)} nodes")

    for i, door1 in enumerate(doors_data):
        class1 = classifications.get(door1, {})

        for j, door2 in enumerate(doors_data[i + 1 :], i + 1):
            class2 = classifications.get(door2, {})

            floor1 = int(class1.get("floor", 1))
            floor2 = int(class2.get("floor", 1))
            level1 = class1.get("security_level", 1)
            level2 = class2.get("security_level", 1)
            is_entrance1 = class1.get("is_ee", False)
            is_entrance2 = class2.get("is_ee", False)

            should_connect = False
            edge_type = "normal"

            if floor1 == floor2:
                if abs(level1 - level2) <= 3:
                    should_connect = True
                    edge_type = "floor"
                elif is_entrance1 or is_entrance2:
                    should_connect = True
                    edge_type = "entrance"

            elif abs(floor1 - floor2) == 1:
                if class1.get("is_stair") or class2.get("is_stair"):
                    should_connect = True
                    edge_type = "stair"

            elif is_entrance1 and level2 <= 5:
                should_connect = True
                edge_type = "access"

            elif is_entrance2 and level1 <= 5:
                should_connect = True
                edge_type = "access"

            if should_connect and (
                edge_type in ["entrance", "stair", "access"]
                or hash(f"{door1}_{door2}") % 3 == 0
            ):
                edge = {
                    "data": {
                        "id": f"edge_{door1}_{door2}",
                        "source": str(door1),
                        "target": str(door2),
                        "type": edge_type,
                        "weight": abs(level1 - level2) + 1,
                    }
                }
                edges.append(edge)

    print(f"✅ Created {len(nodes)} nodes and {len(edges)} edges")

    all_elements = nodes + edges

    high_security = [n for n in nodes if n["data"].get("security_level", 0) >= 8]
    if high_security:
        core_node = {
            "data": {
                "id": "security_core",
                "label": "CORE",
                "type": "core",
                "security_level": 10,
                "layer": 0,
            },
            "position": {"x": 0, "y": 0},
        }
        all_elements.append(core_node)

        for node in high_security[:3]:
            core_edge = {
                "data": {
                    "id": f"core_edge_{node['data']['id']}",
                    "source": "security_core",
                    "target": node["data"]["id"],
                    "type": "core",
                }
            }
            all_elements.append(core_edge)

    return all_elements


def test_simple_graph():
    """Test function to verify graph works with minimal data"""
    test_elements = [
        {"data": {"id": "entrance", "label": "Main Entrance", "type": "entrance"}},
        {"data": {"id": "lobby", "label": "Lobby", "type": "device"}},
        {"data": {"id": "secure", "label": "Secure Area", "type": "device"}},
        {"data": {"id": "edge1", "source": "entrance", "target": "lobby"}},
        {"data": {"id": "edge2", "source": "lobby", "target": "secure"}},
    ]
    return test_elements


# ============================================================================
# CONSOLIDATED ANALYTICS CALLBACKS
# ============================================================================

# Show/hide analytics container and update status message
@app.callback(
    [
        Output("analytic-stats-container", "style", allow_duplicate=True),
        Output("status-message-store", "data", allow_duplicate=True),
    ],
    Input("confirm-and-generate-button", "n_clicks"),
    [
        State("uploaded-file-store", "data"),
        State("processed-data-store", "data"),
        State("manual-door-classifications-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_enhanced_analysis_updated(n_clicks, file_data, processed_data, device_classifications):
    """Updated analysis callback for consolidated container"""

    if not n_clicks or not file_data:
        hide_style = {"display": "none"}
        return hide_style, "Click generate to start analysis"

    try:
        processed_dict = safe_dict_access(processed_data)
        if processed_dict and "dataframe" in processed_dict:
            df = pd.DataFrame(processed_dict["dataframe"])

            timestamp_col = "Timestamp (Event Time)"
            if timestamp_col in df.columns:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

            device_attrs = None
            classifications_dict = safe_dict_access(device_classifications)
            if classifications_dict:
                device_attrs = pd.DataFrame.from_dict(classifications_dict, orient="index")
                device_attrs.reset_index(inplace=True)
                device_attrs.rename(columns={"index": "Door Number"}, inplace=True)

            enhanced_metrics = process_uploaded_data(df, device_attrs)

            show_style = {
                "display": "block",
                "width": "95%",
                "margin": "20px auto",
                "backgroundColor": COLORS["background"],
                "borderRadius": "12px",
                "padding": "20px",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            }

            return show_style, "Analysis complete! Enhanced metrics calculated."

        else:
            hide_style = {"display": "none"}
            return hide_style, "Error: Invalid processed data format"

    except Exception as e:
        print(f"Error in analysis: {e}")
        hide_style = {"display": "none"}
        return hide_style, f"Error: {str(e)}"


# Store enhanced stats data for consolidated container
@app.callback(
    Output("enhanced-stats-data-store", "data"),
    Input("status-message-store", "data"),
    State("processed-data-store", "data"),
    State("manual-door-classifications-store", "data"),
    prevent_initial_call=True,
)
def update_enhanced_stats_store_fixed(status_message, processed_data, device_classifications):
    """Store enhanced stats data for the consolidated display"""

    if not status_message or "Analysis complete" not in str(status_message):
        return {}

    try:
        processed_dict = safe_dict_access(processed_data)
        if not processed_dict or "dataframe" not in processed_dict:
            return {}

        df = pd.DataFrame(processed_dict["dataframe"])

        timestamp_col = "Timestamp (Event Time)"
        if timestamp_col in df.columns:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

        device_attrs = None
        classifications_dict = safe_dict_access(device_classifications)
        if classifications_dict:
            device_attrs = pd.DataFrame.from_dict(classifications_dict, orient="index")
            device_attrs.reset_index(inplace=True)
            device_attrs.rename(columns={"index": "Door Number"}, inplace=True)

        enhanced_metrics = process_uploaded_data(df, device_attrs)
        metrics_dict = safe_dict_access(enhanced_metrics)

        if not metrics_dict:
            return {}

        print(f"✅ Enhanced stats stored: {len(metrics_dict)} metrics")
        return metrics_dict

    except Exception as e:
        print(f"❌ Error storing enhanced stats: {e}")
        return {}


# Update ALL analytics in the consolidated container
@app.callback(
    [
        Output("analytic-stats-container", "style"),
        Output("total-access-events-H1", "children"),
        Output("event-date-range-P", "children"),
        Output("events-trend-indicator", "children"),
        Output("avg-events-per-day", "children"),
        Output("stats-unique-users", "children"),
        Output("stats-avg-events-per-user", "children"),
        Output("stats-most-active-user", "children"),
        Output("stats-devices-per-user", "children"),
        Output("total-devices-count", "children"),
        Output("entrance-devices-count", "children"),
        Output("high-security-devices", "children"),
        Output("device-utilization-rate", "children"),
        Output("peak-hour-display", "children"),
        Output("peak-day-display", "children"),
        Output("busiest-floor", "children"),
        Output("weekend-vs-weekday", "children"),
        Output("security-score-insight", "children"),
        Output("anomaly-insight", "children"),
        Output("compliance-score", "children"),
        Output("entry-exit-ratio", "children"),
        Output("traffic-pattern-insight", "children"),
        Output("behavioral-insight", "children"),
        Output("efficiency-insight", "children"),
        Output("trend-insight", "children"),
        Output("unique-card-holders", "children"),
        Output("avg-session-duration", "children"),
        Output("peak-concurrent-users", "children"),
        Output("security-events-count", "children"),
        Output("maintenance-alerts", "children"),
        Output("system-uptime", "children"),
        Output("most-active-devices-table-body", "children"),
    ],
    [
        Input("enhanced-stats-data-store", "data"),
        Input("confirm-and-generate-button", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_consolidated_analytics(enhanced_metrics, generate_clicks):
    """Update ALL analytics in the consolidated container"""

    if not enhanced_metrics or not generate_clicks:
        hide_style = {"display": "none"}
        # Return placeholders matching the number of outputs
        # There are 31 outputs besides the style, with the last
        # being the most-active-devices table rows.
        empty_values = ["N/A"] * 30
        return [hide_style] + empty_values + [[]]

    show_style = {
        "display": "block",
        "width": "95%",
        "margin": "20px auto",
        "backgroundColor": COLORS["background"],
        "borderRadius": "12px",
        "padding": "20px",
        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    }

    metrics = enhanced_metrics or {}

    total_events = f"{metrics.get('total_events', 0):,}"
    date_range = metrics.get('date_range', 'No data available')

    events_count = metrics.get('total_events', 0)
    if events_count > 1000:
        trend_indicator = "📈 High Activity"
    elif events_count > 100:
        trend_indicator = "📊 Normal Activity"
    else:
        trend_indicator = "📉 Low Activity"

    avg_per_day = f"Avg: {metrics.get('avg_events_per_day', 0):.1f} events/day"

    unique_users = f"Users: {metrics.get('unique_users', 0):,}"
    avg_events_user = f"Avg: {metrics.get('avg_events_per_user', 0):.1f} events/user"
    most_active = f"Most active: {metrics.get('most_active_user', 'N/A')}"
    devices_per_user = f"Avg: {metrics.get('avg_users_per_device', 0):.2f} users/device"

    total_devices = f"Total: {metrics.get('num_devices', 0):,} devices"
    entrance_devices = f"Entrances: {metrics.get('entrance_devices_count', 0):,}"
    high_security = f"High security: {metrics.get('high_security_devices', 0):,}"
    utilization = f"Utilization: {metrics.get('device_utilization_rate', 0):.1f}%"

    peak_hour = f"Peak hour: {metrics.get('peak_hour', 'N/A')}"
    peak_day = f"Peak day: {metrics.get('peak_day', 'N/A')}"
    busiest_floor_val = f"Busiest floor: {metrics.get('busiest_floor', 'N/A')}"
    weekend_weekday = f"Weekend vs Weekday: {metrics.get('weekend_vs_weekday_ratio', 'N/A')}"

    security_score = f"Security score: {metrics.get('security_score', 0):.1f}%"
    anomalies = f"Anomalies: {metrics.get('anomaly_count', 0)} detected"
    compliance = f"Compliance: {metrics.get('compliance_score', 0):.1f}%"
    entry_exit = f"Entry/Exit: {metrics.get('entry_exit_ratio', 'N/A')}"

    traffic_pattern = f"Pattern: {metrics.get('dominant_pattern', 'Normal business hours')}"
    behavioral = f"Behavior: {metrics.get('behavioral_pattern', 'Standard access patterns')}"
    efficiency = f"Efficiency: {metrics.get('efficiency_score', 0):.1f}%"
    trend = f"Trend: {metrics.get('overall_trend', 'Stable')}"

    card_holders = f"Card holders: {metrics.get('unique_card_holders', 0):,}"
    session_duration = f"Avg session: {metrics.get('avg_session_duration', 0):.1f} min"
    concurrent_users = f"Peak concurrent: {metrics.get('peak_concurrent_users', 0):,}"
    security_events = f"Security events: {metrics.get('security_events_count', 0):,}"
    maintenance = f"Maintenance: {metrics.get('maintenance_alerts', 0):,}"
    uptime = f"Uptime: {metrics.get('system_uptime', 100):.1f}%"

    table_rows = []
    most_active_devices = metrics.get('most_active_devices', [])
    if isinstance(most_active_devices, list) and most_active_devices:
        for i, device in enumerate(most_active_devices[:5]):
            if isinstance(device, dict):
                device_name = device.get('device', f'Device {i+1}')
                event_count = device.get('events')

            elif isinstance(device, (list, tuple)) and len(device) >= 2:
                device_name = device[0]
                event_count = device[1]
            else:
                device_name = str(device)
                event_count = None

            if not isinstance(event_count, (int, float)):
                event_count = 0

            table_rows.append(
                html.Tr([
                    html.Td(
                        device_name,
                        style={"padding": "5px", "color": COLORS["text_primary"]},
                    ),
                    html.Td(
                        f"{int(event_count):,}",
                        style={"padding": "5px", "color": COLORS["accent"]},
                    ),
                ])
            )

    if not table_rows:
        table_rows = [
            html.Tr([
                html.Td("No device data", style={"padding": "5px", "color": COLORS["text_secondary"]}),
                html.Td("0", style={"padding": "5px", "color": COLORS["text_secondary"]}),
            ])
        ]

    return [
        show_style,
        total_events, date_range, trend_indicator, avg_per_day,
        unique_users, avg_events_user, most_active, devices_per_user,
        total_devices, entrance_devices, high_security, utilization,
        peak_hour, peak_day, busiest_floor_val, weekend_weekday,
        security_score, anomalies, compliance, entry_exit,
        traffic_pattern, behavioral, efficiency, trend,
        card_holders, session_duration, concurrent_users, security_events, maintenance, uptime,
        table_rows,
    ]


# Charts update callback
@app.callback(
    [
        Output("main-analytics-chart", "figure"),
        Output("security-pie-chart", "figure"),
        Output("device-distribution-chart", "figure"),
    ],
    [
        Input("enhanced-stats-data-store", "data"),
        Input("chart-type-selector", "value"),
    ],
    State("processed-data-store", "data"),
    prevent_initial_call=True,
)
def update_consolidated_charts(enhanced_metrics, chart_type, processed_data):
    """Update all charts in the consolidated container"""

    import pandas as pd
    if go is None:
        raise ImportError("Plotly is not available")

    if not enhanced_metrics:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLORS["surface"],
            plot_bgcolor=COLORS["background"],
            font_color=COLORS["text_primary"],
            title="No data available",
        )
        return empty_fig, empty_fig, empty_fig

    metrics = enhanced_metrics or {}
    df = pd.DataFrame()
    if processed_data and isinstance(processed_data, dict) and "dataframe" in processed_data:
        df = pd.DataFrame(processed_data["dataframe"])
        ts_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        if ts_col in df.columns:
            df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

    main_fig = go.Figure()

    if chart_type == "timeline":
        hourly_data = metrics.get('hourly_distribution', {})
        if hourly_data:
            hours = list(hourly_data.keys())
            counts = list(hourly_data.values())
            main_fig.add_trace(go.Scatter(x=hours, y=counts, mode='lines+markers', name='Activity Timeline', line=dict(color=COLORS["accent"], width=3)))
            main_fig.update_layout(title="Activity Timeline", xaxis_title="Hour", yaxis_title="Events")
    elif chart_type == "hourly":
        hourly_data = metrics.get('hourly_distribution', {})
        if hourly_data:
            main_fig.add_trace(go.Bar(x=list(hourly_data.keys()), y=list(hourly_data.values()), marker_color=COLORS["accent"], name='Hourly Activity'))
            main_fig.update_layout(title="Hourly Distribution", xaxis_title="Hour", yaxis_title="Events")
    elif chart_type == "daily":
        daily_data = metrics.get('daily_distribution', {})
        if daily_data:
            main_fig.add_trace(go.Bar(x=list(daily_data.keys()), y=list(daily_data.values()), marker_color=COLORS["success"], name='Daily Activity'))
            main_fig.update_layout(title="Daily Patterns", xaxis_title="Day", yaxis_title="Events")
    elif chart_type == "floor":
        floor_data = metrics.get('floor_distribution', {})
        if floor_data:
            main_fig.add_trace(go.Bar(x=list(floor_data.keys()), y=list(floor_data.values()), marker_color=COLORS["warning"], name='Floor Activity'))
            main_fig.update_layout(title="Floor Activity", xaxis_title="Floor", yaxis_title="Events")
    elif chart_type == "heatmap":
        stats_component = component_instances.get("enhanced_stats")
        if stats_component is not None and not df.empty:
            main_fig = stats_component.create_activity_heatmap(df)
        else:
            main_fig.update_layout(title="Activity Heatmap")

    main_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["background"],
        font_color=COLORS["text_primary"],
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
    )

    security_fig = go.Figure()
    security_distribution = metrics.get('security_level_distribution', {})
    if security_distribution:
        security_fig.add_trace(go.Pie(labels=list(security_distribution.keys()), values=list(security_distribution.values()), hole=.3, marker_colors=[COLORS["success"], COLORS["warning"], COLORS["critical"]]))
    security_fig.update_layout(title="Security Levels", template="plotly_dark", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["background"], font_color=COLORS["text_primary"], height=180, margin=dict(l=20, r=20, t=30, b=20))

    device_fig = go.Figure()
    device_types = metrics.get('device_type_distribution', {})
    if device_types:
        device_fig.add_trace(go.Pie(labels=list(device_types.keys()), values=list(device_types.values()), hole=.3, marker_colors=[COLORS["accent"], COLORS["accent_light"], COLORS["success"]]))
    device_fig.update_layout(title="Device Types", template="plotly_dark", paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["background"], font_color=COLORS["text_primary"], height=180, margin=dict(l=20, r=20, t=30, b=20))

    return main_fig, security_fig, device_fig


# Export callbacks for consolidated container
@app.callback(
    Output("export-status", "children"),
    [
        Input("export-csv-btn", "n_clicks"),
        Input("export-charts-btn", "n_clicks"),
        Input("export-report-btn", "n_clicks"),
    ],
    State("enhanced-stats-data-store", "data"),
    prevent_initial_call=True,
)
def handle_exports(csv_clicks, charts_clicks, report_clicks, enhanced_metrics):
    """Handle export button clicks"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Ready to export"

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "export-csv-btn" and csv_clicks:
        return "CSV export initiated..."
    elif button_id == "export-charts-btn" and charts_clicks:
        return "Chart export initiated..."
    elif button_id == "export-report-btn" and report_clicks:
        return "Report generation initiated..."

    return "Ready to export"


# Manual refresh callback
@app.callback(
    Output("enhanced-stats-data-store", "data", allow_duplicate=True),
    Input("refresh-stats-btn", "n_clicks"),
    State("processed-data-store", "data"),
    State("manual-door-classifications-store", "data"),
    prevent_initial_call=True,
)
def refresh_analytics_data(refresh_clicks, processed_data, device_classifications):
    """Refresh analytics data when refresh button is clicked"""

    if not refresh_clicks:
        return dash.no_update

    try:
        processed_dict = safe_dict_access(processed_data)
        if not processed_dict or "dataframe" not in processed_dict:
            return {}

        df = pd.DataFrame(processed_dict["dataframe"])

        timestamp_col = "Timestamp (Event Time)"
        if timestamp_col in df.columns:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

        device_attrs = None
        classifications_dict = safe_dict_access(device_classifications)
        if classifications_dict:
            device_attrs = pd.DataFrame.from_dict(classifications_dict, orient="index")
            device_attrs.reset_index(inplace=True)
            device_attrs.rename(columns={"index": "Door Number"}, inplace=True)

        enhanced_metrics = process_uploaded_data(df, device_attrs)

        return safe_dict_access(enhanced_metrics) or {}

    except Exception as e:
        print(f"Error refreshing analytics: {e}")
        return {}

