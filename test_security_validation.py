#!/usr/bin/env python3
"""
Simple test script for security validation functionality.
"""

import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.security_validator import SecurityValidator, InputSanitizer

def test_security_validator():
    """Test SecurityValidator functionality."""
    print("Testing SecurityValidator...")
    
    # Test 1: Valid file path
    try:
        safe_path = SecurityValidator.validate_file_path('test.xlsx')
        print("✓ Valid file path accepted")
    except Exception as e:
        print(f"✗ Valid file path rejected: {e}")
        return False
    
    # Test 2: Path traversal protection
    try:
        SecurityValidator.validate_file_path('../../../etc/passwd')
        print("✗ Path traversal not blocked")
        return False
    except ValueError as e:
        print("✓ Path traversal blocked")
    
    # Test 3: Null byte protection
    try:
        SecurityValidator.validate_file_path('test\x00file.xlsx')
        print("✗ Null byte injection not blocked")
        return False
    except ValueError as e:
        print("✓ Null byte injection blocked")
    
    # Test 4: Filename sanitization
    clean_name = SecurityValidator.sanitize_filename('test<file>:name?.xlsx')
    if '<' not in clean_name and '>' not in clean_name and ':' not in clean_name:
        print("✓ Filename sanitization working")
    else:
        print("✗ Filename sanitization failed")
        return False
    
    # Test 5: Directory validation
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            safe_dir = SecurityValidator.validate_directory_path(tmp_dir)
            print("✓ Directory validation working")
        except Exception as e:
            print(f"✗ Directory validation failed: {e}")
            return False
    
    return True

def test_input_sanitizer():
    """Test InputSanitizer functionality."""
    print("\nTesting InputSanitizer...")
    
    # Test 1: String sanitization
    clean_string = InputSanitizer.sanitize_string('test\x00\x01\x02string')
    if '\x00' not in clean_string and '\x01' not in clean_string:
        print("✓ String sanitization working")
    else:
        print("✗ String sanitization failed")
        return False
    
    # Test 2: Numeric input sanitization
    num = InputSanitizer.sanitize_numeric_input('123.45')
    if num == 123.45:
        print("✓ Numeric input sanitization working")
    else:
        print("✗ Numeric input sanitization failed")
        return False
    
    # Test 3: Invalid numeric input
    num = InputSanitizer.sanitize_numeric_input('abc')
    if num is None:
        print("✓ Invalid numeric input rejected")
    else:
        print("✗ Invalid numeric input not rejected")
        return False
    
    # Test 4: Email validation
    if InputSanitizer.validate_email('test@example.com'):
        print("✓ Valid email accepted")
    else:
        print("✗ Valid email rejected")
        return False
    
    if not InputSanitizer.validate_email('invalid-email'):
        print("✓ Invalid email rejected")
    else:
        print("✗ Invalid email accepted")
        return False
    
    return True

def test_file_type_validation():
    """Test file type validation."""
    print("\nTesting file type validation...")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        tmp.write(b'dummy excel content')
        tmp_path = tmp.name
    
    try:
        # Test Excel file validation
        is_valid, error_msg = SecurityValidator.validate_excel_file(tmp_path)
        if is_valid:
            print("✓ Excel file validation working")
        else:
            print(f"✗ Excel file validation failed: {error_msg}")
            return False
        
        # Test non-existent file
        is_valid, error_msg = SecurityValidator.validate_excel_file('/nonexistent/file.xlsx')
        if not is_valid and "does not exist" in error_msg:
            print("✓ Non-existent file properly handled")
        else:
            print("✗ Non-existent file not properly handled")
            return False
            
    finally:
        os.unlink(tmp_path)
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("SECURITY VALIDATION TESTS")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_security_validator()
    all_passed &= test_input_sanitizer()
    all_passed &= test_file_type_validation()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL SECURITY VALIDATION TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)