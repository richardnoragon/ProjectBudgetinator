"""
Preferences management functionality.
"""
import json
import tkinter as tk
from tkinter import ttk, messagebox
from utils.config_utils import get_app_directory, load_json_config, save_json_config


class PreferencesManager:
    """Manager class for handling application preferences."""

    def __init__(self):
        """Initialize the preferences manager."""
        self.current_config = self.load_config()

    def _get_default_config(self):
        """Get the default configuration."""
        return {
            "theme": "light",
            "welcome_screen": True,
            "startup_diagnostic": "verbose",
            "window_positioning": self._get_default_window_positioning()
        }
    
    def _get_default_window_positioning(self):
        """Get default window positioning configuration."""
        return {
            "main_window": {
                "mode": "center_screen",
                "custom_x": 100,
                "custom_y": 100,
                "last_position": {
                    "x": 200,
                    "y": 150,
                    "width": 800,
                    "height": 600
                },
                "remember_size": True,
                "default_size": {
                    "width": 800,
                    "height": 600
                }
            },
            "dialogs": {
                "horizontal_alignment": "center",
                "vertical_alignment": "center",
                "custom_offset": {
                    "x": 0,
                    "y": 0
                },
                "respect_screen_bounds": True,
                "cascade_multiple_dialogs": False
            }
        }
    
    def _merge_window_positioning_config(self, config, default_positioning):
        """Merge window positioning configuration with defaults."""
        if "window_positioning" not in config:
            config["window_positioning"] = default_positioning
            return
        
        for section, section_data in default_positioning.items():
            if section not in config["window_positioning"]:
                config["window_positioning"][section] = section_data
            elif isinstance(section_data, dict):
                for setting, default_val in section_data.items():
                    if setting not in config["window_positioning"][section]:
                        config["window_positioning"][section][setting] = default_val

    def load_config(self):
        """Load the user configuration."""
        default_config = self._get_default_config()
        
        config = load_json_config("user.config.json")
        if not config:
            return default_config
        
        # Merge with defaults to ensure all keys exist
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
            elif key == "window_positioning" and isinstance(value, dict):
                self._merge_window_positioning_config(config, value)
        
        return config

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

        # Window positioning section
        positioning_frame = ttk.LabelFrame(
            main_frame,
            text="Window Positioning",
            padding="5"
        )
        positioning_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            positioning_frame,
            text="Configure Window Positioning...",
            command=self.show_positioning_preferences
        ).pack(pady=5)

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

    def show_positioning_preferences(self):
        """Show the window positioning preferences dialog."""
        try:
            from gui.position_preferences import show_position_preferences_dialog
        except ImportError:
            try:
                from ..gui.position_preferences import show_position_preferences_dialog
            except ImportError:
                try:
                    from src.gui.position_preferences import show_position_preferences_dialog
                except ImportError:
                    messagebox.showerror("Error", "Could not import positioning preferences module")
                    return
            result = show_position_preferences_dialog(self.dialog, self.prefs_manager)
            if result:
                # Positioning preferences were saved, no need to do anything here
                # as they're saved directly by the positioning dialog
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not load positioning preferences: {e}")

    def save_preferences(self):
        """Save the preferences and close the dialog."""
        # Get current config to preserve window_positioning and other settings
        current_config = self.prefs_manager.current_config.copy()
        
        # Update only the preferences we're managing in this dialog
        current_config.update({
            "theme": self.theme_var.get(),
            "welcome_screen": self.welcome_var.get(),
            "startup_diagnostic": self.diag_var.get()
        })

        if self.prefs_manager.save_config(current_config):
            self.dialog.destroy()
