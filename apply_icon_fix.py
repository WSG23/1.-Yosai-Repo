#!/usr/bin/env python3
"""
Apply the get_icon method fix to resolve ModularUploadComponent error
"""

def apply_icon_method_fix():
    """Add get_icon method to interfaces.py"""
    
    fixed_interfaces_content = '''# ui/core/interfaces.py - Fixed with get_icon method
"""
Updated component interfaces with icon support
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class ComponentConfig:
    """Configuration container for components"""
    theme: Dict[str, Any] = field(default_factory=dict)
    icons: Dict[str, str] = field(default_factory=dict) 
    settings: Dict[str, Any] = field(default_factory=dict)

class ComponentInterface(ABC):
    """Base interface for all UI components"""
    
    def __init__(self, config: ComponentConfig, **kwargs):
        self.config = config
        self.props = kwargs
    
    @abstractmethod
    def render(self, **props) -> Any:
        """Render the component - returns Dash component"""
        pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value with default fallback"""
        return self.config.settings.get(key, default)
    
    def get_theme(self, key: str, default: Any = None) -> Any:
        """Get a theme value with default fallback"""
        return self.config.theme.get(key, default)
    
    def get_style(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get style configuration"""
        if default is None:
            default = {}
        return self.config.theme.get(f"{key}_style", default)
    
    def get_icon(self, icon_name: str, default: str = "📄") -> str:
        """Get icon by name with fallback to default"""
        # Try exact match first
        if icon_name in self.config.icons:
            return self.config.icons[icon_name]
        
        # Try with common prefixes
        icon_keys = [
            icon_name,
            f"actions_{icon_name}",
            f"status_{icon_name}",
            f"data_{icon_name}",
            f"navigation_{icon_name}"
        ]
        
        for key in icon_keys:
            if key in self.config.icons:
                return self.config.icons[key]
        
        # Default icon mappings for common names
        default_icons = {
            'upload': '📤',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'file': '📄',
            'csv': '📊',
            'json': '📋',
            'download': '📥',
            'refresh': '🔄'
        }
        
        return default_icons.get(icon_name, default)

class StatelessComponent(ComponentInterface):
    """Component without state management - simple render only"""
    
    def __init__(self, config: ComponentConfig, **kwargs):
        super().__init__(config, **kwargs)
    
    def render(self, **props) -> Any:
        """Render the component - override in subclasses"""
        raise NotImplementedError("Subclasses must implement render method")

class StatefulComponent(ComponentInterface):
    """Component with state management capabilities"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, **kwargs)
        self.component_id = component_id or self._generate_id()
        self._validate_config()
    
    def _generate_id(self) -> str:
        """Generate unique component ID"""
        import uuid
        return f"component-{uuid.uuid4().hex[:8]}"
    
    def _validate_config(self) -> None:
        """Validate component configuration - Base implementation"""
        # Base interface - override in subclasses for specific validation
        pass
    
    def get_required_setting(self, key: str) -> Any:
        """Get a required setting, raise error if missing"""
        value = self.get_setting(key)
        if value is None:
            raise ValueError(f"Missing required setting: {key}")
        return value
    
    def register_callbacks(self, app) -> None:
        """Register component callbacks - override in subclasses"""
        pass

class ConfigurableComponent(StatefulComponent):
    """Component with comprehensive configuration support"""
    
    def __init__(self, config: ComponentConfig, component_id: Optional[str] = None, **kwargs):
        super().__init__(config, component_id, **kwargs)
        
    def _validate_config(self) -> None:
        """Validate configuration with fallbacks"""
        # Don't raise errors - just log warnings and use defaults
        required_settings = self._get_required_settings()
        for setting in required_settings:
            if not self.get_setting(setting):
                print(f"Warning: Missing setting '{setting}', using defaults")
    
    def _get_required_settings(self) -> list:
        """Override in subclasses to specify required settings"""
        return []
'''
    
    with open('ui/core/interfaces.py', 'w') as f:
        f.write(fixed_interfaces_content)
    
    print("✅ Added get_icon method to interfaces.py")

def test_icon_access():
    """Test that icon access works"""
    try:
        from ui.core.config_manager import get_component_config
        from ui.core.interfaces import ComponentInterface
        
        # Create a test component config
        config = get_component_config('upload')
        
        # Create a dummy component to test icon access
        class TestComponent(ComponentInterface):
            def render(self, **props):
                return None
        
        test_comp = TestComponent(config)
        upload_icon = test_comp.get_icon('upload')
        print(f"✅ Icon access test passed: upload = {upload_icon}")
        
    except Exception as e:
        print(f"⚠️ Icon access test error: {e}")

if __name__ == '__main__':
    print("🔧 Applying get_icon method fix...")
    apply_icon_method_fix()
    test_icon_access()
    print("🧪 Try again: python3 run.py")