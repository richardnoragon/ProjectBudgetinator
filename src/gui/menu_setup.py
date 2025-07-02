"""
GUI menu setup and configuration.
"""
import tkinter as tk
from tkinter import messagebox

def setup_menu(app):
    """
    Set up the main menu bar and all menu items for the GUI.
    """
    menubar = tk.Menu(app.root)

    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Backup", command=app.backup_file)
    file_menu.add_separator()
    file_menu.add_command(label="Clone", command=app.clone_file)
    file_menu.add_separator()
    file_menu.add_command(label="Compare", command=app.compare_files)
    file_menu.add_separator()
    file_menu.add_command(label="Create from scratch", command=app.create_from_scratch)
    file_menu.add_command(label="Create from template", command=app.create_from_template)
    file_menu.add_separator()
    
    # Modify Submenu
    modify_menu = tk.Menu(file_menu, tearoff=0)
    modify_menu.add_command(label="Add Partner", command=app.add_partner)
    modify_menu.add_command(label="Delete Partner", command=app.delete_partner)
    modify_menu.add_command(label="Edit Partner", command=app.edit_partner)
    modify_menu.add_separator()
    modify_menu.add_command(label="Add Workpackage", command=app.add_workpackage)
    modify_menu.add_command(label="Delete Workpackage", command=app.delete_workpackage)
    modify_menu.add_command(label="Edit Workpackage", command=app.edit_workpackage)
    file_menu.add_cascade(label="Modify", menu=modify_menu)
    file_menu.add_separator()
    file_menu.add_command(label="Restore", command=app.restore_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.exit_program)

    # Preferences Menu
    pref_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Preferences", menu=pref_menu)
    pref_menu.add_command(label="Settings", command=app.show_preferences)

    # Tools Menu
    tools_menu = tk.Menu(menubar, tearoff=0)
    devtools_menu = tk.Menu(tools_menu, tearoff=0)
    devtools_menu.add_checkbutton(label="Developer Mode", command=app.toggle_developer_mode)
    devtools_menu.add_command(label="Show Debug Console", command=app.toggle_debug_console)
    tools_menu.add_cascade(label="Dev Tools", menu=devtools_menu)
    tools_menu.add_separator()
    tools_menu.add_command(label="Diagnostics", command=app.show_diagnostics)
    menubar.add_cascade(label="Tools", menu=tools_menu)

    # Help Menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Help", command=app.show_help)

    app.root.config(menu=menubar)
    return menubar
