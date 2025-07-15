"""
Menu setup for the main window.
"""
import tkinter as tk
from tkinter import ttk


def create_menu(root, callbacks):
    """Create the main menu bar with all menus."""
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(
        label="New",
        command=callbacks.get('new_file'),
        accelerator="Ctrl+N"
    )
    file_menu.add_command(
        label="Open...",
        command=callbacks.get('open_file'),
        accelerator="Ctrl+O"
    )
    file_menu.add_command(
        label="Save",
        command=callbacks.get('save_file'),
        accelerator="Ctrl+S"
    )
    file_menu.add_command(
        label="Save As...",
        command=callbacks.get('save_as'),
        accelerator="Ctrl+Shift+S"
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Batch Operations...",
        command=callbacks.get('batch_operations'),
        accelerator="Ctrl+B"
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Exit",
        command=callbacks.get('exit_app'),
        accelerator="Alt+F4"
    )

    # Project menu
    project_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Project", menu=project_menu)
    project_menu.add_command(
        label="Add Partner...",
        command=callbacks.get('add_partner')
    )
    project_menu.add_command(
        label="Project Settings...",
        command=callbacks.get('project_settings')
    )

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(
        label="About",
        command=callbacks.get('show_about')
    )

    return menubar


def setup_keyboard_shortcuts(root, callbacks):
    """Set up keyboard shortcuts for menu items."""
    root.bind('<Control-n>', lambda e: callbacks.get('new_file')())
    root.bind('<Control-o>', lambda e: callbacks.get('open_file')())
    root.bind('<Control-s>', lambda e: callbacks.get('save_file')())
    root.bind('<Control-S>', lambda e: callbacks.get('save_as')())
    root.bind('<Control-b>', lambda e: callbacks.get('batch_operations')())
