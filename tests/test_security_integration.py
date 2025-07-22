#!/usr/bin/env python3
"""
Comprehensive integration test for security validation implementation.

This test verifies that the security validation is properly integrated
throughout the ProjectBudgetinator application.
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.security_validator import SecurityValidator, InputSanitizer
from validation import FormValidator, validate_wp_value, validate_required_text
from handlers.file_handler import open_file_direct, save_file_direct
import openpyxl


class TestSecurityValidationIntegration(unittest.TestCase):
    """Test security validation integration across the application."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_excel_file = os.path.join(self.temp_dir, "test.xlsx")
        
        # Create a valid test Excel file
        wb = openpyxl.Workbook()
        wb.save(self.test_excel_file)
        wb.close()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_security_validator_path_validation(self):
        """Test path validation functionality."""
        # Test valid path
        safe_path = SecurityValidator.validate_file_path(self.test_excel_file)
        self.assertEqual(safe_path, self.test_excel_file)
        
        # Test path traversal protection
        with self.assertRaises(ValueError):
            SecurityValidator.validate_file_path("../../../etc/passwd")
        
        # Test null byte protection
        with self.assertRaises(ValueError):
            SecurityValidator.validate_file_path("test\x00.xlsx")
    
    def test_security_validator_excel_validation(self):
        """Test Excel file validation."""
        # Test valid Excel file
        is_valid, error = SecurityValidator.validate_excel_file(self.test_excel_file)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Test non-existent file
        is_valid, error = SecurityValidator.validate_excel_file("nonexistent.xlsx")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)
        
        # Test invalid file type
        text_file = os.path.join(self.temp_dir, "test.txt")
        with open(text_file, 'w') as f:
            f.write("test")
        
        is_valid, error = SecurityValidator.validate_excel_file(text_file)
        self.assertFalse(is_valid)
        self.assertIn("Invalid", error)
    
    def test_security_validator_filename_sanitization(self):
        """Test filename sanitization."""
        # Test dangerous characters
        clean_name = SecurityValidator.sanitize_filename("test<script>.xlsx")
        self.assertNotIn("<", clean_name)
        self.assertNotIn(">", clean_name)
        
        # Test null bytes
        clean_name = SecurityValidator.sanitize_filename("test\x00.xlsx")
        self.assertNotIn("\x00", clean_name)
        
        # Test path separators
        clean_name = SecurityValidator.sanitize_filename("../test.xlsx")
        self.assertNotIn("..", clean_name)
        self.assertNotIn("/", clean_name)
    
    def test_input_sanitizer_string_sanitization(self):
        """Test string input sanitization."""
        # Test null bytes
        clean_input = InputSanitizer.sanitize_string("test\x00input")
        self.assertNotIn("\x00", clean_input)
        
        # Test control characters
        clean_input = InputSanitizer.sanitize_string("test\x01\x02input")
        self.assertNotIn("\x01", clean_input)
        self.assertNotIn("\x02", clean_input)
        
        # Test length limiting
        long_input = "a" * 2000
        clean_input = InputSanitizer.sanitize_string(long_input, max_length=100)
        self.assertEqual(len(clean_input), 100)
    
    def test_input_sanitizer_numeric_validation(self):
        """Test numeric input sanitization."""
        # Test valid numbers
        result = InputSanitizer.sanitize_numeric_input("123.45")
        self.assertEqual(result, 123.45)
        
        result = InputSanitizer.sanitize_numeric_input("123")
        self.assertEqual(result, 123)
        
        # Test invalid input
        result = InputSanitizer.sanitize_numeric_input("abc")
        self.assertIsNone(result)
        
        # Test with separators
        result = InputSanitizer.sanitize_numeric_input("1,234.56")
        self.assertEqual(result, 1234.56)
    
    def test_form_validation_integration(self):
        """Test form validation with security integration."""
        # Test partner form validation
        valid_data = {
            "partner_identification_code": "TEST001",
            "name_of_beneficiary": "Test Organization",
            "country": "Germany",
            "wp1": "1000.50",
            "wp2": "2000.75"
        }
        
        is_valid, errors = FormValidator.validate_partner_form(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test with malicious input
        malicious_data = {
            "partner_identification_code": "TEST<script>alert('xss')</script>",
            "name_of_beneficiary": "Test\x00Organization",
            "country": "Germany",
            "wp1": "invalid_number",
            "wp2": "2000.75"
        }
        
        is_valid, errors = FormValidator.validate_partner_form(malicious_data)
        # Should still be valid after sanitization, but values should be cleaned
        self.assertTrue(is_valid)
    
    def test_wp_value_validation(self):
        """Test work package value validation."""
        # Test valid values
        is_valid, value, error = validate_wp_value("1000.50")
        self.assertTrue(is_valid)
        self.assertEqual(value, 1000.50)
        self.assertIsNone(error)
        
        # Test empty value
        is_valid, value, error = validate_wp_value("")
        self.assertTrue(is_valid)
        self.assertEqual(value, 0.0)
        self.assertIsNone(error)
        
        # Test invalid value
        is_valid, value, error = validate_wp_value("invalid")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIsNotNone(error)
        
        # Test negative value
        is_valid, value, error = validate_wp_value("-100")
        self.assertFalse(is_valid)
        self.assertIsNone(value)
        self.assertIsNotNone(error)
        
        # Test malicious input
        is_valid, value, error = validate_wp_value("100<script>")
        self.assertFalse(is_valid)  # Should fail after sanitization
    
    def test_required_text_validation(self):
        """Test required text field validation."""
        # Test valid text
        is_valid, result = validate_required_text("Valid Text", "Test Field")
        self.assertTrue(is_valid)
        self.assertEqual(result, "Valid Text")
        
        # Test empty text
        is_valid, result = validate_required_text("", "Test Field")
        self.assertFalse(is_valid)
        self.assertIn("required", result)
        
        # Test text with malicious content
        is_valid, result = validate_required_text("Text\x00with\x01control", "Test Field")
        self.assertTrue(is_valid)  # Should be valid after sanitization
        self.assertNotIn("\x00", result)
        self.assertNotIn("\x01", result)
        
        # Test overly long text
        long_text = "a" * 200
        is_valid, result = validate_required_text(long_text, "Test Field", max_length=50)
        self.assertTrue(is_valid)
        self.assertEqual(len(result), 50)
    
    def test_file_operations_security(self):
        """Test file operations with security validation."""
        # Test opening a valid file
        workbook, filepath = open_file_direct()
        # This will return None, None since no file dialog interaction
        # but the function should not crash
        self.assertIsNone(workbook)
        self.assertIsNone(filepath)
        
        # Test saving with invalid path (would be caught by security validation)
        wb = openpyxl.Workbook()
        try:
            # This should work with a valid path
            result = save_file_direct(wb, self.test_excel_file)
            # Function returns None when no dialog interaction
            self.assertIsNone(result)
        finally:
            wb.close()
    
    def test_directory_validation(self):
        """Test directory path validation."""
        # Test valid directory
        safe_dir = SecurityValidator.validate_directory_path(self.temp_dir)
        self.assertEqual(safe_dir, self.temp_dir)
        
        # Test path traversal in directory
        with self.assertRaises(ValueError):
            SecurityValidator.validate_directory_path("../../../etc")
        
        # Test creating missing directory
        new_dir = os.path.join(self.temp_dir, "new_subdir")
        safe_dir = SecurityValidator.validate_directory_path(new_dir, create_if_missing=True)
        self.assertTrue(os.path.exists(safe_dir))
    
    def test_file_info_security(self):
        """Test file information gathering with security."""
        # Test valid file
        info = SecurityValidator.get_file_info(self.test_excel_file)
        self.assertNotIn("error", info)
        self.assertEqual(info["path"], self.test_excel_file)
        self.assertTrue(info["is_file"])
        
        # Test invalid path
        info = SecurityValidator.get_file_info("../../../etc/passwd")
        self.assertIn("error", info)
    
    def test_email_validation(self):
        """Test email validation functionality."""
        # Test valid emails
        self.assertTrue(InputSanitizer.validate_email("test@example.com"))
        self.assertTrue(InputSanitizer.validate_email("user.name+tag@domain.co.uk"))
        
        # Test invalid emails
        self.assertFalse(InputSanitizer.validate_email("invalid-email"))
        self.assertFalse(InputSanitizer.validate_email("test@"))
        self.assertFalse(InputSanitizer.validate_email("@domain.com"))
        
        # Test malicious input
        self.assertFalse(InputSanitizer.validate_email("test\x00@example.com"))
        self.assertFalse(InputSanitizer.validate_email("test<script>@example.com"))


def run_security_integration_tests():
    """Run all security integration tests."""
    print("Running Security Validation Integration Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurityValidationIntegration)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    success = run_security_integration_tests()
    sys.exit(0 if success else 1)