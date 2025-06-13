# ui/components/enhanced_stats_modular.py
"""
Modular enhanced stats component using new architecture
"""
from typing import Dict, Any, Optional, List
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash
import pandas as pd
import plotly.graph_objs as go

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.dependency_injection import inject, DataService, EventBus
from ui.core.config_manager import get_component_config

class ModularEnhancedStatsComponent(StatefulComponent):
    """Modular enhanced stats component with clean separation of concerns"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.refresh_id = f"{self.component_id}-refresh"
        self.stats_id = f"{self.component_id}-stats"
        self.chart_id = f"{self.component_id}-chart"
        
        # Store additional props
        self.props = kwargs
        
    def _validate_config(self) -> None:
        """Validate required configuration"""
        # Don't raise errors, just use defaults
        pass
    
    def render(self, **props) -> html.Div:
        """Render the enhanced stats component"""
        return html.Div([
            html.H3("📊 Enhanced Statistics", style={'margin': '16px 0', 'color': '#2c3e50'}),
            self._create_controls(),
            self._create_stats_display(),
            self._create_chart_display()
        ], id=self.component_id, style=self._get_container_style())
    
    def _create_controls(self) -> html.Div:
        """Create control buttons"""
        return html.Div([
            dbc.Button(
                "🔄 Refresh Stats",
                id=self.refresh_id,
                color="secondary",
                size="sm",
                style={'margin': '8px 0'}
            )
        ])
    
    def _create_stats_display(self) -> html.Div:
        """Create stats display area"""
        return html.Div(
            id=self.stats_id,
            children=self._create_default_stats(),
            style={
                'padding': '20px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '8px',
                'margin': '16px 0'
            }
        )
    
    def _create_chart_display(self) -> html.Div:
        """Create chart display area"""
        return html.Div([
            dcc.Graph(
                id=self.chart_id,
                figure=self._create_default_chart(),
                style={'height': f"{self.get_setting('chart_height', 300)}px"}
            )
        ], style={'margin': '16px 0'})
    
    def _create_default_stats(self) -> List:
        """Create default stats display"""
        return [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("0", className="card-title"),
                            html.P("Total Records", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("0", className="card-title"),
                            html.P("Unique Users", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("0", className="card-title"),
                            html.P("Unique Doors", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("0%", className="card-title"),
                            html.P("Success Rate", className="card-text")
                        ])
                    ])
                ], md=3)
            ])
        ]
    
    def _create_default_chart(self) -> go.Figure:
        """Create default chart"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[2, 4, 3, 5, 6],
            mode='lines+markers',
            name='Sample Data'
        ))
        fig.update_layout(
            title="Sample Statistics Chart",
            xaxis_title="Time",
            yaxis_title="Count",
            template="plotly_white"
        )
        return fig
    
    def _get_container_style(self) -> Dict[str, Any]:
        """Get container styling"""
        base_style = {
            'margin': '20px 0',
            'padding': '20px',
            'borderRadius': '8px',
            'backgroundColor': '#ffffff',
            'border': '1px solid #e5e7eb',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
        return {**base_style, **self.get_style('container')}
    
    def register_callbacks(self, app: dash.Dash) -> None:
        """Register component callbacks"""
        
        @app.callback(
            [Output(self.stats_id, 'children'),
             Output(self.chart_id, 'figure')],
            Input(self.refresh_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def handle_refresh(n_clicks):
            if n_clicks is None:
                return no_update, no_update
            return self._handle_refresh_with_injection()
    
    def _handle_refresh_with_injection(self):
        """Handle refresh with dependency injection wrapper"""
        
        from ui.core.dependency_injection import get_container
        container = get_container()
        
        try:
            data_service = container.get(DataService)
            event_bus = container.get(EventBus)
        except ValueError:
            from ui.core.dependency_injection import InMemoryDataService, SimpleEventBus
            data_service = InMemoryDataService()
            event_bus = SimpleEventBus()
        
        return self._handle_refresh_callback(data_service, event_bus)
    
    def _handle_refresh_callback(self, data_service: DataService, event_bus: EventBus):
        """Handle refresh with dependency injection"""
        
        # Generate sample stats
        import random
        stats = {
            'total_records': random.randint(1000, 5000),
            'unique_users': random.randint(100, 500),
            'unique_doors': random.randint(10, 50),
            'success_rate': random.randint(85, 98)
        }
        
        # Store stats data
        data_service.save_data(f"{self.component_id}_stats", stats)
        
        # Publish event
        event_bus.publish('stats_refreshed', {
            'component_id': self.component_id,
            'stats': stats
        })
        
        # Create updated stats display
        updated_stats = [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{stats['total_records']:,}", className="card-title"),
                            html.P("Total Records", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{stats['unique_users']:,}", className="card-title"),
                            html.P("Unique Users", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{stats['unique_doors']:,}", className="card-title"),
                            html.P("Unique Doors", className="card-text")
                        ])
                    ])
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{stats['success_rate']}%", className="card-title"),
                            html.P("Success Rate", className="card-text")
                        ])
                    ])
                ], md=3)
            ])
        ]
        
        # Create updated chart
        updated_chart = go.Figure()
        updated_chart.add_trace(go.Bar(
            x=['Records', 'Users', 'Doors'],
            y=[stats['total_records'], stats['unique_users'], stats['unique_doors']],
            name='Current Stats'
        ))
        updated_chart.update_layout(
            title="Updated Statistics",
            template="plotly_white"
        )
        
        return updated_stats, updated_chart

# Factory function
def create_modular_enhanced_stats_component(component_id: Optional[str] = None, **props):
    """Factory function to create modular enhanced stats component"""
    config = get_component_config('stats')
    return ModularEnhancedStatsComponent(config, component_id, **props)

# Registration function
def register_modular_enhanced_stats_component():
    """Register modular enhanced stats component with global registry"""
    from ui.core.component_registry import register_component
    
    register_component(
        'enhanced_stats_modular',
        ModularEnhancedStatsComponent,
        default_props={
            'show_advanced': False,
            'chart_height': 400
        }
    )
