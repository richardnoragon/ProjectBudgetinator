"""
Exception handling module for ProjectBudgetinator.

This module provides custom exception classes and utilities for better
error handling throughout the application.
"""

from .budget_exceptions import (
    BudgetError,
    BudgetFormatError,
    BudgetDataError,
    BudgetCalculationError,
    BudgetValidationError,
    WorksheetAccessError,
    CellAccessError,
    StyleApplicationError,
    handle_budget_exception
)

from .database_exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseTransactionError,
    DatabaseDataError,
    DateTimeParsingError,
    JSONProcessingError,
    DatabaseValidationError,
    DatabaseIntegrityError,
    handle_database_exception,
    safe_datetime_parse,
    safe_json_loads,
    safe_json_dumps
)

__all__ = [
    # Budget exceptions
    'BudgetError',
    'BudgetFormatError',
    'BudgetDataError',
    'BudgetCalculationError',
    'BudgetValidationError',
    'WorksheetAccessError',
    'CellAccessError',
    'StyleApplicationError',
    'handle_budget_exception',
    
    # Database exceptions
    'DatabaseError',
    'DatabaseConnectionError',
    'DatabaseTransactionError',
    'DatabaseDataError',
    'DateTimeParsingError',
    'JSONProcessingError',
    'DatabaseValidationError',
    'DatabaseIntegrityError',
    'handle_database_exception',
    'safe_datetime_parse',
    'safe_json_loads',
    'safe_json_dumps'
]