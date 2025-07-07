import tkinter as tk
from tkinter import ttk, messagebox

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
            
        try:
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
            
            # Import and call work_package_table_format
            try:
                from ..config import work_package_table_format
                work_package_table_format.format_table(self.workbook)
            except ImportError:
                # In case the relative import fails, try absolute import
                from config import work_package_table_format
                work_package_table_format.format_table(self.workbook)
            except Exception as e:
                # Log the error but don't prevent saving
                print(f"Warning: Could not apply table formatting: {str(e)}")
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save workpackage:\n{str(e)}"
            )
