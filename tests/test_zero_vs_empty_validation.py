"""
Test suite for zero vs empty value handling in ProjectBudgetinator.

This test suite ensures that the application properly distinguishes between
user input of "0" (explicit zero) versus empty/null values throughout the system.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation import (
    validate_wp_value,
    validate_financial_value,
    validate_required_text,
    validate_optional_text,
    FormValidator,
    format_value_for_excel,
    format_value_for_display
)


class TestZeroVsEmptyValidation(unittest.TestCase):
    """Test zero vs empty value validation functions."""
    
    def test_validate_wp_value_empty_input(self):
        """Test that empty WP input returns None (not zero)."""
        test_cases = ["", "   ", "\t", "\n", "  \t  \n  "]
        
        for empty_input in test_cases:
            with self.subTest(input=repr(empty_input)):
                is_valid, value, error = validate_wp_value(empty_input)
                self.assertTrue(is_valid, f"Empty input should be valid: {repr(empty_input)}")
                self.assertIsNone(value, f"Empty input should return None, got {value}")
                self.assertIsNone(error, f"Empty input should not have error: {error}")
    
    def test_validate_wp_value_explicit_zero(self):
        """Test that explicit zero input returns 0.0 (not None)."""
        test_cases = ["0", "0.0", "0.00", "  0  ", "  0.0  "]
        
        for zero_input in test_cases:
            with self.subTest(input=repr(zero_input)):
                is_valid, value, error = validate_wp_value(zero_input)
                self.assertTrue(is_valid, f"Zero input should be valid: {repr(zero_input)}")
                self.assertEqual(value, 0.0, f"Zero input should return 0.0, got {value}")
                self.assertIsNone(error, f"Zero input should not have error: {error}")
    
    def test_validate_wp_value_positive_numbers(self):
        """Test that positive numbers are handled correctly."""
        test_cases = [
            ("1", 1.0),
            ("1.5", 1.5),
            ("100", 100.0),
            ("123.45", 123.45),
            ("  42.0  ", 42.0)
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=repr(input_str)):
                is_valid, value, error = validate_wp_value(input_str)
                self.assertTrue(is_valid, f"Valid number should be valid: {repr(input_str)}")
                self.assertEqual(value, expected, f"Expected {expected}, got {value}")
                self.assertIsNone(error, f"Valid number should not have error: {error}")
    
    def test_validate_wp_value_negative_numbers(self):
        """Test that negative numbers are rejected for WP values."""
        test_cases = ["-1", "-0.5", "-100", "  -42  "]
        
        for negative_input in test_cases:
            with self.subTest(input=repr(negative_input)):
                is_valid, value, error = validate_wp_value(negative_input)
                self.assertFalse(is_valid, f"Negative input should be invalid: {repr(negative_input)}")
                self.assertIsNone(value, f"Invalid input should return None value")
                self.assertIsNotNone(error, f"Invalid input should have error message")
                self.assertIn("negative", error.lower(), f"Error should mention negative: {error}")
    
    def test_validate_wp_value_invalid_input(self):
        """Test that invalid input is rejected."""
        test_cases = ["abc", "1.2.3", "1a", "a1", "€100", "$50"]
        
        for invalid_input in test_cases:
            with self.subTest(input=repr(invalid_input)):
                is_valid, value, error = validate_wp_value(invalid_input)
                self.assertFalse(is_valid, f"Invalid input should be invalid: {repr(invalid_input)}")
                self.assertIsNone(value, f"Invalid input should return None value")
                self.assertIsNotNone(error, f"Invalid input should have error message")
    
    def test_validate_financial_value_empty_input(self):
        """Test that empty financial input returns None (not zero)."""
        test_cases = ["", "   ", "\t", "\n"]
        
        for empty_input in test_cases:
            with self.subTest(input=repr(empty_input)):
                is_valid, value, error = validate_financial_value(empty_input)
                self.assertTrue(is_valid, f"Empty input should be valid: {repr(empty_input)}")
                self.assertIsNone(value, f"Empty input should return None, got {value}")
                self.assertIsNone(error, f"Empty input should not have error: {error}")
    
    def test_validate_financial_value_explicit_zero(self):
        """Test that explicit zero financial input returns 0.0."""
        test_cases = ["0", "0.0", "-0", "-0.0"]
        
        for zero_input in test_cases:
            with self.subTest(input=repr(zero_input)):
                is_valid, value, error = validate_financial_value(zero_input)
                self.assertTrue(is_valid, f"Zero input should be valid: {repr(zero_input)}")
                self.assertEqual(value, 0.0, f"Zero input should return 0.0, got {value}")
                self.assertIsNone(error, f"Zero input should not have error: {error}")
    
    def test_validate_financial_value_negative_allowed(self):
        """Test that negative financial values are allowed (unlike WP values)."""
        test_cases = [
            ("-1", -1.0),
            ("-100.50", -100.50),
            ("  -42  ", -42.0)
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=repr(input_str)):
                is_valid, value, error = validate_financial_value(input_str)
                self.assertTrue(is_valid, f"Negative financial value should be valid: {repr(input_str)}")
                self.assertEqual(value, expected, f"Expected {expected}, got {value}")
                self.assertIsNone(error, f"Valid negative should not have error: {error}")


class TestFormValidator(unittest.TestCase):
    """Test the FormValidator class with zero vs empty handling."""
    
    def test_partner_form_validation_empty_wp_fields(self):
        """Test that empty WP fields are preserved as None."""
        data = {
            "partner_identification_code": "TEST123",
            "name_of_beneficiary": "Test Partner",
            "country": "Test Country",
            "wp1": "",  # Empty
            "wp2": "0",  # Explicit zero
            "wp3": "100.50",  # Positive value
            "wp4": "   ",  # Whitespace only
        }
        
        is_valid, errors = FormValidator.validate_partner_form(data)
        
        self.assertTrue(is_valid, f"Form should be valid, errors: {errors}")
        self.assertIsNone(data["wp1"], "Empty WP1 should be None")
        self.assertEqual(data["wp2"], 0.0, "Explicit zero WP2 should be 0.0")
        self.assertEqual(data["wp3"], 100.50, "WP3 should be 100.50")
        self.assertIsNone(data["wp4"], "Whitespace-only WP4 should be None")
    
    def test_partner_form_validation_financial_fields(self):
        """Test that financial fields preserve zero vs empty distinction."""
        data = {
            "partner_identification_code": "TEST123",
            "name_of_beneficiary": "Test Partner",
            "country": "Test Country",
            "sum_travel": "",  # Empty
            "sum_equipment": "0",  # Explicit zero
            "sum_other": "-50.25",  # Negative (allowed for financial)
            "sum_financial_support": "   ",  # Whitespace only
        }
        
        is_valid, errors = FormValidator.validate_partner_form(data)
        
        self.assertTrue(is_valid, f"Form should be valid, errors: {errors}")
        self.assertIsNone(data["sum_travel"], "Empty travel sum should be None")
        self.assertEqual(data["sum_equipment"], 0.0, "Explicit zero equipment should be 0.0")
        self.assertEqual(data["sum_other"], -50.25, "Negative other sum should be -50.25")
        self.assertIsNone(data["sum_financial_support"], "Whitespace-only financial support should be None")


class TestFormatFunctions(unittest.TestCase):
    """Test value formatting functions."""
    
    def test_format_value_for_excel(self):
        """Test Excel formatting preserves zero vs empty distinction."""
        test_cases = [
            (None, None),  # Empty -> Empty cell
            (0, 0.0),      # Zero -> Zero value
            (0.0, 0.0),    # Zero float -> Zero value
            (42, 42.0),    # Integer -> Float
            (42.5, 42.5),  # Float -> Float
            ("", None),    # Empty string -> Empty cell
            ("  ", None),  # Whitespace -> Empty cell
            ("text", "text"),  # Text -> Text
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=repr(input_val)):
                result = format_value_for_excel(input_val)
                self.assertEqual(result, expected, f"Expected {expected}, got {result}")
    
    def test_format_value_for_display(self):
        """Test GUI display formatting preserves zero vs empty distinction."""
        test_cases = [
            (None, ""),     # Empty -> Empty field
            (0, "0"),       # Zero -> "0"
            (0.0, "0"),     # Zero float -> "0"
            (42, "42"),     # Integer -> String
            (42.5, "42.5"), # Float -> String
            ("text", "text"),  # Text -> Text
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=repr(input_val)):
                result = format_value_for_display(input_val)
                self.assertEqual(result, expected, f"Expected {expected}, got {result}")


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios for zero vs empty handling."""
    
    def test_data_round_trip_scenario(self):
        """Test complete data round-trip: Form -> Validation -> Excel -> Display."""
        # Simulate form data with mix of empty and zero values
        form_data = {
            "partner_identification_code": "P123",
            "name_of_beneficiary": "Test University",
            "country": "Germany",
            "wp1": "",      # Empty
            "wp2": "0",     # Explicit zero
            "wp3": "150.75", # Value
            "sum_travel": "",     # Empty
            "sum_equipment": "0", # Explicit zero
            "sum_other": "200.00", # Value
        }
        
        # Step 1: Validate form data
        is_valid, errors = FormValidator.validate_partner_form(form_data)
        self.assertTrue(is_valid, f"Form validation failed: {errors}")
        
        # Step 2: Check internal representation
        self.assertIsNone(form_data["wp1"], "WP1 should be None (empty)")
        self.assertEqual(form_data["wp2"], 0.0, "WP2 should be 0.0 (explicit zero)")
        self.assertEqual(form_data["wp3"], 150.75, "WP3 should be 150.75")
        
        # Step 3: Format for Excel
        excel_values = {
            key: format_value_for_excel(value) 
            for key, value in form_data.items()
        }
        
        self.assertIsNone(excel_values["wp1"], "Excel WP1 should be None (empty cell)")
        self.assertEqual(excel_values["wp2"], 0.0, "Excel WP2 should be 0.0")
        self.assertEqual(excel_values["wp3"], 150.75, "Excel WP3 should be 150.75")
        
        # Step 4: Format for display (simulating loading back from Excel)
        display_values = {
            key: format_value_for_display(value) 
            for key, value in excel_values.items()
        }
        
        self.assertEqual(display_values["wp1"], "", "Display WP1 should be empty")
        self.assertEqual(display_values["wp2"], "0", "Display WP2 should be '0'")
        self.assertEqual(display_values["wp3"], "150.75", "Display WP3 should be '150.75'")
    
    def test_edge_cases(self):
        """Test edge cases for zero vs empty handling."""
        edge_cases = [
            ("0.000", 0.0),    # Multiple decimal zeros
            ("00", 0.0),       # Leading zeros
            ("0.", 0.0),       # Trailing decimal
            (".0", 0.0),       # Leading decimal
            ("000.000", 0.0),  # Multiple leading/trailing zeros
        ]
        
        for input_str, expected in edge_cases:
            with self.subTest(input=repr(input_str)):
                is_valid, value, error = validate_wp_value(input_str)
                self.assertTrue(is_valid, f"Should be valid: {repr(input_str)}")
                self.assertEqual(value, expected, f"Expected {expected}, got {value}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)