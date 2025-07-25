"""
Theme Manager for ProjectBudgetinator.

This module provides comprehensive theming support for the application,
including light and dark themes that affect all UI components.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional


class ThemeManager:
    """Manages application themes and applies them to UI components."""
    
    def __init__(self):
        """Initialize the theme manager."""
        self.logger = logging.getLogger("ProjectBudgetinator.theme")
        self.current_theme = "light"
        self._style = None
        
        # Define theme configurations
        self.themes = {
            "light": {
                "name": "Light Theme",
                "colors": {
                    # Main colors
                    "bg": "#f0f0f0",           # Main background
                    "fg": "#000000",           # Main foreground (text)
                    "select_bg": "#0078d4",    # Selection background
                    "select_fg": "#ffffff",    # Selection foreground
                    
                    # Window colors
                    "window_bg": "#ffffff",    # Window background
                    "frame_bg": "#f0f0f0",     # Frame background
                    "panel_bg": "#fafafa",     # Panel background
                    
                    # Input colors
                    "entry_bg": "#ffffff",     # Entry background
                    "entry_fg": "#000000",     # Entry foreground
                    "entry_border": "#cccccc", # Entry border
                    "entry_focus": "#0078d4",  # Entry focus border
                    
                    # Button colors
                    "button_bg": "#e1e1e1",    # Button background
                    "button_fg": "#000000",    # Button foreground
                    "button_hover": "#d0d0d0", # Button hover
                    "button_active": "#c0c0c0", # Button active
                    
                    # Menu colors
                    "menu_bg": "#f0f0f0",      # Menu background
                    "menu_fg": "#000000",      # Menu foreground
                    "menu_select": "#0078d4",  # Menu selection
                    
                    # Status colors
                    "success": "#107c10",      # Success color
                    "warning": "#ff8c00",      # Warning color
                    "error": "#d13438",        # Error color
                    "info": "#0078d4",         # Info color
                    
                    # Border colors
                    "border": "#cccccc",       # General border
                    "border_focus": "#0078d4", # Focused border
                    "border_disabled": "#e0e0e0", # Disabled border
                }
            },
            "dark": {
                "name": "Dark Theme",
                "colors": {
                    # Main colors
                    "bg": "#2d2d30",           # Main background
                    "fg": "#ffffff",           # Main foreground (text)
                    "select_bg": "#0e639c",    # Selection background
                    "select_fg": "#ffffff",    # Selection foreground
                    
                    # Window colors
                    "window_bg": "#1e1e1e",    # Window background
                    "frame_bg": "#2d2d30",     # Frame background
                    "panel_bg": "#252526",     # Panel background
                    
                    # Input colors
                    "entry_bg": "#3c3c3c",     # Entry background
                    "entry_fg": "#ffffff",     # Entry foreground
                    "entry_border": "#555555", # Entry border
                    "entry_focus": "#007acc",  # Entry focus border
                    
                    # Button colors
                    "button_bg": "#0e639c",    # Button background
                    "button_fg": "#ffffff",    # Button foreground
                    "button_hover": "#1177bb", # Button hover
                    "button_active": "#094771", # Button active
                    
                    # Menu colors
                    "menu_bg": "#2d2d30",      # Menu background
                    "menu_fg": "#ffffff",      # Menu foreground
                    "menu_select": "#094771",  # Menu selection
                    
                    # Status colors
                    "success": "#4ec9b0",      # Success color
                    "warning": "#ffcc02",      # Warning color
                    "error": "#f44747",        # Error color
                    "info": "#007acc",         # Info color
                    
                    # Border colors
                    "border": "#555555",       # General border
                    "border_focus": "#007acc", # Focused border
                    "border_disabled": "#404040", # Disabled border
                }
            }
        }
    
    def initialize_style(self, root: tk.Tk):
        """Initialize the ttk style system."""
        try:
            self._style = ttk.Style(root)
            self.logger.info("TTK Style system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTK style: {e}")
            raise
    
    def get_theme_names(self) -> list:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def get_current_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get colors for specified theme or current theme."""
        theme_name = theme_name or self.current_theme
        if theme_name not in self.themes:
            self.logger.warning(f"Theme '{theme_name}' not found, using light theme")
            theme_name = "light"
        return self.themes[theme_name]["colors"]
    
    def set_theme(self, theme_name: str):
        """Set the current theme."""
        if theme_name not in self.themes:
            self.logger.error(f"Theme '{theme_name}' not found")
            return False
        
        self.current_theme = theme_name
        self.logger.info(f"Theme set to: {theme_name}")
        return True
    
    def apply_theme(self, root: tk.Tk, theme_name: Optional[str] = None):
        """Apply theme to the application."""
        if theme_name:
            self.set_theme(theme_name)
        
        colors = self.get_theme_colors()
        
        try:
            # Apply theme to root window
            self._apply_root_theme(root, colors)
            
            # Apply theme to TTK widgets
            if self._style:
                self._apply_ttk_theme(colors)
            
            # Apply theme to standard tkinter widgets
            self._apply_tk_theme(root, colors)
            
            self.logger.info(f"Applied {self.current_theme} theme successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
            raise
    
    def _apply_root_theme(self, root: tk.Tk, colors: Dict[str, str]):
        """Apply theme to root window."""
        root.configure(
            bg=colors["window_bg"],
            highlightbackground=colors["border"],
            highlightcolor=colors["border_focus"]
        )
    
    def _apply_ttk_theme(self, colors: Dict[str, str]):
        """Apply theme to TTK widgets."""
        if not self._style:
            return
        
        # Configure TTK Button
        self._style.configure(
            "TButton",
            background=colors["button_bg"],
            foreground=colors["button_fg"],
            borderwidth=1,
            focuscolor=colors["border_focus"],
            relief="raised"
        )
        
        self._style.map(
            "TButton",
            background=[
                ("active", colors["button_hover"]),
                ("pressed", colors["button_active"]),
                ("disabled", colors["border_disabled"])
            ],
            foreground=[
                ("disabled", colors["border"])
            ]
        )
        
        # Configure TTK Entry
        self._style.configure(
            "TEntry",
            fieldbackground=colors["entry_bg"],
            foreground=colors["entry_fg"],
            borderwidth=1,
            insertcolor=colors["entry_fg"]
        )
        
        self._style.map(
            "TEntry",
            focuscolor=[("focus", colors["entry_focus"])],
            bordercolor=[("focus", colors["entry_focus"])]
        )
        
        # Configure TTK Label
        self._style.configure(
            "TLabel",
            background=colors["frame_bg"],
            foreground=colors["fg"]
        )
        
        # Configure TTK Frame
        self._style.configure(
            "TFrame",
            background=colors["frame_bg"],
            borderwidth=0
        )
        
        # Configure TTK LabelFrame
        self._style.configure(
            "TLabelframe",
            background=colors["frame_bg"],
            foreground=colors["fg"],
            borderwidth=1,
            relief="groove"
        )
        
        self._style.configure(
            "TLabelframe.Label",
            background=colors["frame_bg"],
            foreground=colors["fg"]
        )
        
        # Configure TTK Combobox
        self._style.configure(
            "TCombobox",
            fieldbackground=colors["entry_bg"],
            background=colors["button_bg"],
            foreground=colors["entry_fg"],
            arrowcolor=colors["fg"],
            borderwidth=1
        )
        
        # Configure TTK Checkbutton
        self._style.configure(
            "TCheckbutton",
            background=colors["frame_bg"],
            foreground=colors["fg"],
            focuscolor=colors["border_focus"]
        )
        
        # Configure TTK Radiobutton
        self._style.configure(
            "TRadiobutton",
            background=colors["frame_bg"],
            foreground=colors["fg"],
            focuscolor=colors["border_focus"]
        )
        
        # Configure TTK Progressbar
        self._style.configure(
            "TProgressbar",
            background=colors["select_bg"],
            troughcolor=colors["border"],
            borderwidth=1,
            lightcolor=colors["border"],
            darkcolor=colors["border"]
        )
        
        # Configure TTK Treeview
        self._style.configure(
            "Treeview",
            background=colors["entry_bg"],
            foreground=colors["entry_fg"],
            fieldbackground=colors["entry_bg"],
            borderwidth=1
        )
        
        self._style.configure(
            "Treeview.Heading",
            background=colors["button_bg"],
            foreground=colors["button_fg"],
            relief="raised",
            borderwidth=1
        )
        
        # Configure TTK Notebook
        self._style.configure(
            "TNotebook",
            background=colors["frame_bg"],
            borderwidth=1,
            tabmargins=[2, 5, 2, 0]
        )
        
        self._style.configure(
            "TNotebook.Tab",
            background=colors["button_bg"],
            foreground=colors["button_fg"],
            padding=[12, 8, 12, 8]
        )
        
        self._style.map(
            "TNotebook.Tab",
            background=[
                ("selected", colors["select_bg"]),
                ("active", colors["button_hover"])
            ],
            foreground=[
                ("selected", colors["select_fg"])
            ]
        )
    
    def _apply_tk_theme(self, root: tk.Tk, colors: Dict[str, str]):
        """Apply theme to standard tkinter widgets recursively."""
        self._apply_widget_theme(root, colors)
    
    def _apply_widget_theme(self, widget, colors: Dict[str, str]):
        """Apply theme to a widget and all its children."""
        try:
            widget_class = widget.winfo_class()
            
            # Apply theme based on widget type
            if widget_class == "Toplevel":
                widget.configure(bg=colors["window_bg"])
            elif widget_class == "Frame":
                widget.configure(
                    bg=colors["frame_bg"],
                    highlightbackground=colors["border"]
                )
            elif widget_class == "Label":
                widget.configure(
                    bg=colors["frame_bg"],
                    fg=colors["fg"]
                )
            elif widget_class == "Button":
                widget.configure(
                    bg=colors["button_bg"],
                    fg=colors["button_fg"],
                    activebackground=colors["button_hover"],
                    activeforeground=colors["button_fg"],
                    highlightbackground=colors["border"],
                    highlightcolor=colors["border_focus"]
                )
            elif widget_class == "Entry":
                widget.configure(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    insertbackground=colors["entry_fg"],
                    selectbackground=colors["select_bg"],
                    selectforeground=colors["select_fg"],
                    highlightbackground=colors["entry_border"],
                    highlightcolor=colors["entry_focus"]
                )
            elif widget_class == "Text":
                widget.configure(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    insertbackground=colors["entry_fg"],
                    selectbackground=colors["select_bg"],
                    selectforeground=colors["select_fg"],
                    highlightbackground=colors["entry_border"],
                    highlightcolor=colors["entry_focus"]
                )
            elif widget_class == "Listbox":
                widget.configure(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    selectbackground=colors["select_bg"],
                    selectforeground=colors["select_fg"],
                    highlightbackground=colors["entry_border"],
                    highlightcolor=colors["entry_focus"]
                )
            elif widget_class == "Checkbutton":
                widget.configure(
                    bg=colors["frame_bg"],
                    fg=colors["fg"],
                    activebackground=colors["frame_bg"],
                    activeforeground=colors["fg"],
                    selectcolor=colors["entry_bg"],
                    highlightbackground=colors["border"]
                )
            elif widget_class == "Radiobutton":
                widget.configure(
                    bg=colors["frame_bg"],
                    fg=colors["fg"],
                    activebackground=colors["frame_bg"],
                    activeforeground=colors["fg"],
                    selectcolor=colors["entry_bg"],
                    highlightbackground=colors["border"]
                )
            elif widget_class == "Menu":
                widget.configure(
                    bg=colors["menu_bg"],
                    fg=colors["menu_fg"],
                    activebackground=colors["menu_select"],
                    activeforeground=colors["select_fg"],
                    selectcolor=colors["select_bg"]
                )
            elif widget_class == "Menubutton":
                widget.configure(
                    bg=colors["button_bg"],
                    fg=colors["button_fg"],
                    activebackground=colors["button_hover"],
                    activeforeground=colors["button_fg"]
                )
            elif widget_class == "Scale":
                widget.configure(
                    bg=colors["frame_bg"],
                    fg=colors["fg"],
                    activebackground=colors["select_bg"],
                    highlightbackground=colors["border"],
                    troughcolor=colors["entry_bg"]
                )
            elif widget_class == "Scrollbar":
                widget.configure(
                    bg=colors["button_bg"],
                    activebackground=colors["button_hover"],
                    troughcolor=colors["frame_bg"],
                    highlightbackground=colors["border"]
                )
            
            # Recursively apply to children
            for child in widget.winfo_children():
                self._apply_widget_theme(child, colors)
                
        except tk.TclError:
            # Some widgets might not support certain options
            pass
        except Exception as e:
            self.logger.debug(f"Error applying theme to widget {widget}: {e}")
    
    def create_themed_dialog(self, parent, title: str, geometry: str = "400x300") -> tk.Toplevel:
        """Create a new dialog window with current theme applied."""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry(geometry)
        
        # Apply theme to the new dialog
        colors = self.get_theme_colors()
        self._apply_widget_theme(dialog, colors)
        
        return dialog
    
    def update_menu_theme(self, menubar: tk.Menu):
        """Update menu theme specifically."""
        colors = self.get_theme_colors()
        
        def update_menu_recursive(menu):
            try:
                menu.configure(
                    bg=colors["menu_bg"],
                    fg=colors["menu_fg"],
                    activebackground=colors["menu_select"],
                    activeforeground=colors["select_fg"]
                )
                
                # Update submenus
                for i in range(menu.index("end") + 1):
                    try:
                        submenu = menu.entrycget(i, "menu")
                        if submenu:
                            submenu_widget = menu.nametowidget(submenu)
                            update_menu_recursive(submenu_widget)
                    except (tk.TclError, AttributeError):
                        continue
                        
            except tk.TclError:
                pass
        
        update_menu_recursive(menubar)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme_to_app(root: tk.Tk, theme_name: str):
    """Apply theme to the entire application."""
    theme_manager = get_theme_manager()
    
    # Initialize style if not already done
    if theme_manager._style is None:
        theme_manager.initialize_style(root)
    
    # Apply the theme
    theme_manager.apply_theme(root, theme_name)
    
    # Update menu if it exists
    try:
        menubar = root.cget("menu")
        if menubar:
            menu_widget = root.nametowidget(menubar)
            theme_manager.update_menu_theme(menu_widget)
    except (tk.TclError, AttributeError):
        pass


def get_theme_color(color_name: str, theme_name: Optional[str] = None) -> str:
    """Get a specific color from the current or specified theme."""
    theme_manager = get_theme_manager()
    colors = theme_manager.get_theme_colors(theme_name)
    return colors.get(color_name, "#000000")  # Default to black if color not found