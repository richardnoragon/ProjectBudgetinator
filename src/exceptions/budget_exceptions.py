"""
Custom exception classes for ProjectBudgetinator budget operations.

This module defines specific exception types for budget-related errors,
providing better error handling and debugging capabilities.
"""

import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class BudgetError(Exception):
    """Base exception class for all budget-related errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize budget error with message and optional context.
        
        Args:
            message: Human-readable error message
            context: Optional dictionary with error context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        
        # Log the error with context
        logger.error(f"BudgetError: {message}", extra={"error_context": self.context})
    
    def __str__(self) -> str:
        """Return string representation with context if available."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class BudgetFormatError(BudgetError):
    """Exception raised when budget formatting operations fail."""
    
    def __init__(self, message: str, worksheet_name: Optional[str] = None, 
                 cell_ref: Optional[str] = None, **kwargs):
        """
        Initialize budget format error.
        
        Args:
            message: Error description
            worksheet_name: Name of the worksheet where error occurred
            cell_ref: Cell reference where error occurred
            **kwargs: Additional context information
        """
        context = kwargs
        if worksheet_name:
            context['worksheet_name'] = worksheet_name
        if cell_ref:
            context['cell_ref'] = cell_ref
            
        super().__init__(message, context)


class BudgetDataError(BudgetError):
    """Exception raised when budget data is invalid or corrupted."""
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 expected_type: Optional[str] = None, actual_value: Optional[Any] = None,
                 **kwargs):
        """
        Initialize budget data error.
        
        Args:
            message: Error description
            data_type: Type of data that caused the error
            expected_type: Expected data type
            actual_value: Actual value that caused the error
            **kwargs: Additional context information
        """
        context = kwargs
        if data_type:
            context['data_type'] = data_type
        if expected_type:
            context['expected_type'] = expected_type
        if actual_value is not None:
            context['actual_value'] = str(actual_value)
            
        super().__init__(message, context)


class BudgetCalculationError(BudgetError):
    """Exception raised when budget calculations fail."""
    
    def __init__(self, message: str, calculation_type: Optional[str] = None,
                 input_values: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize budget calculation error.
        
        Args:
            message: Error description
            calculation_type: Type of calculation that failed
            input_values: Input values used in the calculation
            **kwargs: Additional context information
        """
        context = kwargs
        if calculation_type:
            context['calculation_type'] = calculation_type
        if input_values:
            context['input_values'] = input_values
            
        super().__init__(message, context)


class BudgetValidationError(BudgetError):
    """Exception raised when budget validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None,
                 validation_rule: Optional[str] = None, **kwargs):
        """
        Initialize budget validation error.
        
        Args:
            message: Error description
            field_name: Name of the field that failed validation
            validation_rule: Validation rule that was violated
            **kwargs: Additional context information
        """
        context = kwargs
        if field_name:
            context['field_name'] = field_name
        if validation_rule:
            context['validation_rule'] = validation_rule
            
        super().__init__(message, context)


class WorksheetAccessError(BudgetError):
    """Exception raised when worksheet access operations fail."""
    
    def __init__(self, message: str, worksheet_name: Optional[str] = None,
                 operation: Optional[str] = None, **kwargs):
        """
        Initialize worksheet access error.
        
        Args:
            message: Error description
            worksheet_name: Name of the worksheet
            operation: Operation that failed
            **kwargs: Additional context information
        """
        context = kwargs
        if worksheet_name:
            context['worksheet_name'] = worksheet_name
        if operation:
            context['operation'] = operation
            
        super().__init__(message, context)


class CellAccessError(BudgetError):
    """Exception raised when cell access operations fail."""
    
    def __init__(self, message: str, cell_ref: Optional[str] = None,
                 worksheet_name: Optional[str] = None, **kwargs):
        """
        Initialize cell access error.
        
        Args:
            message: Error description
            cell_ref: Cell reference that caused the error
            worksheet_name: Name of the worksheet
            **kwargs: Additional context information
        """
        context = kwargs
        if cell_ref:
            context['cell_ref'] = cell_ref
        if worksheet_name:
            context['worksheet_name'] = worksheet_name
            
        super().__init__(message, context)


class StyleApplicationError(BudgetError):
    """Exception raised when style application fails."""
    
    def __init__(self, message: str, style_type: Optional[str] = None,
                 cell_ref: Optional[str] = None, **kwargs):
        """
        Initialize style application error.
        
        Args:
            message: Error description
            style_type: Type of style being applied
            cell_ref: Cell reference where style application failed
            **kwargs: Additional context information
        """
        context = kwargs
        if style_type:
            context['style_type'] = style_type
        if cell_ref:
            context['cell_ref'] = cell_ref
            
        super().__init__(message, context)


def handle_budget_exception(func):
    """
    Decorator for handling budget exceptions with proper logging and context.
    
    Args:
        func: Function to wrap with exception handling
        
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BudgetError:
            # Re-raise budget errors as they already have proper logging
            raise
        except ValueError as e:
            # Convert ValueError to BudgetDataError
            raise BudgetDataError(
                f"Invalid data value in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except KeyError as e:
            # Convert KeyError to BudgetDataError
            raise BudgetDataError(
                f"Missing required data key in {func.__name__}: {str(e)}",
                function_name=func.__name__,
                missing_key=str(e)
            ) from e
        except TypeError as e:
            # Convert TypeError to BudgetDataError
            raise BudgetDataError(
                f"Incorrect data type in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except AttributeError as e:
            # Convert AttributeError to WorksheetAccessError
            raise WorksheetAccessError(
                f"Missing attribute or method in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except IndexError as e:
            # Convert IndexError to BudgetDataError
            raise BudgetDataError(
                f"Index out of range in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except Exception as e:
            # Convert any other exception to generic BudgetError
            logger.exception(f"Unexpected error in {func.__name__}")
            raise BudgetError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                {"function_name": func.__name__, "original_error": str(e)}
            ) from e
    
    return wrapper