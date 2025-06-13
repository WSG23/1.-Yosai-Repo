# ui/core/interfaces.py
"""
Core interfaces and base classes for UI components
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import dash
from dash import html

@dataclass
class ComponentConfig:
    """Standardized configuration for all components"""
    theme: Dict[str, Any]
    icons: Dict[str, str] 
    settings: Dict[str, Any]
    callbacks: Optional[Dict[str, Any]] = None

class ComponentInterface(ABC):
    """Base interface that all UI components must implement"""
    
    def __init__(self, config: ComponentConfig, **kwargs):
        self.config = config
        self._initialized = False
        self._container: Optional[Any] = None  # For dependency injection
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate that required configuration is present"""
        pass
    
    @abstractmethod
    def render(self, **props) -> html.Div:  # ← THIS IS THE KEY FIX
        """Render the component with given props"""
        pass
    
    @abstractmethod
    def get_component_id(self) -> str:
        """Get unique component identifier"""
        pass
    
    def get_style(self, style_key: str) -> Dict[str, Any]:
        """Get theme-based styles safely"""
        return self.config.theme.get('components', {}).get(
            self.__class__.__name__.lower(), {}
        ).get(style_key, {})
    
    def get_icon(self, icon_key: str) -> str:
        """Get icon safely with fallback"""
        return self.config.icons.get(icon_key, "📄")
    
    def get_setting(self, setting_key: str, default: Any = None) -> Any:
        """Get setting safely with default"""
        return self.config.settings.get(setting_key, default)

class StatelessComponent(ComponentInterface):
    """Base class for stateless UI components"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None):
        super().__init__(config)
        self.component_id = component_id if component_id is not None else f"{self.__class__.__name__.lower()}-{id(self)}"
    
    def get_component_id(self) -> str:
        return self.component_id

class StatefulComponent(ComponentInterface):
    """Base class for stateful UI components with callbacks"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None):
        super().__init__(config)
        self.component_id = component_id if component_id is not None else f"{self.__class__.__name__.lower()}-{id(self)}"
        self._callbacks_registered = False
    
    @abstractmethod
    def register_callbacks(self, app: dash.Dash) -> None:
        """Register component callbacks"""
        pass
    
    def get_component_id(self) -> str:
        return self.component_id