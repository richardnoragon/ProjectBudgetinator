import tkinter as tk
from tkinter import messagebox
import json
import os
from pathlib import Path

class ProjectBudgetinator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ProjectBudgetinator Hub")
        self.setup_menu()
        self.check_first_run()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup")
        file_menu.add_separator()
        file_menu.add_command(label="Clone")
        file_menu.add_separator()
        file_menu.add_command(label="Compare")
        file_menu.add_separator()
        file_menu.add_command(label="Create from scratch")
        file_menu.add_command(label="Create from template")
        file_menu.add_separator()
        file_menu.add_command(label="Modify")
        file_menu.add_separator()
        file_menu.add_command(label="Restore")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)

        # Preferences Menu
        pref_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferences", menu=pref_menu)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

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
            "user.config.json": {"theme": "light", "welcome_screen": True, "startup_diagnostics": "verbose"},
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
