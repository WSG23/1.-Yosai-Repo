# ui/core/config_manager.py
"""
Centralized configuration management system
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
        return cls(**data)
    
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
        
        # Load theme configuration
        theme_path = os.path.join(self.config_dir, "theme.json")
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    theme_data = json.load(f)
                self._theme = ThemeConfig.from_dict(theme_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load theme config: {e}")
                self._theme = self._get_default_theme()
        else:
            self._theme = self._get_default_theme()
        
        # Load icon configuration  
        icons_path = os.path.join(self.config_dir, "icons.json")
        if os.path.exists(icons_path):
            try:
                with open(icons_path, 'r') as f:
                    icons_data = json.load(f)
                self._icons = IconConfig.from_dict(icons_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load icons config: {e}")
                self._icons = self._get_default_icons()
        else:
            self._icons = self._get_default_icons()
        
        # Load component settings
        settings_path = os.path.join(self.config_dir, "components.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    settings_data = json.load(f)
                self._settings = ComponentSettings.from_dict(settings_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load components config: {e}")
                self._settings = self._get_default_settings()
        else:
            self._settings = self._get_default_settings()
        
        self._loaded = True
    
    def get_component_config(self, component_name: str) -> ComponentConfig:
        """Get complete configuration for a component"""
        self.load_config()
        
        if self._theme is None or self._icons is None or self._settings is None:
            raise RuntimeError("Configuration not loaded properly")
        
        return ComponentConfig(
            theme=self._theme.get_component_theme(component_name),
            icons=self._icons.to_flat_dict(),
            settings=self._settings.get_component_settings(component_name)
        )
    
    def _get_default_theme(self) -> ThemeConfig:
        """Get default theme configuration"""
        # Import your existing style config
        try:
            from ui.themes.style_config import COLORS, TYPOGRAPHY, SPACING
            return ThemeConfig(
                colors=COLORS,
                typography=TYPOGRAPHY,
                spacing=SPACING,
                components={}
            )
        except ImportError:
            # Fallback if style_config is not available
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
        try:
            from config.settings import DEFAULT_ICONS
            # Parse your existing icons into categories
            return IconConfig(
                actions={"upload": "📤", "download": "📥", "refresh": "🔄"},
                status={"success": "✅", "error": "❌", "warning": "⚠️"},
                data={"file": "📄", "csv": "📊", "json": "📋"},
                navigation={"next": "➡️", "previous": "⬅️", "home": "🏠"}
            )
        except ImportError:
            # Fallback if settings not available
            return IconConfig(
                actions={"upload": "📤", "download": "📥", "refresh": "🔄"},
                status={"success": "✅", "error": "❌", "warning": "⚠️"},
                data={"file": "📄", "csv": "📊", "json": "📋"},
                navigation={"next": "➡️", "previous": "⬅️", "home": "🏠"}
            )
    
    def _get_default_settings(self) -> ComponentSettings:
        """Get default component settings"""
        return ComponentSettings(
            upload={"max_file_size": 10 * 1024 * 1024, "accepted_types": [".csv", ".json"]},
            graph={"default_layout": "cose", "show_labels": True},
            mapping={"auto_suggest": True, "fuzzy_threshold": 0.6},
            stats={"show_advanced": False, "chart_height": 300}
        )

# Global configuration manager
config_manager = ConfigManager()

def get_component_config(component_name: str) -> ComponentConfig:
    """Get configuration for a specific component"""
    return config_manager.get_component_config(component_name)