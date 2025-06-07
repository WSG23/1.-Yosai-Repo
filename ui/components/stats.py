# ui/components/stats.py - ENHANCED VERSION (FIXED)
"""
Enhanced statistics component with advanced metrics, charts, and export features
"""

from dash import html, dcc
from ui.components.graph import create_graph_container ###
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs import Figure  # For proper type hints
import pandas as pd
import base64
import io
from datetime import datetime
from typing import Optional
from ui.themes.style_config import COLORS, UI_VISIBILITY, SPACING, BORDER_RADIUS, SHADOWS
from config.settings import SECURITY_LEVELS

class EnhancedStatsComponent:
    """Enhanced statistics component with advanced analytics and visualizations"""
    
    def __init__(self):
        self.panel_style_base = {
            'flex': '1',
            'padding': '20px',
            'margin': '0 10px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'textAlign': 'center',
            'boxShadow': '2px 2px 5px rgba(0,0,0,0.2)'
        }
        
        # Chart color palette matching theme
        self.chart_colors = [
            COLORS['accent'], COLORS['success'], COLORS['warning'],
            COLORS['critical'], COLORS['accent_light'], '#66BB6A', '#FFA726', '#EF5350'
        ]
    
    def create_enhanced_stats_container(self):
        """Creates the complete enhanced statistics container with organized rows"""
        return html.Div([
        html.Div(
                id='stats-row-1',
                style=UI_VISIBILITY['show_flex_stats'],
                children=[
                    self.create_enhanced_access_events_panel(),
                    self.create_enhanced_statistics_panel(),
                    self.create_enhanced_active_devices_panel(),
                ]
            ),

            html.Div(
                id='stats-row-2',
                style=UI_VISIBILITY['show_flex_stats'],
                children=[
                    self.create_peak_activity_panel(),
                    self.create_security_overview_panel(),
                    self.create_analytics_section(),
                ]
            ),

            html.Div(
                id='stats-row-3',
                children=[
                    self.create_charts_section(),
                ]
            ),

            self.create_export_section()
        ], id='stats-panels-container', style=UI_VISIBILITY['show_flex_stats'])
    
    def create_enhanced_stats_panels(self):
        """Enhanced version of original stats panels with additional metrics"""
        return html.Div(
            id='stats-panels-container',
            style=UI_VISIBILITY['show_flex_stats'],
            children=[
                self.create_enhanced_access_events_panel(),
                self.create_enhanced_statistics_panel(),
                self.create_enhanced_active_devices_panel(),
                self.create_peak_activity_panel(),  # NEW
                self.create_security_overview_panel()  # NEW
            ]
        )
    
    def create_enhanced_access_events_panel(self):
        """Enhanced access events panel with additional metrics"""
        panel_style = self.panel_style_base.copy()
        panel_style['borderLeft'] = f'5px solid {COLORS["accent"]}'
        
        return html.Div([
            html.H3("Access Events", style={'color': COLORS['text_primary']}),
            html.H1(id="total-access-events-H1", style={'color': COLORS['text_primary']}),
            html.P(id="event-date-range-P", style={'color': COLORS['text_secondary']}),
            # NEW: Additional metrics
            html.P(id="avg-events-per-day", style={'color': COLORS['text_secondary'], 'fontSize': '0.9rem'}),
            html.P(id="peak-activity-day", style={'color': COLORS['text_secondary'], 'fontSize': '0.9rem'})
        ], style=panel_style)
    
    def create_enhanced_statistics_panel(self):
        """Enhanced statistics panel with user analytics"""
        panel_style = self.panel_style_base.copy()
        panel_style['borderLeft'] = f'5px solid {COLORS["warning"]}'
        
        return html.Div([
            html.H3("User Analytics", style={'color': COLORS['text_primary']}),
            html.P(id="stats-unique-users", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-avg-events-per-user", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-most-active-user", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-devices-per-user", style={'color': COLORS['text_secondary']}),
            html.P(id="stats-peak-hour", style={'color': COLORS['text_secondary']})
        ], style=panel_style)
    
    def create_enhanced_active_devices_panel(self):
        """Enhanced active devices panel with floor breakdown"""
        panel_style = self.panel_style_base.copy()
        panel_style['borderLeft'] = f'5px solid {COLORS["critical"]}'
        
        return html.Div([
            html.H3("Device Analytics", style={'color': COLORS['text_primary']}),
            html.P(id="total-devices-count", style={'color': COLORS['text_secondary']}),
            html.P(id="entrance-devices-count", style={'color': COLORS['text_secondary']}),
            html.P(id="high-security-devices", style={'color': COLORS['text_secondary']}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("DEVICE", style={'color': COLORS['text_primary'], 'fontSize': '0.8rem'}),
                    html.Th("EVENTS", style={'color': COLORS['text_primary'], 'fontSize': '0.8rem'})
                ])),
                html.Tbody(id='most-active-devices-table-body')
            ], style={'fontSize': '0.85rem'})
        ], style=panel_style)
    
    def create_peak_activity_panel(self):
        """NEW: Peak activity analysis panel"""
        panel_style = self.panel_style_base.copy()
        panel_style['borderLeft'] = f'5px solid {COLORS["success"]}'
        
        return html.Div([
            html.H3("Peak Activity", style={'color': COLORS['text_primary']}),
            html.P(id="peak-hour-display", style={'color': COLORS['text_secondary']}),
            html.P(id="peak-day-display", style={'color': COLORS['text_secondary']}),
            html.P(id="busiest-floor", style={'color': COLORS['text_secondary']}),
            html.P(id="entry-exit-ratio", style={'color': COLORS['text_secondary']}),
            html.P(id="weekend-vs-weekday", style={'color': COLORS['text_secondary']})
        ], style=panel_style)
    
    def create_security_overview_panel(self):
        """NEW: Security metrics panel"""
        panel_style = self.panel_style_base.copy()
        panel_style['borderLeft'] = f'5px solid {COLORS["info"]}'
        
        return html.Div([
            html.H3("Security Overview", style={'color': COLORS['text_primary']}),
            html.Div(id="security-level-breakdown", children=[
                html.P("Security analysis loading...", style={'color': COLORS['text_secondary']})
            ]),
            html.P(id="compliance-score", style={'color': COLORS['text_secondary']}),
            html.P(id="anomaly-alerts", style={'color': COLORS['text_secondary']})
        ], style=panel_style)
    
    def create_analytics_section(self):
        """NEW: Advanced analytics section with key insights"""
        return html.Div([
            html.H4("Advanced Analytics",
                   style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '20px'}),
            
            html.Div([
                # Insights cards
                self.create_insight_card("Traffic Pattern", "traffic-pattern-insight", COLORS['accent']),
                self.create_insight_card("Security Score", "security-score-insight", COLORS['success']),
                self.create_insight_card("Usage Efficiency", "efficiency-insight", COLORS['warning']),
                self.create_insight_card("Anomaly Detection", "anomaly-insight", COLORS['critical'])
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'marginBottom': '20px',
                'flexWrap': 'wrap'
            }),
            
            # Detailed breakdown
            html.Div(id="analytics-detailed-breakdown")
            
        ], id='analytics-section', style={            
            'padding': '20px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'margin': '20px 0',
            'border': f'1px solid {COLORS["border"]}'
        })
    
    def create_charts_section(self):
        """NEW: Interactive charts section"""
        return html.Div(
            id='charts-section',
            className='charts-section',
            children=[
                html.H4("Data Visualization",
                       style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '20px'}),
            
            # Chart controls
            html.Div([
                html.Label("Chart Type:", style={'color': COLORS['text_primary'], 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='chart-type-selector',
                    options=[
                        {'label': 'Hourly Activity', 'value': 'hourly'},
                        {'label': 'Daily Trends', 'value': 'daily'},
                        {'label': 'Security Distribution', 'value': 'security'},
                        {'label': 'Floor Activity', 'value': 'floor'},
                        {'label': 'User Patterns', 'value': 'users'},
                        {'label': 'Device Usage', 'value': 'devices'}
                    ],
                    value='hourly',
                    style={'width': '200px', 'color': COLORS['text_primary']}
                )
            ], style={'marginBottom': '20px', 'textAlign': 'center'}),
            
            # Chart container
            html.Div([
                dcc.Graph(
                    id='main-analytics-chart',
                    config={'displayModeBar': True, 'toImageButtonOptions': {'format': 'png'}},
                    style={'height': '400px'}
                )
            ], style={'backgroundColor': COLORS['background'], 'borderRadius': '8px', 'padding': '10px'}),
            
            # Secondary charts row
            html.Div([
                html.Div([
                    dcc.Graph(id='security-pie-chart', style={'height': '300px'})
                ], style={'flex': '1', 'margin': '0 10px'}),
                html.Div([
                    create_graph_container()], style={'flex': '1', 'margin': '0 10px'}),
                html.Div([
                    dcc.Graph(id='heatmap-chart', style={'height': '300px'})
                ], style={'flex': '1', 'margin': '0 10px'})
            ], style={'display': 'flex', 'marginTop': '20px'})
            
        ], style={
            'padding': '20px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'margin': '20px 0',
            'border': f'1px solid {COLORS["border"]}'
        })
    
    def create_export_section(self):
        """NEW: Export and download section"""
        return html.Div(
            id='export-section',
            children=[
            html.H4("Export & Reports",
                   style={'color': COLORS['text_primary'], 'textAlign': 'center', 'marginBottom': '20px'}),
            
            html.Div([
                html.Button(
                    "📊 Export Stats CSV",
                    id='export-stats-csv',
                    className='btn-secondary',
                    style=self.get_export_button_style()
                ),
                html.Button(
                    "📈 Download Charts",
                    id='export-charts-png',
                    className='btn-secondary',
                    style=self.get_export_button_style()
                ),
                html.Button(
                    "📄 Generate Report",
                    id='generate-pdf-report',
                    className='btn-primary',
                    style=self.get_export_button_style()
                ),
                html.Button(
                    "🔄 Refresh Data",
                    id='refresh-analytics',
                    className='btn-secondary',
                    style=self.get_export_button_style()
                )
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'gap': '15px',
                'flexWrap': 'wrap'
            }),
            
            # Download components (hidden)
            dcc.Download(id="download-stats-csv"),
            dcc.Download(id="download-charts"),
            dcc.Download(id="download-report"),
            
            # Export status
            html.Div(id="export-status", style={'textAlign': 'center', 'marginTop': '10px'})
            
        ], style={
            'padding': '20px',
            'backgroundColor': COLORS['surface'],
            'borderRadius': '8px',
            'margin': '20px 0',
            'border': f'1px solid {COLORS["border"]}'
        })
    
    def create_insight_card(self, title, content_id, color):
        """Create a small insight card"""
        return html.Div([
            html.H6(title, style={'color': COLORS['text_primary'], 'margin': '0', 'fontSize': '0.9rem'}),
            html.H4(id=content_id, style={'color': color, 'margin': '5px 0', 'fontSize': '1.2rem'})
        ], style={
            'padding': '15px',
            'backgroundColor': COLORS['background'],
            'borderRadius': '6px',
            'border': f'1px solid {color}',
            'textAlign': 'center',
            'flex': '1',
            'margin': '0 5px',
            'minWidth': '120px'
        })
    
    def get_export_button_style(self):
        """Standard export button styling"""
        return {
            'padding': '8px 16px',
            'border': 'none',
            'borderRadius': '5px',
            'fontSize': '0.9rem',
            'fontWeight': '500',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease'
        }
    
    def create_custom_header(self, main_logo_path):
        """Enhanced custom header with analytics toggle"""
        return html.Div(
            id='yosai-custom-header',
            style=UI_VISIBILITY['show_header'],
            children=[
                html.Div([
                    html.Img(
                        src=main_logo_path, 
                        style={
                            'height': '24px',
                            'marginRight': '10px',
                            'verticalAlign': 'middle'
                        }
                    ),
                    html.Span(
                        "Enhanced Analytics Dashboard",  # Updated title
                        style={
                            'fontSize': '18px',
                            'fontWeight': '400',
                            'color': COLORS['text_on_accent'],
                            'fontFamily': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                            'verticalAlign': 'middle'
                        }
                    ),
                    # NEW: Analytics toggle
                    html.Div([
                        html.Button(
                            "📊 Advanced View",
                            id='toggle-advanced-analytics',
                            style={
                                'marginLeft': '20px',
                                'padding': '5px 10px',
                                'backgroundColor': COLORS['accent'],
                                'color': COLORS['text_on_accent'],
                                'border': 'none',
                                'borderRadius': '4px',
                                'fontSize': '0.8rem',
                                'cursor': 'pointer'
                            }
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'padding': '16px 0',
                    'margin': '0'
                })
            ]
        )
    
    def _create_empty_figure(self, message: str = "No data available") -> Figure:
        """Create an empty figure with a message"""
        # Use plotly express to create a simple figure, then clear it
        fig = px.scatter(x=[0], y=[0])
        fig.data = []  # Remove the scatter trace
        
        # Add annotation using the layout
        fig.update_layout(
            annotations=[
                dict(
                    text=message,
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    font=dict(size=16, color=COLORS['text_secondary'])
                )
            ],
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['surface'],
            font_color=COLORS['text_primary'],
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        
        return fig
    
    def _normalize_security_column(self, series: pd.Series) -> pd.Series:
        """Translate numeric security levels to their string color values."""
        level_map = {lvl: info['value'] for lvl, info in SECURITY_LEVELS.items()}

        def convert(val):
            try:
                return level_map[int(val)]
            except (ValueError, TypeError, KeyError):
                return str(val)

        return series.map(convert)

    # Chart generation methods - FIXED
    def create_hourly_activity_chart(self, df) -> Figure:
        """Generate hourly activity chart"""
        if df is None or df.empty:
            return self._create_empty_figure("No data available")
        
        # Extract hour from timestamp
        df_copy = df.copy()
        timestamp_col = 'Timestamp (Event Time)'
        if timestamp_col in df_copy.columns:
            df_copy['Hour'] = df_copy[timestamp_col].dt.hour
            hourly_counts = df_copy['Hour'].value_counts().sort_index()
            
            fig = px.bar(
                x=hourly_counts.index,
                y=hourly_counts.values,
                title="Access Events by Hour",
                labels={'x': 'Hour of Day', 'y': 'Number of Events'},
                color=hourly_counts.values,
                color_continuous_scale=['#1A2332', COLORS['accent']]
            )
            
            fig.update_layout(
                title="Security Level Distribution",
                plot_bgcolor=COLORS['background'],
                paper_bgcolor=COLORS['surface'],
                font_color=COLORS['text_primary'],
                title_font_color=COLORS['text_primary']
            )
            
            return fig
        
        return self._create_empty_figure("No timestamp data available")
    
    def create_security_pie_chart(self, device_attrs) -> Figure:
        """Generate security level distribution pie chart"""
        if device_attrs is None or device_attrs.empty:
            return self._create_empty_figure("No security data")
        
        if 'SecurityLevel' in device_attrs.columns:
            sec_series = self._normalize_security_column(device_attrs['SecurityLevel'])
            security_counts = sec_series.value_counts()
            
            colors = {
                'green': COLORS['success'],
                'yellow': COLORS['warning'],
                'red': COLORS['critical'],
                'unclassified': COLORS['border']
            }

            fig = go.Figure(data=[go.Pie(
                labels=security_counts.index,
                values=security_counts.values,
                marker_colors=[colors.get(level, COLORS['accent']) for level in security_counts.index],
                textinfo='label+percent',
                textfont_size=12
            )])
            
            fig.update_layout(
                plot_bgcolor=COLORS['background'],
                paper_bgcolor=COLORS['surface'],
                font_color=COLORS['text_primary'],
                title_font_color=COLORS['text_primary']
            )
            
            return fig
        
        return self._create_empty_figure("No security level data")
    
    def create_activity_heatmap(self, df) -> Figure:
        """Generate day/hour activity heatmap"""
        if df is None or df.empty:
            return self._create_empty_figure("No data for heatmap")
        
        timestamp_col = 'Timestamp (Event Time)'
        if timestamp_col in df.columns:
            df_copy = df.copy()
            df_copy['Hour'] = df_copy[timestamp_col].dt.hour
            df_copy['DayOfWeek'] = df_copy[timestamp_col].dt.day_name()
            
            # Create pivot table for heatmap
            heatmap_data = df_copy.groupby(['DayOfWeek', 'Hour']).size().unstack(fill_value=0)
            
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex(days_order)
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=list(range(24)),
                y=days_order,
                colorscale='Blues',
                text=heatmap_data.values,
                texttemplate="%{text}",
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title="Activity Heatmap (Day vs Hour)",
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week",
                plot_bgcolor=COLORS['background'],
                paper_bgcolor=COLORS['surface'],
                font_color=COLORS['text_primary'],
                title_font_color=COLORS['text_primary']
            )
            
            return fig
        
        return self._create_empty_figure("No timestamp data for heatmap")
    
    # Enhanced data processing methods
    def calculate_enhanced_metrics(self, df, device_attrs=None):
        """Calculate all enhanced metrics from data"""
        if df is None or df.empty:
            return self.get_default_enhanced_stats()
        
        timestamp_col = 'Timestamp (Event Time)'
        user_col = 'UserID (Person Identifier)'
        door_col = 'DoorID (Device Name)'
        
        metrics = {}
        
        # Basic metrics
        metrics['total_events'] = len(df)
        metrics['unique_users'] = df[user_col].nunique() if user_col in df.columns else 0
        metrics['unique_devices'] = df[door_col].nunique() if door_col in df.columns else 0
        
        if timestamp_col in df.columns:
            # Date range
            min_date = df[timestamp_col].min()
            max_date = df[timestamp_col].max()
            metrics['date_range'] = f"{min_date.strftime('%d.%m.%Y')} - {max_date.strftime('%d.%m.%Y')}"
            
            # Days and averages
            unique_days = df[timestamp_col].dt.date.nunique()
            metrics['unique_days'] = unique_days
            metrics['avg_events_per_day'] = f"Avg: {metrics['total_events'] / max(unique_days, 1):.1f} events/day"
            
            # Peak analysis
            df_copy = df.copy()
            df_copy['Hour'] = df_copy[timestamp_col].dt.hour
            df_copy['DayOfWeek'] = df_copy[timestamp_col].dt.day_name()
            df_copy['Date'] = df_copy[timestamp_col].dt.date
            
            # Peak hour
            hour_counts = df_copy['Hour'].value_counts()
            peak_hour = hour_counts.index[0] if not hour_counts.empty else "N/A"
            metrics['peak_hour'] = f"Peak: {peak_hour}:00" if peak_hour != "N/A" else "N/A"
            
            # Peak day
            day_counts = df_copy['DayOfWeek'].value_counts()
            peak_day = day_counts.index[0] if not day_counts.empty else "N/A"
            metrics['peak_day'] = f"Busiest: {peak_day}"
            
            # Daily activity breakdown
            daily_counts = df_copy.groupby('Date').size()
            busiest_date = daily_counts.idxmax() if not daily_counts.empty else None
            metrics['peak_activity_day'] = f"Peak: {busiest_date}" if busiest_date else "N/A"
        
        # User analytics
        if user_col in df.columns and metrics['unique_users'] > 0:
            user_event_counts = df[user_col].value_counts()
            metrics['avg_events_per_user'] = f"Avg: {user_event_counts.mean():.1f} events/user"
            most_active_user = user_event_counts.index[0] if not user_event_counts.empty else "N/A"
            metrics['most_active_user'] = f"Top: {most_active_user} ({user_event_counts.iloc[0]} events)"
            
            # Users per device analysis
            if door_col in df.columns:
                users_per_device = df.groupby(door_col)[user_col].nunique().mean()
                metrics['avg_users_per_device'] = f"Avg: {users_per_device:.1f} users/device"
        
        # Device analytics with enhanced features
        if device_attrs is not None and not device_attrs.empty:
            total_devices = len(device_attrs)
            entrance_devices = device_attrs['IsOfficialEntrance'].sum() if 'IsOfficialEntrance' in device_attrs.columns else 0
            high_security_devices = 0
            
            if 'SecurityLevel' in device_attrs.columns:
                sec_series = self._normalize_security_column(device_attrs['SecurityLevel'])
                high_security_devices = len(sec_series[sec_series.isin(['red', 'critical'])])
    
                # Security distribution
                security_dist = sec_series.value_counts()
                metrics['security_breakdown'] = security_dist.to_dict()
            
            metrics['total_devices_count'] = f"Total: {total_devices} devices"
            metrics['entrance_devices_count'] = f"Entrances: {entrance_devices}"
            metrics['high_security_devices'] = f"High Security: {high_security_devices}"
            
            # Floor analysis
            if 'Floor' in device_attrs.columns:
                floor_activity = df.groupby(df[door_col].map(
                    device_attrs.set_index('DoorID')['Floor'].to_dict()
                )).size()
                busiest_floor = floor_activity.idxmax() if not floor_activity.empty else "N/A"
                metrics['busiest_floor'] = f"Floor {busiest_floor}" if busiest_floor != "N/A" else "N/A"
        
        # Advanced analytics
        metrics.update(self.calculate_advanced_insights(df, device_attrs))
        
        return metrics
    
    def calculate_advanced_insights(self, df, device_attrs=None):
        """Calculate advanced insights and scores"""
        insights = {}
        
        if df is None or df.empty:
            return {
                'traffic_pattern': "No Data",
                'security_score': "N/A",
                'efficiency_score': "N/A", 
                'anomaly_count': 0
            }
        
        timestamp_col = 'Timestamp (Event Time)'
        user_col = 'UserID (Person Identifier)'
        door_col = 'DoorID (Device Name)'
        
        # Traffic pattern analysis
        if timestamp_col in df.columns:
            df_copy = df.copy()
            df_copy['Hour'] = df_copy[timestamp_col].dt.hour
            business_hours = df_copy[(df_copy['Hour'] >= 8) & (df_copy['Hour'] <= 18)]
            business_ratio = len(business_hours) / len(df_copy)
            
            if business_ratio > 0.8:
                insights['traffic_pattern'] = "Business Hours"
            elif business_ratio > 0.6:
                insights['traffic_pattern'] = "Mixed Schedule"
            else:
                insights['traffic_pattern'] = "24/7 Operation"
        
        # Security score calculation
        security_score = 85  # Base score
        if device_attrs is not None and 'SecurityLevel' in device_attrs.columns:
            sec_series = self._normalize_security_column(device_attrs['SecurityLevel'])
            high_security_ratio = len(sec_series[sec_series == 'red']) / len(device_attrs)
            security_score = min(100, 70 + (high_security_ratio * 30))
        
        insights['security_score'] = f"{security_score:.0f}%"
        
        # Efficiency analysis
        if user_col in df.columns and door_col in df.columns:
            user_device_pairs = df.groupby([user_col, door_col]).size()
            avg_accesses_per_pair = user_device_pairs.mean()
            
            if avg_accesses_per_pair > 10:
                insights['efficiency_score'] = "High"
            elif avg_accesses_per_pair > 5:
                insights['efficiency_score'] = "Medium"
            else:
                insights['efficiency_score'] = "Low"
        else:
            insights['efficiency_score'] = "N/A"
        
        # Simple anomaly detection (placeholder)
        anomaly_count = 0
        if timestamp_col in df.columns:
            # Detect unusual activity patterns (very basic)
            daily_counts = df.groupby(df[timestamp_col].dt.date).size()
            if len(daily_counts) > 1:
                mean_daily = daily_counts.mean()
                std_daily = daily_counts.std()
                anomaly_threshold = mean_daily + (2 * std_daily)
                anomaly_count = len(daily_counts[daily_counts > anomaly_threshold])
        
        insights['anomaly_count'] = anomaly_count
        
        return insights
    
    def get_default_enhanced_stats(self):
        """Default values for enhanced statistics"""
        return {
            'total_events': 0,
            'unique_users': 0,
            'unique_devices': 0,
            'date_range': "N/A",
            'avg_events_per_day': "N/A",
            'peak_hour': "N/A",
            'peak_day': "N/A",
            'peak_activity_day': "N/A",
            'avg_events_per_user': "N/A",
            'most_active_user': "N/A",
            'avg_users_per_device': "N/A",
            'total_devices_count': "0 devices",
            'entrance_devices_count': "0 entrances",
            'high_security_devices': "0 high security",
            'busiest_floor': "N/A",
            'traffic_pattern': "No Data",
            'security_score': "N/A",
            'efficiency_score': "N/A",
            'anomaly_count': 0,
            'security_breakdown': {}
        }
    
    # Export functionality
    def export_stats_to_csv(self, metrics_data):
        """Export statistics to CSV format"""
        if not metrics_data:
            return None
        
        # Convert metrics to DataFrame
        data = []
        for key, value in metrics_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    data.append({'Metric': f"{key}_{sub_key}", 'Value': sub_value})
            else:
                data.append({'Metric': key, 'Value': value})
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_bytes = csv_string.encode('utf-8')
        csv_b64 = base64.b64encode(csv_bytes).decode()
        
        return csv_b64
    
    def generate_summary_report(self, metrics_data, charts_data=None):
        """Generate a comprehensive text report"""
        if not metrics_data:
            return "No data available for report generation."
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Enhanced Analytics Report
Generated: {timestamp}

## Summary Statistics
- Total Access Events: {metrics_data.get('total_events', 'N/A')}
- Unique Users: {metrics_data.get('unique_users', 'N/A')}
- Unique Devices: {metrics_data.get('unique_devices', 'N/A')}
- Date Range: {metrics_data.get('date_range', 'N/A')}

## Activity Analysis
- {metrics_data.get('avg_events_per_day', 'N/A')}
- {metrics_data.get('peak_hour', 'N/A')}
- {metrics_data.get('peak_day', 'N/A')}
- Peak Activity Day: {metrics_data.get('peak_activity_day', 'N/A')}

## User Analytics
- {metrics_data.get('avg_events_per_user', 'N/A')}
- {metrics_data.get('most_active_user', 'N/A')}
- {metrics_data.get('avg_users_per_device', 'N/A')}

## Device & Security
- {metrics_data.get('total_devices_count', 'N/A')}
- {metrics_data.get('entrance_devices_count', 'N/A')}
- {metrics_data.get('high_security_devices', 'N/A')}
- Busiest Floor: {metrics_data.get('busiest_floor', 'N/A')}

## Advanced Insights
- Traffic Pattern: {metrics_data.get('traffic_pattern', 'N/A')}
- Security Score: {metrics_data.get('security_score', 'N/A')}
- Efficiency Rating: {metrics_data.get('efficiency_score', 'N/A')}
- Anomaly Alerts: {metrics_data.get('anomaly_count', 0)} detected

## Security Level Distribution
"""
        
        if 'security_breakdown' in metrics_data:
            for level, count in metrics_data['security_breakdown'].items():
                report += f"- {level.title()}: {count} devices\n"
        
        report += f"""
## Recommendations
Based on the analysis, consider:
1. Monitor peak hours ({metrics_data.get('peak_hour', 'N/A')}) for capacity planning
2. Review security policies for {metrics_data.get('high_security_devices', '0')} high-security devices
3. Investigate {metrics_data.get('anomaly_count', 0)} anomalous activity patterns
4. Optimize access flows on busiest floor: {metrics_data.get('busiest_floor', 'N/A')}

---
Report generated by Enhanced Analytics Dashboard
"""
        
        return report


# Factory functions for easy component creation
def create_enhanced_stats_component():
    """Factory function to create enhanced stats component instance"""
    return EnhancedStatsComponent()

# Backward compatibility
StatsComponent = EnhancedStatsComponent  # Alias for existing code

# Convenience functions
def create_stats_container():
    """Create the enhanced stats container"""
    component = EnhancedStatsComponent()
    return component.create_enhanced_stats_container()

def create_custom_header(main_logo_path):
    """Create the enhanced custom header"""
    component = EnhancedStatsComponent()
    return component.create_custom_header(main_logo_path)