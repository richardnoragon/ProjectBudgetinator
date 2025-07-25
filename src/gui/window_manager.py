"""
GUI Window lifecycle management system.

This module provides comprehensive window lifecycle management to prevent
memory leaks in tkinter GUI applications. It includes automatic cleanup,
weak reference management, and resource tracking.
"""

import tkinter as tk
import weakref
import gc
import logging
from typing import Optional, Dict, Any, List, Callable
import threading
from abc import ABC

logger = logging.getLogger(__name__)


class WindowLifecycleManager:
    """
    Centralized manager for GUI window lifecycle.
    
    Ensures proper cleanup of dialog windows, prevents memory leaks,
    and manages window references with weak references.
    """
    
    def __init__(self):
        self._open_windows: Dict[str, weakref.ReferenceType] = {}
        self._cleanup_callbacks: Dict[str, List[Callable]] = {}
        self._window_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def register_window(self, window_id: str, window: tk.Toplevel,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a window for lifecycle management.
        
        Args:
            window_id: Unique identifier for the window
            window: The tkinter Toplevel window
            metadata: Optional metadata about the window
        """
        with self._lock:
            # Store weak reference to prevent memory leaks
            self._open_windows[window_id] = weakref.ref(
                window, self._on_window_destroyed)
            self._window_metadata[window_id] = metadata or {}
            self._cleanup_callbacks[window_id] = []
            
            # Bind window close event
            window.protocol("WM_DELETE_WINDOW",
                            lambda: self.close_window(window_id))
            
            logger.debug(f"Registered window: {window_id}")
    
    def add_cleanup_callback(self, window_id: str, callback: Callable) -> None:
        """
        Add cleanup callback for when window is destroyed.
        
        Args:
            window_id: Window identifier
            callback: Function to call on cleanup
        """
        with self._lock:
            if window_id in self._cleanup_callbacks:
                self._cleanup_callbacks[window_id].append(callback)
    
    def close_window(self, window_id: str) -> bool:
        """
        Close a specific window and cleanup resources.
        
        Args:
            window_id: Window identifier to close
            
        Returns:
            bool: True if window was closed successfully
        """
        with self._lock:
            if window_id not in self._open_windows:
                return False
            
            # Get window reference
            window_ref = self._open_windows[window_id]
            window = window_ref()
            
            if window and window.winfo_exists():
                try:
                    # Execute cleanup callbacks
                    for callback in self._cleanup_callbacks.get(window_id, []):
                        try:
                            callback()
                        except Exception as e:
                            logger.error(f"Cleanup callback error: {e}")
                    
                    # Destroy window
                    window.destroy()
                    logger.debug(f"Closed window: {window_id}")
                    
                except Exception as e:
                    logger.error(f"Error closing window {window_id}: {e}")
                    return False
            
            # Cleanup references
            self._cleanup_references(window_id)
            return True
    
    def close_all_windows(self) -> int:
        """
        Close all managed windows.
        
        Returns:
            int: Number of windows closed
        """
        closed_count = 0
        with self._lock:
            window_ids = list(self._open_windows.keys())
            for window_id in window_ids:
                if self.close_window(window_id):
                    closed_count += 1
        
        logger.info(f"Closed {closed_count} windows")
        return closed_count
    
    def get_window(self, window_id: str) -> Optional[tk.Toplevel]:
        """
        Get window by ID if it still exists.
        
        Args:
            window_id: Window identifier
            
        Returns:
            Optional[tk.Toplevel]: Window instance or None
        """
        with self._lock:
            if window_id not in self._open_windows:
                return None
            
            window = self._open_windows[window_id]()
            if window and window.winfo_exists():
                return window
            else:
                # Window no longer exists, cleanup
                self._cleanup_references(window_id)
                return None
    
    def get_open_windows(self) -> List[str]:
        """
        Get list of currently open window IDs.
        
        Returns:
            List[str]: List of active window identifiers
        """
        with self._lock:
            active_windows = []
            for window_id, window_ref in self._open_windows.items():
                window = window_ref()
                if window and window.winfo_exists():
                    active_windows.append(window_id)
                else:
                    # Cleanup orphaned references
                    self._cleanup_references(window_id)
            return active_windows
    
    def _on_window_destroyed(self, window_ref: weakref.ReferenceType) -> None:
        """
        Callback when window is garbage collected.
        
        Args:
            window_ref: Weak reference to the destroyed window
        """
        # Find and cleanup the window ID
        with self._lock:
            for window_id, ref in self._open_windows.items():
                if ref is window_ref:
                    self._cleanup_references(window_id)
                    break
    
    def _cleanup_references(self, window_id: str) -> None:
        """Cleanup all references for a window ID."""
        self._open_windows.pop(window_id, None)
        self._cleanup_callbacks.pop(window_id, None)
        self._window_metadata.pop(window_id, None)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics for managed windows.
        
        Returns:
            Dict[str, Any]: Memory statistics
        """
        with self._lock:
            active_count = len(self.get_open_windows())
            return {
                'total_windows': active_count,
                'registered_windows': len(self._open_windows),
                'cleanup_callbacks': sum(len(cbs) for cbs in
                                         self._cleanup_callbacks.values())
            }


# Global window manager instance
window_manager = WindowLifecycleManager()


class BaseDialog(tk.Toplevel, ABC):
    """
    Base dialog class with automatic lifecycle management.
    
    Provides consistent dialog behavior, automatic cleanup, and
    memory leak prevention.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "",
                 window_id: Optional[str] = None, **kwargs):
        """
        Initialize base dialog with lifecycle management.
        
        Args:
            parent: Parent widget
            title: Dialog title
            window_id: Unique identifier (auto-generated if None)
            **kwargs: Additional arguments
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.window_id = window_id or f"{self.__class__.__name__}_{id(self)}"
        
        # Configure dialog
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Register with lifecycle manager
        window_manager.register_window(self.window_id, self)
        
        # Setup cleanup
        self._setup_cleanup()
        
        logger.debug(f"Created dialog: {self.window_id}")
    
    def _center_dialog(self):
        """Position the dialog according to user preferences."""
        try:
            from utils.window_positioning import position_dialog
            position_dialog(self, self.parent, self.__class__.__name__)
        except ImportError:
            # Fallback to original centering if positioning module not available
            self._fallback_center_dialog()
    
    def _fallback_center_dialog(self):
        """Fallback dialog centering method."""
        self.update_idletasks()
        
        # Get parent window position
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _setup_cleanup(self):
        """Setup automatic cleanup handlers."""
        # Add cleanup callback
        window_manager.add_cleanup_callback(self.window_id, self._on_cleanup)
        
        # Bind window events
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Destroy>", self._on_destroy)
    
    def _on_close(self):
        """Handle window close event."""
        self.destroy()
    
    def _on_destroy(self, event=None):
        """Handle window destroy event."""
        if event and event.widget is self:
            window_manager.close_window(self.window_id)
    
    def _on_cleanup(self):
        """Override for custom cleanup logic."""
        pass
    
    def close(self):
        """Close the dialog."""
        window_manager.close_window(self.window_id)
    
    def show_modal(self) -> Any:
        """
        Show dialog modally and return result.
        
        Returns:
            Any: Dialog result
        """
        self.wait_window()
        return getattr(self, '_result', None)


class WeakCallbackManager:
    """
    Manager for weak reference callbacks to prevent memory leaks.
    
    Ensures callbacks don't prevent garbage collection of objects.
    """
    
    def __init__(self):
        self._callbacks: Dict[str, weakref.WeakMethod] = {}
    
    def register_callback(self, callback_id: str, callback: Callable) -> None:
        """
        Register a weak reference callback.
        
        Args:
            callback_id: Unique identifier
            callback: Method to call
        """
        if hasattr(callback, '__self__'):
            # It's a bound method
            self._callbacks[callback_id] = weakref.WeakMethod(callback)
        else:
            # It's a regular function
            self._callbacks[callback_id] = weakref.ref(callback)
    
    def execute_callback(self, callback_id: str, *args, **kwargs) -> bool:
        """
        Execute callback if target still exists.
        
        Args:
            callback_id: Callback identifier
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            bool: True if callback was executed
        """
        if callback_id not in self._callbacks:
            return False
        
        callback_ref = self._callbacks[callback_id]
        callback = callback_ref()
        
        if callback:
            try:
                callback(*args, **kwargs)
                return True
            except Exception as e:
                logger.error(f"Callback execution error: {e}")
        
        # Cleanup expired callback
        del self._callbacks[callback_id]
        return False
    
    def cleanup_expired_callbacks(self) -> int:
        """
        Remove expired callbacks.
        
        Returns:
            int: Number of callbacks removed
        """
        expired = [cid for cid, ref in self._callbacks.items()
                   if ref() is None]
        
        for callback_id in expired:
            del self._callbacks[callback_id]
        
        return len(expired)


# Global callback manager
weak_callback_manager = WeakCallbackManager()


def force_gui_cleanup():
    """
    Force cleanup of all GUI resources.
    
    Should be called on application exit to ensure
    all resources are properly released.
    """
    closed_count = window_manager.close_all_windows()
    cleaned_callbacks = weak_callback_manager.cleanup_expired_callbacks()
    
    # Force garbage collection
    gc.collect()
    
    logger.info(f"GUI cleanup: {closed_count} windows closed, "
               f"{cleaned_callbacks} callbacks cleaned")


# Register cleanup on application exit
import atexit
atexit.register(force_gui_cleanup)
