"""
Partner service layer for managing partner-related operations.

Provides a clean interface for partner data management with proper
validation and business logic separation from GUI code.
"""

import logging
from typing import Dict, Optional, Any

from handlers.base_handler import ValidationResult, OperationResult
from services.excel_service import ExcelService, ExcelContextService

logger = logging.getLogger(__name__)


class PartnerService:
    """
    Core partner service for managing partner data and operations.
    
    Provides business logic for partner management including
    validation, CRUD operations, and data integrity checks.
    """
    
    def __init__(self, excel_service: Optional[ExcelService] = None):
        """
        Initialize partner service.
        
        Args:
            excel_service: Excel service instance (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.PartnerService")
        self.excel_service = excel_service or ExcelService()
        self.context_service = ExcelContextService()
    
    def _validate_required_fields(self, data: Dict[str, Any],
                                  result: ValidationResult) -> None:
        """Validate required fields."""
        required_fields = ['name', 'role', 'organization']
        for field in required_fields:
            if not data.get(field):
                result.add_error(f"{field.capitalize()} is required")
    
    def _validate_name(self, name: str, result: ValidationResult) -> None:
        """Validate name field."""
        if name and len(name) < 2:
            result.add_error("Name must be at least 2 characters long")
        elif name and len(name) > 100:
            result.add_error("Name must be less than 100 characters")
    
    def _validate_email(self, email: str, result: ValidationResult) -> None:
        """Validate email format."""
        if email and ('@' not in email or
                      '.' not in email.split('@')[-1]):
            result.add_error("Invalid email format")
    
    def _validate_phone(self, phone: str, result: ValidationResult) -> None:
        """Validate phone format."""
        if phone:
            cleaned = phone.replace(' ', '').replace('-', '').replace('+', '')
            if not cleaned.isdigit():
                result.add_error("Invalid phone format")
    
    def _validate_budget(self, budget: Any, result: ValidationResult) -> None:
        """Validate budget value."""
        if budget is not None:
            try:
                budget_value = float(budget)
                if budget_value < 0:
                    result.add_error("Budget must be non-negative")
            except (ValueError, TypeError):
                result.add_error("Budget must be a valid number")
    
    def validate_partner_data(self, partner_data: Dict[str, Any]
                              ) -> ValidationResult:
        """
        Validate partner data.
        
        Args:
            partner_data: Dictionary containing partner information
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        self._validate_required_fields(partner_data, result)
        
        name = partner_data.get('name', '').strip()
        self._validate_name(name, result)
        
        email = partner_data.get('email', '').strip()
        self._validate_email(email, result)
        
        phone = partner_data.get('phone', '').strip()
        self._validate_phone(phone, result)
        
        budget = partner_data.get('budget')
        self._validate_budget(budget, result)
        
        return result
    
    def get_partners(self, file_path: str,
                    sheet_name: str = "Partners") -> OperationResult:
        """
        Get all partners from Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result with partner data
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
                    message="No partners found",
                    data={'partners': []}
                )
            
            # Assume first row is headers
            if len(rows) < 2:
                return OperationResult(
                    success=True,
                    message="No partner data found",
                    data={'partners': []}
                )
            
            headers = [str(cell).strip() if cell else '' for cell in rows[0]]
            partners = []
            
            # Process data rows
            for row in rows[1:]:
                if not any(row):  # Skip empty rows
                    continue
                
                partner = {}
                for idx, header in enumerate(headers):
                    key = header.lower().replace(' ', '_')
                    partner[key] = row[idx] if idx < len(row) else None
                
                partners.append(partner)
            
            return OperationResult(
                success=True,
                message=f"Found {len(partners)} partners",
                data={'partners': partners, 'headers': headers}
            )
            
        except Exception as e:
            self.logger.exception(f"Error getting partners from {file_path}")
            return OperationResult(
                success=False,
                message=f"Error reading partners: {str(e)}",
                errors=[str(e)]
            )
    
    def add_partner(self, file_path: str, partner_data: Dict[str, Any],
                   sheet_name: str = "Partners") -> OperationResult:
        """
        Add a new partner to the Excel file.
        
        Args:
            file_path: Path to Excel file
            partner_data: Dictionary containing partner information
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result of add operation
        """
        # Validate partner data
        validation = self.validate_partner_data(partner_data)
        if not validation.valid:
            return OperationResult(
                success=False,
                message="Validation failed",
                errors=validation.errors
            )
        
        try:
            # Get existing partners
            existing_result = self.get_partners(file_path, sheet_name)
            if not existing_result.success and "not found" not in str(
                existing_result.message).lower():
                return existing_result
            
            existing_partners = existing_result.data.get('partners', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Role', 'Organization', 'Email', 'Phone', 'Budget'
            ])
            
            # Check for duplicate name
            partner_name = partner_data.get('name', '').strip()
            for partner in existing_partners:
                if partner.get('name', '').strip().lower() == partner_name.lower():
                    return OperationResult(
                        success=False,
                        message=f"Partner '{partner_name}' already exists",
                        errors=["Duplicate partner name"]
                    )
            
            # Create new partner row
            new_row = []
            for header in headers:
                key = header.lower().replace(' ', '_')
                new_row.append(partner_data.get(key, ''))
            
            # Add to existing data
            all_data = []
            if existing_partners:
                all_data = [[
                    row.get(h.lower().replace(' ', '_'), '')
                    for h in headers
                ] for row in existing_partners]
            
            all_data.append(new_row)
            
            # Write back to Excel
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Partner '{partner_name}' added successfully",
                    data={'partner': partner_data}
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error adding partner to {file_path}")
            return OperationResult(
                success=False,
                message=f"Error adding partner: {str(e)}",
                errors=[str(e)]
            )
    
    def update_partner(self, file_path: str, partner_name: str,
                      updated_data: Dict[str, Any],
                      sheet_name: str = "Partners") -> OperationResult:
        """
        Update an existing partner.
        
        Args:
            file_path: Path to Excel file
            partner_name: Name of partner to update
            updated_data: Dictionary with updated partner information
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result of update operation
        """
        # Validate updated data
        validation = self.validate_partner_data(updated_data)
        if not validation.valid:
            return OperationResult(
                success=False,
                message="Validation failed",
                errors=validation.errors
            )
        
        try:
            # Get existing partners
            existing_result = self.get_partners(file_path, sheet_name)
            if not existing_result.success:
                return existing_result
            
            partners = existing_result.data.get('partners', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Role', 'Organization', 'Email', 'Phone', 'Budget'
            ])
            
            # Find and update partner
            partner_found = False
            updated_partners = []
            
            for partner in partners:
                if partner.get('name', '').strip().lower() == partner_name.lower():
                    # Update partner data
                    updated_partner = partner.copy()
                    for key, value in updated_data.items():
                        updated_partner[key] = value
                    updated_partners.append(updated_partner)
                    partner_found = True
                else:
                    updated_partners.append(partner)
            
            if not partner_found:
                return OperationResult(
                    success=False,
                    message=f"Partner '{partner_name}' not found",
                    errors=["Partner not found"]
                )
            
            # Write updated data back to Excel
            all_data = [[
                row.get(h.lower().replace(' ', '_'), '')
                for h in headers
            ] for row in updated_partners]
            
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Partner '{partner_name}' updated successfully",
                    data={'partner': updated_data}
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error updating partner in {file_path}")
            return OperationResult(
                success=False,
                message=f"Error updating partner: {str(e)}",
                errors=[str(e)]
            )
    
    def delete_partner(self, file_path: str, partner_name: str,
                      sheet_name: str = "Partners") -> OperationResult:
        """
        Delete a partner from the Excel file.
        
        Args:
            file_path: Path to Excel file
            partner_name: Name of partner to delete
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result of delete operation
        """
        try:
            # Get existing partners
            existing_result = self.get_partners(file_path, sheet_name)
            if not existing_result.success:
                return existing_result
            
            partners = existing_result.data.get('partners', [])
            headers = existing_result.data.get('headers', [
                'Name', 'Role', 'Organization', 'Email', 'Phone', 'Budget'
            ])
            
            # Filter out the partner to delete
            remaining_partners = [
                partner for partner in partners
                if partner.get('name', '').strip().lower() != partner_name.lower()
            ]
            
            if len(remaining_partners) == len(partners):
                return OperationResult(
                    success=False,
                    message=f"Partner '{partner_name}' not found",
                    errors=["Partner not found"]
                )
            
            # Write remaining data back to Excel
            all_data = [[
                row.get(h.lower().replace(' ', '_'), '')
                for h in headers
            ] for row in remaining_partners]
            
            write_result = self.excel_service.write_sheet_data(
                file_path, sheet_name, all_data, headers
            )
            
            if write_result.success:
                return OperationResult(
                    success=True,
                    message=f"Partner '{partner_name}' deleted successfully"
                )
            else:
                return write_result
                
        except Exception as e:
            self.logger.exception(f"Error deleting partner from {file_path}")
            return OperationResult(
                success=False,
                message=f"Error deleting partner: {str(e)}",
                errors=[str(e)]
            )
    
    def search_partners(self, file_path: str, search_term: str,
                       sheet_name: str = "Partners") -> OperationResult:
        """
        Search for partners by name, role, or organization.
        
        Args:
            file_path: Path to Excel file
            search_term: Term to search for
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result with matching partners
        """
        try:
            # Get all partners
            result = self.get_partners(file_path, sheet_name)
            if not result.success:
                return result
            
            partners = result.data.get('partners', [])
            
            if not search_term.strip():
                return OperationResult(
                    success=True,
                    message="Showing all partners",
                    data={'partners': partners, 'search_term': ''}
                )
            
            search_term_lower = search_term.lower().strip()
            matching_partners = []
            
            for partner in partners:
                # Search in name, role, and organization
                searchable_fields = [
                    partner.get('name', ''),
                    partner.get('role', ''),
                    partner.get('organization', ''),
                    partner.get('email', '')
                ]
                
                if any(search_term_lower in str(field).lower()
                      for field in searchable_fields if field):
                    matching_partners.append(partner)
            
            return OperationResult(
                success=True,
                message=f"Found {len(matching_partners)} matching partners",
                data={
                    'partners': matching_partners,
                    'search_term': search_term,
                    'total_found': len(matching_partners)
                }
            )
            
        except Exception as e:
            self.logger.exception(f"Error searching partners in {file_path}")
            return OperationResult(
                success=False,
                message=f"Error searching partners: {str(e)}",
                errors=[str(e)]
            )
    
    def get_partner_summary(self, file_path: str,
                          sheet_name: str = "Partners") -> OperationResult:
        """
        Get summary statistics for partners.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of partners sheet
            
        Returns:
            OperationResult: Result with summary statistics
        """
        try:
            # Get all partners
            result = self.get_partners(file_path, sheet_name)
            if not result.success:
                return result
            
            partners = result.data.get('partners', [])
            
            # Calculate summary statistics
            total_partners = len(partners)
            
            # Count by role
            roles = {}
            for partner in partners:
                role = partner.get('role', 'Unknown')
                roles[role] = roles.get(role, 0) + 1
            
            # Count by organization
            organizations = {}
            for partner in partners:
                org = partner.get('organization', 'Unknown')
                organizations[org] = organizations.get(org, 0) + 1
            
            # Calculate total budget
            total_budget = 0
            for partner in partners:
                try:
                    budget = float(partner.get('budget', 0) or 0)
                    total_budget += budget
                except (ValueError, TypeError):
                    pass
            
            summary = {
                'total_partners': total_partners,
                'roles_distribution': roles,
                'organizations_distribution': organizations,
                'total_budget': total_budget,
                'average_budget': total_budget / total_partners if total_partners > 0 else 0
            }
            
            return OperationResult(
                success=True,
                message=f"Summary generated for {total_partners} partners",
                data=summary
            )
            
        except Exception as e:
            self.logger.exception(
                f"Error generating partner summary for {file_path}"
            )
            return OperationResult(
                success=False,
                message=f"Error generating summary: {str(e)}",
                errors=[str(e)]
            )
