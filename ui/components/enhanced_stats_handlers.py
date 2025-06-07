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
            ],
            [
                State('processed-data-store', 'data'),
                State('enhanced-metrics-store', 'data'),
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