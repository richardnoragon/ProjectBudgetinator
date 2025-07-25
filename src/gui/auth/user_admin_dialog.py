"""
User Administration Dialog for ProjectBudgetinator User Administration System.

This module provides a GUI dialog for system administrators to manage users,
including creating, editing, and deleting user accounts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import logging
from database.models import User

logger = logging.getLogger(__name__)


class UserAdminDialog:
    """Dialog for user administration."""
    
    def __init__(self, parent: tk.Tk, auth_manager):
        """
        Initialize user administration dialog.
        
        Args:
            parent: Parent window
            auth_manager: Authentication manager instance
        """
        self.parent = parent
        self.auth_manager = auth_manager
        self.users: List[User] = []
        self.selected_user: Optional[User] = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("User Administration")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create UI elements
        self._create_widgets()
        
        # Load users
        self._load_users()
        
        logger.info("User administration dialog opened")
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 700
        dialog_height = 600
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="User Administration", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # User list frame
        list_frame = ttk.LabelFrame(main_frame, text="Users", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # User treeview with scrollbar
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("Username", "Full Name", "Email", "Created", "Last Login", "Profiles")
        self.user_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Full Name", text="Full Name")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("Created", text="Created")
        self.user_tree.heading("Last Login", text="Last Login")
        self.user_tree.heading("Profiles", text="Profiles")
        
        # Configure column widths
        self.user_tree.column("Username", width=100)
        self.user_tree.column("Full Name", width=120)
        self.user_tree.column("Email", width=150)
        self.user_tree.column("Created", width=100)
        self.user_tree.column("Last Login", width=100)
        self.user_tree.column("Profiles", width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                   command=self.user_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=v_scrollbar.set, 
                                xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.user_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.user_tree.bind('<<TreeviewSelect>>', self._on_user_select)
        
        # User details frame
        details_frame = ttk.LabelFrame(main_frame, text="User Details", 
                                      padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create form fields
        self._create_user_form(details_frame)
        
        # User action buttons
        user_buttons_frame = ttk.Frame(details_frame)
        user_buttons_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.new_user_button = ttk.Button(user_buttons_frame, text="New User", 
                                         command=self._new_user)
        self.new_user_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_user_button = ttk.Button(user_buttons_frame, text="Save", 
                                          command=self._save_user, state=tk.DISABLED)
        self.save_user_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_user_button = ttk.Button(user_buttons_frame, text="Delete", 
                                            command=self._delete_user, state=tk.DISABLED)
        self.delete_user_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_password_button = ttk.Button(user_buttons_frame, text="Reset Password", 
                                               command=self._reset_password, state=tk.DISABLED)
        self.reset_password_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self._load_users).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=self._close).pack(side=tk.RIGHT)
    
    def _create_user_form(self, parent):
        """Create user form fields."""
        # Username
        ttk.Label(parent, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(parent, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # Full name
        ttk.Label(parent, text="Full Name:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.full_name_var = tk.StringVar()
        self.full_name_entry = ttk.Entry(parent, textvariable=self.full_name_var, width=30)
        self.full_name_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        # Email
        ttk.Label(parent, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(parent, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        # Password (for new users)
        ttk.Label(parent, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(parent, textvariable=self.password_var, 
                                       show="*", width=30)
        self.password_entry.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        # Password note
        note_label = ttk.Label(parent, text="(Leave blank to keep current password)", 
                              font=("Arial", 8), foreground="gray")
        note_label.grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
    
    def _load_users(self):
        """Load users into the treeview."""
        try:
            # Clear treeview
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            # Get all users
            self.users = self.auth_manager.user_manager.get_all_users()
            
            # Add users to treeview
            for user in self.users:
                # Get profile count
                profiles = self.auth_manager.profile_manager.get_user_profiles(user.user_id)
                profile_count = len(profiles)
                
                # Format dates
                created_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
                last_login = user.last_login.strftime("%Y-%m-%d") if user.last_login else "Never"
                
                # Insert user into treeview
                self.user_tree.insert("", tk.END, values=(
                    user.username,
                    user.full_name or "",
                    user.email or "",
                    created_date,
                    last_login,
                    f"{profile_count}/5"
                ))
            
            logger.info(f"Loaded {len(self.users)} users")
            
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
    
    def _on_user_select(self, event):
        """Handle user selection."""
        selection = self.user_tree.selection()
        if not selection:
            self._clear_user_form()
            return
        
        # Get selected item index
        item = selection[0]
        index = self.user_tree.index(item)
        
        if index < len(self.users):
            self.selected_user = self.users[index]
            self._load_user_details()
    
    def _load_user_details(self):
        """Load selected user details into form."""
        if not self.selected_user:
            return
        
        # Check if selected user is admin
        is_admin = self.auth_manager.user_manager.is_admin_user(self.selected_user)
        
        # Load user data
        self.username_var.set(self.selected_user.username)
        self.full_name_var.set(self.selected_user.full_name or "")
        self.email_var.set(self.selected_user.email or "")
        self.password_var.set("")  # Never show password
        
        # Enable buttons
        self.save_user_button.configure(state=tk.NORMAL)
        
        # Disable admin-specific operations
        if is_admin:
            self.delete_user_button.configure(state=tk.DISABLED)
            self.reset_password_button.configure(state=tk.DISABLED)
            self.password_entry.configure(state=tk.DISABLED)
        else:
            self.delete_user_button.configure(state=tk.NORMAL)
            self.reset_password_button.configure(state=tk.NORMAL)
            self.password_entry.configure(state=tk.NORMAL)
        
        # Disable username editing for existing users
        self.username_entry.configure(state=tk.DISABLED)
    
    def _clear_user_form(self):
        """Clear user form."""
        self.selected_user = None
        self.username_var.set("")
        self.full_name_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        
        # Disable buttons
        self.save_user_button.configure(state=tk.DISABLED)
        self.delete_user_button.configure(state=tk.DISABLED)
        self.reset_password_button.configure(state=tk.DISABLED)
        
        # Enable username editing and password entry
        self.username_entry.configure(state=tk.NORMAL)
        self.password_entry.configure(state=tk.NORMAL)
    
    def _new_user(self):
        """Create a new user."""
        self._clear_user_form()
        self.save_user_button.configure(state=tk.NORMAL)
        self.username_entry.focus()
    
    def _save_user(self):
        """Save current user."""
        # Validate input
        username = self.username_var.get().strip()
        full_name = self.full_name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not username:
            messagebox.showerror("Error", "Username is required.")
            self.username_entry.focus()
            return
        
        try:
            if self.selected_user:
                # Update existing user
                user_data = {
                    'full_name': full_name if full_name else None,
                    'email': email if email else None
                }
                
                # Update password if provided
                if password:
                    success = self.auth_manager.user_manager.change_password(
                        self.selected_user.user_id, password)
                    if not success:
                        messagebox.showerror("Error", "Failed to update password.")
                        return
                
                # Update user info
                success = self.auth_manager.user_manager.update_user(
                    self.selected_user.user_id, user_data)
                if success:
                    messagebox.showinfo("Success", "User updated successfully!")
                    self._load_users()
                    logger.info(f"User updated: {username}")
                else:
                    messagebox.showerror("Error", "Failed to update user.")
            else:
                # Create new user
                if not password:
                    password = "pbi"  # Default password
                
                user_data = {
                    'username': username,
                    'password': password,
                    'full_name': full_name if full_name else None,
                    'email': email if email else None
                }
                
                new_user = self.auth_manager.user_manager.create_user(user_data)
                if new_user:
                    messagebox.showinfo("Success", 
                                      f"User created successfully!\nDefault password: pbi")
                    self._load_users()
                    self._clear_user_form()
                    logger.info(f"User created: {username}")
                else:
                    messagebox.showerror("Error", "Failed to create user.")
        
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")
    
    def _delete_user(self):
        """Delete selected user."""
        if not self.selected_user:
            return
        
        # Check if trying to delete admin user
        if self.auth_manager.user_manager.is_admin_user(self.selected_user):
            messagebox.showerror(
                "Cannot Delete Admin",
                "The admin user cannot be deleted.\n\n"
                "The admin user is required for system administration."
            )
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{self.selected_user.username}'?\n\n"
            "This will also delete all associated profiles and data.\n"
            "This action cannot be undone."
        )
        
        if result:
            try:
                success = self.auth_manager.user_manager.delete_user(
                    self.selected_user.user_id)
                if success:
                    messagebox.showinfo("Success", "User deleted successfully!")
                    self._load_users()
                    self._clear_user_form()
                    logger.info(f"User deleted: {self.selected_user.username}")
                else:
                    messagebox.showerror("Error", "Failed to delete user.")
            
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def _reset_password(self):
        """Reset user password to default."""
        if not self.selected_user:
            return
        
        # Check if trying to reset admin password
        if self.auth_manager.user_manager.is_admin_user(self.selected_user):
            messagebox.showerror(
                "Cannot Reset Admin Password",
                "The admin user password cannot be changed.\n\n"
                "The admin password is permanently set to 'pbi' for security reasons."
            )
            return
        
        # Confirm password reset
        result = messagebox.askyesno(
            "Confirm Password Reset",
            f"Reset password for user '{self.selected_user.username}' to 'pbi'?"
        )
        
        if result:
            try:
                success = self.auth_manager.user_manager.reset_password(
                    self.selected_user.user_id, "pbi")
                if success:
                    messagebox.showinfo("Success",
                                      "Password reset successfully!\nNew password: pbi")
                    logger.info(f"Password reset for user: {self.selected_user.username}")
                else:
                    messagebox.showerror("Error", "Failed to reset password.")
            
            except Exception as e:
                logger.error(f"Error resetting password: {e}")
                messagebox.showerror("Error", f"Failed to reset password: {str(e)}")
    
    def _close(self):
        """Close the dialog."""
        self.dialog.destroy()
        logger.info("User administration dialog closed")
    
    def show(self):
        """Show the dialog."""
        self.dialog.wait_window()


def show_user_admin_dialog(parent: tk.Tk, auth_manager):
    """
    Show user administration dialog.
    
    Args:
        parent: Parent window
        auth_manager: Authentication manager instance
    """
    dialog = UserAdminDialog(parent, auth_manager)
    dialog.show()