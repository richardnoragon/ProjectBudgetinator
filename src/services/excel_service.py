"""
Excel service layer for managing Excel operations.

Provides a clean interface for Excel operations with proper
resource management and error handling.
"""

import logging
from typing import List, Optional
from pathlib import Path
from contextlib import contextmanager

from utils.excel_manager import excel_context
from handlers.base_handler import ValidationResult, OperationResult

logger = logging.getLogger(__name__)

# Constants
FILE_VALIDATION_FAILED = "File validation failed"


class ExcelService:
    """
    Core Excel service for managing Excel file operations.
    
    Provides a clean interface for Excel operations with proper
    resource management and error handling.
    """
    
    def __init__(self):
        """Initialize Excel service."""
        self.logger = logging.getLogger(f"{__name__}.ExcelService")
    
    def validate_file_path(self, file_path: str) -> ValidationResult:
        """
        Validate Excel file path.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not file_path:
            result.add_error("File path is required")
            return result
        
        path = Path(file_path)
        
        if not path.exists():
            result.add_error(f"File does not exist: {file_path}")
        elif path.suffix.lower() not in ['.xlsx', '.xls']:
            result.add_error("File must be an Excel file (.xlsx or .xls)")
        elif not path.is_file():
            result.add_error("Path is not a file")
        
        return result
    
    def get_sheet_names(self, file_path: str) -> OperationResult:
        """
        Get sheet names from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            OperationResult: Result with sheet names
        """
        validation = self.validate_file_path(file_path)
        if not validation.valid:
            return OperationResult(
                success=False,
                message=FILE_VALIDATION_FAILED,
                errors=validation.errors
            )
        
        try:
            with excel_context(file_path) as wb:
                sheet_names = wb.sheetnames
                return OperationResult(
                    success=True,
                    message=f"Found {len(sheet_names)} sheets",
                    data={'sheet_names': sheet_names}
                )
        except Exception as e:
            self.logger.exception(
                f"Error getting sheet names from {file_path}"
            )
            return OperationResult(
                success=False,
                message=f"Error reading file: {str(e)}",
                errors=[str(e)]
            )
    
    def read_sheet_data(
        self,
        file_path: str,
        sheet_name: str,
        start_row: int = 1,
        max_rows: Optional[int] = None
    ) -> OperationResult:
        """
        Read data from a specific sheet.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to read
            start_row: Starting row (1-based)
            max_rows: Maximum rows to read
            
        Returns:
            OperationResult: Result with sheet data
        """
        validation = self.validate_file_path(file_path)
        if not validation.valid:
            return OperationResult(
                success=False,
                message=FILE_VALIDATION_FAILED,
                errors=validation.errors
            )
        
        try:
            with excel_context(file_path) as wb:
                if sheet_name not in wb.sheetnames:
                    return OperationResult(
                        success=False,
                        message=f"Sheet '{sheet_name}' not found",
                        errors=[f"Available sheets: {wb.sheetnames}"]
                    )
                
                sheet = wb[sheet_name]
                
                # Read data
                data = []
                for row_idx, row in enumerate(
                    sheet.iter_rows(values_only=True), 1
                ):
                    if row_idx < start_row:
                        continue
                    if max_rows and len(data) >= max_rows:
                        break
                    data.append(row)
                
                return OperationResult(
                    success=True,
                    message=f"Read {len(data)} rows from '{sheet_name}'",
                    data={'rows': data, 'sheet_name': sheet_name}
                )
        except Exception as e:
            self.logger.exception(
                f"Error reading sheet {sheet_name} from {file_path}"
            )
            return OperationResult(
                success=False,
                message=f"Error reading sheet: {str(e)}",
                errors=[str(e)]
            )
    
    def write_sheet_data(
        self,
        file_path: str,
        sheet_name: str,
        data: List[List],
        headers: Optional[List[str]] = None
    ) -> OperationResult:
        """
        Write data to a specific sheet.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to write to
            data: Data to write (list of rows)
            headers: Optional headers for the sheet
            
        Returns:
            OperationResult: Result of write operation
        """
        validation = self.validate_file_path(file_path)
        if not validation.valid:
            return OperationResult(
                success=False,
                message=FILE_VALIDATION_FAILED,
                errors=validation.errors
            )
        
        try:
            with excel_context(file_path) as wb:
                # Create or get sheet
                if sheet_name in wb.sheetnames:
                    sheet = wb[sheet_name]
                    sheet.delete_rows(1, sheet.max_row)
                else:
                    sheet = wb.create_sheet(sheet_name)
                
                # Write headers if provided
                start_row = 1
                if headers:
                    for col_idx, header in enumerate(headers, 1):
                        sheet.cell(
                            row=1,
                            column=col_idx,
                            value=header
                        )
                    start_row = 2
                
                # Write data
                for row_idx, row_data in enumerate(data, start_row):
                    for col_idx, value in enumerate(row_data, 1):
                        sheet.cell(
                            row=row_idx,
                            column=col_idx,
                            value=value
                        )
                
                # Save changes
                wb.save(file_path)
                
                return OperationResult(
                    success=True,
                    message=f"Written {len(data)} rows to '{sheet_name}'",
                    data={'rows_written': len(data), 'sheet_name': sheet_name}
                )
        except Exception as e:
            self.logger.exception(
                f"Error writing to sheet {sheet_name} in {file_path}"
            )
            return OperationResult(
                success=False,
                message=f"Error writing data: {str(e)}",
                errors=[str(e)]
            )
    
    def create_backup(
        self,
        file_path: str,
        backup_suffix: str = "_backup"
    ) -> OperationResult:
        """
        Create a backup of the Excel file.
        
        Args:
            file_path: Path to original file
            backup_suffix: Suffix for backup file name
            
        Returns:
            OperationResult: Result with backup file path
        """
        validation = self.validate_file_path(file_path)
        if not validation.valid:
            return OperationResult(
                success=False,
                message=FILE_VALIDATION_FAILED,
                errors=validation.errors
            )
        
        try:
            from shutil import copy2
            
            path = Path(file_path)
            backup_path = path.with_stem(path.stem + backup_suffix)
            
            copy2(file_path, backup_path)
            
            return OperationResult(
                success=True,
                message=f"Backup created: {backup_path}",
                data={'backup_path': str(backup_path)}
            )
        except Exception as e:
            self.logger.exception(f"Error creating backup for {file_path}")
            return OperationResult(
                success=False,
                message=f"Error creating backup: {str(e)}",
                errors=[str(e)]
            )


class ExcelContextService:
    """
    Context-based Excel service for managing workbook contexts.
    
    Provides context managers for safe Excel operations with
    automatic resource cleanup.
    """
    
    def __init__(self):
        """Initialize context service."""
        self.logger = logging.getLogger(f"{__name__}.ExcelContextService")
    
    @contextmanager
    def open_workbook(self, file_path: str, read_only: bool = False):
        """
        Context manager for safe workbook operations.
        
        Args:
            file_path: Path to Excel file
            read_only: Whether to open in read-only mode
            
        Yields:
            Workbook: Excel workbook instance
        """
        excel_service = ExcelService()
        validation = excel_service.validate_file_path(file_path)
        
        if not validation.valid:
            raise ValueError(f"Invalid file path: {validation.errors}")
        
        try:
            with excel_context(file_path) as wb:
                self.logger.debug(f"Opened workbook: {file_path}")
                yield wb
        except Exception as e:
            self.logger.exception(f"Error opening workbook: {file_path}")
            raise
    
    def with_workbook(
        self,
        file_path: str,
        operation_func,
        *args,
        **kwargs
    ):
        """
        Execute operation with workbook context.
        
        Args:
            file_path: Path to Excel file
            operation_func: Function to execute with workbook
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Any: Result of operation
        """
        with self.open_workbook(file_path) as wb:
            return operation_func(wb, *args, **kwargs)
