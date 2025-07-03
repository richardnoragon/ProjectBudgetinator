"""Unit tests for validation logic."""

import unittest
from validation import validate_wp_value, validate_required_text, FormValidator


class TestValidation(unittest.TestCase):
    """Test cases for validation functions."""
    
    def test_wp_value_validation(self):
        """Test work package value validation."""
        # Test valid cases
        self.assertEqual(validate_wp_value(""), (True, 0.0, None))
        self.assertEqual(validate_wp_value("0"), (True, 0.0, None))
        self.assertEqual(validate_wp_value("42.5"), (True, 42.5, None))
        
        # Test invalid cases
        self.assertEqual(
            validate_wp_value("-1")[0:2],
            (False, None)
        )
        self.assertEqual(
            validate_wp_value("abc")[0:2],
            (False, None)
        )
    
    def test_required_text_validation(self):
        """Test required text field validation."""
        # Test valid cases
        self.assertEqual(
            validate_required_text("Test", "Field Name"),
            (True, None)
        )
        
        # Test invalid cases
        self.assertEqual(
            validate_required_text("", "Field Name")[0],
            False
        )
        self.assertEqual(
            validate_required_text("  ", "Field Name")[0],
            False
        )
        
        # Test length constraints
        self.assertEqual(
            validate_required_text(
                "a",
                "Field Name",
                min_length=2
            )[0],
            False
        )
        self.assertEqual(
            validate_required_text(
                "toolong",
                "Field Name",
                max_length=5
            )[0],
            False
        )


class TestFormValidator(unittest.TestCase):
    """Test cases for the FormValidator class."""
    
    def test_partner_form_validation(self):
        """Test complete partner form validation."""
        valid_data = {
            "partner_identification_code": "TEST123",
            "name_of_beneficiary": "Test Company",
            "country": "Test Country",
            "wp1": "10.5",
            "wp2": "0",
            "wp3": "",  # Empty should be valid
        }
        
        is_valid, errors = FormValidator.validate_partner_form(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test with invalid data
        invalid_data = {
            "partner_identification_code": "",  # Required field missing
            "name_of_beneficiary": "Test Company",
            "country": "Test Country",
            "wp1": "-1",  # Invalid negative value
        }
        
        is_valid, errors = FormValidator.validate_partner_form(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("partner_identification_code", errors)
        self.assertIn("wp1", errors)


if __name__ == '__main__':
    unittest.main()
