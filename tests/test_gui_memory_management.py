"""
Comprehensive tests for GUI memory management and base handler classes.

This module contains tests for:
- Window lifecycle management
- Memory leak prevention
- Base handler functionality
- Resource cleanup
"""

import unittest
import tkinter as tk
import tempfile
import os
import sys
import gc
import weakref
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.window_manager import (
    WindowLifecycleManager, BaseDialog, window_manager, 
    weak_callback_manager, force_gui_cleanup
)
from handlers.base_handler import (
    BaseHandler, ExcelOperationHandler, ValidationResult, OperationResult,
    ValidationResult, OperationResult
)


class TestWindowLifecycleManager(unittest.TestCase):
    """Test window lifecycle management."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.manager = WindowLifecycleManager()
    
    def tearDown(self):
        """Clean up test environment."""
        self.manager.close_all_windows()
        self.root.destroy()
    
    def test_register_window(self):
        """Test window registration."""
        window = tk.Toplevel(self.root)
        window_id = "test_window"
        
        self.manager.register_window(window_id, window)
        
        self.assertIn(window_id, self.manager._open_windows)
        self.assertEqual(len(self.manager.get_open_windows()), 1)
    
    def test_close_window(self):
        """Test window closing."""
        window = tk.Toplevel(self.root)
        window_id = "test_close"
        
        self.manager.register_window(window_id, window)
        result = self.manager.close_window(window_id)
        
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_open_windows()), 0)
    
    def test_close_nonexistent_window(self):
        """Test closing non-existent window."""
        result = self.manager.close_window("nonexistent")
        self.assertFalse(result)
    
    def test_close_all_windows(self):
        """Test closing all windows."""
        windows = []
        for i in range(3):
            window = tk.Toplevel(self.root)
            windows.append(window)
            self.manager.register_window(f"window_{i}", window)
        
        closed_count = self.manager.close_all_windows()
        self.assertEqual(closed_count, 3)
        self.assertEqual(len(self.manager.get_open_windows()), 0)
    
    def test_get_window(self):
        """Test getting window by ID."""
        window = tk.Toplevel(self.root)
        window_id = "test_get"
        
        self.manager.register_window(window_id, window)
        retrieved_window = self.manager.get_window(window_id)
        
        self.assertIsNotNone(retrieved_window)
        self.assertEqual(retrieved_window, window)
    
    def test_get_nonexistent_window(self):
        """Test getting non-existent window."""
        window = self.manager.get_window("nonexistent")
        self.assertIsNone(window)
    
    def test_cleanup_callbacks(self):
        """Test cleanup callbacks."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
        
        window = tk.Toplevel(self.root)
        window_id = "test_callback"
        
        self.manager.register_window(window_id, window)
        self.manager.add_cleanup_callback(window_id, test_callback)
        self.manager.close_window(window_id)
        
        self.assertTrue(callback_called)
    
    def test_memory_stats(self):
        """Test memory statistics."""
        window = tk.Toplevel(self.root)
        self.manager.register_window("test_stats", window)
        
        stats = self.manager.get_memory_stats()
        
        self.assertIn('total_windows', stats)
        self.assertIn('registered_windows', stats)
        self.assertIn('cleanup_callbacks', stats)


class TestBaseDialog(unittest.TestCase):
    """Test base dialog functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
    
    def tearDown(self):
        """Clean up test environment."""
        force_gui_cleanup()
        self.root.destroy()
    
    def test_dialog_creation(self):
        """Test dialog creation."""
        dialog = BaseDialog(self.root, "Test Dialog")
        
        self.assertEqual(dialog.title(), "Test Dialog")
        self.assertEqual(dialog.parent, self.root)
        self.assertIsNotNone(dialog.window_id)
    
    def test_dialog_close(self):
        """Test dialog closing."""
        dialog = BaseDialog(self.root, "Test Close")
        dialog.close()
        
        # Give time for cleanup
        self.root.update()
        self.assertEqual(len(window_manager.get_open_windows()), 0)
    
    def test_dialog_cleanup(self):
        """Test dialog cleanup."""
        cleanup_called = []
        
        class TestDialog(BaseDialog):
            def _on_cleanup(self):
                cleanup_called.append(True)
        
        dialog = TestDialog(self.root, "Test Cleanup")
        dialog.close()
        
        self.assertTrue(cleanup_called)


class TestBaseHandler(unittest.TestCase):
    """Test base handler functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.handler = BaseHandler(self.root)
    
    def tearDown(self):
        """Clean up test environment."""
        self.root.destroy()
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        self.assertEqual(self.handler.parent, self.root)
        self.assertIsNone(self.handler.workbook_path)
        self.assertIsNotNone(self.handler.logger)
    
    def test_validate_workbook_path(self):
        """Test workbook path validation."""
        # Test empty path
        result = self.handler.validate_workbook_path("")
        self.assertFalse(result.valid)
        self.assertIn("Workbook path is required", result.errors)
        
        # Test non-existent file
        result = self.handler.validate_workbook_path("nonexistent.xlsx")
        self.assertFalse(result.valid)
        
        # Test valid path (using temp file)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp.write(b'dummy')
            result = self.handler.validate_workbook_path(tmp.name)
            self.assertTrue(result.valid)
            os.unlink(tmp.name)
    
    def test_validate_required_fields(self):
        """Test required fields validation."""
        data = {'name': 'John', 'age': 30}
        result = self.handler.validate_required_fields(data, ['name', 'age'])
        self.assertTrue(result.valid)
        
        data = {'name': 'John'}
        result = self.handler.validate_required_fields(data, ['name', 'age'])
        self.assertFalse(result.valid)
        self.assertIn("age is required", result.errors)
    
    def test_validate_numeric_fields(self):
        """Test numeric fields validation."""
        data = {'age': 30, 'budget': 1000.5}
        result = self.handler.validate_numeric_fields(data, ['age', 'budget'])
        self.assertTrue(result.valid)
        
        data = {'age': 'invalid', 'budget': 1000}
        result = self.handler.validate_numeric_fields(data, ['age', 'budget'])
        self.assertFalse(result.valid)
        self.assertIn("age must be a valid number", result.errors)
    
    def test_operation_history(self):
        """Test operation history."""
        self.assertEqual(len(self.handler.get_operation_history()), 0)
        
        result = OperationResult(success=True, message="Test")
        self.handler._operation_history.append(result)
        
        history = self.handler.get_operation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].message, "Test")
        
        self.handler.clear_history()
        self.assertEqual(len(self.handler.get_operation_history()), 0)


class TestExcelOperationHandler(unittest.TestCase):
    """Test Excel operation handler."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.xlsx')
        
        # Create test Excel file
        from openpyxl import Workbook
        wb = Workbook()
        wb.save(self.test_file)
        wb.close()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        self.root.destroy()
    
    def test_handler_initialization(self):
        """Test Excel handler initialization."""
        handler = ExcelOperationHandler(self.root, self.test_file)
        self.assertEqual(handler.workbook_path, self.test_file)
    
    def test_open_workbook(self):
        """Test opening workbook."""
        handler = ExcelOperationHandler(self.root, self.test_file)
        
        workbook = handler.open_workbook()
        self.assertIsNotNone(workbook)
        self.assertIsNotNone(handler.get_workbook())
        
        handler.close_workbook()
        self.assertIsNone(handler.get_workbook())
    
    def test_get_sheet_names(self):
        """Test getting sheet names."""
        handler = ExcelOperationHandler(self.root, self.test_file)
        
        sheet_names = handler.get_sheet_names()
        self.assertIsInstance(sheet_names, list)
        self.assertIn('Sheet', sheet_names)
    
    def test_sheet_exists(self):
        """Test sheet existence check."""
        handler = ExcelOperationHandler(self.root, self.test_file)
        
        self.assertTrue(handler.sheet_exists('Sheet'))
        self.assertFalse(handler.sheet_exists('Nonexistent'))


class TestValidationResult(unittest.TestCase):
    """Test validation result functionality."""
    
    def test_initialization(self):
        """Test validation result initialization."""
        result = ValidationResult()
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
    
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult()
        result.add_error("Test error")
        
        self.assertFalse(result.valid)
        self.assertIn("Test error", result.errors)
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        self.assertTrue(result.valid)
        self.assertIn("Test warning", result.warnings)
    
    def test_merge(self):
        """Test merging validation results."""
        result1 = ValidationResult()
        result1.add_error("Error 1")
        result1.add_warning("Warning 1")
        
        result2 = ValidationResult()
        result2.add_error("Error 2")
        result2.add_warning("Warning 2")
        
        merged = result1.merge(result2)
        self.assertFalse(merged.valid)
        self.assertEqual(len(merged.errors), 2)
        self.assertEqual(len(merged.warnings), 2)


class TestOperationResult(unittest.TestCase):
    """Test operation result functionality."""
    
    def test_initialization(self):
        """Test operation result initialization."""
        result = OperationResult()
        self.assertTrue(result.success)
        self.assertEqual(result.message, "")
        self.assertEqual(len(result.errors), 0)
        self.assertIsInstance(result.timestamp, object)
    
    def test_with_data(self):
        """Test operation result with data."""
        data = {'key': 'value'}
        result = OperationResult(success=True, message="Success", data=data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertEqual(result.data, data)


class TestWeakCallbackManager(unittest.TestCase):
    """Test weak callback manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.callback_manager = weak_callback_manager
    
    def test_register_callback(self):
        """Test callback registration."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
        
        self.callback_manager.register_callback("test", test_callback)
        
        result = self.callback_manager.execute_callback("test")
        self.assertTrue(result)
        self.assertTrue(callback_called)
    
    def test_execute_expired_callback(self):
        """Test executing expired callback."""
        class TestClass:
            def callback(self):
                pass
        
        obj = TestClass()
        self.callback_manager.register_callback("expired", obj.callback)
        
        # Delete object to expire callback
        del obj
        gc.collect()
        
        result = self.callback_manager.execute_callback("expired")
        self.assertFalse(result)
    
    def test_cleanup_expired_callbacks(self):
        """Test cleanup of expired callbacks."""
        class TestClass:
            def callback(self):
                pass
        
        obj = TestClass()
        self.callback_manager.register_callback("cleanup", obj.callback)
        
        del obj
        gc.collect()
        
        cleaned = self.callback_manager.cleanup_expired_callbacks()
        self.assertEqual(cleaned, 1)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.xlsx')
        
        # Create test Excel file
        from openpyxl import Workbook
        wb = Workbook()
        wb.save(self.test_file)
        wb.close()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_gui_cleanup()
        self.root.destroy()
    
    def test_complete_workflow(self):
        """Test complete workflow."""
        # Test window management
        dialog = BaseDialog(self.root, "Integration Test")
        self.assertEqual(len(window_manager.get_open_windows()), 1)
        
        # Test handler
        handler = ExcelOperationHandler(self.root, self.test_file)
        
        data = {'partner_number': 'P001', 'partner_name': 'Test', 'budget': 1000}
        validation = handler.validate_input(data)
        self.assertTrue(validation.valid)
        
        # Cleanup
        dialog.close()
        self.assertEqual(len(window_manager.get_open_windows()), 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
