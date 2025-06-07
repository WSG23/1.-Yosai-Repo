# utils/error_handler.py
"""
Centralized error handling system
"""

import logging
import traceback
import uuid
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, ParamSpec, Union
from datetime import datetime
from utils.logging_config import get_logger   # NEW
logger = get_logger(__name__)                # NEW

# Type variables for better type hinting
P = ParamSpec('P')
T = TypeVar('T')

# Custom exception classes
class YosaiError(Exception):
    """Base exception for Yosai application"""
    pass

class DataProcessingError(YosaiError):
    """Error in data processing operations"""
    pass

class ValidationError(YosaiError):
    """Error in data validation"""
    pass

class FileProcessingError(YosaiError):
    """Error in file processing operations"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate formatting"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle and log errors with context"""
        error_id = self._generate_error_id()
        error_info = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {},
            'traceback': traceback.format_exc() if self.logger.isEnabledFor(logging.DEBUG) else None
        }
        
        # Log the error
        self.logger.error(
            f"Error {error_id}: {error_info['error_type']} - {error_info['error_message']}",
            extra={'error_info': error_info, 'context': context}
        )
        
        # Log stack trace for debugging
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Stack trace for error {error_id}:", exc_info=True)
        
        return error_info
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ERR_{uuid.uuid4().hex[:8].upper()}"
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message with optional context"""
        self.logger.info(message, extra={'context': context})
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message with optional context"""
        self.logger.warning(message, extra={'context': context})
    
    def log_debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message with optional context"""
        self.logger.debug(message, extra={'context': context})

def error_boundary(
    fallback_value: Any = None,
    error_message: str = "An error occurred",
    log_errors: bool = True,
    return_error_dict: bool = True
):
    """Decorator to catch and handle errors gracefully"""
    def decorator(func: Callable[P, T]) -> Callable[P, Union[T, Dict[str, Any], Any]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[T, Dict[str, Any], Any]:
            error_handler = None
            if log_errors:
                error_handler = ErrorHandler(func.__module__)
            
            try:
                return func(*args, **kwargs)
                
            except YosaiError as e:
                # Known application errors - handle gracefully
                if log_errors and error_handler:
                    context = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys())
                    }
                    error_handler.handle_error(e, context)
                
                # Return user-friendly error response
                if return_error_dict:
                    return {
                        'success': False,
                        'error': str(e),
                        'error_type': 'application_error',
                        'user_message': str(e)
                    }
                else:
                    return fallback_value
            
            except Exception as e:
                # Unexpected errors - log and return generic message
                if log_errors and error_handler:
                    context = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys()),
                        'unexpected_error': True
                    }
                    error_handler.handle_error(e, context)
                
                if return_error_dict:
                    return {
                        'success': False,
                        'error': error_message,
                        'error_type': 'system_error',
                        'user_message': error_message
                    }
                else:
                    return fallback_value
        
        return wrapper
    return decorator

def safe_execute(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Dict[str, Any]:
    """Safely execute a function and return structured result"""
    error_handler = ErrorHandler()
    
    try:
        result = func(*args, **kwargs)
        return {
            'success': True,
            'result': result,
            'error': None
        }
    except Exception as e:
        context = {
            'function': func.__name__,
            'module': getattr(func, '__module__', 'unknown'),
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        }
        error_info = error_handler.handle_error(e, context)
        
        return {
            'success': False,
            'result': None,
            'error': error_info
        }

def log_function_call(logger_name: Optional[str] = None):
    """Decorator to log function calls and their results"""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            error_handler = ErrorHandler(logger_name or func.__module__)
            
            # Log function entry
            context = {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            error_handler.log_debug(f"Entering function {func.__name__}", context)
            
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                context['execution_time'] = execution_time
                error_handler.log_debug(f"Function {func.__name__} completed successfully", context)
                
                return result
                
            except Exception as e:
                # Log function failure
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                context['execution_time'] = execution_time
                context['error'] = str(e)
                error_handler.log_debug(f"Function {func.__name__} failed", context)
                raise
        
        return wrapper
    return decorator

class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, operation_name: str, logger_name: Optional[str] = None):
        self.operation_name = operation_name
        self.error_handler = ErrorHandler(logger_name or __name__)
        self.start_time: Optional[datetime] = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.error_handler.log_info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            execution_time = (datetime.utcnow() - self.start_time).total_seconds()
        else:
            execution_time = 0.0
        
        if exc_type is None:
            # Success
            self.error_handler.log_info(
                f"Operation completed: {self.operation_name}",
                {'execution_time': execution_time}
            )
        else:
            # Error occurred
            context = {
                'operation': self.operation_name,
                'execution_time': execution_time
            }
            self.error_handler.handle_error(exc_val, context)
        
        # Don't suppress the exception
        return False

# Convenience functions for common error patterns
def handle_file_error(func: Callable[P, T]) -> Callable[P, Union[T, Dict[str, Any]]]:
    """Specific error handler for file operations"""
    return error_boundary(
        fallback_value=None,
        error_message="File processing failed",
        log_errors=True
    )(func)

def handle_data_error(func: Callable[P, T]) -> Callable[P, Union[T, Dict[str, Any]]]:
    """Specific error handler for data processing operations"""
    return error_boundary(
        fallback_value=None,
        error_message="Data processing failed",
        log_errors=True
    )(func)

def handle_validation_error(func: Callable[P, T]) -> Callable[P, Union[T, Dict[str, Any]]]:
    """Specific error handler for validation operations"""
    return error_boundary(
        fallback_value=None,
        error_message="Validation failed",
        log_errors=True
    )(func)

# Global error handler instance
global_error_handler = ErrorHandler('yosai.global')

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to log errors globally"""
    return global_error_handler.handle_error(error, context)

def log_info(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function to log info globally"""
    global_error_handler.log_info(message, context)

def log_warning(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function to log warnings globally"""
    global_error_handler.log_warning(message, context)

def log_debug(message: str, context: Optional[Dict[str, Any]] = None):
    """Convenience function to log debug messages globally"""
    global_error_handler.log_debug(message, context)

# Example usage and testing
def test_error_handling():
    """Test the error handling system"""
    
    @error_boundary(error_message="Test function failed")
    def test_function(should_fail: bool = False):
        if should_fail:
            raise ValueError("This is a test error")
        return "Success!"
    
    @log_function_call()
    def logged_function(x: int, y: int) -> int:
        return x + y
    
    # Test successful execution
    result1 = test_function(False)
    logger.info("Success result:", result1)
    
    # Test error handling
    result2 = test_function(True)
    logger.info("Error result:", result2)
    
    # Test function logging
    result3 = logged_function(5, 3)
    logger.info("Logged function result:", result3)
    
    # Test context manager
    try:
        with ErrorContext("test_operation"):
            # This would be your actual operation
            logger.info("Performing operation...")
    except Exception:
        pass
    
    logger.info("✅ Error handling tests completed")

if __name__ == "__main__":
    test_error_handling()