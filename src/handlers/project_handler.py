"""
Project menu handlers and related functions.
"""
import tkinter as tk
from tkinter import filedialog
from gui.dialogs import ProjectSettingsDialog
from handlers.file_handler import new_file, open_file, save_file
from handlers.add_partner_handler import (
    add_partner_to_workbook, 
    add_partner_with_progress,
    PartnerDialog
)
from handlers.add_workpackage_handler import (
    add_workpackage_to_workbook,
    WorkpackageDialog
)
from utils.dialog_utils import get_input, show_error, show_info
from logger import get_structured_logger, LogContext
from gui.batch_operations import show_batch_operations_dialog


logger = get_structured_logger("handlers.project")


class ProjectMenuHandler:
    """Handler class for project-related menu actions."""

    def __init__(self, root, status_bar=None):
        """Initialize the project menu handler."""
        self.root = root
        self.status_bar = status_bar
        self.current_workbook = None
        self.current_filepath = None

    def update_status(self, message):
        """Update the status bar message."""
        if self.status_bar:
            self.status_bar.config(text=message)

    def on_new_file(self):
        """Handle New File action."""
        self.current_workbook, self.current_filepath = new_file()
        self.update_status("Created new workbook")

    def on_open_file(self):
        """Handle Open File action with progress feedback."""
        with LogContext("open_file_action"):
            logger.info("User initiated file open operation")
            
            # Use progress-enabled file open
            workbook, filepath = open_file(parent_window=self.root)
            if workbook and filepath:
                self.current_workbook = workbook
                self.current_filepath = filepath
                self.update_status(f"Opened: {filepath}")
                logger.info("File opened successfully", filepath=filepath)

    def on_save_file(self):
        """Handle Save File action with progress feedback."""
        if not self.current_workbook:
            show_error("Error", "No workbook is currently open.")
            return

        with LogContext("save_file_action"):
            logger.info("User initiated file save operation")
            
            if not self.current_filepath:
                self.on_save_as()
                return

            # Use progress-enabled file save
            filepath = save_file(
                self.current_workbook, 
                self.current_filepath,
                parent_window=self.root
            )
            if filepath:
                self.current_filepath = filepath
                self.update_status(f"Saved: {filepath}")
                logger.info("File saved successfully", filepath=filepath)

    def on_save_as(self):
        """Handle Save As action with progress feedback."""
        if not self.current_workbook:
            show_error("Error", "No workbook is currently open.")
            return

        with LogContext("save_as_action"):
            logger.info("User initiated save as operation")
            
            # Use progress-enabled file save
            filepath = save_file(self.current_workbook, parent_window=self.root)
            if filepath:
                self.current_filepath = filepath
                self.update_status(f"Saved as: {filepath}")
                logger.info("File saved as successfully", filepath=filepath)

    def on_add_partner(self):
        """Handle Add Partner action with progress feedback."""
        if not self.current_workbook:
            show_error("Error", "No workbook is currently open.")
            return

        with LogContext("add_partner_action"):
            logger.info("User initiated add partner operation")
            
            partner_number = get_input(
                "Add Partner",
                "Enter Partner Number:",
                initial_value=""
            )
            if not partner_number:
                return

            if partner_number == "1":
                show_error(
                    "Invalid",
                    "P1 (Coordinator) cannot be added or edited."
                )
                return

            partner_acronym = get_input(
                "Add Partner",
                "Enter Partner Acronym:",
                initial_value=""
            )
            if not partner_acronym:
                return

            dialog = PartnerDialog(self.root, partner_number, partner_acronym)
            if dialog.result:
                partner_info = dialog.result
                partner_info['project_partner_number'] = partner_number
                partner_info['partner_acronym'] = partner_acronym

                # Use progress-enabled partner addition
                if add_partner_with_progress(
                    self.root, 
                    self.current_workbook, 
                    partner_info
                ):
                    self.update_status(
                        f"Adding partner {partner_number}: {partner_acronym}..."
                    )
                    logger.info("Partner addition initiated",
                               partner_number=partner_number,
                               partner_acronym=partner_acronym)

    def on_add_workpackage(self):
        """Handle Add Workpackage action."""
        if not self.current_workbook:
            show_error("Error", "No workbook is currently open.")
            return

        dialog = WorkpackageDialog(self.root)
        if dialog.result:
            if add_workpackage_to_workbook(self.current_workbook, dialog.result):
                self.update_status(
                    f"Added workpackage: {dialog.result['workpackage_number']}"
                )

    def on_project_settings(self):
        """Handle Project Settings action."""
        dialog = ProjectSettingsDialog(self.root)
        if dialog.result:
            # TODO: Apply project settings
            pass

    def on_batch_operations(self):
        """Handle Batch Operations action."""
        with LogContext("batch_operations_action"):
            logger.info("User opened batch operations dialog")
            
            result = show_batch_operations_dialog(self.root)
            if result:
                logger.info("Batch operations completed",
                           total_operations=result.total_operations,
                           completed=result.completed,
                           failed=result.failed,
                           success_rate=result.success_rate)
                
                self.update_status(
                    f"Batch processing completed: {result.completed}/{result.total_operations} files"
                )
