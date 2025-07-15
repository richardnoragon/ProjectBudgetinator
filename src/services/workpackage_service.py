"""
Workpackage service layer for managing workpackage-related operations.

Provides a clean interface for workpackage data management with proper
validation and business logic separation from GUI code.
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

from handlers.base_handler import ValidationResult, OperationResult
from services.excel_service import ExcelService, ExcelContextService

logger = logging.getLogger(__name__)


class WorkpackageService:
    """
    Core workpackage service for managing workpackage data and operations.
    
    Provides business logic for workpackage management including
    validation, CRUD operations, and data integrity checks.
    """
    
    def __init__(self, excel_service: Optional[ExcelService] = None):
        """
        Initialize workpackage service.
        
        Args:
            excel_service: Excel service instance (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.WorkpackageService")
        self.excel_service = excel_service or ExcelService()
        self.context_service = ExcelContextService()
    
    def _validate_required_fields(self, data: Dict[str, Any],
                                  result: ValidationResult) -> None:
        """Validate required fields."""
        required_fields = ['name', 'description', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                result.add_error(f"{field.replace('_', ' ').title()} is required")
    
    def _validate_name(self, name: str, result: ValidationResult) -> None:
        """Validate name field."""
        if name and len(name) < 3:
            result.add_error("Name must be at least 3 characters long")
        elif name and len(name) > 200:
            result.add_error("Name must be less than 200 characters")
    
    def _validate_dates(self, start_date: str, end_date: str,
                       result: ValidationResult) -> None:
        """Validate date fields."""
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                if end < start:
                    result.add_error("End date must be after start date")
            except ValueError:
                result.add_error("Invalid date format. Use YYYY-MM-DD")
    
    def _validate_budget(self, budget: Any, result: ValidationResult) -> None:
        """Validate budget value."""
        if budget is not None:
            try:
                budget_value = float(budget)
                if budget_value < 0:
                    result.add_error("Budget must be non-negative")
            except (ValueError, TypeError):
                result.add_error("Budget must be a valid number")
    
    def _validate_status(self, status: str, result: ValidationResult) -> None:
        """Validate status field."""
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
        if status and status.lower() not in valid_statuses:
            result.add_error(f"Status must be one of: {', '.join(valid_statuses)}")
    
    def validate_workpackage_data(self, workpackage_data: Dict[str, Any]
                                 ) -> ValidationResult:
        """
        Validate workpackage data.
        
        Args:
            workpackage_data: Dictionary containing workpackage information
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        self._validate_required_fields(workpackage_data, result)
        
        name = workpackage_data.get('name', '').strip()
        self._validate_name(name, result)
        
        start_date = workpackage_data.get('start_date', '').strip()
        end_date = workpackage_data.get('end_date', '').strip()
        self._validate_dates(start_date, end_date, result)
        
        budget = workpackage_data.get('budget')
        self._validate_budget(budget, result)
        
        status = workpackage_data.get('status', '').strip()
        self._validate_status(status, result)
        
        return result
    
    def get_workpackages(self, file_path: str,
                        sheet_name: str = "Workpackages") -> OperationResult:
        """
        Get all workpackages from Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of workpackages sheet
            
        Returns:
            OperationResult: Result with workpackage data
        """
        try:
            # Read sheet data
            result = self.excel_service.read_sheet_data(file_path, sheet_name)
            if not result.success:
                return result
            
            rows = result.data.get('rows', [])
            if not rows:
                return OperationResult(
                    success=True,
                    message="No workpackages found",
                    data={'workpackages': []}
                )
            
            # Assume first row is headers
            if len(rows) < 2:
                return OperationResult(
                    success=True,
                    message="No workpackage data found",
                    data={'workpackages': []}
                )
            
            headers = [str(cell).strip() if cell else '' for cell in rows[0]]
            workpackages = []
            
            # Process data rows
            for row in rows[1:]:
                if not any(row):  # Skip empty rows
                    continue
                
                workpackage = {}
                for idx, header in enumerate(headers):
                    key = header.lower().replace(' ', '_')
                    workpackage[key] = row[idx] if idx < len(row) else None
                
                workpackages.append(workpackage)
            
            return OperationResult(
                success=True,
                message=f"Found {len(workpackages)} workpackages",
                data={'workpackages': workpackages, 'headers': headers}
            )
            
        except Exception as e:
            self.logger.exception(f"Error getting workpackages from {file_path}")
            return OperationResult(
                success=False,
                message=f"Error reading workpackages: {str(e)}",
                errors=[str(e)]
            )
    
    def add_workpackage(self, file_path: str, workpackage_data: Dict[str, Any],
                       sheet_name: str = "Workpackages") -> OperationResult:
        """
        Add a new workpackage to the Excel file.
        
        Args:
            file_path: Path to Excel file
            workpackage_data: Dictionary containing workpackage information
            sheet_name: Name of workpackages sheet
            
        Returns:
            OperationResult: Result of add operation
        """
        # Validate workpackage data
        validation = self.validate_workpackage_data(workpackage_data)
        if not validation.valid:
            return OperationResult(
                success=False,
                message="Validation failed",
                errors=validation.errors
            )
        
        try:
            # Get existing workpackages
            existing_result = self.get_workpackages(file_path, sheet_name)
            if not existing_result.success and "not found" not in str(
                existing_result.message).lower():
                return existing_result
            
            existing_workpackages = existing_result.data.get('workpackages', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Description', 'Start_Date', 'End_Date',
                'Budget', 'Status', 'Responsible_Partner', 'Deliverables'
            ])
            
            # Check for duplicate name
            workpackage_name = workpackage_data.get('name', '').strip()
            for wp in existing_workpackages:
                if wp.get('name', '').strip().lower() == workpackage_name.lower():
                    return OperationResult(
                        success=False,
                        message=f"Workpackage '{workpackage_name}' already exists",
                        errors=["Duplicate workpackage name"]
                    )
            
            # Create new workpackage row
            new_row = []
            for header in headers:
                key = header.lower().replace('_', '_')
                new_row.append(workpackage_data.get(key, ''))
            
            # Add to existing data
            all_data = []
            if existing_workpackages:
                all_data = [[
                    row.get(h.lower().replace('_', '_'), '')
                    for h in headers
                ] for row in existing_workpackages]
            
            all_data.append(new_row)
            
            # Write back to Excel
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Workpackage '{workpackage_name}' added successfully",
                    data={'workpackage': workpackage_data}
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error adding workpackage to {file_path}")
            return OperationResult(
                success=False,
                message=f"Error adding workpackage: {str(e)}",
                errors=[str(e)]
            )
    
    def update_workpackage(self, file_path: str, workpackage_name: str,
                          updated_data: Dict[str, Any],
                          sheet_name: str = "Workpackages") -> OperationResult:
        """
        Update an existing workpackage.
        
        Args:
            file_path: Path to Excel file
            workpackage_name: Name of workpackage to update
            updated_data: Dictionary with updated workpackage information
            sheet_name: Name of workpackages sheet
            
        Returns:
            OperationResult: Result of update operation
        """
        # Validate updated data
        validation = self.validate_workpackage_data(updated_data)
        if not validation.valid:
            return OperationResult(
                success=False,
                message="Validation failed",
                errors=validation.errors
            )
        
        try:
            # Get existing workpackages
            existing_result = self.get_workpackages(file_path, sheet_name)
            if not existing_result.success:
                return existing_result
            
            workpackages = existing_result.data.get('workpackages', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Description', 'Start_Date', 'End_Date',
                'Budget', 'Status', 'Responsible_Partner', 'Deliverables'
            ])
            
            # Find and update workpackage
            workpackage_found = False
            updated_workpackages = []
            
            for wp in workpackages:
                if wp.get('name', '').strip().lower() == workpackage_name.lower():
                    # Update workpackage data
                    updated_wp = wp.copy()
                    for key, value in updated_data.items():
                        updated_wp[key] = value
                    updated_workpackages.append(updated_wp)
                    workpackage_found = True
                else:
                    updated_workpackages.append(wp)
            
            if not workpackage_found:
                return OperationResult(
                    success=False,
                    message=f"Workpackage '{workpackage_name}' not found",
                    errors=["Workpackage not found"]
                )
            
            # Write updated data back to Excel
            all_data = [[
                row.get(h.lower().replace('_', '_'), '')
                for h in headers
            ] for row in updated_workpackages]
            
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Workpackage '{workpackage_name}' updated successfully",
                    data={'workpackage': updated_data}
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error updating workpackage in {file_path}")
            return OperationResult(
                success=False,
                message=f"Error updating workpackage: {str(e)}",
                errors=[str(e)]
            )
    
    def delete_workpackage(self, file_path: str, workpackage_name: str,
                          sheet_name: str = "Workpackages") -> OperationResult:
        """
        Delete a workpackage from the Excel file.
        
        Args:
            file_path: Path to Excel file
            workpackage_name: Name of workpackage to delete
            sheet_name: Name of workpackages sheet
            
        Returns:
            OperationResult: Result of delete operation
        """
        try:
            # Get existing workpackages
            existing_result = self.get_workpackages(file_path, sheet_name)
            if not existing_result.success:
                return existing_result
            
            workpackages = existing_result.data.get('workpackages', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Description', 'Start_Date', 'End_Date',
                'Budget', 'Status', 'Responsible_Partner', 'Deliverables'
            ])
            
            # Filter out the workpackage to delete
            remaining_workpackages = [
                wp for wp in workpackages
                if wp.get('name', '').strip().lower() != workpackage_name.lower()
            ]
            
            if len(remaining_workpackages) == len(workpackages):
                return OperationResult(
                    success=False,
                    message=f"Workpackage '{workpackage_name}' not found",
                    errors=["Workpackage not found"]
                )
            
            # Write remaining data back to Excel
            all_data = [[
                row.get(h.lower().replace('_', '_'), '')
                for h in headers
            ] for row in remaining_workpackages]
            
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Workpackage '{workpackage_name}' deleted successfully"
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error deleting workpackage from {file_path}")
            return OperationResult(
                success=False,
                message=f"Error deleting workpackage: {str(e)}",
                errors=[str(e)]
            )
    
    def get_workpackage_summary(self, file_path: str,
                              sheet_name: str = "Workpackages") -> OperationResult:
        """
        Get summary statistics for workpackages.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of workpackages sheet
            
        Returns:
            OperationResult: Result with summary statistics
        """
        try:
            # Get all workpackages
            result = self.get_workpackages(file_path, sheet_name)
            if not result.success:
                return result
            
            workpackages = result.data.get('workpackages', [])
            
            # Calculate summary statistics
            total_workpackages = len(workpackages)
            
            # Count by status
            statuses = {}
            for wp in workpackages:
                status = wp.get('status', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            # Count by responsible partner
            responsible_partners = {}
            for wp in workpackages:
                partner = wp.get('responsible_partner', 'Unknown')
                responsible_partners[partner] = responsible_partners.get(partner, 0) + 1
            
            # Calculate total budget
            total_budget = 0
            for wp in workpackages:
                try:
                    budget = float(wp.get('budget', 0) or 0)
                    total_budget += budget
                except (ValueError, TypeError):
                    pass
            
            # Calculate duration statistics
            total_duration = 0
            valid_durations = 0
            for wp in workpackages:
                try:
                    start = datetime.strptime(wp.get('start_date', ''), '%Y-%m-%d')
                    end = datetime.strptime(wp.get('end_date', ''), '%Y-%m-%d')
                    duration = (end - start).days
                    if duration >= 0:
                        total_duration += duration
                        valid_durations += 1
                except (ValueError, TypeError):
                    pass
            
            summary = {
                'total_workpackages': total_workpackages,
                'statuses_distribution': statuses,
                'responsible_partners_distribution': responsible_partners,
                'total_budget': total_budget,
                'average_budget': total_budget / total_workpackages if total_workpackages > 0 else 0,
                'average_duration_days': total_duration / valid_durations if valid_durations > 0 else 0
            }
            
            return OperationResult(
                success=True,
                message=f"Summary generated for {total_workpackages} workpackages",
                data=summary
            )
            
        except Exception as e:
            self.logger.exception(
                f"Error generating workpackage summary for {file_path}"
            )
            return OperationResult(
                success=False,
                message=f"Error generating summary: {str(e)}",
                errors=[str(e)]
            )
