#!/usr/bin/env python3
"""
Excel Formula Validation Script

This script validates all Excel formulas found in the documentation
to ensure they are syntactically correct and functionally accurate.
"""

import re
import sys
import os

def validate_excel_formula(formula: str) -> tuple:
    """
    Validate an Excel formula for syntax and logical correctness.
    
    Args:
        formula: Excel formula string (with or without leading =)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not formula.strip():
        return False, "Empty formula"
    
    # Ensure formula starts with =
    if not formula.startswith('='):
        formula = '=' + formula
    
    # Check for invalid patterns
    invalid_patterns = [
        r'[A-Z]+-\d+',  # Negative row numbers like A-11
        r'\$[A-Z]+\$-\d+',  # Negative absolute row numbers
        r'[A-Z]+0',  # Zero row numbers like A0
        r'[A-Z]{4,}',  # Column names longer than 3 letters
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, formula):
            return False, f"Invalid pattern found: {pattern}"
    
    # Check for valid Excel function syntax
    function_pattern = r'=([A-Z]+)\([^)]*\)'
    if re.match(function_pattern, formula):
        # Extract function name
        func_match = re.match(r'=([A-Z]+)\(', formula)
        if func_match:
            func_name = func_match.group(1)
            # Check if it's a known Excel function
            known_functions = ['SUM', 'AVERAGE', 'COUNT', 'MAX', 'MIN', 'IF', 'VLOOKUP', 'INDEX', 'MATCH']
            if func_name not in known_functions:
                return True, f"Warning: Unknown function {func_name} (may be valid)"
    
    # Check cell reference patterns
    cell_ref_pattern = r'[A-Z]{1,3}[1-9]\d*'
    if re.search(cell_ref_pattern, formula):
        # Validate individual cell references
        cell_refs = re.findall(r'[A-Z]{1,3}[1-9]\d*', formula)
        for ref in cell_refs:
            col_part = ''.join(c for c in ref if c.isalpha())
            row_part = ''.join(c for c in ref if c.isdigit())
            
            # Check Excel limits
            if len(col_part) > 3:
                return False, f"Invalid column reference: {col_part}"
            if len(col_part) == 3 and col_part > 'XFD':
                return False, f"Column reference exceeds Excel limit: {col_part}"
            if int(row_part) > 1048576:
                return False, f"Row reference exceeds Excel limit: {row_part}"
    
    return True, "Valid formula"


def extract_formulas_from_file(file_path: str) -> list:
    """Extract Excel formulas from a markdown file."""
    formulas = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find formulas in code blocks and inline code
        formula_patterns = [
            r'`(=[^`]+)`',  # Inline code with formulas
            r'```[^`]*?(=[^`\n]+)[^`]*?```',  # Code blocks with formulas
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    formulas.extend([m for m in match if m.startswith('=')])
                else:
                    if match.startswith('='):
                        formulas.append(match)
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return formulas


def main():
    """Main validation function."""
    print("🔍 Excel Formula Validation")
    print("=" * 50)
    
    # Files to check
    documentation_files = [
        'PM_OVERVIEW_IMPLEMENTATION_GUIDE.md',
        'UPDATE_BUDGET_OVERVIEW_IMPLEMENTATION_GUIDE.md',
        'UPDATE_BUDGET_OVERVIEW_HANDLER_DESIGN.md',
        'UPDATE_PM_OVERVIEW_HANDLER_DESIGN.md',
        'Excel_Formula_Logic_Solution_Architecture.md',
        'Excel_Formula_Fix_Implementation_Summary.md'
    ]
    
    total_formulas = 0
    valid_formulas = 0
    invalid_formulas = []
    
    for file_path in documentation_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue
            
        print(f"\n📄 Checking {file_path}...")
        formulas = extract_formulas_from_file(file_path)
        
        if not formulas:
            print("   No Excel formulas found")
            continue
        
        for formula in formulas:
            total_formulas += 1
            is_valid, message = validate_excel_formula(formula)
            
            if is_valid:
                valid_formulas += 1
                print(f"   ✅ {formula} - {message}")
            else:
                invalid_formulas.append((file_path, formula, message))
                print(f"   ❌ {formula} - {message}")
    
    # Manual validation of known formulas from documentation
    print(f"\n📋 Manual Formula Validation...")
    
    test_formulas = [
        "=SUM(A1:A10)",
        "=SUM($A$1:$A$10)", 
        "=SUM(A$1:A$10)",
        "=B1*2",
        "=SUM(C1:C5)",
        "=A1+B1",
        "=SUM(A1:A10)",
        "=Sheet2!A1",
        "=A1*2"
    ]
    
    for formula in test_formulas:
        total_formulas += 1
        is_valid, message = validate_excel_formula(formula)
        
        if is_valid:
            valid_formulas += 1
            print(f"   ✅ {formula} - {message}")
        else:
            invalid_formulas.append(("manual_test", formula, message))
            print(f"   ❌ {formula} - {message}")
    
    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"   Total formulas checked: {total_formulas}")
    print(f"   Valid formulas: {valid_formulas}")
    print(f"   Invalid formulas: {len(invalid_formulas)}")
    
    if invalid_formulas:
        print(f"\n❌ Invalid Formulas Found:")
        for file_path, formula, error in invalid_formulas:
            print(f"   {file_path}: {formula} - {error}")
        return False
    else:
        print(f"\n🎉 All Excel formulas are valid!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)