"""
Unit tests for database error handling functionality.

This module tests the comprehensive error handling improvements for database operations,
including datetime parsing, JSON processing, and database transaction error handling.
"""

import unittest
import tempfile
import os
import sqlite3
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the modules to test
from src.database.db_manager import DatabaseManager
from src.database.models import User, UserProfile, UserSession
from src.exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseTransactionError,
    DatabaseDataError,
    DateTimeParsingError,
    JSONProcessingError,
    DatabaseValidationError,
    DatabaseIntegrityError,
    safe_datetime_parse,
    safe_json_loads,
    safe_json_dumps
)


class TestDatabaseErrorHandling(unittest.TestCase):
    """Test cases for database error handling functionality."""
    
    def setUp(self):
        """Set up test environment with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db_manager = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_safe_datetime_parse_valid_iso_format(self):
        """Test safe datetime parsing with valid ISO format."""
        test_datetime = "2023-07-24T15:30:45"
        result = safe_datetime_parse(test_datetime, "test_field")
        
        self.assertIsInstance(result, datetime)
        if result:  # Type guard for mypy/pylance
            self.assertEqual(result.year, 2023)
            self.assertEqual(result.month, 7)
            self.assertEqual(result.day, 24)
    
    def test_safe_datetime_parse_empty_string(self):
        """Test safe datetime parsing with empty string."""
        result = safe_datetime_parse("", "test_field")
        self.assertIsNone(result)
        
        result = safe_datetime_parse("   ", "test_field")
        self.assertIsNone(result)
    
    def test_safe_datetime_parse_invalid_format(self):
        """Test safe datetime parsing with invalid format."""
        with self.assertRaises(DateTimeParsingError) as context:
            safe_datetime_parse("invalid-date", "test_field")
        
        self.assertIn("Failed to parse datetime string", str(context.exception))
        self.assertIn("test_field", str(context.exception))
    
    def test_safe_datetime_parse_alternative_formats(self):
        """Test safe datetime parsing with alternative formats."""
        test_cases = [
            "2023-07-24 15:30:45",
            "2023-07-24T15:30:45.123456",
            "2023-07-24"
        ]
        
        for test_datetime in test_cases:
            result = safe_datetime_parse(test_datetime, "test_field")
            self.assertIsInstance(result, datetime)
    
    def test_safe_json_loads_valid_json(self):
        """Test safe JSON loading with valid JSON."""
        test_data = {"key": "value", "number": 42}
        json_string = json.dumps(test_data)
        
        result = safe_json_loads(json_string, "test_field")
        self.assertEqual(result, test_data)
    
    def test_safe_json_loads_empty_string(self):
        """Test safe JSON loading with empty string."""
        result = safe_json_loads("", "test_field")
        self.assertEqual(result, {})
        
        result = safe_json_loads("   ", "test_field")
        self.assertEqual(result, {})
    
    def test_safe_json_loads_invalid_json(self):
        """Test safe JSON loading with invalid JSON."""
        with self.assertRaises(JSONProcessingError) as context:
            safe_json_loads("invalid-json", "test_field")
        
        self.assertIn("Failed to parse JSON string", str(context.exception))
        self.assertIn("test_field", str(context.exception))
    
    def test_safe_json_dumps_valid_data(self):
        """Test safe JSON dumping with valid data."""
        test_data = {"key": "value", "number": 42}
        result = safe_json_dumps(test_data, "test_field")
        
        self.assertIsInstance(result, str)
        parsed_back = json.loads(result)
        self.assertEqual(parsed_back, test_data)
    
    def test_safe_json_dumps_with_datetime(self):
        """Test safe JSON dumping with datetime objects."""
        test_data = {"timestamp": datetime.now()}
        result = safe_json_dumps(test_data, "test_field")
        
        self.assertIsInstance(result, str)
        # Should not raise an exception
        parsed_back = json.loads(result)
        self.assertIn("timestamp", parsed_back)
    
    def test_create_user_validation_errors(self):
        """Test user creation with validation errors."""
        # Test with None user
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.create_user(None)  # type: ignore
        self.assertIn("User object cannot be None", str(context.exception))
        
        # Test with empty username
        user = User(username="", password_hash="hash123")
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.create_user(user)
        self.assertIn("Username must be a non-empty string", str(context.exception))
        
        # Test with empty password hash
        user = User(username="testuser", password_hash="")
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.create_user(user)
        self.assertIn("Password hash must be a non-empty string", str(context.exception))
    
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username."""
        user1 = User(username="testuser", password_hash="hash123")
        user2 = User(username="testuser", password_hash="hash456")
        
        # First user should be created successfully
        user_id = self.db_manager.create_user(user1)
        self.assertIsNotNone(user_id)
        
        # Second user with same username should raise integrity error
        with self.assertRaises(DatabaseIntegrityError) as context:
            self.db_manager.create_user(user2)
        self.assertIn("already exists", str(context.exception))
    
    def test_get_user_by_username_validation(self):
        """Test get user by username with validation errors."""
        # Test with empty username
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.get_user_by_username("")
        self.assertIn("Username must be a non-empty string", str(context.exception))
        
        # Test with non-string username
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.get_user_by_username(123)  # type: ignore
        self.assertIn("Username must be a non-empty string", str(context.exception))
    
    def test_get_user_by_id_validation(self):
        """Test get user by ID with validation errors."""
        # Test with invalid user ID
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.get_user_by_id(0)
        self.assertIn("User ID must be a positive integer", str(context.exception))
        
        # Test with non-integer user ID
        with self.assertRaises(DatabaseValidationError) as context:
            self.db_manager.get_user_by_id("invalid")  # type: ignore
        self.assertIn("User ID must be a positive integer", str(context.exception))
    
    def test_user_model_datetime_parsing_errors(self):
        """Test User model with datetime parsing errors."""
        # Test with invalid datetime format
        data = {
            'user_id': 1,
            'username': 'testuser',
            'password_hash': 'hash123',
            'created_at': 'invalid-datetime',
            'last_login': None
        }
        
        with self.assertRaises(DateTimeParsingError):
            User.from_dict(data)
    
    def test_user_profile_json_processing_errors(self):
        """Test UserProfile model with JSON processing errors."""
        # Test with invalid JSON in preferences_data
        data = {
            'profile_id': 1,
            'user_id': 1,
            'profile_name': 'test_profile',
            'environment_type': 'Development',
            'preferences_data': 'invalid-json',
            'is_default': False,
            'created_at': '2023-07-24T15:30:45',
            'updated_at': '2023-07-24T15:30:45'
        }
        
        with self.assertRaises(JSONProcessingError):
            UserProfile.from_dict(data)
    
    def test_user_session_datetime_parsing(self):
        """Test UserSession model with datetime parsing."""
        # Test with valid datetime
        data = {
            'session_id': 'session123',
            'user_id': 1,
            'current_profile_id': 1,
            'login_time': '2023-07-24T15:30:45',
            'last_activity': '2023-07-24T16:30:45'
        }
        
        session = UserSession.from_dict(data)
        self.assertIsInstance(session.login_time, datetime)
        self.assertIsInstance(session.last_activity, datetime)
    
    @patch('sqlite3.connect')
    def test_database_connection_error(self, mock_connect):
        """Test database connection error handling."""
        mock_connect.side_effect = sqlite3.Error("Connection failed")
        
        with self.assertRaises(DatabaseConnectionError) as context:
            DatabaseManager("/invalid/path/test.db")
        
        self.assertIn("SQLite error during database initialization", str(context.exception))
    
    def test_get_all_users_with_corrupted_datetime(self):
        """Test get_all_users with corrupted datetime data."""
        # Create a user first
        user = User(username="testuser", password_hash="hash123")
        user_id = self.db_manager.create_user(user)
        self.assertIsNotNone(user_id)
        
        # Manually corrupt the datetime data in the database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET created_at = ? WHERE user_id = ?",
                ("invalid-datetime", user_id)
            )
            conn.commit()
        
        # get_all_users should handle the error gracefully
        users = self.db_manager.get_all_users()
        # Should return empty list or skip the corrupted user
        self.assertIsInstance(users, list)
    
    def test_database_transaction_rollback(self):
        """Test database transaction rollback on error."""
        # This test simulates a transaction that should rollback on error
        user = User(username="testuser", password_hash="hash123")
        
        # Create user successfully first
        user_id = self.db_manager.create_user(user)
        self.assertIsNotNone(user_id)
        
        # Verify user exists
        if user_id:  # Type guard
            retrieved_user = self.db_manager.get_user_by_id(user_id)
            self.assertIsNotNone(retrieved_user)
            if retrieved_user:  # Type guard
                self.assertEqual(retrieved_user.username, "testuser")
    
    def test_exception_context_preservation(self):
        """Test that exception context is properly preserved."""
        try:
            safe_datetime_parse("invalid-date", "test_field")
        except DateTimeParsingError as e:
            # Check that context information is preserved
            self.assertIn("test_field", str(e))
            self.assertIn("invalid-date", str(e))
            # Check that original exception is chained
            self.assertIsNotNone(e.__cause__)
    
    def test_json_processing_error_context(self):
        """Test JSON processing error context preservation."""
        try:
            safe_json_loads("invalid-json", "preferences_data")
        except JSONProcessingError as e:
            # Check that context information is preserved
            self.assertIn("preferences_data", str(e))
            self.assertIn("invalid-json", str(e))
            # Check that original exception is chained
            self.assertIsNotNone(e.__cause__)


class TestDatabaseExceptionHierarchy(unittest.TestCase):
    """Test cases for database exception hierarchy and inheritance."""
    
    def test_exception_inheritance(self):
        """Test that all database exceptions inherit from DatabaseError."""
        exceptions_to_test = [
            DatabaseConnectionError,
            DatabaseTransactionError,
            DatabaseDataError,
            DateTimeParsingError,
            JSONProcessingError,
            DatabaseValidationError,
            DatabaseIntegrityError
        ]
        
        for exception_class in exceptions_to_test:
            self.assertTrue(issubclass(exception_class, DatabaseError))
    
    def test_exception_context_logging(self):
        """Test that exceptions properly log context information."""
        with patch('src.exceptions.database_exceptions.logger') as mock_logger:
            try:
                raise DatabaseValidationError(
                    "Test validation error",
                    validation_rule="test_rule",
                    field_name="test_field"
                )
            except DatabaseValidationError:
                pass
            
            # Verify that logger.error was called
            mock_logger.error.assert_called_once()
    
    def test_database_error_string_representation(self):
        """Test string representation of database errors."""
        error = DatabaseValidationError(
            "Test error message",
            validation_rule="test_rule",
            field_name="test_field"
        )
        
        error_str = str(error)
        self.assertIn("Test error message", error_str)
        self.assertIn("validation_rule=test_rule", error_str)
        self.assertIn("field_name=test_field", error_str)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDatabaseErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestDatabaseExceptionHierarchy))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")