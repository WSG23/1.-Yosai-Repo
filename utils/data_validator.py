# utils/data_validator.py - Fixed Version
"""
Enhanced data validation with detailed error reporting
"""

import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import re
import uuid

from utils.logging_config import get_logger

from utils.error_handler import ValidationError, DataProcessingError
from utils.csv_validator import CSVValidator
from ui.components.mapping import MappingValidator
from config.settings import REQUIRED_INTERNAL_COLUMNS, FILE_LIMITS

logger = get_logger(__name__)

# Thresholds used across validation routines
MAX_MISSING_PERCENTAGE_THRESHOLD = 50
MAX_STRING_LENGTH_THRESHOLD = 1000

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
            try:
                validation = self.mapping_validator.validate_mapping(mapping)
            except (TypeError, ValueError) as e:
                return {
                    'success': False,
                    'error': f"Invalid mapping format: {str(e)}",
                    'missing_mappings': []
                }

            if not validation.get('is_valid'):
                missing_keys = validation.get('missing_columns', [])
                raise ValidationError(validation.get('message', 'Invalid mapping'))

            # Check for duplicate internal mappings
            values = list(mapping.values())
            duplicates = [v for v in set(values) if values.count(v) > 1]
            if duplicates:
                raise ValidationError(
                    f"Duplicate internal mappings: {', '.join(duplicates)}"
                )

            # Check that mapped CSV columns exist
            missing_csv_columns = [col for col in mapping.keys() if col not in csv_headers]
            if missing_csv_columns:
                raise ValidationError(
                    f"Mapped CSV columns not found: {', '.join(missing_csv_columns)}"
                )

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
                if max_length > MAX_STRING_LENGTH_THRESHOLD:
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
            'data_types': self._analyze_data_types_optimized(df),
            'duplicates': self._analyze_duplicates_optimized(df),
            'outliers': self._detect_outliers_optimized(df),
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
        """Analyze missing data patterns using vectorized operations"""
        total_rows = len(df)
        total_cells = total_rows * len(df.columns)

        missing_counts = df.isna().sum()
        missing_percentages = df.isna().mean() * 100

        missing_stats = {
            col: {
                'missing_count': int(missing_counts[col]),
                'missing_percentage': float(missing_percentages[col]) if total_rows > 0 else 0.0,
            }
            for col in df.columns
        }

        total_missing_cells = int(missing_counts.sum())
        total_missing_percentage = (
            (total_missing_cells / total_cells) * 100 if total_cells > 0 else 0.0
        )

        return {
            'by_column': missing_stats,
            'total_missing_cells': total_missing_cells,
            'total_missing_percentage': total_missing_percentage,
        }
    
    def _analyze_data_types_optimized(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types and suggest improvements (vectorized)"""
        dtypes = df.dtypes.astype(str)
        unique_counts = df.nunique()
        total_count = len(df)

        type_analysis = {}
        for col in df.columns:
            dtype = dtypes[col]
            unique_count = int(unique_counts[col])

            should_be_categorical = (
                dtype == 'object'
                and unique_count < total_count * 0.1
                and unique_count < 50
            )

            type_analysis[col] = {
                'current_type': dtype,
                'unique_values': unique_count,
                'should_be_categorical': should_be_categorical,
            }

        return type_analysis
    
    def _analyze_duplicates_optimized(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate data using vectorized operations"""
        total_rows = len(df)
        duplicate_rows = int(df.duplicated().sum())

        key_column_duplicates = {}
        potential_key_columns = {'id', 'user_id', 'userid', 'door_id', 'doorid'}
        key_cols = [c for c in df.columns if c.lower() in potential_key_columns]

        for col in key_cols:
            key_column_duplicates[col] = int(df[col].duplicated().sum())

        return {
            'total_duplicate_rows': duplicate_rows,
            'duplicate_percentage': (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0.0,
            'key_column_duplicates': key_column_duplicates,
        }
    
    def _detect_outliers_optimized(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numeric columns using vectorized operations"""
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            return {}

        q1 = numeric_df.quantile(0.25)
        q3 = numeric_df.quantile(0.75)
        iqr = q3 - q1

        lower_bounds = q1 - 1.5 * iqr
        upper_bounds = q3 + 1.5 * iqr

        mask_lower = numeric_df.lt(lower_bounds, axis=1)
        mask_upper = numeric_df.gt(upper_bounds, axis=1)
        outlier_counts = (mask_lower | mask_upper).sum()

        outlier_analysis = {}
        total_rows = len(df)
        for col in numeric_df.columns:
            outlier_count = int(outlier_counts[col])
            outlier_analysis[col] = {
                'outlier_count': outlier_count,
                'outlier_percentage': (outlier_count / total_rows) * 100 if total_rows > 0 else 0.0,
                'lower_bound': lower_bounds[col],
                'upper_bound': upper_bounds[col],
            }

        return outlier_analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate data quality recommendations"""
        recommendations = []
        
        # Missing data recommendations
        missing_data = analysis['missing_data']
        high_missing_columns = [
            col for col, stats in missing_data['by_column'].items()
            if stats['missing_percentage'] > MAX_MISSING_PERCENTAGE_THRESHOLD
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
        
    except pd.errors.EmptyDataError:
        return {
            'success': False,
            'error': 'File is empty - no data to validate'
        }
    except pd.errors.ParserError as e:
        return {
            'success': False,
            'error': f"File format error: {str(e)}"
        }
    except MemoryError:
        return {
            'success': False,
            'error': 'File too large to validate - please use a smaller file'
        }
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error("Validation error (ID: %s): %s", error_id, str(e))
        return {
            'success': False,
            'error': f"Validation failed (Error ID: {error_id})"
        }
