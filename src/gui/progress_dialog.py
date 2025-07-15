"""
Progress indicators and dialogs for long-running operations.

This module provides comprehensive progress feedback including:
- Progress bars with percentage completion
- Estimated time remaining
- Cancellation support
- Status messages
- Threaded operations
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional, Any
from logger import get_structured_logger, LogContext


logger = get_structured_logger("gui.progress")


class ProgressDialog:
    """
    Advanced progress dialog with cancellation and time estimation.
    
    Features:
    - Determinate and indeterminate progress bars
    - Time estimation and remaining time display
    - Cancellation support with callbacks
    - Status message updates
    - Thread-safe operation
    """
    
    def __init__(self, parent, title="Processing...", 
                 can_cancel=True, show_eta=True):
        """
        Initialize progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            can_cancel: Whether to show cancel button
            show_eta: Whether to show time estimation
        """
        self.parent = parent
        self.cancelled = False
        self.start_time = time.time()
        self.can_cancel = can_cancel
        self.show_eta = show_eta
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.geometry("400x150")
        
        # Center the dialog
        self._center_dialog()
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Prevent closing with X button unless cancellable
        if self.can_cancel:
            self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        else:
            self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self._setup_ui()
        
        logger.info("Progress dialog initialized", 
                   title=title, can_cancel=can_cancel, show_eta=show_eta)
    
    def _center_dialog(self):
        """Center the dialog over parent window."""
        self.dialog.update_idletasks()
        
        # Get parent geometry
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the user interface components."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='determinate',
            length=350
        )
        self.progress.pack(pady=(0, 10))
        
        # Progress info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Percentage label
        self.percentage_var = tk.StringVar(value="0%")
        self.percentage_label = ttk.Label(info_frame, textvariable=self.percentage_var)
        self.percentage_label.pack(side=tk.LEFT)
        
        # ETA label (if enabled)
        if self.show_eta:
            self.eta_var = tk.StringVar(value="")
            self.eta_label = ttk.Label(info_frame, textvariable=self.eta_var)
            self.eta_label.pack(side=tk.RIGHT)
        
        # Cancel button (if enabled)
        if self.can_cancel:
            button_frame = ttk.Frame(main_frame)
            button_frame.pack()
            
            self.cancel_button = ttk.Button(
                button_frame,
                text="Cancel",
                command=self.cancel
            )
            self.cancel_button.pack()
    
    def update_progress(self, value, maximum=None, status=None):
        """
        Update progress bar and information.
        
        Args:
            value: Current progress value
            maximum: Maximum value (if changed)
            status: Status message to display
        """
        if self.cancelled:
            return
        
        try:
            # Update maximum if provided
            if maximum is not None:
                self.progress['maximum'] = maximum
            
            # Update progress value
            self.progress['value'] = value
            
            # Calculate percentage
            max_val = self.progress['maximum']
            if max_val > 0:
                percentage = int((value / max_val) * 100)
                self.percentage_var.set(f"{percentage}%")
                
                # Calculate ETA if enabled and we have meaningful progress
                if self.show_eta and percentage > 0:
                    elapsed = time.time() - self.start_time
                    if percentage < 100:
                        total_estimated = elapsed / (percentage / 100)
                        remaining = total_estimated - elapsed
                        eta_text = self._format_time(remaining)
                        self.eta_var.set(f"ETA: {eta_text}")
                    else:
                        self.eta_var.set("Complete")
            
            # Update status if provided
            if status:
                self.status_var.set(status)
            
            # Force update
            self.dialog.update()
            
        except tk.TclError:
            # Dialog was destroyed
            pass
    
    def set_indeterminate(self, active=True):
        """
        Switch to indeterminate mode.
        
        Args:
            active: Whether to activate indeterminate mode
        """
        if active:
            self.progress.config(mode='indeterminate')
            self.progress.start(10)
            self.percentage_var.set("Working...")
            if self.show_eta:
                self.eta_var.set("")
        else:
            self.progress.stop()
            self.progress.config(mode='determinate')
    
    def update_status(self, status):
        """
        Update status message.
        
        Args:
            status: New status message
        """
        self.status_var.set(status)
        self.dialog.update()
    
    def cancel(self):
        """Cancel the operation."""
        if not self.cancelled:
            self.cancelled = True
            self.status_var.set("Cancelling...")
            if self.can_cancel:
                self.cancel_button.config(state='disabled')
            logger.info("Operation cancelled by user")
    
    def is_cancelled(self):
        """Check if operation was cancelled."""
        return self.cancelled
    
    def close(self):
        """Close the progress dialog."""
        try:
            if hasattr(self, 'progress') and self.progress.cget('mode') == 'indeterminate':
                self.progress.stop()
            self.dialog.grab_release()
            self.dialog.destroy()
        except tk.TclError:
            # Dialog already destroyed
            pass
    
    def _format_time(self, seconds):
        """Format seconds into human-readable time."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class ProgressContext:
    """
    Context manager for progress operations.
    
    Automatically handles dialog creation, cleanup, and error handling.
    """
    
    def __init__(self, parent, title="Processing...", 
                 can_cancel=True, show_eta=True):
        """
        Initialize progress context.
        
        Args:
            parent: Parent window
            title: Dialog title
            can_cancel: Whether operation can be cancelled
            show_eta: Whether to show time estimation
        """
        self.parent = parent
        self.title = title
        self.can_cancel = can_cancel
        self.show_eta = show_eta
        self.dialog = None
    
    def __enter__(self):
        """Enter context and create progress dialog."""
        self.dialog = ProgressDialog(
            self.parent, 
            self.title, 
            self.can_cancel, 
            self.show_eta
        )
        return self.dialog
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and cleanup dialog."""
        if self.dialog:
            self.dialog.close()
        
        # Log completion or error
        if exc_type is None:
            logger.info("Progress operation completed successfully")
        else:
            logger.error("Progress operation failed", 
                        error_type=exc_type.__name__ if exc_type else None)


class ThreadedProgressOperation:
    """
    Helper for running operations in background thread with progress.
    """
    
    def __init__(self, parent, operation_func, title="Processing...",
                 can_cancel=True, show_eta=True, completion_callback=None):
        """
        Initialize threaded operation.
        
        Args:
            parent: Parent window
            operation_func: Function to run in background
            title: Progress dialog title
            can_cancel: Whether operation can be cancelled
            show_eta: Whether to show time estimation
            completion_callback: Callback when operation completes
        """
        self.parent = parent
        self.operation_func = operation_func
        self.title = title
        self.can_cancel = can_cancel
        self.show_eta = show_eta
        self.completion_callback = completion_callback
        self.result = None
        self.exception = None
    
    def start(self, *args, **kwargs):
        """Start the threaded operation."""
        with LogContext("threaded_operation", operation=self.title):
            logger.info("Starting threaded operation", title=self.title)
            
            # Create progress dialog
            progress = ProgressDialog(
                self.parent, 
                self.title, 
                self.can_cancel, 
                self.show_eta
            )
            
            # Start operation in thread
            thread = threading.Thread(
                target=self._run_operation,
                args=(progress, *args),
                kwargs=kwargs,
                daemon=True
            )
            thread.start()
            
            # Monitor thread completion
            self._monitor_thread(thread, progress)
    
    def _run_operation(self, progress, *args, **kwargs):
        """Run the operation in background thread."""
        try:
            # Pass progress dialog to operation function
            self.result = self.operation_func(progress, *args, **kwargs)
        except Exception as e:
            self.exception = e
            logger.exception("Threaded operation failed")
    
    def _monitor_thread(self, thread, progress):
        """Monitor thread completion and handle cleanup."""
        if thread.is_alive():
            # Check for cancellation
            if progress.is_cancelled():
                logger.info("Threaded operation cancelled")
                progress.close()
                return
            
            # Schedule next check
            self.parent.after(100, lambda: self._monitor_thread(thread, progress))
        else:
            # Thread completed
            progress.close()
            
            if self.exception:
                logger.error("Threaded operation failed with exception")
                # Handle exception (show error dialog, etc.)
                from tkinter import messagebox
                messagebox.showerror(
                    "Operation Failed", 
                    f"Operation failed: {str(self.exception)}"
                )
            else:
                logger.info("Threaded operation completed successfully")
                # Handle success
                if self.completion_callback:
                    self.completion_callback(self.result)


# Convenience functions for common use cases

def show_progress_for_operation(parent, operation_func, title="Processing...",
                              can_cancel=True, show_eta=True, 
                              completion_callback=None):
    """
    Convenience function to show progress for any operation.
    
    Args:
        parent: Parent window
        operation_func: Function that accepts progress dialog as first argument
        title: Dialog title
        can_cancel: Whether operation can be cancelled
        show_eta: Whether to show time estimation
        completion_callback: Callback when operation completes
    """
    threaded_op = ThreadedProgressOperation(
        parent, operation_func, title, can_cancel, show_eta, completion_callback
    )
    threaded_op.start()


def create_progress_dialog(parent, title="Processing...", 
                         can_cancel=True, show_eta=True):
    """
    Create a basic progress dialog.
    
    Args:
        parent: Parent window
        title: Dialog title
        can_cancel: Whether to show cancel button
        show_eta: Whether to show time estimation
        
    Returns:
        ProgressDialog instance
    """
    return ProgressDialog(parent, title, can_cancel, show_eta)
