"""
File management functions for working with Excel workbooks.
"""
from tkinter import filedialog
from tkinter import messagebox
import openpyxl
import os


def open_file():
    """Open an Excel file and return the workbook."""
    filepath = filedialog.askopenfilename(
        title="Open Budgetinator File",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )

    if filepath:
        try:
            workbook = openpyxl.load_workbook(filepath)
            return workbook, filepath
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            return None, None
    return None, None


def save_file(workbook, filepath=None):
    """Save the workbook to a file."""
    if not filepath:
        filepath = filedialog.asksaveasfilename(
            title="Save Budgetinator File As",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

    if filepath:
        try:
            workbook.save(filepath)
            messagebox.showinfo("Success", "File saved successfully!")
            return filepath
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            return None
    return None


def new_file():
    """Create a new Excel workbook."""
    workbook = openpyxl.Workbook()
    if "Sheet" in workbook.sheetnames:
        workbook.remove(workbook["Sheet"])
    return workbook, None
