# config/settings.py
"""
Unified Configuration - SINGLE SOURCE OF TRUTH
Replaces all other config files
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import os
from utils.logging_config import get_logger

logger = get_logger(__name__)

# ============================================================================
# CONSTANTS - SINGLE SOURCE OF TRUTH
# ============================================================================

# Required CSV columns mapping
REQUIRED_INTERNAL_COLUMNS = {
    'Timestamp': 'Timestamp (Event Time)',
    'UserID': 'UserID (Person Identifier)',
    'DoorID': 'DoorID (Device Name)',
    'EventType': 'EventType (Access Result)'
}

# Security level definitions
SECURITY_LEVELS = {
    0: {"label": "⬜️ Unclassified", "color": "#2D3748", "value": "unclassified"},
    1: {"label": "🟢 Green (Public)", "color": "#2DBE6C", "value": "green"},
    2: {"label": "🟠 Orange (Semi-Restricted)", "color": "#FFB020", "value": "yellow"},
    3: {"label": "🔴 Red (Restricted)", "color": "#E02020", "value": "red"},
}

# Default icon paths
DEFAULT_ICONS = {
    'upload_default': '/assets/upload_file_csv_icon.png',
    'upload_success': '/assets/upload_file_csv_icon_success.png',
    'upload_fail': '/assets/upload_file_csv_icon_fail.png',
    'main_logo': '/assets/logo_white.png'
}

# File processing limits
FILE_LIMITS = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'max_rows': 1_000_000,
    'allowed_extensions': ['.csv', '.json'],
    'encoding': 'utf-8'
}

# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    port: int = 8050
    host: str = '127.0.0.1'
    suppress_callback_exceptions: bool = True
    assets_folder: str = 'assets'
    
    # Security settings
    secret_key: Optional[str] = None
    csrf_protection: bool = False
    
    # Performance settings
    cache_timeout: int = 3600
    max_workers: int = 4
    
    # Logging settings
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            port=int(os.getenv('PORT', '8050')),
            host=os.getenv('HOST', '127.0.0.1'),
            secret_key=os.getenv('SECRET_KEY'),
            cache_timeout=int(os.getenv('CACHE_TIMEOUT', '3600')),
            max_workers=int(os.getenv('MAX_WORKERS', '4')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE')
        )

@dataclass
class UIConfig:
    """UI configuration and styling"""
    
    # Color palette
    colors: Dict[str, str] = field(default_factory=lambda: {
        'primary': '#1B2A47',
        'accent': '#2196F3',
        'accent_light': '#42A5F5',
        'success': '#2DBE6C',
        'warning': '#FFB020',
        'critical': '#E02020',
        'info': '#2196F3',
        'background': '#0F1419',
        'surface': '#1A2332',
        'border': '#2D3748',
        'text_primary': '#F7FAFC',
        'text_secondary': '#E2E8F0',
        'text_tertiary': '#A0AEC0',
    })
    
    # Animation settings
    animations: Dict[str, str] = field(default_factory=lambda: {
        'fast': '0.15s',
        'normal': '0.3s',
        'slow': '0.5s'
    })

    # Typography
    typography: Dict[str, str] = field(default_factory=lambda: {
        'text_xs': '0.75rem',
        'text_sm': '0.875rem',
        'text_base': '1rem',
        'text_lg': '1.125rem',
        'text_xl': '1.25rem',
        'text_2xl': '1.5rem',
        'text_3xl': '1.875rem',
        'font_light': '300',
        'font_normal': '400',
        'font_medium': '500',
        'font_semibold': '600',
        'font_bold': '700',
    })
    
    # Component visibility
    ui_visibility: Dict[str, Any] = field(default_factory=lambda: {
        'show_upload_section': True,
        'show_mapping_section': True,
        'show_classification_section': True,
        'show_graph_section': True,
        'show_stats_section': True,
        'show_debug_info': False,
        'hide': {'display': 'none'},
        'show_block': {'display': 'block'},
        'show_flex': {'display': 'flex'},
    })

@dataclass
class ProcessingConfig:
    """Data processing configuration"""
    
    # Facility settings
    num_floors: int = 1
    top_n_heuristic_entrances: int = 5
    
    # Event filtering
    primary_positive_indicator: str = "ACCESS GRANTED"
    invalid_phrases_exact: List[str] = field(default_factory=lambda: ["INVALID ACCESS LEVEL"])
    invalid_phrases_contain: List[str] = field(default_factory=lambda: ["NO ENTRY MADE"])
    
    # Cleaning thresholds
    same_door_scan_threshold_seconds: int = 10
    ping_pong_threshold_minutes: int = 1
    
    # Performance limits
    max_processing_time: int = 300  # 5 minutes
    chunk_size: int = 1000000

@dataclass
class Settings:
    """Main settings container"""
    app: AppConfig = field(default_factory=AppConfig.from_env)
    ui: UIConfig = field(default_factory=UIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Direct access to constants
    required_columns: Dict[str, str] = field(default_factory=lambda: REQUIRED_INTERNAL_COLUMNS)
    security_levels: Dict[int, Dict[str, str]] = field(default_factory=lambda: SECURITY_LEVELS)
    default_icons: Dict[str, str] = field(default_factory=lambda: DEFAULT_ICONS)
    file_limits: Dict[str, Any] = field(default_factory=lambda: FILE_LIMITS)

# ============================================================================
# GLOBAL INSTANCE & FUNCTIONS
# ============================================================================

# Global settings instance
settings = Settings()

def get_config() -> AppConfig:
    """Get application configuration (backwards compatibility)"""
    return settings.app

def get_ui_config() -> UIConfig:
    """Get UI configuration"""
    return settings.ui

def get_processing_config() -> ProcessingConfig:
    """Get processing configuration"""
    return settings.processing

def get_settings() -> Settings:
    """Get complete settings"""
    return settings

# Export everything for easy importing
__all__ = [
    'REQUIRED_INTERNAL_COLUMNS',
    'SECURITY_LEVELS', 
    'DEFAULT_ICONS',
    'FILE_LIMITS',
    'AppConfig',
    'UIConfig', 
    'ProcessingConfig',
    'Settings',
    'get_config',
    'get_ui_config',
    'get_processing_config',
    'get_settings',
    'settings'
]

logger.info(
    "🔧 Unified settings loaded: %d required columns",
    len(REQUIRED_INTERNAL_COLUMNS),
)
