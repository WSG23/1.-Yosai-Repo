# utils/logging_config.py - FIXED VERSION - Simple and Reliable

"""
Simple logging configuration that works without external dependencies
"""

import logging
import sys
import os
from datetime import datetime

# ============================================================================
# SIMPLE LOGGER SETUP
# ============================================================================

def setup_application_logging(log_level='INFO', log_file=None):
    """
    Set up application logging with simple configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            root_logger.addHandler(file_handler)
            
            print(f"📝 Logging to file: {log_file}")
            
        except Exception as e:
            print(f"⚠️ Could not set up file logging: {e}")
    
    print(f"📊 Logging configured - Level: {log_level}")

def get_logger(name=None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = __name__
    
    logger = logging.getLogger(name)
    
    # If no handlers are set up, create a simple console logger
    if not logger.handlers and not logging.getLogger().handlers:
        setup_simple_console_logging()
    
    return logger

def setup_simple_console_logging():
    """Set up basic console logging as fallback"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout
    )

# ============================================================================
# SIMPLE LOGGER CLASS (FALLBACK)
# ============================================================================

class SimpleLogger:
    """
    Simple logger class for when logging module isn't working
    """
    
    def __init__(self, name="app"):
        self.name = name
        self.enabled = True
    
    def _log(self, level, message):
        if self.enabled:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"{timestamp} - {level} - {self.name} - {message}")
    
    def info(self, message):
        self._log("INFO", message)
    
    def debug(self, message):
        self._log("DEBUG", message)
    
    def warning(self, message):
        self._log("WARNING", message)
    
    def error(self, message):
        self._log("ERROR", message)
    
    def critical(self, message):
        self._log("CRITICAL", message)

# ============================================================================
# SAFE LOGGER FACTORY
# ============================================================================

def get_safe_logger(name=None):
    """
    Get a logger that always works, even if logging is broken
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance or SimpleLogger fallback
    """
    try:
        return get_logger(name)
    except Exception:
        return SimpleLogger(name or "app")

# ============================================================================
# INITIALIZATION
# ============================================================================

# Set up basic logging on import
try:
    # Try to set up proper logging
    setup_application_logging()
except Exception as e:
    # Fall back to basic logging
    print(f"⚠️ Logging setup failed: {e}")
    try:
        setup_simple_console_logging()
    except Exception:
        print("⚠️ Even basic logging failed - using print statements")

# Create default logger
logger = get_safe_logger(__name__)
logger.info("✅ Logging configuration loaded")

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'setup_application_logging',
    'get_logger',
    'get_safe_logger',
    'SimpleLogger'
]