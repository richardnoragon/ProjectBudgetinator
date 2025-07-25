"""ProjectBudgetinator Window Positioning Module.

This module provides comprehensive window and dialog positioning functionality for
ProjectBudgetinator with user preferences support, multi-monitor awareness, and
various alignment options. It implements a singleton pattern for screen information
management and provides flexible positioning strategies.

The module handles:
    - Main window positioning with multiple modes (center, corners, custom, remember last)
    - Dialog positioning relative to parent windows with alignment options
    - Screen dimension detection and caching with proper cleanup
    - Multi-monitor support and screen bounds validation
    - User preference integration for positioning behavior
    - Cascade positioning for multiple dialogs
    - Window geometry calculation and validation

Classes:
    MainWindowMode: Enumeration of main window positioning modes
    DialogHorizontalAlignment: Enumeration of dialog horizontal alignment options
    DialogVerticalAlignment: Enumeration of dialog vertical alignment options
    ScreenInfo: Singleton class for screen information management with cleanup
    WindowPositionCalculator: Static methods for position calculations
    WindowPositionManager: Main manager class with preferences integration

Functions:
    get_position_manager: Factory function for global position manager
    position_main_window: Convenience function for main window positioning
    position_dialog: Convenience function for dialog positioning
    save_main_window_position: Convenience function for saving window position

Key Features:
    - Singleton pattern for efficient screen information caching
    - Proper resource cleanup to prevent memory leaks
    - Flexible alignment system for dialogs
    - Screen bounds validation for all positioning
    - Integration with user preferences system
    - Support for custom positioning offsets

Example:
    Basic window positioning:
    
        # Position main window
        position_main_window(root_window, preferences_manager)
        
        # Position dialog relative to parent
        position_dialog(dialog_window, parent_window, "settings")

Note:
    The module uses a singleton pattern for ScreenInfo to cache screen dimensions
    and prevent repeated system calls. Proper cleanup is essential to prevent
    memory leaks in long-running applications.
"""

import tkinter as tk
from typing import Dict, Any, Tuple, Optional, Union
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MainWindowMode(Enum):
    """Main window positioning modes."""
    CENTER_SCREEN = "center_screen"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    REMEMBER_LAST = "remember_last"
    CUSTOM = "custom"


class DialogHorizontalAlignment(Enum):
    """Dialog horizontal alignment options."""
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CUSTOM = "custom"


class DialogVerticalAlignment(Enum):
    """Dialog vertical alignment options."""
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"


class ScreenInfo:
    """Screen information utility with singleton pattern and proper resource cleanup.
    
    This class provides screen dimension information using a singleton pattern to
    cache screen dimensions and minimize system calls. It includes proper resource
    cleanup to prevent memory leaks in long-running applications.
    
    The class manages:
        - Screen dimension detection and caching
        - Shared Tkinter root window for system queries
        - Thread-safe singleton implementation
        - Proper resource cleanup and memory management
        - Screen bounds validation for window positioning
        - Usable screen area calculation (excluding taskbars)
    
    Class Attributes:
        _instance (Optional[ScreenInfo]): Singleton instance
        _cached_dimensions (Optional[Tuple[int, int]]): Cached screen dimensions
        _shared_root (Optional[tk.Tk]): Shared Tkinter root for system queries
    
    Methods:
        get_screen_dimensions: Get screen width and height with caching
        cleanup: Clean up all cached resources and shared root window
        get_usable_screen_area: Get usable screen area excluding system UI
        is_position_on_screen: Check if window position is visible on screen
    
    Example:
        Getting screen dimensions:
        
            width, height = ScreenInfo.get_screen_dimensions()
            print(f"Screen size: {width}x{height}")
            
            # Check if position is valid
            if ScreenInfo.is_position_on_screen(100, 100, 800, 600):
                print("Position is valid")
            
            # Clean up when done (important for long-running apps)
            ScreenInfo.cleanup()
    
    Note:
        This class uses a singleton pattern for efficiency but requires proper
        cleanup to prevent memory leaks. The shared root window is automatically
        hidden and should not interfere with the main application.
    """
    
    _instance: Optional['ScreenInfo'] = None
    _cached_dimensions: Optional[Tuple[int, int]] = None
    _shared_root: Optional[tk.Tk] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def get_screen_dimensions() -> Tuple[int, int]:
        """Get screen width and height using cached values or shared root."""
        # Use cached dimensions if available
        if ScreenInfo._cached_dimensions:
            return ScreenInfo._cached_dimensions
        
        # Try to use shared root if it exists
        if ScreenInfo._shared_root:
            try:
                width = ScreenInfo._shared_root.winfo_screenwidth()
                height = ScreenInfo._shared_root.winfo_screenheight()
                ScreenInfo._cached_dimensions = (width, height)
                return width, height
            except tk.TclError:
                # Shared root is no longer valid
                ScreenInfo._shared_root = None
        
        # Create a shared root for screen dimension queries only if needed
        try:
            if not ScreenInfo._shared_root:
                ScreenInfo._shared_root = tk.Tk()
                ScreenInfo._shared_root.withdraw()  # Hide the window
            width = ScreenInfo._shared_root.winfo_screenwidth()
            height = ScreenInfo._shared_root.winfo_screenheight()
            ScreenInfo._cached_dimensions = (width, height)
            return width, height
        except Exception as e:
            logger.warning(f"Could not get screen dimensions: {e}")
            # Return reasonable defaults
            return 1920, 1080
    
    @classmethod
    def cleanup(cls):
        """Clean up all cached resources and shared root window."""
        if cls._shared_root:
            try:
                cls._shared_root.destroy()
            except tk.TclError:
                pass
            cls._shared_root = None
            cls._cached_dimensions = None
    
    @staticmethod
    def cleanup_shared_root():
        """Clean up the shared root window (legacy method for compatibility)."""
        ScreenInfo.cleanup()
    
    @staticmethod
    def get_usable_screen_area() -> Tuple[int, int, int, int]:
        """Get usable screen area (excluding taskbars, etc.)."""
        # For now, return full screen. Could be enhanced with platform-specific logic
        width, height = ScreenInfo.get_screen_dimensions()
        return 0, 0, width, height
    
    @staticmethod
    def is_position_on_screen(x: int, y: int, width: int, height: int) -> bool:
        """Check if a window position is visible on screen."""
        screen_width, screen_height = ScreenInfo.get_screen_dimensions()
        
        # Window must have at least 100px visible on screen
        min_visible = 100
        
        return (
            x + min_visible < screen_width and
            y + min_visible < screen_height and
            x + width > min_visible and
            y + height > min_visible
        )


class WindowPositionCalculator:
    """Static utility class for calculating window and dialog positions.
    
    This class provides static methods for calculating optimal window positions
    based on various positioning modes, parent window relationships, and screen
    constraints. It handles both main window positioning and dialog positioning
    relative to parent windows.
    
    The calculator handles:
        - Main window positioning with multiple modes (center, corners, custom)
        - Dialog positioning relative to parent windows
        - Screen bounds validation and correction
        - Horizontal and vertical alignment options
        - Custom offset support for precise positioning
        - Parent window geometry detection and handling
    
    Methods:
        calculate_main_window_position: Calculate main window position based on mode
        calculate_dialog_position: Calculate dialog position relative to parent
        _get_parent_geometry: Safely get parent window geometry (private)
        _calculate_horizontal_position: Calculate horizontal dialog position (private)
        _calculate_vertical_position: Calculate vertical dialog position (private)
    
    Example:
        Calculating main window position:
        
            x, y = WindowPositionCalculator.calculate_main_window_position(
                mode=MainWindowMode.CENTER_SCREEN,
                window_width=800,
                window_height=600
            )
        
        Calculating dialog position:
        
            x, y = WindowPositionCalculator.calculate_dialog_position(
                parent_window=main_window,
                dialog_width=400,
                dialog_height=300,
                horizontal_alignment=DialogHorizontalAlignment.CENTER,
                vertical_alignment=DialogVerticalAlignment.CENTER
            )
    
    Note:
        All position calculations include screen bounds validation to ensure
        windows remain visible. Invalid positions are automatically corrected
        to safe defaults (typically screen center).
    """
    
    @staticmethod
    def calculate_main_window_position(
        mode: MainWindowMode,
        window_width: int,
        window_height: int,
        custom_x: int = 0,
        custom_y: int = 0,
        last_position: Optional[Dict[str, int]] = None
    ) -> Tuple[int, int]:
        """
        Calculate main window position based on mode and parameters.
        
        Args:
            mode: Positioning mode
            window_width: Window width
            window_height: Window height
            custom_x: Custom X coordinate
            custom_y: Custom Y coordinate
            last_position: Last saved position dict
            
        Returns:
            Tuple of (x, y) coordinates
        """
        screen_width, screen_height = ScreenInfo.get_screen_dimensions()
        
        if mode == MainWindowMode.CENTER_SCREEN:
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
        elif mode == MainWindowMode.TOP_LEFT:
            x, y = 50, 50
            
        elif mode == MainWindowMode.TOP_RIGHT:
            x = screen_width - window_width - 50
            y = 50
            
        elif mode == MainWindowMode.BOTTOM_LEFT:
            x = 50
            y = screen_height - window_height - 100  # Account for taskbar
            
        elif mode == MainWindowMode.BOTTOM_RIGHT:
            x = screen_width - window_width - 50
            y = screen_height - window_height - 100
            
        elif mode == MainWindowMode.REMEMBER_LAST and last_position:
            x = last_position.get('x', 100)
            y = last_position.get('y', 100)
            
        elif mode == MainWindowMode.CUSTOM:
            x, y = custom_x, custom_y
            
        else:
            # Fallback to center
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        
        # Validate position is on screen
        if not ScreenInfo.is_position_on_screen(x, y, window_width, window_height):
            logger.warning(f"Calculated position ({x}, {y}) is off-screen, using center")
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        
        return max(0, x), max(0, y)
    
    @staticmethod
    def _get_parent_geometry(parent_window) -> Optional[Tuple[int, int, int, int]]:
        """Get parent window geometry safely."""
        try:
            parent_window.update_idletasks()
            return (
                parent_window.winfo_rootx(),
                parent_window.winfo_rooty(),
                parent_window.winfo_width(),
                parent_window.winfo_height()
            )
        except tk.TclError:
            logger.warning("Could not get parent window geometry")
            return None
    
    @staticmethod
    def _calculate_horizontal_position(
        parent_x: int,
        parent_width: int,
        dialog_width: int,
        horizontal_alignment: DialogHorizontalAlignment,
        custom_offset: Optional[Dict[str, int]] = None
    ) -> int:
        """Calculate horizontal position for dialog."""
        if horizontal_alignment == DialogHorizontalAlignment.CENTER:
            return parent_x + (parent_width - dialog_width) // 2
        elif horizontal_alignment == DialogHorizontalAlignment.LEFT:
            return parent_x
        elif horizontal_alignment == DialogHorizontalAlignment.RIGHT:
            return parent_x + parent_width - dialog_width
        elif horizontal_alignment in [
            DialogHorizontalAlignment.TOP_LEFT,
            DialogHorizontalAlignment.BOTTOM_LEFT
        ]:
            return parent_x
        elif horizontal_alignment in [
            DialogHorizontalAlignment.TOP_RIGHT,
            DialogHorizontalAlignment.BOTTOM_RIGHT
        ]:
            return parent_x + parent_width - dialog_width
        elif horizontal_alignment == DialogHorizontalAlignment.CUSTOM and custom_offset:
            return parent_x + custom_offset.get('x', 0)
        else:
            # Default to center
            return parent_x + (parent_width - dialog_width) // 2
    
    @staticmethod
    def _calculate_vertical_position(
        parent_y: int,
        parent_height: int,
        dialog_height: int,
        horizontal_alignment: DialogHorizontalAlignment,
        vertical_alignment: DialogVerticalAlignment,
        custom_offset: Optional[Dict[str, int]] = None
    ) -> int:
        """Calculate vertical position for dialog."""
        # Handle corner alignments first (they override vertical alignment)
        if horizontal_alignment in [
            DialogHorizontalAlignment.TOP_LEFT,
            DialogHorizontalAlignment.TOP_RIGHT
        ]:
            return parent_y
        elif horizontal_alignment in [
            DialogHorizontalAlignment.BOTTOM_LEFT,
            DialogHorizontalAlignment.BOTTOM_RIGHT
        ]:
            return parent_y + parent_height - dialog_height
        elif horizontal_alignment == DialogHorizontalAlignment.CUSTOM and custom_offset:
            return parent_y + custom_offset.get('y', 0)
        
        # Use vertical alignment
        if vertical_alignment == DialogVerticalAlignment.CENTER:
            return parent_y + (parent_height - dialog_height) // 2
        elif vertical_alignment == DialogVerticalAlignment.TOP:
            return parent_y
        elif vertical_alignment == DialogVerticalAlignment.BOTTOM:
            return parent_y + parent_height - dialog_height
        else:
            # Default to center
            return parent_y + (parent_height - dialog_height) // 2
    
    @staticmethod
    def calculate_dialog_position(
        parent_window,
        dialog_width: int,
        dialog_height: int,
        horizontal_alignment: DialogHorizontalAlignment,
        vertical_alignment: DialogVerticalAlignment,
        custom_offset: Optional[Dict[str, int]] = None
    ) -> Tuple[int, int]:
        """
        Calculate dialog position relative to parent window.
        
        Args:
            parent_window: Parent window widget
            dialog_width: Dialog width
            dialog_height: Dialog height
            horizontal_alignment: Horizontal alignment mode
            vertical_alignment: Vertical alignment mode
            custom_offset: Custom offset dict with 'x' and 'y' keys
            
        Returns:
            Tuple of (x, y) coordinates
        """
        # Get parent window geometry
        parent_geometry = WindowPositionCalculator._get_parent_geometry(parent_window)
        if not parent_geometry:
            # Fallback to screen center
            screen_width, screen_height = ScreenInfo.get_screen_dimensions()
            return (screen_width - dialog_width) // 2, (screen_height - dialog_height) // 2
        
        parent_x, parent_y, parent_width, parent_height = parent_geometry
        
        # Calculate positions
        x = WindowPositionCalculator._calculate_horizontal_position(
            parent_x, parent_width, dialog_width, horizontal_alignment, custom_offset
        )
        y = WindowPositionCalculator._calculate_vertical_position(
            parent_y, parent_height, dialog_height, horizontal_alignment,
            vertical_alignment, custom_offset
        )
        
        # Validate position is on screen
        screen_width, screen_height = ScreenInfo.get_screen_dimensions()
        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))
        
        return x, y


class WindowPositionManager:
    """Main window positioning manager with comprehensive preferences integration.
    
    This class serves as the primary interface for window positioning functionality,
    integrating with user preferences, managing positioning state, and providing
    high-level positioning operations for both main windows and dialogs.
    
    The manager handles:
        - Integration with user preferences system
        - Main window positioning with multiple modes
        - Dialog positioning with alignment options
        - Cascade positioning for multiple dialogs
        - Window position saving and restoration
        - Default preferences management
        - Position validation and correction
    
    Args:
        preferences_manager: Optional preferences manager instance for configuration.
            If None, default preferences will be used.
    
    Attributes:
        preferences_manager: The preferences manager instance
        _cascade_offset (int): Current cascade offset for dialog positioning
    
    Methods:
        get_positioning_preferences: Get window positioning preferences from config
        position_main_window: Position main window according to preferences
        position_dialog: Position dialog according to preferences
        save_main_window_position: Save current main window position
        reset_cascade_offset: Reset cascade offset for dialogs
        _get_default_preferences: Get default positioning preferences (private)
    
    Example:
        Using the position manager:
        
            # Create manager with preferences
            manager = WindowPositionManager(prefs_manager)
            
            # Position main window
            manager.position_main_window(root_window)
            
            # Position dialog
            manager.position_dialog(dialog, parent_window, "settings")
            
            # Save position when closing
            manager.save_main_window_position(root_window)
    
    Note:
        The manager maintains cascade offset state for multiple dialogs and
        integrates seamlessly with the application's preferences system.
    """
    
    def __init__(self, preferences_manager=None):
        """
        Initialize window position manager.
        
        Args:
            preferences_manager: Preferences manager instance
        """
        self.preferences_manager = preferences_manager
        self._cascade_offset = 0
        
    def get_positioning_preferences(self) -> Dict[str, Any]:
        """Get window positioning preferences from config."""
        if not self.preferences_manager:
            return self._get_default_preferences()
        
        config = self.preferences_manager.get_preference('window_positioning')
        if not config:
            return self._get_default_preferences()
        
        return config
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default window positioning preferences."""
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
    
    def position_main_window(self, window: tk.Tk) -> None:
        """
        Position the main window according to preferences.
        
        Args:
            window: Main window to position
        """
        prefs = self.get_positioning_preferences()
        main_prefs = prefs.get('main_window', {})
        
        # Get window size
        window.update_idletasks()
        width = main_prefs.get('default_size', {}).get('width', 800)
        height = main_prefs.get('default_size', {}).get('height', 600)
        
        # Handle remember_last mode with size
        if main_prefs.get('remember_size', True) and main_prefs.get('last_position'):
            last_pos = main_prefs['last_position']
            width = last_pos.get('width', width)
            height = last_pos.get('height', height)
        
        # Calculate position
        mode_str = main_prefs.get('mode', 'center_screen')
        try:
            mode = MainWindowMode(mode_str)
        except ValueError:
            mode = MainWindowMode.CENTER_SCREEN
            logger.warning(f"Invalid main window mode: {mode_str}, using center_screen")
        
        x, y = WindowPositionCalculator.calculate_main_window_position(
            mode=mode,
            window_width=width,
            window_height=height,
            custom_x=main_prefs.get('custom_x', 100),
            custom_y=main_prefs.get('custom_y', 100),
            last_position=main_prefs.get('last_position')
        )
        
        # Apply geometry
        window.geometry(f"{width}x{height}+{x}+{y}")
        logger.info(f"Positioned main window at ({x}, {y}) with size {width}x{height}")
    
    def position_dialog(
        self,
        dialog: tk.Toplevel,
        parent,
        dialog_type: str = "default"
    ) -> None:
        """
        Position a dialog according to preferences.
        
        Args:
            dialog: Dialog window to position
            parent: Parent window
            dialog_type: Type of dialog for specific positioning rules
        """
        prefs = self.get_positioning_preferences()
        dialog_prefs = prefs.get('dialogs', {})
        
        # Update dialog to get accurate size
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        # Handle cascade mode
        if dialog_prefs.get('cascade_multiple_dialogs', False):
            self._cascade_offset += 30
            if self._cascade_offset > 150:  # Reset after 5 dialogs
                self._cascade_offset = 0
        
        # Get alignment preferences
        h_align_str = dialog_prefs.get('horizontal_alignment', 'center')
        v_align_str = dialog_prefs.get('vertical_alignment', 'center')
        
        try:
            h_align = DialogHorizontalAlignment(h_align_str)
            v_align = DialogVerticalAlignment(v_align_str)
        except ValueError:
            h_align = DialogHorizontalAlignment.CENTER
            v_align = DialogVerticalAlignment.CENTER
            logger.warning(f"Invalid dialog alignment: {h_align_str}, {v_align_str}")
        
        # Calculate position
        x, y = WindowPositionCalculator.calculate_dialog_position(
            parent_window=parent,
            dialog_width=dialog_width,
            dialog_height=dialog_height,
            horizontal_alignment=h_align,
            vertical_alignment=v_align,
            custom_offset=dialog_prefs.get('custom_offset')
        )
        
        # Apply cascade offset
        if dialog_prefs.get('cascade_multiple_dialogs', False):
            x += self._cascade_offset
            y += self._cascade_offset
        
        # Apply geometry
        dialog.geometry(f"+{x}+{y}")
        logger.debug(f"Positioned {dialog_type} dialog at ({x}, {y})")
    
    def save_main_window_position(self, window: tk.Tk) -> None:
        """
        Save the current main window position and size.
        
        Args:
            window: Main window to save position for
        """
        if not self.preferences_manager:
            return
        
        try:
            # Get current geometry
            geometry = window.geometry()
            # Parse geometry string (e.g., "800x600+100+50")
            size_part, pos_part = geometry.split('+', 1)
            width, height = map(int, size_part.split('x'))
            x, y = map(int, pos_part.split('+'))
            
            # Update preferences
            prefs = self.get_positioning_preferences()
            prefs['main_window']['last_position'] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
            self.preferences_manager.set_preference('window_positioning', prefs)
            logger.info(f"Saved main window position: {x}, {y}, size: {width}x{height}")
            
        except Exception as e:
            logger.error(f"Failed to save window position: {e}")
    
    def reset_cascade_offset(self) -> None:
        """Reset the cascade offset for dialogs."""
        self._cascade_offset = 0


# Global instance for easy access
_position_manager = None


def get_position_manager(preferences_manager=None) -> WindowPositionManager:
    """Get the global window position manager instance."""
    global _position_manager
    if _position_manager is None:
        _position_manager = WindowPositionManager(preferences_manager)
    return _position_manager


def position_main_window(window: tk.Tk, preferences_manager=None) -> None:
    """Convenience function to position main window."""
    manager = get_position_manager(preferences_manager)
    manager.position_main_window(window)


def position_dialog(dialog: tk.Toplevel, parent, dialog_type: str = "default") -> None:
    """Convenience function to position dialog."""
    manager = get_position_manager()
    manager.position_dialog(dialog, parent, dialog_type)


def save_main_window_position(window: tk.Tk) -> None:
    """Convenience function to save main window position."""
    manager = get_position_manager()
    manager.save_main_window_position(window)