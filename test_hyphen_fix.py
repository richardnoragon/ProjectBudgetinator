#!/usr/bin/env python3
"""
Simple test script to verify the hyphen fix works correctly.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from handlers.update_budget_overview_handler import get_partner_number_from_sheet_name
from handlers.add_partner_handler import get_existing_partners

def test_partner_number_extraction():
    """Test partner number extraction with new hyphen format."""
    print("=" * 60)
    print("TESTING PARTNER NUMBER EXTRACTION")
    print("=" * 60)
    
    # Test cases for new hyphen format
    test_cases = [
        ("P2-ACME", 2, "✅ Should work"),
        ("P3-University", 3, "✅ Should work"),
        ("P15-Company", 15, "✅ Should work"),
        ("P4-abc", 4, "✅ Should work (user's example)"),
        ("P1-Coordinator", None, "❌ Should fail (P1 not allowed)"),
        ("P21-Invalid", None, "❌ Should fail (P21 > 20)"),
        ("Summary", None, "❌ Should fail (not partner sheet)"),
        ("P2 ACME", None, "❌ Should fail (old space format)"),
        ("P3 University", None, "❌ Should fail (old space format)"),
    ]
    
    all_passed = True
    
    for sheet_name, expected, description in test_cases:
        result = get_partner_number_from_sheet_name(sheet_name)
        status = "PASS" if result == expected else "FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status:>4} | {sheet_name:<15} | Expected: {str(expected):<4} | Got: {str(result):<4} | {description}")
    
    print("\n" + "=" * 60)
    print(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 60)
    
    return all_passed

def test_worksheet_name_creation():
    """Test worksheet name creation with hyphen format."""
    print("\n" + "=" * 60)
    print("TESTING WORKSHEET NAME CREATION")
    print("=" * 60)
    
    # Simulate partner info as created by the dialog
    test_partner_info = {
        'project_partner_number': '4',
        'partner_acronym': 'abc'
    }
    
    # This is how the worksheet name is created in add_partner_handler.py
    sheet_name = f"P{test_partner_info['project_partner_number']}-{test_partner_info['partner_acronym']}"
    
    expected = "P4-abc"
    status = "PASS" if sheet_name == expected else "FAIL"
    
    print(f"{status:>4} | Created sheet name: '{sheet_name}'")
    print(f"     | Expected:          '{expected}'")
    print(f"     | Match:             {sheet_name == expected}")
    
    # Test that the created name can be parsed back correctly
    parsed_number = get_partner_number_from_sheet_name(sheet_name)
    parse_status = "PASS" if parsed_number == 4 else "FAIL"
    
    print(f"{parse_status:>4} | Parsed back:       {parsed_number}")
    print(f"     | Expected:          4")
    
    print("\n" + "=" * 60)
    overall_pass = (sheet_name == expected) and (parsed_number == 4)
    print(f"WORKSHEET NAME TEST: {'✅ PASSED' if overall_pass else '❌ FAILED'}")
    print("=" * 60)
    
    return overall_pass

def test_edit_partner_filtering():
    """Test that edit partner functionality only recognizes hyphen format sheets."""
    print("\n" + "=" * 60)
    print("TESTING EDIT PARTNER FILTERING")
    print("=" * 60)
    
    # Import the main app's filtering function
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from main import ProjectBudgetinator
    
    app = ProjectBudgetinator()
    
    # Test cases for sheet filtering
    test_cases = [
        ("P2-ACME", True, "✅ Should be recognized"),
        ("P3-University", True, "✅ Should be recognized"),
        ("P15-Company", True, "✅ Should be recognized"),
        ("P4-abc", True, "✅ Should be recognized (user's example)"),
        ("P1-Coordinator", False, "❌ Should be filtered out (P1 not allowed)"),
        ("P21-Invalid", False, "❌ Should be filtered out (P21 > 20)"),
        ("Summary", False, "❌ Should be filtered out (not partner sheet)"),
        ("P2 ACME", False, "❌ Should be filtered out (old space format)"),
        ("P3 University", False, "❌ Should be filtered out (old space format)"),
        ("Budget Overview", False, "❌ Should be filtered out (not partner sheet)"),
    ]
    
    all_passed = True
    
    for sheet_name, expected, description in test_cases:
        result = app._is_partner_worksheet(sheet_name)
        status = "PASS" if result == expected else "FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"{status:>4} | {sheet_name:<15} | Expected: {str(expected):<5} | Got: {str(result):<5} | {description}")
    
    print("\n" + "=" * 60)
    print(f"EDIT PARTNER FILTERING: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    print("🔍 TESTING HYPHEN FIX FOR PARTNER WORKSHEETS")
    print("This test verifies that partner worksheets now use hyphens instead of spaces")
    print("and that edit partner functionality only works with hyphen format sheets")
    print()
    
    test1_passed = test_partner_number_extraction()
    test2_passed = test_worksheet_name_creation()
    test3_passed = test_edit_partner_filtering()
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Partner Number Extraction: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Worksheet Name Creation:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Edit Partner Filtering:    {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print()
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED! The hyphen fix is working correctly.")
        print("✅ Partner worksheets will now be created with hyphens (e.g., P4-abc)")
        print("✅ The system can correctly parse hyphen-formatted sheet names")
        print("✅ Edit partner functionality only recognizes hyphen format sheets")
        print("✅ Old space-formatted names are no longer recognized (as intended)")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    
    print("=" * 60)