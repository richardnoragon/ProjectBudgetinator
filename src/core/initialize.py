"""
Application initialization and setup.
"""
import os
from pathlib import Path
import logging
from utils.config_utils import create_directory_structure, get_app_directory
from utils.dialog_utils import show_info
from core.diagnostics import get_diagnostic_summary
from core.preferences import PreferencesManager


def init_application():
    """Initialize the application environment."""
    # Set up logging first
    setup_logging()

    # Create directory structure and config files
    create_directory_structure()

    # Load preferences
    prefs_manager = PreferencesManager()
    current_config = prefs_manager.load_config()

    # Check if this is first run
    is_first_run = check_first_run()
    if is_first_run:
        show_first_run_message()

    # Show diagnostics if needed
    if (is_first_run or
            current_config.get("startup_diagnostic", "verbose") == "verbose"):
        show_diagnostics()

    return current_config


def setup_logging():
    """Set up application logging."""
    log_dir = os.path.join(get_app_directory(), "logs", "system")
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, "application.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("ProjectBudgetinator")
    return logger


def check_first_run():
    """Check if this is the first time running the application."""
    app_dir = os.path.join(str(Path.home()), "ProjectBudgetinator")
    return not os.path.exists(app_dir)


def show_first_run_message():
    """Show the welcome message for first-time users."""
    show_info(
        "Welcome",
        "Welcome to ProjectBudgetinator!\n\n"
        "This appears to be your first time running the program. "
        "The necessary directories and config files have been created."
    )


def show_diagnostics():
    """Show the diagnostic summary."""
    report = get_diagnostic_summary()

    if report:
        from tkinter import Tk, Toplevel, Label, Text, Button, Listbox
        from tkinter import END, BOTH, X, W

        diag_win = Toplevel()
        diag_win.title("Startup Diagnostics Dashboard")
        diag_win.geometry("400x370")
        diag_win.grab_set()

        # Category list
        cat_label = Label(
            diag_win,
            text="Select Diagnostic Category:",
            font=("Arial", 11, "bold")
        )
        cat_label.pack(pady=(10, 0))

        cat_listbox = Listbox(diag_win, height=7)
        for category in report.keys():
            cat_listbox.insert(END, category)
        cat_listbox.pack(fill=X, padx=10, pady=5)

        # Details display
        details_text = Text(diag_win, height=10, wrap="word", state="disabled")
        details_text.pack(fill=BOTH, expand=True, padx=10, pady=5)

        def show_details(event=None):
            """Show details for the selected category."""
            selection = cat_listbox.curselection()
            if selection:
                category = cat_listbox.get(selection[0])
                details_text.config(state="normal")
                details_text.delete("1.0", END)
                details_text.insert(END, report[category])
                details_text.config(state="disabled")

        cat_listbox.bind("<<ListboxSelect>>", show_details)
        cat_listbox.selection_set(0)
        show_details()

        Button(
            diag_win,
            text="Close",
            command=diag_win.destroy
        ).pack(pady=5)
