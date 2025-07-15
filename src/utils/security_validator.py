"""
Comprehensive security validation utilities for ProjectBudgetinator.

This module provides security-focused validation for file operations,
input sanitization, and protection against common vulnerabilities.
"""

import os
import mimetypes
import re
from pathlib import Path
from typing import Optional, List, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Comprehensive security validation for file operations and user input.
    
    Provides protection against:
    - Path traversal attacks
    - Malicious file uploads
    - Invalid file formats
    - Unsafe file paths
    - Code injection attempts
    """

    # Allowed file extensions for Excel files
    ALLOWED_EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    
    # Allowed MIME types for Excel files
    ALLOWED_EXCEL_MIME_TYPES = {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'application/vnd.ms-excel',  # .xls
        'application/vnd.ms-excel.sheet.macroEnabled.12',  # .xlsm
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12',  # .xlsb
        'application/octet-stream'  # Sometimes used for Excel files
    }
    
    # Maximum file size (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Suspicious patterns for path traversal
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',  # Unix-style
        r'\.\.\\',  # Windows-style
        r'%2e%2e%2f',  # URL encoded
        r'%2e%2e%5c',  # URL encoded backslash
        r'\.\.%2f',  # Mixed encoding
        r'\.\.%5c',  # Mixed encoding
    ]
    
    # Suspicious characters in filenames
    SUSPICIOUS_CHARS = ['<', '>', ':', '"', '|', '?', '*', '\x00']
    
    @staticmethod
    def validate_file_path(file_path: str, base_directory: Optional[str] = None) -> str:
        """
        Validate and sanitize file path to prevent path traversal attacks.
        
        Args:
            file_path: The file path to validate
            base_directory: Optional base directory to restrict paths to
            
        Returns:
            Normalized and validated file path
            
        Raises:
            ValueError: If path is invalid or contains traversal attempts
        """
        return SecurityValidator._validate_path_internal(file_path, base_directory)
    
    @staticmethod
    def _validate_path_internal(file_path: str, base_directory: Optional[str] = None) -> str:
        """Internal path validation implementation."""
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Invalid file path: must be a non-empty string")
        
        # Check for null bytes
        if '\x00' in file_path:
            raise ValueError("Invalid file path: contains null bytes")
        
        # Check for suspicious patterns
        for pattern in SecurityValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                raise ValueError("Invalid file path: potential path traversal detected")
        
        # Normalize the path
        try:
            normalized = os.path.normpath(file_path)
        except Exception as e:
            raise ValueError(f"Invalid file path: {str(e)}")
        
        # Check if normalized path contains traversal
        if '..' in normalized:
            raise ValueError("Invalid file path: contains directory traversal")
        
        # Ensure path is absolute if base directory provided
        if base_directory:
            normalized = SecurityValidator._validate_base_directory(normalized, base_directory)
        
        # Additional checks for Windows
        if os.name == 'nt':
            normalized = SecurityValidator._validate_windows_path(normalized)
        
        return normalized
    
    @staticmethod
    def _validate_base_directory(normalized: str, base_directory: str) -> str:
        """Validate path against base directory."""
        try:
            base_path = Path(base_directory).resolve()
            full_path = (base_path / normalized).resolve()
            
            # Ensure the resolved path is within the base directory
            try:
                full_path.relative_to(base_path)
            except ValueError:
                raise ValueError("Invalid file path: outside allowed directory")
            
            return str(full_path)
        except Exception as e:
            raise ValueError(f"Invalid file path: {str(e)}")
    
    @staticmethod
    def _validate_windows_path(normalized: str) -> str:
        """Validate Windows-specific path issues."""
        windows_devices = {
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        filename = Path(normalized).name.upper()
        if filename in windows_devices or any(filename.startswith(f"{dev}.") for dev in windows_devices):
            raise ValueError("Invalid file path: reserved Windows device name")
        
        return normalized
    
    @staticmethod
    def validate_excel_file(file_path: str, check_content: bool = True) -> Tuple[bool, str]:
        """
        Comprehensive validation of Excel files beyond extension checking.
        
        Args:
            file_path: Path to the file to validate
            check_content: Whether to perform deep content validation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return SecurityValidator._validate_excel_internal(file_path, check_content)
    
    @staticmethod
    def _validate_excel_internal(file_path: str, check_content: bool) -> Tuple[bool, str]:
        """Internal Excel file validation implementation."""
        if not file_path:
            return False, "File path is required"
        
        try:
            validated_path = SecurityValidator.validate_file_path(file_path)
            return SecurityValidator._perform_excel_validation(validated_path)
        except Exception as e:
            logger.error("Error validating Excel file: %s", str(e))
            return False, "Validation error"
    
    @staticmethod
    def _perform_excel_validation(validated_path: str) -> Tuple[bool, str]:
        """Perform actual Excel file validation."""
        # Check if file exists
        if not os.path.exists(validated_path):
            return False, "File does not exist"
        
        # Check file size
        file_size = os.path.getsize(validated_path)
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > SecurityValidator.MAX_FILE_SIZE:
            size_mb = file_size / 1024 / 1024
            max_mb = SecurityValidator.MAX_FILE_SIZE / 1024 / 1024
            return False, f"File too large: {size_mb:.1f}MB (max {max_mb:.0f}MB)"
        
        # Check file extension
        file_extension = Path(validated_path).suffix.lower()
        if file_extension not in SecurityValidator.ALLOWED_EXCEL_EXTENSIONS:
            return False, "Invalid file extension"
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(validated_path)
        if mime_type and mime_type not in SecurityValidator.ALLOWED_EXCEL_MIME_TYPES:
            return False, "Invalid MIME type"
        
        # Validate Excel structure
        return SecurityValidator._validate_excel_structure(validated_path)
    
    @staticmethod
    def _validate_excel_structure(validated_path: str) -> Tuple[bool, str]:
        """Validate Excel file structure."""
        try:
            import openpyxl
            with open(validated_path, 'rb') as f:
                openpyxl.load_workbook(f, read_only=True, data_only=True).close()
            return True, ""
        except Exception as e:
            return False, f"Invalid Excel file structure: {str(e)}"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent injection attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove suspicious characters
        for char in SecurityValidator.SUSPICIOUS_CHARS:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        
        # Ensure filename is not empty
        if not filename or filename.startswith('.'):
            filename = f"file_{filename}"
        
        return filename
    
    @staticmethod
    def validate_directory_path(dir_path: str, create_if_missing: bool = False) -> str:
        """
        Validate directory path for safe operations.
        
        Args:
            dir_path: Directory path to validate
            create_if_missing: Whether to create directory if it doesn't exist
            
        Returns:
            Validated directory path
            
        Raises:
            ValueError: If directory path is invalid
        """
        if not dir_path:
            raise ValueError("Directory path is required")
        
        # Validate using file path validation
        validated_path = SecurityValidator.validate_file_path(dir_path)
        
        # Ensure it's a directory
        if os.path.exists(validated_path) and not os.path.isdir(validated_path):
            raise ValueError("Path exists but is not a directory")
        
        # Create directory if requested
        if create_if_missing and not os.path.exists(validated_path):
            try:
                os.makedirs(validated_path, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create directory: {str(e)}")
        
        return validated_path
    
    @staticmethod
    def is_safe_path(path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Quick safety check for file paths.
        
        Args:
            path: File path to check
            allowed_extensions: Optional list of allowed extensions
            
        Returns:
            True if path appears safe
        """
        try:
            SecurityValidator.validate_file_path(path)
            
            if allowed_extensions:
                ext = Path(path).suffix.lower()
                if ext not in [e.lower() for e in allowed_extensions]:
                    return False
            
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get comprehensive file information for security analysis.
        
        Args:
            file_path: Path to analyze
            
        Returns:
            Dictionary with file information
        """
        try:
            validated_path = SecurityValidator.validate_file_path(file_path)
            
            if not os.path.exists(validated_path):
                return {"error": "File does not exist"}
            
            stat = os.stat(validated_path)
            mime_type, _ = mimetypes.guess_type(validated_path)
            
            info = {
                "path": validated_path,
                "size": stat.st_size,
                "mime_type": mime_type,
                "extension": Path(validated_path).suffix.lower(),
                "is_file": os.path.isfile(validated_path),
                "is_directory": os.path.isdir(validated_path),
                "readable": os.access(validated_path, os.R_OK),
                "writable": os.access(validated_path, os.W_OK),
            }
            
            return info
            
        except Exception as e:
            return {"error": str(e)}


class InputSanitizer:
    """
    Input sanitization utilities for user-provided data.
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input to prevent injection attacks.
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except common whitespace
        value = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_numeric_input(value: str, allow_float: bool = True) -> Optional[Union[int, float]]:
        """
        Sanitize and validate numeric input.
        
        Args:
            value: Input string to validate
            allow_float: Whether to allow floating point numbers
            
        Returns:
            Sanitized numeric value or None if invalid
        """
        if not isinstance(value, str):
            return None
        
        # Remove whitespace and common separators
        value = value.strip().replace(',', '').replace(' ', '')
        
        if not value:
            return None
        
        try:
            if allow_float:
                result = float(value)
                # Return as int if it's a whole number
                if result.is_integer():
                    return int(result)
                return result
            else:
                # For integer-only, handle float strings
                float_val = float(value)
                return int(float_val)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None


# Global validator instance for convenience
security_validator = SecurityValidator()
input_sanitizer = InputSanitizer()