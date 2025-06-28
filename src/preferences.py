import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class PreferencesManager:
    def __init__(self):
        self.user_home = str(Path.home())
        self.app_dir = os.path.join(self.user_home, "ProjectBudgetinator")
        self.config_dir = os.path.join(self.app_dir, "config")
        self.default_config = {
            "theme": "light",
            "startup_diagnostic": "verbose",
            "welcome_screen": True,
            "default_file_location": str(Path.home()),
            "remember_last_location": False,
            "save_location": str(Path.home())
        }

    def load_config(self, config_name="user.config.json"):
        """Load a configuration file, migrate old keys if needed"""
        config_path = os.path.join(self.config_dir, config_name)
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Migrate old key if present
                if "startup_diagnostics" in config:
                    config["startup_diagnostic"] = config.pop("startup_diagnostics")
                    self.save_config(config, config_name)
                # Fill missing keys with defaults
                for k, v in self.default_config.items():
                    if k not in config:
                        config[k] = v
                self.save_config(config, config_name)
                return config
        except FileNotFoundError:
            return self.default_config.copy()
        except json.JSONDecodeError:
            # Backup corrupted config and create new one
            self._backup_corrupted_config(config_path)
            return self.default_config.copy()

    def save_config(self, config_data, config_name="user.config.json"):
        """Save configuration to file"""
        config_path = os.path.join(self.config_dir, config_name)
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)

    def _backup_corrupted_config(self, config_path):
        """Backup a corrupted config file"""
        import datetime
        backup_name = f"{os.path.basename(config_path)}.corrupted.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(os.path.dirname(config_path), backup_name)
        os.rename(config_path, backup_path)

    def list_config_files(self):
        """List all available config files"""
        return [f for f in os.listdir(self.config_dir) if f.endswith('.config.json')]

    def merge_configs(self, config1, config2):
        """Merge two configurations, prioritizing user-edited fields"""
        merged = self.default_config.copy()
        merged.update(config1)
        merged.update(config2)
        return merged

class PreferencesDialog:
    def __init__(self, parent):
        self.parent = parent
        self.prefs_manager = PreferencesManager()
        self.current_config = self.prefs_manager.load_config()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Preferences")
        self.dialog.grab_set()  # Make dialog modal
        
        self.setup_ui()

    def setup_ui(self):
        # Theme selection
        theme_frame = ttk.LabelFrame(self.dialog, text="Theme")
        theme_frame.pack(fill="x", padx=5, pady=5)
        
        self.theme_var = tk.StringVar(value=self.current_config["theme"])
        ttk.Radiobutton(theme_frame, text="Light", value="light", variable=self.theme_var).pack(side="left")
        ttk.Radiobutton(theme_frame, text="Dark", value="dark", variable=self.theme_var).pack(side="left")

        # Startup options
        startup_frame = ttk.LabelFrame(self.dialog, text="Startup Options")
        startup_frame.pack(fill="x", padx=5, pady=5)
        
        self.diagnostic_var = tk.StringVar(value=self.current_config["startup_diagnostic"])
        ttk.Radiobutton(startup_frame, text="Verbose", value="verbose", 
                       variable=self.diagnostic_var).pack(anchor="w")
        ttk.Radiobutton(startup_frame, text="Silent", value="silent", 
                       variable=self.diagnostic_var).pack(anchor="w")
        
        self.welcome_var = tk.BooleanVar(value=self.current_config["welcome_screen"])
        ttk.Checkbutton(startup_frame, text="Show welcome screen", 
                       variable=self.welcome_var).pack(anchor="w")

        # File locations
        locations_frame = ttk.LabelFrame(self.dialog, text="File Locations")
        locations_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(locations_frame, text="Default file location:").pack(anchor="w")
        self.default_location = tk.StringVar(value=self.current_config["default_file_location"])
        loc_entry = ttk.Entry(locations_frame, textvariable=self.default_location)
        loc_entry.pack(fill="x", padx=5)
        ttk.Button(locations_frame, text="Browse", 
                  command=self.browse_default_location).pack(anchor="e", padx=5)

        self.remember_location = tk.BooleanVar(value=self.current_config["remember_last_location"])
        ttk.Checkbutton(locations_frame, text="Remember last used location", 
                       variable=self.remember_location).pack(anchor="w")

        # Config file management
        config_frame = ttk.LabelFrame(self.dialog, text="Configuration Management")
        config_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(config_frame, text="Create New Config", 
                  command=self.create_new_config).pack(side="left", padx=5)
        ttk.Button(config_frame, text="Merge Configs", 
                  command=self.merge_config_dialog).pack(side="left", padx=5)
        ttk.Button(config_frame, text="Reset to Default", 
                  command=self.reset_config).pack(side="left", padx=5)

        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(button_frame, text="Save", command=self.save_preferences).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side="right", padx=5)

    def browse_default_location(self):
        directory = filedialog.askdirectory(
            initialdir=self.default_location.get(),
            title="Select Default File Location"
        )
        if directory:
            self.default_location.set(directory)

    def create_new_config(self):
        name = tk.simpledialog.askstring("New Configuration", 
                                       "Enter name for new configuration:")
        if name:
            if not name.endswith('.config.json'):
                name = f"{name}.config.json"
            self.current_config["theme"] = self.theme_var.get()
            self.current_config["startup_diagnostic"] = self.diagnostic_var.get()
            self.current_config["welcome_screen"] = self.welcome_var.get()
            self.current_config["default_file_location"] = self.default_location.get()
            self.current_config["remember_last_location"] = self.remember_location.get()
            self.prefs_manager.save_config(self.current_config, name)
            messagebox.showinfo("Success", f"Created new configuration: {name}")

    def merge_config_dialog(self):
        configs = self.prefs_manager.list_config_files()
        if len(configs) < 2:
            messagebox.showwarning("Error", "Need at least two config files to merge")
            return

        dialog = tk.Toplevel(self.dialog)
        dialog.title("Merge Configurations")
        dialog.grab_set()

        ttk.Label(dialog, text="Select configurations to merge:").pack(pady=5)
        
        config1_var = tk.StringVar()
        config2_var = tk.StringVar()
        
        ttk.Combobox(dialog, textvariable=config1_var, values=configs).pack(pady=5)
        ttk.Combobox(dialog, textvariable=config2_var, values=configs).pack(pady=5)
        
        def do_merge():
            if config1_var.get() and config2_var.get():
                config1 = self.prefs_manager.load_config(config1_var.get())
                config2 = self.prefs_manager.load_config(config2_var.get())
                merged = self.prefs_manager.merge_configs(config1, config2)
                
                name = tk.simpledialog.askstring("Save Merged Config", 
                                               "Enter name for merged configuration:")
                if name:
                    if not name.endswith('.config.json'):
                        name = f"{name}.config.json"
                    self.prefs_manager.save_config(merged, name)
                    messagebox.showinfo("Success", f"Created merged configuration: {name}")
                dialog.destroy()
        
        ttk.Button(dialog, text="Merge", command=do_merge).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def reset_config(self):
        if messagebox.askyesno("Confirm Reset", 
                              "Are you sure you want to reset to default settings?"):
            self.current_config = self.prefs_manager.default_config.copy()
            self.theme_var.set(self.current_config["theme"])
            self.diagnostic_var.set(self.current_config["startup_diagnostic"])
            self.welcome_var.set(self.current_config["welcome_screen"])
            self.default_location.set(self.current_config["default_file_location"])
            self.remember_location.set(self.current_config["remember_last_location"])

    def save_preferences(self):
        self.current_config["theme"] = self.theme_var.get()
        self.current_config["startup_diagnostic"] = self.diagnostic_var.get()
        self.current_config["welcome_screen"] = self.welcome_var.get()
        self.current_config["default_file_location"] = self.default_location.get()
        self.current_config["remember_last_location"] = self.remember_location.get()
        
        self.prefs_manager.save_config(self.current_config)
        messagebox.showinfo("Success", "Preferences saved successfully")
        self.dialog.destroy()
