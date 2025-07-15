"""
Centralized exception handling system for ProjectBudgetinator.

Provides consistent error handling across all modules with proper
logging, user feedback, and error recovery mechanisms.
"""

import functools
import logging
import traceback
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Optional, Type, Union
import threading
from contextvars import ContextVar

# Import structured logging
from logger import get_structured_logger, LogContext

logger = get_structured_logger(__name__)

# Context variable for operation tracking
operation_id = ContextVar('operation_id', default=None)


class ErrorContext:
    """Context information for error handling."""
    
    def __init__(self, operation: str = None, user_id: str = None, 
                 file_path: str = None, additional_info: dict = None):
        self.operation = operation
        self.user_id = user_id
        self.file_path = file_path
        self.additional_info = additional_info or {}
        self.timestamp = logging.Formatter().formatTime(
            logging.LogRecord(
                name="", level=0, pathname="", lineno=0,
                msg="", args=(), exc_info=None
            )
        )


class ValidationResult:
    """Result of validation operations."""
    
    def __init__(self, valid: bool = True, errors: list = None, 
                 warnings: list = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)


class ErrorHandler:
    """Centralized error handling system."""
    
    def __init__(self, parent_window: tk.Tk = None):
        self.parent = parent_window
        self.logger = logging.getLogger(f"{__name__}.ErrorHandler")
    
    @staticmethod
    def generate_operation_id() -> str:
        """Generate a unique operation ID for tracking."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def set_operation_context(operation: str, **kwargs):
        """Set operation context for error tracking."""
        token = operation_id.set(ErrorHandler.generate_operation_id())
        return token
    
    @staticmethod
    def clear_operation_context(token):
        """Clear operation context."""
        operation_id.reset(token)
    
    def log_error(self, exception: Exception, context: ErrorContext = None):
        """Log error with context information."""
        if context is None:
            context = ErrorContext()
        
        log_entry = {
            'operation_id': operation_id.get(),
            'operation': context.operation,
            'user_id': context.user_id,
            'file_path': context.file_path,
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'traceback': traceback.format_exc(),
            'additional_info': context.additional_info,
            'timestamp': context.timestamp
        }
        
        self.logger.error(
            f"Error in {context.operation or 'unknown operation'}: {str(exception)}",
            extra={'error_context': log_entry}
        )
    
    def show_error_dialog(self, title: str, message: str, 
                         detail: str = None, parent=None):
        """Show error dialog to user."""
        parent = parent or self.parent
        
        if detail:
            messagebox.showerror(title, f"{message}\n\nDetails: {detail}", 
                               parent=parent)
        else:
            messagebox.showerror(title, message, parent=parent)
    
    def show_warning_dialog(self, title: str, message: str, parent=None):
        """Show warning dialog to user."""
        parent = parent or self.parent
        messagebox.showwarning(title, message, parent=parent)
    
    def show_info_dialog(self, title: str, message: str, parent=None):
        """Show info dialog to user."""
        parent = parent or self.parent
        messagebox.showinfo(title, message, parent=parent)


class ExceptionHandler:
    """Decorator-based exception handling system."""
    
    def __init__(self, parent_window: tk.Tk = None):
        self.error_handler = ErrorHandler(parent_window)
    
    @staticmethod
    def handle_exceptions(show_dialog: bool = True, 
                         log_error: bool = True,
                         return_value: Any = None,
                         parent=None):
        """
        Decorator for consistent exception handling.
        
        Args:
            show_dialog: Whether to show error dialog to user
            log_error: Whether to log the error
            return_value: Value to return on exception
            parent: Parent window for dialogs
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except FileNotFoundError as e:
                    if log_error:
                        logger.error(f"File not found: {e}")
                    if show_dialog:
                        messagebox.showerror("File Error", 
                                           f"File not found: {str(e)}", 
                                           parent=parent)
                    return return_value
                
                except PermissionError as e:
                    if log_error:
                        logger.error(f"Permission denied: {e}")
                    if show_dialog:
                        messagebox.showerror("Permission Error", 
                                           f"Permission denied: {str(e)}", 
                                           parent=parent)
                    return return_value
                
                except ValueError as e:
                    if log_error:
                        logger.error(f"Invalid value: {e}")
                    if show_dialog:
                        messagebox.showerror("Invalid Input", 
                                           str(e), 
                                           parent=parent)
                    return return_value
                
                except ConnectionError as e:
                    if log_error:
                        logger.error(f"Connection error: {e}")
                    if show_dialog:
                        messagebox.showerror("Connection Error", 
                                           f"Connection failed: {str(e)}", 
                                           parent=parent)
                    return return_value
                
                except MemoryError as e:
                    if log_error:
                        logger.error(f"Memory error: {e}")
                    if show_dialog:
                        messagebox.showerror("Memory Error", 
                                           "Insufficient memory to complete operation", 
                                           parent=parent)
                    return return_value
                
                except Exception as e:
                    if log_error:
                        logger.exception("Unexpected error occurred")
                    if show_dialog:
                        messagebox.showerror("Error", 
                                           f"An unexpected error occurred: {str(e)}", 
                                           parent=parent)
                    return return_value
            
            return wrapper
        return decorator
    
    @staticmethod
    def handle_with_context(operation: str = None, **context_kwargs):
        """
        Decorator with operation context.
        
        Args:
            operation: Operation name for logging
            **context_kwargs: Additional context information
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                token = None
                try:
                    token = ErrorHandler.set_operation_context(operation or func.__name__)
                    context = ErrorContext(operation=operation or func.__name__, 
                                         **context_kwargs)
                    return func(*args, **kwargs)
                except Exception as e:
                    error_handler = ErrorHandler()
                    error_handler.log_error(e, context)
                    raise
                finally:
                    if token:
                        ErrorHandler.clear_operation_context(token)
            return wrapper
        return decorator


class ValidationHandler:
    """Centralized validation utilities."""
    
    @staticmethod
    def validate_file_path(file_path: str) -> ValidationResult:
        """Validate file path."""
        result = ValidationResult()
        
        if not file_path:
            result.add_error("File path is required")
            return result
        
        import os
        if not os.path.exists(file_path):
            result.add_error(f"File does not exist: {file_path}")
        elif not os.path.isfile(file_path):
            result.add_error("Path is not a file")
        elif not file_path.lower().endswith(('.xlsx', '.xls')):
            result.add_error("File must be an Excel file (.xlsx or .xls)")
        
        return result
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email format."""
        result = ValidationResult()
        
        if email and ('@' not in email or 
                     '.' not in email.split('@')[-1]):
            result.add_error("Invalid email format")
        
        return result
    
    @staticmethod
    def validate_positive_number(value: str, field_name: str) -> ValidationResult:
        """Validate positive number."""
        result = ValidationResult()
        
        try:
            num = float(value)
            if num < 0:
                result.add_error(f"{field_name} must be positive")
        except (ValueError, TypeError):
            result.add_error(f"{field_name} must be a valid number")
        
        return result


class RecoveryHandler:
    """Error recovery and retry mechanisms."""
    
    @staticmethod
    def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
        """
        Decorator for retrying operations on exception.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import time
                
                last_exception = None
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(
                                f"Retry attempt {attempt + 1}/{max_retries} "
                                f"for {func.__name__}: {str(e)}"
                            )
                            time.sleep(delay * (attempt + 1))  # Exponential backoff
                        else:
                            logger.error(
                                f"Max retries ({max_retries}) exceeded for "
                                f"{func.__name__}: {str(e)}"
                            )
                            raise last_exception
                
                return None
            return wrapper
        return decorator


# Convenience decorators
handle_exceptions = ExceptionHandler.handle_exceptions()
handle_with_context = ExceptionHandler.handle_with_context

# Global error handler instance
global_error_handler = ErrorHandler()


def setup_error_handling(parent_window: tk.Tk = None):
    """Initialize global error handling system."""
    global global_error_handler
    global_error_handler = ErrorHandler(parent_window)
    logger.info("Error handling system initialized")


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return global_error_handler
