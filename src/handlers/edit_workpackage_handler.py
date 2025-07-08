import tkinter as tk
from tkinter import ttk, messagebox


class EditWorkpackageDialog:
    def __init__(self, parent, workbook):
        """Initialize the dialog for editing a workpackage.
        
        Args:
            parent: The parent window
            workbook: The Excel workbook object
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Workpackage")
        self.dialog.grab_set()
        
        self.workbook = workbook
        self.result = None
        
        # Get the PM Summary worksheet
        self.ws = self.workbook["PM Summary"]
        
        # Get all workpackage rows (from A4 to A18)
        self.workpackages = []
        for row in range(4, 19):
            if self.ws[f'A{row}'].value:  # If there's a value in column A
                self.workpackages.append({
                    'row': row,
                    'title': self.ws[f'B{row}'].value or '',
                    'lead_partner': self.ws[f'D{row}'].value or '',
                    'start_month': self.ws[f'F{row}'].value or '',
                    'end_month': self.ws[f'G{row}'].value or ''
                })
                
        if not self.workpackages:
            messagebox.showinfo(
                "No Workpackages",
                "No workpackages found to edit."
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
        
        # Instructions label
        ttk.Label(
            main_frame,
            text="Select a workpackage to edit:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Create listbox for workpackages
        self.wp_listbox = tk.Listbox(main_frame, width=50, height=6)
        self.wp_listbox.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Populate listbox
        for wp in self.workpackages:
            self.wp_listbox.insert(tk.END, 
                f"Row {wp['row']}: {wp['title']} (Lead: {wp['lead_partner']})")
        
        # Entry fields frame
        entry_frame = ttk.LabelFrame(main_frame, text="Workpackage Details")
        entry_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Entry fields
        self.title_var = tk.StringVar()
        self.lead_partner_var = tk.StringVar()
        self.start_month_var = tk.StringVar()
        self.end_month_var = tk.StringVar()
        
        # WP Title
        ttk.Label(entry_frame, text="WP Title:").grid(
            row=0, column=0, sticky=tk.W, pady=2, padx=5
        )
        self.title_entry = ttk.Entry(
            entry_frame,
            textvariable=self.title_var,
            width=40
        )
        self.title_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Lead Partner
        ttk.Label(entry_frame, text="Lead Partner:").grid(
            row=1, column=0, sticky=tk.W, pady=2, padx=5
        )
        self.lead_partner_entry = ttk.Entry(
            entry_frame,
            textvariable=self.lead_partner_var,
            width=40
        )
        self.lead_partner_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Start Month
        ttk.Label(entry_frame, text="Start Month:").grid(
            row=2, column=0, sticky=tk.W, pady=2, padx=5
        )
        self.start_month_entry = ttk.Entry(
            entry_frame,
            textvariable=self.start_month_var,
            width=10
        )
        self.start_month_entry.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # End Month
        ttk.Label(entry_frame, text="End Month:").grid(
            row=3, column=0, sticky=tk.W, pady=2, padx=5
        )
        self.end_month_entry = ttk.Entry(
            entry_frame,
            textvariable=self.end_month_var,
            width=10
        )
        self.end_month_entry.grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
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
        
        # Bind selection event
        self.wp_listbox.bind('<<ListboxSelect>>', self._on_select)
        
        # Select first workpackage by default
        self.wp_listbox.selection_set(0)
        self._on_select()
        
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        parent = self.dialog.master
        
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    def _on_select(self, event=None):
        """Handle workpackage selection."""
        selection = self.wp_listbox.curselection()
        if not selection:
            return
            
        # Get selected workpackage
        wp = self.workpackages[selection[0]]
        
        # Update entry fields
        self.title_var.set(wp['title'])
        self.lead_partner_var.set(wp['lead_partner'])
        self.start_month_var.set(wp['start_month'])
        self.end_month_var.set(wp['end_month'])
        
    def _on_commit(self):
        """Handle the commit button click."""
        selection = self.wp_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select a workpackage to edit."
            )
            return
            
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
            # Get selected workpackage row
            row = self.workpackages[selection[0]]['row']
            
            # Write values to worksheet
            self.ws[f'B{row}'] = self.title_var.get().strip()
            self.ws[f'D{row}'] = self.lead_partner_var.get().strip()
            self.ws[f'F{row}'] = self.start_month_var.get().strip()
            self.ws[f'G{row}'] = self.end_month_var.get().strip()
            
            # Set the result to indicate success
            self.result = {
                'row': row,
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
                from config import workpackage_table_format
                workpackage_table_format.format_table(self.workbook)
            except Exception as e:
                # Log the error but don't prevent saving
                print(f"Warning: Could not apply table formatting: {str(e)}")
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save workpackage:\n{str(e)}"
            )
