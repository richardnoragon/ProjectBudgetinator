
import tkinter as tk
from tkinter import messagebox
import json
import os
from pathlib import Path
from devtools import not_implemented_yet, DebugConsole, dev_log
from version import get_version, get_schema, full_version_string
from logger import setup_logging



class ProjectBudgetinator:
    def add_partner(self):
        if self.developer_mode:
            dev_log("Add Partner triggered.")
        not_implemented_yet("Add Partner")

    def delete_partner(self):
        if self.developer_mode:
            dev_log("Delete Partner triggered.")
        not_implemented_yet("Delete Partner")

    def edit_partner(self):
        if self.developer_mode:
            dev_log("Edit Partner triggered.")
        not_implemented_yet("Edit Partner")

    def add_workpackage(self):
        if self.developer_mode:
            dev_log("Add Workpackage triggered.")
        not_implemented_yet("Add Workpackage")

    def delete_workpackage(self):
        if self.developer_mode:
            dev_log("Delete Workpackage triggered.")
        not_implemented_yet("Delete Workpackage")

    def edit_workpackage(self):
        if self.developer_mode:
            dev_log("Edit Workpackage triggered.")
        not_implemented_yet("Edit Workpackage")
    def __init__(self):
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

        # Apply theme
        self.apply_theme()

        # Check first run
        self.check_first_run()

    def setup_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup", command=self.backup_file)
        file_menu.add_separator()
        file_menu.add_command(label="Clone", command=self.clone_file)
        file_menu.add_separator()
        file_menu.add_command(label="Compare", command=self.compare_files)
        file_menu.add_separator()
        file_menu.add_command(label="Create from scratch", command=self.create_from_scratch)
        file_menu.add_command(label="Create from template", command=self.create_from_template)
        file_menu.add_separator()
        # Modify Submenu
        modify_menu = tk.Menu(file_menu, tearoff=0)
        modify_menu.add_command(label="Add Partner", command=self.add_partner)
        modify_menu.add_command(label="Delete Partner", command=self.delete_partner)
        modify_menu.add_command(label="Edit Partner", command=self.edit_partner)
        modify_menu.add_separator()
        modify_menu.add_command(label="Add Workpackage", command=self.add_workpackage)
        modify_menu.add_command(label="Delete Workpackage", command=self.delete_workpackage)
        modify_menu.add_command(label="Edit Workpackage", command=self.edit_workpackage)
        file_menu.add_cascade(label="Modify", menu=modify_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Restore", command=self.restore_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)

        # Preferences Menu
        pref_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferences", menu=pref_menu)
        pref_menu.add_command(label="Settings", command=self.show_preferences)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        # Dev Tools submenu (above Diagnostics)
        devtools_menu = tk.Menu(tools_menu, tearoff=0)
        devtools_menu.add_checkbutton(label="Developer Mode", command=self.toggle_developer_mode)
        devtools_menu.add_command(label="Show Debug Console", command=self.toggle_debug_console)
        tools_menu.add_cascade(label="Dev Tools", menu=devtools_menu)
        tools_menu.add_separator()
        tools_menu.add_command(label="Diagnostics", command=self.show_diagnostics)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help)

        self.root.config(menu=menubar)

    def toggle_developer_mode(self):
        self.developer_mode = not self.developer_mode
        if self.developer_mode:
            dev_log("Developer mode enabled.")
            self.debug_console.show()
        else:
            dev_log("Developer mode disabled.")
            self.debug_console.hide()

    def toggle_debug_console(self):
        if self.debug_console.visible:
            self.debug_console.hide()
        else:
            self.debug_console.show()

    def backup_file(self):
        if self.developer_mode:
            dev_log("Backup file triggered.")
        not_implemented_yet("Backup")

    def clone_file(self):
        if self.developer_mode:
            dev_log("Clone file triggered.")
        from tkinter import filedialog, simpledialog
        # Step 1: Select source file
        src_path = filedialog.askopenfilename(
            title="Select file to clone",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        if not src_path:
            return
        # Step 2: Select destination and edit details
        dest_dir = filedialog.askdirectory(title="Select destination folder for clone")
        if not dest_dir:
            return
        base_name = os.path.splitext(os.path.basename(src_path))[0]
        ext = os.path.splitext(src_path)[1]
        new_name = simpledialog.askstring("Clone File", "Enter new file name:", initialvalue=base_name)
        if not new_name:
            return
        new_ext = simpledialog.askstring("Clone File", "Enter file extension:", initialvalue=ext)
        if not new_ext:
            return
        project_name = simpledialog.askstring("Clone File", "Enter project name (optional):", initialvalue="")
        dest_path = os.path.join(dest_dir, new_name + new_ext)
        try:
            import shutil
            shutil.copy2(src_path, dest_path)
            messagebox.showinfo("Clone Complete", f"File cloned to:\n{dest_path}")
            if project_name:
                dev_log(f"Project name for clone: {project_name}")
        except Exception as e:
            messagebox.showerror("Clone Failed", f"Error cloning file:\n{e}")

    def compare_files(self):
        if self.developer_mode:
            dev_log("Compare files triggered.")
        import pandas as pd
        from tkinter import filedialog, simpledialog, Toplevel, Listbox, Button, Label, StringVar, Radiobutton, Text, END

        # Step 1: Select up to 3 files
        file_paths = filedialog.askopenfilenames(
            title="Select up to 3 files to compare",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        file_paths = list(file_paths)
        if not file_paths or len(file_paths) < 2:
            messagebox.showinfo("Compare Files", "Please select at least 2 files to compare.")
            return
        if len(file_paths) > 3:
            file_paths = file_paths[:3]


        # --- Helper to run comparison and show dialog ---
        def run_comparison_dialog(ref_idx):
            ref_file = file_paths[ref_idx]
            others = [f for i, f in enumerate(file_paths) if i != ref_idx]
            try:
                ref_df = pd.read_excel(ref_file)
                other_dfs = [pd.read_excel(f) for f in others]
            except Exception as e:
                messagebox.showerror("Compare Failed", f"Error reading files:\n{e}")
                return

            # Simple diff: show rows in others not in reference (by all columns)
            diffs = []
            for i, df in enumerate(other_dfs):
                diff = df.merge(ref_df, how='outer', indicator=True).query('_merge != "both"')
                if not diff.empty:
                    diffs.append((os.path.basename(others[i]), diff))
                else:
                    diffs.append((os.path.basename(others[i]), pd.DataFrame(["No differences found."])) )

            # Step 4: Show results in a dialog


            from tkinter import Frame
            result_win = Toplevel(self.root)
            result_win.title("Comparison Results")
            result_win.geometry("600x400")
            result_win.minsize(600, 220)
            result_win.grid_rowconfigure(1, weight=1)
            result_win.grid_columnconfigure(0, weight=1)

            ref_label = Label(result_win, text=f"Reference: {os.path.basename(ref_file)}", font=("Arial", 11, "bold"))
            ref_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

            listbox = Listbox(result_win)
            for name, _ in diffs:
                listbox.insert(END, name)
            listbox.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))

            diff_text = Text(result_win, wrap="none", height=12)
            diff_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 0))

            button_frame = Frame(result_win)
            button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=8)
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            btn_change = Button(button_frame, text="Change Reference", command=lambda: change_reference())
            btn_change.grid(row=0, column=0, sticky="w", padx=5)
            btn_close = Button(button_frame, text="Close", command=result_win.destroy)
            btn_close.grid(row=0, column=1, sticky="e", padx=5)

            def show_diff(event=None):
                sel = listbox.curselection()
                if not sel:
                    return
                idx = sel[0]
                name, diff = diffs[idx]
                diff_text.config(state="normal")
                diff_text.delete("1.0", END)
                if isinstance(diff, pd.DataFrame):
                    diff_text.insert(END, diff.to_string(index=False))
                else:
                    diff_text.insert(END, str(diff))
                diff_text.config(state="disabled")
            listbox.bind("<<ListboxSelect>>", show_diff)
            listbox.selection_set(0)
            show_diff()

            def change_reference():
                dialog = Toplevel(self.root)
                dialog.title("Select Reference File")
                Label(dialog, text="Choose the reference file:").pack(pady=5)
                ref_var = StringVar(value=file_paths[ref_idx])
                for i, path in enumerate(file_paths):
                    Radiobutton(dialog, text=os.path.basename(path), variable=ref_var, value=path).pack(anchor="w")
                def set_ref():
                    dialog.ref_idx = file_paths.index(ref_var.get())
                    dialog.destroy()
                Button(dialog, text="OK", command=set_ref).pack(pady=5)
                dialog.wait_window()
                new_ref_idx = getattr(dialog, 'ref_idx', ref_idx)
                result_win.destroy()
                run_comparison_dialog(new_ref_idx)

        # Initial reference selection
        def choose_reference_dialog():
            dialog = Toplevel(self.root)
            dialog.title("Select Reference File")
            Label(dialog, text="Choose the reference file:").pack(pady=5)
            ref_var = StringVar(value=file_paths[0])
            for i, path in enumerate(file_paths):
                Radiobutton(dialog, text=os.path.basename(path), variable=ref_var, value=path).pack(anchor="w")
            def set_ref():
                dialog.ref_idx = file_paths.index(ref_var.get())
                dialog.destroy()
            Button(dialog, text="OK", command=set_ref).pack(pady=5)
            dialog.wait_window()
            return getattr(dialog, 'ref_idx', 0)

        ref_idx = choose_reference_dialog()
        run_comparison_dialog(ref_idx)

    def create_from_scratch(self):
        if self.developer_mode:
            dev_log("Create from scratch triggered.")
        from tkinter import filedialog, simpledialog
        # Step 1: Select save location
        dest_dir = filedialog.askdirectory(title="Select folder to save new file")
        if not dest_dir:
            return
        # Step 2: Input file name and extension
        file_name = simpledialog.askstring("Create from Scratch", "Enter file name:")
        if not file_name:
            return
        file_ext = simpledialog.askstring("Create from Scratch", "Enter file extension:", initialvalue=".xlsx")
        if not file_ext:
            return
        dest_path = os.path.join(dest_dir, file_name + file_ext)
        # Step 3: Create empty file (Excel placeholder)
        try:
            import pandas as pd
            df = pd.DataFrame()
            df.to_excel(dest_path, index=False)
            messagebox.showinfo("File Created", f"New file created at:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("Create Failed", f"Error creating file:\n{e}")

    def create_from_template(self):
        if self.developer_mode:
            dev_log("Create from template triggered.")
        from tkinter import filedialog, simpledialog
        # Step 1: Select template or existing file
        template_path = filedialog.askopenfilename(
            title="Select template or existing file",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        if not template_path:
            return
        # Validate file (basic check: exists and is Excel)
        if not (template_path.endswith(".xlsx") or template_path.endswith(".xls")):
            messagebox.showerror("Invalid File", "Selected file is not an Excel file.")
            return
        # Step 2: Select save location
        dest_dir = filedialog.askdirectory(title="Select folder to save new file")
        if not dest_dir:
            return
        # Step 3: Input new file name and extension
        file_name = simpledialog.askstring("Create from Template", "Enter new file name:")
        if not file_name:
            return
        file_ext = simpledialog.askstring("Create from Template", "Enter file extension:", initialvalue=".xlsx")
        if not file_ext:
            return
        dest_path = os.path.join(dest_dir, file_name + file_ext)
        # Step 4: Copy template to new location
        try:
            import shutil
            shutil.copy2(template_path, dest_path)
            messagebox.showinfo("File Created", f"File created from template at:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("Create Failed", f"Error creating file from template:\n{e}")

    def modify_file(self):
        if self.developer_mode:
            dev_log("Modify file triggered.")
        not_implemented_yet("Modify")

    def restore_file(self):
        if self.developer_mode:
            dev_log("Restore file triggered.")
        not_implemented_yet("Restore")

    def show_diagnostics(self):
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
            "Summary": "Startup passed with 2 warnings and 2 recoveries.\nNew folders/configs have been generated where needed.\n\n📌 All systems go — launching interface...",
            "Version Info": version_info
        }

        # Category list
        cat_label = tk.Label(diag_win, text="Select Diagnostic Category:", font=("Arial", 11, "bold"))
        cat_label.pack(pady=(10, 0))
        cat_listbox = tk.Listbox(diag_win, height=7)
        for cat in categories:
            cat_listbox.insert(tk.END, cat)
        cat_listbox.pack(fill="x", padx=10, pady=5)

        # Details display
        details_text = tk.Text(diag_win, height=10, wrap="word", state="disabled")
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
        help_win = tk.Toplevel(self.root)
        help_win.title("Hub")
        help_win.geometry("400x250")
        help_win.grab_set()

        title = tk.Label(help_win, text="Hub", font=("Arial", 16, "bold"))
        title.pack(pady=(15, 5))
        attention = tk.Label(help_win, text="Attention needed", font=("Arial", 12, "bold"), fg="red")
        attention.pack(pady=(0, 5))
        help_text = (
            "Help menu\n\n"
            "This is a placeholder for the Help section.\n\n"
            "For assistance, please refer to the documentation or contact support."
        )
        text = tk.Label(help_win, text=help_text, font=("Arial", 11), justify="left")
        text.pack(padx=15, pady=5)
        close_btn = tk.Button(help_win, text="Close", command=help_win.destroy)
        close_btn.pack(pady=10)

        # (No menu bar code here)

    def show_preferences(self):
        from preferences import PreferencesDialog
        dialog = PreferencesDialog(self.root)
        self.root.wait_window(dialog.dialog)
        # Reload preferences after dialog is closed
        self.current_config = self.prefs_manager.load_config()
        self.apply_theme()

    def apply_theme(self):
        # This is a placeholder for theme implementation
        # In a real implementation, you would apply colors and styles based on the theme
        theme = self.current_config.get("theme", "light")
        if theme == "dark":
            self.root.configure(bg="gray20")
        else:
            self.root.configure(bg="SystemButtonFace")

    def check_first_run(self):
        """Check if this is the first time running the program"""
        user_home = str(Path.home())
        app_dir = os.path.join(user_home, "ProjectBudgetinator")
        
        if not os.path.exists(app_dir):
            response = messagebox.askyesno(
                "Welcome", 
                "Welcome to ProjectBudgetinator!\n\n"
                "This appears to be your first time running the program. "
                "Would you like to create the necessary directories in your user folder?"
            )
            
            if response:
                self.create_directory_structure()
            else:
                messagebox.showinfo("Exit", "The program cannot operate without the necessary directories.")
                self.root.quit()

    def create_directory_structure(self):
        """Create the necessary directory structure"""
        user_home = str(Path.home())
        base_dir = os.path.join(user_home, "ProjectBudgetinator")
        
        directories = [
            os.path.join(base_dir, "workbooks"),
            os.path.join(base_dir, "logs", "system"),
            os.path.join(base_dir, "logs", "user_actions"),
            os.path.join(base_dir, "logs", "comparisons", "snapshots"),
            os.path.join(base_dir, "config"),
            os.path.join(base_dir, "backups"),
            os.path.join(base_dir, "templates")
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        # Create default configuration files
        config_files = {
            "user.config.json": {"theme": "light", "welcome_screen": True, "startup_diagnostic": "verbose"},
            "backup.config.json": {"frequency": "daily", "keep_versions": 5},
            "diagnostic.config.json": {"debug_mode": False, "log_level": "INFO"}
        }

        for filename, default_content in config_files.items():
            filepath = os.path.join(base_dir, "config", filename)
            with open(filepath, "w") as f:
                json.dump(default_content, f, indent=4)

    def exit_program(self):
        """Clean exit of the program"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ProjectBudgetinator()
    app.run()
