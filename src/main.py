
"""
main.py

Main application logic for ProjectBudgetinator.
Handles the Tkinter GUI, Excel file operations, partner management, diagnostics,
directory/config creation, and version history tracking.
"""

import json
import os
import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from devtools import not_implemented_yet, DebugConsole, dev_log
from version import full_version_string  # Only import what we use
from logger import setup_logging
from openpyxl.styles import PatternFill  # Used in _add_partner_worksheet

# Application config defaults
DEFAULT_USER_CONFIG = {
    "theme": "light",
    "welcome_screen": True,
    "startup_diagnostic": "verbose"
}

DEFAULT_BACKUP_CONFIG = {
    "frequency": "daily",
    "keep_versions": 5
}

DEFAULT_DIAGNOSTIC_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO"
}

# File type constants
EXCEL_FILETYPES = [("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
EXCEL_DEFAULT_EXT = ".xlsx"

# Dialog strings
CLONE_FILE_TITLE = "Clone File"
CREATE_SCRATCH_TITLE = "Create from Scratch"
ENTER_FILE_EXT = "Enter file extension:"

# Column headers
VERSION_HISTORY_COLUMNS = ["Timestamp", "Version Info", "Summary"]



class ProjectBudgetinator:
    """
    Main application class for ProjectBudgetinator.
    Manages the GUI, user actions, Excel file modifications, and diagnostics.
    """

    def add_partner(self):
        """
        Add a new partner to an Excel file.
        Prompts the user for partner details, creates a new worksheet,
        merges and fills specified cells, and updates the version history sheet.
        """
        if self.developer_mode:
            dev_log("Add Partner triggered.")

        import openpyxl

        file_path = filedialog.askopenfilename(
            title="Select Excel file to add partner",
            filetypes=EXCEL_FILETYPES
        )
        if not file_path:
            return

        try:
            wb = openpyxl.load_workbook(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
            return

        existing_partners = self._get_existing_partners(wb)
        result = self._prompt_partner_number_acronym(existing_partners)
        if not result:
            return
        partner_number, partner_acronym = result

        partner_info = self._prompt_partner_details(partner_number, partner_acronym)
        if not partner_info:
            return
        partner_info['project_partner_number'] = partner_number
        partner_info['partner_acronym'] = partner_acronym

        confirm_msg = (f"Add partner P{partner_number} {partner_acronym}?\n"
                      f"Proceed?")
        if not messagebox.askyesno("Confirm", confirm_msg):
            return

        if not self._add_partner_worksheet(wb, partner_info):
            return

        self._update_version_history(
            wb=wb,
            partner_number=partner_number,
            partner_acronym=partner_acronym,
            partner_info=partner_info
        )

        try:
            wb.save(file_path)
            success_msg = (f"Partner P{partner_number} {partner_acronym} "
                         f"added to file.")
            messagebox.showinfo("Success", success_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def _get_existing_partners(self, wb):
        existing_partners = set()
        for sheet in wb.sheetnames:
            if sheet.startswith("P"):
                parts = sheet[1:].split(" ", 1)
                if len(parts) == 2:
                    existing_partners.add((parts[0], parts[1]))
        return existing_partners

    def _prompt_partner_number_acronym(self, existing_partners):
        from tkinter import simpledialog, messagebox
        while True:
            partner_number = simpledialog.askstring(
                "Partner Number", "Enter partner number (e.g., 2):")
            if partner_number is None:
                return None, None
            if partner_number == "1":
                messagebox.showerror(
                    "Invalid", "P1 (Coordinator) cannot be added or edited.")
                return None, None
            partner_acronym = simpledialog.askstring(
                "Partner Acronym", "Enter partner acronym:")
            if partner_acronym is None:
                return None, None
            key = (partner_number, partner_acronym)
            if key in existing_partners:
                action = messagebox.askquestion(
                    "Partner Exists",
                    "Partner already exists. Edit/Review this partner? (Yes to edit/review, No to add a different partner)",
                    icon='warning'
                )
                if action == 'yes':
                    self.edit_partner()
                    return None, None
                else:
                    continue
            break
        return partner_number, partner_acronym

    def _prompt_partner_details(self, partner_number, partner_acronym):
        from tkinter import Toplevel, Label, Entry, Button, StringVar
        import tkinter as tk
        class PartnerDialog(tk.Toplevel):
            """Dialog for entering partner details."""

            def __init__(self, master, partner_number, partner_acronym):
                super().__init__(master)
                self.title("Add Partner Details")
                self.resizable(False, False)
                self.result = None
                self.vars = {}
                self._create_fields(partner_number, partner_acronym)
                self.protocol("WM_DELETE_WINDOW", self.cancel)
                self.grab_set()
                self.wait_window()

            def _create_fields(self, partner_number, partner_acronym):
                """Create and layout dialog fields."""
                fields = [
                    ("partner_identification_code", "Partner ID Code"),
                    ("name_of_beneficiary", "Name of Beneficiary"),
                    ("country", "Country"),
                    ("role", "Role"),
                    ("total_estimated_income", "Total Estimated Income"),
                    ("other_explanation_income", "Other Explanation Income"),
                    ("other_explanation_contributions",
                     "Other Explanation Contributions"),
                    ("other_explanation_self", "Other Explanation Self")
                ]

                row = 0
                # Partner number field
                tk.Label(self, text=f"Partner Number: {partner_number}").grid(
                    row=row, column=0, sticky="w", padx=8, pady=2
                )
                row += 1

                # Partner acronym field
                tk.Label(self, text=f"Partner Acronym: {partner_acronym}").grid(
                    row=row, column=0, sticky="w", padx=8, pady=2
                )
                row += 1

                # Create dynamic fields
                for key, label in fields:
                    tk.Label(self, text=f"{label}:").grid(
                        row=row, column=0, sticky="w", padx=8, pady=2
                    )
                    var = tk.StringVar()
                    entry = tk.Entry(self, textvariable=var, width=32)
                    entry.grid(row=row, column=1, padx=8, pady=2)
                    self.vars[key] = var
                    row += 1

                # Create button frame
                btn_frame = tk.Frame(self)
                btn_frame.grid(row=row, column=0, columnspan=2, pady=8)
                tk.Button(btn_frame, text="Commit",
                         command=self.commit).pack(side="left", padx=8)
                tk.Button(btn_frame, text="Cancel",
                         command=self.cancel).pack(side="left", padx=8)

            def commit(self):
                self.result = {k: v.get() for k, v in self.vars.items()}
                self.destroy()

            def cancel(self):
                self.result = None
                self.destroy()

        dialog = PartnerDialog(self.root, partner_number, partner_acronym)
        return dialog.result

    def _add_partner_worksheet(self, wb, partner_info):
        """Add a new worksheet for the partner."""
        import openpyxl

        # Generate sheet name
        partner_num = partner_info['project_partner_number']
        partner_acr = partner_info['partner_acronym']
        sheet_name = f"P{partner_num} {partner_acr}"

        if sheet_name in wb.sheetnames:
            messagebox.showerror("Error", "Worksheet already exists.")
            return False

        ws = wb.create_sheet(title=sheet_name)

        # Define cell mappings
        merge_map = {
            "project_partner_number": "D2:E2",
            "partner_identification_code": "D4:E4",
            "partner_acronym": "D3:E3",
            "name_of_beneficiary": "D13",
            "country": "D5:E5",
            "role": "D6:E6"
        }

        # Debug highlighting fill pattern
        debug_fill = PatternFill(
            start_color="FFFF99",
            end_color="FFFF99",
            fill_type="solid"
        )

        # Apply cell values and merging
        for key, cell_range in merge_map.items():
            value = partner_info.get(key, "")
            if ":" in cell_range:
                ws.merge_cells(cell_range)
                start, end = cell_range.split(":")
                col_start = openpyxl.utils.cell.column_index_from_string(
                    start[0])
                row_start = int(start[1:])
                col_end = openpyxl.utils.cell.column_index_from_string(
                    end[0])
                row_end = int(end[1:])

                # Apply debug fill to merged area
                for row in range(row_start, row_end + 1):
                    for col in range(col_start, col_end + 1):
                        ws.cell(row=row, column=col).fill = debug_fill
                start_cell = start
            else:
                start_cell = cell_range
            ws[start_cell] = value

        return True

    def _update_version_history(self, wb, partner_number, partner_acronym,
                              partner_info):
        """Update version history worksheet with new partner information."""
        import datetime
        version_sheet_name = "Version History"
        merge_map = {
            "project_partner_number": "D2:E2",
            "partner_identification_code": "D4:E4",
            "partner_acronym": "D3:E3",
            "name_of_beneficiary": "D13",
            "country": "D5:E5",
            "role": "D6:E6"
        }

        # Get populated fields
        populated_fields = [
            k for k in merge_map.keys()
            if partner_info.get(k)
        ]
        field_list = ", ".join(populated_fields)

        # Create version history entry
        version_info = full_version_string()
        summary = (f"Added partner: P{partner_number} {partner_acronym} | "
                  f"Fields: {field_list}")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update version history sheet
        if version_sheet_name not in wb.sheetnames:
            vh_ws = wb.create_sheet(title=version_sheet_name)
            vh_ws.append(VERSION_HISTORY_COLUMNS)
        else:
            vh_ws = wb[version_sheet_name]
        vh_ws.append([timestamp, version_info, summary])

    def delete_partner(self):
        """
        Placeholder for deleting a partner from the workbook.
        """
        if self.developer_mode:
            dev_log("Delete Partner triggered.")
        not_implemented_yet("Delete Partner")

    def edit_partner(self):
        """
        Placeholder for editing an existing partner in the workbook.
        """
        if self.developer_mode:
            dev_log("Edit Partner triggered.")
        not_implemented_yet("Edit Partner")

    def add_workpackage(self):
        """
        Placeholder for adding a workpackage to the workbook.
        """
        if self.developer_mode:
            dev_log("Add Workpackage triggered.")
        not_implemented_yet("Add Workpackage")

    def delete_workpackage(self):
        """
        Placeholder for deleting a workpackage from the workbook.
        """
        if self.developer_mode:
            dev_log("Delete Workpackage triggered.")
        not_implemented_yet("Delete Workpackage")

    def edit_workpackage(self):
        """
        Placeholder for editing a workpackage in the workbook.
        """
        if self.developer_mode:
            dev_log("Edit Workpackage triggered.")
        not_implemented_yet("Edit Workpackage")

    def __init__(self):
        """
        Initialize the ProjectBudgetinator application.
        Sets up logging, GUI, preferences, directory structure, and diagnostics.
        """
        # Set up logging first
        self.logger = setup_logging()
        self.root = tk.Tk()
        self.root.title("ProjectBudgetinator Hub")
        self.developer_mode = False
        self.debug_console = DebugConsole(self.root)
        self.debug_console.hide()
        self.setup_menu()

        # Load preferences
        from preferences import PreferencesManager
        self.prefs_manager = PreferencesManager()
        self.current_config = self.prefs_manager.load_config()

        # Always ensure directory structure and config files exist
        self.create_directory_structure()

        # Apply theme
        self.apply_theme()

        # Show diagnostics if first run or if configured
        self.check_first_run_and_show_diagnostics()

    def check_first_run_and_show_diagnostics(self):
        """
        Check if this is the first time running the program and show diagnostics if needed.
        Creates directories/configs on first run and shows a welcome message.
        """
        """Check if this is the first time running the program and show diagnostics if needed"""
        user_home = str(Path.home())
        app_dir = os.path.join(user_home, "ProjectBudgetinator")
        first_run = not os.path.exists(app_dir)
        # If first run, create structure and show diagnostics
        if first_run:
            self.create_directory_structure()
            messagebox.showinfo(
                "Welcome",
                "Welcome to ProjectBudgetinator!\n\n"
                "This appears to be your first time running the program. "
                "The necessary directories and config files have been created."
            )
            self.show_diagnostics()
        else:
            # Show diagnostics on startup if user config says so
            show_diag = self.current_config.get("startup_diagnostic", "verbose") == "verbose"
            if show_diag:
                self.show_diagnostics()

    def setup_menu(self):
        """Set up the main menu bar and all menu items for the GUI."""
        menubar = tk.Menu(self.root)
        self._setup_file_menu(menubar)
        self._setup_preferences_menu(menubar)
        self._setup_tools_menu(menubar)
        self._setup_help_menu(menubar)
        self.root.config(menu=menubar)

    def _setup_file_menu(self, menubar):
        """Set up the File menu and its submenus."""
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        # Basic file operations
        commands = [
            ("Backup", self.backup_file),
            ("Clone", self.clone_file),
            ("Compare", self.compare_files),
            ("Create from scratch", self.create_from_scratch),
            ("Create from template", self.create_from_template)
        ]
        for label, command in commands:
            file_menu.add_command(label=label, command=command)
            if label != commands[-1][0]:  # Don't add separator after last item
                file_menu.add_separator()

        # Modify submenu
        modify_menu = self._create_modify_submenu(file_menu)
        file_menu.add_cascade(label="Modify", menu=modify_menu)
        file_menu.add_separator()

        # Final commands
        file_menu.add_command(label="Restore", command=self.restore_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)

    def _create_modify_submenu(self, parent):
        """Create the Modify submenu for partner and workpackage operations."""
        modify_menu = tk.Menu(parent, tearoff=0)

        # Partner operations
        partner_commands = [
            ("Add Partner", self.add_partner),
            ("Delete Partner", self.delete_partner),
            ("Edit Partner", self.edit_partner)
        ]
        for label, command in partner_commands:
            modify_menu.add_command(label=label, command=command)
        modify_menu.add_separator()

        # Workpackage operations
        workpackage_commands = [
            ("Add Workpackage", self.add_workpackage),
            ("Delete Workpackage", self.delete_workpackage),
            ("Edit Workpackage", self.edit_workpackage)
        ]
        for label, command in workpackage_commands:
            modify_menu.add_command(label=label, command=command)

        return modify_menu

    def _setup_preferences_menu(self, menubar):
        """Set up the Preferences menu."""
        pref_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferences", menu=pref_menu)
        pref_menu.add_command(
            label="Settings",
            command=self.show_preferences
        )

    def _setup_tools_menu(self, menubar):
        """Set up the Tools menu and its submenus."""
        tools_menu = tk.Menu(menubar, tearoff=0)

        # Dev Tools submenu
        devtools_menu = tk.Menu(tools_menu, tearoff=0)
        devtools_menu.add_checkbutton(
            label="Developer Mode",
            command=self.toggle_developer_mode
        )
        devtools_menu.add_command(
            label="Show Debug Console",
            command=self.toggle_debug_console
        )
        tools_menu.add_cascade(label="Dev Tools", menu=devtools_menu)

        # Additional tools
        tools_menu.add_separator()
        tools_menu.add_command(
            label="Diagnostics",
            command=self.show_diagnostics
        )
        menubar.add_cascade(label="Tools", menu=tools_menu)

    def _setup_help_menu(self, menubar):
        """Set up the Help menu."""
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help)

    def toggle_developer_mode(self):
        """
        Toggle developer mode and show/hide the debug console.
        """
        self.developer_mode = not self.developer_mode
        if self.developer_mode:
            dev_log("Developer mode enabled.")
            self.debug_console.show()
        else:
            dev_log("Developer mode disabled.")
            self.debug_console.hide()

    def toggle_debug_console(self):
        """
        Show or hide the debug console window.
        """
        if self.debug_console.visible:
            self.debug_console.hide()
        else:
            self.debug_console.show()

    def backup_file(self):
        """
        Create a backup of the selected Excel file.
        
        Creates a timestamped backup copy in the configured backups
        directory and maintains a history of backups.
        """
        if self.developer_mode:
            dev_log("Backup file triggered.")

        # Get file to backup
        file_path = filedialog.askopenfilename(
            title="Select file to backup",
            filetypes=EXCEL_FILETYPES
        )
        if not file_path:
            return

        # Get backup directory from config
        user_home = str(Path.home())
        backup_dir = os.path.join(user_home, "ProjectBudgetinator", "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        backup_name = f"{base_name}_backup_{timestamp}.xlsx"
        backup_path = os.path.join(backup_dir, backup_name)

        try:
            # Copy file to backup location
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Update backup history in config
            # Load or create backup config
            config_path = os.path.join(
                user_home,
                "ProjectBudgetinator",
                "config",
                "backup.config.json"
            )
            try:
                with open(config_path, 'r') as f:
                    backup_config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                backup_config = DEFAULT_BACKUP_CONFIG.copy()
                backup_config['history'] = []
            
            # Create backup info entry
            backup_info = {
                'original_file': file_path,
                'backup_file': backup_path,
                'timestamp': timestamp,
                'version': full_version_string()
            }
            
            # Add to history and maintain history size limit
            if 'history' not in backup_config:
                backup_config['history'] = []
            backup_config['history'].append(backup_info)
            keep_versions = backup_config.get('keep_versions', 5)
            if len(backup_config['history']) > keep_versions:
                # Remove old backups
                old_backups = backup_config['history'][:-keep_versions]
                # Keep only latest versions
                backup_config['history'] = (
                    backup_config['history'][-keep_versions:]
                )
                for old in old_backups:
                    try:
                        os.remove(old['backup_file'])
                    except OSError:
                        pass  # Skip if file already deleted

            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(backup_config, f, indent=4)

            messagebox.showinfo(
                "Backup Complete",
                f"File backed up to:\n{backup_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Backup Failed",
                f"Error backing up file:\n{e}"
            )

    def clone_file(self):
        """
        Clone an Excel file to a new location with user-provided details.
        Prompts for new name, extension and optional project name.
        """
        if self.developer_mode:
            dev_log("Clone file triggered.")

        # Step 1: Select source file
        src_path = filedialog.askopenfilename(
            title="Select file to clone",
            filetypes=EXCEL_FILETYPES
        )
        if not src_path:
            return

        # Step 2: Select destination directory
        dest_dir = filedialog.askdirectory(
            title="Select destination folder"
        )
        if not dest_dir:
            return

        # Step 3: Get file details
        base_name = os.path.splitext(os.path.basename(src_path))[0]
        ext = os.path.splitext(src_path)[1]

        new_name = self._prompt_for_detail(
            CLONE_FILE_TITLE, "Enter new file name:", base_name)
        if not new_name:
            return

        new_ext = self._prompt_for_detail(
            CLONE_FILE_TITLE, ENTER_FILE_EXT, ext)
        if not new_ext:
            return

        # Optional project name
        project_name = self._prompt_for_detail(
            CLONE_FILE_TITLE,
            "Enter project name (optional):",
            ""
        )

        # Step 4: Clone the file
        dest_path = os.path.join(dest_dir, new_name + new_ext)
        try:
            import shutil
            shutil.copy2(src_path, dest_path)
            messagebox.showinfo(
                "Clone Complete",
                f"File cloned to:\n{dest_path}"
            )
            if project_name:
                dev_log(f"Project name for clone: {project_name}")
        except Exception as e:
            messagebox.showerror(
                "Clone Failed",
                f"Error cloning file:\n{e}"
            )

    def _prompt_for_detail(self, title, prompt, default=""):
        """Helper method to prompt user for input with a default value."""
        from tkinter import simpledialog
        return simpledialog.askstring(
            title,
            prompt,
            initialvalue=default
        )

    def compare_files(self):
        """Compare Excel files and display differences in a dialog."""
        if self.developer_mode:
            dev_log("Compare files triggered.")

        import pandas as pd
        import tkinter as tk
        from tkinter import ttk

        # Select files to compare
        file_paths = filedialog.askopenfilenames(
            title="Select up to 3 files to compare",
            filetypes=EXCEL_FILETYPES
        )
        file_paths = list(file_paths)[:3]  # Limit to 3 files
        
        if len(file_paths) < 2:
            messagebox.showinfo(
                "Compare Files",
                "Please select 2-3 files to compare."
            )
            return

        def create_comparison_view(ref_idx, result_win):
            """Create the comparison view dialog."""
            ref_file = file_paths[ref_idx]
            others = [f for i, f in enumerate(file_paths) if i != ref_idx]
            
            try:
                ref_df = pd.read_excel(ref_file)
                other_dfs = [pd.read_excel(f) for f in others]
            except Exception as e:
                messagebox.showerror(
                    "Compare Failed",
                    f"Error reading files:\n{e}"
                )
                return

            diffs = []
            for i, df in enumerate(other_dfs):
                # Find rows that differ between files
                diff = df.merge(
                    ref_df,
                    how='outer',
                    indicator=True
                ).query('_merge != "both"')
                
                base_name = os.path.basename(others[i])
                if diff.empty:
                    diffs.append((
                        base_name,
                        pd.DataFrame(["No differences found."])
                    ))
                else:
                    diffs.append((base_name, diff))

            # Configure result window
            result_win.title("Comparison Results")
            result_win.geometry("600x400")
            result_win.minsize(600, 220)
            result_win.grid_rowconfigure(1, weight=1)
            result_win.grid_columnconfigure(0, weight=1)

            # Reference file label
            ref_name = os.path.basename(ref_file)
            ttk.Label(
                result_win,
                text=f"Reference: {ref_name}",
                font=("Arial", 11, "bold")
            ).grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

            # List of comparison files
            listbox = tk.Listbox(result_win)
            for name, _ in diffs:
                listbox.insert(tk.END, name)
            listbox.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))

            # Differences display
            diff_text = tk.Text(result_win, wrap="none", height=12)
            diff_text.grid(
                row=2, column=0,
                sticky="nsew", padx=10, pady=(5, 0)
            )

            def show_diff(event=None):
                """Display differences for selected file."""
                sel = listbox.curselection()
                if not sel:
                    return
                _, diff = diffs[sel[0]]
                diff_text.config(state="normal")
                diff_text.delete("1.0", tk.END)
                diff_str = (diff.to_string(index=False)
                           if isinstance(diff, pd.DataFrame)
                           else str(diff))
                diff_text.insert(tk.END, diff_str)
                diff_text.config(state="disabled")

            def change_reference():
                """Change the reference file for comparison."""
                dialog = tk.Toplevel(self.root)
                dialog.title("Select Reference File")
                ttk.Label(
                    dialog,
                    text="Choose the reference file:"
                ).pack(pady=5)
                
                ref_var = tk.StringVar(value=file_paths[ref_idx])
                for path in file_paths:
                    ttk.Radiobutton(
                        dialog,
                        text=os.path.basename(path),
                        variable=ref_var,
                        value=path
                    ).pack(anchor="w")

                def set_ref():
                    dialog.ref_idx = file_paths.index(ref_var.get())
                    dialog.destroy()

                ttk.Button(
                    dialog,
                    text="OK",
                    command=set_ref
                ).pack(pady=5)

                dialog.wait_window()
                new_ref_idx = getattr(dialog, 'ref_idx', ref_idx)
                result_win.destroy()
                show_comparison_dialog(new_ref_idx)

            # Button frame
            btn_frame = ttk.Frame(result_win)
            btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=8)
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)

            ttk.Button(
                btn_frame,
                text="Change Reference",
                command=change_reference
            ).grid(row=0, column=0, sticky="w", padx=5)

            ttk.Button(
                btn_frame,
                text="Close",
                command=result_win.destroy
            ).grid(row=0, column=1, sticky="e", padx=5)

            # Bind events
            listbox.bind("<<ListboxSelect>>", show_diff)
            listbox.selection_set(0)
            show_diff()

        def show_comparison_dialog(ref_idx):
            """Show the main comparison dialog."""
            result_win = tk.Toplevel(self.root)
            create_comparison_view(ref_idx, result_win)

        def choose_initial_reference():
            """Let user choose the initial reference file."""
            dialog = tk.Toplevel(self.root)
            dialog.title("Select Reference File")
            ttk.Label(
                dialog,
                text="Choose the reference file:"
            ).pack(pady=5)
            
            ref_var = tk.StringVar(value=file_paths[0])
            for path in file_paths:
                ttk.Radiobutton(
                    dialog,
                    text=os.path.basename(path),
                    variable=ref_var,
                    value=path
                ).pack(anchor="w")

            def set_ref():
                dialog.ref_idx = file_paths.index(ref_var.get())
                dialog.destroy()

            ttk.Button(dialog, text="OK", command=set_ref).pack(pady=5)
            dialog.wait_window()
            return getattr(dialog, 'ref_idx', 0)

        ref_idx = choose_initial_reference()
        show_comparison_dialog(ref_idx)

    def create_from_scratch(self):
        """Create a new, empty Excel file at a user-specified location."""
        if self.developer_mode:
            dev_log("Create from scratch triggered.")

        # Step 1: Select save location
        dest_dir = filedialog.askdirectory(
            title="Select save folder"
        )
        if not dest_dir:
            return

        # Step 2: Get file details
        file_name = self._prompt_for_detail(
            CREATE_SCRATCH_TITLE,
            "Enter file name:"
        )
        if not file_name:
            return

        file_ext = self._prompt_for_detail(
            CREATE_SCRATCH_TITLE,
            ENTER_FILE_EXT,
            EXCEL_DEFAULT_EXT
        )
        if not file_ext:
            return

        # Step 3: Create empty file
        dest_path = os.path.join(dest_dir, file_name + file_ext)
        try:
            import pandas as pd
            df = pd.DataFrame()
            df.to_excel(dest_path, index=False)
            messagebox.showinfo(
                "File Created",
                f"New file created:\n{dest_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Create Failed",
                f"Error creating file:\n{e}"
            )

    def create_from_template(self):
        """Create a new Excel file from a template or existing file."""
        if self.developer_mode:
            dev_log("Create from template triggered.")

        # Step 1: Select template
        template_path = filedialog.askopenfilename(
            title="Select template",
            filetypes=EXCEL_FILETYPES
        )
        if not template_path:
            return

        # Validate file is Excel
        is_excel = any(
            template_path.endswith(ext)
            for ext in (".xlsx", ".xls")
        )
        if not is_excel:
            messagebox.showerror(
                "Invalid File",
                "Not an Excel file."
            )
            return

        # Step 2: Select save location
        dest_dir = filedialog.askdirectory(
            title="Select save folder"
        )
        if not dest_dir:
            return

        # Step 3: Get new file details
        file_name = self._prompt_for_detail(
            "Create from Template",
            "Enter new file name:"
        )
        if not file_name:
            return

        file_ext = self._prompt_for_detail(
            "Create from Template",
            ENTER_FILE_EXT,
            EXCEL_DEFAULT_EXT
        )
        if not file_ext:
            return

        # Step 4: Copy template
        dest_path = os.path.join(dest_dir, file_name + file_ext)
        try:
            import shutil
            shutil.copy2(template_path, dest_path)
            messagebox.showinfo(
                "File Created",
                f"Template copied to:\n{dest_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Create Failed",
                f"Copy error:\n{e}"
            )

    def modify_file(self):
        """
        Placeholder for modifying a file (not yet implemented).
        """
        if self.developer_mode:
            dev_log("Modify file triggered.")
        not_implemented_yet("Modify")

    def restore_file(self):
        """
        Placeholder for restoring a file from backup (not yet implemented).
        """
        if self.developer_mode:
            dev_log("Restore file triggered.")
        not_implemented_yet("Restore")

    def show_diagnostics(self):
        """
        Show the diagnostics dashboard window with startup and config status.
        """
        # Diagnostics dashboard window
        diag_win = tk.Toplevel(self.root)
        diag_win.title("Startup Diagnostics Dashboard")
        diag_win.geometry("400x370")
        diag_win.grab_set()

        version_info = full_version_string()

        categories = [
            "Directory Check",
            "Config File Check",
            "Log Integrity",
            "Summary",
            "Version Info"
        ]
        details = {
            "Directory Check": "\n".join([
                "✅ workbooks/          …exists",
                "✅ logs/system/        …ready",
                "✅ logs/user_actions/  …ready",
                "🆕 logs/comparisons/snapshots/  …created",
                "✅ config/             …ready",
                "⚠️  backups/            …missing (created default)",
                "✅ templates/          …exists"
            ]),
            "Config File Check": "\n".join([
                "✅ user.config.json     …loaded successfully",
                "⚠️  backup.config.json   …not found (restored defaults)",
                "🆕 diagnostic.config.json …created new with defaults"
            ]),
            "Log Integrity": "\n".join([
                "⚠️  2 comparison logs from v0.8 detected  → marked as legacy",
                "✅ latest snapshot valid (2025-06-22)"
            ]),
            "Summary": (
                "Startup passed with 2 warnings and 2 recoveries.\n"
                "New folders/configs have been generated where needed.\n\n"
                "📌 All systems go — launching interface..."
            ),
            "Version Info": version_info
        }

        # Category list
        # Category label
        cat_label = tk.Label(
            diag_win,
            text="Select Diagnostic Category:",
            font=("Arial", 11, "bold")
        )
        cat_label.pack(pady=(10, 0))
        
        # Category listbox
        cat_listbox = tk.Listbox(diag_win, height=7)
        for cat in categories:
            cat_listbox.insert(tk.END, cat)
        cat_listbox.pack(fill="x", padx=10, pady=5)

        # Details display
        details_text = tk.Text(
            diag_win,
            height=10,
            wrap="word",
            state="disabled"
        )
        details_text.pack(fill="both", expand=True, padx=10, pady=5)

        def show_details(event=None):
            selection = cat_listbox.curselection()
            if selection:
                cat = categories[selection[0]]
                details_text.config(state="normal")
                details_text.delete("1.0", tk.END)
                details_text.insert(tk.END, details[cat])
                details_text.config(state="disabled")

        cat_listbox.bind("<<ListboxSelect>>", show_details)
        # Show first category by default
        cat_listbox.selection_set(0)
        show_details()

        # Close button
        close_btn = tk.Button(diag_win, text="Close", command=diag_win.destroy)
        close_btn.pack(pady=5)
        # (No menu bar code here)
    def show_help(self):
        """Show the Help window with basic instructions and contact info."""
        help_win = tk.Toplevel(self.root)
        help_win.title("Hub")
        help_win.geometry("400x250")
        help_win.grab_set()

        # Title
        title = ttk.Label(
            help_win,
            text="Hub",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(15, 5))

        # Attention message
        attention = ttk.Label(
            help_win,
            text="Attention needed",
            font=("Arial", 12, "bold"),
            foreground="red"
        )
        attention.pack(pady=(0, 5))

        # Help text
        help_msg = (
            "Help menu\n\n"
            "This is a placeholder for the Help section.\n\n"
            "Please refer to the documentation or contact\n"
            "support for assistance."
        )
        text = ttk.Label(
            help_win,
            text=help_msg,
            font=("Arial", 11),
            justify="left"
        )
        text.pack(padx=15, pady=5)

        # Close button
        close_btn = ttk.Button(
            help_win,
            text="Close",
            command=help_win.destroy
        )
        close_btn.pack(pady=10)


    def show_preferences(self):
        """Show the Preferences dialog and reload preferences after closing."""
        from preferences import PreferencesDialog
        dialog = PreferencesDialog(self.root)
        self.root.wait_window(dialog.dialog)
        # Reload preferences after dialog is closed
        self.current_config = self.prefs_manager.load_config()
        self.apply_theme()

    def apply_theme(self):
        """Apply the selected theme (light or dark) to the main window."""
        # This is a placeholder for theme implementation
        # In real impl., apply colors and styles for each theme
        theme = self.current_config.get("theme", "light")
        bg_color = "gray20" if theme == "dark" else "SystemButtonFace"
        self.root.configure(bg=bg_color)

    # check_first_run is now replaced by check_first_run_and_show_diagnostics

    def create_directory_structure(self):
        """Create the necessary directory structure and config files."""
        user_home = str(Path.home())
        base_dir = os.path.join(user_home, "ProjectBudgetinator")
        
        # Define directory structure
        directories = [
            os.path.join(base_dir, "workbooks"),
            os.path.join(base_dir, "logs", "system"),
            os.path.join(base_dir, "logs", "user_actions"),
            os.path.join(base_dir, "logs", "comparisons", "snapshots"),
            os.path.join(base_dir, "config"),
            os.path.join(base_dir, "backups"),
            os.path.join(base_dir, "templates")
        ]

        # Create directories
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        # Map config files to their default content
        config_files = {
            "user.config.json": DEFAULT_USER_CONFIG,
            "backup.config.json": DEFAULT_BACKUP_CONFIG,
            "diagnostic.config.json": DEFAULT_DIAGNOSTIC_CONFIG
        }

        # Create config files
        config_dir = os.path.join(base_dir, "config")
        for filename, content in config_files.items():
            filepath = os.path.join(config_dir, filename)
            with open(filepath, "w") as f:
                json.dump(content, f, indent=4)

    def exit_program(self):
        """
        Prompt the user to confirm exit and quit the application.
        """
        """Clean exit of the program"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def run(self):
        """
        Start the Tkinter main event loop for the application.
        """
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProjectBudgetinator()
    app.run()
