"""
Dialog utilities for creating and managing various dialog boxes.
"""
import tkinter as tk
from tkinter import messagebox


def confirm_action(title, message):
    """Show a confirmation dialog and return True if the user confirms."""
    return messagebox.askyesno(title, message)


def show_error(title, message):
    """Show an error dialog."""
    messagebox.showerror(title, message)


def show_info(title, message):
    """Show an information dialog."""
    messagebox.showinfo(title, message)


def show_warning(title, message):
    """Show a warning dialog."""
    messagebox.showwarning(title, message)


def get_input(title, prompt, initial_value=""):
    """Show an input dialog and return the entered value."""
    return tk.simpledialog.askstring(title, prompt, initialvalue=initial_value)
