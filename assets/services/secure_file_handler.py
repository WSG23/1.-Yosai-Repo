# data_io/secure_file_handler.py
"""
Secure file handling with comprehensive validation
"""

import base64
import io
from typing import Dict, Tuple, Optional, Any
import mimetypes
import hashlib
import logging

from core.exceptions import FileProcessingError, ValidationError
from utils.validators import CSVValidator
from utils.error_handler import error_boundary
from utils.input_sanitizer import InputSanitizer
from config.settings import FILE_LIMITS

logger = logging.getLogger(__name__)

class SecureFileHandler:
    """Secure file handler with validation and sanitization"""
    
    def __init__(self):
        self.csv_validator = CSVValidator()
        self.sanitizer = InputSanitizer()
    
    @error_boundary(
        fallback_value={'success': False, 'error': 'File processing failed'},
        error_message="File processing failed"
    )
    def process_uploaded_file(
        self, 
        contents: str, 
        filename: str,
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded file with comprehensive security checks
        
        Args:
            contents: Base64 encoded file contents
            filename: Original filename
            max_size: Maximum allowed file size (bytes)
            
        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Processing uploaded file: {filename}")
            
            # Step 1: Validate and sanitize filename
            clean_filename = self._validate_and_clean_filename(filename)
            
            # Step 2: Decode and validate file contents
            decoded_contents, file_size = self._decode_and_validate_contents(contents, max_size)
            
            # Step 3: Validate file type and structure
            self._validate_file_type_and_structure(clean_filename, decoded_contents, file_size)
            
            # Step 4: Create StringIO object for processing
            file_io = io.StringIO(decoded_contents)
            
            # Step 5: Generate file hash for integrity
            file_hash = self._generate_file_hash(decoded_contents)
            
            logger.info(f"Successfully processed file: {clean_filename} ({file_size:,} bytes)")
            
            return {
                'success': True,
                'filename': clean_filename,
                'file_io': file_io,
                'file_size': file_size,
                'file_hash': file_hash,
                'contents': contents  # Keep original for storage
            }
            
        except (ValidationError, FileProcessingError) as e:
            logger.error(f"File processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'validation_error'
            }
        except Exception as e:
            logger.error(f"Unexpected file processing error: {str(e)}")
            return {
                'success': False,
                'error': 'File processing failed due to unexpected error',
                'error_type': 'system_error'
            }
    
    def _validate_and_clean_filename(self, filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise ValidationError("Filename is required")
        
        # Sanitize filename
        clean_filename = self.sanitizer.sanitize_filename(filename)
        
        if not clean_filename:
            raise ValidationError("Invalid filename")
        
        # Validate file extension
        self.csv_validator.validate_file_extension(clean_filename)
        
        return clean_filename
    
    def _decode_and_validate_contents(self, contents: str, max_size: Optional[int] = None) -> Tuple[str, int]:
        """Decode base64 contents and validate size"""
        try:
            # Split content type and data
            if ',' not in contents:
                raise ValidationError("Invalid file format")
            
            content_type, content_string = contents.split(',', 1)
            
            # Decode base64
            try:
                decoded_bytes = base64.b64decode(content_string)
            except Exception:
                raise ValidationError("Invalid file encoding")
            
            # Check file size
            file_size = len(decoded_bytes)
            max_allowed = max_size or FILE_LIMITS['max_file_size']
            
            if file_size > max_allowed:
                raise ValidationError(
                    f"File size ({file_size:,} bytes) exceeds maximum allowed size ({max_allowed:,} bytes)"
                )
            
            # Try to decode as text with multiple encodings
            decoded_text = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    decoded_text = decoded_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded_text is None:
                raise ValidationError("Could not decode file with any supported encoding")
            
            return decoded_text, file_size
            
        except ValidationError:
            raise
        except Exception as e:
            raise FileProcessingError(f"Failed to decode file contents: {str(e)}")
    
    def _validate_file_type_and_structure(self, filename: str, contents: str, file_size: int) -> None:
        """Validate file type and basic structure"""
        # MIME type validation
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and not mime_type.startswith('text/'):
            logger.warning(f"Unexpected MIME type for CSV: {mime_type}")
        
        # Basic CSV structure validation
        lines = contents.split('\n')
        if len(lines) < 2:
            raise ValidationError("CSV file must have at least a header and one data row")
        
        # Check for common CSV patterns
        first_line = lines[0].strip()
        if not first_line:
            raise ValidationError("CSV file appears to be empty")
        
        # Basic delimiter detection
        common_delimiters = [',', ';', '\t', '|']
        delimiter_counts = {delim: first_line.count(delim) for delim in common_delimiters}
        max_delimiter = max(delimiter_counts.values())
        
        if max_delimiter == 0:
            raise ValidationError("No common CSV delimiters found in header row")
        
        logger.info(f"File validation passed. Detected {len(lines)} lines, likely delimiter has {max_delimiter} occurrences")
    
    def _generate_file_hash(self, contents: str) -> str:
        """Generate SHA-256 hash of file contents for integrity checking"""
        return hashlib.sha256(contents.encode('utf-8')).hexdigest()

def decode_uploaded_csv(contents_b64: str) -> io.StringIO:
    """
    Legacy function for backward compatibility
    Enhanced with better error handling
    """
    handler = SecureFileHandler()
    result = handler.process_uploaded_file(contents_b64, 'uploaded.csv')
    
    if result['success']:
        return result['file_io']
    else:
        raise FileProcessingError(result['error'])