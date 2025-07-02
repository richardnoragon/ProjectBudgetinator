"""
Dialog boxes and forms for user input.
"""
import tkinter as tk
from tkinter import ttk


class ProjectSettingsDialog(tk.Toplevel):
    """Dialog for entering project settings."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Project Settings")
        self.resizable(False, False)
        self.result = None

        # Create and pack the form
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Add form fields
        row = 0
        ttk.Label(form_frame, text="Project Title:").grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=5
        )
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=40).grid(
            row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5
        )

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=5)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

    def _on_ok(self):
        """Handle OK button click."""
        self.result = {
            'title': self.title_var.get()
        }
        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()


class AboutDialog(tk.Toplevel):
    """Dialog showing application information."""
    
    def __init__(self, parent, version):
        super().__init__(parent)
        self.title("About Project Budgetinator")
        self.resizable(False, False)

        # Create and pack the content
        content = ttk.Frame(self, padding="20")
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            content,
            text="Project Budgetinator",
            font=("TkDefaultFont", 14, "bold")
        ).pack(pady=(0, 10))

        ttk.Label(
            content,
            text=f"Version {version}"
        ).pack()

        ttk.Label(
            content,
            text="© 2024 Your Name",
            font=("TkDefaultFont", 8)
        ).pack(pady=(10, 0))

        ttk.Button(
            content,
            text="OK",
            command=self.destroy
        ).pack(pady=(20, 0))

        # Make dialog modal
        self.transient(parent)
        self.grab_set()
