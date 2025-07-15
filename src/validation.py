"""Form validation utilities for ProjectBudgetinator."""

from typing import Any, Dict, Optional, Union
from tkinter import messagebox
from utils.security_validator import InputSanitizer


def validate_wp_value(value: str) -> tuple[bool, Optional[float], Optional[str]]:
    """
    Validate a work package value.
    
    Args:
        value: The string value to validate
        
    Returns:
        Tuple of (is_valid, converted_value, error_message)
    """
    # Sanitize input
    sanitized = InputSanitizer.sanitize_string(value)
    
    if not sanitized:
        return True, 0.0, None
        
    # Validate as numeric
    numeric_value = InputSanitizer.sanitize_numeric_input(sanitized)
    if numeric_value is None:
        return False, None, "WP value must be a valid number"
    
    if numeric_value < 0:
        return False, None, "WP value cannot be negative"
    
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


class FormValidator:
    """Validator for partner detail forms."""
    
    @staticmethod
    def validate_partner_form(data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate all fields in the partner form.
        
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
        
        # Validate WP fields
        for i in range(1, 16):
            field = f"wp{i}"
            value = str(data.get(field, ""))
            is_valid, _, error = validate_wp_value(value)
            if not is_valid and error is not None:
                errors[field] = error
        
        return len(errors) == 0, errors
