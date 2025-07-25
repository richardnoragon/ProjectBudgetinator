"""
Workpackage management functions for working with Excel workbooks.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils.error_handler import ExceptionHandler

# Create exception handler instance
exception_handler = ExceptionHandler()


@exception_handler.handle_exceptions(
    show_dialog=True, log_error=True, return_value=False
)
def add_workpackage_to_workbook(workbook, wp_info):
    """Add a workpackage to the PM Summary sheet in an Excel workbook."""
    ws = workbook["PM Summary"]
    row = wp_info['row']
    
    # Write the values
    ws[f'B{row}'] = wp_info['title']
    ws[f'D{row}'] = wp_info['lead_partner']
    ws[f'F{row}'] = wp_info['start_month']
    ws[f'G{row}'] = wp_info['end_month']
    
    return True


class AddWorkpackageDialog:
    def __init__(self, parent, workbook):
        """Initialize the dialog for adding a new workpackage.
        
        Args:
            parent: The parent window
            workbook: The Excel workbook object
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Workpackage")
        self.dialog.grab_set()
        
        self.workbook = workbook
        self.result = None
        
        # Get the PM Summary worksheet
        self.ws = self.workbook["PM Summary"]
        
        # Find next available row (scanning from A4 to A18)
        self.next_row = None
        for row in range(4, 19):
            if not self.ws[f'A{row}'].value:
                self.next_row = row
                break
                
        if self.next_row is None:
            messagebox.showerror(
                "Error",
                "No empty rows available for new workpackage (A4-A18 all filled)"
            )
            self.dialog.destroy()
            return
            
        # Create the form
        self._create_widgets()
        self._center_dialog()
        
    def _create_widgets(self):
        """Create and layout all dialog widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Row info label
        ttk.Label(
            main_frame,
            text=f"Adding workpackage in row {self.next_row}",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Entry fields
        self.title_var = tk.StringVar()
        self.lead_partner_var = tk.StringVar()
        self.start_month_var = tk.StringVar()
        self.end_month_var = tk.StringVar()
        
        # WP Title
        ttk.Label(main_frame, text="WP Title:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(
            main_frame,
            textvariable=self.title_var,
            width=40
        ).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Lead Partner
        ttk.Label(main_frame, text="Lead Partner:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(
            main_frame,
            textvariable=self.lead_partner_var,
            width=40
        ).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Start Month
        ttk.Label(main_frame, text="Start Month:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(
            main_frame,
            textvariable=self.start_month_var,
            width=10
        ).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # End Month
        ttk.Label(main_frame, text="End Month:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(
            main_frame,
            textvariable=self.end_month_var,
            width=10
        ).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Commit",
            command=self._on_commit
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        parent = self.dialog.master
        
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    @exception_handler.handle_exceptions(
        show_dialog=True, log_error=True, return_value=None
    )
    def _on_commit(self):
        """Handle the commit button click."""
        # Validate inputs (basic validation)
        if not all([
            self.title_var.get().strip(),
            self.lead_partner_var.get().strip(),
            self.start_month_var.get().strip(),
            self.end_month_var.get().strip()
        ]):
            messagebox.showerror(
                "Error",
                "All fields must be filled out"
            )
            return
            
        # Write values to worksheet
        self.ws[f'B{self.next_row}'] = self.title_var.get().strip()
        self.ws[f'D{self.next_row}'] = self.lead_partner_var.get().strip()
        self.ws[f'F{self.next_row}'] = self.start_month_var.get().strip()
        self.ws[f'G{self.next_row}'] = self.end_month_var.get().strip()
        
        # Set the result to indicate success
        self.result = {
            'row': self.next_row,
            'title': self.title_var.get().strip(),
            'lead_partner': self.lead_partner_var.get().strip(),
            'start_month': self.start_month_var.get().strip(),
            'end_month': self.end_month_var.get().strip()
        }
        
        # Import and call workpackage_table_format
        try:
            from ..config import workpackage_table_format
            workpackage_table_format.format_table(self.workbook)
        except ImportError:
            # In case the relative import fails, try absolute import
            try:
                from config import workpackage_table_format
                workpackage_table_format.format_table(self.workbook)
            except ImportError:
                print("Warning: Could not import workpackage_table_format")
        except Exception as e:
            # Log the error but don't prevent saving
            print(f"Warning: Could not apply table formatting: {str(e)}")
        
        # Update PM Overview after workpackage operation
        try:
            from handlers.update_pm_overview_handler import update_pm_overview_after_workpackage_operation
            parent_window = self.dialog.master if hasattr(self.dialog, 'master') else None
            pm_success = update_pm_overview_after_workpackage_operation(self.workbook, parent_window)
            if pm_success:
                print("PM Overview updated successfully after workpackage add")
            else:
                print("Warning: PM Overview update failed after workpackage add")
        except ImportError:
            print("Warning: Could not import PM Overview update function")
        except Exception as e:
            print(f"Warning: PM Overview update failed: {str(e)}")
        
        self.dialog.destroy()


# For backward compatibility
WorkpackageDialog = AddWorkpackageDialog
