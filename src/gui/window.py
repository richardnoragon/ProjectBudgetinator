"""
GUI setup functions for the main window.
"""
import tkinter as tk
from tkinter import ttk


def create_main_window():
    """Create and configure the main application window."""
    root = tk.Tk()
    root.title("Project Budgetinator")
    root.geometry("800x600")
    
    # Configure style
    style = ttk.Style()
    style.theme_use('default')
    
    return root


def create_status_bar(root):
    """Create a status bar at the bottom of the main window."""
    status_bar = ttk.Label(
        root,
        text="Ready",
        relief=tk.SUNKEN,
        anchor=tk.W,
        padding=(5, 2)
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    return status_bar


def create_toolbar(root):
    """Create a toolbar with common actions."""
    toolbar = ttk.Frame(root)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Add toolbar buttons here
    return toolbar


def setup_gui(root):
    """Set up the complete GUI layout."""
    # Create main components
    toolbar = create_toolbar(root)
    status_bar = create_status_bar(root)
    
    # Create main content area
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    return {
        'toolbar': toolbar,
        'status_bar': status_bar,
        'main_frame': main_frame
    }
