#!/usr/bin/env python3
"""
Test script for the new partner validation functionality.
This demonstrates the validation logic without requiring the full GUI.
"""

import tkinter as tk
from tkinter import messagebox

# Simulated existing partners (like in your example)
existing_entries = [
    "P12",
    "P17"
]

def validate_partner_input(user_input, existing_partners):
    """
    Validate partner input according to the specified format.
    Returns (is_valid, error_message, result_dict)
    """
    
    if not user_input:
        return False, "Please enter a partner identifier", None
    
    # Check if input contains a dash
    if "-" not in user_input:
        return False, "Format must be: {number}-{string}", None
    
    # Extract number part
    try:
        dash_pos = user_input.find("-")
        number_part = int(user_input[:dash_pos])
    except ValueError:
        return False, "Number part must be an integer", None
    
    # Validate number range
    if not (2 <= number_part <= 20):
        return False, "Number must be between 2 and 20", None
    
    # Check if number already exists
    partner_identifier = f"P{number_part}"
    if partner_identifier in existing_partners:
        return False, f"Partner P{number_part} already exists", None
    
    # Validate string part
    string_part = user_input[dash_pos + 1:]
    if len(string_part) < 1 or len(string_part) > 16:
        return False, "String part must be between 1 and 16 characters", None
    
    # If we get here, input is valid
    full_input = f"P{user_input}"
    result = {
        'partner_number': str(number_part),
        'partner_acronym': string_part,
        'full_identifier': full_input
    }
    
    return True, f"Valid input: {full_input}", result

def test_validation():
    """Test various input scenarios"""
    test_cases = [
        # Valid cases
        ("5-abcdefghijklmnop", True, "Valid case - 16 characters"),
        ("20-1234567890123456", True, "Valid case with numbers - 16 characters"),
        ("3-a", True, "Valid case - 1 character"),
        ("4-short", True, "Valid case - 5 characters"),
        ("6-mediumlength", True, "Valid case - 12 characters"),
        
        # Invalid cases
        ("1-abcdefghijklmnop", False, "Number too low"),
        ("21-abcdefghijklmnop", False, "Number too high"),
        ("12-abcdefghijklmnop", False, "Duplicate number"),
        ("5-", False, "String too short - empty"),
        ("5-toolongstringhere123", False, "String too long - 22 characters"),
        ("abc-abcdefghijklmnop", False, "Non-numeric number part"),
        ("5abcdefghijklmnop", False, "Missing dash"),
        ("", False, "Empty input"),
    ]
    
    print("Testing Partner Validation Logic")
    print("=" * 50)
    
    for test_input, expected_valid, description in test_cases:
        is_valid, message, result = validate_partner_input(test_input, existing_entries)
        
        status = "✅ PASS" if (is_valid == expected_valid) else "❌ FAIL"
        print(f"{status} | Input: '{test_input}' | {description}")
        print(f"      | Result: {message}")
        if result:
            print(f"      | Parsed: {result}")
        print()

def create_gui_demo():
    """Create a simple GUI demo of the validation"""
    root = tk.Tk()
    root.title("Partner Validation Demo")
    root.geometry("500x300")
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Enter partner in format: {number}-{string}\n"
             "Number must be between 2 and 20\n"
             "String must be between 1 and 16 characters\n\n"
             f"Existing partners: {', '.join(existing_entries)}",
        font=("Arial", 10),
        justify="left"
    )
    instructions.pack(pady=10)
    
    # Input frame
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)
    
    tk.Label(input_frame, text="P", font=("Arial", 12)).pack(side=tk.LEFT)
    
    entry = tk.Entry(input_frame, width=30, font=("Arial", 12))
    entry.pack(side=tk.LEFT)
    entry.focus()
    
    # Result display
    result_text = tk.Text(root, height=8, width=60)
    result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def validate_and_show():
        user_input = entry.get().strip()
        is_valid, message, result = validate_partner_input(user_input, existing_entries)
        
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Input: P{user_input}\n")
        result_text.insert(tk.END, f"Status: {'✅ Valid' if is_valid else '❌ Invalid'}\n")
        result_text.insert(tk.END, f"Message: {message}\n\n")
        
        if result:
            result_text.insert(tk.END, "Parsed Result:\n")
            for key, value in result.items():
                result_text.insert(tk.END, f"  {key}: {value}\n")
        
        # Show messagebox like in the real implementation
        if is_valid:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Invalid", message)
    
    # Button
    tk.Button(root, text="Validate", command=validate_and_show).pack(pady=5)
    
    # Bind Enter key
    entry.bind('<Return>', lambda e: validate_and_show())
    
    root.mainloop()

if __name__ == "__main__":
    print("Partner Validation Test")
    print("Choose an option:")
    print("1. Run automated tests")
    print("2. Run GUI demo")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            test_validation()
        elif choice == "2":
            create_gui_demo()
        else:
            print("Invalid choice. Running automated tests...")
            test_validation()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to automated tests
        test_validation()