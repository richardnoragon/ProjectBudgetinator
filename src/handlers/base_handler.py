"""
Base handler class for all Excel operation handlers.

This module provides a comprehensive base class that eliminates
code duplication across handler modules while providing consistent
error handling, validation, and resource management.
"""

import logging
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import traceback
from datetime import datetime

from utils.excel_manager import ExcelManager, excel_context
from utils.resource_cleanup import force_system_cleanup
from utils.performance_monitor import monitor_performance, monitor_file_operation
from gui.window_manager import BaseDialog


class ValidationResult:
    """Result of input validation."""
    
    def __init__(self, valid: bool = True, errors: Optional[List[str]] = None,
                 warnings: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.valid = False
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge another validation result."""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings
        )


class OperationResult:
    """Result of an operation."""
    
    def __init__(self, success: bool = True, message: str = "",
                 data: Optional[Dict[str, Any]] = None,
                 errors: Optional[List[str]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.errors = errors or []
        self.timestamp = datetime.now()


class BaseHandler(ABC):
    """
    Base class for all Excel operation handlers.
    
    Provides consistent error handling, validation, logging, and
    resource management across all handler modules.
    """
    
    def __init__(self, parent_window: Optional[tk.Widget],
                 workbook_path: Optional[str] = None):
        """
        Initialize base handler.
        
        Args:
            parent_window: Parent tkinter window (can be None for automatic operations)
            workbook_path: Path to Excel workbook (optional)
        """
        self.parent = parent_window
        self.workbook_path = workbook_path
        class_name = self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{class_name}")
        self._operation_history: List[OperationResult] = []
        
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate input data before processing.
        
        Args:
            data: Input data to validate
            
        Returns:
            ValidationResult: Validation result with errors/warnings
        """
        pass
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> OperationResult:
        """
        Process the operation.
        
        Args:
            data: Processed and validated data
            
        Returns:
            OperationResult: Operation result
        """
        pass
    
    @monitor_performance(include_memory=True, log_level='INFO')
    def execute(self, data: Dict[str, Any]) -> OperationResult:
        """
        Execute the complete operation with validation and error handling.
        
        Args:
            data: Raw input data
            
        Returns:
            OperationResult: Final operation result
        """
        try:
            self.logger.info(f"Starting {self.__class__.__name__} operation")
            
            # Validate input
            validation_result = self.validate_input(data)
            if not validation_result.valid:
                return OperationResult(
                    success=False,
                    message="Validation failed",
                    errors=validation_result.errors
                )
            
            # Log warnings if any
            if validation_result.warnings:
                for warning in validation_result.warnings:
                    self.logger.warning(warning)
            
            # Process operation
            result = self.process(data)
            
            # Record in history
            self._operation_history.append(result)
            
            status = 'success' if result.success else 'failed'
            self.logger.info(
                f"Completed {self.__class__.__name__} operation: {status}"
            )
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Error in {self.__class__.__name__}")
            return OperationResult(
                success=False,
                message=f"Unexpected error: {str(e)}",
                errors=[str(e), traceback.format_exc()]
            )
    
    def show_error(self, message: str, title: str = "Error") -> None:
        """
        Show consistent error message.
        
        Args:
            message: Error message
            title: Dialog title
        """
        if self.parent:
            from tkinter import messagebox
            messagebox.showerror(title, message)
        self.logger.error(message)
    
    def show_success(self, message: str, title: str = "Success") -> None:
        """
        Show consistent success message.
        
        Args:
            message: Success message
            title: Dialog title
        """
        if self.parent:
            from tkinter import messagebox
            messagebox.showinfo(title, message)
        self.logger.info(message)
    
    def show_warning(self, message: str, title: str = "Warning") -> None:
        """
        Show consistent warning message.
        
        Args:
            message: Warning message
            title: Dialog title
        """
        if self.parent:
            from tkinter import messagebox
            messagebox.showwarning(title, message)
        self.logger.warning(message)
    
    def show_confirmation(self, message: str, title: str = "Confirm") -> bool:
        """
        Show confirmation dialog.
        
        Args:
            message: Confirmation message
            title: Dialog title
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        if self.parent:
            from tkinter import messagebox
            return messagebox.askyesno(title, message)
        else:
            # For automatic operations, log the confirmation request and return True
            self.logger.info(f"Auto-confirmation: {message}")
            return True
    
    def get_operation_history(self) -> List[OperationResult]:
        """
        Get operation history.
        
        Returns:
            List[OperationResult]: List of operation results
        """
        return self._operation_history.copy()
    
    def clear_history(self) -> None:
        """Clear operation history."""
        self._operation_history.clear()
    
    def validate_workbook_path(self, path: str) -> ValidationResult:
        """
        Validate workbook path.
        
        Args:
            path: Path to validate
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not path:
            result.add_error("Workbook path is required")
            return result
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            result.add_error(f"File does not exist: {path}")
        elif path_obj.suffix.lower() not in ['.xlsx', '.xls']:
            result.add_error("File must be an Excel file (.xlsx or .xls)")
        elif not path_obj.is_file():
            result.add_error("Path is not a file")
        
        return result
    
    def validate_required_fields(self, data: Dict[str, Any],
                                 required_fields: List[str]) -> ValidationResult:
        """
        Validate required fields in data.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        for field in required_fields:
            # For required fields, we need to check if the field is truly missing or empty
            # Note: 0 is a valid value for required numeric fields
            if field not in data or data[field] is None:
                result.add_error(f"{field} is required")
            elif isinstance(data[field], str) and str(data[field]).strip() == "":
                result.add_error(f"{field} is required")
            elif isinstance(data[field], (int, float)) and data[field] == 0:
                # 0 is a valid value for numeric fields, don't treat as missing
                pass
        
        return result
    
    def validate_numeric_fields(self, data: Dict[str, Any],
                                numeric_fields: List[str]) -> ValidationResult:
        """
        Validate numeric fields.
        
        Args:
            data: Data to validate
            numeric_fields: List of field names that should be numeric
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        for field in numeric_fields:
            if field in data and data[field] is not None:
                # Handle the case where data[field] might already be a number
                if isinstance(data[field], (int, float)):
                    # Already a valid number, including 0
                    continue
                try:
                    # Try to convert string to number
                    converted = float(str(data[field]))
                    # Update the data with the converted value
                    data[field] = converted
                except (ValueError, TypeError):
                    result.add_error(f"{field} must be a valid number")
        
        return result


class ExcelOperationHandler(BaseHandler):
    """
    Base handler for Excel-specific operations.
    
    Extends BaseHandler with Excel-specific functionality.
    """
    
    def __init__(self, parent_window: tk.Widget, workbook_path: str):
        """
        Initialize Excel operation handler.
        
        Args:
            parent_window: Parent tkinter window
            workbook_path: Path to Excel workbook
        """
        super().__init__(parent_window, workbook_path)
        self._workbook: Optional[ExcelManager] = None
    
    def get_workbook(self) -> Optional[ExcelManager]:
        """
        Get workbook instance.
        
        Returns:
            Optional[ExcelManager]: Workbook instance or None
        """
        return self._workbook
    
    def open_workbook(self) -> ExcelManager:
        """
        Open workbook with proper error handling.
        
        Returns:
            ExcelManager: Workbook instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other file-related errors
        """
        if not self.workbook_path:
            raise ValueError("Workbook path not specified")
        
        validation = self.validate_workbook_path(self.workbook_path)
        if not validation.valid:
            raise ValueError("; ".join(validation.errors))
        
        self._workbook = ExcelManager(self.workbook_path)
        return self._workbook
    
    def close_workbook(self) -> None:
        """Close workbook and cleanup resources."""
        if self._workbook:
            self._workbook.force_close()
            self._workbook = None
    
    def with_workbook_context(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with workbook context manager.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Function result
        """
        if not self.workbook_path:
            raise ValueError("Workbook path not specified")
        
        with excel_context(self.workbook_path) as wb:
            return func(wb, *args, **kwargs)
    
    def get_sheet_names(self) -> List[str]:
        """
        Get list of sheet names from workbook.
        
        Returns:
            List[str]: List of sheet names
        """
        if not self.workbook_path:
            return []
        
        try:
            with excel_context(self.workbook_path) as wb:
                return wb.sheetnames
        except Exception as e:
            self.logger.error(f"Error getting sheet names: {e}")
            return []
    
    def sheet_exists(self, sheet_name: str) -> bool:
        """
        Check if sheet exists in workbook.
        
        Args:
            sheet_name: Name of sheet to check
            
        Returns:
            bool: True if sheet exists
        """
        return sheet_name in self.get_sheet_names()


class DialogHandler(BaseHandler):
    """
    Base handler for dialog-based operations.
    
    Provides common functionality for dialog-based handlers.
    """
    
    def __init__(self, parent_window: tk.Widget, dialog_class: type):
        """
        Initialize dialog handler.
        
        Args:
            parent_window: Parent tkinter window
            dialog_class: Dialog class to instantiate
        """
        super().__init__(parent_window)
        self.dialog_class = dialog_class
        self._current_dialog: Optional[BaseDialog] = None
    
    def show_dialog(self, *args, **kwargs) -> Any:
        """
        Show dialog and return result.
        
        Args:
            *args: Positional arguments for dialog
            **kwargs: Keyword arguments for dialog
            
        Returns:
            Any: Dialog result
        """
        try:
            self._current_dialog = self.dialog_class(self.parent, *args, **kwargs)
            result = self._current_dialog.show_modal()
            return result
        except Exception as e:
            self.logger.error(f"Error showing dialog: {e}")
            self.show_error(f"Error showing dialog: {str(e)}")
            return None
        finally:
            self._current_dialog = None
    
    def close_dialog(self) -> None:
        """Close current dialog if open."""
        if self._current_dialog:
            self._current_dialog.close()
            self._current_dialog = None


class BatchOperationHandler(BaseHandler):
    """
    Base handler for batch operations.
    
    Provides common functionality for processing multiple items.
    """
    
    def __init__(self, parent_window: tk.Widget, items: List[Dict[str, Any]]):
        """
        Initialize batch operation handler.
        
        Args:
            parent_window: Parent tkinter window
            items: List of items to process
        """
        super().__init__(parent_window)
        self.items = items
        self.processed_count = 0
        self.error_count = 0
    
    def process_batch(self, process_func: Callable[[Dict[str, Any]], OperationResult]) -> List[OperationResult]:
        """
        Process batch of items.
        
        Args:
            process_func: Function to process each item
            
        Returns:
            List[OperationResult]: Results for each item
        """
        results = []
        
        for i, item in enumerate(self.items):
            try:
                result = process_func(item)
                results.append(result)
                
                if result.success:
                    self.processed_count += 1
                else:
                    self.error_count += 1
                
                status = 'success' if result.success else 'failed'
                self.logger.info(f"Processed item {i+1}/{len(self.items)}: {status}")
                
            except Exception as e:
                self.logger.error(f"Error processing item {i+1}: {e}")
                error_result = OperationResult(
                    success=False,
                    message=f"Error processing item: {str(e)}",
                    errors=[str(e)]
                )
                results.append(error_result)
                self.error_count += 1
        
        return results
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Get batch processing summary.
        
        Returns:
            Dict[str, Any]: Processing summary
        """
        return {
            'total_items': len(self.items),
            'processed': self.processed_count,
            'errors': self.error_count,
            'success_rate': (self.processed_count / len(self.items) * 100)
                           if self.items else 0
        }


def cleanup_all_handlers():
    """
    Cleanup all handler resources.
    
    Should be called on application exit to ensure
    all resources are properly released.
    """
    # Force cleanup of Excel resources
    force_system_cleanup()
    
    # Get logger for cleanup
    cleanup_logger = logging.getLogger(__name__)
    cleanup_logger.info("All handlers cleaned up")


# Register cleanup on application exit
import atexit
atexit.register(cleanup_all_handlers)
