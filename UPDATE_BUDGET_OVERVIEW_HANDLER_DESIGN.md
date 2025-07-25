# Update Budget Overview Handler - Design Specification

## Overview

This document provides a comprehensive design specification for implementing `update_budget_overview_handler.py`, which will update the Budget Overview worksheet after partner operations (add/edit) and provide a manual menu option for updates.

## Requirements Summary

- **Primary Function**: Update Budget Overview worksheet with data from partner worksheets (P2, P3, etc.)
- **Trigger Modes**: 
  - Automatic: After partner add/edit operations
  - Manual: Via "Update Budget Overview" menu item
- **Data Mapping**: Copy specific cells from partner worksheets to corresponding rows in Budget Overview
- **Integration**: Seamless integration with existing partner handlers

## Data Mapping Specification

### Source to Target Mapping

For each partner worksheet (P2, P3, P4, etc.):

| Source Cell (Partner WS) | Target Column (Budget Overview) | Description |
|--------------------------|----------------------------------|-------------|
| D4 | B | Partner ID Code |
| D13 | C | Name of Beneficiary |
| D5 | D | Name of Beneficiary |
| D6 | E | Country |
| G13 | F | WP Data Column 1 |
| H13 | G | WP Data Column 2 |
| I13 | H | WP Data Column 3 |
| J13 | I | WP Data Column 4 |
| K13 | J | WP Data Column 5 |
| L13 | K | WP Data Column 6 |
| M13 | L | WP Data Column 7 |
| N13 | M | WP Data Column 8 |
| O13 | N | WP Data Column 9 |
| P13 | O | WP Data Column 10 |
| Q13 | P | WP Data Column 11 |
| R13 | Q | WP Data Column 12 |
| S13 | R | WP Data Column 13 |
| T13 | S | WP Data Column 14 |
| U13 | T | WP Data Column 15 |
| W13 | V | Additional Data 1 (skip U) |
| X13 | W | Additional Data 2 |

### Row Mapping

- **Partner 2 (P2)** → **Budget Overview Row 9**
- **Partner 3 (P3)** → **Budget Overview Row 10**
- **Partner N** → **Budget Overview Row (N + 7)**

## Class Architecture

### UpdateBudgetOverviewHandler Class

```python
class UpdateBudgetOverviewHandler(ExcelOperationHandler):
    """
    Handler for updating Budget Overview worksheet with partner data.
    
    Extends ExcelOperationHandler to provide Excel-specific functionality
    with proper resource management and error handling.
    """
```

### Key Methods

#### Core Methods
- `__init__(parent_window, workbook_path)`: Initialize handler
- `validate_input(data)`: Validate workbook and worksheet existence
- `process(data)`: Main processing logic for updating Budget Overview
- `update_budget_overview(workbook)`: Core update logic
- `get_partner_worksheets(workbook)`: Discover partner worksheets
- `extract_partner_data(worksheet, partner_number)`: Extract data from partner worksheet
- `update_budget_row(budget_ws, partner_data, row_number)`: Update specific row in Budget Overview

#### Integration Methods
- `update_from_partner_operation(workbook, partner_number)`: Called after partner add/edit
- `manual_update(parent_window)`: Called from menu item

#### Utility Methods
- `validate_budget_overview_worksheet(workbook)`: Ensure Budget Overview exists
- `get_partner_number_from_sheet_name(sheet_name)`: Extract partner number
- `create_cell_mapping()`: Define source-to-target cell mappings

## Implementation Details

### Cell Mapping Configuration

```python
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

def get_budget_overview_row(partner_number):
    """Calculate Budget Overview row number from partner number."""
    return partner_number + 7  # P2->Row9, P3->Row10, etc.
```

### Error Handling Strategy

1. **Validation Errors**:
   - Missing Budget Overview worksheet
   - Invalid partner worksheet format
   - Missing required cells

2. **Data Errors**:
   - Malformed partner data
   - Type conversion issues
   - Cell access failures

3. **Integration Errors**:
   - Workbook save failures
   - Concurrent access issues
   - Permission problems

### Logging Strategy

```python
# Structured logging with context
logger = get_structured_logger("handlers.update_budget_overview")

# Log levels:
# - INFO: Operation start/completion, partner counts
# - DEBUG: Cell-by-cell updates, data extraction
# - WARNING: Missing data, fallback operations
# - ERROR: Validation failures, update errors
```

### Progress Tracking

For operations involving multiple partners:
- Use `ProgressContext` for user feedback
- Update progress per partner processed
- Provide cancellation capability
- Show ETA for large operations

## Integration Points

### 1. Add Partner Handler Integration

**File**: `src/handlers/add_partner_handler.py`
**Location**: After line 834 (in `update_version_history` call)

```python
# Add after successful partner addition
from handlers.update_budget_overview_handler import update_budget_overview_after_partner_operation

# Update Budget Overview
try:
    update_budget_overview_after_partner_operation(workbook, partner_info['project_partner_number'])
    logger.info("Budget Overview updated after partner addition")
except Exception as e:
    logger.warning("Failed to update Budget Overview after partner addition", error=str(e))
    # Don't fail the entire operation, just warn user
```

### 2. Edit Partner Handler Integration

**File**: `src/handlers/edit_partner_handler.py`
**Location**: After line 549 (in worksheet update success)

```python
# Add after successful partner edit
from handlers.update_budget_overview_handler import update_budget_overview_after_partner_operation

# Update Budget Overview
try:
    # Extract partner number from worksheet data
    partner_number = self.result.get('project_partner_number')
    if partner_number and hasattr(self, 'worksheet'):
        workbook = self.worksheet.parent
        update_budget_overview_after_partner_operation(workbook, partner_number)
        logger.info("Budget Overview updated after partner edit")
except Exception as e:
    logger.warning("Failed to update Budget Overview after partner edit", error=str(e))
```

### 3. Menu Integration

**File**: `src/gui/menu_setup.py`
**Location**: In modify_menu after line 34

```python
# Add to modify menu
modify_menu.add_separator()
modify_menu.add_command(label="Update Budget Overview", command=app.update_budget_overview)
```

**File**: `src/main.py`
**Location**: Add new method to ProjectBudgetinator class

```python
def update_budget_overview(self):
    """Manually update Budget Overview worksheet."""
    from handlers.update_budget_overview_handler import UpdateBudgetOverviewHandler
    
    # Prompt for workbook if none open
    if self.current_workbook is None:
        # [Standard workbook opening logic]
    
    try:
        handler = UpdateBudgetOverviewHandler(self.root, None)
        result = handler.manual_update(self.current_workbook)
        
        if result.success:
            messagebox.showinfo("Success", "Budget Overview updated successfully!")
        else:
            messagebox.showerror("Error", f"Failed to update Budget Overview: {result.message}")
    except Exception as e:
        messagebox.showerror("Error", f"Update failed: {str(e)}")
```

## Validation Requirements

### Pre-Update Validation
1. Verify "Budget Overview" worksheet exists
2. Check partner worksheets are valid (P2-P20 range)
3. Validate required cells exist in partner worksheets
4. Ensure Budget Overview has sufficient rows

### Data Validation
1. Partner number extraction and validation
2. Cell value type checking and conversion
3. Range boundary validation
4. Data consistency checks

### Post-Update Validation
1. Verify all expected data was written
2. Check for any data corruption
3. Validate formulas still work (if any)
4. Confirm row/column alignment

## Testing Strategy

### Unit Tests
1. **Cell Mapping Tests**: Verify correct source-to-target mapping
2. **Partner Discovery Tests**: Test partner worksheet identification
3. **Data Extraction Tests**: Validate data reading from partner worksheets
4. **Row Calculation Tests**: Verify partner number to row mapping
5. **Error Handling Tests**: Test various failure scenarios

### Integration Tests
1. **Add Partner Integration**: Test automatic update after partner addition
2. **Edit Partner Integration**: Test automatic update after partner edit
3. **Manual Update**: Test menu-driven manual update
4. **Multiple Partners**: Test bulk update scenarios

### Test Data Requirements
- Sample workbook with Budget Overview worksheet
- Multiple partner worksheets (P2, P3, P4)
- Various data types in partner cells
- Edge cases (missing data, malformed worksheets)

## Performance Considerations

### Optimization Strategies
1. **Batch Operations**: Group multiple partner updates
2. **Selective Updates**: Only update changed partners when possible
3. **Cell Access Optimization**: Minimize worksheet read/write operations
4. **Memory Management**: Proper cleanup of Excel objects

### Scalability
- Handle workbooks with 15+ partners efficiently
- Provide progress feedback for long operations
- Support cancellation of long-running updates
- Graceful degradation for large datasets

## Security Considerations

### Input Validation
- Sanitize all data extracted from partner worksheets
- Validate cell references before access
- Check worksheet names for security issues
- Prevent injection attacks through cell data

### File Access
- Use existing SecurityValidator for file operations
- Validate workbook integrity before processing
- Ensure proper file locking during updates
- Handle concurrent access scenarios

## Error Recovery

### Rollback Strategy
1. Create backup of Budget Overview before updates
2. Implement transaction-like behavior
3. Restore original state on critical failures
4. Provide user option to retry or abort

### User Communication
1. Clear error messages for common issues
2. Actionable suggestions for problem resolution
3. Progress indication during long operations
4. Confirmation of successful updates

## Documentation Requirements

### Code Documentation
- Comprehensive docstrings for all methods
- Inline comments for complex logic
- Type hints for all parameters and returns
- Examples in docstrings

### User Documentation
- Menu item usage instructions
- Troubleshooting guide for common issues
- Data mapping explanation
- Integration behavior description

## Future Enhancements

### Potential Extensions
1. **Configurable Mappings**: Allow users to customize cell mappings
2. **Conditional Updates**: Update only when partner data changes
3. **Audit Trail**: Track what was updated and when
4. **Backup Integration**: Automatic backup before updates
5. **Template Support**: Support for different Budget Overview layouts

### API Extensions
1. **Batch Update API**: Update multiple partners in one call
2. **Selective Update API**: Update specific partners only
3. **Validation API**: Pre-validate before update
4. **Status API**: Check update status and history

This design specification provides a comprehensive foundation for implementing the Budget Overview update functionality while maintaining consistency with the existing codebase architecture and patterns.