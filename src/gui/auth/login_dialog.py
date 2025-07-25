"""
Login dialog for user authentication.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
import logging

from auth.auth_manager import get_auth_manager
from database.models import User, UserProfile


class LoginDialog:
    """Login dialog for user authentication."""
    
    def __init__(self, parent: tk.Tk):
        """Initialize login dialog."""
        self.parent = parent
        self.dialog: Optional[tk.Toplevel] = None
        self.result: Optional[Tuple[User, UserProfile]] = None
        self.auth_manager = get_auth_manager()
        self.logger = logging.getLogger("ProjectBudgetinator.login")
        
        # UI variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        
        # Track login attempts
        self.login_attempts = 0
        self.max_attempts = 3
    
    def show(self) -> Optional[Tuple[User, UserProfile]]:
        """
        Show the login dialog.
        
        Returns:
            Tuple of (User, UserProfile) if login successful, None otherwise
        """
        self._create_dialog()
        self._setup_ui()
        self._center_dialog()
        
        # Set focus to username field
        self.username_entry.focus_set()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def _create_dialog(self):
        """Create the dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("ProjectBudgetinator - Login")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="ProjectBudgetinator",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Please log in to continue",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Login form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Username field
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(
            form_frame,
            textvariable=self.username_var,
            width=30,
            font=("Arial", 10)
        )
        self.username_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Password field
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(
            form_frame,
            textvariable=self.password_var,
            show="*",
            width=30,
            font=("Arial", 10)
        )
        self.password_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Configure column weight
        form_frame.columnconfigure(0, weight=1)
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Remember login checkbox (placeholder for future enhancement)
        remember_check = ttk.Checkbutton(
            options_frame,
            text="Remember me",
            variable=self.remember_var
        )
        remember_check.pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Login button
        self.login_button = ttk.Button(
            buttons_frame,
            text="Login",
            command=self._on_login,
            width=12
        )
        self.login_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._on_cancel,
            width=12
        )
        cancel_button.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            foreground="red",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Bind Enter key to login
        if self.dialog:
            self.dialog.bind('<Return>', lambda e: self._on_login())
            self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # Check if this is first run and show helpful message
        if not self.auth_manager.has_users():
            self._show_first_run_info()
        else:
            self._show_default_credentials_hint()
    
    def _show_first_run_info(self):
        """Show information for first-time users."""
        info_frame = ttk.LabelFrame(self.dialog, text="First Time Setup", padding="10")
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        info_text = (
            "Welcome to ProjectBudgetinator!\n\n"
            "A default admin account has been created:\n"
            "Username: admin\n"
            "Password: pbi\n\n"
            "You can change the password after logging in."
        )
        
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            justify=tk.LEFT
        )
        info_label.pack()
        
        # Pre-fill the username
        self.username_var.set("admin")
        self.password_entry.focus_set()
    
    def _show_default_credentials_hint(self):
        """Show hint about default credentials."""
        hint_text = "Hint: Default password is 'pbi' for new accounts"
        hint_label = ttk.Label(
            self.dialog,
            text=hint_text,
            font=("Arial", 8),
            foreground="gray"
        )
        hint_label.pack(pady=(0, 10))
    
    def _on_login(self):
        """Handle login button click."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        # Validate input
        if not username:
            self._show_status("Please enter a username", "red")
            self.username_entry.focus_set()
            return
        
        if not password:
            self._show_status("Please enter a password", "red")
            self.password_entry.focus_set()
            return
        
        # Disable login button during authentication
        self.login_button.config(state="disabled")
        self._show_status("Authenticating...", "blue")
        
        # Update UI
        if self.dialog:
            self.dialog.update()
        
        try:
            # Attempt login
            session_id = self.auth_manager.login(username, password)
            
            if session_id:
                # Login successful
                user = self.auth_manager.get_current_user()
                profile = self.auth_manager.get_current_profile()
                
                if user and profile:
                    self.result = (user, profile)
                    self.logger.info(f"User logged in successfully: {username}")
                    
                    # Check if using default password
                    if self.auth_manager.is_using_default_password():
                        self._show_password_change_prompt()
                    
                    if self.dialog:
                        self.dialog.destroy()
                    return
                else:
                    self._show_status("Login failed - session error", "red")
            else:
                # Login failed
                self.login_attempts += 1
                remaining = self.max_attempts - self.login_attempts
                
                if remaining > 0:
                    self._show_status(f"Invalid credentials. {remaining} attempts remaining.", "red")
                    self.password_var.set("")  # Clear password
                    self.password_entry.focus_set()
                else:
                    self._show_status("Too many failed attempts. Please restart the application.", "red")
                    self.login_button.config(state="disabled")
                    return
        
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            self._show_status("Login failed - system error", "red")
        
        finally:
            # Re-enable login button
            if self.login_attempts < self.max_attempts:
                self.login_button.config(state="normal")
    
    def _show_password_change_prompt(self):
        """Show prompt to change default password."""
        response = messagebox.askyesno(
            "Default Password",
            "You are using the default password 'pbi'.\n\n"
            "For security, it's recommended to change your password.\n"
            "Would you like to change it now?",
            parent=self.dialog
        )
        
        if response:
            self._show_change_password_dialog()
    
    def _show_change_password_dialog(self):
        """Show change password dialog."""
        from .password_change_dialog import show_password_change_dialog
        
        try:
            def change_password_callback(old_password: str, new_password: str) -> bool:
                return self.auth_manager.change_password(old_password, new_password)
            
            current_user = self.auth_manager.get_current_user()
            if current_user:
                show_password_change_dialog(self.dialog, current_user.username, change_password_callback)
        except ImportError:
            # Fallback to simple dialog if password change dialog not available
            messagebox.showinfo(
                "Change Password",
                "Password change feature will be available in the main application.",
                parent=self.dialog
            )
    
    def _show_status(self, message: str, color: str = "black"):
        """Show status message."""
        self.status_label.config(text=message, foreground=color)
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        if self.dialog:
            self.dialog.destroy()
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        if not self.dialog:
            return
            
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


def show_login_dialog(parent: tk.Tk) -> Optional[Tuple[User, UserProfile]]:
    """
    Show login dialog and return authentication result.
    
    Args:
        parent: Parent window
        
    Returns:
        Tuple of (User, UserProfile) if login successful, None otherwise
    """
    dialog = LoginDialog(parent)
    return dialog.show()


if __name__ == "__main__":
    # Test the login dialog
    root = tk.Tk()
    root.title("Test Login Dialog")
    root.geometry("200x100")
    
    def test_login():
        result = show_login_dialog(root)
        if result:
            user, profile = result
            print(f"Login successful: {user.username}, Profile: {profile.profile_name}")
        else:
            print("Login cancelled or failed")
    
    ttk.Button(root, text="Show Login", command=test_login).pack(pady=20)
    
    root.mainloop()