# enhanced_stats.py - FIXED VERSION
# Consolidates ALL statistics and graphs under 'analytic-stats-container'

from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from ui.themes.style_config import COLORS, SPACING, BORDER_RADIUS, SHADOWS, TYPOGRAPHY
from config.settings import REQUIRED_INTERNAL_COLUMNS, SECURITY_LEVELS


class EnhancedStatsComponent:
    """Enhanced statistics component with comprehensive metrics and visualizations"""

    def __init__(self):
        self.panel_style_base = {
            "flex": "1",
            "padding": "20px",
            "margin": "0 10px",
            "backgroundColor": COLORS["surface"],
            "borderRadius": "8px",
            "textAlign": "center",
            "boxShadow": "2px 2px 5px rgba(0,0,0,0.2)",
            "minHeight": "200px",
        }

        # Chart theme matching app colors
        self.chart_theme = {
            "layout": {
                "paper_bgcolor": COLORS["surface"],
                "plot_bgcolor": COLORS["background"],
                "font": {
                    "color": COLORS["text_primary"],
                    "family": "Inter, sans-serif",
                },
                "colorway": [
                    COLORS["accent"],
                    COLORS["success"],
                    COLORS["warning"],
                    COLORS["critical"],
                    COLORS["accent_light"],
                    "#66BB6A",
                    "#FFA726",
                    "#EF5350",
                ],
            }
        }

    def create_enhanced_stats_container(self):
        """Creates the CONSOLIDATED analytics stats container with ALL statistics and graphs"""
        return html.Div(
            id="analytic-stats-container",  # MAIN CONTAINER FOR ALL STATS
            style={
                "display": "none",  # Initially hidden, shown when data is ready
                "width": "95%",
                "margin": "20px auto",
                "backgroundColor": COLORS["background"],
                "borderRadius": "12px",
                "padding": "20px",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
            },
            children=[
                # Header Section
                self.create_analytics_header(),
                
                # Row 1: Core Statistics (Access Events, Users, Devices)
                html.Div(
                    id="core-stats-row",
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "30px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        self.create_access_events_panel(),
                        self.create_user_analytics_panel(),
                        self.create_device_analytics_panel(),
                    ],
                ),
                
                # Row 2: Activity & Security Analytics
                html.Div(
                    id="activity-security-row",
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "30px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        self.create_peak_activity_panel(),
                        self.create_security_overview_panel(),
                        self.create_insights_panel(),
                    ],
                ),
                
                # Row 3: Charts and Visualizations
                html.Div(
                    id="charts-visualization-row",
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "30px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        self.create_main_chart_panel(),
                        self.create_secondary_charts_panel(),
                    ],
                ),
                
                # Row 4: Additional Metrics and Export Tools
                html.Div(
                    id="additional-metrics-row",
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "20px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        self.create_additional_metrics_panel(),
                        self.create_export_tools_panel(),
                    ],
                ),
                
                # Hidden data stores and components
                dcc.Store(id="enhanced-stats-data-store"),
                dcc.Store(id="chart-data-store"),
                dcc.Interval(
                    id="stats-refresh-interval",
                    interval=30 * 1000,  # 30 seconds
                    n_intervals=0,
                    disabled=True,
                ),
            ]
        )

    def create_analytics_header(self):
        """Creates the analytics header section"""
        return html.Div(
            id="analytics-header-section",
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "30px",
                "padding": "15px 20px",
                "backgroundColor": COLORS["surface"],
                "borderRadius": "8px",
                "border": f"1px solid {COLORS['border']}",
            },
            children=[
                html.Div([
                    html.H2(
                        "📊 Enhanced Analytics Dashboard",
                        style={
                            "margin": "0",
                            "color": COLORS["text_primary"],
                            "fontSize": "1.8rem",
                            "fontWeight": "600",
                        }
                    ),
                    html.P(
                        id="analytics-status-text",
                        children="Real-time analytics and insights",
                        style={
                            "margin": "5px 0 0 0",
                            "color": COLORS["text_secondary"],
                            "fontSize": "0.9rem",
                        }
                    ),
                ]),
                html.Div([
                    html.Button(
                        "🔄 Refresh",
                        id="refresh-stats-btn",
                        style={
                            "padding": "8px 16px",
                            "backgroundColor": COLORS["accent"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "marginRight": "10px",
                            "cursor": "pointer",
                        }
                    ),
                    html.Button(
                        "📊 Export",
                        id="export-analytics-btn",
                        style={
                            "padding": "8px 16px",
                            "backgroundColor": COLORS["success"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        }
                    ),
                ]),
            ]
        )


    # ------------------------------------------------------------------
    # Chart helper methods
    # ------------------------------------------------------------------

    def _create_empty_chart(self, message):
        """Return a blank figure with a message."""
        fig = go.Figure()
        fig.update_layout(
            annotations=[
                dict(
                    text=message,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color=COLORS["text_secondary"]),
                )
            ],
            **self.chart_theme["layout"],
        )
        return fig

    def create_activity_heatmap(self, df):
        """Create day/hour activity heatmap."""
        if df is None or df.empty:
            return self._create_empty_chart("No data for heatmap")

        ts_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        if ts_col not in df.columns:
            return self._create_empty_chart("Timestamp data not available")

        dfc = df.copy()
        dfc["Hour"] = dfc[ts_col].dt.hour
        dfc["DayOfWeek"] = dfc[ts_col].dt.day_name()

        heatmap_data = dfc.groupby(["DayOfWeek", "Hour"]).size().unstack(fill_value=0)
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = heatmap_data.reindex(days_order)

        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=list(range(24)),
                y=days_order,
                colorscale="Blues",
                text=heatmap_data.values,
                texttemplate="%{text}",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title="Activity Heatmap (Day vs Hour)",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            **self.chart_theme["layout"],
        )

        return fig

    def create_access_events_panel(self):
        """Access Events Panel - Core Statistics"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("🚪 Access Events", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.H1(
                    id="total-access-events-H1",
                    children="0",
                    style={"color": COLORS["accent"], "margin": "10px 0", "fontSize": "2.5rem"}
                ),
                html.P(
                    id="event-date-range-P",
                    children="No data available",
                    style={"color": COLORS["text_secondary"], "fontSize": "0.9rem", "marginBottom": "15px"}
                ),
                html.Div([
                    html.P(id="events-trend-indicator", children="📈 Analyzing...", style={"margin": "5px 0"}),
                    html.P(id="avg-events-per-day", children="Avg: 0 events/day", style={"margin": "5px 0"}),
                ]),
                html.Table([html.Tbody(id="most-active-devices-table-body")], style={"width": "100%", "marginTop": "10px"}),
            ]
        )

    def create_user_analytics_panel(self):
        """User Analytics Panel"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("👥 User Analytics", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.P(id="stats-unique-users", children="Users: 0", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="stats-avg-events-per-user", children="Avg: 0 events/user", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="stats-most-active-user", children="Most active: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="stats-devices-per-user", children="Avg: 0 users/device", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                ]),
            ]
        )

    def create_device_analytics_panel(self):
        """Device Analytics Panel"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("🔧 Device Analytics", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.P(id="total-devices-count", children="Total: 0 devices", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="entrance-devices-count", children="Entrances: 0", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="high-security-devices", children="High security: 0", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="device-utilization-rate", children="Utilization: 0%", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                ]),
            ]
        )

    def create_peak_activity_panel(self):
        """Peak Activity Analysis Panel"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("⏰ Peak Activity", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.P(id="peak-hour-display", children="Peak hour: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="peak-day-display", children="Peak day: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="busiest-floor", children="Busiest floor: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="weekend-vs-weekday", children="Weekend vs Weekday: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                ]),
            ]
        )

    def create_security_overview_panel(self):
        """Security Overview Panel"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("🔒 Security Overview", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.P(id="security-score-insight", children="Security score: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="anomaly-insight", children="Anomalies: 0 detected", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="compliance-score", children="Compliance: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="entry-exit-ratio", children="Entry/Exit: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                ]),
            ]
        )

    def create_insights_panel(self):
        """Traffic and Behavioral Insights Panel"""
        return html.Div(
            style=self.panel_style_base,
            children=[
                html.H3("🧠 Insights", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.P(id="traffic-pattern-insight", children="Analyzing patterns...", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="behavioral-insight", children="Behavioral analysis: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="efficiency-insight", children="Efficiency: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                    html.P(id="trend-insight", children="Trends: N/A", style={"margin": "8px 0", "color": COLORS["text_secondary"]}),
                ]),
            ]
        )

    def create_main_chart_panel(self):
        """Main Chart Panel - Time Series and Activity Charts"""
        return html.Div(
            style={
                **self.panel_style_base,
                "flex": "2",  # Takes more space
                "minHeight": "400px",
            },
            children=[
                html.H3("📈 Activity Charts", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    dcc.Dropdown(
                        id="chart-type-selector",
                        options=[
                            {"label": "📊 Activity Timeline", "value": "timeline"},
                            {"label": "📈 Hourly Distribution", "value": "hourly"},
                            {"label": "📅 Daily Patterns", "value": "daily"},
                            {"label": "🏢 Floor Activity", "value": "floor"},
                            {"label": "🔥 Activity Heatmap", "value": "heatmap"},
                        ],
                        value="timeline",
                        style={"marginBottom": "15px", "color": COLORS["text_primary"]},
                    ),
                    dcc.Graph(
                        id="main-analytics-chart",
                        style={"height": "350px"},
                        config={"displayModeBar": True, "displaylogo": False}
                    ),
                ]),
            ]
        )

    def create_secondary_charts_panel(self):
        """Secondary Charts Panel - Pie Charts and Distributions"""
        return html.Div(
            style={
                **self.panel_style_base,
                "flex": "1",
                "minHeight": "400px",
            },
            children=[
                html.H3("🥧 Distributions", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    dcc.Graph(
                        id="security-pie-chart",
                        style={"height": "180px", "marginBottom": "10px"},
                        config={"displayModeBar": False}
                    ),
                    dcc.Graph(
                        id="heatmap-chart",
                        style={"height": "180px"},
                        config={"displayModeBar": False}
                    ),
                ]),
            ]
        )

    def create_additional_metrics_panel(self):
        """Additional Metrics Panel"""
        return html.Div(
            style={
                **self.panel_style_base,
                "flex": "2",
            },
            children=[
                html.H3("📊 Additional Metrics", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "15px"},
                    children=[
                        html.Div([
                            html.P(id="unique-card-holders", children="Card holders: 0", style={"margin": "5px 0"}),
                            html.P(id="avg-session-duration", children="Avg session: 0 min", style={"margin": "5px 0"}),
                            html.P(id="peak-concurrent-users", children="Peak concurrent: 0", style={"margin": "5px 0"}),
                        ]),
                        html.Div([
                            html.P(id="security-events-count", children="Security events: 0", style={"margin": "5px 0"}),
                            html.P(id="maintenance-alerts", children="Maintenance: 0", style={"margin": "5px 0"}),
                            html.P(id="system-uptime", children="Uptime: 100%", style={"margin": "5px 0"}),
                        ]),
                    ]
                ),
            ]
        )

    def create_export_tools_panel(self):
        """Export Tools Panel"""
        return html.Div(
            style={
                **self.panel_style_base,
                "flex": "1",
            },
            children=[
                html.H3("📤 Export Tools", style={"color": COLORS["text_primary"], "marginBottom": "15px"}),
                html.Div([
                    html.Button(
                        "📊 Export CSV",
                        id="export-csv-btn",
                        style={
                            "width": "100%",
                            "padding": "10px",
                            "margin": "5px 0",
                            "backgroundColor": COLORS["success"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        }
                    ),
                    html.Button(
                        "📈 Export Charts",
                        id="export-charts-btn",
                        style={
                            "width": "100%",
                            "padding": "10px",
                            "margin": "5px 0",
                            "backgroundColor": COLORS["accent"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        }
                    ),
                    html.Button(
                        "📄 Generate Report",
                        id="export-report-btn",
                        style={
                            "width": "100%",
                            "padding": "10px",
                            "margin": "5px 0",
                            "backgroundColor": COLORS["warning"],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        }
                    ),
                    html.P(
                        id="export-status",
                        children="Ready to export",
                        style={
                            "textAlign": "center",
                            "marginTop": "10px",
                            "fontSize": "0.8rem",
                            "color": COLORS["text_secondary"],
                        }
                    ),
                ]),
            ]
        )


# Create the component instance
def create_enhanced_stats_component():
    """Factory function to create enhanced stats component"""
    return EnhancedStatsComponent()


# Add this to your app.py layout creation:
def get_consolidated_analytics_layout():
    """Get the consolidated analytics layout for integration"""
    component = create_enhanced_stats_component()
    return component.create_enhanced_stats_container()
