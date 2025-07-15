#!/usr/bin/env python3
"""
Simple test for security validator functionality.
"""

import sys
import os
sys.path.insert(0, 'src')

from utils.security_validator import SecurityValidator, InputSanitizer

def test_security_validator():
    """Test all security validation functionality."""
    print("Testing SecurityValidator...")
    
    # Test 1: Path validation
    try:
        safe_path = SecurityValidator.validate_file_path('test.xlsx')
        print("✓ Path validation passed")
    except Exception as e:
        print(f"✗ Path validation failed: {e}")
        return False
    
    # Test 2: Path traversal protection
    try:
        SecurityValidator.validate_file_path('../../../etc/passwd')
        print("✗ Path traversal test failed - should have raised ValueError")
        return False
    except ValueError:
        print("✓ Path traversal protection working")
    except Exception as e:
        print(f"✗ Path traversal test error: {e}")
        return False
    
    # Test 3: Filename sanitization
    try:
        clean_name = SecurityValidator.sanitize_filename('test<file>.xlsx')
        expected = 'test_file_.xlsx'
        if clean_name == expected or 'test' in clean_name and '<' not in clean_name:
            print("✓ Filename sanitization passed")
        else:
            print(f"✗ Filename sanitization unexpected: {clean_name}")
            return False
    except Exception as e:
        print(f"✗ Filename sanitization failed: {e}")
        return False
    
    # Test 4: Input sanitization
    try:
        clean_input = InputSanitizer.sanitize_string('test\x00input')
        if '\x00' not in clean_input:
            print("✓ Input sanitization passed")
        else:
            print("✗ Input sanitization failed - null bytes present")
            return False
    except Exception as e:
        print(f"✗ Input sanitization failed: {e}")
        return False
    
    # Test 5: Excel file validation (non-existent file)
    try:
        is_valid, error = SecurityValidator.validate_excel_file('nonexistent.xlsx')
        if not is_valid and "does not exist" in error:
            print("✓ Excel validation working for non-existent file")
        else:
            print(f"✗ Excel validation unexpected: {is_valid}, {error}")
            return False
    except Exception as e:
        print(f"✗ Excel validation failed: {e}")
        return False
    
    print("All security validation tests passed!")
    return True

if __name__ == "__main__":
    success = test_security_validator()
    sys.exit(0 if success else 1)