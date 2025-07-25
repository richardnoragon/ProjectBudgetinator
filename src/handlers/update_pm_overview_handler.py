"""
PM Overview update handler for ProjectBudgetinator.

This module provides functionality to update the PM Overview worksheet
with formulas from partner worksheets after partner add/edit operations.
"""

import datetime
import tkinter as tk
import re
from typing import Dict, Any, List, Optional, Tuple, Union, TYPE_CHECKING

# Conditional imports for type hints
if TYPE_CHECKING:
    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet
else:
    # Runtime fallbacks when openpyxl is not available
    try:
        from openpyxl import Workbook
        from openpyxl.worksheet.worksheet import Worksheet
    except ImportError:
        Workbook = None
        Worksheet = None

# Local imports
from handlers.base_handler import BaseHandler, ValidationResult, OperationResult
from utils.error_handler import ExceptionHandler
from utils.security_validator import SecurityValidator, InputSanitizer
from logger import get_structured_logger, LogContext
from gui.progress_dialog import ProgressContext, show_progress_for_operation

# Create exception handler instance
exception_handler = ExceptionHandler()

# Create structured logger for this module
logger = get_structured_logger("handlers.update_pm_overview")

# PM Overview cell mappings configuration
PM_OVERVIEW_CELL_MAPPINGS = {
    # Source cells from partner worksheet -> Target column in PM Overview
    'C18': 'C',   # WP1
    'D18': 'D',   # WP2
    'E18': 'E',   # WP3
    'F18': 'F',   # WP4
    'G18': 'G',   # WP5
    'H18': 'H',   # WP6
    'I18': 'I',   # WP7
    'J18': 'J',   # WP8
    'K18': 'K',   # WP9
    'L18': 'L',   # WP10
    'M18': 'M',   # WP11
    'N18': 'N',   # WP12
    'O18': 'O',   # WP13
    'P18': 'P',   # WP14
    'Q18': 'Q',   # WP15
}

# Debug configuration
DEBUG_ENABLED = True
DEBUG_DETAILED = True


def get_pm_overview_row(partner_number: int) -> int:
    """
    Calculate PM Overview row number from partner number.
    
    Args:
        partner_number: Partner number (2, 3, 4, etc.)
        
    Returns:
        int: Row number in PM Overview (6, 7, 8, etc.)
    """
    return partner_number + 4  # P2->Row6, P3->Row7, etc.


def get_partner_number_from_sheet_name(sheet_name: str) -> Optional[int]:
    """
    Extract partner number from sheet name.
    
    Args:
        sheet_name: Sheet name like "P2-ACME" or "P3-University"
        
    Returns:
        Optional[int]: Partner number or None if invalid
    """
    if not sheet_name.startswith('P'):
        return None
    
    try:
        # Extract the part after 'P' and before the first hyphen
        parts = sheet_name[1:].split('-', 1)
        if parts and parts[0].isdigit():
            partner_num = int(parts[0])
            # Only accept partners 2-20
            if 2 <= partner_num <= 20:
                return partner_num
    except (ValueError, IndexError):
        pass
    
    return None


def adjust_formula_references(formula: str, source_row: int, target_row: int,
                              source_sheet: str, target_sheet: str) -> str:
    """
    Adjust cell references in a formula when copying from source to target location.
    
    Args:
        formula: Original formula string
        source_row: Source row number
        target_row: Target row number
        source_sheet: Source worksheet name
        target_sheet: Target worksheet name
        
    Returns:
        str: Adjusted formula string
    """
    if not formula or not formula.startswith('='):
        return formula
    
    # Pattern to match cell references (e.g., A1, $A$1, A$1, $A1)
    cell_pattern = r'(\$?)([A-Z]+)(\$?)(\d+)'
    
    def replace_cell_ref(match):
        col_abs, col, row_abs, row = match.groups()
        row_num = int(row)
        
        # If row is not absolute, adjust it based on the row difference
        if not row_abs:
            row_offset = target_row - source_row
            new_row = row_num + row_offset
            return f"{col_abs}{col}{row_abs}{new_row}"
        else:
            # Keep absolute references unchanged
            return match.group(0)
    
    # Apply the replacement
    adjusted_formula = re.sub(cell_pattern, replace_cell_ref, formula)
    
    return adjusted_formula


class PMOverviewDebugWindow:
    """Debug window for showing PM Overview update details."""
    
    def __init__(self, parent_window: Optional[tk.Widget] = None):
        self.parent = parent_window
        self.debug_window = None
        
    def show_debug_info(self, title: str, debug_data: List[Dict[str, Any]]):
        """Show debug information in a window."""
        if self.debug_window:
            self.debug_window.destroy()
        
        # Only create debug window if we have a parent window
        if self.parent:
            self.debug_window = tk.Toplevel(self.parent)
        else:
            # For automatic operations, don't create debug window
            self.debug_window = None
            return
        self.debug_window.title(title)
        self.debug_window.geometry("1400x900")
        
        # Create main frame
        main_frame = tk.Frame(self.debug_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate debug content
        content = self._generate_debug_content(debug_data)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(main_frame, text="Close",
                              command=self.debug_window.destroy)
        close_btn.pack(pady=5)
    
    def _generate_debug_content(self, debug_data: List[Dict[str, Any]]) -> str:
        """Generate comprehensive debug content."""
        lines = []
        
        # Header
        lines.append("🔧 PM OVERVIEW UPDATE DEBUG INFORMATION")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("📊 Update Summary:")
        lines.append(f"   Total Operations: {len(debug_data)}")
        lines.append(f"   Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Detailed operations
        lines.append("📋 Detailed Operations:")
        lines.append("=" * 80)
        lines.append("SOURCE SHEET | SOURCE CELL | TARGET CELL | ORIGINAL FORMULA | ADJUSTED FORMULA | VALUE")
        lines.append("-" * 80)
        
        for item in debug_data:
            source_sheet = item.get('source_sheet', 'Unknown')
            source_cell = item.get('source_cell', 'Unknown')
            target_cell = item.get('target_cell', 'Unknown')
            original_formula = item.get('original_formula', 'N/A')
            adjusted_formula = item.get('adjusted_formula', 'N/A')
            value = item.get('value', 'N/A')
            
            # Truncate long formulas for display
            orig_display = str(original_formula)[:30] + "..." if len(str(original_formula)) > 30 else str(original_formula)
            adj_display = str(adjusted_formula)[:30] + "..." if len(str(adjusted_formula)) > 30 else str(adjusted_formula)
            
            lines.append(f"{source_sheet:<12} | {source_cell:<11} | {target_cell:<11} | {orig_display:<16} | {adj_display:<16} | {value}")
        
        lines.append("-" * 80)
        lines.append("")
        
        # Error summary if any
        errors = [item for item in debug_data if item.get('error')]
        if errors:
            lines.append("❌ Errors Encountered:")
            lines.append("=" * 80)
            for item in errors:
                lines.append(f"   {item['source_cell']} → {item['target_cell']}: {item['error']}")
            lines.append("")
        
        return "\n".join(lines)


class UpdatePMOverviewHandler(BaseHandler):
    """
    Handler for updating PM Overview worksheet with partner formula data.
    
    This handler updates the PM Overview worksheet with formulas from
    partner worksheets (P2, P3, etc.) after partner operations.
    """
    
    def __init__(self, parent_window: Optional[tk.Widget], workbook_path: Optional[str] = None):
        """
        Initialize the PM Overview update handler.
        
        Args:
            parent_window: Parent tkinter window (can be None for automatic updates)
            workbook_path: Optional path to Excel workbook
        """
        # Initialize base handler with optional parent window
        super().__init__(parent_window, workbook_path)
        self.pm_overview_sheet_name = "PM Overview"
        self.debug_window = PMOverviewDebugWindow(parent_window)
        self.parent_window = parent_window  # Store for debug window access
    
    def validate_input(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate input data and workbook structure.
        
        Args:
            data: Input data containing workbook reference
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        # Check if workbook is provided
        workbook = data.get('workbook')
        if not workbook:
            result.add_error("Workbook is required")
            return result
        
        # Validate PM Overview worksheet exists
        if self.pm_overview_sheet_name not in workbook.sheetnames:
            result.add_error(f"'{self.pm_overview_sheet_name}' worksheet not found")
        
        # Check for at least one partner worksheet
        partner_sheets = self.get_partner_worksheets(workbook)
        if not partner_sheets:
            result.add_warning("No partner worksheets found (P2-P20)")
        
        return result
    
    def process(self, data: Dict[str, Any]) -> OperationResult:
        """
        Process the PM Overview update operation.
        
        Args:
            data: Data containing workbook and optional partner_number
            
        Returns:
            OperationResult: Operation result
        """
        workbook = data['workbook']
        specific_partner = data.get('partner_number')
        
        try:
            with LogContext("update_pm_overview",
                            specific_partner=specific_partner):
                
                debug_data = []
                
                if specific_partner:
                    # Update specific partner only
                    updated_count, partner_debug = self._update_specific_partner(workbook, specific_partner)
                    debug_data.extend(partner_debug)
                else:
                    # Update all partners
                    updated_count, all_debug = self._update_all_partners(workbook)
                    debug_data.extend(all_debug)
                
                # Show debug window if parent window is available
                if self.parent_window and debug_data:
                    self.debug_window.show_debug_info(
                        f"PM Overview Update - {updated_count} Partner(s)",
                        debug_data
                    )
                
                return OperationResult(
                    success=True,
                    message=f"Updated {updated_count} partner(s) in PM Overview",
                    data={'updated_partners': updated_count, 'debug_data': debug_data}
                )
                
        except Exception as e:
            logger.exception("Failed to update PM Overview")
            return OperationResult(
                success=False,
                message=f"Update failed: {str(e)}",
                errors=[str(e)]
            )
    
    def get_partner_worksheets(self, workbook: "Workbook") -> List[Tuple[str, int]]:
        """
        Get list of partner worksheets in the workbook.
        
        Args:
            workbook: Excel workbook
            
        Returns:
            List[Tuple[str, int]]: List of (sheet_name, partner_number) tuples
        """
        partner_sheets = []
        
        for sheet_name in workbook.sheetnames:
            partner_number = get_partner_number_from_sheet_name(sheet_name)
            if partner_number:
                partner_sheets.append((sheet_name, partner_number))
        
        # Sort by partner number
        partner_sheets.sort(key=lambda x: x[1])
        
        logger.debug(f"Found {len(partner_sheets)} partner worksheets",
                     partner_sheets=[f"{name} (P{num})" for name, num in partner_sheets])
        
        return partner_sheets
    
    def extract_partner_formulas(self, worksheet: "Worksheet", partner_number: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extract formulas from a partner worksheet with detailed debugging.
        
        Args:
            worksheet: Partner worksheet
            partner_number: Partner number
            
        Returns:
            Tuple[Dict[str, Any], List[Dict[str, Any]]]: (partner_data, debug_data)
        """
        data = {
            'partner_number': partner_number,
            'formula_mappings': {}
        }
        debug_data = []
        
        logger.info(f"🔍 EXTRACTING FORMULAS from Partner {partner_number} worksheet: {worksheet.title}")
        
        try:
            # Extract all mapped cells
            for source_cell, target_col in PM_OVERVIEW_CELL_MAPPINGS.items():
                try:
                    # Get the cell
                    cell = worksheet[source_cell]
                    
                    # Check if cell contains a formula
                    if hasattr(cell, 'value') and cell.value is not None:
                        if hasattr(cell, 'data_type') and cell.data_type == 'f':
                            # Cell contains a formula
                            formula = cell.value
                            calculated_value = cell.displayed_value if hasattr(cell, 'displayed_value') else 'N/A'
                        else:
                            # Cell contains a value, create a simple formula
                            formula = f"={cell.value}" if isinstance(cell.value, (int, float)) else cell.value
                            calculated_value = cell.value
                    else:
                        # Empty cell
                        formula = None
                        calculated_value = None
                    
                    # Store the mapping
                    data['formula_mappings'][source_cell] = {
                        'formula': formula,
                        'value': calculated_value,
                        'target_col': target_col
                    }
                    
                    # Add to debug data
                    debug_item = {
                        'source_sheet': worksheet.title,
                        'source_cell': source_cell,
                        'target_cell': f"{target_col}{get_pm_overview_row(partner_number)}",
                        'original_formula': formula,
                        'value': calculated_value
                    }
                    debug_data.append(debug_item)
                    
                    if DEBUG_ENABLED:
                        logger.info(f"📍 SOURCE: {source_cell:>4} | FORMULA: {str(formula):>20} | VALUE: {str(calculated_value):>15} | TARGET: Column {target_col}")
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to extract from {source_cell}: {e}")
                    debug_item = {
                        'source_sheet': worksheet.title,
                        'source_cell': source_cell,
                        'target_cell': f"{target_col}{get_pm_overview_row(partner_number)}",
                        'original_formula': None,
                        'value': None,
                        'error': str(e)
                    }
                    debug_data.append(debug_item)
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR extracting formulas from partner {partner_number}: {e}")
            raise
        
        return data, debug_data
    
    def update_pm_overview_row(self, pm_ws: "Worksheet", partner_data: Dict[str, Any],
                               debug_data: List[Dict[str, Any]]) -> None:
        """
        Update a specific row in the PM Overview worksheet with formulas.
        
        Args:
            pm_ws: PM Overview worksheet
            partner_data: Partner data to write
            debug_data: Debug data list to append to
        """
        partner_number = partner_data['partner_number']
        target_row = get_pm_overview_row(partner_number)
        formula_mappings = partner_data.get('formula_mappings', {})
        
        logger.info(f"🎯 UPDATING PM Overview Row {target_row} for Partner {partner_number}")
        
        try:
            update_count = 0
            
            # Process all formula mappings
            for source_cell, mapping_info in formula_mappings.items():
                target_col = mapping_info.get('target_col', '')
                original_formula = mapping_info.get('formula')
                target_cell = f"{target_col}{target_row}"
                
                try:
                    if original_formula:
                        # Adjust formula references for new location
                        adjusted_formula = adjust_formula_references(
                            original_formula,
                            18,  # Source row (always 18 for partner worksheets)
                            target_row,  # Target row in PM Overview
                            f"P{partner_number}",  # Source sheet reference
                            "PM Overview"  # Target sheet reference
                        )
                        
                        # Set the adjusted formula
                        pm_ws[target_cell] = adjusted_formula
                        
                        # Update debug data
                        self._update_debug_item(debug_data, source_cell, target_cell,
                                                'adjusted_formula', adjusted_formula)
                        
                        if DEBUG_ENABLED:
                            logger.info(f"✅ {source_cell:>4} → {target_cell:>4} | FORMULA: {str(adjusted_formula):>20}")
                        
                        update_count += 1
                    else:
                        # Handle empty cells
                        pm_ws[target_cell] = None
                        
                        # Update debug data
                        self._update_debug_item(debug_data, source_cell, target_cell,
                                                'adjusted_formula', 'Empty')
                
                except Exception as e:
                    logger.error(f"❌ FAILED to update {source_cell} → {target_col}{target_row}: {e}")
                    
                    # Update debug data with error
                    self._update_debug_item(debug_data, source_cell, f"{target_col}{target_row}",
                                            'error', str(e))
            
            if DEBUG_ENABLED:
                logger.info(f"✅ Successfully updated {update_count} formulas in PM Overview row {target_row}")
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR updating PM Overview row {target_row}: {e}")
            raise
    
    def _update_debug_item(self, debug_data: List[Dict[str, Any]], source_cell: str,
                           target_cell: str, key: str, value: Any) -> None:
        """Helper method to update debug data items."""
        for debug_item in debug_data:
            if (debug_item.get('source_cell') == source_cell and
                    debug_item.get('target_cell') == target_cell):
                debug_item[key] = value
                break
    
    def _update_specific_partner(self, workbook: "Workbook", partner_number: int) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Update PM Overview for a specific partner.
        
        Args:
            workbook: Excel workbook
            partner_number: Partner number to update
            
        Returns:
            Tuple[int, List[Dict[str, Any]]]: (updated_count, debug_data)
        """
        # Find the partner worksheet
        partner_sheets = self.get_partner_worksheets(workbook)
        partner_sheet_name = None
        
        for sheet_name, pnum in partner_sheets:
            if pnum == partner_number:
                partner_sheet_name = sheet_name
                break
        
        if not partner_sheet_name:
            logger.warning(f"Partner {partner_number} worksheet not found")
            return 0, []
        
        # Get worksheets
        partner_ws = workbook[partner_sheet_name]
        pm_ws = workbook[self.pm_overview_sheet_name]
        
        # Extract and update data
        partner_data, debug_data = self.extract_partner_formulas(partner_ws, partner_number)
        self.update_pm_overview_row(pm_ws, partner_data, debug_data)
        
        return 1, debug_data
    
    def _update_all_partners(self, workbook: "Workbook") -> Tuple[int, List[Dict[str, Any]]]:
        """
        Update PM Overview for all partners.
        
        Args:
            workbook: Excel workbook
            
        Returns:
            Tuple[int, List[Dict[str, Any]]]: (updated_count, debug_data)
        """
        partner_sheets = self.get_partner_worksheets(workbook)
        pm_ws = workbook[self.pm_overview_sheet_name]
        updated_count = 0
        all_debug_data = []
        
        for sheet_name, partner_number in partner_sheets:
            try:
                partner_ws = workbook[sheet_name]
                partner_data, debug_data = self.extract_partner_formulas(partner_ws, partner_number)
                self.update_pm_overview_row(pm_ws, partner_data, debug_data)
                all_debug_data.extend(debug_data)
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update partner {partner_number}: {e}")
                # Continue with other partners
        
        return updated_count, all_debug_data
    
    def manual_update(self, workbook: "Workbook") -> OperationResult:
        """
        Perform manual update of PM Overview (called from menu).
        
        Args:
            workbook: Excel workbook
            
        Returns:
            OperationResult: Operation result
        """
        return self.execute({'workbook': workbook})


# Integration functions for automatic updates

@exception_handler.handle_exceptions(
    show_dialog=True, log_error=True, return_value=False
)
def update_pm_overview_after_partner_operation(workbook: "Workbook", partner_number: int, parent_window: Optional[tk.Widget] = None) -> bool:
    """
    Update PM Overview after a partner add/edit operation.
    
    Args:
        workbook: Excel workbook
        partner_number: Partner number that was added/edited (for logging purposes)
        parent_window: Parent window for debug display
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with LogContext("auto_update_pm_overview",
                        partner_number=partner_number):
            
            logger.info(f"Auto-updating PM Overview for all partners (triggered by partner {partner_number})")
            
            # Create handler instance
            handler = UpdatePMOverviewHandler(parent_window, None)
            
            # Perform the update for ALL partners (not just the specific one)
            result = handler.execute({
                'workbook': workbook
                # No partner_number specified = update all partners
            })
            
            if result.success:
                logger.info(f"PM Overview auto-update successful for all partners (triggered by partner {partner_number})")
                return True
            else:
                logger.error(f"PM Overview auto-update failed: {result.message}")
                return False
                
    except Exception:
        logger.exception(f"Exception during PM Overview auto-update for all partners (triggered by partner {partner_number})")
        return False


@exception_handler.handle_exceptions(
    show_dialog=True, log_error=True, return_value=False
)
def update_pm_overview_after_workpackage_operation(workbook: "Workbook", parent_window: Optional[tk.Widget] = None) -> bool:
    """
    Update PM Overview after a workpackage add/edit operation.
    
    Args:
        workbook: Excel workbook
        parent_window: Parent window for debug display
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with LogContext("auto_update_pm_overview_workpackage"):
            
            logger.info("Auto-updating PM Overview for all partners (triggered by workpackage operation)")
            
            # Create handler instance
            handler = UpdatePMOverviewHandler(parent_window, None)
            
            # Perform the update for ALL partners
            result = handler.execute({
                'workbook': workbook
                # No partner_number specified = update all partners
            })
            
            if result.success:
                logger.info("PM Overview auto-update successful for all partners (triggered by workpackage operation)")
                return True
            else:
                logger.error(f"PM Overview auto-update failed: {result.message}")
                return False
                
    except Exception:
        logger.exception("Exception during PM Overview auto-update for all partners (triggered by workpackage operation)")
        return False


def update_pm_overview_with_progress(parent_window, workbook: "Workbook") -> bool:
    """
    Update PM Overview with progress dialog (for manual updates).
    
    Args:
        parent_window: Parent window for progress dialog
        workbook: Excel workbook
        
    Returns:
        bool: True if successful, False otherwise
    """
    def _update_with_progress(progress_dialog):
        """Internal function for progress-tracked update."""
        try:
            progress_dialog.update_status("Validating PM Overview worksheet...")
            progress_dialog.update_progress(10, 100)
            
            handler = UpdatePMOverviewHandler(parent_window, None)
            
            # Validate first
            validation = handler.validate_input({'workbook': workbook})
            if not validation.valid:
                progress_dialog.update_status("Validation failed")
                return False
            
            progress_dialog.update_status("Discovering partner worksheets...")
            progress_dialog.update_progress(25, 100)
            
            partner_sheets = handler.get_partner_worksheets(workbook)
            if not partner_sheets:
                progress_dialog.update_status("No partner worksheets found")
                return False
            
            progress_dialog.update_status(f"Updating {len(partner_sheets)} partners...")
            progress_dialog.update_progress(50, 100)
            
            # Perform the update
            result = handler.execute({'workbook': workbook})
            
            progress_dialog.update_status("Finalizing update...")
            progress_dialog.update_progress(90, 100)
            
            if result.success:
                progress_dialog.update_status("PM Overview updated successfully")
                progress_dialog.update_progress(100, 100)
                return True
            else:
                progress_dialog.update_status(f"Update failed: {result.message}")
                return False
                
        except Exception as e:
            progress_dialog.update_status(f"Error: {str(e)}")
            logger.exception("Error during PM Overview update with progress")
            return False
    
    if parent_window:
        # Use progress dialog
        result = show_progress_for_operation(
            parent_window,
            _update_with_progress,
            title="Updating PM Overview...",
            can_cancel=False,
            show_eta=True
        )
        return result if result is not None else False
    else:
        # Direct update without progress
        handler = UpdatePMOverviewHandler(None, None)
        result = handler.execute({'workbook': workbook})
        return result.success