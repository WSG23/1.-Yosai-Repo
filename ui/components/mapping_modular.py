# ui/components/mapping_modular.py
"""
Modular mapping component using new architecture
"""
from typing import Dict, Any, Optional, List
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import dash
import pandas as pd

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.dependency_injection import inject, DataService, EventBus
from ui.core.config_manager import get_component_config

class ModularMappingComponent(StatefulComponent):
    """Modular mapping component with clean separation of concerns"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.mapping_id = f"{self.component_id}-mapping"
        self.submit_id = f"{self.component_id}-submit"
        self.output_id = f"{self.component_id}-output"
        
        # Store additional props
        self.props = kwargs
        
    def _validate_config(self) -> None:
        """Validate required configuration"""
        required_settings = ['auto_suggest', 'fuzzy_threshold']
        for setting in required_settings:
            if not self.get_setting(setting):
                print(f"Warning: Missing mapping setting '{setting}', using defaults")
    
    def render(self, **props) -> html.Div:
        """Render the mapping component"""
        return html.Div([
            html.H3("📋 Column Mapping", style={'margin': '16px 0', 'color': '#2c3e50'}),
            html.P("Map your CSV columns to the required internal columns:", 
                  style={'margin': '8px 0', 'color': '#666'}),
            self._create_mapping_interface(),
            self._create_submit_button(),
            html.Div(id=self.output_id, style={'margin': '16px 0'})
        ], id=self.component_id, style=self._get_container_style())
    
    def _create_mapping_interface(self) -> html.Div:
        """Create the mapping interface"""
        return html.Div([
            html.Div([
                html.Label("Select columns to map:", style={'fontWeight': 'bold', 'margin': '8px 0'}),
                dcc.Dropdown(
                    id=self.mapping_id,
                    options=[
                        {'label': 'UserID Column', 'value': 'userid'},
                        {'label': 'Timestamp Column', 'value': 'timestamp'},
                        {'label': 'DoorID Column', 'value': 'doorid'},
                        {'label': 'EventType Column', 'value': 'eventtype'}
                    ],
                    multi=True,
                    placeholder="Select columns to map to internal schema..."
                )
            ], style={'margin': '16px 0'})
        ], style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px',
            'border': '1px solid #e5e7eb'
        })
    
    def _create_submit_button(self) -> html.Div:
        """Create submit button"""
        return html.Div([
            dbc.Button(
                "Apply Column Mapping",
                id=self.submit_id,
                color="primary",
                size="lg",
                style={'margin': '16px 0'}
            )
        ])
    
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
            Output(self.output_id, 'children'),
            Input(self.submit_id, 'n_clicks'),
            State(self.mapping_id, 'value'),
            prevent_initial_call=True
        )
        def handle_mapping(n_clicks, selected_columns):
            if n_clicks is None:
                return no_update
            return self._handle_mapping_with_injection(selected_columns)
    
    def _handle_mapping_with_injection(self, selected_columns):
        """Handle mapping with dependency injection wrapper"""
        
        from ui.core.dependency_injection import get_container
        container = get_container()
        
        try:
            data_service = container.get(DataService)
            event_bus = container.get(EventBus)
        except ValueError:
            from ui.core.dependency_injection import InMemoryDataService, SimpleEventBus
            data_service = InMemoryDataService()
            event_bus = SimpleEventBus()
        
        return self._handle_mapping_callback(data_service, event_bus, selected_columns)
    
    def _handle_mapping_callback(self, data_service: DataService, event_bus: EventBus, selected_columns):
        """Handle mapping with dependency injection"""
        
        if not selected_columns:
            return dbc.Alert("⚠️ Please select columns to map.", color="warning")
        
        # Store mapping data
        mapping_data = {
            'selected_columns': selected_columns,
            'timestamp': str(pd.Timestamp.now()),
            'component_id': self.component_id
        }
        data_service.save_data(f"{self.component_id}_mapping", mapping_data)
        
        # Publish event
        event_bus.publish('mapping_applied', {
            'component_id': self.component_id,
            'mapping': mapping_data
        })
        
        # Return success message
        return dbc.Alert([
            html.Strong("✅ Column Mapping Applied Successfully!"),
            html.Br(),
            f"📊 Mapped {len(selected_columns)} columns: {', '.join(selected_columns)}",
            html.Br(),
            html.Small(f"Applied at: {mapping_data['timestamp']}", style={'opacity': '0.7'})
        ], color="success")

# Factory function
def create_modular_mapping_component(component_id: Optional[str] = None, **props):
    """Factory function to create modular mapping component"""
    config = get_component_config('mapping')
    return ModularMappingComponent(config, component_id, **props)

# Registration function
def register_modular_mapping_component():
    """Register modular mapping component with global registry"""
    from ui.core.component_registry import register_component
    
    register_component(
        'mapping_modular',
        ModularMappingComponent,
        default_props={
            'auto_suggest': True,
            'fuzzy_threshold': 0.6
        }
    )
