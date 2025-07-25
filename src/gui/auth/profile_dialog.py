"""
Profile Management Dialog for ProjectBudgetinator User Administration System.

This module provides a GUI dialog for managing user profiles,
including creating, editing, and deleting profiles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import logging
from database.models import UserProfile

logger = logging.getLogger(__name__)


class ProfileManagementDialog:
    """Dialog for managing user profiles."""
    
    def __init__(self, parent, profile_manager, current_user_id: int):
        """
        Initialize profile management dialog.
        
        Args:
            parent: Parent window
            profile_manager: Profile manager instance
            current_user_id: Current user ID
        """
        self.parent = parent
        self.profile_manager = profile_manager
        self.current_user_id = current_user_id
        self.profiles: List[UserProfile] = []
        self.selected_profile: Optional[UserProfile] = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Profile Management")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create UI elements
        self._create_widgets()
        
        # Load profiles
        self._load_profiles()
        
        logger.info(f"Profile management dialog opened for user ID: {current_user_id}")
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 600
        dialog_height = 500
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Profile Management", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Profile list frame
        list_frame = ttk.LabelFrame(main_frame, text="Profiles", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Profile listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.profile_listbox = tk.Listbox(listbox_frame, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                 command=self.profile_listbox.yview)
        self.profile_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.profile_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.profile_listbox.bind('<<ListboxSelect>>', self._on_profile_select)
        
        # Profile details frame
        details_frame = ttk.LabelFrame(main_frame, text="Profile Details", 
                                      padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Profile name
        ttk.Label(details_frame, text="Profile Name:").grid(row=0, column=0, 
                                                           sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(details_frame, textvariable=self.name_var, 
                                   width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # Environment
        ttk.Label(details_frame, text="Environment:").grid(row=1, column=0, 
                                                          sticky=tk.W, pady=(0, 5))
        self.environment_var = tk.StringVar()
        self.environment_combo = ttk.Combobox(details_frame, 
                                            textvariable=self.environment_var,
                                            values=["Development", "Testing", 
                                                   "Staging", "Production", "Personal"],
                                            state="readonly", width=27)
        self.environment_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        # Description
        ttk.Label(details_frame, text="Description:").grid(row=2, column=0, 
                                                          sticky=tk.NW, pady=(0, 5))
        self.description_text = tk.Text(details_frame, height=3, width=30)
        self.description_text.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        # Profile buttons
        profile_buttons_frame = ttk.Frame(details_frame)
        profile_buttons_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.new_button = ttk.Button(profile_buttons_frame, text="New Profile", 
                                    command=self._new_profile)
        self.new_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(profile_buttons_frame, text="Save", 
                                     command=self._save_profile, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(profile_buttons_frame, text="Delete", 
                                       command=self._delete_profile, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Close", 
                  command=self._close).pack(side=tk.RIGHT)
    
    def _load_profiles(self):
        """Load user profiles into the listbox."""
        try:
            self.profiles = self.profile_manager.get_user_profiles(self.current_user_id)
            
            # Clear listbox
            self.profile_listbox.delete(0, tk.END)
            
            # Add profiles to listbox
            for profile in self.profiles:
                display_text = f"{profile.profile_name} ({profile.environment_type})"
                self.profile_listbox.insert(tk.END, display_text)
            
            # Update profile count info
            count = len(self.profiles)
            max_profiles = 5
            self.dialog.title(f"Profile Management ({count}/{max_profiles} profiles)")
            
            # Enable/disable new button based on profile count
            if count >= max_profiles:
                self.new_button.configure(state=tk.DISABLED)
            else:
                self.new_button.configure(state=tk.NORMAL)
            
            logger.info(f"Loaded {count} profiles for user ID: {self.current_user_id}")
            
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
    
    def _on_profile_select(self, event):
        """Handle profile selection."""
        selection = self.profile_listbox.curselection()
        if not selection:
            self._clear_details()
            return
        
        index = selection[0]
        if index < len(self.profiles):
            self.selected_profile = self.profiles[index]
            self._load_profile_details()
    
    def _load_profile_details(self):
        """Load selected profile details into form."""
        if not self.selected_profile:
            return
        
        # Load profile data
        self.name_var.set(self.selected_profile.profile_name)
        self.environment_var.set(self.selected_profile.environment_type)
        
        # Load description from preferences
        self.description_text.delete(1.0, tk.END)
        description = self.selected_profile.get_preference('description', '')
        if description:
            self.description_text.insert(1.0, description)
        
        # Enable buttons
        self.save_button.configure(state=tk.NORMAL)
        self.delete_button.configure(state=tk.NORMAL)
    
    def _clear_details(self):
        """Clear profile details form."""
        self.selected_profile = None
        self.name_var.set("")
        self.environment_var.set("")
        self.description_text.delete(1.0, tk.END)
        
        # Disable buttons
        self.save_button.configure(state=tk.DISABLED)
        self.delete_button.configure(state=tk.DISABLED)
    
    def _new_profile(self):
        """Create a new profile."""
        # Check profile limit
        if len(self.profiles) >= 5:
            messagebox.showerror("Error", "Maximum of 5 profiles allowed per user.")
            return
        
        # Clear form for new profile
        self.selected_profile = None
        self.name_var.set("")
        self.environment_var.set("Development")  # Default environment
        self.description_text.delete(1.0, tk.END)
        
        # Enable save button
        self.save_button.configure(state=tk.NORMAL)
        self.delete_button.configure(state=tk.DISABLED)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def _save_profile(self):
        """Save current profile."""
        # Validate input
        profile_name = self.name_var.get().strip()
        environment = self.environment_var.get()
        description = self.description_text.get(1.0, tk.END).strip()
        
        if not profile_name:
            messagebox.showerror("Error", "Profile name is required.")
            self.name_entry.focus()
            return
        
        if not environment:
            messagebox.showerror("Error", "Environment is required.")
            self.environment_combo.focus()
            return
        
        try:
            if self.selected_profile:
                # Update existing profile
                self.selected_profile.profile_name = profile_name
                self.selected_profile.environment_type = environment
                self.selected_profile.set_preference('description', description)
                
                success = self.profile_manager.update_profile(self.selected_profile)
                if success:
                    messagebox.showinfo("Success", "Profile updated successfully!")
                    self._load_profiles()
                    logger.info(f"Profile updated: {profile_name}")
                else:
                    messagebox.showerror("Error", "Failed to update profile.")
            else:
                # Create new profile
                profile_data = {
                    'profile_name': profile_name,
                    'environment_type': environment,
                    'preferences_data': {'description': description}
                }
                
                new_profile = self.profile_manager.create_profile(
                    self.current_user_id, profile_data)
                if new_profile:
                    messagebox.showinfo("Success", "Profile created successfully!")
                    self._load_profiles()
                    logger.info(f"Profile created: {profile_name}")
                else:
                    messagebox.showerror("Error", "Failed to create profile.")
        
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def _delete_profile(self):
        """Delete selected profile."""
        if not self.selected_profile:
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the profile '{self.selected_profile.profile_name}'?\n\n"
            "This action cannot be undone."
        )
        
        if result:
            try:
                success = self.profile_manager.delete_profile(self.selected_profile.profile_id)
                if success:
                    messagebox.showinfo("Success", "Profile deleted successfully!")
                    self._load_profiles()
                    self._clear_details()
                    logger.info(f"Profile deleted: {self.selected_profile.profile_name}")
                else:
                    messagebox.showerror("Error", "Failed to delete profile.")
            
            except Exception as e:
                logger.error(f"Error deleting profile: {e}")
                messagebox.showerror("Error", f"Failed to delete profile: {str(e)}")
    
    def _close(self):
        """Close the dialog."""
        self.dialog.destroy()
        logger.info("Profile management dialog closed")
    
    def show(self):
        """Show the dialog."""
        self.dialog.wait_window()


def show_profile_management_dialog(parent, profile_manager, current_user_id: int):
    """
    Show profile management dialog.
    
    Args:
        parent: Parent window
        profile_manager: Profile manager instance
        current_user_id: Current user ID
    """
    dialog = ProfileManagementDialog(parent, profile_manager, current_user_id)
    dialog.show()