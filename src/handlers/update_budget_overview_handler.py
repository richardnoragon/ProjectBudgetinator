"""
Budget Overview update handler for ProjectBudgetinator.

This module provides functionality to update the Budget Overview worksheet
with data from partner worksheets after partner add/edit operations.
"""

import datetime
import tkinter as tk
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
logger = get_structured_logger("handlers.update_budget_overview")

# Budget Overview cell mappings configuration
BUDGET_OVERVIEW_CELL_MAPPINGS = {
    # Complete cell mapping from partner worksheets to Budget Overview
    # Format: source_cell -> target_column
    'D4': 'B',   # Partner ID Code
    'D13': 'C',  # Name of Beneficiary (from row 13)
    'D5': 'D',   # Name of Beneficiary (from row 5)
    'D6': 'E',   # Country
    
    # WP data from row 13 (G13 through U13) -> columns F through T
    'G13': 'F', 'H13': 'G', 'I13': 'H', 'J13': 'I', 'K13': 'J',
    'L13': 'K', 'M13': 'L', 'N13': 'M', 'O13': 'N', 'P13': 'O',
    'Q13': 'P', 'R13': 'Q', 'S13': 'R', 'T13': 'S', 'U13': 'T',
    
    # Additional data (skip column U in target, so V13->U, W13->V, X13->W)
    'V13': 'U', 'W13': 'V', 'X13': 'W'
}

# Debug configuration
DEBUG_ENABLED = True
DEBUG_DETAILED = True  # Set to False to reduce debug output


def get_budget_overview_row(partner_number: int) -> int:
    """
    Calculate Budget Overview row number from partner number.
    
    Args:
        partner_number: Partner number (2, 3, 4, etc.)
        
    Returns:
        int: Row number in Budget Overview (9, 10, 11, etc.)
    """
    return partner_number + 7  # P2->Row9, P3->Row10, etc.


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


class UpdateBudgetOverviewHandler(BaseHandler):
    """
    Handler for updating Budget Overview worksheet with partner data.
    
    This handler updates the Budget Overview worksheet with data from
    partner worksheets (P2, P3, etc.) after partner operations.
    """
    
    def __init__(self, parent_window: Optional[tk.Widget], workbook_path: Optional[str] = None):
        """
        Initialize the Budget Overview update handler.
        
        Args:
            parent_window: Parent tkinter window (can be None for automatic updates)
            workbook_path: Optional path to Excel workbook
        """
        # Initialize base handler with optional parent window
        super().__init__(parent_window, workbook_path)
        self.budget_overview_sheet_name = "Budget Overview"
    
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
        
        # Validate Budget Overview worksheet exists
        if self.budget_overview_sheet_name not in workbook.sheetnames:
            result.add_error(f"'{self.budget_overview_sheet_name}' worksheet not found")
        
        # Check for at least one partner worksheet
        partner_sheets = self.get_partner_worksheets(workbook)
        if not partner_sheets:
            result.add_warning("No partner worksheets found (P2-P20)")
        
        return result
    
    def process(self, data: Dict[str, Any]) -> OperationResult:
        """
        Process the Budget Overview update operation.
        
        Args:
            data: Data containing workbook and optional partner_number
            
        Returns:
            OperationResult: Operation result
        """
        workbook = data['workbook']
        specific_partner = data.get('partner_number')
        
        try:
            with LogContext("update_budget_overview",
                            specific_partner=specific_partner):
                
                if specific_partner:
                    # Update specific partner only
                    updated_count = self._update_specific_partner(workbook, specific_partner)
                else:
                    # Update all partners
                    updated_count = self._update_all_partners(workbook)
                
                return OperationResult(
                    success=True,
                    message=f"Updated {updated_count} partner(s) in Budget Overview",
                    data={'updated_partners': updated_count}
                )
                
        except Exception as e:
            logger.exception("Failed to update Budget Overview")
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
    
    def extract_partner_data(self, worksheet: "Worksheet", partner_number: int) -> Dict[str, Any]:
        """
        Extract data from a partner worksheet with detailed debugging.
        
        Args:
            worksheet: Partner worksheet
            partner_number: Partner number
            
        Returns:
            Dict[str, Any]: Extracted partner data with cell mappings
        """
        data: Dict[str, Any] = {
            'partner_number': partner_number,
            'cell_mappings': {}  # Store source->value mappings for debugging
        }
        
        logger.info(f"🔍 EXTRACTING DATA from Partner {partner_number} worksheet: {worksheet.title}")
        
        if DEBUG_ENABLED:
            logger.info("=" * 80)
            logger.info(f"📊 DEBUG: Partner {partner_number} Data Extraction")
            logger.info("=" * 80)
        
        try:
            # Extract all mapped cells
            for source_cell, target_col in BUDGET_OVERVIEW_CELL_MAPPINGS.items():
                try:
                    # Get the cell value
                    cell = worksheet[source_cell]
                    value = cell.value
                    
                    # Store the mapping
                    data['cell_mappings'][source_cell] = {
                        'value': value,
                        'target_col': target_col,
                        'formatted_value': value if value is not None else ''
                    }
                    
                    if DEBUG_ENABLED:
                        logger.info(f"📍 SOURCE: {source_cell:>4} | VALUE: {str(value):>15} | TARGET: Column {target_col}")
                        
                        if DEBUG_DETAILED:
                            logger.debug(f"   Cell type: {type(value).__name__}")
                            logger.debug(f"   Cell coordinate: {cell.coordinate}")
                            logger.debug(f"   Cell data type: {cell.data_type}")
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to extract from {source_cell}: {e}")
                    data['cell_mappings'][source_cell] = {
                        'value': None,
                        'target_col': target_col,
                        'formatted_value': '',
                        'error': str(e)
                    }
            
            if DEBUG_ENABLED:
                logger.info("=" * 80)
                logger.info(f"✅ Successfully extracted {len(data['cell_mappings'])} cell mappings from partner {partner_number}")
                logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR extracting data from partner {partner_number}: {e}")
            raise
        
        return data
    
    def _update_single_cell(self, budget_ws: "Worksheet", source_cell: str,
                            mapping_info: Dict[str, Any], target_row: int) -> bool:
        """
        Update a single cell in the Budget Overview worksheet.
        
        Args:
            budget_ws: Budget Overview worksheet
            source_cell: Source cell reference
            mapping_info: Mapping information with target_col and value
            target_row: Target row number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_col = mapping_info.get('target_col', '')
            value = mapping_info.get('formatted_value', '')
            target_cell = f"{target_col}{target_row}"
            
            # Update the cell
            budget_ws[target_cell] = value
            
            if DEBUG_ENABLED:
                logger.info(f"✅ {source_cell:>4} → {target_cell:>4} | VALUE: {str(value):>15}")
                
                if DEBUG_DETAILED:
                    logger.debug(f"   Original value: {mapping_info.get('value')}")
                    logger.debug(f"   Value type: {type(value).__name__}")
                    logger.debug(f"   Target worksheet: {budget_ws.title}")
            
            return True
            
        except Exception as e:
            target_col = mapping_info.get('target_col', 'UNKNOWN')
            logger.error(f"❌ FAILED to update {source_cell} → {target_col}{target_row}: {e}")
            if 'error' not in mapping_info:
                mapping_info['error'] = str(e)
            return False

    def update_budget_row(self, budget_ws: "Worksheet", partner_data: Dict[str, Any]) -> None:
        """
        Update a specific row in the Budget Overview worksheet with detailed debugging.
        
        Args:
            budget_ws: Budget Overview worksheet
            partner_data: Partner data to write
        """
        partner_number = partner_data['partner_number']
        target_row = get_budget_overview_row(partner_number)
        cell_mappings = partner_data.get('cell_mappings', {})
        
        logger.info(f"🎯 UPDATING Budget Overview Row {target_row} for Partner {partner_number}")
        
        if DEBUG_ENABLED:
            logger.info("=" * 80)
            logger.info(f"📝 DEBUG: Budget Overview Row {target_row} Update")
            logger.info("=" * 80)
        
        try:
            update_count = 0
            
            # Process all cell mappings
            for source_cell, mapping_info in cell_mappings.items():
                if self._update_single_cell(budget_ws, source_cell, mapping_info, target_row):
                    update_count += 1
            
            if DEBUG_ENABLED:
                logger.info("=" * 80)
                logger.info(f"✅ Successfully updated {update_count} cells in Budget Overview row {target_row}")
                logger.info(f"📊 Partner {partner_number} → Row {target_row} mapping complete")
                logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR updating Budget Overview row {target_row}: {e}")
            raise
    
    def _update_specific_partner(self, workbook: "Workbook", partner_number: int) -> int:
        """
        Update Budget Overview for a specific partner.
        
        Args:
            workbook: Excel workbook
            partner_number: Partner number to update
            
        Returns:
            int: Number of partners updated (0 or 1)
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
            return 0
        
        # Get worksheets
        partner_ws = workbook[partner_sheet_name]
        budget_ws = workbook[self.budget_overview_sheet_name]
        
        # Extract and update data
        partner_data = self.extract_partner_data(partner_ws, partner_number)
        self.update_budget_row(budget_ws, partner_data)
        
        return 1
    
    def _update_all_partners(self, workbook: "Workbook") -> int:
        """
        Update Budget Overview for all partners.
        
        Args:
            workbook: Excel workbook
            
        Returns:
            int: Number of partners updated
        """
        partner_sheets = self.get_partner_worksheets(workbook)
        budget_ws = workbook[self.budget_overview_sheet_name]
        updated_count = 0
        
        for sheet_name, partner_number in partner_sheets:
            try:
                partner_ws = workbook[sheet_name]
                partner_data = self.extract_partner_data(partner_ws, partner_number)
                self.update_budget_row(budget_ws, partner_data)
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update partner {partner_number}: {e}")
                # Continue with other partners
        
        return updated_count
    
    def manual_update(self, workbook: "Workbook") -> OperationResult:
        """
        Perform manual update of Budget Overview (called from menu).
        
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
def update_budget_overview_after_partner_operation(workbook: "Workbook", partner_number: int) -> bool:
    """
    Update Budget Overview after a partner add/edit operation.
    
    Args:
        workbook: Excel workbook
        partner_number: Partner number that was added/edited
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with LogContext("auto_update_budget_overview",
                        partner_number=partner_number):
            
            logger.info(f"Auto-updating Budget Overview for partner {partner_number}")
            
            # Create handler instance (no parent window for automatic updates)
            handler = UpdateBudgetOverviewHandler(None, None)
            
            # Perform the update
            result = handler.execute({
                'workbook': workbook,
                'partner_number': partner_number
            })
            
            if result.success:
                logger.info(f"Budget Overview auto-update successful for partner {partner_number}")
                return True
            else:
                logger.error(f"Budget Overview auto-update failed: {result.message}")
                return False
                
    except Exception:
        logger.exception(f"Exception during Budget Overview auto-update for partner {partner_number}")
        return False


def update_budget_overview_with_progress(parent_window, workbook: "Workbook") -> bool:
    """
    Update Budget Overview with progress dialog (for manual updates).
    
    Args:
        parent_window: Parent window for progress dialog
        workbook: Excel workbook
        
    Returns:
        bool: True if successful, False otherwise
    """
    def _update_with_progress(progress_dialog):
        """Internal function for progress-tracked update."""
        try:
            progress_dialog.update_status("Validating Budget Overview worksheet...")
            progress_dialog.update_progress(10, 100)
            
            handler = UpdateBudgetOverviewHandler(parent_window, None)
            
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
                progress_dialog.update_status("Budget Overview updated successfully")
                progress_dialog.update_progress(100, 100)
                return True
            else:
                progress_dialog.update_status(f"Update failed: {result.message}")
                return False
                
        except Exception as e:
            progress_dialog.update_status(f"Error: {str(e)}")
            logger.exception("Error during Budget Overview update with progress")
            return False
    
    if parent_window:
        # Use progress dialog
        result = show_progress_for_operation(
            parent_window,
            _update_with_progress,
            title="Updating Budget Overview...",
            can_cancel=False,
            show_eta=True
        )
        return result if result is not None else False
    else:
        # Direct update without progress
        handler = UpdateBudgetOverviewHandler(None, None)
        result = handler.execute({'workbook': workbook})
        return result.success