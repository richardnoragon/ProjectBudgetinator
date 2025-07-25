"""
User utilities for ProjectBudgetinator.

This module provides common user object construction and validation patterns
to eliminate code duplication in database operations.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class UserData:
    """Standard user data structure."""
    user_id: Optional[int] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    role: str = "user"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class UserValidationResult:
    """Result of user data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[UserData] = None


class UserConstructor:
    """Handles user object construction with validation and sanitization."""
    
    def __init__(self):
        self.required_fields = ['username', 'email']
        self.optional_fields = ['full_name', 'role', 'is_active', 'preferences']
        self.valid_roles = ['admin', 'manager', 'user', 'viewer']
        
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email must be a non-empty string"
            
        email = email.strip().lower()
        
        # Basic email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, f"Invalid email format: {email}"
            
        return True, None
        
    def validate_username(self, username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not isinstance(username, str):
            return False, "Username must be a non-empty string"
            
        username = username.strip()
        
        # Username validation rules
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
            
        if len(username) > 50:
            return False, "Username must be no more than 50 characters long"
            
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
            
        return True, None
        
    def validate_role(self, role: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user role.
        
        Args:
            role: Role to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not role or not isinstance(role, str):
            return False, "Role must be a non-empty string"
            
        role = role.strip().lower()
        
        if role not in self.valid_roles:
            return False, f"Invalid role: {role}. Valid roles are: {', '.join(self.valid_roles)}"
            
        return True, None
        
    def sanitize_user_data(self, raw_data: Dict[str, Any]) -> UserData:
        """
        Sanitize raw user data into UserData object.
        
        Args:
            raw_data: Raw user data dictionary
            
        Returns:
            Sanitized UserData object
        """
        user_data = UserData()
        
        # Handle user_id
        if 'user_id' in raw_data and raw_data['user_id'] is not None:
            try:
                user_data.user_id = int(raw_data['user_id'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id: {raw_data['user_id']}")
                
        # Handle username
        if 'username' in raw_data:
            user_data.username = str(raw_data['username']).strip()
            
        # Handle email
        if 'email' in raw_data:
            user_data.email = str(raw_data['email']).strip().lower()
            
        # Handle full_name
        if 'full_name' in raw_data:
            user_data.full_name = str(raw_data['full_name']).strip()
            
        # Handle role
        if 'role' in raw_data:
            user_data.role = str(raw_data['role']).strip().lower()
        else:
            user_data.role = 'user'  # Default role
            
        # Handle is_active
        if 'is_active' in raw_data:
            if isinstance(raw_data['is_active'], bool):
                user_data.is_active = raw_data['is_active']
            else:
                # Convert string/int to bool
                user_data.is_active = str(raw_data['is_active']).lower() in ['true', '1', 'yes', 'active']
        else:
            user_data.is_active = True  # Default to active
            
        # Handle timestamps
        for field in ['created_at', 'updated_at', 'last_login']:
            if field in raw_data and raw_data[field] is not None:
                try:
                    if isinstance(raw_data[field], datetime):
                        setattr(user_data, field, raw_data[field])
                    elif isinstance(raw_data[field], str):
                        # Try to parse datetime string
                        dt = datetime.fromisoformat(raw_data[field].replace('Z', '+00:00'))
                        setattr(user_data, field, dt)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid {field}: {raw_data[field]} - {e}")
                    
        # Handle preferences
        if 'preferences' in raw_data:
            if isinstance(raw_data['preferences'], dict):
                user_data.preferences = raw_data['preferences']
            elif isinstance(raw_data['preferences'], str):
                try:
                    user_data.preferences = json.loads(raw_data['preferences'])
                except (json.JSONDecodeError, ValueError):
                    logger.warning(f"Invalid preferences JSON: {raw_data['preferences']}")
                    user_data.preferences = {}
            else:
                user_data.preferences = {}
        else:
            user_data.preferences = {}
            
        return user_data
        
    def validate_user_data(self, user_data: UserData) -> UserValidationResult:
        """
        Validate user data object.
        
        Args:
            user_data: UserData object to validate
            
        Returns:
            UserValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Validate required fields
        for field in self.required_fields:
            value = getattr(user_data, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Required field '{field}' is missing or empty")
                
        # Validate username
        if user_data.username:
            is_valid, error = self.validate_username(user_data.username)
            if not is_valid:
                errors.append(error)
                
        # Validate email
        if user_data.email:
            is_valid, error = self.validate_email(user_data.email)
            if not is_valid:
                errors.append(error)
                
        # Validate role
        if user_data.role:
            is_valid, error = self.validate_role(user_data.role)
            if not is_valid:
                errors.append(error)
                
        # Check for warnings
        if not user_data.full_name:
            warnings.append("Full name is not provided")
            
        if user_data.preferences is None or len(user_data.preferences) == 0:
            warnings.append("No user preferences set")
            
        is_valid = len(errors) == 0
        
        return UserValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_data=user_data if is_valid else None
        )
        
    def construct_user_from_dict(self, raw_data: Dict[str, Any]) -> UserValidationResult:
        """
        Construct and validate user from dictionary data.
        
        Args:
            raw_data: Raw user data dictionary
            
        Returns:
            UserValidationResult with constructed user or errors
        """
        try:
            # Sanitize the data
            user_data = self.sanitize_user_data(raw_data)
            
            # Validate the sanitized data
            validation_result = self.validate_user_data(user_data)
            
            if validation_result.is_valid:
                logger.debug(f"Successfully constructed user: {user_data.username}")
            else:
                logger.warning(f"User validation failed: {validation_result.errors}")
                
            return validation_result
            
        except Exception as e:
            error_msg = f"Error constructing user from data: {str(e)}"
            logger.error(error_msg)
            return UserValidationResult(
                is_valid=False,
                errors=[error_msg],
                warnings=[]
            )
            
    def construct_user_from_db_row(self, db_row: Any) -> UserValidationResult:
        """
        Construct user from database row.
        
        Args:
            db_row: Database row object (dict-like or tuple)
            
        Returns:
            UserValidationResult with constructed user or errors
        """
        try:
            # Convert db_row to dictionary
            if hasattr(db_row, '_asdict'):
                # Named tuple
                raw_data = db_row._asdict()
            elif hasattr(db_row, 'keys'):
                # Dict-like object
                raw_data = dict(db_row)
            elif isinstance(db_row, (list, tuple)):
                # Assume standard column order
                column_names = ['user_id', 'username', 'email', 'full_name', 'role',
                                'is_active', 'created_at', 'updated_at', 'last_login', 'preferences']
                raw_data = dict(zip(column_names[:len(db_row)], db_row))
            else:
                raise ValueError(f"Unsupported db_row type: {type(db_row)}")
                
            return self.construct_user_from_dict(raw_data)
            
        except Exception as e:
            error_msg = f"Error constructing user from database row: {str(e)}"
            logger.error(error_msg)
            return UserValidationResult(
                is_valid=False,
                errors=[error_msg],
                warnings=[]
            )


def create_user_constructor() -> UserConstructor:
    """Create a new UserConstructor instance."""
    return UserConstructor()


def construct_user_safely(raw_data: Dict[str, Any]) -> Tuple[bool, Optional[UserData], List[str]]:
    """
    Safely construct a user from raw data.
    
    Args:
        raw_data: Raw user data dictionary
        
    Returns:
        Tuple of (success, user_data, errors)
    """
    constructor = create_user_constructor()
    result = constructor.construct_user_from_dict(raw_data)
    
    return result.is_valid, result.sanitized_data, result.errors


def construct_users_from_db_results(db_results: List[Any]) -> Tuple[List[UserData], List[str]]:
    """
    Construct multiple users from database results.
    
    Args:
        db_results: List of database row objects
        
    Returns:
        Tuple of (valid_users, errors)
    """
    constructor = create_user_constructor()
    valid_users = []
    all_errors = []
    
    for i, db_row in enumerate(db_results):
        result = constructor.construct_user_from_db_row(db_row)
        
        if result.is_valid and result.sanitized_data:
            valid_users.append(result.sanitized_data)
        else:
            all_errors.extend([f"Row {i}: {error}" for error in result.errors])
            
    return valid_users, all_errors


def update_user_preferences(user_data: UserData, new_preferences: Dict[str, Any]) -> UserData:
    """
    Update user preferences safely.
    
    Args:
        user_data: Existing UserData object
        new_preferences: New preferences to merge
        
    Returns:
        Updated UserData object
    """
    if user_data.preferences is None:
        user_data.preferences = {}
        
    # Merge preferences
    user_data.preferences.update(new_preferences)
    user_data.updated_at = datetime.now()
    
    return user_data


def create_default_user(username: str, email: str, **kwargs) -> UserData:
    """
    Create a user with default values.
    
    Args:
        username: Username
        email: Email address
        **kwargs: Additional user fields
        
    Returns:
        UserData object with defaults
    """
    user_data = UserData(
        username=username,
        email=email,
        full_name=kwargs.get('full_name', ''),
        role=kwargs.get('role', 'user'),
        is_active=kwargs.get('is_active', True),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        preferences=kwargs.get('preferences', {})
    )
    
    return user_data