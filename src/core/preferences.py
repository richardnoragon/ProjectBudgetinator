"""
Preferences management functionality.
"""
import json
import tkinter as tk
from tkinter import ttk
from ..utils.config_utils import get_app_directory, load_json_config, save_json_config


class PreferencesManager:
    """Manager class for handling application preferences."""

    def __init__(self):
        """Initialize the preferences manager."""
        self.current_config = self.load_config()

    def load_config(self):
        """Load the user configuration."""
        return load_json_config("user.config.json") or {
            "theme": "light",
            "welcome_screen": True,
            "startup_diagnostic": "verbose"
        }

    def save_config(self, config):
        """Save the user configuration."""
        self.current_config = config
        return save_json_config("user.config.json", config)

    def get_preference(self, key, default=None):
        """Get a specific preference value."""
        return self.current_config.get(key, default)

    def set_preference(self, key, value):
        """Set a specific preference value and save."""
        self.current_config[key] = value
        return self.save_config(self.current_config)


class PreferencesDialog:
    """Dialog for editing preferences."""

    def __init__(self, parent):
        """Initialize the preferences dialog."""
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Preferences")
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        # Load current preferences
        self.prefs_manager = PreferencesManager()
        self.current_config = self.prefs_manager.load_config()

        # Variables to hold preference values
        self.theme_var = tk.StringVar(
            value=self.current_config.get("theme", "light")
        )
        self.welcome_var = tk.BooleanVar(
            value=self.current_config.get("welcome_screen", True)
        )
        self.diag_var = tk.StringVar(
            value=self.current_config.get("startup_diagnostic", "verbose")
        )

        self.setup_gui()

    def setup_gui(self):
        """Set up the dialog GUI."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Theme selection
        theme_frame = ttk.LabelFrame(main_frame, text="Theme", padding="5")
        theme_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            theme_frame,
            text="Light",
            variable=self.theme_var,
            value="light"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            theme_frame,
            text="Dark",
            variable=self.theme_var,
            value="dark"
        ).pack(side=tk.LEFT, padx=5)

        # Startup options
        startup_frame = ttk.LabelFrame(
            main_frame,
            text="Startup Options",
            padding="5"
        )
        startup_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(
            startup_frame,
            text="Show welcome screen",
            variable=self.welcome_var
        ).pack(anchor=tk.W)

        # Diagnostic options
        diag_frame = ttk.LabelFrame(
            main_frame,
            text="Diagnostic Options",
            padding="5"
        )
        diag_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            diag_frame,
            text="Verbose",
            variable=self.diag_var,
            value="verbose"
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            diag_frame,
            text="Silent",
            variable=self.diag_var,
            value="silent"
        ).pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            button_frame,
            text="Save",
            command=self.save_preferences
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def save_preferences(self):
        """Save the preferences and close the dialog."""
        new_config = {
            "theme": self.theme_var.get(),
            "welcome_screen": self.welcome_var.get(),
            "startup_diagnostic": self.diag_var.get()
        }

        if self.prefs_manager.save_config(new_config):
            self.dialog.destroy()
