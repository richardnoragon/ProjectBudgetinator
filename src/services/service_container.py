"""
Service container for dependency injection and service management.

Provides a centralized location for service registration and resolution,
enabling loose coupling between components and easy testing.
"""

import logging
from typing import Dict, Type, Any
from threading import Lock

from services.excel_service import ExcelService, ExcelContextService
from services.partner_service import PartnerService
from services.workpackage_service import WorkpackageService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Service container for dependency injection.
    
    Provides a centralized registry for services with thread-safe
    registration and resolution.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize service container."""
        if not hasattr(self, '_initialized'):
            self.logger = logging.getLogger(f"{__name__}.ServiceContainer")
            self._services: Dict[str, Any] = {}
            self._service_types: Dict[str, Type] = {}
            self._initialized = True
            self._register_default_services()
    
    def _register_default_services(self):
        """Register default services."""
        try:
            # Register core services
            self.register_singleton('excel_service', ExcelService())
            self.register_singleton(
                'excel_context_service', ExcelContextService()
            )
            
            # Register business services with dependencies
            excel_service = self.get_service('excel_service')
            self.register_singleton(
                'partner_service', PartnerService(excel_service)
            )
            self.register_singleton(
                'workpackage_service', WorkpackageService(excel_service)
            )
            
            self.logger.info("Default services registered successfully")
            
        except Exception:
            self.logger.exception("Error registering default services")
            raise
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton service.
        
        Args:
            name: Service name
            instance: Service instance
        """
        with self._lock:
            self._services[name] = instance
            self.logger.debug(f"Registered singleton service: {name}")
    
    def register_transient(self, name: str, service_type: Type) -> None:
        """
        Register a transient service.
        
        Args:
            name: Service name
            service_type: Service class type
        """
        with self._lock:
            self._service_types[name] = service_type
            self.logger.debug(f"Registered transient service: {name}")
    
    def get_service(self, name: str) -> Any:
        """
        Get a service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not found
        """
        with self._lock:
            if name in self._services:
                return self._services[name]
            
            if name in self._service_types:
                service_type = self._service_types[name]
                instance = service_type()
                return instance
            
            raise KeyError(f"Service '{name}' not found")
    
    def has_service(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service exists
        """
        with self._lock:
            return name in self._services or name in self._service_types
    
    def remove_service(self, name: str) -> bool:
        """
        Remove a service.
        
        Args:
            name: Service name
            
        Returns:
            True if service was removed
        """
        with self._lock:
            removed = False
            if name in self._services:
                del self._services[name]
                removed = True
            
            if name in self._service_types:
                del self._service_types[name]
                removed = True
            
            if removed:
                self.logger.debug(f"Removed service: {name}")
            
            return removed
    
    def clear(self):
        """Clear all services."""
        with self._lock:
            self._services.clear()
            self._service_types.clear()
            self.logger.debug("All services cleared")
    
    def list_services(self) -> Dict[str, str]:
        """
        List all registered services.
        
        Returns:
            Dictionary mapping service names to their types
        """
        with self._lock:
            services = {}
            
            for name, instance in self._services.items():
                services[name] = (
                    f"{type(instance).__module__}.{type(instance).__name__}"
                )
            
            for name, service_type in self._service_types.items():
                services[name] = (
                    f"{service_type.__module__}.{service_type.__name__}"
                )
            
            return services
    
    def reset(self):
        """Reset the container to initial state."""
        with self._lock:
            self.clear()
            self._register_default_services()
            self.logger.info("Service container reset")


# Global service container instance
container = ServiceContainer()


def get_service(name: str) -> Any:
    """
    Convenience function to get a service from the global container.
    
    Args:
        name: Service name
        
    Returns:
        Service instance
    """
    return container.get_service(name)


def register_service(name: str, instance: Any) -> None:
    """
    Convenience function to register a service in the global container.
    
    Args:
        name: Service name
        instance: Service instance
    """
    container.register_singleton(name, instance)


def reset_services():
    """Reset the global service container."""
    container.reset()


class ServiceProvider:
    """
    Service provider for easy service access.
    
    Provides a convenient way to access services without direct
    dependency on the service container.
    """
    
    @staticmethod
    def excel_service() -> ExcelService:
        """Get Excel service."""
        return get_service('excel_service')
    
    @staticmethod
    def excel_context_service() -> ExcelContextService:
        """Get Excel context service."""
        return get_service('excel_context_service')
    
    @staticmethod
    def partner_service() -> PartnerService:
        """Get partner service."""
        return get_service('partner_service')
    
    @staticmethod
    def workpackage_service() -> WorkpackageService:
        """Get workpackage service."""
        return get_service('workpackage_service')


# Export commonly used items
__all__ = [
    'ServiceContainer',
    'container',
    'get_service',
    'register_service',
    'reset_services',
    'ServiceProvider'
]
