"""
Window positioning preferences dialog.

Provides a comprehensive UI for configuring window and dialog positioning preferences.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Window positioning and sizing constants
DEFAULT_CUSTOM_X = 100
DEFAULT_CUSTOM_Y = 100
DEFAULT_LAST_POSITION_X = 200
DEFAULT_LAST_POSITION_Y = 150
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600

# Input validation constants
MIN_COORDINATE_VALUE = 0
MAX_COORDINATE_VALUE = 9999
MIN_WIDTH_VALUE = 400
MIN_HEIGHT_VALUE = 300
MAX_SIZE_VALUE = 9999

# Dialog offset constants
MIN_OFFSET_VALUE = -999
MAX_OFFSET_VALUE = 999
DEFAULT_OFFSET_X = 0
DEFAULT_OFFSET_Y = 0

# UI layout constants
MAIN_FRAME_PADDING = "10"
LABELFRAME_PADDING = "5"
NOTEBOOK_BOTTOM_PADDING = 10
BUTTON_FRAME_TOP_PADDING = 5
SPINBOX_WIDTH = 10
GRID_PADX = 5
GRID_PADY = 2
BUTTON_PADX = 5

# Preview dialog constants
PREVIEW_DIALOG_WIDTH = 300
PREVIEW_DIALOG_HEIGHT = 200
PREVIEW_BUTTON_PADY = 10


class WindowPositionPreferencesDialog:
    """Dialog for configuring window positioning preferences."""
    
    def __init__(self, parent, preferences_manager=None):
        """
        Initialize the window position preferences dialog.
        
        Args:
            parent: Parent widget
            preferences_manager: Preferences manager instance
        """
        self.parent = parent
        self.preferences_manager = preferences_manager
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Window Positioning Preferences")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Load current preferences
        self.current_prefs = self._load_current_preferences()
        
        # Create UI variables
        self._create_variables()
        
        # Build the UI
        self._create_widgets()
        
        # Center the dialog
        self._center_dialog()
        
        logger.debug("Window position preferences dialog created")
    
    def _load_current_preferences(self) -> Dict[str, Any]:
        """Load current window positioning preferences."""
        if not self.preferences_manager:
            return self._get_default_preferences()
        
        prefs = self.preferences_manager.get_preference('window_positioning')
        if not prefs:
            return self._get_default_preferences()
        
        return prefs
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default window positioning preferences."""
        return {
            "main_window": {
                "mode": "center_screen",
                "custom_x": DEFAULT_CUSTOM_X,
                "custom_y": DEFAULT_CUSTOM_Y,
                "last_position": {
                    "x": DEFAULT_LAST_POSITION_X,
                    "y": DEFAULT_LAST_POSITION_Y,
                    "width": DEFAULT_WINDOW_WIDTH,
                    "height": DEFAULT_WINDOW_HEIGHT
                },
                "remember_size": True,
                "default_size": {
                    "width": DEFAULT_WINDOW_WIDTH,
                    "height": DEFAULT_WINDOW_HEIGHT
                }
            },
            "dialogs": {
                "horizontal_alignment": "center",
                "vertical_alignment": "center",
                "custom_offset": {
                    "x": DEFAULT_OFFSET_X,
                    "y": DEFAULT_OFFSET_Y
                },
                "respect_screen_bounds": True,
                "cascade_multiple_dialogs": False
            }
        }
    
    def _create_variables(self):
        """Create tkinter variables for the preferences."""
        main_prefs = self.current_prefs.get('main_window', {})
        dialog_prefs = self.current_prefs.get('dialogs', {})
        
        # Main window variables
        self.main_mode_var = tk.StringVar(value=main_prefs.get('mode', 'center_screen'))
        self.custom_x_var = tk.IntVar(value=main_prefs.get('custom_x', DEFAULT_CUSTOM_X))
        self.custom_y_var = tk.IntVar(value=main_prefs.get('custom_y', DEFAULT_CUSTOM_Y))
        self.remember_size_var = tk.BooleanVar(value=main_prefs.get('remember_size', True))
        
        default_size = main_prefs.get('default_size', {})
        self.default_width_var = tk.IntVar(value=default_size.get('width', DEFAULT_WINDOW_WIDTH))
        self.default_height_var = tk.IntVar(value=default_size.get('height', DEFAULT_WINDOW_HEIGHT))
        
        # Dialog variables
        self.dialog_h_align_var = tk.StringVar(value=dialog_prefs.get('horizontal_alignment', 'center'))
        self.dialog_v_align_var = tk.StringVar(value=dialog_prefs.get('vertical_alignment', 'center'))
        
        custom_offset = dialog_prefs.get('custom_offset', {})
        self.dialog_offset_x_var = tk.IntVar(value=custom_offset.get('x', DEFAULT_OFFSET_X))
        self.dialog_offset_y_var = tk.IntVar(value=custom_offset.get('y', DEFAULT_OFFSET_Y))
        
        self.respect_bounds_var = tk.BooleanVar(value=dialog_prefs.get('respect_screen_bounds', True))
        self.cascade_dialogs_var = tk.BooleanVar(value=dialog_prefs.get('cascade_multiple_dialogs', False))
    
    def validate_coordinate_input(self, value):
        """Validate coordinate input for spinboxes."""
        if value == "":
            return True  # Allow empty string
        try:
            val = int(value)
            if val < MIN_COORDINATE_VALUE or val > MAX_COORDINATE_VALUE:
                return False
            return True
        except ValueError:
            return False
    
    def validate_size_input(self, value):
        """Validate size input for width/height spinboxes."""
        if value == "":
            return True  # Allow empty string
        try:
            val = int(value)
            if val < MIN_WIDTH_VALUE or val > MAX_SIZE_VALUE:
                return False
            return True
        except ValueError:
            return False
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.dialog, padding=MAIN_FRAME_PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        # Main window tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Main Window")
        self._create_main_window_tab(main_tab)
        
        # Dialog positioning tab
        dialog_tab = ttk.Frame(notebook)
        notebook.add(dialog_tab, text="Dialogs")
        self._create_dialog_tab(dialog_tab)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(BUTTON_FRAME_TOP_PADDING, 0))
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults
        ).pack(side=tk.LEFT, padx=(0, BUTTON_PADX))
        
        ttk.Button(
            button_frame,
            text="Preview",
            command=self._preview_settings
        ).pack(side=tk.LEFT, padx=BUTTON_PADX)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=(BUTTON_PADX, 0))
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        ).pack(side=tk.RIGHT)
    
    def _create_main_window_tab(self, parent):
        """Create the main window positioning tab."""
        # Positioning mode frame
        mode_frame = ttk.LabelFrame(parent, text="Window Position", padding=LABELFRAME_PADDING)
        mode_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        # Position mode options
        modes = [
            ("Center of Screen", "center_screen"),
            ("Top-Left Corner", "top_left"),
            ("Top-Right Corner", "top_right"),
            ("Bottom-Left Corner", "bottom_left"),
            ("Bottom-Right Corner", "bottom_right"),
            ("Remember Last Position", "remember_last"),
            ("Custom Coordinates", "custom")
        ]
        
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.main_mode_var,
                value=value,
                command=self._on_mode_change
            ).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=GRID_PADX, pady=GRID_PADY)
        
        # Custom coordinates frame
        self.custom_frame = ttk.LabelFrame(parent, text="Custom Coordinates", padding=LABELFRAME_PADDING)
        self.custom_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        ttk.Label(self.custom_frame, text="X Position:").grid(row=0, column=0, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            self.custom_frame,
            from_=MIN_COORDINATE_VALUE, to=MAX_COORDINATE_VALUE,
            textvariable=self.custom_x_var,
            validate='key',
            validatecommand=(self.dialog.register(self.validate_coordinate_input), '%P'),
            width=SPINBOX_WIDTH
        ).grid(row=0, column=1, padx=GRID_PADX)
        
        ttk.Label(self.custom_frame, text="Y Position:").grid(row=0, column=2, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            self.custom_frame,
            from_=MIN_COORDINATE_VALUE, to=MAX_COORDINATE_VALUE,
            textvariable=self.custom_y_var,
            validate='key',
            validatecommand=(self.dialog.register(self.validate_coordinate_input), '%P'),
            width=SPINBOX_WIDTH
        ).grid(row=0, column=3, padx=GRID_PADX)
        
        # Window size frame
        size_frame = ttk.LabelFrame(parent, text="Window Size", padding=LABELFRAME_PADDING)
        size_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        ttk.Checkbutton(
            size_frame,
            text="Remember window size",
            variable=self.remember_size_var
        ).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, GRID_PADX))
        
        ttk.Label(size_frame, text="Default Width:").grid(row=1, column=0, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            size_frame,
            from_=MIN_WIDTH_VALUE, to=MAX_SIZE_VALUE,
            textvariable=self.default_width_var,
            validate='key',
            validatecommand=(self.dialog.register(self.validate_size_input), '%P'),
            width=SPINBOX_WIDTH
        ).grid(row=1, column=1, padx=GRID_PADX)
        
        ttk.Label(size_frame, text="Default Height:").grid(row=1, column=2, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            size_frame,
            from_=MIN_HEIGHT_VALUE, to=MAX_SIZE_VALUE,
            textvariable=self.default_height_var,
            validate='key',
            validatecommand=(self.dialog.register(self.validate_size_input), '%P'),
            width=SPINBOX_WIDTH
        ).grid(row=1, column=3, padx=GRID_PADX)
        
        # Update custom frame state
        self._on_mode_change()
    
    def _create_dialog_tab(self, parent):
        """Create the dialog positioning tab."""
        # Horizontal alignment frame
        h_align_frame = ttk.LabelFrame(parent, text="Horizontal Alignment", padding=LABELFRAME_PADDING)
        h_align_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        h_alignments = [
            ("Centered", "center"),
            ("Left-Aligned", "left"),
            ("Right-Aligned", "right"),
            ("Top-Left Corner", "top_left"),
            ("Top-Right Corner", "top_right"),
            ("Bottom-Left Corner", "bottom_left"),
            ("Bottom-Right Corner", "bottom_right"),
            ("Custom Offset", "custom")
        ]
        
        for i, (text, value) in enumerate(h_alignments):
            ttk.Radiobutton(
                h_align_frame,
                text=text,
                variable=self.dialog_h_align_var,
                value=value,
                command=self._on_dialog_alignment_change
            ).grid(row=i // 2, column=i % 2, sticky=tk.W, padx=GRID_PADX, pady=GRID_PADY)
        
        # Vertical alignment frame
        v_align_frame = ttk.LabelFrame(parent, text="Vertical Alignment", padding=LABELFRAME_PADDING)
        v_align_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        v_alignments = [
            ("Centered", "center"),
            ("Top-Aligned", "top"),
            ("Bottom-Aligned", "bottom")
        ]
        
        for i, (text, value) in enumerate(v_alignments):
            ttk.Radiobutton(
                v_align_frame,
                text=text,
                variable=self.dialog_v_align_var,
                value=value
            ).grid(row=0, column=i, sticky=tk.W, padx=GRID_PADX, pady=GRID_PADY)
        
        # Custom offset frame
        self.offset_frame = ttk.LabelFrame(parent, text="Custom Offset", padding=LABELFRAME_PADDING)
        self.offset_frame.pack(fill=tk.X, pady=(0, NOTEBOOK_BOTTOM_PADDING))
        
        ttk.Label(self.offset_frame, text="X Offset:").grid(row=0, column=0, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            self.offset_frame,
            from_=MIN_OFFSET_VALUE, to=MAX_OFFSET_VALUE,
            textvariable=self.dialog_offset_x_var,
            width=SPINBOX_WIDTH
        ).grid(row=0, column=1, padx=GRID_PADX)
        
        ttk.Label(self.offset_frame, text="Y Offset:").grid(row=0, column=2, sticky=tk.W, padx=GRID_PADX)
        ttk.Spinbox(
            self.offset_frame,
            from_=MIN_OFFSET_VALUE, to=MAX_OFFSET_VALUE,
            textvariable=self.dialog_offset_y_var,
            width=SPINBOX_WIDTH
        ).grid(row=0, column=3, padx=GRID_PADX)
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding=LABELFRAME_PADDING)
        advanced_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(
            advanced_frame,
            text="Keep dialogs within screen bounds",
            variable=self.respect_bounds_var
        ).pack(anchor=tk.W, pady=GRID_PADY)
        
        ttk.Checkbutton(
            advanced_frame,
            text="Cascade multiple dialogs",
            variable=self.cascade_dialogs_var
        ).pack(anchor=tk.W, pady=GRID_PADY)
        
        # Update offset frame state
        self._on_dialog_alignment_change()
    
    def _on_mode_change(self):
        """Handle main window mode change."""
        mode = self.main_mode_var.get()
        if mode == "custom":
            self._enable_frame(self.custom_frame)
        else:
            self._disable_frame(self.custom_frame)
    
    def _on_dialog_alignment_change(self):
        """Handle dialog alignment change."""
        h_align = self.dialog_h_align_var.get()
        if h_align == "custom":
            self._enable_frame(self.offset_frame)
        else:
            self._disable_frame(self.offset_frame)
    
    def _enable_frame(self, frame):
        """Enable all widgets in a frame."""
        for child in frame.winfo_children():
            child.configure(state='normal')
    
    def _disable_frame(self, frame):
        """Disable all widgets in a frame."""
        for child in frame.winfo_children():
            if hasattr(child, 'configure'):
                child.configure(state='disabled')
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset to Defaults",
                               "Are you sure you want to reset all window positioning settings to defaults?"):
            defaults = self._get_default_preferences()
            self.current_prefs = defaults
            self._create_variables()
            self._on_mode_change()
            self._on_dialog_alignment_change()
    
    def _preview_settings(self):
        """Preview the current settings."""
        # Create a small preview dialog to show positioning
        preview = tk.Toplevel(self.dialog)
        preview.title("Preview")
        preview.geometry(f"{PREVIEW_DIALOG_WIDTH}x{PREVIEW_DIALOG_HEIGHT}")
        
        ttk.Label(
            preview,
            text="This is a preview of dialog positioning\nwith your current settings.",
            justify=tk.CENTER
        ).pack(expand=True)
        
        ttk.Button(
            preview,
            text="Close Preview",
            command=preview.destroy
        ).pack(pady=PREVIEW_BUTTON_PADY)
        
        # Position the preview according to current settings
        try:
            from utils.window_positioning import position_dialog
            # Temporarily apply current settings for preview
            position_dialog(preview, self.dialog, "preview")
        except ImportError:
            # Fallback positioning
            preview.transient(self.dialog)
    
    def _center_dialog(self):
        """Center this dialog on parent."""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _on_save(self):
        """Save the preferences and close dialog."""
        try:
            # Build preferences dictionary
            preferences = {
                "main_window": {
                    "mode": self.main_mode_var.get(),
                    "custom_x": self.custom_x_var.get(),
                    "custom_y": self.custom_y_var.get(),
                    "last_position": self.current_prefs.get('main_window', {}).get('last_position', {
                        "x": DEFAULT_LAST_POSITION_X, "y": DEFAULT_LAST_POSITION_Y,
                        "width": DEFAULT_WINDOW_WIDTH, "height": DEFAULT_WINDOW_HEIGHT
                    }),
                    "remember_size": self.remember_size_var.get(),
                    "default_size": {
                        "width": self.default_width_var.get(),
                        "height": self.default_height_var.get()
                    }
                },
                "dialogs": {
                    "horizontal_alignment": self.dialog_h_align_var.get(),
                    "vertical_alignment": self.dialog_v_align_var.get(),
                    "custom_offset": {
                        "x": self.dialog_offset_x_var.get(),
                        "y": self.dialog_offset_y_var.get()
                    },
                    "respect_screen_bounds": self.respect_bounds_var.get(),
                    "cascade_multiple_dialogs": self.cascade_dialogs_var.get()
                }
            }
            
            # Save preferences
            if self.preferences_manager:
                self.preferences_manager.set_preference('window_positioning', preferences)
                messagebox.showinfo("Success", "Window positioning preferences saved successfully!")
            
            self.result = preferences
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save window positioning preferences: {e}")
            messagebox.showerror("Error", f"Failed to save preferences:\n{str(e)}")
    
    def _on_cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.dialog.destroy()


def show_position_preferences_dialog(parent, preferences_manager=None) -> Optional[Dict[str, Any]]:
    """
    Show the window position preferences dialog.
    
    Args:
        parent: Parent widget
        preferences_manager: Preferences manager instance
        
    Returns:
        Dictionary of preferences if saved, None if cancelled
    """
    dialog = WindowPositionPreferencesDialog(parent, preferences_manager)
    parent.wait_window(dialog.dialog)
    return dialog.result