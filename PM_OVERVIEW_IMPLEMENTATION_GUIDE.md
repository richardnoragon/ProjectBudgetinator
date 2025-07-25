# PM Overview Handler Implementation Guide

## Overview

This document provides a comprehensive guide to the PM Overview update functionality implemented for ProjectBudgetinator. The PM Overview handler automatically updates the PM Overview worksheet with formulas from partner worksheets after partner add/edit operations.

## Architecture

### Core Components

1. **`src/handlers/update_pm_overview_handler.py`** - Main handler for PM Overview updates
2. **`src/handlers/pm_overview_format.py`** - Conditional formatting for PM Overview
3. **Integration hooks** - Automatic updates in add/edit partner handlers
4. **Menu integration** - Manual update option via "Update PM Overview" menu item
5. **Comprehensive tests** - Full test coverage in `tests/test_update_pm_overview_handler.py`

### Key Features

- **Formula Copying**: Copies actual formulas from partner worksheets C18-Q18 to PM Overview
- **Cell Reference Adjustment**: Automatically adjusts cell references when copying formulas
- **Debug Window**: Shows detailed information about source, target, and values
- **Automatic Integration**: Updates PM Overview after partner add/edit operations
- **Manual Updates**: Menu option for manual PM Overview updates
- **Conditional Formatting**: Visual formatting based on row completion status

## Cell Mapping Strategy

### Partner Worksheet to PM Overview Mapping

| Partner Number | PM Overview Row | Source Cells | Target Cells |
|----------------|-----------------|--------------|--------------|
| Partner 2      | Row 6          | C18-Q18      | C6-Q6        |
| Partner 3      | Row 7          | C18-Q18      | C7-Q7        |
| Partner 4      | Row 8          | C18-Q18      | C8-Q8        |
| ...            | ...            | ...          | ...          |
| Partner 20     | Row 24         | C18-Q18      | C24-Q24      |

### Formula Calculation

```python
def get_pm_overview_row(partner_number: int) -> int:
    """Calculate PM Overview row number from partner number."""
    return partner_number + 4  # P2->Row6, P3->Row7, etc.
```

### Cell Mappings (WP1-WP15)

```python
PM_OVERVIEW_CELL_MAPPINGS = {
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
```

## Formula Adjustment Logic

### How Formula References Are Adjusted

When copying formulas from partner worksheets to PM Overview, cell references are automatically adjusted:

1. **Relative References**: Adjusted based on row difference
   - Source: `=SUM(A1:A10)` in row 18
   - Target: `=SUM(A1:A10)` in row 6 (formulas maintain absolute references for cross-sheet calculations)

2. **Absolute References**: Remain unchanged
   - Source: `=SUM($A$1:$A$10)` in row 18
   - Target: `=SUM($A$1:$A$10)` in row 6

3. **Mixed References**: Only relative parts are adjusted
   - Source: `=SUM(A$1:A$10)` in row 18
   - Target: `=SUM(A$1:A$10)` in row 6 (absolute references preserved)

### Formula Adjustment Function

```python
def adjust_formula_references(formula: str, source_row: int, target_row: int,
                              source_sheet: str, target_sheet: str) -> str:
    """
    Adjust cell references in a formula when copying from source to target location.
    
    Args:
        formula: Original formula string
        source_row: Source row number (always 18 for partner worksheets)
        target_row: Target row number in PM Overview
        source_sheet: Source worksheet name (e.g., "P2-ACME")
        target_sheet: Target worksheet name ("PM Overview")
        
    Returns:
        str: Adjusted formula string
    """
```

## Integration Points

### Automatic Updates

#### Add Partner Handler Integration

```python
# In src/handlers/add_partner_handler.py
try:
    from handlers.update_pm_overview_handler import update_pm_overview_after_partner_operation
    partner_number = int(partner_info['project_partner_number'])
    success = update_pm_overview_after_partner_operation(workbook, partner_number)
    if success:
        logger.info("PM Overview updated successfully after partner addition")
    else:
        logger.warning("Failed to update PM Overview after partner addition")
except Exception as e:
    logger.warning("Exception during PM Overview update after partner addition")
```

#### Edit Partner Handler Integration

```python
# In src/handlers/edit_partner_handler.py
try:
    from handlers.update_pm_overview_handler import update_pm_overview_after_partner_operation
    workbook = self.worksheet.parent
    partner_num = int(partner_number)
    parent_window = self.master if hasattr(self, 'master') else None
    pm_success = update_pm_overview_after_partner_operation(workbook, partner_num, parent_window)
    if pm_success:
        logger.info("PM Overview updated successfully after partner edit")
except Exception as e:
    logger.warning("Exception during PM Overview update after partner edit")
```

### Manual Updates

#### Menu Integration

```python
# In src/gui/menu_setup.py
modify_menu.add_command(label="Update PM Overview", command=app.update_pm_overview)
```

#### Main Application Method

```python
# In src/main.py
def update_pm_overview(self):
    """Manually update PM Overview worksheet from menu."""
    # Load workbook if needed
    # Perform PM Overview update with progress dialog
    # Apply conditional formatting
    # Save workbook
```

## Debug Window Functionality

### Debug Information Displayed

The debug window shows comprehensive information about the PM Overview update process:

1. **Update Summary**
   - Total operations performed
   - Timestamp of update
   - Success/failure status

2. **Detailed Operations Table**
   - Source sheet and cell
   - Target cell
   - Original formula
   - Adjusted formula
   - Calculated value

3. **Error Summary**
   - Any errors encountered during update
   - Specific error messages for troubleshooting

### Debug Window Example

```
🔧 PM OVERVIEW UPDATE DEBUG INFORMATION
================================================================================

📊 Update Summary:
   Total Operations: 30
   Timestamp: 2025-07-22 19:30:00

📋 Detailed Operations:
================================================================================
SOURCE SHEET | SOURCE CELL | TARGET CELL | ORIGINAL FORMULA | ADJUSTED FORMULA | VALUE
--------------------------------------------------------------------------------
P2-ACME      | C18         | C6          | =SUM(A1:A10)     | =SUM(A1:A10)     | 100
P2-ACME      | D18         | D6          | =B1*2            | =B1*2            | 200
P3-University| C18         | C7          | =SUM(C1:C5)      | =SUM(C1:C5)      | 150
...
```

## Conditional Formatting

### Row Status Classification

The PM Overview formatter analyzes rows and applies conditional formatting based on completion status:

1. **Complete Rows** (Green)
   - All cells C-Q contain data
   - Background: #E8F5E8
   - Text: #2E7D32 (bold)

2. **Partial Rows** (Blue/Gray)
   - Some cells contain data, others are empty
   - Filled cells: #E3F2FD background, #1565C0 text
   - Empty cells: #F5F5F5 background, #757575 text (italic)

3. **Empty Rows** (Red)
   - No cells contain data
   - Background: #FFEBEE
   - Text: #C62828

### Formatting Application

```python
# Apply PM Overview formatting
from handlers.pm_overview_format import apply_pm_overview_formatting
success = apply_pm_overview_formatting(parent_window, workbook)
```

## Error Handling and Logging

### Structured Logging

All PM Overview operations use structured logging for comprehensive tracking:

```python
logger = get_structured_logger("handlers.update_pm_overview")

# Log with context
with LogContext("update_pm_overview", partner_number=partner_number):
    logger.info("Starting PM Overview update")
    # ... perform operations
    logger.info("PM Overview update completed successfully")
```

### Exception Handling

All functions use the centralized exception handler:

```python
@exception_handler.handle_exceptions(
    show_dialog=True, log_error=True, return_value=False
)
def update_pm_overview_after_partner_operation(workbook, partner_number, parent_window=None):
    # Function implementation with automatic exception handling
```

## Testing

### Comprehensive Test Coverage

The test suite covers all aspects of PM Overview functionality:

1. **Unit Tests**
   - Cell mapping calculations
   - Formula adjustment logic
   - Debug window functionality
   - Handler validation

2. **Integration Tests**
   - Automatic update integration
   - Manual update workflow
   - Progress dialog functionality

3. **End-to-End Tests**
   - Complete workflow testing
   - Real workbook operations
   - Formula copying verification

### Running Tests

```bash
# Run PM Overview tests
python -m pytest tests/test_update_pm_overview_handler.py -v

# Run all tests
python -m pytest tests/ -v
```

## Usage Examples

### Automatic Update (After Partner Add/Edit)

```python
# Automatic update happens transparently
# No user action required - integrated into partner operations
```

### Manual Update (From Menu)

1. Open ProjectBudgetinator application
2. Load an Excel workbook with PM Overview and partner worksheets
3. Go to **Modify** → **Update PM Overview**
4. Review debug window showing update details
5. Save the updated workbook when prompted

### Programmatic Update

```python
from handlers.update_pm_overview_handler import UpdatePMOverviewHandler
from openpyxl import load_workbook

# Load workbook
workbook = load_workbook("project_budget.xlsx")

# Create handler
handler = UpdatePMOverviewHandler(parent_window=None)

# Perform update
result = handler.execute({'workbook': workbook})

if result.success:
    print(f"Updated {result.data['updated_partners']} partners")
    workbook.save("updated_project_budget.xlsx")
else:
    print(f"Update failed: {result.message}")
```

## Troubleshooting

### Common Issues

1. **PM Overview worksheet not found**
   - Ensure the workbook contains a worksheet named "PM Overview"
   - Check worksheet name spelling and case sensitivity

2. **No partner worksheets found**
   - Verify partner worksheets follow naming convention: "P{number}-{acronym}"
   - Partner numbers must be between 2-20

3. **Formula adjustment errors**
   - Check that source formulas are valid Excel formulas
   - Verify cell references in original formulas

4. **Debug window not showing**
   - Ensure parent window is provided for debug display
   - Check that debug functionality is enabled

### Debug Logging

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger("handlers.update_pm_overview").setLevel(logging.DEBUG)
```

## Performance Considerations

### Optimization Features

1. **Selective Updates**: Can update specific partners or all partners
2. **Progress Tracking**: Shows progress for large workbooks
3. **Efficient Cell Access**: Minimizes worksheet read/write operations
4. **Error Recovery**: Continues processing other partners if one fails

### Memory Management

- Uses lazy loading for worksheet access
- Processes partners sequentially to minimize memory usage
- Cleans up resources automatically

## Security Considerations

### Input Validation

- All file paths are validated using SecurityValidator
- Partner numbers are range-checked (2-20)
- Formula content is sanitized before processing

### Error Handling

- No sensitive information exposed in error messages
- All exceptions are logged securely
- User input is sanitized before processing

## Future Enhancements

### Potential Improvements

1. **Batch Operations**: Support for updating multiple workbooks
2. **Formula Templates**: Predefined formula templates for common scenarios
3. **Undo Functionality**: Ability to revert PM Overview updates
4. **Export Options**: Export debug information to Excel/CSV
5. **Custom Mappings**: User-configurable cell mappings

### Extension Points

The architecture supports easy extension for:
- Additional worksheet types
- Custom formula adjustment rules
- Alternative formatting schemes
- Integration with external systems

## Conclusion

The PM Overview handler provides a robust, well-tested solution for automatically updating PM Overview worksheets with partner data. The implementation includes comprehensive error handling, detailed debugging capabilities, and seamless integration with existing partner management workflows.

Key benefits:
- **Automatic Updates**: No manual intervention required
- **Formula Preservation**: Maintains Excel formula functionality
- **Debug Transparency**: Clear visibility into update process
- **Robust Error Handling**: Graceful handling of edge cases
- **Comprehensive Testing**: Full test coverage for reliability

The system is designed to be maintainable, extensible, and user-friendly while providing the advanced functionality required for complex project budget management.