"""
Service layer package for ProjectBudgetinator.

This package provides a clean service layer architecture that separates
business logic from GUI code. It includes services for:
- Excel operations (ExcelService, ExcelContextService)
- Partner management (PartnerService)
- Workpackage management (WorkpackageService)
- Dependency injection (ServiceContainer, ServiceProvider)

Usage:
    from services import get_service, ServiceProvider
    
    # Get services via global container
    excel_service = get_service('excel_service')
    partner_service = get_service('partner_service')
    
    # Or use the service provider for convenience
    excel_service = ServiceProvider.excel_service()
    partner_service = ServiceProvider.partner_service()
"""

# Import core services
from services.excel_service import ExcelService, ExcelContextService
from services.partner_service import PartnerService
from services.workpackage_service import WorkpackageService

# Import service container and utilities
from services.service_container import (
    ServiceContainer,
    container,
    get_service,
    register_service,
    reset_services,
    ServiceProvider
)

# Define what should be imported with "from services import *"
__all__ = [
    # Core services
    'ExcelService',
    'ExcelContextService',
    'PartnerService',
    'WorkpackageService',
    
    # Service container
    'ServiceContainer',
    'container',
    'get_service',
    'register_service',
    'reset_services',
    'ServiceProvider'
]

# Version info for the service layer
__version__ = "1.0.0"
__author__ = "ProjectBudgetinator Team"
