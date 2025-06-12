# utils/secure_validator.py
"""
Secure file validation for uploads - CLEANED UP VERSION
"""

import pandas as pd
import hashlib
import tempfile
import os
from typing import Dict, List, Optional, Any
import re
import logging

from config.settings import FILE_LIMITS

# Initialize logger at module level
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Security-related validation error"""
    pass

class SecureFileValidator:
    """Secure file validation with comprehensive checks"""
    
    def __init__(self):
        self.max_file_size = FILE_LIMITS['max_file_size']
        self.max_rows = FILE_LIMITS['max_rows']
        self.allowed_extensions = FILE_LIMITS['allowed_extensions']
        
        # Try to import python-magic, fallback if not available
        try:
            import magic
            self.magic = magic.Magic(mime=True)
            self.magic_available = True
            logger.info("python-magic available - MIME type detection enabled")
        except ImportError:
            self.magic = None
            self.magic_available = False
            logger.warning("python-magic not available. MIME type detection disabled.")
    
    def validate_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Comprehensive file validation
        Returns validation result with details
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'file_info': {}
        }
        
        try:
            logger.info(f"Starting security validation for: {filename}")
            
            # 1. File size validation
            if len(file_content) > self.max_file_size:
                error_msg = (f"File too large: {len(file_content):,} bytes "
                           f"(max: {self.max_file_size:,})")
                result['errors'].append(error_msg)
                logger.warning(f"File size validation failed: {error_msg}")
                return result
            
            # 2. Extension validation
            if not any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                error_msg = f"Invalid file extension. Allowed: {', '.join(self.allowed_extensions)}"
                result['errors'].append(error_msg)
                logger.warning(f"Extension validation failed: {error_msg}")
                return result
            
            # 3. MIME type validation (if python-magic is available)
            if self.magic_available and self.magic is not None:
                try:
                    detected_mime = self.magic.from_buffer(file_content)
                    allowed_mimes = [
                        'text/csv', 'text/plain', 'application/csv',
                        'application/json', 'text/json'
                    ]
                    if detected_mime not in allowed_mimes:
                        warning_msg = (
                            f"Detected MIME type: {detected_mime}. Expected CSV or JSON format."
                        )
                        result['warnings'].append(warning_msg)
                        logger.info(f"MIME type warning: {warning_msg}")
                except Exception as e:
                    warning_msg = f"Could not detect MIME type: {str(e)}"
                    result['warnings'].append(warning_msg)
                    logger.warning(warning_msg)

            # 4. Content structure validation
            csv_validation = self._validate_file_structure(file_content, filename)
            if not csv_validation['valid']:
                result['errors'].extend(csv_validation['errors'])
                logger.warning(f"CSV structure validation failed: {csv_validation['errors']}")
                return result
            
            # 5. Malicious pattern detection
            malware_check = self._check_malicious_patterns(file_content)
            if not malware_check['safe']:
                result['errors'].extend(malware_check['threats'])
                logger.warning(f"Malicious patterns detected: {malware_check['threats']}")
                return result
            
            # Success
            result['valid'] = True
            result['file_info'] = {
                'size_bytes': len(file_content),
                'row_count': csv_validation.get('row_count', 0),
                'column_count': csv_validation.get('column_count', 0),
                'file_hash': hashlib.sha256(file_content).hexdigest()[:16]
            }
            
            logger.info(f"Security validation passed for: {filename}")
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(f"Security validation error for {filename}: {str(e)}")
            result['errors'].append(error_msg)
        
        return result
    
    def _validate_file_structure(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate CSV or JSON file structure based on extension"""
        temp_file_path = None
        is_json = filename.lower().endswith('.json')

        try:
            # Create temporary file for pandas
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
                tmp_file.write(file_content)
                temp_file_path = tmp_file.name

            try:
                if is_json:
                    # Validate JSON structure first
                    json_validation = self._validate_json_structure(file_content)
                    if not json_validation['valid']:
                        return json_validation

                    df_preview = pd.read_json(temp_file_path, dtype=str)
                else:
                    # Read CSV with limited preview (first 1000 rows)
                    df_preview = pd.read_csv(temp_file_path, nrows=1000, dtype=str)

                # Common validation for both formats
                if df_preview.empty:
                    return {
                        'valid': False,
                        'errors': [f"{filename} contains no data rows"]
                    }

                if len(df_preview.columns) == 0:
                    return {
                        'valid': False,
                        'errors': [f"{filename} contains no columns"]
                    }

                if len(df_preview.columns) > 1000:
                    return {
                        'valid': False,
                        'errors': [f"{filename} has too many columns (>1000)"]
                    }

                return {
                    'valid': True,
                    'row_count': len(df_preview),
                    'column_count': len(df_preview.columns),
                    'column_names': df_preview.columns.tolist()[:10]
                }

            except Exception as e:
                return {
                    'valid': False,
                    'errors': [f"Failed to parse {filename}: {str(e)}"]
                }

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

    def _validate_json_structure(self, file_content: bytes) -> Dict[str, Any]:
        """Validate JSON file structure and content"""
        import json

        try:
            # First check if it's valid JSON
            decoded_string = file_content.decode('utf-8')
            json_data = json.loads(decoded_string)

            # Check if it's an array of objects (table-like structure)
            if isinstance(json_data, list):
                if not json_data:
                    return {
                        'valid': False,
                        'errors': ['JSON array is empty']
                    }

                if not all(isinstance(item, dict) for item in json_data):
                    return {
                        'valid': False,
                        'errors': ['JSON array contains non-object elements']
                    }

                if len(json_data) > 1:
                    first_keys = set(json_data[0].keys())
                    for i, item in enumerate(json_data[1:], 1):
                        if set(item.keys()) != first_keys:
                            return {
                                'valid': False,
                                'errors': [f'Inconsistent schema at row {i+1}']
                            }

            elif isinstance(json_data, dict):
                # Single object - convert to list for consistency
                pass
            else:
                return {
                    'valid': False,
                    'errors': ['JSON must contain an array of objects or a single object']
                }

            return {'valid': True}

        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'errors': [f'Invalid JSON format: {str(e)}']
            }
        except UnicodeDecodeError:
            return {
                'valid': False,
                'errors': ['JSON file contains invalid UTF-8 characters']
            }
    
    def _estimate_csv_rows(self, file_path: str) -> int:
        """Estimate number of rows in a text-based file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Count lines in first chunk
                chunk_size = 1024 * 1024  # 1MB
                chunk = f.read(chunk_size)
                lines_in_chunk = chunk.count('\n')
                
                # Get file size
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()
                
                if file_size <= chunk_size:
                    return max(lines_in_chunk - 1, 0)  # Subtract header
                
                # Estimate based on proportion
                estimated_lines = int((lines_in_chunk / chunk_size) * file_size)
                return max(estimated_lines - 1, 0)  # Subtract header
                
        except Exception as e:
            logger.warning(f"Could not estimate CSV rows: {str(e)}")
            return 0
    
    def _check_malicious_patterns(self, file_content: bytes) -> Dict[str, Any]:
        """Check for malicious patterns in file content"""
        threats = []
        
        try:
            # Convert to string for pattern matching
            content_str = file_content.decode('utf-8', errors='ignore')

            # Existing patterns + JSON-specific ones
            malicious_patterns = [
                r'<script[^>]*>',
                r'javascript:',
                r'vbscript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'eval\s*\(',
                r'setTimeout\s*\(',
                r'setInterval\s*\(',
                r'document\.cookie',
                r'document\.write',
                r'window\.location',
                r'\.\.\/.*\.\./',
                r'__import__\s*\(',
                r'exec\s*\(',
                r'system\s*\(',
                r'shell_exec\s*\(',
                r'<%.*%>',
                r'"__proto__"\s*:',
                r'"constructor"\s*:',
                r'"\$where"\s*:',
                r'"\$regex"\s*:',
                r'"eval"\s*:'
            ]
            
            for pattern in malicious_patterns:
                try:
                    if re.search(pattern, content_str, re.IGNORECASE):
                        threats.append(f"Suspicious pattern detected: {pattern}")
                except re.error as e:
                    logger.warning(f"Regex error checking pattern {pattern}: {str(e)}")
            
            # Check for excessive nesting in JSON (potential DoS)
            if content_str.strip().startswith('{') or content_str.strip().startswith('['):
                nesting_level = self._check_json_nesting_depth(content_str)
                if nesting_level > 10:
                    threats.append(f"Excessive JSON nesting detected: {nesting_level} levels")

            if len(content_str) > 0:
                special_char_count = sum(1 for c in content_str if ord(c) < 32 and c not in '\r\n\t')
                special_char_ratio = special_char_count / len(content_str)
                if special_char_ratio > 0.1:
                    threats.append("High ratio of special characters detected")
            
        except UnicodeDecodeError:
            threats.append("File contains invalid UTF-8 characters")
        except Exception as e:
            logger.error(f"Error checking malicious patterns: {str(e)}")
            threats.append(f"Pattern checking failed: {str(e)}")
        
        return {
            'safe': len(threats) == 0,
            'threats': threats
        }

    def _check_json_nesting_depth(self, json_str: str) -> int:
        """Check JSON nesting depth to prevent DoS attacks"""
        max_depth = 0
        current_depth = 0

        for char in json_str:
            if char in '{[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '}]':
                current_depth = max(0, current_depth - 1)

        return max_depth

# Export for easier importing
__all__ = ['SecureFileValidator', 'SecurityError']

# Convenience wrapper used by upload handlers
_validator_instance = SecureFileValidator()

def validate_upload_security(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Validate uploaded file content and return simplified result."""
    result = _validator_instance.validate_upload(file_content, filename)
    return {
        'is_valid': result.get('valid', False),
        'errors': result.get('errors', []),
        'warnings': result.get('warnings', []),
        'file_info': result.get('file_info', {})
    }
