"""
Profile switcher widget for switching between user profiles during active sessions.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
import logging

from auth.auth_manager import get_auth_manager
from database.models import UserProfile


class ProfileSwitcher:
    """Widget for switching between user profiles."""
    
    def __init__(self, parent: tk.Widget, on_profile_changed: Optional[Callable[[UserProfile], None]] = None):
        """
        Initialize profile switcher.
        
        Args:
            parent: Parent widget
            on_profile_changed: Callback when profile is changed
        """
        self.parent = parent
        self.on_profile_changed = on_profile_changed
        self.auth_manager = get_auth_manager()
        self.logger = logging.getLogger("ProjectBudgetinator.profile_switcher")
        
        # UI variables
        self.current_profile_var = tk.StringVar()
        
        # Create the widget
        self.frame = ttk.Frame(parent)
        self._setup_ui()
        self._load_profiles()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Profile label
        profile_label = ttk.Label(self.frame, text="Profile:")
        profile_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Profile combobox
        self.profile_combo = ttk.Combobox(
            self.frame,
            textvariable=self.current_profile_var,
            state="readonly",
            width=20
        )
        self.profile_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_selected)
        
        # Manage profiles button
        manage_button = ttk.Button(
            self.frame,
            text="Manage...",
            command=self._show_profile_management,
            width=10
        )
        manage_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def _load_profiles(self):
        """Load user profiles into the combobox."""
        try:
            profiles = self.auth_manager.get_user_profiles()
            current_profile = self.auth_manager.get_current_profile()
            
            # Clear existing items
            self.profile_combo['values'] = ()
            
            if not profiles:
                self.profile_combo['values'] = ("No profiles available",)
                self.current_profile_var.set("No profiles available")
                self.profile_combo.config(state="disabled")
                return
            
            # Add profiles to combobox
            profile_names = []
            current_index = 0
            
            for i, profile in enumerate(profiles):
                display_name = f"{profile.profile_name} ({profile.environment_type})"
                profile_names.append(display_name)
                
                if current_profile and profile.profile_id == current_profile.profile_id:
                    current_index = i
            
            self.profile_combo['values'] = tuple(profile_names)
            self.profile_combo.config(state="readonly")
            
            # Set current selection
            if profile_names:
                self.current_profile_var.set(profile_names[current_index])
            
            self.logger.debug(f"Loaded {len(profiles)} profiles")
            
        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}")
            self.profile_combo['values'] = ("Error loading profiles",)
            self.current_profile_var.set("Error loading profiles")
            self.profile_combo.config(state="disabled")
    
    def _on_profile_selected(self, event=None):
        """Handle profile selection."""
        try:
            selected_text = self.current_profile_var.get()
            if not selected_text or selected_text in ("No profiles available", "Error loading profiles"):
                return
            
            # Find the selected profile
            profiles = self.auth_manager.get_user_profiles()
            selected_index = self.profile_combo.current()
            
            if 0 <= selected_index < len(profiles):
                selected_profile = profiles[selected_index]
                current_profile = self.auth_manager.get_current_profile()
                
                # Check if this is actually a different profile
                if current_profile and selected_profile.profile_id == current_profile.profile_id:
                    return  # Same profile, no change needed
                
                # Switch to the selected profile
                if selected_profile.profile_id is not None:
                    success = self.auth_manager.switch_profile(selected_profile.profile_id)
                    
                    if success:
                        self.logger.info(f"Switched to profile: {selected_profile.profile_name}")
                        
                        # Notify callback
                        if self.on_profile_changed:
                            self.on_profile_changed(selected_profile)
                        
                        # Show success message
                        self._show_status(f"Switched to {selected_profile.profile_name}", "green")
                    else:
                        self.logger.error(f"Failed to switch to profile: {selected_profile.profile_name}")
                        messagebox.showerror(
                            "Profile Switch Failed",
                            f"Could not switch to profile '{selected_profile.profile_name}'.\n"
                            "Please try again or contact support."
                        )
                        # Revert selection
                        self._load_profiles()
                else:
                    self.logger.error("Selected profile has no valid ID")
                    messagebox.showerror("Error", "Invalid profile selected.")
            
        except Exception as e:
            self.logger.error(f"Error switching profile: {e}")
            messagebox.showerror("Error", f"Failed to switch profile: {str(e)}")
            # Reload profiles to reset state
            self._load_profiles()
    
    def _show_profile_management(self):
        """Show profile management dialog."""
        try:
            from .profile_dialog import show_profile_management_dialog
            
            # Get current user from auth manager
            current_user = self.auth_manager.get_current_user()
            if current_user:
                # Get root window
                root = self.parent.winfo_toplevel()
                show_profile_management_dialog(root, self.auth_manager.profile_manager,
                                              current_user.user_id)
                # Profiles may have changed, reload them
                self._load_profiles()
                self.logger.info("Profile management completed, reloaded profiles")
            else:
                messagebox.showerror("Error", "No current user found.")
                
        except ImportError:
            # Fallback if profile management dialog not available
            messagebox.showinfo(
                "Profile Management",
                "Profile management feature is not yet available.\n"
                "This will be implemented in a future update."
            )
        except Exception as e:
            self.logger.error(f"Error opening profile management: {e}")
            messagebox.showerror("Error", f"Failed to open profile management: {str(e)}")
    
    def _show_status(self, message: str, color: str = "black"):
        """Show a temporary status message."""
        # Create a temporary status label
        status_label = ttk.Label(self.frame, text=message, foreground=color)
        status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Remove the status after 3 seconds
        self.frame.after(3000, status_label.destroy)
    
    def get_widget(self) -> ttk.Frame:
        """Get the main widget frame."""
        return self.frame
    
    def refresh(self):
        """Refresh the profile list."""
        self._load_profiles()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the profile switcher."""
        state = "readonly" if enabled else "disabled"
        self.profile_combo.config(state=state)
    
    def get_current_profile_name(self) -> str:
        """Get the currently selected profile name."""
        return self.current_profile_var.get()


class ProfileSwitcherMenu:
    """Profile switcher as a menu item."""
    
    def __init__(self, parent_menu: tk.Menu, on_profile_changed: Optional[Callable[[UserProfile], None]] = None):
        """
        Initialize profile switcher menu.
        
        Args:
            parent_menu: Parent menu to add items to
            on_profile_changed: Callback when profile is changed
        """
        self.parent_menu = parent_menu
        self.on_profile_changed = on_profile_changed
        self.auth_manager = get_auth_manager()
        self.logger = logging.getLogger("ProjectBudgetinator.profile_switcher_menu")
        
        # Create profile submenu
        self.profile_menu = tk.Menu(parent_menu, tearoff=0)
        parent_menu.add_cascade(label="Switch Profile", menu=self.profile_menu)
        
        # Load profiles
        self._load_profiles()
    
    def _load_profiles(self):
        """Load profiles into the menu."""
        try:
            # Clear existing menu items
            self.profile_menu.delete(0, tk.END)
            
            profiles = self.auth_manager.get_user_profiles()
            current_profile = self.auth_manager.get_current_profile()
            
            if not profiles:
                self.profile_menu.add_command(label="No profiles available", state="disabled")
                return
            
            # Add profile menu items
            for profile in profiles:
                display_name = f"{profile.profile_name} ({profile.environment_type})"
                
                # Mark current profile
                if current_profile and profile.profile_id == current_profile.profile_id:
                    display_name = f"● {display_name}"
                
                self.profile_menu.add_command(
                    label=display_name,
                    command=lambda p=profile: self._switch_to_profile(p)
                )
            
            # Add separator and management option
            self.profile_menu.add_separator()
            self.profile_menu.add_command(
                label="Manage Profiles...",
                command=self._show_profile_management
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load profile menu: {e}")
            self.profile_menu.delete(0, tk.END)
            self.profile_menu.add_command(label="Error loading profiles", state="disabled")
    
    def _switch_to_profile(self, profile: UserProfile):
        """Switch to the specified profile."""
        try:
            current_profile = self.auth_manager.get_current_profile()
            
            # Check if this is the current profile
            if current_profile and profile.profile_id == current_profile.profile_id:
                return  # Already using this profile
            
            if profile.profile_id is not None:
                success = self.auth_manager.switch_profile(profile.profile_id)
                
                if success:
                    self.logger.info(f"Switched to profile: {profile.profile_name}")
                    
                    # Notify callback
                    if self.on_profile_changed:
                        self.on_profile_changed(profile)
                    
                    # Reload menu to update current profile indicator
                    self._load_profiles()
                else:
                    messagebox.showerror(
                        "Profile Switch Failed",
                        f"Could not switch to profile '{profile.profile_name}'."
                    )
            
        except Exception as e:
            self.logger.error(f"Error switching to profile: {e}")
            messagebox.showerror("Error", f"Failed to switch profile: {str(e)}")
    
    def _show_profile_management(self):
        """Show profile management dialog."""
        try:
            from .profile_dialog import ProfileManagementDialog
            
            # Get root window
            root = self.parent_menu.winfo_toplevel()
            
            from .profile_dialog import show_profile_management_dialog
            current_user = self.auth_manager.get_current_user()
            if current_user:
                show_profile_management_dialog(root, self.auth_manager.profile_manager,
                                              current_user.user_id)
                # Profiles may have changed, reload menu
                self._load_profiles()
            else:
                messagebox.showerror("Error", "No current user found.")
                
        except ImportError:
            messagebox.showinfo(
                "Profile Management",
                "Profile management feature is not yet available."
            )
        except Exception as e:
            self.logger.error(f"Error opening profile management: {e}")
            messagebox.showerror("Error", f"Failed to open profile management: {str(e)}")
    
    def refresh(self):
        """Refresh the profile menu."""
        self._load_profiles()


if __name__ == "__main__":
    # Test the profile switcher
    root = tk.Tk()
    root.title("Test Profile Switcher")
    root.geometry("400x200")
    
    def on_profile_change(profile):
        print(f"Profile changed to: {profile.profile_name}")
    
    # Test widget version
    frame = ttk.Frame(root)
    frame.pack(pady=20)
    
    switcher = ProfileSwitcher(frame, on_profile_change)
    switcher.get_widget().pack()
    
    # Test menu version
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    profile_menu = ProfileSwitcherMenu(menubar, on_profile_change)
    
    root.mainloop()