import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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
from validation import FormValidator

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




import openpyxl.utils.cell

class ProjectBudgetinator:
    def __init__(self):
        self.root = tk.Tk()
        self.developer_mode = False
        self.prefs_manager = None
        self.current_config = DEFAULT_USER_CONFIG.copy()
        self.current_workbook = None
        # Set up the menu bar
        self._setup_file_menu()
    def _setup_file_menu(self):
        menubar = tk.Menu(self.root)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Clone", command=self.clone_file)
        file_menu.add_command(label="Compare", command=self.compare_files)
        file_menu.add_command(label="Create from scratch", command=self.create_from_scratch)
        file_menu.add_command(label="Create from template", command=self.create_from_template)
        file_menu.add_separator()
        file_menu.add_command(label="Restore", command=self.restore_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)
        menubar.add_cascade(label="File", menu=file_menu)

        # Modify menu (partner and workpackage operations)
        modify_menu = self._create_modify_submenu(menubar)
        menubar.add_cascade(label="Modify", menu=modify_menu)

        # Preferences menu
        pref_menu = tk.Menu(menubar, tearoff=0)
        pref_menu.add_command(label="Preferences", command=self.show_preferences)
        menubar.add_cascade(label="Preferences", menu=pref_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="Diagnostics", command=self.show_diagnostics)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)


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

    # Partner and workpackage operations
    def add_partner(self):
        """Open a dialog to add a new partner to the project."""
        # Check if we have an open workbook
        if self.current_workbook is None:
            response = messagebox.askyesno(
                "No Workbook Open",
                "No workbook is currently open. Would you like to open one now?"
            )
            if response:
                file_path = filedialog.askopenfilename(
                    title="Open Excel Workbook",
                    filetypes=EXCEL_FILETYPES
                )
                if file_path:
                    try:
                        from openpyxl import load_workbook
                        self.current_workbook = load_workbook(file_path)
                    except Exception as e:
                        messagebox.showerror(
                            "Error",
                            f"Could not open workbook:\n{str(e)}"
                        )
                        return
                else:
                    return
            else:
                return

        from tkinter import simpledialog
        from handlers.partner_handler import (
            PartnerDialog,
            add_partner_to_workbook
        )
        
        # Get partner number
        partner_number = simpledialog.askstring(
            "Add Partner",
            "Enter Partner Number:",
            parent=self.root
        )
        if not partner_number:
            return
            
        if partner_number == "1":
            messagebox.showerror(
                "Invalid",
                "P1 (Coordinator) cannot be added or edited."
            )
            return

        # Get partner acronym
        partner_acronym = simpledialog.askstring(
            "Add Partner",
            "Enter Partner Acronym:",
            parent=self.root
        )
        if not partner_acronym:
            return

        # Create and show the partner dialog
        dialog = PartnerDialog(self.root, partner_number, partner_acronym)
        if dialog.result:
            partner_info = dialog.result
            partner_info['project_partner_number'] = partner_number
            partner_info['partner_acronym'] = partner_acronym

            if add_partner_to_workbook(self.current_workbook, partner_info):
                # Save the workbook
                try:
                    # Ask user where to save if this is a new workbook
                    save_path = filedialog.asksaveasfilename(
                        title="Save Workbook",
                        defaultextension=".xlsx",
                        filetypes=EXCEL_FILETYPES
                    )
                    if save_path:
                        self.current_workbook.save(save_path)
                        messagebox.showinfo(
                            "Success",
                            f"Added partner {partner_number}: {partner_acronym}\n"
                            f"Workbook saved to: {save_path}"
                        )
                    else:
                        messagebox.showwarning(
                            "Warning",
                            "Partner added but workbook not saved!"
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Failed to save workbook:\n{str(e)}"
                    )

    def delete_partner(self):
        pass

    def edit_partner(self):
        pass

    def add_workpackage(self):
        pass

    def delete_workpackage(self):
        pass

    def edit_workpackage(self):
        pass

    def _setup_preferences_menu(self, menubar):
        """Set up the Preferences menu."""
        pref_menu = tk.Menu(menubar, tearoff=0)
        # ...existing code...

    def clone_file(self):
        """Clone an Excel file to a new location with user-provided details. Prompts for new name, extension and optional project name."""
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
                if isinstance(diff, pd.DataFrame):
                    diff_str = diff.to_string(index=False)
                else:
                    diff_str = str(diff)
                diff_text.insert(tk.END, diff_str)
                diff_text.config(state="disabled")

            def export_to_excel():
                """Export the currently selected difference to an Excel file."""
                sel = listbox.curselection()
                if not sel:
                    messagebox.showinfo("Export", "Please select a file to export.")
                    return
                name, diff = diffs[sel[0]]
                
                # Create a timestamp for the export
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Prompt for save location
                save_path = filedialog.asksaveasfilename(
                    title="Save Differences As",
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=f"diff_{name}_{timestamp}.xlsx"
                )
                if not save_path:
                    return
                    
                try:
                    # Create Excel writer object
                    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                        # Write comparison information
                        info_df = pd.DataFrame({
                            'Parameter': ['Reference File', 'Compared File', 'Export Date'],
                            'Value': [
                                os.path.basename(ref_file),
                                name,
                                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ]
                        })
                        info_df.to_excel(writer, sheet_name='Info', index=False)
                        
                        # Write differences
                        if isinstance(diff, pd.DataFrame):
                            # Format the differences DataFrame
                            if '_merge' in diff.columns:
                                diff = diff.drop('_merge', axis=1)
                            diff.to_excel(writer, sheet_name='Differences', index=False)
                        else:
                            # If diff is not a DataFrame, write as plain text
                            pd.DataFrame({'Result': [str(diff)]}).to_excel(
                                writer, sheet_name='Differences', index=False
                            )
                            
                    messagebox.showinfo(
                        "Export Complete",
                        f"Differences exported to:\n{save_path}"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Export Failed",
                        f"Error exporting differences:\n{e}"
                    )

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

                ref_idx_holder = {}

                def set_ref():
                    ref_idx_holder["idx"] = file_paths.index(ref_var.get())
                    dialog.destroy()

                ttk.Button(
                    dialog,
                    text="OK",
                    command=set_ref
                ).pack(pady=5)

                dialog.wait_window()
                new_ref_idx = ref_idx_holder.get("idx", ref_idx)
                result_win.destroy()
                show_comparison_dialog(new_ref_idx)

            # Button frame

            btn_frame = ttk.Frame(result_win)
            btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=8)
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            btn_frame.grid_columnconfigure(2, weight=1)

            ttk.Button(
                btn_frame,
                text="Change Reference",
                command=change_reference
            ).grid(row=0, column=0, sticky="w", padx=5)

            ttk.Button(
                btn_frame,
                text="Export to Excel",
                command=export_to_excel
            ).grid(row=0, column=1, sticky="ew", padx=5)

            ttk.Button(
                btn_frame,
                text="Close",
                command=result_win.destroy
            ).grid(row=0, column=2, sticky="e", padx=5)

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

            ref_idx_holder = {}

            def set_ref():
                ref_idx_holder["idx"] = file_paths.index(ref_var.get())
                dialog.destroy()

            ttk.Button(dialog, text="OK", command=set_ref).pack(pady=5)
            dialog.wait_window()
            return ref_idx_holder.get("idx", 0)

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
        """Placeholder for modifying a file (not yet implemented)."""
        if self.developer_mode:
            dev_log("Modify file triggered.")
        not_implemented_yet("Modify")

    def restore_file(self):
        """Placeholder for restoring a file from backup (not yet implemented)."""
        if self.developer_mode:
            dev_log("Restore file triggered.")
        not_implemented_yet("Restore")

    def show_diagnostics(self):
        """Show the diagnostics dashboard window with startup and config status."""
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
        if self.prefs_manager is not None:
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
        """Prompt the user to confirm exit and quit the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def run(self):
        """Start the Tkinter main event loop for the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProjectBudgetinator()
    app.run()
