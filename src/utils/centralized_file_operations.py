"""ProjectBudgetinator Centralized File Operations Module.

This module provides a unified, secure interface for all file operations in the
ProjectBudgetinator application, ensuring consistent security validation, error
handling, and logging across all file interactions.

The module centralizes:
    - Excel workbook opening with security validation
    - Workbook saving with path sanitization
    - File path validation and sanitization
    - Consistent error handling and logging
    - Security validator integration
    - Operation result standardization

Functions:
    safe_file_operation: Core function for all secure file operations
    safe_open_workbook: Safely open Excel workbooks with validation
    safe_save_workbook: Safely save workbooks with path validation
    validate_file_path: Validate file paths for security compliance

Security Features:
    - All file paths are validated and sanitized
    - Excel files are validated before opening
    - Proper extension handling for save operations
    - Comprehensive error logging and reporting
    - Protection against path traversal attacks

Example:
    Opening a workbook safely:
    
        success, workbook, error = safe_open_workbook("path/to/file.xlsx")
        if success:
            # Process workbook
            pass
        else:
            print(f"Error: {error}")

    Saving a workbook safely:
    
        success, saved_path, error = safe_save_workbook(workbook, "output.xlsx")

Note:
    All operations return a consistent tuple format: (success, result, error_message).
    This ensures predictable error handling throughout the application.
"""

import logging
from typing import Tuple, Any, Optional
from utils.security_validator import SecurityValidator

logger = logging.getLogger(__name__)


def safe_file_operation(operation_type: str, file_path: str, **kwargs) -> Tuple[bool, Optional[Any], Optional[str]]:
    """Centralized secure file operations with comprehensive validation and error handling.
    
    This function provides a unified interface for all file operations in the application,
    ensuring consistent security validation, error handling, and logging. It supports
    multiple operation types and maintains a standardized return format.
    
    Args:
        operation_type (str): Type of operation to perform. Supported values:
            - 'open': Open and load an Excel workbook
            - 'save': Save a workbook to specified path
            - 'validate': Validate file path only
        file_path (str): Path to the file to operate on
        **kwargs: Additional arguments for specific operations:
            - workbook: Required for 'save' operations (openpyxl.Workbook)
    
    Returns:
        Tuple[bool, Optional[Any], Optional[str]]: A tuple containing:
            - success (bool): True if operation succeeded, False otherwise
            - result (Optional[Any]): Operation result or None if failed:
                - For 'open': openpyxl.Workbook object
                - For 'save': validated file path string
                - For 'validate': validated file path string
            - error_message (Optional[str]): Error description if operation failed
    
    Raises:
        None: All exceptions are caught and returned as error messages.
    
    Examples:
        Opening a workbook:
        
            success, workbook, error = safe_file_operation('open', 'data.xlsx')
            if success:
                # Process workbook
                pass
            else:
                print(f"Error: {error}")
        
        Saving a workbook:
        
            success, path, error = safe_file_operation(
                'save', 'output.xlsx', workbook=my_workbook
            )
        
        Validating a path:
        
            success, validated_path, error = safe_file_operation('validate', 'file.xlsx')
    
    Security Features:
        - Excel file content validation before opening
        - Path traversal attack prevention
        - File extension validation and correction
        - Comprehensive input sanitization
        - Detailed security logging
    
    Note:
        This function is the recommended way to perform all file operations
        in the application to ensure consistent security and error handling.
    """
    try:
        # Validate Excel file for read operations
        if operation_type in ['open', 'load']:
            is_valid, error_msg = SecurityValidator.validate_excel_file(file_path)
            if not is_valid:
                logger.warning(f"Security validation failed for {operation_type}: {error_msg} (file: {file_path})")
                return False, None, f"Security validation failed: {error_msg}"
        
        # Validate and sanitize file path
        try:
            safe_path = SecurityValidator.validate_file_path(file_path)
        except ValueError as e:
            logger.warning(f"File path validation failed for {operation_type}: {str(e)} (file: {file_path})")
            return False, None, f"Invalid file path: {str(e)}"
        
        # Perform the operation based on type
        if operation_type == 'open':
            from openpyxl import load_workbook
            workbook = load_workbook(safe_path)
            logger.info(f"Successfully opened workbook: {safe_path}")
            return True, workbook, None
            
        elif operation_type == 'save':
            workbook = kwargs.get('workbook')
            if not workbook:
                return False, None, "No workbook provided for save operation"
            
            # Ensure proper extension
            if not safe_path.lower().endswith('.xlsx'):
                safe_path += '.xlsx'
            
            workbook.save(safe_path)
            logger.info(f"Successfully saved workbook: {safe_path}")
            return True, safe_path, None
            
        elif operation_type == 'validate':
            # Just validate the path and return
            logger.info(f"File path validation successful: {safe_path}")
            return True, safe_path, None
            
        else:
            return False, None, f"Unknown operation type: {operation_type}"
            
    except Exception as e:
        logger.error(f"File operation failed - {operation_type}: {str(e)} (file: {file_path})")
        return False, None, f"Operation failed: {str(e)}"


def safe_open_workbook(file_path: str):
    """
    Safely open an Excel workbook with security validation.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Tuple of (success, workbook, error_message)
    """
    return safe_file_operation('open', file_path)


def safe_save_workbook(workbook, file_path: str):
    """
    Safely save an Excel workbook with path validation.
    
    Args:
        workbook: The openpyxl workbook object
        file_path: Path where to save the file
        
    Returns:
        Tuple of (success, saved_path, error_message)
    """
    return safe_file_operation('save', file_path, workbook=workbook)


def validate_file_path(file_path: str):
    """
    Validate a file path for security.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Tuple of (success, validated_path, error_message)
    """
    return safe_file_operation('validate', file_path)