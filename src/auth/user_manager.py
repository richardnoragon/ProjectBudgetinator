"""
User management functionality.
"""
import logging
from typing import Optional, List
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import User, EnvironmentType
from .password_utils import PasswordUtils


class UserManager:
    """Manages user operations and administration."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize user manager."""
        self.db_manager = db_manager
        self.logger = logging.getLogger("ProjectBudgetinator.user_manager")
    
    def create_user(self, username: str, password: str, email: str = "", full_name: str = "") -> Optional[User]:
        """
        Create a new user.
        
        Args:
            username: Unique username
            password: Plain text password
            email: User email (optional)
            full_name: User's full name (optional)
            
        Returns:
            Created user or None if creation failed
        """
        # Validate input
        if not username or not username.strip():
            self.logger.error("Username cannot be empty")
            return None
        
        username = username.strip()
        
        # Validate password
        is_valid, error_msg = PasswordUtils.validate_password_strength(password)
        if not is_valid:
            self.logger.error(f"Password validation failed: {error_msg}")
            return None
        
        # Check if username already exists
        existing_user = self.db_manager.get_user_by_username(username)
        if existing_user:
            self.logger.error(f"Username already exists: {username}")
            return None
        
        # Hash password
        password_hash = PasswordUtils.hash_password(password)
        
        # Create user object
        user = User(
            username=username,
            password_hash=password_hash,
            email=email.strip(),
            full_name=full_name.strip(),
            created_at=datetime.now(),
            is_active=True
        )
        
        # Save to database
        user_id = self.db_manager.create_user(user)
        if user_id:
            user.user_id = user_id
            self.logger.info(f"Created user: {username}")
            return user
        
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if not username or not password:
            return None
        
        user = self.db_manager.get_user_by_username(username.strip())
        if not user:
            self.logger.warning(f"Authentication failed - user not found: {username}")
            return None
        
        if not user.is_active:
            self.logger.warning(f"Authentication failed - user inactive: {username}")
            return None
        
        if PasswordUtils.verify_password(password, user.password_hash):
            self.logger.info(f"User authenticated successfully: {username}")
            return user
        else:
            self.logger.warning(f"Authentication failed - invalid password: {username}")
            return None
    
    def is_admin_user(self, user: User) -> bool:
        """
        Check if user is the admin user.
        
        Args:
            user: User object to check
            
        Returns:
            True if user is admin
        """
        return user.username.lower() == "admin"
    
    def is_admin_user_by_id(self, user_id: int) -> bool:
        """
        Check if user ID belongs to admin user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is admin
        """
        user = self.db_manager.get_user_by_id(user_id)
        return user is not None and self.is_admin_user(user)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"User not found for password change: {user_id}")
            return False
        
        # Prevent admin password changes
        if self.is_admin_user(user):
            self.logger.warning(f"Password change blocked for admin user: {user.username}")
            return False
        
        # Verify old password
        if not PasswordUtils.verify_password(old_password, user.password_hash):
            self.logger.warning(f"Password change failed - invalid old password: {user.username}")
            return False
        
        # Validate new password
        is_valid, error_msg = PasswordUtils.validate_password_strength(new_password)
        if not is_valid:
            self.logger.error(f"New password validation failed: {error_msg}")
            return False
        
        # Hash new password
        new_password_hash = PasswordUtils.hash_password(new_password)
        
        # Update in database
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE user_id = ?",
                    (new_password_hash, user_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Password changed for user: {user.username}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to change password: {e}")
        
        return False
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        Reset user password (admin function).
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            True if password reset successfully
        """
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"User not found for password reset: {user_id}")
            return False
        
        # Prevent admin password resets
        if self.is_admin_user(user):
            self.logger.warning(f"Password reset blocked for admin user: {user.username}")
            return False
        
        # Validate new password
        is_valid, error_msg = PasswordUtils.validate_password_strength(new_password)
        if not is_valid:
            self.logger.error(f"New password validation failed: {error_msg}")
            return False
        
        # Hash new password
        new_password_hash = PasswordUtils.hash_password(new_password)
        
        # Update in database
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE user_id = ?",
                    (new_password_hash, user_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Password reset for user: {user.username}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to reset password: {e}")
        
        return False
    
    def update_user_info(self, user_id: int, email: Optional[str] = None, full_name: Optional[str] = None) -> bool:
        """
        Update user information.
        
        Args:
            user_id: User ID
            email: New email (optional)
            full_name: New full name (optional)
            
        Returns:
            True if update successful
        """
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"User not found for info update: {user_id}")
            return False
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if email is not None:
                    updates.append("email = ?")
                    params.append(email.strip())
                
                if full_name is not None:
                    updates.append("full_name = ?")
                    params.append(full_name.strip())
                
                if not updates:
                    return True  # Nothing to update
                
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                
                cursor.execute(query, params)
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated info for user: {user.username}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to update user info: {e}")
        
        return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user (soft delete).
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if deactivation successful
        """
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"User not found for deactivation: {user_id}")
            return False
        
        # Prevent admin user deactivation
        if self.is_admin_user(user):
            self.logger.warning(f"Deactivation blocked for admin user: {user.username}")
            return False
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_active = 0 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deactivated user: {user.username}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to deactivate user: {e}")
        
        return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user (hard delete).
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deletion successful
        """
        user = self.db_manager.get_user_by_id(user_id)
        if not user:
            self.logger.error(f"User not found for deletion: {user_id}")
            return False
        
        # Prevent admin user deletion
        if self.is_admin_user(user):
            self.logger.warning(f"Deletion blocked for admin user: {user.username}")
            return False
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete user profiles first (foreign key constraint)
                cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
                
                # Delete user sessions
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
                
                # Delete user
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted user: {user.username}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
        
        return False
    
    def activate_user(self, user_id: int) -> bool:
        """
        Activate a user.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if activation successful
        """
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_active = 1 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Activated user ID: {user_id}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to activate user: {e}")
        
        return False
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.db_manager.get_all_users()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db_manager.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db_manager.get_user_by_username(username)
    
    def has_users(self) -> bool:
        """Check if any users exist."""
        return self.db_manager.has_users()
    
    def create_default_admin_user(self) -> Optional[User]:
        """
        Create default admin user with username 'admin' and password 'pbi'.
        
        Returns:
            Created admin user or None if creation failed
        """
        admin_user = self.create_user(
            username="admin",
            password="pbi",
            email="",
            full_name="Administrator"
        )
        
        if admin_user:
            self.logger.info("Created default admin user")
        else:
            self.logger.error("Failed to create default admin user")
        
        return admin_user
    
    def is_using_default_password(self, user: User) -> bool:
        """
        Check if user is using the default password.
        
        Args:
            user: User to check
            
        Returns:
            True if using default password
        """
        return PasswordUtils.verify_password("pbi", user.password_hash)