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
                    allowed_mimes = ['text/csv', 'text/plain', 'application/csv']
                    if detected_mime not in allowed_mimes:
                        warning_msg = f"Detected MIME type: {detected_mime}. Expected CSV format."
                        result['warnings'].append(warning_msg)
                        logger.info(f"MIME type warning: {warning_msg}")
                except Exception as e:
                    warning_msg = f"Could not detect MIME type: {str(e)}"
                    result['warnings'].append(warning_msg)
                    logger.warning(warning_msg)
            
            # 4. Content structure validation
            csv_validation = self._validate_csv_structure(file_content)
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
    
    def _validate_csv_structure(self, file_content: bytes) -> Dict[str, Any]:
        """Validate CSV file structure"""
        temp_file_path = None
        
        try:
            # Create temporary file for pandas
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
                tmp_file.write(file_content)
                temp_file_path = tmp_file.name
            
            try:
                # Read CSV with limited preview (first 1000 rows)
                df_preview = pd.read_csv(temp_file_path, nrows=1000, dtype=str)
                
                # Basic structure checks
                if df_preview.empty:
                    return {'valid': False, 'errors': ['CSV file is empty']}
                
                if len(df_preview.columns) == 0:
                    return {'valid': False, 'errors': ['CSV has no columns']}
                
                # Estimate total rows
                estimated_rows = self._estimate_csv_rows(temp_file_path)
                if estimated_rows > self.max_rows:
                    return {
                        'valid': False, 
                        'errors': [f'Too many rows: ~{estimated_rows:,} (max: {self.max_rows:,})']
                    }
                
                return {
                    'valid': True,
                    'row_count': estimated_rows,
                    'column_count': len(df_preview.columns)
                }
                
            except Exception as e:
                logger.error(f"CSV parsing error: {str(e)}")
                return {'valid': False, 'errors': [f'CSV parsing error: {str(e)}']}
                
        except Exception as e:
            logger.error(f"File handling error: {str(e)}")
            return {'valid': False, 'errors': [f'File handling error: {str(e)}']}
            
        finally:
            # Clean up temp file
            if temp_file_path:
                try:
                    os.unlink(temp_file_path)
                except OSError as e:
                    logger.warning(f"Could not delete temp file {temp_file_path}: {str(e)}")
    
    def _estimate_csv_rows(self, file_path: str) -> int:
        """Estimate number of rows in CSV file"""
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
            
            # Check for suspicious patterns
            malicious_patterns = [
                r'<script[^>]*>',  # JavaScript
                r'javascript:',     # JavaScript URLs
                r'vbscript:',      # VBScript
                r'onload=',        # Event handlers
                r'onerror=',
                r'eval\(',         # Code execution
                r'exec\(',
                r'import\s+os',    # Python OS imports
                r'subprocess',
                r'__import__',
                r'<\?php',         # PHP tags
                r'<%.*%>',         # ASP/JSP tags
            ]
            
            for pattern in malicious_patterns:
                try:
                    if re.search(pattern, content_str, re.IGNORECASE):
                        threats.append(f"Suspicious pattern detected: {pattern}")
                except re.error as e:
                    logger.warning(f"Regex error checking pattern {pattern}: {str(e)}")
            
            # Check for excessive special characters (potential binary data)
            if len(content_str) > 0:
                special_char_count = sum(1 for c in content_str if ord(c) < 32 and c not in '\r\n\t')
                special_char_ratio = special_char_count / len(content_str)
                if special_char_ratio > 0.1:  # More than 10% special characters
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

# Export for easier importing
__all__ = ['SecureFileValidator', 'SecurityError']