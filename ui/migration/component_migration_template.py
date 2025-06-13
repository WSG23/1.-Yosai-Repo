# migration/component_migration_template.py
"""
Template for migrating existing components to modular architecture
"""
from typing import Dict, Any, Optional
from dash import html, dcc, Input, Output, State, callback, no_update
import dash

from ui.core.interfaces import StatefulComponent, ComponentConfig
from ui.core.dependency_injection import inject, DataService, EventBus
from ui.core.config_manager import get_component_config

class TemplateComponent(StatefulComponent):
    """Template for migrating components to modular architecture"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id)
        self.main_id = f"{self.component_id}-main"
        self.content_id = f"{self.component_id}-content"
        self.props = kwargs
        
    def _validate_config(self) -> None:
        """Validate required configuration"""
        required_settings = ['setting1', 'setting2']
        for setting in required_settings:
            if not self.get_setting(setting):
                print(f"Warning: Missing setting '{setting}', using defaults")
    
    def render(self, **props):
        """Render the component"""
        all_props = {**self.props, **props}
        
        return html.Div([
            self._create_main_content(),
            html.Div(id=self.content_id)
        ], id=self.component_id, style=self._get_container_style())
    
    def _create_main_content(self) -> html.Div:
        """Create main component content"""
        return html.Div([
            html.H3("Template Component"),
            html.P("Replace this with actual component content"),
            html.Button("Click Me", id=self.main_id, n_clicks=0)
        ])
    
    def _get_container_style(self) -> Dict[str, Any]:
        """Get container styling"""
        base_style = {
            'margin': '16px 0',
            'padding': '16px',
            'borderRadius': '8px',
            'backgroundColor': '#ffffff',
            'border': '1px solid #e5e7eb'
        }
        return {**base_style, **self.get_style('container')}
    
    def register_callbacks(self, app: dash.Dash) -> None:
        """Register component callbacks"""
        
        @app.callback(
            Output(self.content_id, 'children'),
            Input(self.main_id, 'n_clicks'),
            prevent_initial_call=True
        )
        def handle_interaction(n_clicks):
            if n_clicks is None:
                return no_update
            return self._handle_interaction_with_injection(n_clicks)
    
    def _handle_interaction_with_injection(self, n_clicks):
        """Handle component interaction with dependency injection wrapper"""
        
        from ui.core.dependency_injection import get_container
        container = get_container()
        
        try:
            data_service = container.get(DataService)
            event_bus = container.get(EventBus)
        except ValueError:
            from ui.core.dependency_injection import InMemoryDataService, SimpleEventBus
            data_service = InMemoryDataService()
            event_bus = SimpleEventBus()
        
        return self._handle_interaction_callback(data_service, event_bus, n_clicks)
    
    def _handle_interaction_callback(self, data_service: DataService, event_bus: EventBus, n_clicks):
        """Handle component interaction with dependency injection"""
        
        data_service.save_data(f"{self.component_id}_clicks", n_clicks)
        
        event_bus.publish('component_clicked', {
            'component_id': self.component_id,
            'clicks': n_clicks
        })
        
        return html.P(f"Clicked {n_clicks} times")

def create_template_component(component_id: Optional[str] = None, **props):
    """Factory function to create template component"""
    config = get_component_config('template')
    return TemplateComponent(config, component_id, **props)

def register_template_component():
    """Register template component with global registry"""
    from ui.core.component_registry import register_component
    
    register_component(
        'template',
        TemplateComponent,
        default_props={}
    )