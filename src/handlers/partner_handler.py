"""
Partner management functions for working with Excel workbooks.
"""
import openpyxl
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, StringVar
import tkinter as tk
from openpyxl.styles import PatternFill
import datetime

class PartnerDialog(Toplevel):
    """Dialog for entering partner details"""
    def __init__(self, master, partner_number, partner_acronym):
        super().__init__(master)
        self.title("Add Partner Details")
        self.resizable(False, False)
        self.result = None
        self.vars = {}
        fields = [
            ("partner_identification_code", "Partner ID Code"),
            ("name_of_beneficiary", "Name of Beneficiary"),
            ("country", "Country"),
            ("role", "Role"),
            ("total_estimated_income", "Total Estimated Income"),
            ("other_explanation_income", "Other Explanation Income"),
            ("other_explanation_contributions", "Other Explanation Contributions"),
            ("other_explanation_self", "Other Explanation Self")
        ]
        row = 0
        Label(self, text=f"Partner Number: {partner_number}").grid(
            row=row, column=0, sticky="w", padx=8, pady=2)
        row += 1
        Label(self, text=f"Partner Acronym: {partner_acronym}").grid(
            row=row, column=0, sticky="w", padx=8, pady=2)
        row += 1
        for key, label in fields:
            Label(self, text=label+":").grid(row=row, column=0, sticky="w", padx=8, pady=2)
            var = StringVar()
            entry = Entry(self, textvariable=var, width=32)
            entry.grid(row=row, column=1, padx=8, pady=2)
            self.vars[key] = var
            row += 1
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=8)
        Button(btn_frame, text="Commit", command=self.commit).pack(side="left", padx=8)
        Button(btn_frame, text="Cancel", command=self.cancel).pack(side="left", padx=8)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.grab_set()
        self.wait_window()

    def commit(self):
        self.result = {k: v.get() for k, v in self.vars.items()}
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

def add_partner_to_workbook(workbook, partner_info, dev_log=None):
    """Add a partner worksheet to an Excel workbook"""
    sheet_name = f"P{partner_info['project_partner_number']} {partner_info['partner_acronym']}"
    if sheet_name in workbook.sheetnames:
        messagebox.showerror("Error", "Worksheet already exists.")
        return False

    ws = workbook.create_sheet(title=sheet_name)
    
    # Map fields to cell ranges for merging and value insertion
    merge_map = {
        "project_partner_number": "D2:E2",
        "partner_identification_code": "D4:E4",
        "partner_acronym": "D3:E3",
        "name_of_beneficiary": "D13",
        "country": "D5:E5",
        "role": "D6:E6"
    }
    
    # Merge and set values for mapped fields
    debug_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
    for key, cell_range in merge_map.items():
        value = partner_info.get(key, "")
        if ":" in cell_range:
            ws.merge_cells(cell_range)
            start_cell = cell_range.split(":")[0]
            # Fill merged range for debugging
            min_col = openpyxl.utils.cell.column_index_from_string(start_cell[0])
            min_row = int(start_cell[1:])
            end_cell = cell_range.split(":")[1]
            max_col = openpyxl.utils.cell.column_index_from_string(end_cell[0])
            max_row = int(end_cell[1:])
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    ws.cell(row=row, column=col).fill = debug_fill
        else:
            start_cell = cell_range
        ws[start_cell] = value

    # Update version history
    update_version_history(workbook, f"Added partner: {sheet_name}")
    
    return True

def update_version_history(workbook, summary):
    """Update the version history sheet with a new entry"""
    from version import full_version_string
    version_sheet_name = "Version History"
    version_info = full_version_string()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if version_sheet_name not in workbook.sheetnames:
        vh_ws = workbook.create_sheet(title=version_sheet_name)
        vh_ws.append(["Timestamp", "Version Info", "Summary"])
    else:
        vh_ws = workbook[version_sheet_name]
    
    vh_ws.append([timestamp, version_info, summary])
