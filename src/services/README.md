# Service Layer Architecture

## Overview
This service layer implements optimization recommendation 3.2 from the ProjectBudgetinator optimization plan. It provides a clean separation between business logic and GUI code through a comprehensive service-oriented architecture.

## Architecture Components

### 1. Core Services

#### ExcelService
- **Purpose**: Centralized Excel file operations
- **Features**:
  - File validation and error handling
  - Sheet operations (read/write)
  - Data management with proper formatting
  - Backup creation functionality
  - Comprehensive error reporting

#### ExcelContextService
- **Purpose**: Safe Excel context management
- **Features**:
  - Context managers for automatic resource cleanup
  - Thread-safe workbook operations
  - Exception handling and logging
  - Resource lifecycle management

#### PartnerService
- **Purpose**: Partner data management and business logic
- **Features**:
  - Partner CRUD operations
  - Data validation (name, email, phone, budget)
  - Duplicate detection
  - Search and filtering capabilities
  - Summary statistics generation

#### WorkpackageService
- **Purpose**: Workpackage data management and business logic
- **Features**:
  - Workpackage CRUD operations
  - Date validation and business rules
  - Status management
  - Budget calculations
  - Duration analysis

### 2. Dependency Injection System

#### ServiceContainer
- **Purpose**: Centralized service registry and dependency injection
- **Features**:
  - Singleton pattern for global access
  - Thread-safe service registration
  - Automatic dependency resolution
  - Service lifecycle management
  - Runtime service configuration

#### ServiceProvider
- **Purpose**: Convenient service access interface
- **Features**:
  - Static methods for easy service access
  - No direct dependency on container
  - Type-safe service retrieval

## Usage Examples

### Basic Service Access

```python
from services import get_service, ServiceProvider

# Method 1: Direct container access
excel_service = get_service('excel_service')
partner_service = get_service('partner_service')

# Method 2: Service provider (recommended)
excel_service = ServiceProvider.excel_service()
partner_service = ServiceProvider.partner_service()
```

### Excel Operations

```python
from services import ServiceProvider

# Validate and read Excel file
excel_service = ServiceProvider.excel_service()
result = excel_service.validate_file_path('project.xlsx')
if result.success:
    sheets = excel_service.get_sheet_names('project.xlsx')
    data = excel_service.read_sheet_data('project.xlsx', 'Partners')
```

### Partner Management

```python
from services import ServiceProvider

partner_service = ServiceProvider.partner_service()

# Add new partner
partner_data = {
    'name': 'John Doe',
    'role': 'Project Manager',
    'organization': 'Tech Corp',
    'email': 'john@techcorp.com',
    'phone': '+1234567890',
    'budget': 50000.0
}

result = partner_service.add_partner('project.xlsx', partner_data)
if result.success:
    print(f"Added partner: {result.data['partner']['name']}")
```

### Workpackage Management

```python
from services import ServiceProvider

wp_service = ServiceProvider.workpackage_service()

# Add new workpackage
wp_data = {
    'name': 'UI Development',
    'description': 'Develop user interface components',
    'start_date': '2024-01-01',
    'end_date': '2024-03-31',
    'budget': 25000.0,
    'status': 'planned',
    'responsible_partner': 'John Doe',
    'deliverables': 'UI mockups, components, documentation'
}

result = wp_service.add_workpackage('project.xlsx', wp_data)
```

## Error Handling

All services use the `OperationResult` pattern for consistent error handling:

```python
from handlers.base_handler import OperationResult

result = partner_service.get_partners('project.xlsx')
if result.success:
    partners = result.data['partners']
else:
    print(f"Error: {result.message}")
    for error in result.errors:
        print(f"  - {error}")
```

## Testing Support

The service layer is designed for easy testing:

```python
from services import ServiceContainer

# Create test container
test_container = ServiceContainer()
test_container.register_singleton('excel_service', MockExcelService())
test_container.register_singleton('partner_service', PartnerService(MockExcelService()))

# Use in tests
partner_service = test_container.get_service('partner_service')
```

## Migration from GUI Code

### Before (GUI mixed with business logic)
```python
# Old approach - business logic in GUI handler
def add_partner_gui(self):
    name = self.name_input.text()
    email = self.email_input.text()
    # ... validation and Excel operations mixed with GUI code
```

### After (Clean separation)
```python
# New approach - business logic in service layer
def add_partner_gui(self):
    from services import ServiceProvider
    
    partner_service = ServiceProvider.partner_service()
    result = partner_service.add_partner(self.file_path, partner_data)
    
    if result.success:
        self.show_success_message("Partner added successfully")
    else:
        self.show_error_message(result.message, result.errors)
```

## Configuration

### Custom Service Registration

```python
from services import register_service, ExcelService

# Register custom Excel service with special configuration
custom_excel = ExcelService()
custom_excel.set_custom_config(...)
register_service('custom_excel', custom_excel)
```

### Service Reset

```python
from services import reset_services

# Reset to default configuration
reset_services()
```

## Benefits Achieved

1. **Separation of Concerns**: Business logic completely separated from GUI
2. **Testability**: Services can be easily mocked and tested independently
3. **Reusability**: Services can be used across different parts of the application
4. **Maintainability**: Changes to business logic don't affect GUI code
5. **Scalability**: Easy to add new services and extend functionality
6. **Resource Management**: Automatic cleanup and proper resource handling
7. **Error Handling**: Consistent error reporting across all operations

## File Structure

```
services/
├── __init__.py          # Package initialization and exports
├── excel_service.py     # Excel operations service
├── partner_service.py   # Partner management service
├── workpackage_service.py # Workpackage management service
├── service_container.py # Dependency injection container
└── README.md           # This documentation
```
