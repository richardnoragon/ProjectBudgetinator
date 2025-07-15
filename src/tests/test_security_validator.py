"""
Comprehensive tests for security validation functionality.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.security_validator import SecurityValidator, InputSanitizer


class TestSecurityValidator(unittest.TestCase):
    """Test cases for SecurityValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.xlsx')
        
        # Create a dummy test file
        with open(self.test_file, 'wb') as f:
            f.write(b'dummy excel content')
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.remove(self.test_file)
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def test_validate_file_path_valid(self):
        """Test valid file path validation."""
        valid_paths = [
            'test.xlsx',
            'folder/test.xlsx',
            'test_file.xlsx',
            'test-file.xlsx',
            'test file.xlsx'
        ]
        
        for path in valid_paths:
            result = SecurityValidator.validate_file_path(path)
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)
    
    def test_validate_file_path_traversal(self):
        """Test path traversal attack prevention."""
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '%2e%2e%2fetc%2fpasswd',
            '..\\..\\config.txt',
            'folder/../../../etc/passwd'
        ]
        
        for path in malicious_paths:
            with self.assertRaises(ValueError) as cm:
                SecurityValidator.validate_file_path(path)
            self.assertIn('path traversal', str(cm.exception).lower())
    
    def test_validate_file_path_null_bytes(self):
        """Test null byte injection prevention."""
        with self.assertRaises(ValueError):
            SecurityValidator.validate_file_path('test\x00file.xlsx')
    
    def test_validate_file_path_empty(self):
        """Test empty path handling."""
        with self.assertRaises(ValueError):
            SecurityValidator.validate_file_path('')
        
        with self.assertRaises(ValueError):
            SecurityValidator.validate_file_path(None)
    
    def test_validate_excel_file_valid(self):
        """Test valid Excel file validation."""
        # Test with actual file
        is_valid, error = SecurityValidator.validate_excel_file(self.test_file)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(error, str)
    
    def test_validate_excel_file_nonexistent(self):
        """Test non-existent file handling."""
        is_valid, error = SecurityValidator.validate_excel_file('nonexistent.xlsx')
        self.assertFalse(is_valid)
        self.assertIn('does not exist', error.lower())
    
    def test_validate_excel_file_invalid_extension(self):
        """Test invalid file extension handling."""
        invalid_file = os.path.join(self.temp_dir, 'test.txt')
        with open(invalid_file, 'w') as f:
            f.write('not excel')
        
        is_valid, error = SecurityValidator.validate_excel_file(invalid_file)
        self.assertFalse(is_valid)
        self.assertIn('invalid file extension', error.lower())
        
        try:
            os.remove(invalid_file)
        except OSError:
            pass
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ('test<file>.xlsx', 'test_file_.xlsx'),
            ('test:file.xlsx', 'test_file.xlsx'),
            ('test|file.xlsx', 'test_file.xlsx'),
            ('test\x00file.xlsx', 'testfile.xlsx'),
            ('normal_file.xlsx', 'normal_file.xlsx'),
            ('', 'unnamed_file')
        ]
        
        for input_name, expected_pattern in test_cases:
            result = SecurityValidator.sanitize_filename(input_name)
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)
            # Check that dangerous characters are removed
            for char in '<>:|?*\x00':
                self.assertNotIn(char, result)
    
    def test_validate_directory_path(self):
        """Test directory path validation."""
        # Test existing directory
        result = SecurityValidator.validate_directory_path(self.temp_dir)
        self.assertEqual(result, self.temp_dir)
        
        # Test non-existent directory with create
        new_dir = os.path.join(self.temp_dir, 'new_folder')
        result = SecurityValidator.validate_directory_path(new_dir, create_if_missing=True)
        self.assertTrue(os.path.exists(result))
        
        # Test path traversal in directory
        with self.assertRaises(ValueError):
            SecurityValidator.validate_directory_path('../../../etc')
    
    def test_is_safe_path(self):
        """Test safe path checking."""
        self.assertTrue(SecurityValidator.is_safe_path('test.xlsx'))
        self.assertFalse(SecurityValidator.is_safe_path('../../../etc/passwd'))
        self.assertTrue(SecurityValidator.is_safe_path('test.xlsx', ['.xlsx']))
        self.assertFalse(SecurityValidator.is_safe_path('test.txt', ['.xlsx']))
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        info = SecurityValidator.get_file_info(self.test_file)
        
        self.assertIsInstance(info, dict)
        self.assertIn('path', info)
        self.assertIn('size', info)
        self.assertIn('extension', info)
        self.assertEqual(info['extension'], '.xlsx')
        self.assertTrue(info['is_file'])
        self.assertFalse(info['is_directory'])


class TestInputSanitizer(unittest.TestCase):
    """Test cases for InputSanitizer class."""
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        test_cases = [
            ('hello world', 'hello world'),
            ('test\x00input', 'testinput'),
            ('test<script>alert("xss")</script>', 'testscriptalert("xss")/script'),
            ('normal text 123', 'normal text 123'),
            ('', ''),
            ('   spaced   ', 'spaced')
        ]
        
        for input_str, expected_pattern in test_cases:
            result = InputSanitizer.sanitize_string(input_str)
            self.assertIsInstance(result, str)
            self.assertNotIn('\x00', result)
    
    def test_sanitize_string_max_length(self):
        """Test string length limiting."""
        long_string = 'a' * 2000
        result = InputSanitizer.sanitize_string(long_string, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_sanitize_numeric_input(self):
        """Test numeric input sanitization."""
        test_cases = [
            ('123', 123),
            ('123.45', 123.45),
            ('1,234.56', 1234.56),
            ('  123  ', 123),
            ('abc', None),
            ('', None),
            ('12.34.56', None)
        ]
        
        for input_str, expected in test_cases:
            result = InputSanitizer.sanitize_numeric_input(input_str)
            self.assertEqual(result, expected)
    
    def test_sanitize_numeric_input_int_only(self):
        """Test integer-only numeric sanitization."""
        result = InputSanitizer.sanitize_numeric_input('123.45', allow_float=False)
        self.assertEqual(result, 123)
        
        result = InputSanitizer.sanitize_numeric_input('123', allow_float=False)
        self.assertEqual(result, 123)
    
    def test_validate_email(self):
        """Test email validation."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user@@example.com',
            '',
            None
        ]
        
        for email in valid_emails:
            self.assertTrue(InputSanitizer.validate_email(email))
        
        for email in invalid_emails:
            self.assertFalse(InputSanitizer.validate_email(email))


if __name__ == '__main__':
    unittest.main()