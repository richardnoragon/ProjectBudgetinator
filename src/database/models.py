"""
Data models for the user administration system.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from ..exceptions import (
    DateTimeParsingError,
    JSONProcessingError,
    safe_datetime_parse,
    safe_json_loads,
    safe_json_dumps
)


@dataclass
class User:
    """User model for authentication and management."""
    user_id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    email: str = ""
    full_name: str = ""
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_login:
            data['last_login'] = self.last_login.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary with safe datetime parsing."""
        # Convert ISO strings back to datetime objects with error handling
        if 'created_at' in data and data['created_at']:
            data['created_at'] = safe_datetime_parse(data['created_at'], 'created_at')
        if 'last_login' in data and data['last_login']:
            data['last_login'] = safe_datetime_parse(data['last_login'], 'last_login')
        return cls(**data)


@dataclass
class UserProfile:
    """User profile model for environment-specific preferences."""
    profile_id: Optional[int] = None
    user_id: int = 0
    profile_name: str = ""
    environment_type: str = ""  # Development, Testing, Staging, Production, Personal
    preferences_data: Optional[Dict[str, Any]] = None
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.preferences_data is None:
            self.preferences_data = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary with safe JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        # Convert preferences_data to JSON string for storage with error handling
        data['preferences_data'] = safe_json_dumps(self.preferences_data, 'preferences_data')
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from dictionary with safe parsing."""
        # Convert ISO strings back to datetime objects with error handling
        if 'created_at' in data and data['created_at']:
            data['created_at'] = safe_datetime_parse(data['created_at'], 'created_at')
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = safe_datetime_parse(data['updated_at'], 'updated_at')
        # Parse JSON preferences_data with error handling
        if 'preferences_data' in data and isinstance(data['preferences_data'], str):
            data['preferences_data'] = safe_json_loads(data['preferences_data'], 'preferences_data')
        return cls(**data)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value."""
        if self.preferences_data is None:
            return default
        return self.preferences_data.get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a specific preference value."""
        if self.preferences_data is None:
            self.preferences_data = {}
        self.preferences_data[key] = value
        self.updated_at = datetime.now()

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update multiple preferences at once."""
        if self.preferences_data is None:
            self.preferences_data = {}
        self.preferences_data.update(preferences)
        self.updated_at = datetime.now()


@dataclass
class UserSession:
    """User session model for tracking active sessions."""
    session_id: str = ""
    user_id: int = 0
    current_profile_id: Optional[int] = None
    login_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.login_time is None:
            self.login_time = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.login_time:
            data['login_time'] = self.login_time.isoformat()
        if self.last_activity:
            data['last_activity'] = self.last_activity.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create session from dictionary with safe datetime parsing."""
        # Convert ISO strings back to datetime objects with error handling
        if 'login_time' in data and data['login_time']:
            data['login_time'] = safe_datetime_parse(data['login_time'], 'login_time')
        if 'last_activity' in data and data['last_activity']:
            data['last_activity'] = safe_datetime_parse(data['last_activity'], 'last_activity')
        return cls(**data)

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session is expired."""
        if not self.last_activity:
            return True
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > (timeout_hours * 3600)


# Environment type constants
class EnvironmentType:
    """Constants for environment types."""
    DEVELOPMENT = "Development"
    TESTING = "Testing"
    STAGING = "Staging"
    PRODUCTION = "Production"
    PERSONAL = "Personal"

    @classmethod
    def get_all(cls) -> list:
        """Get all environment types."""
        return [cls.DEVELOPMENT, cls.TESTING, cls.STAGING, cls.PRODUCTION, cls.PERSONAL]

    @classmethod
    def get_default_preferences(cls, env_type: str) -> Dict[str, Any]:
        """Get default preferences for environment type."""
        defaults = {
            "theme": "light",
            "welcome_screen": True,
            "startup_diagnostic": "verbose",
            "default_file_location": "",
            "remember_last_location": False,
            "save_location": "",
            "auto_backup": True,
            "backup_count": 5,
            "max_recent_files": 10,
            "enable_caching": True,
            "cache_size_mb": 100
        }
        
        # Environment-specific overrides
        if env_type == cls.DEVELOPMENT:
            defaults.update({
                "startup_diagnostic": "debug",
                "auto_backup": True,
                "backup_count": 10,
                "enable_caching": False
            })
        elif env_type == cls.TESTING:
            defaults.update({
                "startup_diagnostic": "verbose",
                "auto_backup": False,
                "enable_caching": False
            })
        elif env_type == cls.PRODUCTION:
            defaults.update({
                "startup_diagnostic": "minimal",
                "auto_backup": True,
                "backup_count": 20,
                "enable_caching": True,
                "cache_size_mb": 200
            })
        elif env_type == cls.STAGING:
            defaults.update({
                "startup_diagnostic": "verbose",
                "auto_backup": True,
                "backup_count": 5,
                "enable_caching": True
            })
        
        return defaults