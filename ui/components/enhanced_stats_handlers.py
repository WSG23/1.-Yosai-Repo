# ui/components/enhanced_stats_handlers.py
"""
Enhanced Statistics handlers and callbacks
"""

from dash import Input, Output, State, callback, no_update, html
import pandas as pd
import json
from .enhanced_stats import create_enhanced_stats_component
from ui.themes.style_config import COLORS, TYPOGRAPHY
from config.settings import REQUIRED_INTERNAL_COLUMNS


def safe_callback(callback_func):
    """PERMANENT FIX: Wrapper to make callbacks safe"""
    def wrapper(*args, **kwargs):
        try:
            return callback_func(*args, **kwargs)
        except Exception as e:
            print(f"Callback error in {callback_func.__name__}: {e}")
            return None
    return wrapper

class EnhancedStatsHandlers:
    """Handles enhanced statistics callbacks"""

    def __init__(self, app):
        self.app = app
        self.component = create_enhanced_stats_component()

    def register_callbacks(self):
        """Register all enhanced stats callbacks"""
        self._register_stats_update_callback()
        self._register_user_patterns_callback()
        self._register_device_analytics_callback()
        self._register_peak_activity_callback()
        self._register_security_overview_callback()
        self._register_chart_update_callbacks()
        self._register_export_callbacks()
        self._register_basic_stats_callback()
        self._register_additional_metrics_callback()

    def _register_stats_update_callback(self):
        """Register main stats update callback"""

        @self.app.callback(
            [
                Output("enhanced-total-access-events-H1", "children"),
                Output("enhanced-event-date-range-P", "children"),
                Output("events-trend-indicator", "children"),
                Output("events-trend-indicator", "style"),
                Output("avg-events-per-day", "children"),
                Output("enhanced-stats-data-store", "data", allow_duplicate=True),
            ],
            [
                Input("enhanced-metrics-store", "data"),
                Input("stats-refresh-interval", "n_intervals"),
                Input("refresh-stats-btn", "n_clicks"),
            ],
            prevent_initial_call=True,
        )
        def update_enhanced_stats(enhanced_metrics, n_intervals, refresh_clicks):
            """Update enhanced statistics display"""
            try:
                if enhanced_metrics:
                    total_events = enhanced_metrics.get("total_events", 0)
                    date_range = enhanced_metrics.get("date_range", "N/A")
                    events_per_day = enhanced_metrics.get("events_per_day", 0)

                    # Calculate trend (mock for now)
                    trend_value = "+12%"
                    trend_style = {
                        "color": COLORS["success"],
                        "fontSize": "1.2rem",
                        "fontWeight": "bold",
                    }

                    return (
                        f"{total_events:,}",
                        date_range,
                        trend_value,
                        trend_style,
                        f"Avg: {events_per_day:.1f} events/day",
                        enhanced_metrics,
                    )
                else:
                    return "0", "No data", "--", {}, "No data", {}

            except Exception as e:
                return "Error", "Error", "--", {}, "Error", {}

    def _register_user_patterns_callback(self):
        """Register User Patterns panel callback"""

        @self.app.callback(
            [
                Output("most-active-user", "children"),
                Output("avg-user-activity", "children"),
                Output("unique-users-today", "children"),
            ],
            [
                Input("enhanced-stats-data-store", "data"),
                Input("stats-refresh-interval", "n_intervals"),
            ],
            prevent_initial_call=True,
        )
        def update_user_patterns(enhanced_metrics, n_intervals):
            """Update User Patterns panel"""
            try:
                if enhanced_metrics:
                    return (
                        f"Most Active: {enhanced_metrics.get('most_active_user', 'N/A')}",
                        f"Avg Events/User: {enhanced_metrics.get('avg_events_per_user', 0):.1f}",
                        f"Unique Users: {enhanced_metrics.get('unique_users', 0):,}",
                    )
                else:
                    return "No data", "No data", "No data"
            except Exception:
                return "Error", "Error", "Error"

    def _register_device_analytics_callback(self):
        """Register Device Analytics panel callback"""

        @self.app.callback(
            [
                Output("total-devices-summary", "children"),
                Output("active-devices-today", "children"),
                Output("enhanced-most-active-devices-table-body", "children"),
            ],
            [
                Input("enhanced-stats-data-store", "data"),
                Input("stats-refresh-interval", "n_intervals"),
            ],
            prevent_initial_call=True,
        )
        def update_device_analytics(enhanced_metrics, n_intervals):
            """Update Device Analytics panel"""
            try:
                if enhanced_metrics:
                    table_rows = []
                    most_active_devices = enhanced_metrics.get(
                        "most_active_devices", []
                    )
                    for device_info in most_active_devices[:5]:
                        if isinstance(device_info, dict):
                            device_name = device_info.get("device", "Unknown")
                            event_count = device_info.get("events", 0)
                        else:
                            device_name = (
                                str(device_info[0])
                                if len(device_info) > 0
                                else "Unknown"
                            )
                            event_count = device_info[1] if len(device_info) > 1 else 0

                        table_rows.append(
                            html.Tr(
                                [
                                    html.Td(
                                        device_name,
                                        style={"color": COLORS["text_primary"]},
                                    ),
                                    html.Td(
                                        f"{event_count:,}",
                                        style={"color": COLORS["text_secondary"]},
                                    ),
                                ]
                            )
                        )

                    return (
                        f"Total Devices: {enhanced_metrics.get('total_devices_count', 0):,}",
                        f"Active Today: {enhanced_metrics.get('devices_active_today', 0):,}",
                        table_rows,
                    )
                else:
                    return "No data", "No data", []
            except Exception:
                return "Error", "Error", []

    def _register_peak_activity_callback(self):
        """Register Peak Activity panel callback - PERMANENT FIX VERSION"""

        @self.app.callback(
            [
                Output("peak-hour-display", "children", allow_duplicate=True),
                Output("peak-day-display", "children", allow_duplicate=True),
                Output("peak-activity-events", "children", allow_duplicate=True),
                Output("busiest-floor", "children", allow_duplicate=True),
                Output("entry-exit-ratio", "children", allow_duplicate=True),
                Output("weekend-vs-weekday", "children", allow_duplicate=True),
            ],
            [
                Input("enhanced-stats-data-store", "data"),
                Input("stats-refresh-interval", "n_intervals"),
            ],
            prevent_initial_call=True,
        )
        @safe_callback
        def update_peak_activity(enhanced_metrics, n_intervals):
            """Update Peak Activity panel - PERMANENT FIX"""
            try:
                if enhanced_metrics and isinstance(enhanced_metrics, dict):
                    peak_hour = enhanced_metrics.get('peak_hour', 'N/A')
                    peak_day = enhanced_metrics.get('peak_day', 'N/A')
                    busiest_floor = enhanced_metrics.get('busiest_floor', 'N/A')
                    entry_exit_ratio = enhanced_metrics.get('entry_exit_ratio', 'N/A')
                    weekend_vs_weekday = enhanced_metrics.get('weekend_vs_weekday', 'N/A')

                    peak_activity_count = enhanced_metrics.get('peak_activity_count', 0)
                    peak_activity = f"Peak Activity: {peak_activity_count} events"

                    return (
                        f"Peak Hour: {peak_hour}",
                        f"Peak Day: {peak_day}",
                        peak_activity,
                        f"Busiest Floor: {busiest_floor}",
                        f"Entry/Exit Ratio: {entry_exit_ratio}",
                        f"Weekend vs Weekday: {weekend_vs_weekday}"
                    )
                else:
                    return (
                        "Peak Hour: N/A",
                        "Peak Day: N/A",
                        "Peak Activity: N/A",
                        "Busiest Floor: N/A",
                        "Entry/Exit Ratio: N/A",
                        "Weekend vs Weekday: N/A",
                    )
            except Exception as e:
                print(f"Error in update_peak_activity: {e}")
                return (
                    "Peak Hour: Error",
                    "Peak Day: Error",
                    "Peak Activity: Error",
                    "Busiest Floor: Error",
                    "Entry/Exit Ratio: Error",
                    "Weekend vs Weekday: Error",
                )

    def _register_security_overview_callback(self):
        """Register Security Overview panel callback"""

        @self.app.callback(
            [
                Output("security-level-breakdown", "children"),
                Output("security-compliance-score", "children"),
            ],
            [
                Input("enhanced-stats-data-store", "data"),
                Input("stats-refresh-interval", "n_intervals"),
            ],
            prevent_initial_call=True,
        )
        def update_security_overview(enhanced_metrics, n_intervals):
            """Update Security Overview panel"""
            try:
                if enhanced_metrics:
                    security_breakdown = enhanced_metrics.get("security_breakdown", {})
                    breakdown_elements = []
                    for level, count in security_breakdown.items():
                        breakdown_elements.append(
                            html.P(
                                f"{level.title()}: {count} devices",
                                style={
                                    "color": COLORS["text_secondary"],
                                    "margin": "2px 0",
                                },
                            )
                        )

                    if not breakdown_elements:
                        breakdown_elements = [
                            html.P(
                                "No security data",
                                style={"color": COLORS["text_secondary"]},
                            )
                        ]

                    return (
                        breakdown_elements,
                        f"Security Score: {enhanced_metrics.get('security_score', 'N/A')}",
                    )
                else:
                    return [
                        html.P("No data", style={"color": COLORS["text_secondary"]})
                    ], "No data"
            except Exception:
                return [
                    html.P("Error", style={"color": COLORS["text_secondary"]})
                ], "Error"

    def _register_chart_update_callbacks(self):
        """Register chart update callbacks"""

        @self.app.callback(
            Output("main-analytics-chart", "figure"),
            [
                Input("chart-hourly-btn", "n_clicks"),
                Input("chart-daily-btn", "n_clicks"),
                Input("chart-security-btn", "n_clicks"),
                Input("chart-devices-btn", "n_clicks"),
            ],
            [
                State("enhanced-stats-data-store", "data"),
                State("processed-data-store", "data"),
                State("device-attrs-store", "data"),
            ],
            prevent_initial_call=True,
        )
        def update_main_chart(
            hourly_clicks,
            daily_clicks,
            security_clicks,
            devices_clicks,
            stats_data,
            processed_data,
            device_attrs,
        ):
            """Update main analytics chart based on button clicks"""
            from dash import ctx
            import pandas as pd

            if not ctx.triggered:
                return self.component._create_empty_chart("Select a chart type")

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            df = pd.DataFrame()
            if (
                processed_data
                and isinstance(processed_data, dict)
                and "dataframe" in processed_data
            ):
                df = pd.DataFrame(processed_data["dataframe"])
                ts_col = REQUIRED_INTERNAL_COLUMNS["Timestamp"]
                if ts_col in df.columns:
                    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

            device_df = pd.DataFrame()
            if device_attrs and isinstance(device_attrs, dict):
                try:
                    device_df = pd.DataFrame.from_dict(device_attrs, orient="index")
                    device_df.reset_index(inplace=True)
                    device_df.rename(columns={"index": "Door Number"}, inplace=True)
                except Exception:
                    device_df = pd.DataFrame()

            if button_id == "chart-hourly-btn":
                return self.component.create_hourly_activity_chart(df)
            elif button_id == "chart-daily-btn":
                return self.component.create_daily_trends_chart(df)
            elif button_id == "chart-security-btn":
                return self.component.create_security_distribution_chart(device_df)
            elif button_id == "chart-devices-btn":
                return self.component.create_device_usage_chart(df)
            else:
                return self.component._create_empty_chart("Unknown chart type")

    def _register_export_callbacks(self):
        """Register export callbacks"""

        @self.app.callback(
            [
                Output("download-pdf", "data"),
                Output("download-excel", "data"),
                Output("download-charts-png", "data"),
                Output("download-json", "data"),
                Output("export-status", "children", allow_duplicate=True),
            ],
            [
                Input("export-pdf-btn", "n_clicks"),
                Input("export-excel-btn", "n_clicks"),
                Input("export-charts-btn", "n_clicks"),
                Input("export-json-btn", "n_clicks"),
            ],
            State("enhanced-stats-data-store", "data"),
            State("main-analytics-chart", "figure"),
            prevent_initial_call=True,
        )
        def handle_export_actions(pdf_clicks, excel_clicks, charts_clicks, json_clicks, stats_data, chart_fig):
            """Handle export button clicks and provide downloadable files"""
            from dash import ctx
            from utils.enhanced_analytics import create_enhanced_export_manager
            import plotly.io as pio
            import base64

            if not ctx.triggered:
                return [no_update] * 5

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            manager = create_enhanced_export_manager()

            if button_id == "export-pdf-btn":
                report = manager.export_comprehensive_report(stats_data or {}, format="PDF")
                if report.get("download_ready"):
                    data = dict(content=report["content"], filename=report["filename"])
                    return data, no_update, no_update, no_update, "📄 PDF report generated successfully!"
            elif button_id == "export-excel-btn":
                report = manager.export_comprehensive_report(stats_data or {}, format="Excel")
                if report.get("download_ready"):
                    content = base64.b64decode(report["content"])
                    return no_update, dict(content=content, filename=report["filename"]), no_update, no_update, "📊 Excel data exported successfully!"
            elif button_id == "export-charts-btn":
                if chart_fig:
                    try:
                        img_bytes = pio.to_image(chart_fig, format="png")
                        return no_update, no_update, dict(content=img_bytes, filename="chart.png"), no_update, "📈 Charts exported as PNG!"
                    except Exception:
                        pass
            elif button_id == "export-json-btn":
                report = manager.export_comprehensive_report(stats_data or {}, format="JSON")
                if report.get("download_ready"):
                    content = base64.b64decode(report["content"])
                    return no_update, no_update, no_update, dict(content=content, filename=report["filename"]), "💾 Raw data exported as JSON!"

            return [no_update, no_update, no_update, no_update, "Export completed"]

    def _register_basic_stats_callback(self):
        """Update legacy stats elements"""
        @self.app.callback(
            [
                Output("total-access-events-H1", "children", allow_duplicate=True),
                Output("event-date-range-P", "children", allow_duplicate=True),
                Output("stats-unique-users", "children", allow_duplicate=True),
                Output("stats-avg-events-per-user", "children", allow_duplicate=True),
                Output("stats-most-active-user", "children", allow_duplicate=True),
                Output("total-devices-count", "children", allow_duplicate=True),
                Output("peak-hour-display", "children", allow_duplicate=True),
                Output("busiest-floor", "children", allow_duplicate=True),
                Output("traffic-pattern-insight", "children", allow_duplicate=True),
                Output("security-score-insight", "children", allow_duplicate=True),
                Output("anomaly-insight", "children", allow_duplicate=True),
            ],
            Input("enhanced-stats-data-store", "data"),
            prevent_initial_call=True,
        )
        def _update_basic(enhanced_metrics):
            metrics = enhanced_metrics or {}

            total_events = str(metrics.get("total_events", "0"))
            date_range = metrics.get('date_range', 'N/A')
            unique_users = f"{metrics.get('unique_users', 0)} users"
            avg_events = f"Avg: {metrics.get('avg_events_per_user', 0)} events/user"

            most_active = f"Most Active: {metrics.get('most_active_user', 'N/A')}"
            total_devices = f"{metrics.get('total_devices_count', 0)} devices"
            peak_hour = f"Peak: {metrics.get('peak_hour', 'N/A')}:00"
            busiest_floor = f"Busiest Day: {metrics.get('peak_day', 'N/A')}"
            activity_intensity = metrics.get('activity_intensity', 'N/A')
            traffic_pattern = f"Activity: {activity_intensity}"
            sec = metrics.get('security_score')
            security_score = f"Score: {sec}" if sec is not None else "Score: N/A"
            anomaly_insight = f"Sessions: {metrics.get('total_events', '0')}"

            return (
                total_events,
                date_range,
                unique_users,
                avg_events,
                most_active,
                total_devices,
                peak_hour,
                busiest_floor,
                traffic_pattern,
                security_score,
                anomaly_insight,
            )

    def _register_additional_metrics_callback(self):
        """Update extended metric elements"""

        @self.app.callback(
            [
                Output("stats-devices-per-user", "children"),
                Output("entrance-devices-count", "children"),
                Output("high-security-devices", "children"),
                Output("efficiency-insight", "children"),
            ],
            Input("enhanced-stats-data-store", "data"),
            prevent_initial_call=True,
        )
        def _update_additional(metrics):
            metrics = metrics or {}

            devices_per_user = metrics.get("avg_users_per_device", "N/A")
            entrance_count = metrics.get("entrance_devices_count", "N/A")
            high_sec = metrics.get("high_security_devices", "N/A")
            efficiency = metrics.get("efficiency_score", "N/A")
            return (
                devices_per_user,
                entrance_count,
                high_sec,
                efficiency,
            )


def create_enhanced_stats_handlers(app):
    """Factory function to create enhanced stats handlers"""
    return EnhancedStatsHandlers(app)
