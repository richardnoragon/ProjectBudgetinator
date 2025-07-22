"""
Partner editing functions for working with Excel workbooks.
"""
import tkinter as tk
from tkinter import StringVar, Label, Entry, Button, Frame, messagebox

# Local imports
from utils.error_handler import ExceptionHandler
from utils.security_validator import SecurityValidator, InputSanitizer
from handlers.base_handler import BaseHandler, ValidationResult, OperationResult
from logger import get_structured_logger, LogContext

# Create exception handler instance
exception_handler = ExceptionHandler()

# Create structured logger for this module
logger = get_structured_logger("handlers.edit_partner")


def read_partner_data_from_worksheet(worksheet):
    """
    Read partner data from Excel worksheet using the same cell mappings as add_partner_handler.
    
    Args:
        worksheet: openpyxl worksheet object
        
    Returns:
        dict: Dictionary containing all partner data from the worksheet
    """
    partner_data = {}
    
    try:
        # Basic partner information (same as add_partner_handler lines 614-626)
        basic_fields = [
            ('project_partner_number', 'D2'),
            ('partner_acronym', 'D3'),
            ('partner_identification_code', 'D4'),
            ('name_of_beneficiary', 'D5'),
            ('country', 'D6'),
            ('role', 'D7')
        ]
        
        for field_key, cell_ref in basic_fields:
            cell_value = worksheet[cell_ref].value
            partner_data[field_key] = str(cell_value or '')
            logger.debug(f"Read {field_key} from cell {cell_ref}: '{partner_data[field_key]}'")
        
        # WP values (same as add_partner_handler lines 630-639)
        wp_fields = {
            'wp1': 'C18', 'wp2': 'D18', 'wp3': 'E18', 'wp4': 'F18',
            'wp5': 'G18', 'wp6': 'H18', 'wp7': 'I18', 'wp8': 'J18',
            'wp9': 'K18', 'wp10': 'L18', 'wp11': 'M18', 'wp12': 'N18',
            'wp13': 'O18', 'wp14': 'P18', 'wp15': 'Q18'
        }
        for wp_key, cell_ref in wp_fields.items():
            cell_value = worksheet[cell_ref].value
            if cell_value is not None:
                try:
                    partner_data[wp_key] = float(cell_value)
                except (ValueError, TypeError):
                    partner_data[wp_key] = 0.0
            else:
                partner_data[wp_key] = 0.0
            logger.debug(f"Read {wp_key} from cell {cell_ref}: {partner_data[wp_key]}")
        
        # Subcontractor information (same as add_partner_handler lines 641-658)
        subcontractor_fields = [
            ('name_subcontractor_1', 'D22'),
            ('sum_subcontractor_1', 'F22'),
            ('explanation_subcontractor_1', 'G22'),
            ('name_subcontractor_2', 'D23'),
            ('sum_subcontractor_2', 'F23'),
            ('explanation_subcontractor_2', 'G23')
        ]
        
        for field_key, cell_ref in subcontractor_fields:
            cell_value = worksheet[cell_ref].value
            partner_data[field_key] = str(cell_value or '')
            logger.debug(f"Read {field_key} from cell {cell_ref}: '{partner_data[field_key]}'")
        
        # Financial information (same as add_partner_handler lines 661-677)
        financial_fields = [
            ('sum_travel', 'F28'),
            ('sum_equipment', 'F29'),
            ('sum_other', 'F30'),
            ('sum_financial_support', 'F35'),
            ('sum_internal_goods', 'F36'),
            ('sum_income_generated', 'F42'),
            ('sum_financial_contributions', 'F43'),
            ('sum_own_resources', 'F44')
        ]
        for field_key, value_cell in financial_fields:
            cell_value = worksheet[value_cell].value
            if cell_value is not None:
                partner_data[field_key] = str(cell_value)
            else:
                partner_data[field_key] = ''
            logger.debug(f"Read {field_key} from cell {value_cell}: '{partner_data[field_key]}'")
        
        # Explanation fields (same as add_partner_handler lines 680-691)
        explanation_fields = [
            ('explanation_travel', 'G28'),
            ('explanation_equipment', 'G29'),
            ('explanation_other', 'G30'),
            ('explanation_financial_support', 'G35'),
            ('explanation_internal_goods', 'G36'),
            ('explanation_income_generated', 'G42'),
            ('explanation_financial_contributions', 'G43'),
            ('explanation_own_resources', 'G44')
        ]
        for field_key, value_cell in explanation_fields:
            cell_value = worksheet[value_cell].value
            partner_data[field_key] = str(cell_value or '')
            logger.debug(f"Read {field_key} from cell {value_cell}: '{partner_data[field_key]}'")
        
        logger.info("Successfully read partner data from worksheet",
                   partner_number=partner_data.get('project_partner_number'),
                   partner_acronym=partner_data.get('partner_acronym'),
                   field_count=len(partner_data))
        
        # Special debug log for financial support since that was the original question
        logger.info("Financial support data origin",
                   sum_financial_support_cell="F35",
                   sum_financial_support_value=partner_data.get('sum_financial_support', ''),
                   explanation_financial_support_cell="G35",
                   explanation_financial_support_value=partner_data.get('explanation_financial_support', ''))
        
    except Exception as e:
        logger.error("Error reading partner data from worksheet", error=str(e))
        # Return empty data on error
        partner_data = {}
    
    return partner_data


def write_partner_data_to_worksheet(worksheet, partner_data):
    """
    Write partner data to Excel worksheet using the same cell mappings as add_partner_handler.
    
    Args:
        worksheet: openpyxl worksheet object
        partner_data: Dictionary containing partner data to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Basic partner information (same as add_partner_handler lines 614-626)
        basic_fields = [
            ('project_partner_number', 'D2'),
            ('partner_acronym', 'D3'),
            ('partner_identification_code', 'D4'),
            ('name_of_beneficiary', 'D5'),
            ('country', 'D6'),
            ('role', 'D7')
        ]
        
        for field_key, cell_ref in basic_fields:
            value = partner_data.get(field_key, '')
            worksheet[cell_ref] = value
            logger.debug(f"Wrote {field_key} to cell {cell_ref}: '{value}'")
        
        # WP values (same as add_partner_handler lines 630-639)
        wp_fields = {
            'wp1': 'C18', 'wp2': 'D18', 'wp3': 'E18', 'wp4': 'F18',
            'wp5': 'G18', 'wp6': 'H18', 'wp7': 'I18', 'wp8': 'J18',
            'wp9': 'K18', 'wp10': 'L18', 'wp11': 'M18', 'wp12': 'N18',
            'wp13': 'O18', 'wp14': 'P18', 'wp15': 'Q18'
        }
        for wp_key, cell_ref in wp_fields.items():
            value = partner_data.get(wp_key, 0)
            if isinstance(value, (int, float)):
                worksheet[cell_ref] = float(value)
                worksheet[cell_ref].number_format = '#,##0.00'
            else:
                try:
                    worksheet[cell_ref] = float(value) if value else 0.0
                    worksheet[cell_ref].number_format = '#,##0.00'
                except (ValueError, TypeError):
                    worksheet[cell_ref] = 0.0
            logger.debug(f"Wrote {wp_key} to cell {cell_ref}: {worksheet[cell_ref].value}")
        
        # Subcontractor information (same as add_partner_handler lines 641-658)
        subcontractor_fields = [
            ('name_subcontractor_1', 'D22'),
            ('sum_subcontractor_1', 'F22'),
            ('explanation_subcontractor_1', 'G22'),
            ('name_subcontractor_2', 'D23'),
            ('sum_subcontractor_2', 'F23'),
            ('explanation_subcontractor_2', 'G23')
        ]
        
        for field_key, cell_ref in subcontractor_fields:
            value = partner_data.get(field_key, '')
            worksheet[cell_ref] = value
            logger.debug(f"Wrote {field_key} to cell {cell_ref}: '{value}'")
        
        # Financial information (same as add_partner_handler lines 661-677)
        financial_fields = [
            ('sum_travel', 'F28'),
            ('sum_equipment', 'F29'),
            ('sum_other', 'F30'),
            ('sum_financial_support', 'F35'),
            ('sum_internal_goods', 'F36'),
            ('sum_income_generated', 'F42'),
            ('sum_financial_contributions', 'F43'),
            ('sum_own_resources', 'F44')
        ]
        for field_key, value_cell in financial_fields:
            value = partner_data.get(field_key, '')
            if value and isinstance(value, (int, float)):
                worksheet[value_cell] = float(value)
                worksheet[value_cell].number_format = '#,##0.00'
            elif value:
                try:
                    worksheet[value_cell] = float(value)
                    worksheet[value_cell].number_format = '#,##0.00'
                except (ValueError, TypeError):
                    worksheet[value_cell] = str(value)
            else:
                worksheet[value_cell] = ''
            logger.debug(f"Wrote {field_key} to cell {value_cell}: '{worksheet[value_cell].value}'")
        
        # Explanation fields (same as add_partner_handler lines 680-691)
        explanation_fields = [
            ('explanation_travel', 'G28'),
            ('explanation_equipment', 'G29'),
            ('explanation_other', 'G30'),
            ('explanation_financial_support', 'G35'),
            ('explanation_internal_goods', 'G36'),
            ('explanation_income_generated', 'G42'),
            ('explanation_financial_contributions', 'G43'),
            ('explanation_own_resources', 'G44')
        ]
        for field_key, value_cell in explanation_fields:
            value = partner_data.get(field_key, '')
            worksheet[value_cell] = value
            logger.debug(f"Wrote {field_key} to cell {value_cell}: '{value}'")
        
        logger.info("Successfully wrote partner data to worksheet",
                   partner_number=partner_data.get('project_partner_number'),
                   partner_acronym=partner_data.get('partner_acronym'),
                   field_count=len(partner_data))
        
        # Special debug log for financial support since that was the original question
        logger.info("Financial support data written",
                   sum_financial_support_cell="F35",
                   sum_financial_support_value=partner_data.get('sum_financial_support', ''),
                   explanation_financial_support_cell="G35",
                   explanation_financial_support_value=partner_data.get('explanation_financial_support', ''))
        
        return True
        
    except Exception as e:
        logger.error("Error writing partner data to worksheet", error=str(e))
        return False


class EditPartnerDialog(tk.Toplevel):
    def __init__(self, parent, partner_number, partner_acronym, worksheet=None, initial_values=None):
        super().__init__(parent)
        self.title("Edit Partner Details")
        self.resizable(False, False)
        self.result = None
        
        # Store the values
        self.partner_number = partner_number
        self.partner_acronym = partner_acronym
        self.worksheet = worksheet
        self.initial_values = initial_values or {}
        
        # If worksheet is provided, read current data from it
        if self.worksheet:
            self.initial_values = read_partner_data_from_worksheet(self.worksheet)
            logger.info("Read partner data from worksheet",
                       partner_number=partner_number,
                       partner_acronym=partner_acronym,
                       data_fields=len(self.initial_values))
        
        # Create variables dictionary
        self.vars = {}
        
        # Log dialog initialization
        with LogContext("edit_partner_dialog_init",
                        partner_number=partner_number,
                        partner_acronym=partner_acronym):
            logger.info("Initializing edit partner dialog",
                        partner_number=partner_number,
                        partner_acronym=partner_acronym,
                        initial_values_count=len(self.initial_values))
            
            # Create the form using the same layout as PartnerDialog
            self._create_widgets()
            self._load_initial_values()
        
        # Make dialog modal
        self.grab_set()
        self.wait_window()

    def _create_widgets(self):
        # Display Partner Number and Acronym (readonly) - matching PartnerDialog
        Label(self, text="Partner Number and Acronym:").grid(
            row=0, column=0, sticky="w", padx=8, pady=2)
        value = f"{self.partner_number}, {self.partner_acronym}"
        self.vars['partner_number_acronym'] = StringVar(value=value)
        entry = Entry(
            self,
            textvariable=self.vars['partner_number_acronym'],
            width=32,
            state='readonly'
        )
        entry.grid(row=0, column=1, padx=8, pady=2, columnspan=3)

        # Define field groups exactly like PartnerDialog
        fields_col1 = [
            ("partner_identification_code", "Partner ID Code"),
            ("name_of_beneficiary", "Name of Beneficiary"),
            ("country", "Country"),
            ("role", "Role")
        ]
        fields_col2 = [
            ("wp1", "WP1"),
            ("wp2", "WP2"),
            ("wp3", "WP3"),
            ("wp4", "WP4"),
            ("wp5", "WP5"),
            ("wp6", "WP6"),
            ("wp7", "WP7"),
            ("wp8", "WP8"),
            ("wp9", "WP9"),
            ("wp10", "WP10"),
            ("wp11", "WP11"),
            ("wp12", "WP12"),
            ("wp13", "WP13"),
            ("wp14", "WP14"),
            ("wp15", "WP15")
        ]
        fields_col3 = [
            ("name_subcontractor_1", "Name Subcontrator 1"),
            ("sum_subcontractor_1", "Sum Subcontractor 1"),
            ("explanation_subcontractor_1", "Explanation of Subcontractor 1"),
            ("name_subcontractor_2", "Name Subcontrator 2"),
            ("sum_subcontractor_2", "Sum Subcontractor 2"),
            ("explanation_subcontractor_2", "Explanation of Subcontractor 2"),
            ("sum_travel", "Travel and substistence /€"),
            ("explanation_travel", "Travel and substistence"),
            ("sum_equipment", "Equipment /€"),
            ("explanation_equipment", "Equipment"),
            ("sum_other", "Other goods, works and services /€"),
            ("explanation_other", "Other goods, works and services"),
            ("sum_financial_support", "Financial support to third parties /€"),
            ("explanation_financial_support",
             "Financial support to third parties"
             ),
            ("sum_internal_goods",
             "Internally invoiced goods & services "
             "(Unit costs- usual accounting practices) /€"
             ),
            ("explanation_internal_goods",
             "Internally invoiced goods & services "
             "(Unit costs- usual accounting practices)"
             ),
            ("sum_income_generated", "Income generated by the action /€"),
            ("explanation_income_generated",
             "Income generated by the action"
             ),
            ("sum_financial_contributions", "Financial contributions /€"),
            ("explanation_financial_contributions",
             "Financial contributions"
             ),
            ("sum_own_resources", "Own resources /€"),
            ("explanation_own_resources", "Own resources")
        ]
        row0 = 1

        # First column (ends with Role) - same as PartnerDialog
        for i, (key, label) in enumerate(fields_col1):
            Label(
                self, text=f"{label}:"
            ).grid(
                row=i + row0 + 1, column=0, sticky="w", padx=8, pady=2
            )
            var = StringVar()
            entry = Entry(self, textvariable=var, width=32)
            entry.grid(row=i + row0 + 1, column=1, padx=8, pady=2)
            self.vars[key] = var

        # Second column (WP1 to WP15) - same as PartnerDialog
        for i, (key, label) in enumerate(fields_col2):
            Label(
                self, text=f"{label}:"
            ).grid(
                row=i, column=2, sticky="w", padx=8, pady=2
            )
            var = StringVar()
            entry = Entry(self, textvariable=var, width=12)
            entry.grid(row=i, column=3, padx=8, pady=2)
            self.vars[key] = var

        # Third column (rest) - same as PartnerDialog
        for i, (key, label) in enumerate(fields_col3):
            Label(
                self, text=f"{label}:"
            ).grid(
                row=i, column=4, sticky="w", padx=8, pady=2
            )
            var = StringVar()
            entry = Entry(self, textvariable=var, width=24)
            entry.grid(row=i, column=5, padx=8, pady=2)
            self.vars[key] = var

        # Place buttons below the last row - same as PartnerDialog
        row0_offset = row0 + 1
        max_rows = max(
            len(fields_col1) + row0_offset,
            len(fields_col2),
            len(fields_col3)
        )
        btn_frame = Frame(self)
        btn_frame.grid(row=max_rows, column=0, columnspan=6, pady=8)
        
        save_btn = Button(btn_frame, text="Save", command=self._on_save)
        save_btn.pack(side="left", padx=8)
        
        cancel_btn = Button(btn_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side="left", padx=8)
        
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _load_initial_values(self):
        """Load the initial values into the form fields."""
        for key, value in self.initial_values.items():
            if key in self.vars:
                self.vars[key].set(str(value) if value is not None else '')

    @exception_handler.handle_exceptions(
        show_dialog=True, log_error=True, return_value=None
    )
    def _on_save(self):
        """Save the form data with validation and sanitization."""
        # Sanitize and validate all input values
        wp_values = {}
        validation_errors = []

        # Validate WP values with input sanitization
        for key, var in self.vars.items():
            if key.startswith('wp'):
                raw_value = var.get().strip()
                # Sanitize the input first
                sanitized_value = InputSanitizer.sanitize_string(raw_value, max_length=20)
                
                if sanitized_value:
                    # Validate as numeric
                    numeric_value = InputSanitizer.sanitize_numeric_input(sanitized_value)
                    if numeric_value is not None:
                        wp_values[key] = float(numeric_value)
                    else:
                        validation_errors.append(f"{key}: Invalid numeric value '{sanitized_value}'")
                        wp_values[key] = 0.0
                else:
                    wp_values[key] = 0.0

        # Get partner number and acronym from the readonly field
        partner_field = self.vars['partner_number_acronym'].get()
        partner_parts = [x.strip() for x in partner_field.split(',', 1)]
        if len(partner_parts) != 2:
            validation_errors.append("Invalid partner number/acronym format")
            return
        
        partner_number, partner_acronym = partner_parts
        
        # Sanitize partner information
        partner_number = InputSanitizer.sanitize_string(partner_number, max_length=10)
        partner_acronym = InputSanitizer.sanitize_string(partner_acronym, max_length=50)

        # Sanitize all text fields
        v = self.vars  # Shorter alias for vars
        sanitized_data = {}
        
        # Basic information fields with length limits
        text_fields = {
            'partner_identification_code': 50,
            'name_of_beneficiary': 200,
            'country': 100,
            'role': 100,
            'name_subcontractor_1': 200,
            'explanation_subcontractor_1': 500,
            'name_subcontractor_2': 200,
            'explanation_subcontractor_2': 500,
            'explanation_travel': 500,
            'explanation_equipment': 500,
            'explanation_other': 500,
            'explanation_financial_support': 500,
            'explanation_internal_goods': 500,
            'explanation_income_generated': 500,
            'explanation_financial_contributions': 500,
            'explanation_own_resources': 500
        }
        
        for field, max_length in text_fields.items():
            if field in v:
                raw_value = v[field].get()
                sanitized_data[field] = InputSanitizer.sanitize_string(raw_value, max_length=max_length)
        
        # Sanitize and validate financial fields
        financial_fields = [
            'sum_subcontractor_1', 'sum_subcontractor_2', 'sum_travel',
            'sum_equipment', 'sum_other', 'sum_financial_support',
            'sum_internal_goods', 'sum_income_generated',
            'sum_financial_contributions', 'sum_own_resources'
        ]
        
        for field in financial_fields:
            if field in v:
                raw_value = v[field].get().strip()
                sanitized_value = InputSanitizer.sanitize_string(raw_value, max_length=20)
                
                if sanitized_value:
                    numeric_value = InputSanitizer.sanitize_numeric_input(sanitized_value)
                    if numeric_value is not None:
                        sanitized_data[field] = str(numeric_value)
                    else:
                        validation_errors.append(f"{field}: Invalid numeric value '{sanitized_value}'")
                        sanitized_data[field] = ''
                else:
                    sanitized_data[field] = ''

        # Show validation errors if any
        if validation_errors:
            error_msg = "Validation errors found:\n\n" + "\n".join(validation_errors)
            error_msg += "\n\nPlease correct these errors and try again."
            messagebox.showerror("Validation Error", error_msg)
            return

        # Create the result dictionary with sanitized values
        self.result = {
            'project_partner_number': partner_number,
            'partner_acronym': partner_acronym,
        }
        
        # Add all sanitized data
        self.result.update(sanitized_data)
        
        # Add all WP values
        self.result.update(wp_values)

        # If worksheet is provided, write data directly to it
        if self.worksheet:
            success = write_partner_data_to_worksheet(self.worksheet, self.result)
            if success:
                logger.info("Partner data written to worksheet successfully",
                           partner_number=partner_number,
                           partner_acronym=partner_acronym,
                           field_count=len(self.result))
                messagebox.showinfo("Success", "Partner data updated successfully!")
            else:
                logger.error("Failed to write partner data to worksheet")
                messagebox.showerror("Error", "Failed to update partner data in worksheet.")
                return
        else:
            logger.info("Partner data validated and sanitized successfully",
                       partner_number=partner_number,
                       partner_acronym=partner_acronym,
                       field_count=len(self.result))

        self.destroy()

    def _on_cancel(self):
        """Cancel the edit and close the dialog."""
        logger.info("Edit partner dialog cancelled",
                    partner_number=self.partner_number,
                    partner_acronym=self.partner_acronym)
        self.result = None
        self.destroy()


def edit_partner_from_worksheet(parent, workbook, sheet_name):
    """
    Open edit partner dialog with data loaded from the specified worksheet.
    
    Args:
        parent: Parent window for the dialog
        workbook: Excel workbook object
        sheet_name: Name of the partner worksheet (e.g., "P2 ACME")
        
    Returns:
        dict or None: Result data if saved, None if cancelled
    """
    try:
        # Get the worksheet
        if sheet_name not in workbook.sheetnames:
            messagebox.showerror("Error", f"Worksheet '{sheet_name}' not found.")
            return None
        
        worksheet = workbook[sheet_name]
        
        # Extract partner number and acronym from sheet name
        # Expected format: "P{number} {acronym}"
        if not sheet_name.startswith('P'):
            messagebox.showerror("Error", f"Invalid partner sheet name format: '{sheet_name}'")
            return None
        
        parts = sheet_name[1:].split(' ', 1)
        if len(parts) < 2:
            messagebox.showerror("Error", f"Invalid partner sheet name format: '{sheet_name}'")
            return None
        
        partner_number = parts[0]
        partner_acronym = parts[1]
        
        # Open the edit dialog with the worksheet
        dialog = EditPartnerDialog(
            parent=parent,
            partner_number=partner_number,
            partner_acronym=partner_acronym,
            worksheet=worksheet
        )
        
        return dialog.result
        
    except Exception as e:
        logger.exception("Error opening edit partner dialog from worksheet")
        messagebox.showerror("Error", f"Failed to open edit dialog: {str(e)}")
        return None
