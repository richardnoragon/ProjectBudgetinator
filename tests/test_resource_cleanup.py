"""
Comprehensive tests for resource cleanup and memory management system.

This module contains tests for:
- ExcelManager memory management
- Resource cleanup utilities
- Context managers
- Memory leak detection
- System-wide cleanup
"""

import unittest
import tempfile
import os
import shutil
import sys

from utils.excel_manager import (
    ExcelManager, excel_context, memory_safe_bulk_context,
    memory_tracker
)
from utils.resource_cleanup import (
    ResourceCleanupManager, resource_manager,
    get_system_memory_info, force_system_cleanup, memory_monitor,
    ExcelResourceTracker
)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestExcelManagerMemoryManagement(unittest.TestCase):
    """Test ExcelManager memory management features."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_memory.xlsx")
        
        # Create test file
        excel = ExcelManager.create_excel_file(self.test_file, "Test")
        excel.save()
        excel.close()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking functionality."""
        excel = ExcelManager(self.test_file)
        
        # Test memory info retrieval
        memory_info = excel.get_memory_usage()
        self.assertIsInstance(memory_info, dict)
        self.assertIn('process_memory_mb', memory_info)
        self.assertIn('system_memory_gb', memory_info)
        
        excel.close()
    
    def test_force_close(self):
        """Test force close functionality."""
        excel = ExcelManager(self.test_file)
        
        # Verify file is open
        self.assertIsNotNone(excel.workbook)
        
        # Force close
        excel.force_close()
        
        # Verify cleanup
        self.assertIsNone(excel.workbook)
        self.assertEqual(len(excel._open_files), 0)
    
    def test_context_manager_cleanup(self):
        """Test context manager automatic cleanup."""
        with excel_context(self.test_file) as wb:
            self.assertIsNotNone(wb)
            sheet = wb.active
            sheet['A1'] = "Test"
        
        # Verify workbook is closed
        # This is handled by the context manager
    
    def test_memory_tracker_stats(self):
        """Test memory tracker statistics."""
        stats = memory_tracker.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_open_files', stats)
        self.assertIn('total_memory_mb', stats)


class TestResourceCleanupManager(unittest.TestCase):
    """Test ResourceCleanupManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cleanup_manager = ResourceCleanupManager()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_add_cleanup_callback(self):
        """Test adding cleanup callbacks."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
        
        self.cleanup_manager.add_cleanup_callback(test_callback)
        
        # Trigger cleanup
        self.cleanup_manager._cleanup_all_resources()
        
        self.assertTrue(callback_called)
    
    def test_resource_tracking(self):
        """Test resource tracking functionality."""
        test_file = os.path.join(self.temp_dir, "track_test.xlsx")
        
        # Create and track resource
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        
        # Register for cleanup
        self.cleanup_manager.register_resource(
            test_file, 
            lambda: excel.force_close()
        )
        
        # Verify registration
        self.assertIn(test_file, self.cleanup_manager._resources)
        
        # Cleanup
        self.cleanup_manager._cleanup_all_resources()
        
        # Verify cleanup
        self.assertNotIn(test_file, self.cleanup_manager._resources)
    
    def test_cleanup_on_exception(self):
        """Test cleanup on exception."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
        
        self.cleanup_manager.add_cleanup_callback(test_callback)
        
        # Simulate exception during cleanup
        def failing_cleanup():
            raise ValueError("Test exception")
        
        self.cleanup_manager.add_cleanup_callback(failing_cleanup)
        
        # Should not raise exception
        self.cleanup_manager._cleanup_all_resources()
        
        # Verify callbacks were called
        self.assertTrue(callback_called)


class TestExcelResourceTracker(unittest.TestCase):
    """Test Excel resource tracking."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = ExcelResourceTracker()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_track_excel_file(self):
        """Test tracking Excel files."""
        test_file = os.path.join(self.temp_dir, "track.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        
        # Track file
        self.tracker.track_file(test_file, excel)
        
        # Verify tracking
        self.assertIn(test_file, self.tracker._tracked_files)
        
        # Untrack file
        self.tracker.untrack_file(test_file)
        
        # Verify untracking
        self.assertNotIn(test_file, self.tracker._tracked_files)
        
        excel.close()
    
    def test_get_stats(self):
        """Test getting tracker statistics."""
        test_file = os.path.join(self.temp_dir, "stats.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        
        # Track file
        self.tracker.track_file(test_file, excel)
        
        # Get stats
        stats = self.tracker.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_files', stats)
        self.assertIn('total_memory_mb', stats)
        
        excel.close()


class TestMemoryMonitor(unittest.TestCase):
    """Test memory monitoring functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_system_memory_info(self):
        """Test system memory info retrieval."""
        memory_info = get_system_memory_info()
        
        self.assertIsInstance(memory_info, dict)
        self.assertIn('total_memory_gb', memory_info)
        self.assertIn('used_memory_gb', memory_info)
        self.assertIn('available_memory_gb', memory_info)
        self.assertIn('memory_percent', memory_info)
    
    def test_memory_monitor_decorator(self):
        """Test memory monitor decorator."""
        
        @memory_monitor.monitor_operation("test_operation")
        def test_function():
            return "test_result"
        
        result = test_function()
        self.assertEqual(result, "test_result")
    
    def test_memory_monitor_stats(self):
        """Test memory monitor statistics."""
        stats = memory_monitor.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('operations', stats)
        self.assertIn('total_memory_used', stats)


class TestBulkContextManager(unittest.TestCase):
    """Test bulk context manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create test files
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"bulk_{i}.xlsx")
            excel = ExcelManager.create_excel_file(file_path, f"Sheet{i}")
            excel.save()
            excel.close()
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_bulk_context_manager(self):
        """Test bulk context manager."""
        with memory_safe_bulk_context(self.test_files) as workbooks:
            self.assertEqual(len(workbooks), len(self.test_files))
            
            for file_path, wb in workbooks.items():
                self.assertIn(file_path, self.test_files)
                self.assertIsNotNone(wb)
    
    def test_bulk_context_manager_cleanup(self):
        """Test bulk context manager cleanup."""
        with memory_safe_bulk_context(self.test_files) as workbooks:
            # Process files
            for file_path, wb in workbooks.items():
                sheet = wb.active
                sheet['A1'] = "Bulk Test"
        
        # Verify cleanup (handled by context manager)


class TestResourceManager(unittest.TestCase):
    """Test resource manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_get_manager(self):
        """Test getting resource manager."""
        test_file = os.path.join(self.temp_dir, "manager.xlsx")
        
        manager = resource_manager.get_manager(test_file)
        self.assertIsInstance(manager, ExcelManager)
        
        # Same file should return same manager
        manager2 = resource_manager.get_manager(test_file)
        self.assertIs(manager, manager2)
    
    def test_release_manager(self):
        """Test releasing resource manager."""
        test_file = os.path.join(self.temp_dir, "release.xlsx")
        
        manager = resource_manager.get_manager(test_file)
        
        # Release manager
        resource_manager.release_manager(test_file)
        
        # Should create new manager
        new_manager = resource_manager.get_manager(test_file)
        self.assertIsNot(manager, new_manager)
    
    def test_get_resource_stats(self):
        """Test getting resource statistics."""
        test_file = os.path.join(self.temp_dir, "stats.xlsx")
        
        # Get initial stats
        initial_stats = resource_manager.get_resource_stats()
        
        # Create manager
        _ = resource_manager.get_manager(test_file)
        
        # Get updated stats
        updated_stats = resource_manager.get_resource_stats()
        
        self.assertGreater(updated_stats['total_resources'], initial_stats['total_resources'])


class TestSystemCleanup(unittest.TestCase):
    """Test system-wide cleanup functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_force_system_cleanup(self):
        """Test force system cleanup."""
        test_file = os.path.join(self.temp_dir, "cleanup.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        
        # Force cleanup
        force_system_cleanup()
        
        # Verify cleanup
        stats = memory_tracker.get_stats()
        self.assertEqual(stats['total_open_files'], 0)
    
    def test_cleanup_with_exception(self):
        """Test cleanup handles exceptions gracefully."""
        # This should not raise any exceptions
        force_system_cleanup()


class TestMemoryLeakDetection(unittest.TestCase):
    """Test memory leak detection functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_memory_leak_simulation(self):
        """Test memory leak simulation."""
        test_file = os.path.join(self.temp_dir, "leak.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        excel.close()
        
        # Simulate memory leak
        managers = []
        for i in range(10):
            manager = ExcelManager(test_file)
            managers.append(manager)
            
            if i % 3 == 0:
                # Proper cleanup every 3rd iteration
                manager.force_close()
                managers.clear()
        
        # Force cleanup
        force_system_cleanup()
        
        # Verify cleanup
        stats = memory_tracker.get_stats()
        self.assertEqual(stats['total_open_files'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        force_system_cleanup()
    
    def test_complete_workflow(self):
        """Test complete workflow with all components."""
        test_file = os.path.join(self.temp_dir, "workflow.xlsx")
        
        # Create file
        excel = ExcelManager.create_excel_file(test_file, "Test")
        excel.save()
        excel.close()
        
        # Use context manager
        with excel_context(test_file) as wb:
            sheet = wb.active
            sheet['A1'] = "Integration Test"
        
        # Use resource manager
        _ = resource_manager.get_manager(test_file)
        
        # Get stats
        stats = resource_manager.get_resource_stats()
        self.assertGreater(stats['total_resources'], 0)
        
        # Force cleanup
        force_system_cleanup()
        
        # Verify cleanup
        final_stats = memory_tracker.get_stats()
        self.assertEqual(final_stats['total_open_files'], 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
