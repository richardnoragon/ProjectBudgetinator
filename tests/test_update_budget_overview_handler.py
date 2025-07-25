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
        self.assertEqual(get_partner_number_from_sheet_name("P2-ACME"), 2)
        self.assertEqual(get_partner_number_from_sheet_name("P3-University"), 3)
        self.assertEqual(get_partner_number_from_sheet_name("P15-Company"), 15)
        self.assertIsNone(get_partner_number_from_sheet_name("P1-Coordinator"))
        self.assertIsNone(get_partner_number_from_sheet_name("P21-Invalid"))
        self.assertIsNone(get_partner_number_from_sheet_name("Summary"))
        
        # Test backward compatibility with old space format (should fail now)
        self.assertIsNone(get_partner_number_from_sheet_name("P2 ACME"))
        self.assertIsNone(get_partner_number_from_sheet_name("P3 University"))
        
    def test_validate_input_missing_workbook(self):
        """Test validation with missing workbook."""
        result = self.handler.validate_input({})
        self.assertFalse(result.valid)
        self.assertIn("Workbook is required", result.errors)
        
    def test_validate_input_missing_budget_overview(self):
        """Test validation with missing Budget Overview worksheet."""
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["P2-ACME", "P3-University"]
        
        result = self.handler.validate_input({'workbook': mock_workbook})
        self.assertFalse(result.valid)
        self.assertIn("'Budget Overview' worksheet not found", result.errors)
        
    def test_get_partner_worksheets(self):
        """Test partner worksheet discovery."""
        mock_workbook = Mock()
        mock_workbook.sheetnames = [
            "Budget Overview", "P2-ACME", "P3-University",
            "P1-Coordinator", "Summary", "P15-Company"
        ]
        
        partner_sheets = self.handler.get_partner_worksheets(mock_workbook)
        expected = [("P2-ACME", 2), ("P3-University", 3), ("P15-Company", 15)]
        self.assertEqual(partner_sheets, expected)

    @patch('handlers.update_budget_overview_handler.logger')
    def test_update_budget_overview_after_partner_operation(self, mock_logger):
        """Test automatic budget overview update after partner operation."""
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Budget Overview", "P2-ACME"]
        
        # Mock the handler execution
        with patch('handlers.update_budget_overview_handler.UpdateBudgetOverviewHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_result = Mock()
            mock_result.success = True
            mock_handler.execute.return_value = mock_result
            mock_handler_class.return_value = mock_handler
            
            result = update_budget_overview_after_partner_operation(mock_workbook, 2)
            
            self.assertTrue(result)
            mock_handler_class.assert_called_once_with(None, None)
            mock_handler.execute.assert_called_once_with({
                'workbook': mock_workbook,
                'partner_number': 2
            })


if __name__ == '__main__':
    unittest.main()