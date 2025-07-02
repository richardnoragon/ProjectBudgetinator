"""
Project menu handlers and related functions.
"""
import tkinter as tk
from tkinter import filedialog
from ..gui.dialogs import ProjectSettingsDialog
from ..handlers.file_handler import new_file, open_file, save_file
from ..handlers.partner_handler import add_partner_to_workbook, PartnerDialog
from ..handlers.workpackage_handler import (
    add_workpackage_to_workbook,
    WorkpackageDialog
)
from ..utils.dialog_utils import get_input, show_error, show_info


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
        """Handle Open File action."""
        workbook, filepath = open_file()
        if workbook and filepath:
            self.current_workbook = workbook
            self.current_filepath = filepath
            self.update_status(f"Opened: {filepath}")

    def on_save_file(self):
        """Handle Save File action."""
        if not self.current_workbook:
            return

        if not self.current_filepath:
            self.on_save_as()
            return

        filepath = save_file(self.current_workbook, self.current_filepath)
        if filepath:
            self.current_filepath = filepath
            self.update_status(f"Saved: {filepath}")

    def on_save_as(self):
        """Handle Save As action."""
        if not self.current_workbook:
            return

        filepath = save_file(self.current_workbook)
        if filepath:
            self.current_filepath = filepath
            self.update_status(f"Saved as: {filepath}")

    def on_add_partner(self):
        """Handle Add Partner action."""
        if not self.current_workbook:
            show_error("Error", "No workbook is currently open.")
            return

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

            if add_partner_to_workbook(self.current_workbook, partner_info):
                self.update_status(
                    f"Added partner {partner_number}: {partner_acronym}"
                )

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
