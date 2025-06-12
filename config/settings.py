# config/settings.py
"""
Unified Configuration - SINGLE SOURCE OF TRUTH
Replaces all other config files
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import os
import re
import socket
from pathlib import Path
import warnings
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

# Security configuration for file uploads
SECURITY_CONFIG = {
    'enable_file_validation': True,
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': {'.csv', '.txt', '.json'},
    'allowed_mime_types': {
        'text/csv',
        'text/plain',
        'application/csv',
        'application/json',
        'text/json',
    },

    'enable_content_scanning': True,
    'log_security_events': True
}

# File processing limits
FILE_LIMITS = {
    'max_file_size': SECURITY_CONFIG['max_file_size'],
    'max_rows': 1_000_000,
    'allowed_extensions': SECURITY_CONFIG['allowed_extensions']
}

# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_port(port_str: str, default: int = 8050) -> int:
    """Validate port number from environment variable."""
    try:
        port = int(port_str)
        if not 1024 <= port <= 65535:
            raise ValueError(f"Port {port} out of valid range (1024-65535)")
        return port
    except (ValueError, TypeError) as e:
        if port_str:
            warnings.warn(
                f"Invalid port '{port_str}': {e}. Using default {default}"
            )
        return default


def validate_host(host_str: str, default: str = "127.0.0.1") -> str:
    """Validate host address from environment variable."""
    if not host_str:
        return default

    valid_patterns = [
        r"^localhost$",
        r"^127\.0\.0\.1$",
        r"^0\.0\.0\.0$",
        r"^(\d{1,3}\.){3}\d{1,3}$",
        r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
    ]

    for pattern in valid_patterns:
        if re.match(pattern, host_str):
            if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", host_str):
                try:
                    parts = host_str.split(".")
                    if all(0 <= int(part) <= 255 for part in parts):
                        return host_str
                    warnings.warn(
                        f"Invalid IP address '{host_str}'. Using default {default}"
                    )
                    return default
                except ValueError:
                    warnings.warn(
                        f"Invalid IP address format '{host_str}'. Using default {default}"
                    )
                    return default
            return host_str

    warnings.warn(f"Invalid host format '{host_str}'. Using default {default}")
    return default


def validate_log_level(level_str: str, default: str = "INFO") -> str:
    """Validate logging level from environment variable."""
    if not level_str:
        return default

    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    level_upper = level_str.upper()

    if level_upper in valid_levels:
        return level_upper

    warnings.warn(
        f"Invalid log level '{level_str}'. Valid options: {', '.join(valid_levels)}. Using default {default}"
    )
    return default


def validate_positive_int(
    value_str: str,
    name: str,
    default: int,
    min_val: int = 1,
    max_val: int | None = None,
) -> int:
    """Validate positive integer from environment variable."""
    if not value_str:
        return default

    try:
        value = int(value_str)
        if value < min_val:
            raise ValueError(f"{name} must be at least {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{name} must not exceed {max_val}")
        return value
    except (ValueError, TypeError) as e:
        warnings.warn(
            f"Invalid {name} '{value_str}': {e}. Using default {default}"
        )
        return default


def validate_file_path(
    path_str: str,
    default: str | None = None,
    create_dirs: bool = True,
) -> str | None:
    """Validate file path from environment variable."""
    if not path_str:
        return default

    try:
        path = Path(path_str)

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        elif not path.parent.exists():
            warnings.warn(
                f"Parent directory for log file '{path_str}' does not exist. Using default {default}"
            )
            return default

        if not os.access(path.parent, os.W_OK):
            warnings.warn(
                f"Cannot write to directory '{path.parent}'. Using default {default}"
            )
            return default

        return str(path)

    except Exception as e:
        warnings.warn(f"Invalid file path '{path_str}': {e}. Using default {default}")
        return default


def validate_boolean(value_str: str, default: bool = False) -> bool:
    """Validate boolean from environment variable."""
    if not value_str:
        return default

    true_values = {"true", "1", "yes", "on", "enabled"}
    false_values = {"false", "0", "no", "off", "disabled"}

    value_lower = value_str.lower().strip()

    if value_lower in true_values:
        return True
    if value_lower in false_values:
        return False

    warnings.warn(f"Invalid boolean value '{value_str}'. Using default {default}")
    return default


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
        """Create configuration from environment variables with validation."""

        try:
            debug = validate_boolean(os.getenv("DEBUG", ""), default=False)
            port = validate_port(os.getenv("PORT", "8050"), default=8050)
            host = validate_host(os.getenv("HOST", ""), default="127.0.0.1")
            secret_key = os.getenv("SECRET_KEY")
            csrf_protection = validate_boolean(
                os.getenv("CSRF_PROTECTION", ""), default=False
            )
            cache_timeout = validate_positive_int(
                os.getenv("CACHE_TIMEOUT", "3600"),
                "CACHE_TIMEOUT",
                default=3600,
                min_val=60,
                max_val=86400,
            )
            max_workers = validate_positive_int(
                os.getenv("MAX_WORKERS", "4"),
                "MAX_WORKERS",
                default=4,
                min_val=1,
                max_val=32,
            )
            log_level = validate_log_level(os.getenv("LOG_LEVEL", ""), default="INFO")
            log_file = validate_file_path(os.getenv("LOG_FILE", ""), default=None)
            suppress_callback_exceptions = validate_boolean(
                os.getenv("SUPPRESS_CALLBACK_EXCEPTIONS", "true"), default=True
            )

            assets_folder = os.getenv("ASSETS_FOLDER", "assets")
            if not assets_folder or not assets_folder.replace("_", "").replace("-", "").isalnum():
                warnings.warn(
                    f"Invalid assets folder '{assets_folder}'. Using default 'assets'"
                )
                assets_folder = "assets"

            logger.info("✅ Environment configuration loaded successfully")
            if debug:
                logger.debug(
                    f"Configuration: debug={debug}, port={port}, host={host}, log_level={log_level}"
                )

            return cls(
                debug=debug,
                port=port,
                host=host,
                suppress_callback_exceptions=suppress_callback_exceptions,
                assets_folder=assets_folder,
                secret_key=secret_key,
                csrf_protection=csrf_protection,
                cache_timeout=cache_timeout,
                max_workers=max_workers,
                log_level=log_level,
                log_file=log_file,
            )

        except Exception as e:
            logger.error(f"❌ Failed to load environment configuration: {e}")
            logger.info("🔄 Falling back to default configuration")
            return cls()

    def validate_runtime_config(self) -> Dict[str, Any]:
        """Validate configuration at runtime and return a status report."""
        issues: List[str] = []
        warnings_list: List[str] = []

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            if result == 0:
                warnings_list.append(f"Port {self.port} is already in use")
        except Exception as e:
            warnings_list.append(f"Could not test port availability: {e}")

        if not os.path.exists(self.assets_folder):
            issues.append(f"Assets folder '{self.assets_folder}' does not exist")

        if self.log_file:
            try:
                log_path = Path(self.log_file)
                if not log_path.parent.exists():
                    issues.append(
                        f"Log file directory '{log_path.parent}' does not exist"
                    )
                elif not os.access(log_path.parent, os.W_OK):
                    issues.append(
                        f"Cannot write to log directory '{log_path.parent}'"
                    )
            except Exception as e:
                issues.append(f"Invalid log file path: {e}")

        if not self.debug and not self.secret_key:
            warnings_list.append("No SECRET_KEY set in production mode")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings_list,
            "config_summary": {
                "debug": self.debug,
                "port": self.port,
                "host": self.host,
                "log_level": self.log_level,
                "max_workers": self.max_workers,
            },
        }

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


def get_environment_variable_docs() -> str:
    """Return documentation string for supported environment variables."""
    return """
Environment Variables Documentation
==================================

Required Variables:
  None - all variables have sensible defaults

Optional Variables:
  DEBUG                    - Enable debug mode (true/false, default: false)
  PORT                     - Server port (1024-65535, default: 8050)
  HOST                     - Server host (IP or hostname, default: 127.0.0.1)
  SECRET_KEY               - Secret key for security (string, recommended for production)

  CACHE_TIMEOUT            - Cache timeout in seconds (60-86400, default: 3600)
  MAX_WORKERS              - Maximum worker threads (1-32, default: 4)

  LOG_LEVEL                - Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL, default: INFO)
  LOG_FILE                 - Log file path (string, default: console only)

  SUPPRESS_CALLBACK_EXCEPTIONS - Suppress Dash callback exceptions (true/false, default: true)
  ASSETS_FOLDER            - Assets directory name (string, default: assets)
  CSRF_PROTECTION          - Enable CSRF protection (true/false, default: false)

Example Usage:
  export DEBUG=true
  export PORT=8080
  export LOG_LEVEL=DEBUG
  export SECRET_KEY=your-secret-key-here
  export LOG_FILE=/var/log/yosai/app.log

  python app.py
"""


def test_environment_configuration() -> None:
    """Test environment variable validation."""
    print("\U0001F9EA Testing Environment Variable Validation")
    print("=" * 50)

    test_cases = [
        ("DEBUG", "true", True),
        ("DEBUG", "false", False),
        ("DEBUG", "invalid", False),
        ("PORT", "8080", 8080),
        ("PORT", "80", 8050),
        ("PORT", "99999", 8050),
        ("PORT", "invalid", 8050),
        ("LOG_LEVEL", "DEBUG", "DEBUG"),
        ("LOG_LEVEL", "invalid", "INFO"),
        ("MAX_WORKERS", "8", 8),
        ("MAX_WORKERS", "0", 4),
        ("MAX_WORKERS", "100", 4),
    ]

    original_env = dict(os.environ)

    try:
        for var_name, test_value, expected in test_cases:
            os.environ[var_name] = test_value
            config = AppConfig.from_env()
            actual = getattr(config, var_name.lower())
            status = "\u2705" if actual == expected else "\u274C"
            print(f"{status} {var_name}='{test_value}' -> {actual} (expected: {expected})")
            if var_name in os.environ:
                del os.environ[var_name]

        print("\n\uD83C\uDF20 Testing runtime validation...")
        config = AppConfig.from_env()
        validation_report = config.validate_runtime_config()
        print(f"Configuration valid: {validation_report['valid']}")
        if validation_report['issues']:
            print("Issues found:")
            for issue in validation_report['issues']:
                print(f"  \u274C {issue}")

        if validation_report['warnings']:
            print("Warnings:")
            for warning in validation_report['warnings']:
                print(f"  \u26A0\uFE0F {warning}")
    finally:
        os.environ.clear()
        os.environ.update(original_env)

    print("\n\u2705 Environment validation testing complete")

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
    'settings',
    'get_environment_variable_docs',
    'test_environment_configuration'
]

logger.info(
    "🔧 Unified settings loaded: %d required columns",
    len(REQUIRED_INTERNAL_COLUMNS),
)
