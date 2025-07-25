"""
Update utilities for ProjectBudgetinator.

This module provides common update functions and patterns to eliminate code duplication
in update operations across the application.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Try to import openpyxl components
try:
    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet
    OPENPYXL_AVAILABLE = True
except ImportError:
    Workbook = None
    Worksheet = None
    OPENPYXL_AVAILABLE = False


class UpdateType(Enum):
    """Types of update operations."""
    CELL_VALUE = "cell_value"
    FORMULA = "formula"
    RANGE = "range"
    WORKSHEET = "worksheet"
    WORKBOOK = "workbook"


@dataclass
class UpdateOperation:
    """Represents a single update operation."""
    operation_type: UpdateType
    target: str  # Cell reference, range, or identifier
    value: Any
    validation_func: Optional[Callable] = None
    rollback_value: Optional[Any] = None


@dataclass
class UpdateResult:
    """Result of an update operation."""
    success: bool
    operations_completed: int
    total_operations: int
    error_message: Optional[str] = None
    failed_operations: Optional[List[UpdateOperation]] = None
    rollback_performed: bool = False


class UpdateBatch:
    """Manages a batch of update operations with rollback capability."""
    
    def __init__(self, name: str = "Update Batch"):
        self.name = name
        self.operations: List[UpdateOperation] = []
        self.completed_operations: List[UpdateOperation] = []
        self.failed_operations: List[UpdateOperation] = []
        
    def add_operation(self, operation: UpdateOperation) -> None:
        """Add an operation to the batch."""
        self.operations.append(operation)
        
    def add_cell_update(self, cell_ref: str, value: Any,
                        validation_func: Optional[Callable] = None) -> None:
        """Add a cell update operation."""
        operation = UpdateOperation(
            operation_type=UpdateType.CELL_VALUE,
            target=cell_ref,
            value=value,
            validation_func=validation_func
        )
        self.add_operation(operation)
        
    def add_formula_update(self, cell_ref: str, formula: str,
                           validation_func: Optional[Callable] = None) -> None:
        """Add a formula update operation."""
        operation = UpdateOperation(
            operation_type=UpdateType.FORMULA,
            target=cell_ref,
            value=formula,
            validation_func=validation_func
        )
        self.add_operation(operation)
        
    def clear(self) -> None:
        """Clear all operations."""
        self.operations.clear()
        self.completed_operations.clear()
        self.failed_operations.clear()


def validate_cell_reference(cell_ref: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a cell reference format.
    
    Args:
        cell_ref: Cell reference string (e.g., 'A1', 'B10')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cell_ref or not isinstance(cell_ref, str):
        return False, "Cell reference must be a non-empty string"
        
    # Basic validation - should contain letters followed by numbers
    import re
    pattern = r'^[A-Z]+[0-9]+$'
    if not re.match(pattern, cell_ref.upper()):
        return False, f"Invalid cell reference format: {cell_ref}"
        
    return True, None


def validate_range_reference(range_ref: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a range reference format.
    
    Args:
        range_ref: Range reference string (e.g., 'A1:B10')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not range_ref or not isinstance(range_ref, str):
        return False, "Range reference must be a non-empty string"
        
    # Check if it's a range (contains ':')
    if ':' in range_ref:
        parts = range_ref.split(':')
        if len(parts) != 2:
            return False, f"Invalid range format: {range_ref}"
            
        # Validate both parts
        for part in parts:
            is_valid, error = validate_cell_reference(part)
            if not is_valid:
                return False, f"Invalid range reference: {error}"
    else:
        # Single cell reference
        return validate_cell_reference(range_ref)
        
    return True, None


def safe_cell_update(worksheet: Any, cell_ref: str, value: Any,
                     validation_func: Optional[Callable] = None) -> Tuple[bool, Optional[str]]:
    """
    Safely update a cell value with validation.
    
    Args:
        worksheet: Worksheet object
        cell_ref: Cell reference (e.g., 'A1')
        value: Value to set
        validation_func: Optional validation function
        
    Returns:
        Tuple of (success, error_message)
    """
    if not OPENPYXL_AVAILABLE:
        return False, "openpyxl library is not available"
        
    try:
        # Validate cell reference
        is_valid, error = validate_cell_reference(cell_ref)
        if not is_valid:
            return False, error
            
        # Get the cell
        cell = worksheet[cell_ref]
        
        # Store original value for potential rollback
        original_value = cell.value
        
        # Apply validation if provided
        if validation_func:
            try:
                if not validation_func(value):
                    return False, f"Validation failed for value: {value}"
            except Exception as e:
                return False, f"Validation error: {str(e)}"
                
        # Update the cell
        cell.value = value
        
        logger.debug(f"Updated cell {cell_ref}: {original_value} -> {value}")
        return True, None
        
    except Exception as e:
        error_msg = f"Failed to update cell {cell_ref}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def safe_formula_update(worksheet: Any, cell_ref: str, formula: str) -> Tuple[bool, Optional[str]]:
    """
    Safely update a cell formula.
    
    Args:
        worksheet: Worksheet object
        cell_ref: Cell reference (e.g., 'A1')
        formula: Formula string (should start with '=')
        
    Returns:
        Tuple of (success, error_message)
    """
    if not OPENPYXL_AVAILABLE:
        return False, "openpyxl library is not available"
        
    try:
        # Validate cell reference
        is_valid, error = validate_cell_reference(cell_ref)
        if not is_valid:
            return False, error
            
        # Validate formula format
        if not formula.startswith('='):
            formula = '=' + formula
            
        # Get the cell
        cell = worksheet[cell_ref]
        
        # Store original value for potential rollback
        original_value = cell.value
        
        # Update the formula
        cell.value = formula
        
        logger.debug(f"Updated formula in cell {cell_ref}: {original_value} -> {formula}")
        return True, None
        
    except Exception as e:
        error_msg = f"Failed to update formula in cell {cell_ref}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def execute_update_batch(worksheet: Any, batch: UpdateBatch) -> UpdateResult:
    """
    Execute a batch of update operations with rollback capability.
    
    Args:
        worksheet: Worksheet object
        batch: UpdateBatch containing operations
        
    Returns:
        UpdateResult with execution details
    """
    if not OPENPYXL_AVAILABLE:
        return UpdateResult(
            success=False,
            operations_completed=0,
            total_operations=len(batch.operations),
            error_message="openpyxl library is not available"
        )
        
    operations_completed = 0
    failed_operations = []
    
    try:
        logger.info(f"Executing update batch '{batch.name}' with {len(batch.operations)} operations")
        
        for operation in batch.operations:
            try:
                # Store original value for rollback
                if operation.operation_type in [UpdateType.CELL_VALUE, UpdateType.FORMULA]:
                    cell = worksheet[operation.target]
                    operation.rollback_value = cell.value
                
                # Execute the operation
                success = False
                error_msg = None
                
                if operation.operation_type == UpdateType.CELL_VALUE:
                    success, error_msg = safe_cell_update(
                        worksheet, operation.target, operation.value, operation.validation_func
                    )
                elif operation.operation_type == UpdateType.FORMULA:
                    success, error_msg = safe_formula_update(
                        worksheet, operation.target, operation.value
                    )
                else:
                    error_msg = f"Unsupported operation type: {operation.operation_type}"
                
                if success:
                    batch.completed_operations.append(operation)
                    operations_completed += 1
                    logger.debug(f"Completed operation: {operation.operation_type} on {operation.target}")
                else:
                    failed_operations.append(operation)
                    batch.failed_operations.append(operation)
                    logger.warning(f"Failed operation: {operation.operation_type} on {operation.target}: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Exception during operation {operation.operation_type} on {operation.target}: {str(e)}"
                logger.error(error_msg)
                failed_operations.append(operation)
                batch.failed_operations.append(operation)
        
        success = len(failed_operations) == 0
        
        result = UpdateResult(
            success=success,
            operations_completed=operations_completed,
            total_operations=len(batch.operations),
            failed_operations=failed_operations if failed_operations else None
        )
        
        if not success:
            result.error_message = f"Failed {len(failed_operations)} out of {len(batch.operations)} operations"
            
        logger.info(f"Update batch '{batch.name}' completed: {operations_completed}/{len(batch.operations)} successful")
        return result
        
    except Exception as e:
        error_msg = f"Critical error during batch execution: {str(e)}"
        logger.error(error_msg)
        return UpdateResult(
            success=False,
            operations_completed=operations_completed,
            total_operations=len(batch.operations),
            error_message=error_msg,
            failed_operations=failed_operations if failed_operations else None
        )


def rollback_update_batch(worksheet: Any, batch: UpdateBatch) -> UpdateResult:
    """
    Rollback completed operations in a batch.
    
    Args:
        worksheet: Worksheet object
        batch: UpdateBatch with completed operations
        
    Returns:
        UpdateResult with rollback details
    """
    if not OPENPYXL_AVAILABLE:
        return UpdateResult(
            success=False,
            operations_completed=0,
            total_operations=len(batch.completed_operations),
            error_message="openpyxl library is not available"
        )
        
    rollback_count = 0
    failed_rollbacks = []
    
    try:
        logger.info(f"Rolling back update batch '{batch.name}' with {len(batch.completed_operations)} operations")
        
        # Rollback in reverse order
        for operation in reversed(batch.completed_operations):
            try:
                if operation.rollback_value is not None:
                    cell = worksheet[operation.target]
                    cell.value = operation.rollback_value
                    rollback_count += 1
                    logger.debug(f"Rolled back operation: {operation.operation_type} on {operation.target}")
                    
            except Exception as e:
                error_msg = f"Failed to rollback operation {operation.operation_type} on {operation.target}: {str(e)}"
                logger.error(error_msg)
                failed_rollbacks.append(operation)
        
        success = len(failed_rollbacks) == 0
        
        result = UpdateResult(
            success=success,
            operations_completed=rollback_count,
            total_operations=len(batch.completed_operations),
            rollback_performed=True
        )
        
        if not success:
            result.error_message = f"Failed to rollback {len(failed_rollbacks)} operations"
            result.failed_operations = failed_rollbacks
            
        logger.info(f"Rollback completed: {rollback_count}/{len(batch.completed_operations)} successful")
        return result
        
    except Exception as e:
        error_msg = f"Critical error during rollback: {str(e)}"
        logger.error(error_msg)
        return UpdateResult(
            success=False,
            operations_completed=rollback_count,
            total_operations=len(batch.completed_operations),
            error_message=error_msg,
            rollback_performed=True
        )


def create_standard_update_batch(name: str, updates: List[Dict[str, Any]]) -> UpdateBatch:
    """
    Create a standard update batch from a list of update dictionaries.
    
    Args:
        name: Name for the batch
        updates: List of dictionaries with 'cell', 'value', and optional 'type', 'validation'
        
    Returns:
        UpdateBatch ready for execution
    """
    batch = UpdateBatch(name)
    
    for update in updates:
        cell_ref = update.get('cell')
        value = update.get('value')
        update_type = update.get('type', 'value')
        validation_func = update.get('validation')
        
        if not cell_ref or value is None:
            logger.warning(f"Skipping invalid update: {update}")
            continue
            
        if update_type == 'formula':
            batch.add_formula_update(cell_ref, value, validation_func)
        else:
            batch.add_cell_update(cell_ref, value, validation_func)
    
    return batch


# Common validation functions
def validate_positive_number(value: Any) -> bool:
    """Validate that value is a positive number."""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_non_negative_number(value: Any) -> bool:
    """Validate that value is a non-negative number."""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False


def validate_percentage(value: Any) -> bool:
    """Validate that value is a valid percentage (0-100)."""
    try:
        num = float(value)
        return 0 <= num <= 100
    except (ValueError, TypeError):
        return False


def validate_non_empty_string(value: Any) -> bool:
    """Validate that value is a non-empty string."""
    return isinstance(value, str) and len(value.strip()) > 0