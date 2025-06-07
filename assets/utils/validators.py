# shared/validators.py
"""
Validation utilities
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import json
import re
from datetime import datetime

from core.exceptions import ValidationError
from config.settings import REQUIRED_INTERNAL_COLUMNS, FILE_LIMITS

class CSVValidator:
    """Validates CSV files and structure"""
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size is within limits"""
        if file_size > FILE_LIMITS['max_file_size']:
            raise ValidationError(
                f"File size ({file_size:,} bytes) exceeds maximum "
                f"allowed size ({FILE_LIMITS['max_file_size']:,} bytes)"
            )
        return True
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file has allowed extension"""
        if not any(filename.lower().endswith(ext) for ext in FILE_LIMITS['allowed_extensions']):
            raise ValidationError(
                f"File extension not allowed. Allowed extensions: "
                f"{', '.join(FILE_LIMITS['allowed_extensions'])}"
            )
        return True
    
    @staticmethod
    def validate_csv_structure(df: pd.DataFrame) -> bool:
        """Validate CSV has minimum required structure"""
        if df.empty:
            raise ValidationError("CSV file is empty")
        
        if len(df) > FILE_LIMITS['max_rows']:
            raise ValidationError(
                f"CSV has too many rows ({len(df):,}). "
                f"Maximum allowed: {FILE_LIMITS['max_rows']:,}"
            )
        
        if len(df.columns) == 0:
            raise ValidationError("CSV has no columns")
        
        return True
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> bool:
        """Validate that required columns are present after mapping"""
        mapped_columns = set(column_mapping.values())
        required_columns = set(REQUIRED_INTERNAL_COLUMNS.keys())
        
        missing_columns = required_columns - mapped_columns
        if missing_columns:
            raise ValidationError(
                f"Missing required column mappings: {', '.join(missing_columns)}"
            )
        
        return True

class MappingValidator:
    """Validates column mappings"""
    
    @staticmethod
    def validate_mapping_completeness(mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate that all required mappings are present"""
        if not mapping:
            return False, list(REQUIRED_INTERNAL_COLUMNS.keys())
        
        mapped_internal_keys = set(mapping.values())
        required_internal_keys = set(REQUIRED_INTERNAL_COLUMNS.keys())
        missing_keys = required_internal_keys - mapped_internal_keys
        
        return len(missing_keys) == 0, list(missing_keys)
    
    @staticmethod
    def validate_mapping_uniqueness(mapping: Dict[str, str]) -> bool:
        """Validate that each CSV column maps to only one internal field"""
        internal_values = list(mapping.values())
        if len(internal_values) != len(set(internal_values)):
            raise ValidationError("Each CSV column must map to a unique internal field")
        return True

class ClassificationValidator:
    """Validates door classifications"""
    
    @staticmethod
    def validate_classification_completeness(
        classifications: Dict[str, Dict[str, Any]], 
        all_doors: List[str]
    ) -> Dict[str, Any]:
        """Validate classification completeness"""
        if not all_doors:
            return {
                'is_complete': True,
                'total_doors': 0,
                'classified_doors': 0,
                'missing_count': 0,
                'missing_doors': [],
                'message': 'No doors to classify'
            }
        
        missing_doors = []
        incomplete_doors = []
        
        for door_id in all_doors:
            if door_id not in classifications:
                missing_doors.append(door_id)
                continue
            
            classification = classifications[door_id]
            if not ClassificationValidator._is_classification_complete(classification):
                incomplete_doors.append(door_id)
        
        total_doors = len(all_doors)
        missing_count = len(missing_doors) + len(incomplete_doors)
        is_complete = missing_count == 0
        
        return {
            'is_complete': is_complete,
            'total_doors': total_doors,
            'classified_doors': total_doors - missing_count,
            'missing_count': missing_count,
            'missing_doors': missing_doors,
            'incomplete_doors': incomplete_doors,
            'message': ClassificationValidator._get_validation_message(is_complete, missing_count, total_doors)
        }
    
    @staticmethod
    def _is_classification_complete(classification: Dict[str, Any]) -> bool:
        """Check if a single classification is complete"""
        required_fields = ['floor', 'security']
        return all(
            field in classification and classification[field] is not None 
            for field in required_fields
        )
    
    @staticmethod
    def _get_validation_message(is_complete: bool, missing_count: int, total_doors: int) -> str:
        """Get user-friendly validation message"""
        if is_complete:
            return f"✓ All {total_doors} doors classified successfully"
        elif missing_count == 1:
            return "⚠️ 1 door needs classification"
        else:
            return f"⚠️ {missing_count} doors need classification"
