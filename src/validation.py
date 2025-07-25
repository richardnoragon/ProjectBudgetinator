"""ProjectBudgetinator Form Validation Module.

This module provides comprehensive form validation utilities for ProjectBudgetinator
with proper handling of zero vs empty value distinctions, which is critical for
Excel workbook data integrity.

The validation system handles:
    - Work package (WP) value validation with zero/empty distinction
    - Financial value validation with negative value support
    - Required and optional text field validation
    - Partner form validation with comprehensive error reporting
    - Value formatting for Excel output and GUI display
    - Input sanitization through security validators

Functions:
    validate_wp_value: Validate work package values with zero/empty distinction
    validate_financial_value: Validate financial values with negative support
    validate_required_text: Validate required text fields with length constraints
    validate_optional_text: Validate optional text fields
    format_value_for_excel: Format values for Excel output preserving distinctions
    format_value_for_display: Format values for GUI display

Classes:
    FormValidator: Comprehensive validator for partner detail forms

Key Design Principles:
    - Empty strings remain None (empty Excel cells)
    - "0" or "0.0" becomes 0.0 (explicit zero values)
    - All validation preserves the zero vs empty distinction
    - Security validation is applied to all inputs

Example:
    Validating work package values:
    
        is_valid, value, error = validate_wp_value("0")
        # Returns: (True, 0.0, None) - explicit zero
        
        is_valid, value, error = validate_wp_value("")
        # Returns: (True, None, None) - empty field

Note:
    The zero vs empty distinction is critical for Excel data integrity.
    Empty fields should remain empty, while explicit zeros should be preserved.
"""

from typing import Any, Dict, Optional, Union
from tkinter import messagebox
from utils.security_validator import InputSanitizer


def validate_wp_value(value: str) -> tuple[bool, Optional[float], Optional[str]]:
    """Validate a work package value with proper zero vs empty distinction.
    
    This function validates work package (WP) values while maintaining the critical
    distinction between empty fields and explicit zero values. This distinction is
    essential for Excel data integrity where empty cells and zero values have
    different meanings.
    
    Args:
        value (str): The string value to validate from user input.
    
    Returns:
        tuple[bool, Optional[float], Optional[str]]: A tuple containing:
            - is_valid (bool): True if validation passed, False otherwise
            - converted_value (Optional[float]): The converted numeric value or None
            - error_message (Optional[str]): Error message if validation failed
    
    Raises:
        None: This function handles all exceptions internally and returns error states.
    
    Examples:
        Validating different WP values:
        
            # Empty field (should remain empty)
            is_valid, value, error = validate_wp_value("")
            # Returns: (True, None, None)
            
            # Explicit zero
            is_valid, value, error = validate_wp_value("0")
            # Returns: (True, 0.0, None)
            
            # Valid positive value
            is_valid, value, error = validate_wp_value("1500.50")
            # Returns: (True, 1500.5, None)
            
            # Invalid input
            is_valid, value, error = validate_wp_value("abc")
            # Returns: (False, None, "WP value must be a valid number")
    
    Note:
        The zero vs empty distinction is critical for Excel data integrity:
        - Empty strings become None (empty Excel cells)
        - "0" or "0.0" becomes 0.0 (explicit zero values)
        - Negative values are rejected for work package fields
    """
    # Sanitize input
    sanitized = InputSanitizer.sanitize_string(value)
    
    # CRITICAL: Distinguish between empty and zero
    if not sanitized:
        # Empty input should remain empty (None), not become 0.0
        return True, None, None
        
    # Validate as numeric
    numeric_value = InputSanitizer.sanitize_numeric_input(sanitized)
    if numeric_value is None:
        return False, None, "WP value must be a valid number"
    
    if numeric_value < 0:
        return False, None, "WP value cannot be negative"
    
    return True, numeric_value, None


def validate_financial_value(value: str) -> tuple[bool, Optional[float], Optional[str]]:
    """
    Validate a financial value with proper zero vs empty distinction.
    
    Args:
        value: The string value to validate
        
    Returns:
        Tuple of (is_valid, converted_value, error_message)
        
    Note:
        - Empty/whitespace strings return (True, None, None) to preserve empty state
        - "0" or "0.0" returns (True, 0.0, None) to preserve explicit zero
        - Invalid numbers return (False, None, error_message)
    """
    # Sanitize input
    sanitized = InputSanitizer.sanitize_string(value)
    
    # CRITICAL: Distinguish between empty and zero
    if not sanitized:
        # Empty input should remain empty (None), not become 0.0
        return True, None, None
        
    # Validate as numeric
    numeric_value = InputSanitizer.sanitize_numeric_input(sanitized)
    if numeric_value is None:
        return False, None, "Financial value must be a valid number"
    
    # Financial values can be negative (e.g., income generated)
    return True, numeric_value, None


def validate_required_text(
    value: str,
    field_name: str,
    min_length: int = 1,
    max_length: int = 100
) -> tuple[bool, Optional[str]]:
    """
    Validate a required text field.
    
    Args:
        value: The string value to validate
        field_name: Name of the field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Sanitize input
    sanitized = InputSanitizer.sanitize_string(value, max_length=max_length)
    
    if not sanitized:
        return False, f"{field_name} is required"
    
    if len(sanitized) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    return True, sanitized


def validate_optional_text(
    value: str,
    field_name: str,
    max_length: int = 100
) -> tuple[bool, Optional[str]]:
    """
    Validate an optional text field.
    
    Args:
        value: The string value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, sanitized_value_or_error)
    """
    # Sanitize input
    sanitized = InputSanitizer.sanitize_string(value, max_length=max_length)
    
    # Optional fields can be empty
    return True, sanitized


class FormValidator:
    """Comprehensive validator for partner detail forms with zero vs empty distinction.
    
    This class provides static methods for validating complex partner forms while
    maintaining the critical distinction between empty fields (None) and explicit
    zero values (0.0). This distinction is essential for Excel data integrity.
    
    The validator handles:
        - Required text fields with length constraints
        - Work package (WP) fields with numeric validation
        - Financial fields with negative value support
        - Comprehensive error collection and reporting
        - Proper data type conversion and preservation
    
    Key Design Principles:
        - Empty strings become None (empty Excel cells)
        - "0" or "0.0" becomes 0.0 (explicit zero values)
        - All validation preserves the zero vs empty distinction
        - Security validation through InputSanitizer integration
        - Comprehensive error reporting with field-specific messages
    
    Methods:
        validate_partner_form: Validate all fields in a partner form
    
    Example:
        Validating a partner form:
        
            form_data = {
                'partner_identification_code': 'P001',
                'name_of_beneficiary': 'Example Corp',
                'wp1': '1500.0',
                'wp2': '',  # Empty field
                'wp3': '0',  # Explicit zero
                'sum_travel': '2500.50'
            }
            
            is_valid, errors = FormValidator.validate_partner_form(form_data)
            if is_valid:
                # form_data now contains properly converted values
                # wp2 = None, wp3 = 0.0
                pass
            else:
                # Handle validation errors
                for field, error in errors.items():
                    print(f"{field}: {error}")
    
    Note:
        The validator modifies the input data dictionary in-place, converting
        string values to their appropriate types while preserving the critical
        zero vs empty distinction required for Excel data integrity.
    """
    
    @staticmethod
    def validate_partner_form(data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate all fields in the partner form with proper zero vs empty distinction.
        
        Args:
            data: Dictionary of form field values
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: Dict[str, str] = {}
        
        # Validate required fields
        required_fields = {
            "partner_identification_code": "Partner ID",
            "name_of_beneficiary": "Beneficiary Name",
            "country": "Country"
        }
        
        for field, label in required_fields.items():
            is_valid, result = validate_required_text(
                str(data.get(field, "")),
                label
            )
            if not is_valid and result is not None:
                errors[field] = result
        
        # Validate WP fields - CRITICAL: preserve zero vs empty distinction
        for i in range(1, 16):
            field = f"wp{i}"
            value = str(data.get(field, ""))
            is_valid, converted_value, error = validate_wp_value(value)
            if not is_valid and error is not None:
                errors[field] = error
            elif is_valid:
                # Store the properly converted value back to data
                # None means empty, 0.0 means explicit zero
                data[field] = converted_value
        
        # Validate financial fields - CRITICAL: preserve zero vs empty distinction
        financial_fields = [
            'sum_subcontractor_1', 'sum_subcontractor_2', 'sum_travel',
            'sum_equipment', 'sum_other', 'sum_financial_support',
            'sum_internal_goods', 'sum_income_generated',
            'sum_financial_contributions', 'sum_own_resources'
        ]
        
        for field in financial_fields:
            if field in data:
                value = str(data.get(field, ""))
                is_valid, converted_value, error = validate_financial_value(value)
                if not is_valid and error is not None:
                    errors[field] = error
                elif is_valid:
                    # Store the properly converted value back to data
                    # None means empty, numeric value means explicit entry
                    data[field] = converted_value
        
        return len(errors) == 0, errors


def format_value_for_excel(value: Any) -> Any:
    """
    Format a value for Excel output, preserving zero vs empty distinction.
    
    Args:
        value: The value to format
        
    Returns:
        Formatted value for Excel (None for empty, numeric for values)
    """
    if value is None:
        return None  # Empty cell in Excel
    elif isinstance(value, (int, float)):
        return float(value)  # Numeric value in Excel
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None  # Empty string becomes empty cell
        else:
            return stripped  # Non-empty string
    else:
        return value


def format_value_for_display(value: Any) -> str:
    """
    Format a value for display in GUI, preserving zero vs empty distinction.
    
    Args:
        value: The value to format
        
    Returns:
        String representation for GUI display
    """
    if value is None:
        return ""  # Empty field in GUI
    elif isinstance(value, (int, float)):
        if value == 0:
            return "0"  # Explicit zero display
        else:
            return str(value)
    else:
        return str(value)
