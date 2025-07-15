"""
Enhanced Preferences Dialog with Dynamic Configuration Support

This module provides an enhanced preferences dialog that integrates with
the dynamic configuration system, offering:
- Real-time validation
- Configuration import/export
- Environment variable support
- Migration capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, Optional
import os
from pathlib import Path

from config.dynamic_config import (
    ConfigurationManager, 
    UserConfig, 
    ThemeType, 
    DiagnosticLevel,
    get_config_manager,
    get_env_config_override
)


class EnhancedPreferencesDialog:
    """Enhanced preferences dialog with validation and advanced features"""
    
    def __init__(self, parent: tk.Tk, on_config_changed: Optional[Callable[[UserConfig], None]] = None):
        """
        Initialize enhanced preferences dialog.
        
        Args:
            parent: Parent window
            on_config_changed: Callback when configuration changes
        """
        self.parent = parent
        self.on_config_changed = on_config_changed
        self.config_manager = get_config_manager()
        self.current_config = self.config_manager.get_config()
        
        # Dialog window
        self.dialog = None
        self.notebook = None
        
        # UI Variables
        self.ui_vars: Dict[str, tk.Variable] = {}
        self.validation_labels: Dict[str, tk.Label] = {}
        
        # Track changes
        self.has_changes = False
        self.original_config_hash = self.config_manager.get_config_hash()
    
    def show(self):
        """Show the preferences dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Enhanced Preferences")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Setup UI
        self._setup_ui()
        
        # Load current values
        self._load_current_values()
        
        # Setup validation
        self._setup_validation()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Focus on dialog
        self.dialog.focus_set()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self._setup_display_tab()
        self._setup_files_tab()
        self._setup_performance_tab()
        self._setup_advanced_tab()
        self._setup_environment_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Import Config", 
                  command=self._import_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export Config", 
                  command=self._export_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_to_defaults).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply", 
                  command=self._apply).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", 
                  command=self._ok).pack(side=tk.RIGHT)
    
    def _setup_display_tab(self):
        """Setup display preferences tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Display")
        
        # Theme selection
        theme_frame = ttk.LabelFrame(frame, text="Appearance", padding=10)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ui_vars['theme'] = tk.StringVar()
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.ui_vars['theme'],
                                  values=[theme.value for theme in ThemeType],
                                  state="readonly", width=20)
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Welcome screen
        self.ui_vars['welcome_screen'] = tk.BooleanVar()
        welcome_check = ttk.Checkbutton(theme_frame, 
                                       text="Show welcome screen on startup",
                                       variable=self.ui_vars['welcome_screen'])
        welcome_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Diagnostics
        diag_frame = ttk.LabelFrame(frame, text="Diagnostics", padding=10)
        diag_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(diag_frame, text="Startup Diagnostic Level:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ui_vars['startup_diagnostic'] = tk.StringVar()
        diag_combo = ttk.Combobox(diag_frame, textvariable=self.ui_vars['startup_diagnostic'],
                                 values=[level.value for level in DiagnosticLevel],
                                 state="readonly", width=20)
        diag_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def _setup_files_tab(self):
        """Setup file handling preferences tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Files")
        
        # Default locations
        locations_frame = ttk.LabelFrame(frame, text="Default Locations", padding=10)
        locations_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Default file location
        ttk.Label(locations_frame, text="Default File Location:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ui_vars['default_file_location'] = tk.StringVar()
        loc_frame = ttk.Frame(locations_frame)
        loc_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        ttk.Entry(loc_frame, textvariable=self.ui_vars['default_file_location'], width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(loc_frame, text="Browse", 
                  command=lambda: self._browse_directory('default_file_location')).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save location
        ttk.Label(locations_frame, text="Save Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ui_vars['save_location'] = tk.StringVar()
        save_frame = ttk.Frame(locations_frame)
        save_frame.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        ttk.Entry(save_frame, textvariable=self.ui_vars['save_location'], width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(save_frame, text="Browse", 
                  command=lambda: self._browse_directory('save_location')).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configure column weights
        locations_frame.columnconfigure(1, weight=1)
        
        # File options
        options_frame = ttk.LabelFrame(frame, text="File Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_vars['remember_last_location'] = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Remember last used location",
                       variable=self.ui_vars['remember_last_location']).pack(anchor=tk.W, pady=2)
        
        # Recent files
        ttk.Label(options_frame, text="Max Recent Files:").pack(anchor=tk.W, pady=(10, 2))
        self.ui_vars['max_recent_files'] = tk.IntVar()
        recent_spin = ttk.Spinbox(options_frame, from_=1, to=50, 
                                 textvariable=self.ui_vars['max_recent_files'], width=10)
        recent_spin.pack(anchor=tk.W, pady=2)
        self.validation_labels['max_recent_files'] = ttk.Label(options_frame, text="", foreground="red")
        self.validation_labels['max_recent_files'].pack(anchor=tk.W)
    
    def _setup_performance_tab(self):
        """Setup performance preferences tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Performance")
        
        # Caching
        cache_frame = ttk.LabelFrame(frame, text="Caching", padding=10)
        cache_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_vars['enable_caching'] = tk.BooleanVar()
        cache_check = ttk.Checkbutton(cache_frame, text="Enable file caching",
                                     variable=self.ui_vars['enable_caching'])
        cache_check.pack(anchor=tk.W, pady=2)
        
        # Cache size
        cache_size_frame = ttk.Frame(cache_frame)
        cache_size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cache_size_frame, text="Cache Size (MB):").pack(side=tk.LEFT)
        self.ui_vars['cache_size_mb'] = tk.IntVar()
        cache_spin = ttk.Spinbox(cache_size_frame, from_=10, to=1000, 
                                textvariable=self.ui_vars['cache_size_mb'], width=10)
        cache_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        self.validation_labels['cache_size_mb'] = ttk.Label(cache_frame, text="", foreground="red")
        self.validation_labels['cache_size_mb'].pack(anchor=tk.W)
        
        # Backup settings
        backup_frame = ttk.LabelFrame(frame, text="Backup", padding=10)
        backup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.ui_vars['auto_backup'] = tk.BooleanVar()
        backup_check = ttk.Checkbutton(backup_frame, text="Enable automatic backups",
                                      variable=self.ui_vars['auto_backup'])
        backup_check.pack(anchor=tk.W, pady=2)
        
        # Backup count
        backup_count_frame = ttk.Frame(backup_frame)
        backup_count_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(backup_count_frame, text="Number of backups to keep:").pack(side=tk.LEFT)
        self.ui_vars['backup_count'] = tk.IntVar()
        backup_spin = ttk.Spinbox(backup_count_frame, from_=1, to=50, 
                                 textvariable=self.ui_vars['backup_count'], width=10)
        backup_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        self.validation_labels['backup_count'] = ttk.Label(backup_frame, text="", foreground="red")
        self.validation_labels['backup_count'].pack(anchor=tk.W)
    
    def _setup_advanced_tab(self):
        """Setup advanced preferences tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Advanced")
        
        # Configuration info
        info_frame = ttk.LabelFrame(frame, text="Configuration Information", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Version info
        version_frame = ttk.Frame(info_frame)
        version_frame.pack(fill=tk.X, pady=2)
        ttk.Label(version_frame, text="Config Version:").pack(side=tk.LEFT)
        ttk.Label(version_frame, text=self.current_config.config_version).pack(side=tk.LEFT, padx=(10, 0))
        
        # Last updated
        updated_frame = ttk.Frame(info_frame)
        updated_frame.pack(fill=tk.X, pady=2)
        ttk.Label(updated_frame, text="Last Updated:").pack(side=tk.LEFT)
        ttk.Label(updated_frame, text=str(self.current_config.last_updated)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Validation
        validation_frame = ttk.LabelFrame(frame, text="Validation", padding=10)
        validation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(validation_frame, text="Validate Current Configuration",
                  command=self._validate_configuration).pack(anchor=tk.W, pady=2)
        
        self.validation_result_text = tk.Text(validation_frame, height=6, width=50)
        self.validation_result_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar for validation text
        scrollbar = ttk.Scrollbar(validation_frame, orient=tk.VERTICAL, command=self.validation_result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.validation_result_text.config(yscrollcommand=scrollbar.set)
    
    def _setup_environment_tab(self):
        """Setup environment variables tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Environment")
        
        # Environment info
        env_frame = ttk.LabelFrame(frame, text="Environment Variable Overrides", padding=10)
        env_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instructions
        instructions = tk.Text(env_frame, height=3, wrap=tk.WORD)
        instructions.pack(fill=tk.X, pady=(0, 5))
        instructions.insert(tk.END, 
            "Environment variables can override configuration values. "
            "Use the prefix 'BUDGETINATOR_' followed by the configuration key. "
            "Example: BUDGETINATOR_THEME=dark")
        instructions.config(state=tk.DISABLED)
        
        # Current environment overrides
        ttk.Label(env_frame, text="Current Environment Overrides:").pack(anchor=tk.W, pady=(10, 5))
        
        # Tree view for environment variables
        self.env_tree = ttk.Treeview(env_frame, columns=('Key', 'Value'), show='tree headings', height=8)
        self.env_tree.heading('#0', text='Variable')
        self.env_tree.heading('Key', text='Config Key')
        self.env_tree.heading('Value', text='Value')
        self.env_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(env_frame, orient=tk.VERTICAL, command=self.env_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.env_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Load environment overrides
        self._load_environment_overrides()
        
        # Refresh button
        ttk.Button(env_frame, text="Refresh Environment Variables",
                  command=self._load_environment_overrides).pack(anchor=tk.W, pady=(5, 0))
    
    def _load_current_values(self):
        """Load current configuration values into UI"""
        config_dict = self.current_config.dict()
        
        for key, var in self.ui_vars.items():
            if key in config_dict:
                value = config_dict[key]
                if isinstance(var, tk.BooleanVar):
                    var.set(value)
                elif isinstance(var, tk.IntVar):
                    var.set(value)
                else:
                    var.set(str(value))
    
    def _setup_validation(self):
        """Setup real-time validation for UI elements"""
        # Add validation callbacks to variables
        for key, var in self.ui_vars.items():
            if key in ['backup_count', 'max_recent_files', 'cache_size_mb']:
                var.trace_add('write', lambda *args, k=key: self._validate_field(k))
    
    def _validate_field(self, field_name: str):
        """Validate a specific field"""
        label = self.validation_labels.get(field_name)
        if not label:
            return
        
        try:
            value = self.ui_vars[field_name].get()
            
            # Field-specific validation
            if field_name == 'backup_count':
                if not (1 <= value <= 50):
                    label.config(text="Must be between 1 and 50")
                    return
            elif field_name == 'max_recent_files':
                if not (1 <= value <= 50):
                    label.config(text="Must be between 1 and 50")
                    return
            elif field_name == 'cache_size_mb':
                if not (10 <= value <= 1000):
                    label.config(text="Must be between 10 and 1000")
                    return
            
            # Clear validation message if valid
            label.config(text="")
            
        except (ValueError, tk.TclError):
            label.config(text="Invalid value")
    
    def _validate_configuration(self):
        """Validate current configuration and show results"""
        try:
            # Get current values from UI
            config_data = {}
            for key, var in self.ui_vars.items():
                try:
                    config_data[key] = var.get()
                except tk.TclError:
                    pass
            
            # Validate with schema
            validation_errors = self.config_manager.validate_config_data(config_data)
            
            # Show results
            self.validation_result_text.delete(1.0, tk.END)
            
            if not validation_errors:
                self.validation_result_text.insert(tk.END, "✅ Configuration is valid!")
                self.validation_result_text.config(foreground="green")
            else:
                self.validation_result_text.insert(tk.END, "❌ Validation Errors:\n\n")
                for error in validation_errors:
                    self.validation_result_text.insert(tk.END, f"• {error}\n")
                self.validation_result_text.config(foreground="red")
                
        except Exception as e:
            self.validation_result_text.delete(1.0, tk.END)
            self.validation_result_text.insert(tk.END, f"❌ Validation failed: {str(e)}")
            self.validation_result_text.config(foreground="red")
    
    def _load_environment_overrides(self):
        """Load environment variable overrides into tree view"""
        # Clear existing items
        for item in self.env_tree.get_children():
            self.env_tree.delete(item)
        
        # Get environment overrides
        env_overrides = get_env_config_override()
        
        if not env_overrides:
            self.env_tree.insert('', tk.END, text="No environment overrides found", values=('', ''))
            return
        
        # Add environment variables
        for config_key, value in env_overrides.items():
            env_var = f"BUDGETINATOR_{config_key.upper()}"
            self.env_tree.insert('', tk.END, text=env_var, values=(config_key, str(value)))
    
    def _browse_directory(self, var_name: str):
        """Browse for directory"""
        current_path = self.ui_vars[var_name].get()
        if not current_path:
            current_path = str(Path.home())
        
        directory = filedialog.askdirectory(
            title="Select Directory",
            initialdir=current_path
        )
        
        if directory:
            self.ui_vars[var_name].set(directory)
    
    def _import_config(self):
        """Import configuration from file"""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.config_manager.import_config(file_path):
                messagebox.showinfo("Success", "Configuration imported successfully!")
                self.current_config = self.config_manager.get_config()
                self._load_current_values()
            else:
                messagebox.showerror("Error", "Failed to import configuration. Check logs for details.")
    
    def _export_config(self):
        """Export configuration to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.config_manager.export_config(file_path):
                messagebox.showinfo("Success", "Configuration exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export configuration. Check logs for details.")
    
    def _reset_to_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", 
                              "This will reset all settings to default values. Continue?"):
            if self.config_manager.reset_to_defaults():
                messagebox.showinfo("Success", "Configuration reset to defaults!")
                self.current_config = self.config_manager.get_config()
                self._load_current_values()
            else:
                messagebox.showerror("Error", "Failed to reset configuration. Check logs for details.")
    
    def _apply(self):
        """Apply current changes"""
        if self._save_configuration():
            messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def _ok(self):
        """Apply changes and close dialog"""
        if self._save_configuration():
            self.dialog.destroy()
    
    def _cancel(self):
        """Cancel changes and close dialog"""
        if self.has_changes:
            if not messagebox.askyesno("Unsaved Changes", 
                                      "You have unsaved changes. Discard them?"):
                return
        self.dialog.destroy()
    
    def _save_configuration(self) -> bool:
        """Save current configuration"""
        try:
            # Collect values from UI
            config_updates = {}
            for key, var in self.ui_vars.items():
                try:
                    config_updates[key] = var.get()
                except tk.TclError:
                    continue
            
            # Update configuration
            if self.config_manager.update_config(**config_updates):
                self.current_config = self.config_manager.get_config()
                self.has_changes = False
                
                # Notify callback
                if self.on_config_changed:
                    self.on_config_changed(self.current_config)
                
                return True
            else:
                messagebox.showerror("Error", "Failed to save configuration. Check logs for details.")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            return False
    
    def _on_close(self):
        """Handle dialog close"""
        self._cancel()
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get dimensions
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


def show_enhanced_preferences(parent: tk.Tk, on_config_changed: Optional[Callable[[UserConfig], None]] = None):
    """
    Show enhanced preferences dialog.
    
    Args:
        parent: Parent window
        on_config_changed: Callback when configuration changes
    """
    dialog = EnhancedPreferencesDialog(parent, on_config_changed)
    dialog.show()


if __name__ == "__main__":
    # Test the enhanced preferences dialog
    root = tk.Tk()
    root.title("Test Enhanced Preferences")
    root.geometry("400x300")
    
    def on_config_change(config: UserConfig):
        print(f"Configuration changed: {config.dict()}")
    
    ttk.Button(root, text="Open Enhanced Preferences", 
              command=lambda: show_enhanced_preferences(root, on_config_change)).pack(pady=20)
    
    root.mainloop()
