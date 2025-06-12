"""Legacy app.py - Keep only functions imported by app_factory.py
This file will eventually be fully deprecated in favor of app_factory.py
"""

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
from typing import Dict, Any, Union, Optional, List, Tuple
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional cytoscape support
try:
    import dash_cytoscape as cyto  # type: ignore
    CYTOSCAPE_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    cyto = None  # type: ignore
    CYTOSCAPE_AVAILABLE = False

from ui.themes.style_config import COLORS, DEBUG_PANEL_STYLE

# Try to import optional components used by the layout helpers
components_available = {"main_layout": False, "cytoscape": CYTOSCAPE_AVAILABLE}
try:
    from ui.pages.main_page import create_main_layout
    components_available["main_layout"] = True
except Exception:  # pragma: no cover - optional component
    create_main_layout = None

try:
    from ui.components.graph import create_graph_container
except Exception:  # pragma: no cover - optional component
    create_graph_container = None


def make_json_serializable(data: Any) -> Union[Dict[str, Any], List[Any], int, float, str, None]:
    """Convert numpy data types to native Python types for JSON serialization."""
    if isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    return data


def create_fixed_layout_with_required_elements(app_instance, main_logo_path: str, icon_upload_default: str):
    """Create layout that maintains current design but includes all required callback elements"""
    print(">> Creating FIXED layout with all required elements...")

    base_layout = _load_base_layout(app_instance, main_logo_path, icon_upload_default)

    if base_layout:
        return _enhance_existing_layout(base_layout, main_logo_path, icon_upload_default)
    else:
        return _create_complete_fallback_layout(app_instance, main_logo_path, icon_upload_default)


def _load_base_layout(app_instance, main_logo_path: str, icon_upload_default: str):
    """Attempt to load the main layout, with error handling"""
    if not (components_available.get("main_layout") and create_main_layout):
        print(">> Main layout not available, will create fallback")
        return None

    try:
        base_layout = create_main_layout(app_instance, main_logo_path, icon_upload_default)
        print(">> Base main layout loaded successfully")
        return base_layout
    except Exception as e:  # pragma: no cover - defensive
        print(f"!! Error loading main layout: {e}")
        return None


def _enhance_existing_layout(base_layout, main_logo_path: str, icon_upload_default: str):
    """Add missing elements to existing layout while preserving design"""
    try:
        base_children = _extract_layout_children(base_layout)
        existing_ids = _collect_all_element_ids(base_children)
        print(f">> Found existing IDs: {len(existing_ids)} total")

        enhanced_children = _add_required_missing_elements(base_children, existing_ids)
        _add_missing_callback_elements(enhanced_children, existing_ids)

        print(">> Successfully enhanced existing layout")
        return _wrap_final_layout(enhanced_children, base_layout)
    except Exception as e:  # pragma: no cover - defensive
        print(f"!! Error enhancing layout: {e}")
        return _create_complete_fallback_layout(None, main_logo_path, icon_upload_default)


def _extract_layout_children(base_layout):
    """Extract children from layout, handling different structure types"""
    if hasattr(base_layout, "children"):
        children = base_layout.children
        return list(children) if isinstance(children, list) else [children] if children else []
    return []


def _collect_all_element_ids(elements):
    """Recursively collect all element IDs from layout tree"""
    existing_ids = set()

    def collect_ids(element):
        if hasattr(element, "id") and element.id:
            existing_ids.add(element.id)
        if hasattr(element, "children"):
            children = element.children if isinstance(element.children, list) else [element.children] if element.children else []
            for child in children:
                collect_ids(child)

    for element in elements:
        collect_ids(element)

    return existing_ids


def _add_required_missing_elements(base_children, existing_ids):
    """Add specific missing elements that are required for callbacks"""
    enhanced_children = list(base_children)

    required_elements = {
        "enhanced-stats-header": _create_fallback_enhanced_header,
        "stats-panels-container": _create_fallback_stats_container,
        "advanced-analytics-panels-container": _create_advanced_analytics_container,
        "analytics-section": _create_fallback_analytics_section,
        "charts-section": _create_fallback_charts_section,
        "export-section": _create_fallback_export_section,
        "graph-output-container": _create_graph_output_container,
        "mini-graph-container": _create_mini_graph_container,
        "debug-panel": create_debug_panel,
    }

    for element_id, creator_func in required_elements.items():
        if element_id not in existing_ids and creator_func:
            print(f">> Adding missing element: {element_id}")
            enhanced_children.append(creator_func())

    return enhanced_children


def _create_graph_output_container():
    """Create graph output container if needed"""
    try:
        return create_graph_container() if create_graph_container else html.Div(
            id="graph-output-container", style={"display": "none"}
        )
    except Exception:
        return html.Div(id="graph-output-container", style={"display": "none"})


def _wrap_final_layout(children, base_layout=None):
    """Wrap children in final layout div with appropriate styling"""
    style = _get_layout_style(base_layout)
    return html.Div(children, style=style)


def _get_layout_style(base_layout):
    """Get appropriate styling for the layout"""
    if base_layout and hasattr(base_layout, "style"):
        return base_layout.style

    return {
        "backgroundColor": COLORS["background"],
        "minHeight": "100vh",
        "padding": "20px",
        "fontFamily": "Inter, sans-serif",
    }


def _create_complete_fallback_layout(app_instance, main_logo_path: str, icon_upload_default: str):
    """Create complete layout from scratch when base layout unavailable"""
    print(">> Creating complete fallback layout")

    base_children = [
        _create_fallback_header(main_logo_path),
        _create_fallback_upload_section(icon_upload_default),
        _create_fallback_stats_container(),
        _create_fallback_analytics_section(),
        create_debug_panel() if create_debug_panel else html.Div(),
    ]

    existing_ids = _collect_all_element_ids(base_children)
    _add_missing_callback_elements(base_children, existing_ids)

    return _wrap_final_layout(base_children)


def _create_fallback_header(main_logo_path: str):
    """Create fallback header component"""
    return html.Div(
        [html.Img(src=main_logo_path, style={"height": "40px"}), html.H1("Yōsai Analytics Dashboard", id="dashboard-title")],
        style={"padding": "20px", "borderBottom": f"1px solid {COLORS['border']}"},
    )


def _create_fallback_upload_section(icon_upload_default: str):
    """Create fallback upload section"""
    return html.Div(
        [
            html.H2("Upload Data"),
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    html.Img(src=icon_upload_default, style={"height": "50px"}),
                    html.P("Drag and Drop or Select Files"),
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
            ),
        ]
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


def _create_advanced_analytics_container():
    """Create advanced analytics panels container with all required elements"""
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
                    ),
                    html.P(
                        id="weekend-vs-weekday",
                        children="Weekend vs Weekday: Loading...",
                        style={"color": COLORS["text_secondary"]},
                    ),
                ],
                style=panel_style,
            ),
            html.Div(
                [
                    html.H3("Security Overview", style={"color": COLORS["text_primary"]}),
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
            html.Div(
                [
                    html.H3("Analytics Insights", style={"color": COLORS["text_primary"]}),
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
    if CYTOSCAPE_AVAILABLE and cyto is not None:
        mini_graph = cyto.Cytoscape(
            id="mini-onion-graph",
            style={"width": "100%", "height": "300px"},
            elements=[],
            wheelSensitivity=1,
        )

    return html.Div(id="mini-graph-container", style={"display": "none"}, children=[mini_graph])


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
        "enhanced-total-access-events-H1",
        "enhanced-event-date-range-P",
        "events-trend-indicator",
        "avg-events-per-day",
        "most-active-user",
        "avg-user-activity",
        "unique-users-today",
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
            elif element_id in ["main-analytics-chart", "security-pie-chart", "heatmap-chart"]:
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
            html.H4("DEBUG: Enhanced Analytics", style={"color": "#fff", "margin": "0 0 10px 0"}),
            html.P(id="debug-metrics-count", style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"}),
            html.P(id="debug-metrics-keys", style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"}),
            html.P(id="debug-processed-data", style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"}),
            html.P(id="debug-calculation-status", style={"color": "#ccc", "fontSize": "0.8rem", "margin": "2px 0"}),
        ],
        style={
            **DEBUG_PANEL_STYLE,
            "position": "fixed",
            "top": "10px",
            "right": "10px",
            "zIndex": "9999",
            "maxWidth": "300px",
        },
    )


CALLBACKS_REGISTERED = False


def register_all_callbacks_safely(app: dash.Dash) -> None:
    """Register callbacks with conflict prevention"""
    global CALLBACKS_REGISTERED

    if CALLBACKS_REGISTERED:
        print("✅ Callbacks already registered - skipping duplicate registration")
        return

    try:
        print("🔄 Registering callbacks...")

        from ui.components.upload_handlers import UploadHandlers
        from ui.components.upload import create_enhanced_upload_component

        icon_paths = {
            "default": app.get_asset_url("upload_file_csv_icon.png"),
            "success": app.get_asset_url("upload_file_csv_icon_success.png"),
            "fail": app.get_asset_url("upload_file_csv_icon_fail.png"),
        }

        upload_component = create_enhanced_upload_component(
            icon_paths["default"], icon_paths["success"], icon_paths["fail"]
        )
        upload_handlers = UploadHandlers(
            app,
            upload_component,
            icon_paths,
            secure=True,
            max_file_size=50 * 1024 * 1024,
        )
        upload_handlers.register_callbacks()
        print("   ✅ Upload callbacks registered")

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

        CALLBACKS_REGISTERED = True
        print("🎉 All callbacks registered successfully - no conflicts!")

    except Exception as e:  # pragma: no cover - defensive
        print(f"❌ Error registering callbacks: {e}")
        CALLBACKS_REGISTERED = False
        raise


def register_enhanced_callbacks_once(app: dash.Dash) -> None:
    """Compatibility wrapper for production imports."""
    register_all_callbacks_safely(app)


import warnings
warnings.warn(
    "Direct execution of app.py is deprecated. Use 'python run.py' instead.",
    DeprecationWarning,
    stacklevel=2,
)

print("⚠️ app.py loaded as legacy module. Use 'python run.py' for new unified entry point.")
