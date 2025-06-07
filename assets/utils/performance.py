# utils/performance.py - Type fixes for Pylance errors

from typing import Optional, Union, Any, Callable, Dict, List, Sized
from functools import wraps
import time
import logging

# Optional import for psutil - gracefully handle if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)

def check_psutil_availability() -> bool:
    """Check if psutil is available and log helpful info if not"""
    if not PSUTIL_AVAILABLE:
        logger.info(
            "psutil is not installed. Install it with: pip install psutil\n"
            "Memory monitoring features will be limited without psutil."
        )
        return False
    return True

class PerformanceMonitor:
    """Performance monitoring utility with proper type annotations"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, name: str) -> None:
        """Start timing an operation"""
        if name is None:
            # Fix for line 82 error - handle None case
            logger.warning("Timer name cannot be None, using default")
            name = "default_timer"
        
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End timing an operation and return duration"""
        if name is None:
            name = "default_timer"
            
        if name not in self.start_times:
            logger.warning(f"Timer '{name}' was not started")
            return 0.0
        
        duration = time.time() - self.start_times[name]
        del self.start_times[name]
        return duration
    
    def measure_memory_usage(self, obj: Optional[Any] = None) -> Dict[str, Union[int, float]]:
        """Measure memory usage with proper type checking"""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - using basic memory measurement")
            result = {
                'rss': 0,
                'vms': 0,
                'percent': 0.0,
                'error': 'psutil not available'
            }
        else:
            try:
                process = psutil.Process()  # type: ignore
                memory_info = process.memory_info()
                result = {
                    'rss': memory_info.rss,
                    'vms': memory_info.vms,
                    'percent': process.memory_percent()
                }
            except Exception as e:
                logger.error(f"Error measuring memory: {e}")
                result = {
                    'rss': 0,
                    'vms': 0,
                    'percent': 0.0,
                    'error': str(e)
                }
        
        # Fix for line 106 error - check if obj is Sized before calling len()
        if obj is not None:
            try:
                # Check if object has __len__ method (is Sized)
                if hasattr(obj, '__len__'):
                    result['object_size'] = len(obj)  # type: ignore
                else:
                    # For objects without __len__, try to get size another way
                    import sys
                    result['object_size'] = sys.getsizeof(obj)
            except (TypeError, AttributeError):
                logger.warning("Could not determine object size")
                result['object_size'] = 0
        
        return result


def performance_timer(func: Optional[Callable] = None, *, name: Optional[str] = None):
    """Decorator for timing function execution with proper type handling"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            timer_name = name or f.__name__
            if timer_name is None:  # Extra safety check
                timer_name = "unknown_function"
            
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                logger.info(f"Function '{timer_name}' took {duration:.4f} seconds")
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


class CacheManager:
    """Cache management with proper type annotations"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_calls': 0
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return self._stats.copy()
    
    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()
        self._stats = {'hits': 0, 'misses': 0, 'total_calls': 0}


def cached_function(max_size: int = 128):
    """Caching decorator with proper type handling"""
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, Any] = {}
        stats = {'hits': 0, 'misses': 0}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            if key in cache:
                stats['hits'] += 1
                return cache[key]
            
            # Cache miss
            stats['misses'] += 1
            result = func(*args, **kwargs)
            
            # Implement LRU eviction if cache is full
            if len(cache) >= max_size:
                # Remove oldest entry (simple FIFO for this example)
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            cache[key] = result
            return result
        
        # Fix for lines 311-312 errors - properly add attributes to wrapper
        def clear_cache() -> None:
            cache.clear()
            stats['hits'] = 0
            stats['misses'] = 0
        
        def cache_stats() -> Dict[str, int]:
            return stats.copy()
        
        # Properly assign methods to the wrapper function
        wrapper.clear_cache = clear_cache  # type: ignore
        wrapper.cache_stats = cache_stats  # type: ignore
        
        return wrapper
    
    return decorator


class DataFrameProfiler:
    """Profile DataFrame operations with proper type checking"""
    
    @staticmethod
    def profile_dataframe(df: Optional[Any]) -> Dict[str, Any]:
        """Profile a DataFrame with proper null checking"""
        if df is None:
            return {
                'error': 'DataFrame is None',
                'rows': 0,
                'columns': 0,
                'memory_usage': 0
            }
        
        try:
            # Check if it's a pandas DataFrame
            import pandas as pd
            if not isinstance(df, pd.DataFrame):
                return {
                    'error': 'Object is not a pandas DataFrame',
                    'type': type(df).__name__,
                    'size': len(df) if hasattr(df, '__len__') else 'unknown'
                }
            
            return {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error profiling DataFrame: {e}")
            return {
                'error': str(e),
                'rows': 0,
                'columns': 0
            }


# Usage example with proper type handling
def monitor_csv_processing(csv_data: Optional[Any] = None) -> Dict[str, Any]:
    """Monitor CSV processing performance"""
    monitor = PerformanceMonitor()
    
    # Check if advanced monitoring is available
    psutil_status = check_psutil_availability()
    
    # Safe timer name handling
    timer_name = "csv_processing"
    monitor.start_timer(timer_name)
    
    try:
        # Safe memory measurement
        memory_stats = monitor.measure_memory_usage(csv_data)
        
        # Safe DataFrame profiling
        profiler = DataFrameProfiler()
        df_stats = profiler.profile_dataframe(csv_data)
        
        duration = monitor.end_timer(timer_name)
        
        return {
            'duration': duration,
            'memory': memory_stats,
            'dataframe': df_stats,
            'psutil_available': psutil_status,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error in performance monitoring: {e}")
        return {
            'error': str(e),
            'status': 'failed'
        }