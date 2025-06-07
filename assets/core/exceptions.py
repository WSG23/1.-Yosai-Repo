# shared/exceptions.py
"""
Custom exceptions for the application
"""

class YosaiError(Exception):
    """Base exception for Yōsai application"""
    pass

class DataProcessingError(YosaiError):
    """Raised when data processing fails"""
    pass

class ValidationError(YosaiError):
    """Raised when validation fails"""
    pass

class ConfigurationError(YosaiError):
    """Raised when configuration is invalid"""
    pass

class FileProcessingError(YosaiError):
    """Raised when file processing fails"""
    pass

class SecurityModelError(YosaiError):
    """Raised when security model generation fails"""
    pass
