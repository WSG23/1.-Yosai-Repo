# config/__init__.py
"""
Configuration package - Working with current structure
"""

# Import settings directly
from .settings import (
    get_settings,
    get_config,
    get_ui_config,
    get_processing_config,
    AppConfig,
    UIConfig,
    ProcessingConfig,
    Settings,
    REQUIRED_INTERNAL_COLUMNS,
    SECURITY_LEVELS,
    FILE_LIMITS,
    DEFAULT_ICONS,
    settings,
)

# Simple aliases
# Backwards compatibility aliases
def get_config_legacy():
    """Get main application configuration"""
    return get_config()

def get_ui_config_legacy():
    """Get UI configuration"""
    return get_ui_config()

def get_processing_config_legacy():
    """Get processing configuration"""
    return get_processing_config()

__all__ = [
    'get_settings',
    'Settings',
    'AppConfig',
    'UIConfig',
    'ProcessingConfig',
    'settings',
    'get_config',
    'get_ui_config',
    'get_processing_config',
    'get_config_legacy',
    'get_ui_config_legacy',
    'get_processing_config_legacy',
    'REQUIRED_INTERNAL_COLUMNS',
    'SECURITY_LEVELS',
    'DEFAULT_ICONS',
    'FILE_LIMITS'
]

