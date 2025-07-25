"""
Password Change Dialog for ProjectBudgetinator User Administration System.

This module provides a GUI dialog for users to change their passwords,
including validation and security features.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class PasswordChangeDialog:
    """Dialog for changing user passwords with validation."""
    
    def __init__(self, parent, username: str,
                 change_password_callback: Callable[[str, str], bool]):
        """
        Initialize password change dialog.
        
        Args:
            parent: Parent window
            username: Current username
            change_password_callback: Function to call for password change
        """
        self.parent = parent
        self.username = username
        self.change_password_callback = change_password_callback
        self.result = False
        
        # Check if user is admin
        if username.lower() == "admin":
            self._show_admin_blocked_message()
            return
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Change Password")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create UI elements
        self._create_widgets()
        
        # Focus on first entry
        self.old_password_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self._change_password())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        logger.info(f"Password change dialog opened for user: {username}")
    
    def _show_admin_blocked_message(self):
        """Show message that admin password cannot be changed."""
        from tkinter import messagebox
        messagebox.showinfo(
            "Admin Password Protected",
            "The admin user password cannot be changed.\n\n"
            "The admin password is permanently set to 'pbi' for security reasons.\n"
            "This ensures consistent access to system administration functions."
        )
        logger.info("Password change blocked for admin user")
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 400
        dialog_height = 300
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Change Password", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # User info
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(user_frame, text="User:").pack(side=tk.LEFT)
        ttk.Label(user_frame, text=self.username, 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Password fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Old password
        ttk.Label(fields_frame, text="Current Password:").grid(row=0, column=0, 
                                                              sticky=tk.W, pady=(0, 10))
        self.old_password_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.old_password_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # New password
        ttk.Label(fields_frame, text="New Password:").grid(row=1, column=0, 
                                                          sticky=tk.W, pady=(0, 10))
        self.new_password_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.new_password_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Confirm password
        ttk.Label(fields_frame, text="Confirm Password:").grid(row=2, column=0, 
                                                              sticky=tk.W, pady=(0, 10))
        self.confirm_password_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.confirm_password_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # Password requirements
        req_frame = ttk.LabelFrame(main_frame, text="Password Requirements", 
                                  padding="10")
        req_frame.pack(fill=tk.X, pady=(0, 20))
        
        requirements = [
            "• Minimum 3 characters",
            "• Can contain letters, numbers, and symbols",
            "• Default password 'pbi' should be changed"
        ]
        
        for req in requirements:
            ttk.Label(req_frame, text=req, font=("Arial", 9)).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Change Password", 
                  command=self._change_password).pack(side=tk.RIGHT)
    
    def _validate_passwords(self) -> bool:
        """Validate password inputs."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Check if all fields are filled
        if not old_password:
            messagebox.showerror("Error", "Please enter your current password.")
            self.old_password_entry.focus()
            return False
        
        if not new_password:
            messagebox.showerror("Error", "Please enter a new password.")
            self.new_password_entry.focus()
            return False
        
        if not confirm_password:
            messagebox.showerror("Error", "Please confirm your new password.")
            self.confirm_password_entry.focus()
            return False
        
        # Check password length
        if len(new_password) < 3:
            messagebox.showerror("Error", "Password must be at least 3 characters long.")
            self.new_password_entry.focus()
            return False
        
        # Check password confirmation
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match.")
            self.confirm_password_entry.focus()
            return False
        
        # Check if new password is different from old
        if old_password == new_password:
            messagebox.showerror("Error", "New password must be different from current password.")
            self.new_password_entry.focus()
            return False
        
        return True
    
    def _change_password(self):
        """Handle password change."""
        if not self._validate_passwords():
            return
        
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        
        try:
            # Call the password change callback
            if self.change_password_callback(old_password, new_password):
                messagebox.showinfo("Success", "Password changed successfully!")
                self.result = True
                self.dialog.destroy()
                logger.info(f"Password changed successfully for user: {self.username}")
            else:
                messagebox.showerror("Error", "Current password is incorrect.")
                self.old_password_entry.focus()
                self.old_password_entry.select_range(0, tk.END)
                logger.warning(f"Failed password change attempt for user: {self.username}")
        
        except Exception as e:
            logger.error(f"Error changing password for user {self.username}: {e}")
            messagebox.showerror("Error", f"Failed to change password: {str(e)}")
    
    def _cancel(self):
        """Cancel password change."""
        self.result = False
        self.dialog.destroy()
        logger.info(f"Password change cancelled for user: {self.username}")
    
    def show(self) -> bool:
        """
        Show the dialog and return result.
        
        Returns:
            True if password was changed, False otherwise
        """
        # If dialog wasn't created (admin user), return False
        if not hasattr(self, 'dialog'):
            return False
        
        self.dialog.wait_window()
        return self.result


def show_password_change_dialog(parent, username: str,
                               change_password_callback: Callable[[str, str], bool]) -> bool:
    """
    Show password change dialog.
    
    Args:
        parent: Parent window
        username: Current username
        change_password_callback: Function to call for password change
        
    Returns:
        True if password was changed, False otherwise
    """
    dialog = PasswordChangeDialog(parent, username, change_password_callback)
    return dialog.show()