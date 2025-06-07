# core/models.py
"""
Standardized data models and result types
"""
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Dict, List
from datetime import datetime
import pandas as pd

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Standardized result container"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None  # ✅ Fixed: Made Optional
    metadata: Optional[Dict[str, Any]] = None  # ✅ Fixed: Made Optional
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def create_success(cls, data: T, warnings: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> 'Result[T]':
        """Create successful result"""  # ✅ Fixed: Renamed from 'success' to 'create_success'
        return cls(True, data, None, warnings, metadata)
    
    @classmethod
    def create_failure(cls, error: str, warnings: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> 'Result[T]':
        """Create failed result"""  # ✅ Fixed: Renamed from 'failure' to 'create_failure' and fixed parameter types
        return cls(False, None, error, warnings, metadata)

@dataclass
class AccessEvent:
    """Standardized access event model"""
    timestamp: datetime
    user_id: str
    door_id: str
    event_type: str
    floor: Optional[str] = None
    device_depth: Optional[int] = None
    security_level: Optional[str] = None

@dataclass
class DoorClassification:
    """Standardized door classification model"""
    door_id: str
    floor: str
    is_entrance: bool = False
    is_stairway: bool = False
    security_level: int = 5
    security_category: str = 'green'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'floor': self.floor,
            'is_ee': self.is_entrance,
            'is_stair': self.is_stairway,
            'security_level': self.security_level,
            'security': self.security_category
        }

@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    records_processed: int
    processing_time_seconds: float
    warnings_count: int
    errors_count: int
    memory_usage_mb: float

# Type aliases for clarity
DataFrameResult = Result[pd.DataFrame]
ClassificationResult = Result[Dict[str, DoorClassification]]