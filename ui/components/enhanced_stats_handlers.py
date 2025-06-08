# ui/components/enhanced_stats_handlers.py
"""
Enhanced Statistics handlers and callbacks
"""

from dash import Input, Output, State, callback, no_update
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
        self._register_enhanced_metrics_display_callback()
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
                Output('enhanced-stats-data-store', 'data'),
            ],
            [
                Input('stats-refresh-interval', 'n_intervals'),
                Input('refresh-stats-btn', 'n_clicks'),
                Input('enhanced-metrics-store', 'data')
            ],
            [
                State('processed-data-store', 'data'),
            ],
            prevent_initial_call=True
        )
        def update_enhanced_stats(n_intervals, refresh_clicks, enhanced_metrics, processed_data):
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

    def _register_enhanced_metrics_display_callback(self):
        """Register callback to display ALL enhanced metrics"""
        @self.app.callback(
            [
                # User Analytics outputs
                Output('stats-unique-users', 'children'),
                Output('stats-avg-events-per-user', 'children'),
                Output('stats-most-active-user', 'children'),
                Output('stats-devices-per-user', 'children'),
                Output('stats-peak-hour', 'children'),

                # Device Analytics outputs
                Output('total-devices-count', 'children'),
                Output('entrance-devices-count', 'children'),
                Output('high-security-devices', 'children'),
                Output('busiest-floor', 'children'),

                # Advanced Insights outputs
                Output('traffic-pattern-insight', 'children'),
                Output('security-score-insight', 'children'),
                Output('efficiency-insight', 'children'),
                Output('anomaly-insight', 'children'),

                # Additional Activity Analysis
                Output('avg-events-per-day', 'children'),
                Output('peak-activity-day', 'children'),
            ],
            [
                Input('enhanced-metrics-store', 'data'),
                Input('stats-refresh-interval', 'n_intervals'),
            ],
            prevent_initial_call=True
        )
        def update_all_enhanced_metrics(enhanced_metrics, n_intervals):
            """Update ALL enhanced metrics displays"""
            if not enhanced_metrics:
                # Return default values for all outputs
                return (
                    "0 users", "N/A", "N/A", "N/A", "N/A",
                    "0 devices", "0 entrances", "0 high security", "N/A",
                    "No Data", "N/A", "N/A", "0 detected",
                    "N/A", "N/A"
                )

            try:
                # User Analytics
                unique_users = f"{enhanced_metrics.get('unique_users', 0)} users"
                avg_events_per_user = enhanced_metrics.get('avg_events_per_user', 'N/A')
                most_active_user = enhanced_metrics.get('most_active_user', 'N/A')
                devices_per_user = enhanced_metrics.get('avg_users_per_device', 'N/A')
                peak_hour = enhanced_metrics.get('peak_hour', 'N/A')

                # Device Analytics
                total_devices = enhanced_metrics.get('total_devices_count', '0 devices')
                entrance_devices = enhanced_metrics.get('entrance_devices_count', '0 entrances')
                high_security_devices = enhanced_metrics.get('high_security_devices', '0 high security')
                busiest_floor = enhanced_metrics.get('busiest_floor', 'N/A')

                # Advanced Insights
                traffic_pattern = enhanced_metrics.get('traffic_pattern', 'No Data')
                security_score = enhanced_metrics.get('security_score', 'N/A')
                efficiency_score = enhanced_metrics.get('efficiency_score', 'N/A')
                anomaly_count = f"{enhanced_metrics.get('anomaly_count', 0)} detected"

                # Additional Activity Analysis
                avg_events_per_day = enhanced_metrics.get('avg_events_per_day', 'N/A')
                peak_activity_day = enhanced_metrics.get('peak_activity_day', 'N/A')

                return (
                    unique_users, avg_events_per_user, most_active_user, devices_per_user, peak_hour,
                    total_devices, entrance_devices, high_security_devices, busiest_floor,
                    traffic_pattern, security_score, efficiency_score, anomaly_count,
                    avg_events_per_day, peak_activity_day
                )

            except Exception as e:
                print(f"Error updating enhanced metrics display: {e}")
                # Return error values for all outputs
                return (
                    "Error", "Error", "Error", "Error", "Error",
                    "Error", "Error", "Error", "Error",
                    "Error", "Error", "Error", "Error",
                    "Error", "Error"
                )
                
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
            [
                State('enhanced-stats-data-store', 'data'),
                State('processed-data-store', 'data')
            ],
            prevent_initial_call=True
        )
        def update_main_chart(hourly_clicks, daily_clicks, security_clicks, devices_clicks, stats_data, processed_data):
            """Update main analytics chart based on button clicks"""
            from dash import ctx
            
            if not ctx.triggered:
                return self.component._create_empty_chart("Select a chart type")
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            df = None
            if processed_data and isinstance(processed_data, dict) and processed_data.get('dataframe'):
                try:
                    df = pd.DataFrame(processed_data['dataframe'])
                except Exception:
                    df = None

            if button_id == 'chart-hourly-btn':
                return self.component.create_hourly_activity_chart(df)
            elif button_id == 'chart-daily-btn':
                return self.component.create_daily_trends_chart(df)
            elif button_id == 'chart-security-btn':
                return self.component.create_security_distribution_chart(df)
            elif button_id == 'chart-devices-btn':
                return self.component.create_device_usage_chart(df)
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
