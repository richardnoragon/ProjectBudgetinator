#!/usr/bin/env python3
"""
Test script to verify window positioning preferences are working correctly.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_preferences():
    """Test the preferences dialog with window positioning."""
    root = tk.Tk()
    root.title("Test Window Positioning Preferences")
    root.geometry("400x300")
    
    def open_preferences():
        from preferences import PreferencesDialog
        dialog = PreferencesDialog(root)
        root.wait_window(dialog.dialog)
    
    # Create a simple UI
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="Test Window Positioning Preferences", 
              font=("Arial", 14, "bold")).pack(pady=10)
    
    ttk.Label(frame, text="Click the button below to open the preferences dialog.\n"
                         "You should now see a 'Window Positioning' section\n"
                         "with a 'Configure Window Positioning...' button.",
              justify=tk.CENTER).pack(pady=10)
    
    ttk.Button(frame, text="Open Preferences", 
               command=open_preferences).pack(pady=20)
    
    ttk.Button(frame, text="Exit", 
               command=root.quit).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_preferences()