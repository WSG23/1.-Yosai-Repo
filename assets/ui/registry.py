# ui/registry.py
"""
Component registry to resolve circular dependencies
"""
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

@dataclass
class ComponentConfig:
    """Configuration for a component"""
    icons: Dict[str, str]
    theme: Dict[str, Any]
    settings: Dict[str, Any]

class ComponentRegistry:
    """Central registry for UI components"""
    
    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._config: Optional[ComponentConfig] = None
    
    def configure(self, icons: Dict[str, str], theme: Dict[str, Any], settings: Dict[str, Any]):
        """Configure the registry"""
        self._config = ComponentConfig(icons, theme, settings)
    
    def register(self, name: str, component_class: type):
        """Register a component class"""
        self._components[name] = component_class
    
    def create(self, name: str, **kwargs) -> Any:
        """Create a component instance"""
        if name not in self._components:
            raise ValueError(f"Component '{name}' not registered")
        
        if self._config is None:
            raise RuntimeError("Registry not configured")
        
        component_class = self._components[name]
        
        # Inject configuration
        if hasattr(component_class, '__init__'):
            return component_class(
                config=self._config,
                **kwargs
            )
        return component_class(**kwargs)
    
    def get_config(self) -> ComponentConfig:
        """Get current configuration"""
        if self._config is None:
            raise RuntimeError("Registry not configured")
        return self._config

# Global registry instance
registry = ComponentRegistry()

def get_registry() -> ComponentRegistry:
    """Get the component registry"""
    return registry