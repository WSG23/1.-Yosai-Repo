# ui/core/component_registry.py
"""
Enhanced component registry with factory patterns and dependency injection
"""
from typing import Dict, Any, Type, Callable, Optional, Union, TypeVar
from dataclasses import dataclass
import dash
from dash import html, dcc

from ui.core.interfaces import ComponentInterface, StatelessComponent, StatefulComponent
from ui.core.dependency_injection import ServiceContainer, get_container
from ui.core.config_manager import get_component_config

# Try to import the correct Dash component base class
try:
    from dash.development.base_component import Component as DashComponent
    ComponentType = Union[html.Div, DashComponent]
except ImportError:
    # Fallback for older Dash versions
    ComponentType = Union[html.Div, Any]

T = TypeVar('T', bound=ComponentInterface)

@dataclass
class ComponentRegistration:
    """Component registration information"""
    component_class: Type[ComponentInterface]
    factory_function: Optional[Callable] = None
    is_stateful: bool = False
    default_props: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.default_props is None:
            self.default_props = {}

class ComponentFactory:
    """Factory for creating configured component instances"""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self._registrations: Dict[str, ComponentRegistration] = {}
    
    def register(self, name: str, component_class: Type[T], 
                factory_function: Optional[Callable] = None,
                default_props: Optional[Dict[str, Any]] = None) -> None:
        """Register a component class with the factory"""
        
        is_stateful = issubclass(component_class, StatefulComponent)
        
        self._registrations[name] = ComponentRegistration(
            component_class=component_class,
            factory_function=factory_function,
            is_stateful=is_stateful,
            default_props=default_props or {}
        )
    
    def create(self, name: str, component_id: Optional[str] = None, **props) -> ComponentInterface:
        """Create a component instance"""
        
        if name not in self._registrations:
            raise ValueError(f"Component '{name}' not registered")
        
        registration = self._registrations[name]
        
        # Get component configuration
        config = get_component_config(name)
        
        # Merge default props with provided props
        final_props = {**registration.default_props, **props}
        
        # Create component instance
        if registration.factory_function:
            # Use custom factory function
            component = registration.factory_function(
                config=config,
                component_id=component_id,
                container=self.container,
                **final_props
            )
        else:
            # Use standard constructor
            component = registration.component_class(
                config=config,
                component_id=component_id,
                **final_props
            )
        
        # Inject container for dependency injection
        if hasattr(component, '_container'):
            component._container = self.container
        
        return component

class ComponentRegistry:
    """Enhanced component registry with dependency injection"""
    
    def __init__(self, container: Optional[ServiceContainer] = None):
        self.container = container or get_container()
        self.factory = ComponentFactory(self.container)
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize registry with default components"""
        if self._initialized:
            return
        self._initialized = True
    
    def register_component(self, name: str, component_class: Type[ComponentInterface],
                         factory_function: Optional[Callable] = None,
                         default_props: Optional[Dict[str, Any]] = None) -> None:
        """Register a component"""
        self.factory.register(name, component_class, factory_function, default_props)
    
    def create_component(self, name: str, component_id: Optional[str] = None, **props) -> ComponentInterface:
        """Create component instance"""
        self.initialize()
        return self.factory.create(name, component_id, **props)
    
    def render(self, name: str, component_id: Optional[str] = None, **props) -> ComponentType:
        """Create and render component in one step"""
        component = self.create_component(name, component_id, **props)
        return component.render(**props)

# Global registry instance
_global_registry = ComponentRegistry()

def get_registry() -> ComponentRegistry:
    """Get the global component registry"""
    return _global_registry

def register_component(name: str, component_class: Type[ComponentInterface], **options) -> None:
    """Register component with global registry"""
    _global_registry.register_component(name, component_class, **options)

def create_component(name: str, component_id: Optional[str] = None, **props) -> ComponentInterface:
    """Create component using global registry"""
    return _global_registry.create_component(name, component_id, **props)

def render_component(name: str, component_id: Optional[str] = None, **props) -> ComponentType:
    """Render component using global registry"""
    return _global_registry.render(name, component_id, **props)
