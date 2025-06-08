# ui/components/enhanced_stats.py
"""
Enhanced Statistics component with comprehensive metrics, charts, and export features
Maintains exact same style as original stats while adding powerful new capabilities
"""

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
                    COLORS['accent_light'],
                    "#66BB6A",
                    "#FFA726",
                    "#EF5350",
                ],
            }
        }
    
    def create_enhanced_stats_container(self):
        """Creates the main enhanced statistics container"""
        return html.Div(
            [
                # Custom header (same as original)
                self.create_custom_header(),
                # Row 1: Access, User and Device analytics with sidebar
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
                            style={
                                "display": "flex",
                                "flex": "1",
                                "justifyContent": "space-around",
                            },
                            children=[
                                self.create_enhanced_access_events_panel(),
                                self.create_user_patterns_panel(),
                                self.create_enhanced_active_devices_panel(),
                            ],
                        ),
                        self.create_export_tools_section(sidebar=True),
                    ],
                ),
                # Row 2: Peak activity, security overview and visualization
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
                        self.create_peak_activity_panel(),
                        self.create_security_distribution_panel(),
                        self.create_charts_section(inline=True),
                    ],
                ),
                # Additional statistics below
                html.Div(
                    id="additional-stats-container",
                    style={"width": "90%", "margin": "0 auto 30px auto"},
                    children=[self.create_enhanced_statistics_panel()],
                ),
                # Hidden stores for data
                dcc.Store(id="enhanced-stats-data-store"),
                dcc.Store(id="chart-data-store"),
                # Auto-refresh interval
                dcc.Interval(
                    id="stats-refresh-interval",
                    interval=30 * 1000,  # 30 seconds
                    n_intervals=0,
                    disabled=True,  # Enable when real-time mode is active
                ),
            ]
        )

    def create_custom_header(self):
        """Creates the enhanced custom header with controls"""
        return html.Div(
            id="enhanced-stats-header",
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "padding": "16px 32px",
                "backgroundColor": COLORS["background"],
                "borderBottom": f'1px solid {COLORS["border"]}',
                "boxShadow": SHADOWS["sm"],
                "marginBottom": "20px",
                "backdropFilter": "blur(10px)",
            },
            children=[
                # Left: Logo and title (same as original)
                html.Div(
                    [
                        html.Img(
                            src="/assets/logo_white.png",  # Use your logo path
                            style={
                                "height": "24px",
                                "marginRight": "10px",
                                "verticalAlign": "middle",
                            },
                        ),
                        html.Span(
                            "Enhanced Analytics Dashboard",
                            style={
                                "fontSize": "18px",
                                "fontWeight": "400",
                                "color": COLORS['text_on_accent'],
                                "fontFamily": "system-ui, -apple-system, sans-serif",
                                "verticalAlign": "middle",
                            },
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
                
                # Right: Controls
                html.Div(
                    [
                        dbc.Button(
                            "📊 Export Report",
                            id="export-stats-btn",
                            color="primary",
                            size="sm",
                            className="me-2",
                        ),
                        dbc.Button(
                            "🔄 Refresh",
                            id="refresh-stats-btn",
                            color="secondary",
                            size="sm",
                            className="me-2",
                        ),
                        dbc.Switch(
                            id="real-time-toggle",
                            label="Real-time",
                            value=False,
                            style={"color": COLORS["text_secondary"]},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
            ],
        )
    
    def create_enhanced_access_events_panel(self):
        """Enhanced access events panel with trend indicators"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["accent"]}'

        return html.Div(
            [
                html.H3(
                    "Access Events",
                    style={"color": COLORS["text_primary"], "marginBottom": "10px"},
                ),
                html.H1(
                    id="enhanced-total-access-events-H1",
                    style={
                        "color": COLORS["text_primary"],
                        "marginBottom": "5px",
                        "fontSize": "2.5rem",
                    },
                ),
                html.P(
                    id="enhanced-event-date-range-P",
                    style={"color": COLORS["text_secondary"], "marginBottom": "10px"},
                ),
                # New: Trend indicator
                html.Div(
                    [
                        html.Span(
                            id="events-trend-indicator",
                            style={"fontSize": "1.2rem", "fontWeight": "bold"},
                        ),
                        html.Span(
                            " vs last period",
                            style={
                                "fontSize": "0.8rem",
                                "color": COLORS["text_tertiary"],
                            },
                        ),
                    ]
                ),
                # New: Events per day average
                html.P(
                    id="avg-events-per-day",
                    style={
                        "color": COLORS["text_secondary"],
                        "fontSize": "0.9rem",
                        "marginTop": "10px",
                    },
                ),
            ],
            style=panel_style,
        )
    
    def create_enhanced_statistics_panel(self):
        """Enhanced general statistics panel with more metrics"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["warning"]}'

        return html.Div(
            [
                html.H3(
                    "Advanced Statistics",
                    style={"color": COLORS["text_primary"], "marginBottom": "15px"},
                ),
                # Core stats (enhanced from original)
                html.Div(
                    [
                        html.P(
                            id="enhanced-stats-date-range-P",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="enhanced-stats-days-with-data-P",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="enhanced-stats-num-devices-P",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="enhanced-stats-unique-tokens-P",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                    ]
                ),
                html.Hr(style={"borderColor": COLORS["border"], "margin": "15px 0"}),
                # New advanced metrics
                html.Div(
                    [
                        html.P(
                            id="peak-hour-stat",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="busiest-day-stat",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="avg-session-length",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                        html.P(
                            id="compliance-score",
                            style={
                                "color": COLORS["text_secondary"],
                                "margin": "5px 0",
                            },
                        ),
                    ]
                ),
            ],
            style=panel_style,
        )
    
    def create_enhanced_active_devices_panel(self):
        """Enhanced active devices panel with interactive table"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["critical"]}'

        return html.Div(
            [
                html.H3(
                    "Device Analytics",
                    style={"color": COLORS["text_primary"], "marginBottom": "15px"},
                ),
                # Device summary metrics
                html.Div(
                    [
                        html.P(
                            id="total-devices-summary",
                            style={
                                "color": COLORS["text_primary"],
                                "fontSize": "1.2rem",
                                "fontWeight": "bold",
                                "marginBottom": "10px",
                            },
                        ),
                        html.P(
                            id="active-devices-today",
                            style={
                                "color": COLORS["text_secondary"],
                                "marginBottom": "15px",
                            },
                        ),
                    ]
                ),
                # Enhanced devices table with sparklines
                html.Div(
                    [
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th(
                                                "DEVICE",
                                                style={
                                                    "color": COLORS["text_primary"],
                                                    "fontSize": "0.8rem",
                                                },
                                            ),
                                            html.Th(
                                                "EVENTS",
                                                style={
                                                    "color": COLORS["text_primary"],
                                                    "fontSize": "0.8rem",
                                                },
                                            ),
                                            html.Th(
                                                "TREND",
                                                style={
                                                    "color": COLORS["text_primary"],
                                                    "fontSize": "0.8rem",
                                                },
                                            ),
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    id="enhanced-most-active-devices-table-body"
                                ),
                            ],
                            style={"width": "100%", "fontSize": "0.9rem"},
                        )
                    ]
                ),
            ],
            style=panel_style,
        )

    def create_peak_activity_panel(self):
        """New panel for peak activity analysis"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["success"]}'

        return html.Div(
            [
                html.H3(
                    "Peak Activity",
                    style={"color": COLORS["text_primary"], "marginBottom": "15px"},
                ),
                # Peak hour with visual indicator
                html.Div(
                    [
                        html.H2(
                            id="peak-hour-display",
                            style={
                                "color": COLORS["success"],
                                "fontSize": "2rem",
                                "marginBottom": "5px",
                            },
                        ),
                        html.P(
                            "Peak Hour",
                            style={
                                "color": COLORS["text_secondary"],
                                "fontSize": "0.9rem",
                            },
                        ),
                    ]
                ),
                # Peak day and metrics
                html.Div(
                    [
                        html.P(
                            id="peak-day-display",
                            style={
                                "color": COLORS["text_secondary"],
                                "marginBottom": "10px",
                            },
                        ),
                        html.P(
                            id="peak-activity-events",
                            style={
                                "color": COLORS["text_secondary"],
                                "fontSize": "0.9rem",
                            },
                        ),
                    ]
                ),
                # Activity level indicator
                html.Div(id="activity-level-indicator", style={"marginTop": "15px"}),
            ],
            style=panel_style,
        )
    
    def create_security_distribution_panel(self):
        """New panel for security level distribution"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["critical"]}'

        return html.Div(
            [
                html.H3(
                    "Security Overview",
                    style={"color": COLORS["text_primary"], "marginBottom": "15px"},
                ),
                # Security level breakdown
                html.Div(
                    id="security-level-breakdown",
                    children=[
                        html.P(
                            "Loading security data...",
                            style={"color": COLORS["text_secondary"]},
                        )
                    ],
                ),
                # Security compliance score
                html.Div(
                    [
                        html.Hr(
                            style={"borderColor": COLORS["border"], "margin": "15px 0"}
                        ),
                        html.Div(
                            [
                                html.H3(
                                    id="security-compliance-score",
                                    style={
                                        "color": COLORS["critical"],
                                        "fontSize": "1.8rem",
                                        "marginBottom": "5px",
                                    },
                                ),
                                html.P(
                                    "Compliance Score",
                                    style={
                                        "color": COLORS["text_secondary"],
                                        "fontSize": "0.9rem",
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            style=panel_style,
        )

    def create_user_patterns_panel(self):
        """New panel for user behavior patterns"""
        panel_style = self.panel_style_base.copy()
        panel_style["borderLeft"] = f'5px solid {COLORS["accent"]}'

        return html.Div(
            [
                html.H3(
                    "User Patterns",
                    style={"color": COLORS["text_primary"], "marginBottom": "15px"},
                ),
                # User activity metrics
                html.Div(
                    [
                        html.P(
                            id="most-active-user",
                            style={
                                "color": COLORS["text_secondary"],
                                "marginBottom": "8px",
                            },
                        ),
                        html.P(
                            id="avg-user-activity",
                            style={
                                "color": COLORS["text_secondary"],
                                "marginBottom": "8px",
                            },
                        ),
                        html.P(
                            id="unique-users-today",
                            style={
                                "color": COLORS["text_secondary"],
                                "marginBottom": "15px",
                            },
                        ),
                    ]
                ),
                # Behavior insights
                html.Div(
                    [
                        html.H4(
                            id="primary-access-pattern",
                            style={
                                "color": COLORS["accent"],
                                "fontSize": "1.1rem",
                                "marginBottom": "5px",
                            },
                        ),
                        html.P(
                            id="access-pattern-description",
                            style={
                                "color": COLORS["text_secondary"],
                                "fontSize": "0.85rem",
                            },
                        ),
                    ]
                ),
            ],
            style=panel_style,
        )

    def create_charts_section(self, inline: bool = False):
        """Creates the visual charts section

        Parameters
        ----------
        inline: bool, optional
            When True the section is styled to fit inside a row of panels
            (used when displayed alongside other panels).
        """
        container_style = {"width": "90%", "margin": "0 auto", "marginBottom": "30px"}
        if inline:
            # Shrink so it behaves like a panel
            container_style = {"flex": "1", "margin": "0 10px", "marginBottom": "30px"}

        return html.Div(
            [
                html.H3(
                    "Visual Analytics",
                    style={
                        "color": COLORS["text_primary"],
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "fontSize": "1.5rem",
                    },
                ),
                # Chart controls
                html.Div(
                    [
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    "Hourly Activity",
                                    id="chart-hourly-btn",
                                    color="primary",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Daily Trends",
                                    id="chart-daily-btn",
                                    color="outline-primary",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Security Levels",
                                    id="chart-security-btn",
                                    color="outline-primary",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Device Usage",
                                    id="chart-devices-btn",
                                    color="outline-primary",
                                    size="sm",
                                ),
                            ],
                            className="mb-3",
                        )
                    ],
                    style={"textAlign": "center", "marginBottom": "20px"},
                ),
                # Chart container
                html.Div(
                    [
                        # Main chart area
                        html.Div(
                            [
                                dcc.Graph(
                                    id="main-analytics-chart",
                                    style={"height": "400px"},
                                    config={
                                        "displayModeBar": True,
                                        "displaylogo": False,
                                    },
                                )
                            ],
                            style={
                                "backgroundColor": COLORS["surface"],
                                "borderRadius": "8px",
                                "border": f"1px solid {COLORS['border']}",
                                "padding": "15px",
                                "marginBottom": "20px",
                            },
                        ),
                        # Secondary charts row
                        html.Div(
                            [
                                # Security distribution pie chart
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="security-pie-chart",
                                            style={"height": "300px"},
                                            config={"displayModeBar": False},
                                        )
                                    ],
                                    style={
                                        "backgroundColor": COLORS["surface"],
                                        "borderRadius": "8px",
                                        "border": f"1px solid {COLORS['border']}",
                                        "padding": "15px",
                                        "flex": "1",
                                        "marginRight": "10px",
                                    },
                                ),
                                # Device activity heatmap
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="device-heatmap-chart",
                                            style={"height": "300px"},
                                            config={"displayModeBar": False},
                                        )
                                    ],
                                    style={
                                        "backgroundColor": COLORS["surface"],
                                        "borderRadius": "8px",
                                        "border": f"1px solid {COLORS['border']}",
                                        "padding": "15px",
                                        "flex": "1",
                                        "marginLeft": "10px",
                                    },
                                ),
                            ],
                            style={"display": "flex", "gap": "20px"},
                        ),
                    ],
                    style=container_style,
                ),
            ]
        )

    def create_export_tools_section(self, sidebar: bool = False):
        """Creates export and tools section

        Parameters
        ----------
        sidebar: bool, optional
            When True the section is styled as a narrow sidebar rather than a
            full-width row.
        """

        export_options_style = {
            "backgroundColor": COLORS["surface"],
            "borderRadius": "8px",
            "border": f"1px solid {COLORS['border']}",
            "padding": "20px",
        }
        analytics_tools_style = export_options_style.copy()

        if sidebar:
            container_style = {"marginBottom": "30px", "width": "250px"}
            inner_div_style = {
                "display": "flex",
                "flexDirection": "column",
                "gap": "20px",
                "width": "100%",
                "margin": "0",
            }
            export_options_style["marginBottom"] = "20px"
            analytics_tools_style["marginBottom"] = "0"
        else:
            container_style = {"marginBottom": "30px"}
            inner_div_style = {
                "display": "flex",
                "gap": "20px",
                "width": "60%",
                "margin": "0 auto",
            }
            export_options_style["flex"] = "1"
            export_options_style["marginRight"] = "10px"
            analytics_tools_style["flex"] = "1"
            analytics_tools_style["marginLeft"] = "10px"

        return html.Div(
            [
                html.H4(
                    "Export & Tools",
                    style={
                        "color": COLORS["text_primary"],
                        "textAlign": "center",
                        "marginBottom": "20px",
                    },
                ),
                html.Div(
                    [
                        # Export options
                        html.Div(
                            [
                                html.H5(
                                    "Export Options",
                                    style={
                                        "color": COLORS["text_primary"],
                                        "marginBottom": "15px",
                                    },
                                ),
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "📄 PDF Report",
                                            id="export-pdf-btn",
                                            color="success",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "📊 Excel Data",
                                            id="export-excel-btn",
                                            color="info",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "📈 Charts PNG",
                                            id="export-charts-btn",
                                            color="warning",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "💾 Raw JSON",
                                            id="export-json-btn",
                                            color="secondary",
                                            size="sm",
                                        ),
                                    ],
                                    vertical=True,
                                    className="w-100",
                                ),
                            ],
                            style=export_options_style,
                        ),
                        # Analytics tools
                        html.Div(
                            [
                                html.H5(
                                    "Analytics Tools",
                                    style={
                                        "color": COLORS["text_primary"],
                                        "marginBottom": "15px",
                                    },
                                ),
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "🔍 Anomaly Detection",
                                            id="anomaly-detection-btn",
                                            color="danger",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "📊 Custom Report",
                                            id="custom-report-btn",
                                            color="primary",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "⚡ Performance Metrics",
                                            id="performance-btn",
                                            color="info",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "🔔 Alert Setup",
                                            id="alert-setup-btn",
                                            color="warning",
                                            size="sm",
                                        ),
                                    ],
                                    vertical=True,
                                    className="w-100",
                                ),
                            ],
                            style=analytics_tools_style,
                        ),
                    ],
                    style=inner_div_style,
                ),
            ],
            style=container_style,
        )
    
    # Chart creation methods
    def create_hourly_activity_chart(self, df):
        """Creates hourly activity line chart"""
        if df is None or df.empty:
            return self._create_empty_chart("No data available for hourly activity")
        
        # Extract hour from timestamp
        timestamp_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        if timestamp_col not in df.columns:
            return self._create_empty_chart("Timestamp data not available")
        
        hourly_data = df.groupby(df[timestamp_col].dt.hour).size().reset_index()
        hourly_data.columns = ["Hour", "Events"]
        
        # Ensure all 24 hours are represented
        all_hours = pd.DataFrame({"Hour": range(24)})
        hourly_data = all_hours.merge(hourly_data, on="Hour", how="left").fillna(0)

        fig = go.Figure(
            data=go.Scatter(
                x=hourly_data["Hour"],
                y=hourly_data["Events"],
                mode="lines+markers",
                line=dict(color=COLORS["accent"], width=3),
                marker=dict(size=8, color=COLORS["accent"]),
                fill="tonexty",
                fillcolor=f"rgba(33, 150, 243, 0.1)",
            )
        )

        
        fig.update_layout(
            title="Access Events by Hour of Day",
            xaxis_title="Hour",
            yaxis_title="Number of Events",
             **self.chart_theme["layout"],
        )
        
        return fig
    
    def create_daily_trends_chart(self, df):
        """Creates daily trends chart"""
        if df is None or df.empty:
            return self._create_empty_chart("No data available for daily trends")
        
        timestamp_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        if timestamp_col not in df.columns:
            return self._create_empty_chart("Timestamp data not available")
        
        daily_data = df.groupby(df[timestamp_col].dt.date).size().reset_index()
        daily_data.columns = ["Date", "Events"]

        fig = go.Figure(
            data=go.Scatter(
                x=daily_data["Date"],
                y=daily_data["Events"],
                mode="lines+markers",
                line=dict(color=COLORS["success"], width=2),
                marker=dict(size=6, color=COLORS["success"]),
            )
        )
        
        # Add trend line
        if len(daily_data) > 1:
            z = np.polyfit(range(len(daily_data)), daily_data["Events"], 1)
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=daily_data["Date"],
                    y=p(range(len(daily_data))),
                    mode="lines",
                    line=dict(color=COLORS["warning"], width=2, dash="dash"),
                    name="Trend",
                )
            )

        
        fig.update_layout(
            title="Daily Access Events Trend",
            xaxis_title="Date",
            yaxis_title="Number of Events",
            **self.chart_theme['layout'],
        )
        
        return fig
    
    def create_security_distribution_chart(self, device_attrs):
        """Creates security level distribution pie chart"""
        if device_attrs is None or device_attrs.empty:
            return self._create_empty_chart("No security data available")
        
        if 'SecurityLevel' not in device_attrs.columns:
            return self._create_empty_chart("Security level data not available")
                
        sec_series = self._normalize_security_column(device_attrs["SecurityLevel"])
        security_counts = sec_series.value_counts()

        colors = {
            "green": COLORS["success"],
            "yellow": COLORS["warning"],
            "red": COLORS["critical"],
            "unclassified": COLORS["border"],
        }
        
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=security_counts.index,
                    values=security_counts.values,
                    marker_colors=[
                        colors.get(level, COLORS["border"])
                        for level in security_counts.index
                    ],
                    textinfo="label+percent",
                    textfont_size=12,
                )
            ]
        )

        
        fig.update_layout(
            title="Security Level Distribution", **self.chart_theme["layout"]
       )
        
        return fig
    
    def create_device_usage_chart(self, df):
        """Creates device usage bar chart"""
        if df is None or df.empty:
            return self._create_empty_chart("No device data available")
        
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]
        if doorid_col not in df.columns:
            return self._create_empty_chart("Device data not available")
        
        device_counts = df[doorid_col].value_counts().head(10)
        
        fig = go.Figure(
            data=[
                go.Bar(
                    x=device_counts.values,
                    y=device_counts.index,
                    orientation="h",
                    marker_color=COLORS["accent"],
                )
            ]
        )
        
        fig.update_layout(
            title="Top 10 Most Active Devices",
            xaxis_title="Number of Events",
            yaxis_title="Device ID",
            **self.chart_theme["layout"],
        )
        
        return fig
    
    def _create_empty_chart(self, message):
        """Creates an empty chart with a message"""
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
            **self.chart_theme["layout"]
        )
        return fig
    
    # Data processing methods
    def process_enhanced_stats(self, df, device_attrs=None):
        """Process data for enhanced statistics"""
        if df is None or df.empty:
            return self._get_default_enhanced_stats()
        
        stats = {}
        
        # Core metrics (enhanced from original)
        timestamp_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
        doorid_col = REQUIRED_INTERNAL_COLUMNS["DoorID"]
        userid_col = REQUIRED_INTERNAL_COLUMNS["UserID"]

        
        if timestamp_col in df.columns:
            # Basic stats
            stats["total_events"] = len(df)
            stats["date_range"] = self._get_date_range_string(df[timestamp_col])
            stats["days_with_data"] = df[timestamp_col].dt.date.nunique()
            
            # Enhanced time-based analytics
            stats["peak_hour"] = df[timestamp_col].dt.hour.mode()[0]
            stats["peak_day"] = df[timestamp_col].dt.day_name().mode()[0]
            stats["events_per_day"] = stats["total_events"] / max(
                stats["days_with_data"], 1
            )

            
            # Activity patterns
            hourly_activity = df.groupby(df[timestamp_col].dt.hour).size()
            stats["activity_variance"] = hourly_activity.var()
            stats["peak_hour_events"] = hourly_activity.max()
            
        if doorid_col in df.columns:
            stats["num_devices"] = df[doorid_col].nunique()
            stats["devices_active_today"] = self._get_devices_active_today(
                df, doorid_col, timestamp_col
            )
            
        if userid_col in df.columns:
            stats["unique_users"] = df[userid_col].nunique()
            stats["avg_events_per_user"] = stats.get("total_events", 0) / max(
                stats["unique_users"], 1
            )
            stats["most_active_user"] = (
                df[userid_col].value_counts().index[0] if not df.empty else "N/A"
            )
            
        # Security analysis
        if device_attrs is not None and not device_attrs.empty:
            stats["security_distribution"] = self._analyze_security_distribution(
                device_attrs
            )
            stats["compliance_score"] = self._calculate_compliance_score(device_attrs)
            
        return stats
    
    def _get_default_enhanced_stats(self):
        """Returns default enhanced stats structure"""
        return {
            "total_events": 0,
            "date_range": "N/A",
            "days_with_data": 0,
            "num_devices": 0,
            "unique_users": 0,
            "peak_hour": "N/A",
            "peak_day": "N/A",
            "events_per_day": 0,
            "activity_variance": 0,
            "peak_hour_events": 0,
            "devices_active_today": 0,
            "avg_events_per_user": 0,
            "most_active_user": "N/A",
            "security_distribution": {},
            "compliance_score": 0,
        }
    
    def _get_date_range_string(self, timestamp_series):
        """Gets formatted date range string"""
        min_date = timestamp_series.min()
        max_date = timestamp_series.max()
        if pd.notna(min_date) and pd.notna(max_date):
            return f"{min_date.strftime('%d.%m.%Y')} - {max_date.strftime('%d.%m.%Y')}"
        return "N/A"
    
    def _get_devices_active_today(self, df, doorid_col, timestamp_col):
        """Gets count of devices active today"""
        if timestamp_col not in df.columns:
            return 0
        today = datetime.now().date()
        today_data = df[df[timestamp_col].dt.date == today]
        return today_data[doorid_col].nunique() if not today_data.empty else 0

    def _normalize_security_column(self, series: pd.Series) -> pd.Series:
        """Translate numeric security levels to their string color values."""
        level_map = {lvl: info["value"] for lvl, info in SECURITY_LEVELS.items()}

        def convert(val):
            try:
                return level_map[int(val)]
            except (ValueError, TypeError, KeyError):
                return str(val)

        return series.map(convert)
        
    def _analyze_security_distribution(self, device_attrs):
        """Analyzes security level distribution"""
        if "SecurityLevel" not in device_attrs.columns:
            return {}

        sec_series = self._normalize_security_column(device_attrs["SecurityLevel"])
        return sec_series.value_counts().to_dict()
    
    def _calculate_compliance_score(self, device_attrs):
        """Calculates security compliance score (0-100)"""
        if device_attrs is None or device_attrs.empty:
            return 0
        
        total_devices = len(device_attrs)
        if total_devices == 0:
            return 0
        
        # Score based on security classification completeness and distribution
        classified_devices = 0
        high_security_devices = 0
        
        if "SecurityLevel" in device_attrs.columns:
            sec_series = self._normalize_security_column(device_attrs["SecurityLevel"])
            classified_devices = sec_series.notna().sum()
            high_security_devices = (sec_series == "red").sum()

        classification_score = (
            classified_devices / total_devices
        ) * 70  # 70% for classification
        security_balance_score = min(
            30, (high_security_devices / max(total_devices, 1)) * 100
        )  # 30% for security balance

        
        return round(classification_score + security_balance_score, 1)


# Factory function
def create_enhanced_stats_component():
    """Factory function to create enhanced stats component"""
    return EnhancedStatsComponent()