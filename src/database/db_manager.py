"""
Database manager for user administration system.
"""
import sqlite3
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import User, UserProfile, UserSession
from utils.config_utils import get_app_directory
from ..exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseTransactionError,
    DatabaseDataError,
    DateTimeParsingError,
    DatabaseValidationError,
    DatabaseIntegrityError,
    handle_database_exception,
    safe_datetime_parse
)


class DatabaseManager:
    """Manages SQLite database operations for user administration."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager."""
        if db_path is None:
            db_dir = os.path.join(get_app_directory(), "database")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "users.db")
        
        self.db_path = db_path
        self.logger = logging.getLogger("ProjectBudgetinator.database")
        self._init_database()
    
    @handle_database_exception
    def _init_database(self):
        """Initialize database tables with comprehensive error handling."""
        try:
            # Validate database path
            if not self.db_path:
                raise DatabaseValidationError(
                    "Database path is not set",
                    validation_rule="non_empty_path"
                )
            
            # Ensure database directory exists
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except OSError as e:
                    raise DatabaseConnectionError(
                        f"Failed to create database directory: {db_dir}",
                        db_path=self.db_path,
                        operation="create_directory"
                    ) from e
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT,
                        full_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Create user_profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        profile_name TEXT NOT NULL,
                        environment_type TEXT,
                        preferences_data TEXT,
                        is_default BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                        UNIQUE(user_id, profile_name)
                    )
                """)
                
                # Create user_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        current_profile_id INTEGER,
                        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                        FOREIGN KEY (current_profile_id) REFERENCES user_profiles (profile_id) ON DELETE SET NULL
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            raise DatabaseConnectionError(
                f"SQLite error during database initialization: {str(e)}",
                db_path=self.db_path,
                operation="initialize_database"
            ) from e
        except OSError as e:
            raise DatabaseConnectionError(
                f"File system error during database initialization: {str(e)}",
                db_path=self.db_path,
                operation="initialize_database"
            ) from e
    
    # User management methods
    @handle_database_exception
    def create_user(self, user: User) -> Optional[int]:
        """Create a new user and return user_id with comprehensive validation."""
        # Input validation
        if not user:
            raise DatabaseValidationError(
                "User object cannot be None",
                validation_rule="non_null_object",
                field_name="user"
            )
        
        if not user.username or not isinstance(user.username, str):
            raise DatabaseValidationError(
                "Username must be a non-empty string",
                validation_rule="non_empty_string",
                field_name="username",
                invalid_value=user.username
            )
        
        if not user.password_hash or not isinstance(user.password_hash, str):
            raise DatabaseValidationError(
                "Password hash must be a non-empty string",
                validation_rule="non_empty_string",
                field_name="password_hash"
            )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, full_name, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user.username,
                    user.password_hash,
                    user.email,
                    user.full_name,
                    user.created_at or datetime.now(),
                    user.is_active
                ))
                user_id = cursor.lastrowid
                conn.commit()
                self.logger.info(f"Created user: {user.username} (ID: {user_id})")
                return user_id
                
        except sqlite3.IntegrityError as e:
            # Handle constraint violations gracefully
            if "UNIQUE constraint failed" in str(e):
                self.logger.warning(f"User creation failed - username already exists: {user.username}")
                raise DatabaseIntegrityError(
                    f"Username '{user.username}' already exists",
                    constraint_type="UNIQUE",
                    table_name="users",
                    field_name="username",
                    username=user.username
                ) from e
            else:
                raise DatabaseIntegrityError(
                    f"Database integrity constraint violated: {str(e)}",
                    table_name="users",
                    username=user.username
                ) from e
        except sqlite3.Error as e:
            raise DatabaseTransactionError(
                f"Database error while creating user: {str(e)}",
                transaction_type="INSERT",
                table_name="users",
                username=user.username
            ) from e
    
    @handle_database_exception
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username with comprehensive error handling."""
        # Input validation
        if not username or not isinstance(username, str):
            raise DatabaseValidationError(
                "Username must be a non-empty string",
                validation_rule="non_empty_string",
                field_name="username",
                invalid_value=username
            )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
                row = cursor.fetchone()
                
                if row:
                    # Safe datetime parsing with error handling
                    created_at = safe_datetime_parse(row['created_at'], 'created_at') if row['created_at'] else None
                    last_login = safe_datetime_parse(row['last_login'], 'last_login') if row['last_login'] else None
                    
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        password_hash=row['password_hash'],
                        email=row['email'] or "",
                        full_name=row['full_name'] or "",
                        created_at=created_at,
                        last_login=last_login,
                        is_active=bool(row['is_active'])
                    )
                return None
                
        except sqlite3.Error as e:
            raise DatabaseTransactionError(
                f"Database error while retrieving user by username: {str(e)}",
                transaction_type="SELECT",
                table_name="users",
                username=username
            ) from e
        except DateTimeParsingError:
            # Re-raise datetime parsing errors as they already have proper context
            raise
    
    @handle_database_exception
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with comprehensive error handling."""
        # Input validation
        if not isinstance(user_id, int) or user_id <= 0:
            raise DatabaseValidationError(
                "User ID must be a positive integer",
                validation_rule="positive_integer",
                field_name="user_id",
                invalid_value=user_id
            )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ? AND is_active = 1", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    # Safe datetime parsing with error handling
                    created_at = safe_datetime_parse(row['created_at'], 'created_at') if row['created_at'] else None
                    last_login = safe_datetime_parse(row['last_login'], 'last_login') if row['last_login'] else None
                    
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        password_hash=row['password_hash'],
                        email=row['email'] or "",
                        full_name=row['full_name'] or "",
                        created_at=created_at,
                        last_login=last_login,
                        is_active=bool(row['is_active'])
                    )
                return None
                
        except sqlite3.Error as e:
            raise DatabaseTransactionError(
                f"Database error while retrieving user by ID: {str(e)}",
                transaction_type="SELECT",
                table_name="users",
                user_id=user_id
            ) from e
        except DateTimeParsingError:
            # Re-raise datetime parsing errors as they already have proper context
            raise
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(), user_id)
                )
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update last login: {e}")
            return False
    
    @handle_database_exception
    def get_all_users(self) -> List[User]:
        """Get all active users with comprehensive error handling."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY username")
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    try:
                        # Safe datetime parsing with error handling
                        created_at = safe_datetime_parse(row['created_at'], 'created_at') if row['created_at'] else None
                        last_login = safe_datetime_parse(row['last_login'], 'last_login') if row['last_login'] else None
                        
                        users.append(User(
                            user_id=row['user_id'],
                            username=row['username'],
                            password_hash=row['password_hash'],
                            email=row['email'] or "",
                            full_name=row['full_name'] or "",
                            created_at=created_at,
                            last_login=last_login,
                            is_active=bool(row['is_active'])
                        ))
                    except DateTimeParsingError as e:
                        # Log the error but continue processing other users
                        self.logger.warning(f"Skipping user {row['user_id']} due to datetime parsing error: {e}")
                        continue
                        
                return users
                
        except sqlite3.Error as e:
            raise DatabaseTransactionError(
                f"Database error while retrieving all users: {str(e)}",
                transaction_type="SELECT",
                table_name="users"
            ) from e
    
    # Profile management methods
    def create_profile(self, profile: UserProfile) -> Optional[int]:
        """Create a new user profile and return profile_id."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if user already has 5 profiles
                cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = ?", (profile.user_id,))
                count = cursor.fetchone()[0]
                if count >= 5:
                    self.logger.warning(f"User {profile.user_id} already has maximum number of profiles (5)")
                    return None
                
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, profile_name, environment_type, preferences_data, is_default, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.profile_name,
                    profile.environment_type,
                    profile.to_dict()['preferences_data'],
                    profile.is_default,
                    profile.created_at or datetime.now(),
                    profile.updated_at or datetime.now()
                ))
                profile_id = cursor.lastrowid
                conn.commit()
                self.logger.info(f"Created profile: {profile.profile_name} for user {profile.user_id}")
                return profile_id
                
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Profile creation failed - name already exists: {profile.profile_name}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create profile: {e}")
            return None
    
    def get_user_profiles(self, user_id: int) -> List[UserProfile]:
        """Get all profiles for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM user_profiles WHERE user_id = ? ORDER BY is_default DESC, profile_name",
                    (user_id,)
                )
                rows = cursor.fetchall()
                
                profiles = []
                for row in rows:
                    profile_data = {
                        'profile_id': row['profile_id'],
                        'user_id': row['user_id'],
                        'profile_name': row['profile_name'],
                        'environment_type': row['environment_type'],
                        'preferences_data': row['preferences_data'],
                        'is_default': bool(row['is_default']),
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                    profiles.append(UserProfile.from_dict(profile_data))
                return profiles
                
        except Exception as e:
            self.logger.error(f"Failed to get user profiles: {e}")
            return []
    
    def get_profile_by_id(self, profile_id: int) -> Optional[UserProfile]:
        """Get profile by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_profiles WHERE profile_id = ?", (profile_id,))
                row = cursor.fetchone()
                
                if row:
                    profile_data = {
                        'profile_id': row['profile_id'],
                        'user_id': row['user_id'],
                        'profile_name': row['profile_name'],
                        'environment_type': row['environment_type'],
                        'preferences_data': row['preferences_data'],
                        'is_default': bool(row['is_default']),
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                    return UserProfile.from_dict(profile_data)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get profile by ID: {e}")
            return None
    
    def update_profile(self, profile: UserProfile) -> bool:
        """Update an existing profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_profiles 
                    SET profile_name = ?, environment_type = ?, preferences_data = ?, is_default = ?, updated_at = ?
                    WHERE profile_id = ?
                """, (
                    profile.profile_name,
                    profile.environment_type,
                    profile.to_dict()['preferences_data'],
                    profile.is_default,
                    datetime.now(),
                    profile.profile_id
                ))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update profile: {e}")
            return False
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_profiles WHERE profile_id = ?", (profile_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete profile: {e}")
            return False
    
    def set_default_profile(self, user_id: int, profile_id: int) -> bool:
        """Set a profile as default for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove default from all user's profiles
                cursor.execute(
                    "UPDATE user_profiles SET is_default = 0 WHERE user_id = ?",
                    (user_id,)
                )
                
                # Set new default
                cursor.execute(
                    "UPDATE user_profiles SET is_default = 1 WHERE profile_id = ? AND user_id = ?",
                    (profile_id, user_id)
                )
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to set default profile: {e}")
            return False
    
    # Session management methods
    def create_session(self, session: UserSession) -> bool:
        """Create a new user session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old sessions for this user
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (session.user_id,))
                
                # Create new session
                cursor.execute("""
                    INSERT INTO user_sessions (session_id, user_id, current_profile_id, login_time, last_activity)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.current_profile_id,
                    session.login_time or datetime.now(),
                    session.last_activity or datetime.now()
                ))
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                
                if row:
                    session_data = {
                        'session_id': row['session_id'],
                        'user_id': row['user_id'],
                        'current_profile_id': row['current_profile_id'],
                        'login_time': row['login_time'],
                        'last_activity': row['last_activity']
                    }
                    return UserSession.from_dict(session_data)
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE user_sessions SET last_activity = ? WHERE session_id = ?",
                    (datetime.now(), session_id)
                )
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update session activity: {e}")
            return False
    
    def update_session_profile(self, session_id: str, profile_id: int) -> bool:
        """Update current profile for session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE user_sessions SET current_profile_id = ?, last_activity = ? WHERE session_id = ?",
                    (profile_id, datetime.now(), session_id)
                )
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update session profile: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete session: {e}")
            return False
    
    def cleanup_expired_sessions(self, timeout_hours: int = 24) -> int:
        """Clean up expired sessions and return count of deleted sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now().timestamp() - (timeout_hours * 3600)
                cursor.execute(
                    "DELETE FROM user_sessions WHERE strftime('%s', last_activity) < ?",
                    (cutoff_time,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} expired sessions")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    def has_users(self) -> bool:
        """Check if any users exist in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            self.logger.error(f"Failed to check if users exist: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False