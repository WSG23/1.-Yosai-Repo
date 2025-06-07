# shared/utils.py - Fixed Version
"""
General utility functions with proper type annotations
"""

import json
import re
from typing import Any, Optional, Union
from datetime import datetime
import hashlib

def format_file_size(size_bytes: Union[int, float]) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)  # Convert to float explicitly
    
    while size_float >= 1024.0 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1
    
    return f"{size_float:.1f} {size_names[i]}"

def safe_json_loads(json_string: Optional[str], default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    if not json_string:
        return default
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove multiple consecutive dots
    filename = re.sub(r'\.+', '.', filename)
    return filename.strip('._')

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()

def generate_session_id() -> str:
    """Generate a unique session ID"""
    timestamp = str(datetime.utcnow().timestamp())
    return hashlib.md5(timestamp.encode()).hexdigest()[:12]

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def validate_timestamp_format(timestamp_str: str) -> bool:
    """Validate timestamp string format"""
    common_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in common_formats:
        try:
            datetime.strptime(timestamp_str, fmt)
            return True
        except ValueError:
            continue
    
    return False

def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Safely convert value to integer with fallback"""
    try:
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            return int(float(value))  # Handle string numbers with decimals
        else:
            return default
    except (ValueError, TypeError):
        return default

def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with fallback"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_whitespace(text: str) -> str:
    """Clean excessive whitespace from text"""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

def parse_boolean(value: Any) -> bool:
    """Parse various boolean representations"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    if isinstance(value, (int, float)):
        return bool(value)
    return False