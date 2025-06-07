# config/security_config.py
"""
Security configuration and monitoring - FIXED TYPE ANNOTATIONS
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import os

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    
    # File upload security
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_mime_types: List[str] = field(default_factory=lambda: [
        'text/csv', 'text/plain', 'application/csv'
    ])
    
    # Rate limiting
    upload_rate_limit: int = 10  # uploads per minute per IP
    processing_timeout: int = 300  # 5 minutes
    
    # Security monitoring
    enable_security_logging: bool = True
    alert_on_suspicious_patterns: bool = True
    quarantine_suspicious_files: bool = True
    
    # Content security
    max_pattern_checks: int = 1000  # Limit regex checks for performance
    suspicious_threshold: float = 0.1  # 10% suspicious content triggers alert
    
    # Audit settings
    log_all_uploads: bool = True
    log_file_hashes: bool = True
    retain_security_logs_days: int = 90

# Create global config instance
def get_security_config() -> SecurityConfig:
    """Get security configuration instance"""
    return SecurityConfig()

# Export for easy importing
__all__ = ['SecurityConfig', 'get_security_config']