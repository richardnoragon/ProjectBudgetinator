# Update Budget Overview Handler - Implementation Guide

## Complete Implementation Code

### 1. Main Handler File: `src/handlers/update_budget_overview_handler.py`

```python
"""
Budget Overview update handler for ProjectBudgetinator.

This module provides functionality to update the Budget Overview worksheet
with data from partner worksheets after partner add/edit operations.
"""

import datetime
from typing import Dict, Any, List, Optional, Tuple
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Local imports
from handlers.base_handler import ExcelOperationHandler, ValidationResult, OperationResult
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
    # Basic partner information
    'partner_id_code': {'source': 'D4', 'target_col': 'B'},
    'name_beneficiary_13': {'source': 'D13', 'target_col': 'C'},
    'name_beneficiary_5': {'source': 'D5', 'target_col': 'D'},
    'country': {'source': 'D6', 'target_col': 'E'},
    
    # WP data from row 13 (G13 through U13)
    'wp_data': {
        'G13': 'F', 'H13': 'G', 'I13': 'H', 'J13': 'I', 'K13': 'J',
        'L13': 'K', 'M13': 'L', 'N13': 'M', 'O13': 'N', 'P13': 'O',
        'Q13': 'P', 'R13': 'Q', 'S13': 'R', 'T13': 'S', 'U13': 'T'
    },
    
    # Additional data (skip column U in target)
    'additional_data': {
        'W13': 'V',
        'X13': 'W'
    }
}

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
        sheet_name: Sheet name like "P2 ACME" or "P3 University"
        
    Returns:
        Optional[int]: Partner number or None if invalid
    """
    if not sheet_name.startswith('P'):
        return None
    
    try:
        # Extract the part after 'P' and before the first space
        parts = sheet_name[1:].split(' ', 1)
        if parts and parts[0].isdigit():
            partner_num = int(parts[0])
            # Only accept partners 2-20
            if 2 <= partner_num <= 20:
                return partner_num
    except (ValueError, IndexError):
        pass
    
    return None


class UpdateBudgetOverviewHandler(ExcelOperationHandler):
    """
    Handler for updating Budget Overview worksheet with partner data.
    
    This handler updates the Budget Overview worksheet with data from
    partner worksheets (P2, P3, etc.) after partner operations.
    """
    
    def __init__(self, parent_window, workbook_path: Optional[str] = None):
        """
        Initialize the Budget Overview update handler.
        
        Args:
            parent_window: Parent tkinter window
            workbook_path: Optional path to Excel workbook
        """
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
    
    def get_partner_worksheets(self, workbook: Workbook) -> List[Tuple[str, int]]:
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
    
    def extract_partner_data(self, worksheet: Worksheet, partner_number: int) -> Dict[str, Any]:
        """
        Extract data from a partner worksheet.
        
        Args:
            worksheet: Partner worksheet
            partner_number: Partner number
            
        Returns:
            Dict[str, Any]: Extracted partner data
        """
        data = {'partner_number': partner_number}
        
        try:
            # Extract basic partner information
            for field, mapping in BUDGET_OVERVIEW_CELL_MAPPINGS.items():
                if field in ['partner_id_code', 'name_beneficiary_13', 'name_beneficiary_5', 'country']:
                    source_cell = mapping['source']
                    try:
                        value = worksheet[source_cell].value
                        data[field] = value if value is not None else ''
                        logger.debug(f"Extracted {field} from {source_cell}: {value}")
                    except Exception as e:
                        logger.warning(f"Failed to extract {field} from {source_cell}: {e}")
                        data[field] = ''
            
            # Extract WP data from row 13
            wp_data = {}
            for source_cell, target_col in BUDGET_OVERVIEW_CELL_MAPPINGS['wp_data'].items():
                try:
                    value = worksheet[source_cell].value
                    wp_data[source_cell] = value if value is not None else ''
                    logger.debug(f"Extracted WP data from {source_cell}: {value}")
                except Exception as e:
                    logger.warning(f"Failed to extract WP data from {source_cell}: {e}")
                    wp_data[source_cell] = ''
            data['wp_data'] = wp_data
            
            # Extract additional data
            additional_data = {}
            for source_cell, target_col in BUDGET_OVERVIEW_CELL_MAPPINGS['additional_data'].items():
                try:
                    value = worksheet[source_cell].value
                    additional_data[source_cell] = value if value is not None else ''
                    logger.debug(f"Extracted additional data from {source_cell}: {value}")
                except Exception as e:
                    logger.warning(f"Failed to extract additional data from {source_cell}: {e}")
                    additional_data[source_cell] = ''
            data['additional_data'] = additional_data
            
            logger.info(f"Successfully extracted data from partner {partner_number}")
            
        except Exception as e:
            logger.error(f"Error extracting data from partner {partner_number}: {e}")
            raise
        
        return data
    
    def update_budget_row(self, budget_ws: Worksheet, partner_data: Dict[str, Any]) -> None:
        """
        Update a specific row in the Budget Overview worksheet.
        
        Args:
            budget_ws: Budget Overview worksheet
            partner_data: Partner data to write
        """
        partner_number = partner_data['partner_number']
        target_row = get_budget_overview_row(partner_number)
        
        logger.debug(f"Updating Budget Overview row {target_row} for partner {partner_number}")
        
        try:
            # Update basic partner information
            for field, mapping in BUDGET_OVERVIEW_CELL_MAPPINGS.items():
                if field in ['partner_id_code', 'name_beneficiary_13', 'name_beneficiary_5', 'country']:
                    target_col = mapping['target_col']
                    target_cell = f"{target_col}{target_row}"
                    value = partner_data.get(field, '')
                    
                    budget_ws[target_cell] = value
                    logger.debug(f"Updated {target_cell} with {field}: {value}")
            
            # Update WP data
            wp_data = partner_data.get('wp_data', {})
            for source_cell, target_col in BUDGET_OVERVIEW_CELL_MAPPINGS['wp_data'].items():
                target_cell = f"{target_col}{target_row}"
                value = wp_data.get(source_cell, '')
                
                budget_ws[target_cell] = value
                logger.debug(f"Updated {target_cell} with WP data from {source_cell}: {value}")
            
            # Update additional data
            additional_data = partner_data.get('additional_data', {})
            for source_cell, target_col in BUDGET_OVERVIEW_CELL_MAPPINGS['additional_data'].items():
                target_cell = f"{target_col}{target_row}"
                value = additional_data.get(source_cell, '')
                
                budget_ws[target_cell] = value
                logger.debug(f"Updated {target_cell} with additional data from {source_cell}: {value}")
            
            logger.info(f"Successfully updated Budget Overview row {target_row} for partner {partner_number}")
            
        except Exception as e:
            logger.error(f"Error updating Budget Overview row {target_row}: {e}")
            raise
    
    def _update_specific_partner(self, workbook: Workbook, partner_number: int) -> int:
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
    
    def _update_all_partners(self, workbook: Workbook) -> int:
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
    
    def manual_update(self, workbook: Workbook) -> OperationResult:
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
def update_budget_overview_after_partner_operation(workbook: Workbook, partner_number: int) -> bool:
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
                
    except Exception as e:
        logger.exception(f"Exception during Budget Overview auto-update for partner {partner_number}")
        return False


def update_budget_overview_with_progress(parent_window, workbook: Workbook) -> bool:
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
        return show_progress_for_operation(
            parent_window,
            _update_with_progress,
            title="Updating Budget Overview...",
            can_cancel=False,
            show_eta=True
        )
    else:
        # Direct update without progress
        handler = UpdateBudgetOverviewHandler(None, None)
        result = handler.execute({'workbook': workbook})
        return result.success
```

### 2. Integration with Add Partner Handler

**File**: `src/handlers/add_partner_handler.py`

Add this import at the top:
```python
from handlers.update_budget_overview_handler import update_budget_overview_after_partner_operation
```

Add this code after line 834 (after `update_version_history` call):
```python
    # Update Budget Overview with new partner data
    try:
        partner_number = int(partner_info['project_partner_number'])
        success = update_budget_overview_after_partner_operation(workbook, partner_number)
        if success:
            logger.info("Budget Overview updated successfully after partner addition",
                       partner_number=partner_number)
        else:
            logger.warning("Failed to update Budget Overview after partner addition",
                          partner_number=partner_number)
    except Exception as e:
        logger.warning("Exception during Budget Overview update after partner addition",
                      error=str(e), partner_number=partner_info.get('project_partner_number'))
        # Don't fail the entire operation, just log the warning
```

### 3. Integration with Edit Partner Handler

**File**: `src/handlers/edit_partner_handler.py`

Add this import at the top:
```python
from handlers.update_budget_overview_handler import update_budget_overview_after_partner_operation
```

Add this code after line 549 (after successful worksheet update):
```python
        # Update Budget Overview with edited partner data
        if self.worksheet:
            try:
                workbook = self.worksheet.parent
                partner_number = int(partner_number)  # partner_number from line 470
                success = update_budget_overview_after_partner_operation(workbook, partner_number)
                if success:
                    logger.info("Budget Overview updated successfully after partner edit",
                               partner_number=partner_number)
                else:
                    logger.warning("Failed to update Budget Overview after partner edit",
                                  partner_number=partner_number)
            except Exception as e:
                logger.warning("Exception during Budget Overview update after partner edit",
                              error=str(e), partner_number=partner_number)
                # Don't fail the entire operation, just log the warning
```

### 4. Menu Integration

**File**: `src/gui/menu_setup.py`

Add this line after line 34 (in the modify_menu section):
```python
    modify_menu.add_separator()
    modify_menu.add_command(label="Update Budget Overview", command=app.update_budget_overview)
```

### 5. Main Application Integration

**File**: `src/main.py`

Add this method to the `ProjectBudgetinator` class:
```python
    def update_budget_overview(self):
        """Manually update Budget Overview worksheet from menu."""
        with LogContext("manual_update_budget_overview", user_id="current_user"):
            self.logger.info("Starting manual Budget Overview update")
            
            # Check if we have an open workbook
            if self.current_workbook is None:
                self.logger.warning("No workbook open, prompting user to open one")
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
                            # Validate file path and content
                            is_valid, error_msg = SecurityValidator.validate_excel_file(file_path)
                            if not is_valid:
                                messagebox.showerror("Security Error", f"Cannot open file: {error_msg}")
                                self.logger.warning("Security validation failed for file",
                                                  file_path=file_path, error=error_msg)
                                return
                            
                            # Sanitize file path
                            safe_path = SecurityValidator.validate_file_path(file_path)
                            
                            from openpyxl import load_workbook
                            self.current_workbook = load_workbook(safe_path)
                            self.logger.info("Workbook loaded successfully for Budget Overview update",
                                           file_path=safe_path)
                        except ValueError as e:
                            messagebox.showerror("Security Error", str(e))
                            self.logger.warning("Security validation error", error=str(e))
                            return
                        except Exception as e:
                            self.logger.error("Failed to load workbook for Budget Overview update",
                                            file_path=file_path, error=str(e))
                            messagebox.showerror(
                                "Error",
                                f"Could not open workbook:\n{str(e)}"
                            )
                            return
                    else:
                        self.logger.info("User cancelled workbook selection")
                        return
                else:
                    self.logger.info("User declined to open workbook")
                    return

            # Perform the Budget Overview update
            try:
                from handlers.update_budget_overview_handler import update_budget_overview_with_progress
                
                success = update_budget_overview_with_progress(self.root, self.current_workbook)
                
                if success:
                    # Ask user where to save the workbook
                    save_path = filedialog.asksaveasfilename(
                        title="Save Updated Workbook",
                        defaultextension=".xlsx",
                        filetypes=EXCEL_FILETYPES
                    )
                    if save_path:
                        self.current_workbook.save(save_path)
                        messagebox.showinfo(
                            "Success",
                            f"Budget Overview updated successfully!\nWorkbook saved to: {save_path}"
                        )
                        self.logger.info("Budget Overview update completed and workbook saved",
                                        file_path=save_path)
                    else:
                        messagebox.showwarning(
                            "Warning",
                            "Budget Overview updated but workbook not saved!"
                        )
                        self.logger.warning("Budget Overview updated but user did not save workbook")
                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to update Budget Overview. Please check the logs for details."
                    )
                    self.logger.error("Budget Overview update failed")
                    
            except Exception as e:
                self.logger.exception("Exception during manual Budget Overview update")
                messagebox.showerror(
                    "Error",
                    f"An error occurred while updating Budget Overview:\n{str(e)}"
                )
```

## Testing Implementation

### Unit Test File: `tests/test_update_budget_overview_handler.py`

```python
"""
Unit tests for UpdateBudgetOverviewHandler.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from handlers.update_budget_overview_handler import (
    UpdateBudgetOverviewHandler,
    get_budget_overview_row,
    get_partner_number_from_sheet_name,
    update_budget_overview_after_partner_operation
)


class TestUpdateBudgetOverviewHandler(unittest.TestCase):
    """Test cases for UpdateBudgetOverviewHandler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_parent = Mock()
        self.handler = UpdateBudgetOverviewHandler(self.mock_parent, None)
        
    def test_get_budget_overview_row(self):
        """Test budget overview row calculation."""
        self.assertEqual(get_budget_overview_row(2), 9)
        self.assertEqual(get_budget_overview_row(3), 10)
        self.assertEqual(get_budget_overview_row(15), 22)
        
    def test_get_partner_number_from_sheet_name(self):
        """Test partner number extraction from sheet names."""
        self.assertEqual(get_partner_number_from_sheet_name("P2 ACME"), 2)
        self.assertEqual(get_partner_number_from_sheet_name("P3 University"), 3)
        self.assertEqual(get_partner_number_from_sheet_name("P15 Company"), 15)
        self.assertIsNone(get_partner_number_from_sheet_name("P1 Coordinator"))
        self.assertIsNone(get_partner_number_from_sheet_name("P21 Invalid"))
        self.assertIsNone(get_partner_number_from_sheet_name("Summary"))
        
    def test_validate_input_missing_workbook(self):
        """Test validation with missing workbook."""
        result = self.handler.validate_input({})
        self.assertFalse(result.valid)
        self.assertIn("Workbook is required", result.errors)
        
    def test_validate_input_missing_budget_overview(self):
        """Test validation with missing Budget Overview worksheet."""
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["P2 ACME", "P3 University"]
        
        result = self.handler.validate_input({'workbook': mock_workbook})
        self.assertFalse(result.valid)
        self.assertIn("'Budget Overview' worksheet not found", result.errors)
        
    def test_get_partner_worksheets(self):
        """Test partner worksheet discovery."""
        mock_workbook = Mock()
        mock_workbook.sheetnames = [
            "Budget Overview", "P2 ACME", "P3 University", 
            "P1 Coordinator", "Summary", "P15 Company"
        ]
        
        partner_sheets = self.handler.get_partner_worksheets(mock_workbook)
        expected = [("P2 ACME", 2), ("P3 University", 3), ("P15 Company", 15)]
        self.assertEqual(partner_sheets, expected)


if __name__ == '__main__':
    unittest.main()
```

## Deployment Checklist

### Pre-Implementation
- [ ] Review existing codebase patterns
- [ ] Confirm Budget Overview worksheet structure
- [ ] Validate cell mapping requirements
- [ ] Test with sample workbook

### Implementation Phase
- [ ] Create `update_budget_overview_handler.py`
- [ ] Integrate with `add_partner_handler.py`
- [ ] Integrate with `edit_partner_handler.py`
- [ ] Add menu item to `menu_setup.py`
- [ ] Add method to `main.py`

### Testing Phase
- [ ] Unit tests for handler class
- [ ] Integration tests with partner operations
- [ ] Manual testing of menu item
- [ ] Error handling validation
- [ ] Performance testing with multiple partners

### Documentation
- [ ] Code documentation and docstrings
- [ ] User guide updates
- [ ] Integration documentation
- [ ] Troubleshooting guide

This implementation guide provides complete, ready-to-use code that follows the existing patterns in the ProjectBudgetinator codebase while implementing the Budget Overview update functionality as specified.