# ui/core/config_manager.py
"""
Fixed configuration management system
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json
import os
from ui.core.interfaces import ComponentConfig

@dataclass
class ThemeConfig:
    """Theme configuration with component-specific styling"""
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, str] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        """Create theme config from dictionary"""
        return cls(**data)
    
    def get_component_theme(self, component_name: str) -> Dict[str, Any]:
        """Get theme for specific component"""
        return self.components.get(component_name.lower(), {})

@dataclass 
class IconConfig:
    """Icon configuration with categorization"""
    actions: Dict[str, str] = field(default_factory=dict)
    status: Dict[str, str] = field(default_factory=dict)
    data: Dict[str, str] = field(default_factory=dict)
    navigation: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IconConfig':
        """Create icon config from dictionary"""
        return cls(**data)
    
    def to_flat_dict(self) -> Dict[str, str]:
        """Convert to flat dictionary for backward compatibility"""
        result = {}
        for category in ['actions', 'status', 'data', 'navigation']:
            category_dict = getattr(self, category, {})
            for key, value in category_dict.items():
                result[f"{category}_{key}"] = value
                result[key] = value  # Also add without prefix for compatibility
        return result

@dataclass
class ComponentSettings:
    """Component-specific settings"""
    upload: Dict[str, Any] = field(default_factory=dict)
    graph: Dict[str, Any] = field(default_factory=dict)
    mapping: Dict[str, Any] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentSettings':
        """Create settings from dictionary"""
        return cls(
            upload=data.get('upload', {}),
            graph=data.get('graph', {}),
            mapping=data.get('mapping', {}),
            stats=data.get('stats', {})
        )
    
    def get_component_settings(self, component_name: str) -> Dict[str, Any]:
        """Get settings for specific component"""
        return getattr(self, component_name.lower(), {})

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self._theme: Optional[ThemeConfig] = None
        self._icons: Optional[IconConfig] = None
        self._settings: Optional[ComponentSettings] = None
        self._loaded = False
    
    def load_config(self, force_reload: bool = False) -> None:
        """Load all configuration files"""
        if self._loaded and not force_reload:
            return
        
        print(f"🔧 Loading configuration from {self.config_dir}")
        
        # Load component settings FIRST - this is critical
        settings_path = os.path.join(self.config_dir, "components.json")
        print(f"🔍 Looking for components config at: {settings_path}")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    settings_data = json.load(f)
                print(f"✅ Loaded components config: {list(settings_data.keys())}")
                self._settings = ComponentSettings.from_dict(settings_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"❌ Failed to load components config: {e}")
                self._settings = self._get_default_settings()
        else:
            print(f"⚠️ Components config file not found at {settings_path}")
            self._settings = self._get_default_settings()
        
        # Load theme configuration
        self._theme = self._get_default_theme()
        
        # Load icon configuration  
        self._icons = self._get_default_icons()
        
        self._loaded = True
        print("✅ Configuration loading completed")
    
    def get_component_config(self, component_name: str) -> ComponentConfig:
        """Get complete configuration for a component"""
        self.load_config()
        
        if self._theme is None or self._icons is None or self._settings is None:
            raise RuntimeError("Configuration not loaded properly")
        
        settings = self._settings.get_component_settings(component_name)
        print(f"🔧 Component '{component_name}' settings: {settings}")
        
        return ComponentConfig(
            theme=self._theme.get_component_theme(component_name),
            icons=self._icons.to_flat_dict(),
            settings=settings
        )
    
    def _get_default_theme(self) -> ThemeConfig:
        """Get default theme configuration"""
        return ThemeConfig(
            colors={
                "primary": "#1f2937",
                "secondary": "#6b7280",
                "accent": "#3b82f6",
                "surface": "#ffffff",
                "background": "#f9fafb"
            },
            typography={
                "font_family": "Inter, sans-serif",
                "font_size_base": "14px",
                "font_weight_normal": "400"
            },
            spacing={
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            components={}
        )
    
    def _get_default_icons(self) -> IconConfig:
        """Get default icon configuration"""
        return IconConfig(
            actions={"upload": "📤", "download": "📥", "refresh": "🔄"},
            status={"success": "✅", "error": "❌", "warning": "⚠️"},
            data={"file": "📄", "csv": "📊", "json": "📋"},
            navigation={"next": "➡️", "previous": "⬅️", "home": "🏠"}
        )
    
    def _get_default_settings(self) -> ComponentSettings:
        """Get comprehensive default component settings"""
        return ComponentSettings(
            upload={
                "max_file_size": 50 * 1024 * 1024,  # 50MB 
                "allowed_extensions": [".csv", ".json"],
                "secure_validation": True,
                "upload_timeout": 30,
                "auto_process": True,
                "show_preview": True,
                "max_preview_rows": 10
            },
            graph={
                "default_layout": "cose",
                "show_labels": True,
                "interactive": True,
                "animation_duration": 300,
                "node_size": 20,
                "edge_width": 2
            },
            mapping={
                "auto_suggest": True,
                "fuzzy_threshold": 0.6,
                "show_confidence": True,
                "allow_custom_mapping": True
            },
            stats={
                "show_advanced": False,
                "chart_height": 300,
                "show_data_quality": True,
                "max_categories": 10
            }
        )

# Global configuration manager
config_manager = ConfigManager()

def get_component_config(component_name: str) -> ComponentConfig:
    """Get configuration for a specific component"""
    return config_manager.get_component_config(component_name)

# Force load config on import - with error handling
try:
    config_manager.load_config()
except Exception as e:
    print(f"⚠️ Configuration loading error: {e}")
    print("🔧 Using fallback defaults")