# utils/data_validator.py - Fixed Version
"""
Enhanced data validation with detailed error reporting
"""

import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import re

from core.exceptions import ValidationError, DataProcessingError
from utils.validators import CSVValidator, MappingValidator
from config.settings import REQUIRED_INTERNAL_COLUMNS, FILE_LIMITS

class EnhancedDataValidator:
    """Enhanced data validation with detailed reporting"""
    
    def __init__(self):
        self.csv_validator = CSVValidator()
        self.mapping_validator = MappingValidator()
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
    
    def validate_upload(self, filename: str, file_size: int, contents: str) -> Dict[str, Any]:
        """Comprehensive upload validation"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        try:
            # File validation
            self.csv_validator.validate_file_extension(filename)
            self.csv_validator.validate_file_size(file_size)
            
            # Content validation
            df = self._parse_csv_safely(contents)
            self.csv_validator.validate_csv_structure(df)
            
            # Data quality checks
            self._validate_data_quality(df)
            
            return {
                'success': True,
                'dataframe': df,
                'headers': df.columns.tolist(),
                'row_count': len(df),
                'errors': self.validation_errors,
                'warnings': self.validation_warnings
            }
            
        except ValidationError as e:
            self.validation_errors.append(str(e))
            return {
                'success': False,
                'error': str(e),
                'errors': self.validation_errors,
                'warnings': self.validation_warnings
            }
    
    def validate_column_mapping(self, mapping: Dict[str, str], csv_headers: List[str]) -> Dict[str, Any]:
        """Validate column mapping with detailed feedback"""
        # Initialize missing_keys as empty list
        missing_keys: List[str] = []
        
        try:
            # Check mapping completeness
            is_complete, missing_keys = self.mapping_validator.validate_mapping_completeness(mapping)
            
            if not is_complete:
                missing_display_names = [
                    REQUIRED_INTERNAL_COLUMNS[key] for key in missing_keys
                ]
                raise ValidationError(f"Missing required mappings: {', '.join(missing_display_names)}")
            
            # Check mapping uniqueness
            self.mapping_validator.validate_mapping_uniqueness(mapping)
            
            # Check that mapped CSV columns exist
            missing_csv_columns = [col for col in mapping.keys() if col not in csv_headers]
            if missing_csv_columns:
                raise ValidationError(f"Mapped CSV columns not found: {', '.join(missing_csv_columns)}")
            
            return {
                'success': True,
                'mapping': mapping,
                'message': 'All required columns mapped successfully'
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'missing_mappings': missing_keys  # Now always defined
            }
    
    def validate_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate processed data before model generation"""
        issues = []
        warnings = []
        
        # Check for required columns
        display_names = list(REQUIRED_INTERNAL_COLUMNS.values())
        missing_columns = [col for col in display_names if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Data quality checks
        timestamp_col = REQUIRED_INTERNAL_COLUMNS['Timestamp']
        if timestamp_col in df.columns:
            # Check for invalid timestamps
            try:
                pd.to_datetime(df[timestamp_col], errors='coerce')
                null_timestamps = df[timestamp_col].isna().sum()
                if null_timestamps > 0:
                    warnings.append(f"{null_timestamps} records have invalid timestamps")
            except Exception:
                issues.append("Timestamp column cannot be parsed")
        
        # Check for empty required fields
        for internal_key, display_name in REQUIRED_INTERNAL_COLUMNS.items():
            if display_name in df.columns:
                null_count = df[display_name].isna().sum()
                if null_count > 0:
                    warnings.append(f"{null_count} records have empty {internal_key} values")
        
        # Check data volume
        if len(df) == 0:
            issues.append("No data remaining after processing")
        elif len(df) < 10:
            warnings.append("Very small dataset - results may not be meaningful")
        
        return {
            'success': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'record_count': len(df)
        }
    
    def _parse_csv_safely(self, contents: str) -> pd.DataFrame:
        """Safely parse CSV with detailed error reporting"""
        import io
        import base64
        
        try:
            # Decode base64 content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    content_str = decoded.decode(encoding)
                    df = pd.read_csv(io.StringIO(content_str))
                    break
                except UnicodeDecodeError:
                    continue
                except pd.errors.EmptyDataError:
                    raise ValidationError("CSV file is empty")
                except pd.errors.ParserError as e:
                    raise ValidationError(f"CSV parsing error: {str(e)}")
            
            if df is None:
                raise ValidationError("Could not decode CSV file with any supported encoding")
            
            return df
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Failed to parse CSV file: {str(e)}")
    
    def _validate_data_quality(self, df: pd.DataFrame) -> None:
        """Validate data quality and add warnings"""
        # Check for completely empty columns
        empty_columns = df.columns[df.isna().all()].tolist()
        if empty_columns:
            self.validation_warnings.append(f"Empty columns detected: {', '.join(empty_columns)}")
        
        # Check for duplicate headers
        duplicate_headers = df.columns[df.columns.duplicated()].tolist()
        if duplicate_headers:
            self.validation_errors.append(f"Duplicate column headers: {', '.join(duplicate_headers)}")
        
        # Check for suspicious data patterns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for very long strings (possible data corruption)
                max_length = df[col].astype(str).str.len().max()
                if max_length > 1000:
                    self.validation_warnings.append(f"Column '{col}' has very long values (max: {max_length} chars)")
                
                # Check for unusual characters
                if df[col].astype(str).str.contains(r'[^\x00-\x7F]', na=False).any():
                    self.validation_warnings.append(f"Column '{col}' contains non-ASCII characters")

class DataQualityAnalyzer:
    """Analyze data quality and provide recommendations"""
    
    def __init__(self):
        self.quality_metrics: Dict[str, Any] = {}
    
    def analyze_dataframe_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality analysis"""
        if df.empty:
            return {'error': 'DataFrame is empty'}
        
        analysis = {
            'basic_stats': self._get_basic_stats(df),
            'missing_data': self._analyze_missing_data(df),
            'data_types': self._analyze_data_types(df),
            'duplicates': self._analyze_duplicates(df),
            'outliers': self._detect_outliers(df),
            'recommendations': []
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics about the DataFrame"""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns)
        }
    
    def _analyze_missing_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing data patterns"""
        missing_stats = {}
        total_cells = len(df) * len(df.columns)
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_stats[col] = {
                'missing_count': missing_count,
                'missing_percentage': (missing_count / len(df)) * 100 if len(df) > 0 else 0
            }
        
        return {
            'by_column': missing_stats,
            'total_missing_cells': sum(stats['missing_count'] for stats in missing_stats.values()),
            'total_missing_percentage': (sum(stats['missing_count'] for stats in missing_stats.values()) / total_cells) * 100 if total_cells > 0 else 0
        }
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types and suggest improvements"""
        type_analysis = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = df[col].nunique()
            total_count = len(df)
            
            # Suggest categorical conversion for low cardinality string columns
            should_be_categorical = (
                dtype == 'object' and 
                unique_count < total_count * 0.1 and  # Less than 10% unique values
                unique_count < 50  # And less than 50 unique values
            )
            
            type_analysis[col] = {
                'current_type': dtype,
                'unique_values': unique_count,
                'should_be_categorical': should_be_categorical
            }
        
        return type_analysis
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate data"""
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        
        # Check for duplicates in key columns
        key_column_duplicates = {}
        potential_key_columns = ['id', 'user_id', 'userid', 'door_id', 'doorid']
        
        for col in df.columns:
            if col.lower() in potential_key_columns:
                duplicate_count = df[col].duplicated().sum()
                key_column_duplicates[col] = duplicate_count
        
        return {
            'total_duplicate_rows': duplicate_rows,
            'duplicate_percentage': (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0,
            'key_column_duplicates': key_column_duplicates
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numeric columns"""
        outlier_analysis = {}
        
        for col in df.select_dtypes(include=['number']).columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            outlier_analysis[col] = {
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(df)) * 100 if len(df) > 0 else 0,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        return outlier_analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate data quality recommendations"""
        recommendations = []
        
        # Missing data recommendations
        missing_data = analysis['missing_data']
        high_missing_columns = [
            col for col, stats in missing_data['by_column'].items()
            if stats['missing_percentage'] > 50
        ]
        
        if high_missing_columns:
            recommendations.append(
                f"Consider removing columns with high missing data: {', '.join(high_missing_columns)}"
            )
        
        # Duplicate data recommendations
        duplicates = analysis['duplicates']
        if duplicates['duplicate_percentage'] > 5:
            recommendations.append(
                f"Remove {duplicates['total_duplicate_rows']} duplicate rows ({duplicates['duplicate_percentage']:.1f}%)"
            )
        
        # Data type recommendations
        data_types = analysis['data_types']
        categorical_candidates = [
            col for col, info in data_types.items()
            if info['should_be_categorical']
        ]
        
        if categorical_candidates:
            recommendations.append(
                f"Convert to categorical for memory efficiency: {', '.join(categorical_candidates)}"
            )
        
        # Memory optimization
        memory_mb = analysis['basic_stats']['memory_usage_mb']
        if memory_mb > 100:
            recommendations.append(
                f"Large dataset ({memory_mb:.1f}MB) - consider processing in chunks"
            )
        
        return recommendations

def create_data_validator() -> EnhancedDataValidator:
    """Factory function to create data validator"""
    return EnhancedDataValidator()

def create_quality_analyzer() -> DataQualityAnalyzer:
    """Factory function to create quality analyzer"""
    return DataQualityAnalyzer()

def quick_validate_csv(file_path: str) -> Dict[str, Any]:
    """Quick validation of a CSV file"""
    validator = EnhancedDataValidator()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            contents = f.read()
        
        # Convert to base64 format for validation
        import base64
        encoded_contents = f"data:text/csv;base64,{base64.b64encode(contents.encode()).decode()}"
        
        import os
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        return validator.validate_upload(filename, file_size, encoded_contents)
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to validate file: {str(e)}"
        }