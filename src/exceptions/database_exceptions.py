"""
Custom exception classes for ProjectBudgetinator database operations.

This module defines specific exception types for database-related errors,
providing better error handling and debugging capabilities for database operations.
"""

import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception class for all database-related errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize database error with message and optional context.
        
        Args:
            message: Human-readable error message
            context: Optional dictionary with error context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        
        # Log the error with context
        logger.error(f"DatabaseError: {message}", extra={"error_context": self.context})
    
    def __str__(self) -> str:
        """Return string representation with context if available."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection operations fail."""
    
    def __init__(self, message: str, db_path: Optional[str] = None, 
                 operation: Optional[str] = None, **kwargs):
        """
        Initialize database connection error.
        
        Args:
            message: Error description
            db_path: Path to the database file
            operation: Database operation that failed
            **kwargs: Additional context information
        """
        context = kwargs
        if db_path:
            context['db_path'] = db_path
        if operation:
            context['operation'] = operation
            
        super().__init__(message, context)


class DatabaseTransactionError(DatabaseError):
    """Exception raised when database transaction operations fail."""
    
    def __init__(self, message: str, transaction_type: Optional[str] = None,
                 table_name: Optional[str] = None, **kwargs):
        """
        Initialize database transaction error.
        
        Args:
            message: Error description
            transaction_type: Type of transaction (INSERT, UPDATE, DELETE, SELECT)
            table_name: Name of the table involved
            **kwargs: Additional context information
        """
        context = kwargs
        if transaction_type:
            context['transaction_type'] = transaction_type
        if table_name:
            context['table_name'] = table_name
            
        super().__init__(message, context)


class DatabaseDataError(DatabaseError):
    """Exception raised when database data is invalid or corrupted."""
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 field_name: Optional[str] = None, invalid_value: Optional[Any] = None,
                 **kwargs):
        """
        Initialize database data error.
        
        Args:
            message: Error description
            data_type: Type of data that caused the error
            field_name: Name of the field with invalid data
            invalid_value: The invalid value that caused the error
            **kwargs: Additional context information
        """
        context = kwargs
        if data_type:
            context['data_type'] = data_type
        if field_name:
            context['field_name'] = field_name
        if invalid_value is not None:
            context['invalid_value'] = str(invalid_value)
            
        super().__init__(message, context)


class DateTimeParsingError(DatabaseDataError):
    """Exception raised when datetime parsing operations fail."""
    
    def __init__(self, message: str, datetime_string: Optional[str] = None,
                 expected_format: Optional[str] = None, **kwargs):
        """
        Initialize datetime parsing error.
        
        Args:
            message: Error description
            datetime_string: The string that failed to parse
            expected_format: Expected datetime format
            **kwargs: Additional context information
        """
        context = kwargs
        if datetime_string:
            context['datetime_string'] = datetime_string
        if expected_format:
            context['expected_format'] = expected_format
            
        super().__init__(message, data_type="datetime", field_name="datetime_field", **context)


class JSONProcessingError(DatabaseDataError):
    """Exception raised when JSON processing operations fail."""
    
    def __init__(self, message: str, json_data: Optional[str] = None,
                 operation: Optional[str] = None, **kwargs):
        """
        Initialize JSON processing error.
        
        Args:
            message: Error description
            json_data: The JSON data that failed to process
            operation: Operation type (serialize, deserialize)
            **kwargs: Additional context information
        """
        context = kwargs
        if json_data:
            # Truncate long JSON data for logging
            context['json_data'] = json_data[:200] + "..." if len(json_data) > 200 else json_data
        if operation:
            context['operation'] = operation
            
        super().__init__(message, data_type="json", field_name="json_field", **context)


class DatabaseValidationError(DatabaseError):
    """Exception raised when database validation fails."""
    
    def __init__(self, message: str, validation_rule: Optional[str] = None,
                 field_name: Optional[str] = None, **kwargs):
        """
        Initialize database validation error.
        
        Args:
            message: Error description
            validation_rule: Validation rule that was violated
            field_name: Name of the field that failed validation
            **kwargs: Additional context information
        """
        context = kwargs
        if validation_rule:
            context['validation_rule'] = validation_rule
        if field_name:
            context['field_name'] = field_name
            
        super().__init__(message, context)


class DatabaseIntegrityError(DatabaseError):
    """Exception raised when database integrity constraints are violated."""
    
    def __init__(self, message: str, constraint_type: Optional[str] = None,
                 table_name: Optional[str] = None, **kwargs):
        """
        Initialize database integrity error.
        
        Args:
            message: Error description
            constraint_type: Type of constraint violated (UNIQUE, FOREIGN_KEY, etc.)
            table_name: Name of the table involved
            **kwargs: Additional context information
        """
        context = kwargs
        if constraint_type:
            context['constraint_type'] = constraint_type
        if table_name:
            context['table_name'] = table_name
            
        super().__init__(message, context)


def handle_database_exception(func):
    """
    Decorator for handling database exceptions with proper logging and context.
    
    Args:
        func: Function to wrap with exception handling
        
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError:
            # Re-raise database errors as they already have proper logging
            raise
        except ValueError as e:
            # Convert ValueError to DatabaseDataError
            raise DatabaseDataError(
                f"Invalid data value in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except KeyError as e:
            # Convert KeyError to DatabaseDataError
            raise DatabaseDataError(
                f"Missing required data key in {func.__name__}: {str(e)}",
                function_name=func.__name__,
                missing_key=str(e)
            ) from e
        except TypeError as e:
            # Convert TypeError to DatabaseDataError
            raise DatabaseDataError(
                f"Incorrect data type in {func.__name__}: {str(e)}",
                function_name=func.__name__
            ) from e
        except Exception as e:
            # Convert any other exception to generic DatabaseError
            logger.exception(f"Unexpected error in {func.__name__}")
            raise DatabaseError(
                f"Unexpected database error in {func.__name__}: {str(e)}",
                {"function_name": func.__name__, "original_error": str(e)}
            ) from e
    
    return wrapper


def safe_datetime_parse(datetime_string: str, field_name: str = "datetime") -> Optional[Any]:
    """
    Safely parse datetime string with comprehensive error handling.
    
    Args:
        datetime_string: String to parse as datetime
        field_name: Name of the field for error context
        
    Returns:
        Parsed datetime object or None if parsing fails
        
    Raises:
        DateTimeParsingError: If parsing fails and string is not empty
    """
    if not datetime_string or datetime_string.strip() == "":
        return None
    
    try:
        # Try ISO format first
        from datetime import datetime
        return datetime.fromisoformat(datetime_string)
    except ValueError as e:
        # Try alternative formats
        alternative_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d",
        ]
        
        for fmt in alternative_formats:
            try:
                from datetime import datetime
                return datetime.strptime(datetime_string, fmt)
            except ValueError:
                continue
        
        # If all formats fail, raise custom exception
        raise DateTimeParsingError(
            f"Failed to parse datetime string for field '{field_name}'",
            datetime_string=datetime_string,
            field_name=field_name,
            expected_format="ISO format or common datetime formats"
        ) from e


def safe_json_loads(json_string: str, field_name: str = "json_data") -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON string with comprehensive error handling.
    
    Args:
        json_string: String to parse as JSON
        field_name: Name of the field for error context
        
    Returns:
        Parsed JSON object or empty dict if parsing fails
        
    Raises:
        JSONProcessingError: If parsing fails and string is not empty
    """
    import json
    
    if not json_string or json_string.strip() == "":
        return {}
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise JSONProcessingError(
            f"Failed to parse JSON string for field '{field_name}': {str(e)}",
            json_data=json_string,
            field_name=field_name,
            operation="deserialize"
        ) from e
    except TypeError as e:
        raise JSONProcessingError(
            f"Invalid JSON data type for field '{field_name}': {str(e)}",
            json_data=str(json_string),
            field_name=field_name,
            operation="deserialize"
        ) from e


def safe_json_dumps(data: Any, field_name: str = "json_data") -> str:
    """
    Safely serialize data to JSON string with comprehensive error handling.
    
    Args:
        data: Data to serialize as JSON
        field_name: Name of the field for error context
        
    Returns:
        JSON string representation of data
        
    Raises:
        JSONProcessingError: If serialization fails
    """
    import json
    
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise JSONProcessingError(
            f"Failed to serialize data to JSON for field '{field_name}': {str(e)}",
            json_data=str(data),
            field_name=field_name,
            operation="serialize"
        ) from e