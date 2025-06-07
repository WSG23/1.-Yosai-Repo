# utils/input_sanitizer.py
"""
Input sanitization utilities
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
import html
import json
import os
from utils.logging_config import get_logger   # NEW
logger = get_logger(__name__)                # NEW

class InputSanitizer:
    """Sanitize user inputs to prevent injection and other issues"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove/escape HTML
        value = html.escape(value)
        
        # Remove control characters except newlines and tabs
        value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove or replace unsafe characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        
        # Remove multiple consecutive dots
        filename = re.sub(r'\.+', '.', filename)
        
        return filename.strip('._')[:255]  # Limit to 255 chars
    
    @staticmethod
    def sanitize_json_input(json_data: Union[str, Dict, List]) -> Optional[Union[Dict, List]]:
        """Safely parse and sanitize JSON input"""
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                return None
        
        return InputSanitizer._sanitize_json_recursive(json_data)
    
    @staticmethod
    def _sanitize_json_recursive(data: Any, max_depth: int = 10, current_depth: int = 0) -> Any:
        """Recursively sanitize JSON data"""
        if current_depth > max_depth:
            return None
        
        if isinstance(data, dict):
            return {
                InputSanitizer.sanitize_string(str(k)): 
                InputSanitizer._sanitize_json_recursive(v, max_depth, current_depth + 1)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [
                InputSanitizer._sanitize_json_recursive(item, max_depth, current_depth + 1)
                for item in data[:100]  # Limit list size
            ]
        elif isinstance(data, str):
            return InputSanitizer.sanitize_string(data)
        elif isinstance(data, (int, float, bool)) or data is None:
            return data
        else:
            return str(data)
    
    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """Sanitize input to prevent SQL injection"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
            r'(--|#|/\*|\*/)',
            r'(\bUNION\b.*\bSELECT\b)',
            r'(\bOR\b.*=.*)',
            r'(\bAND\b.*=.*)',
            r"('[^']*'|\"[^\"]*\")",  # String literals
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return InputSanitizer.sanitize_string(value)
    
    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """Sanitize and validate email address"""
        if not isinstance(email, str):
            return None
        
        # Basic sanitization
        email = email.strip().lower()
        
        # Basic email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            return email
        else:
            return None
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """Sanitize and validate URL"""
        if not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Only allow http and https protocols
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Remove dangerous characters
        url = re.sub(r'[<>"\']', '', url)
        
        # Basic URL validation
        url_pattern = r'^https?://[a-zA-Z0-9.-]+(/[^\s]*)?$'
        
        if re.match(url_pattern, url):
            return url
        else:
            return None
    
    @staticmethod
    def sanitize_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Optional[int]:
        """Sanitize and validate integer input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except minus sign
                value = re.sub(r'[^\d-]', '', value)
            
            int_value = int(value)
            
            # Apply bounds if specified
            if min_value is not None and int_value < min_value:
                return min_value
            if max_value is not None and int_value > max_value:
                return max_value
            
            return int_value
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[float]:
        """Sanitize and validate float input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point and minus sign
                value = re.sub(r'[^\d.-]', '', value)
            
            float_value = float(value)
            
            # Apply bounds if specified
            if min_value is not None and float_value < min_value:
                return min_value
            if max_value is not None and float_value > max_value:
                return max_value
            
            return float_value
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_boolean(value: Any) -> bool:
        """Sanitize and convert to boolean"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        elif isinstance(value, (int, float)):
            return bool(value)
        else:
            return False
    
    @staticmethod
    def sanitize_list(value: Any, item_sanitizer: Optional[Callable[[Any], Any]] = None, max_items: int = 1000) -> List[Any]:
        """Sanitize list input"""
        if not isinstance(value, (list, tuple)):
            return []
        
        # Limit list size
        value = list(value)[:max_items]
        
        # Apply item sanitizer if provided
        if item_sanitizer:
            value = [item_sanitizer(item) for item in value]
        
        return value
    
    @staticmethod
    def sanitize_dict(value: Any, key_sanitizer: Optional[Callable[[Any], Any]] = None, value_sanitizer: Optional[Callable[[Any], Any]] = None, max_items: int = 1000) -> Dict[str, Any]:
        """Sanitize dictionary input"""
        if not isinstance(value, dict):
            return {}
        
        # Limit dictionary size
        items = list(value.items())[:max_items]
        
        sanitized_dict = {}
        for k, v in items:
            # Sanitize key
            if key_sanitizer:
                k = key_sanitizer(k)
            else:
                k = InputSanitizer.sanitize_string(str(k))
            
            # Sanitize value
            if value_sanitizer:
                v = value_sanitizer(v)
            
            sanitized_dict[k] = v
        
        return sanitized_dict
    
    @staticmethod
    def sanitize_path(path: str, base_path: Optional[str] = None) -> Optional[str]:
        """Sanitize file path to prevent directory traversal"""
        if not isinstance(path, str):
            return None
        
        # Remove dangerous path components
        path = path.replace('..', '').replace('//', '/').replace('\\\\', '\\')
        
        # Remove null bytes
        path = path.replace('\x00', '')
        
        # Normalize path separators
        path = os.path.normpath(path)
        
        # If base path is provided, ensure the path is within it
        if base_path:
            base_path = os.path.abspath(base_path)
            full_path = os.path.abspath(os.path.join(base_path, path))
            
            # Check if the resolved path is within the base path
            if not full_path.startswith(base_path):
                return None
            
            return os.path.relpath(full_path, base_path)
        
        return path
    
    @staticmethod
    def sanitize_csv_value(value: str) -> str:
        """Sanitize CSV cell value"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove or escape dangerous CSV injection patterns
        dangerous_chars = ['=', '+', '-', '@']
        
        # If the value starts with a dangerous character, prepend a space
        if value and value[0] in dangerous_chars:
            value = ' ' + value
        
        # Remove control characters
        value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
        
        # Escape quotes
        value = value.replace('"', '""')
        
        return value
    
    @staticmethod
    def sanitize_regex_input(pattern: str) -> Optional[str]:
        """Sanitize regex pattern to prevent ReDoS attacks"""
        if not isinstance(pattern, str):
            return None
        
        # Check for potentially dangerous regex patterns
        dangerous_patterns = [
            r'\(\?\#',  # Comment groups
            r'\(\?\:.*\*.*\+',  # Nested quantifiers
            r'\(\?\=.*\*.*\+',  # Lookahead with nested quantifiers
            r'\(\?\!.*\*.*\+',  # Negative lookahead with nested quantifiers
        ]
        
        for danger_pattern in dangerous_patterns:
            if re.search(danger_pattern, pattern):
                return None
        
        # Limit pattern length
        if len(pattern) > 1000:
            return None
        
        # Test if the pattern is valid
        try:
            re.compile(pattern)
            return pattern
        except re.error:
            return None

class FormDataSanitizer:
    """Specialized sanitizer for form data"""
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
    
    def sanitize_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all form data"""
        sanitized = {}
        
        for field_name, field_value in form_data.items():
            # Sanitize field name
            clean_field_name = self.sanitizer.sanitize_string(field_name, max_length=100)
            
            # Sanitize field value based on type
            if isinstance(field_value, str):
                sanitized[clean_field_name] = self.sanitizer.sanitize_string(field_value)
            elif isinstance(field_value, list):
                sanitized[clean_field_name] = self.sanitizer.sanitize_list(
                    field_value, 
                    lambda x: self.sanitizer.sanitize_string(str(x))
                )
            elif isinstance(field_value, dict):
                sanitized[clean_field_name] = self.sanitizer.sanitize_dict(field_value)
            else:
                sanitized[clean_field_name] = self.sanitizer.sanitize_string(str(field_value))
        
        return sanitized
    
    def sanitize_file_upload(self, filename: str, content: bytes, max_size: int = 10 * 1024 * 1024) -> Dict[str, Any]:
        """Sanitize file upload data"""
        # Sanitize filename
        clean_filename = self.sanitizer.sanitize_filename(filename)
        
        # Check file size
        if len(content) > max_size:
            return {
                'valid': False,
                'error': f'File too large (max {max_size} bytes)'
            }
        
        # Check for null bytes in content (potential security issue)
        if b'\x00' in content:
            return {
                'valid': False,
                'error': 'File contains null bytes'
            }
        
        return {
            'valid': True,
            'filename': clean_filename,
            'content': content,
            'size': len(content)
        }

# Convenience functions
def sanitize_user_input(value: Any, input_type: str = 'string', **kwargs) -> Any:
    """Convenience function to sanitize user input based on type"""
    sanitizer = InputSanitizer()
    
    if input_type == 'string':
        return sanitizer.sanitize_string(str(value), **kwargs)
    elif input_type == 'integer':
        return sanitizer.sanitize_integer(value, **kwargs)
    elif input_type == 'float':
        return sanitizer.sanitize_float(value, **kwargs)
    elif input_type == 'boolean':
        return sanitizer.sanitize_boolean(value)
    elif input_type == 'email':
        return sanitizer.sanitize_email(str(value))
    elif input_type == 'url':
        return sanitizer.sanitize_url(str(value))
    elif input_type == 'filename':
        return sanitizer.sanitize_filename(str(value))
    elif input_type == 'json':
        return sanitizer.sanitize_json_input(value)
    else:
        return sanitizer.sanitize_string(str(value))

def create_form_sanitizer() -> FormDataSanitizer:
    """Factory function to create form data sanitizer"""
    return FormDataSanitizer()

# Example usage and testing
def test_sanitizers():
    """Test various sanitizer functions"""
    sanitizer = InputSanitizer()
    
    # Test string sanitization
    test_string = "<script>alert('xss')</script>Hello World!"
    logger.info("Original:", test_string)
    logger.info("Sanitized:", sanitizer.sanitize_string(test_string))
    
    # Test filename sanitization
    test_filename = "../../../etc/passwd.txt"
    logger.info("Original filename:", test_filename)
    logger.info("Sanitized filename:", sanitizer.sanitize_filename(test_filename))
    
    # Test email sanitization
    test_email = "  USER@EXAMPLE.COM  "
    logger.info("Original email:", test_email)
    logger.info("Sanitized email:", sanitizer.sanitize_email(test_email))
        
    logger.info("✅ Sanitizer tests completed")

if __name__ == "__main__":
    test_sanitizers()