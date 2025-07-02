"""
Core functionality for managing project information.
"""
from tkinter import messagebox
import os


def create_project_folder(project_dir):
    """Create a project folder structure."""
    if not os.path.exists(project_dir):
        try:
            os.makedirs(project_dir)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project folder: {str(e)}")
            return False
    return True


def initialize_project(workbook, project_info):
    """Initialize a new project in the workbook."""
    # TODO: Implement project initialization logic
    # This should create initial worksheets and populate basic project information
    pass
