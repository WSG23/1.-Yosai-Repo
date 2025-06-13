# ui/core/dependency_injection.py
"""
Dependency injection system for components
"""
from typing import Dict, Any, Callable, Optional, Type, TypeVar
from dataclasses import dataclass
from functools import wraps
import dash

T = TypeVar('T')

@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_type: Type
    implementation: Any
    singleton: bool = True
    factory: Optional[Callable] = None

class ServiceContainer:
    """Dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, ServiceRegistration] = {}
        self._instances: Dict[str, Any] = {}
    
    def register_singleton(self, service_type: Type[T], implementation: T) -> None:
        """Register a singleton service"""
        key = self._get_service_key(service_type)
        self._services[key] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            singleton=True
        )
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register service with factory"""
        key = self._get_service_key(service_type)
        self._services[key] = ServiceRegistration(
            service_type=service_type,
            implementation=None,
            singleton=True,
            factory=factory
        )
    
    def get(self, service_type: Type[T]) -> T:
        """Get service instance"""
        key = self._get_service_key(service_type)
        
        if key not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        registration = self._services[key]
        
        # Return singleton instance if exists
        if registration.singleton and key in self._instances:
            return self._instances[key]
        
        # Create new instance
        if registration.factory:
            instance = registration.factory()
        else:
            instance = registration.implementation
        
        # Store singleton instance
        if registration.singleton:
            self._instances[key] = instance
        
        return instance
    
    def _get_service_key(self, service_type: Type) -> str:
        """Get service key from type"""
        return f"{service_type.__module__}.{service_type.__name__}"

# Service interfaces
class DataService:
    """Interface for data operations"""
    
    def save_data(self, key: str, data: Any) -> None:
        pass
    
    def load_data(self, key: str) -> Any:
        pass
    
    def clear_data(self, key: str) -> None:
        pass

class EventBus:
    """Interface for component communication"""
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        pass
    
    def publish(self, event_type: str, data: Any) -> None:
        pass

# Default implementations
class InMemoryDataService(DataService):
    """In-memory data service implementation"""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
    
    def save_data(self, key: str, data: Any) -> None:
        self._data[key] = data
    
    def load_data(self, key: str) -> Any:
        return self._data.get(key)
    
    def clear_data(self, key: str) -> None:
        self._data.pop(key, None)

class SimpleEventBus(EventBus):
    """Simple event bus implementation"""
    
    def __init__(self):
        self._handlers: Dict[str, list] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Any) -> None:
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in event handler: {e}")

# Dependency injection decorator
def inject(*dependencies: Type):
    """Decorator to automatically inject dependencies into component methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get container from component
            if hasattr(self, '_container'):
                container = self._container
                # Inject dependencies as first arguments
                injected_args = []
                for dep_type in dependencies:
                    injected_args.append(container.get(dep_type))
                return func(self, *injected_args, *args, **kwargs)
            else:
                # Fallback to original call if no container
                return func(self, *args, **kwargs)
        return wrapper
    return decorator

# Global container
_global_container = ServiceContainer()

def get_container() -> ServiceContainer:
    """Get the global service container"""
    return _global_container

def configure_services() -> None:
    """Configure default services"""
    container = get_container()
    
    # Register core services
    container.register_singleton(DataService, InMemoryDataService())
    container.register_singleton(EventBus, SimpleEventBus())

def configure_services_with_app(app) -> None:
    """Configure services with app instance (for backward compatibility)"""
    configure_services()