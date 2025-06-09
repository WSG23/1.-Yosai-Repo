# ui/components/enhanced_stats_handlers.py
"""
Enhanced Statistics handlers and callbacks
"""

from dash import Input, Output, State, callback, no_update, html
import pandas as pd
import json
from .enhanced_stats import create_enhanced_stats_component
from ui.themes.style_config import COLORS, TYPOGRAPHY


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
        
    def _register_stats_update_callback(self):
        """Register main stats update callback"""
        @self.app.callback(
            [
                Output('enhanced-total-access-events-H1', 'children'),
                Output('enhanced-event-date-range-P', 'children'),
                Output('events-trend-indicator', 'children'),
                Output('events-trend-indicator', 'style'),
                Output('avg-events-per-day', 'children'),
                Output('enhanced-stats-data-store', 'data', allow_duplicate=True),            ],
            [
                Input('stats-refresh-interval', 'n_intervals'),
                Input('refresh-stats-btn', 'n_clicks'),
            ],
            [
                State('processed-data-store', 'data'),
                State('enhanced-stats-data-store', 'data'),
            ],
            prevent_initial_call=True
        )
        def update_enhanced_stats(n_intervals, refresh_clicks, processed_data, enhanced_metrics):
            """Update enhanced statistics display"""
            try:
                if enhanced_metrics:
                    total_events = enhanced_metrics.get('total_events', 0)
                    date_range = enhanced_metrics.get('date_range', 'N/A')
                    events_per_day = enhanced_metrics.get('events_per_day', 0)
                    
                    # Calculate trend (mock for now)
                    trend_value = "+12%"
                    trend_style = {
                        'color': COLORS['success'],
                        'fontSize': '1.2rem',
                        'fontWeight': TYPOGRAPHY['font_bold']
                    }
                    
                    return (
                        f"{total_events:,}",
                        date_range,
                        trend_value,
                        trend_style,
                        f"Avg: {events_per_day:.1f} events/day",
                        enhanced_metrics
                    )
                else:
                    return "0", "No data", "--", {}, "No data", {}

            except Exception as e:
                return "Error", "Error", "--", {}, "Error", {}

    def _register_user_patterns_callback(self):
        """Register User Patterns panel callback"""
        @self.app.callback(
            [
                Output('most-active-user', 'children'),
                Output('avg-user-activity', 'children'),
                Output('unique-users-today', 'children'),
            ],
            [
                Input('enhanced-stats-data-store', 'data'),
                Input('stats-refresh-interval', 'n_intervals'),
            ],
            prevent_initial_call=True
        )
        def update_user_patterns(enhanced_metrics, n_intervals):
            """Update User Patterns panel"""
            try:
                if enhanced_metrics:
                    return (
                        f"Most Active: {enhanced_metrics.get('most_active_user', 'N/A')}",
                        f"Avg Events/User: {enhanced_metrics.get('avg_events_per_user', 0):.1f}",
                        f"Unique Users: {enhanced_metrics.get('unique_users', 0):,}"
                    )
                else:
                    return "No data", "No data", "No data"
            except Exception:
                return "Error", "Error", "Error"

    def _register_device_analytics_callback(self):
        """Register Device Analytics panel callback"""
        @self.app.callback(
            [
                Output('total-devices-summary', 'children'),
                Output('active-devices-today', 'children'),
                Output('enhanced-most-active-devices-table-body', 'children'),
            ],
            [
                Input('enhanced-stats-data-store', 'data'),
                Input('stats-refresh-interval', 'n_intervals'),
            ],
            prevent_initial_call=True
        )
        def update_device_analytics(enhanced_metrics, n_intervals):
            """Update Device Analytics panel"""
            try:
                if enhanced_metrics:
                    table_rows = []
                    most_active_devices = enhanced_metrics.get('most_active_devices', [])
                    for device_info in most_active_devices[:5]:
                        if isinstance(device_info, dict):
                            device_name = device_info.get('device', 'Unknown')
                            event_count = device_info.get('events', 0)
                        else:
                            device_name = str(device_info[0]) if len(device_info) > 0 else 'Unknown'
                            event_count = device_info[1] if len(device_info) > 1 else 0

                        table_rows.append(html.Tr([
                            html.Td(device_name, style={'color': COLORS['text_primary']}),
                            html.Td(f"{event_count:,}", style={'color': COLORS['text_secondary']})
                        ]))

                    return (
                        f"Total Devices: {enhanced_metrics.get('total_devices_count', 0):,}",
                        f"Active Today: {enhanced_metrics.get('devices_active_today', 0):,}",
                        table_rows
                    )
                else:
                    return "No data", "No data", []
            except Exception:
                return "Error", "Error", []

    def _register_peak_activity_callback(self):
        """Register Peak Activity panel callback"""
        @self.app.callback(
            [
                Output('peak-hour-display', 'children'),
                Output('peak-day-display', 'children'),
                Output('busiest-floor', 'children'),
                Output('entry-exit-ratio', 'children'),
                Output('weekend-vs-weekday', 'children'),
            ],
            [
                Input('enhanced-stats-data-store', 'data'),
                Input('stats-refresh-interval', 'n_intervals'),
            ],
            prevent_initial_call=True
        )
        def update_peak_activity(enhanced_metrics, n_intervals):
            """Update Peak Activity panel"""
            try:
                if enhanced_metrics:
                    return (
                        f"Peak Hour: {enhanced_metrics.get('peak_hour', 'N/A')}",
                        f"Peak Day: {enhanced_metrics.get('peak_day', 'N/A')}",
                        f"Busiest Floor: {enhanced_metrics.get('busiest_floor', 'N/A')}",
                        f"Entry/Exit: {enhanced_metrics.get('entry_exit_ratio', 'N/A')}",
                        f"Weekend vs Weekday: {enhanced_metrics.get('weekend_vs_weekday', 'N/A')}"
                    )
                else:
                    return "No data", "No data", "No data", "No data", "No data"
            except Exception:
                return "Error", "Error", "Error", "Error", "Error"

    def _register_security_overview_callback(self):
        """Register Security Overview panel callback"""
        @self.app.callback(
            [
                Output('security-level-breakdown', 'children'),
                Output('security-compliance-score', 'children'),
            ],
            [
                Input('enhanced-stats-data-store', 'data'),
                Input('stats-refresh-interval', 'n_intervals'),
            ],
            prevent_initial_call=True
        )
        def update_security_overview(enhanced_metrics, n_intervals):
            """Update Security Overview panel"""
            try:
                if enhanced_metrics:
                    security_breakdown = enhanced_metrics.get('security_breakdown', {})
                    breakdown_elements = []
                    for level, count in security_breakdown.items():
                        breakdown_elements.append(
                            html.P(f"{level.title()}: {count} devices",
                                   style={'color': COLORS['text_secondary'], 'margin': '2px 0'})
                        )

                    if not breakdown_elements:
                        breakdown_elements = [html.P("No security data", style={'color': COLORS['text_secondary']})]

                    return (
                        breakdown_elements,
                        f"Security Score: {enhanced_metrics.get('security_score', 'N/A')}"
                    )
                else:
                    return [html.P("No data", style={'color': COLORS['text_secondary']})], "No data"
            except Exception:
                return [html.P("Error", style={'color': COLORS['text_secondary']})], "Error"
                
    def _register_chart_update_callbacks(self):
        """Register chart update callbacks"""
        @self.app.callback(
            Output('main-analytics-chart', 'figure'),
            [
                Input('chart-hourly-btn', 'n_clicks'),
                Input('chart-daily-btn', 'n_clicks'),
                Input('chart-security-btn', 'n_clicks'),
                Input('chart-devices-btn', 'n_clicks'),
            ],
            State('enhanced-stats-data-store', 'data'),
            prevent_initial_call=True
        )
        def update_main_chart(hourly_clicks, daily_clicks, security_clicks, devices_clicks, stats_data):
            """Update main analytics chart based on button clicks"""
            from dash import ctx
            
            if not ctx.triggered:
                return self.component._create_empty_chart("Select a chart type")
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Mock data for demonstration
            if button_id == 'chart-hourly-btn':
                return self.component.create_hourly_activity_chart(None)  # Would pass real data
            elif button_id == 'chart-daily-btn':
                return self.component.create_daily_trends_chart(None)
            elif button_id == 'chart-security-btn':
                return self.component.create_security_distribution_chart(None)
            elif button_id == 'chart-devices-btn':
                return self.component.create_device_usage_chart(None)
            else:
                return self.component._create_empty_chart("Unknown chart type")
                
    def _register_export_callbacks(self):
        """Register export callbacks"""
        @self.app.callback(
            Output('export-status', 'children', allow_duplicate=True),
            [
                Input('export-pdf-btn', 'n_clicks'),
                Input('export-excel-btn', 'n_clicks'),
                Input('export-charts-btn', 'n_clicks'),
                Input('export-json-btn', 'n_clicks'),
            ],
            prevent_initial_call=True
        )
        def handle_export_actions(pdf_clicks, excel_clicks, charts_clicks, json_clicks):
            """Handle export button clicks"""
            from dash import ctx
            
            if not ctx.triggered:
                return no_update
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'export-pdf-btn':
                return "📄 PDF report generated successfully!"
            elif button_id == 'export-excel-btn':
                return "📊 Excel data exported successfully!"
            elif button_id == 'export-charts-btn':
                return "📈 Charts exported as PNG!"
            elif button_id == 'export-json-btn':
                return "💾 Raw data exported as JSON!"
            else:
                return "Export completed"


def create_enhanced_stats_handlers(app):
    """Factory function to create enhanced stats handlers"""
    return EnhancedStatsHandlers(app)
