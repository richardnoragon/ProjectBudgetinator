"""
Main authentication manager that coordinates all authentication components.
"""
import logging
from typing import Optional, List, Dict, Any

from database.db_manager import DatabaseManager
from database.models import User, UserProfile, EnvironmentType
from .user_manager import UserManager
from .profile_manager import ProfileManager
from .session_manager import SessionManager


class AuthenticationManager:
    """Main authentication manager that coordinates user, profile, and session management."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize authentication manager."""
        self.logger = logging.getLogger("ProjectBudgetinator.auth")
        
        # Initialize database manager
        self.db_manager = DatabaseManager(db_path)
        
        # Initialize component managers
        self.user_manager = UserManager(self.db_manager)
        self.profile_manager = ProfileManager(self.db_manager)
        self.session_manager = SessionManager(self.db_manager)
        
        # Initialize system if needed
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the authentication system."""
        try:
            # Clean up expired sessions
            self.session_manager.cleanup_expired_sessions()
            
            # Check if we need to create default admin user
            if not self.user_manager.has_users():
                self.logger.info("No users found, creating default admin user")
                admin_user = self.user_manager.create_default_admin_user()
                if admin_user and admin_user.user_id is not None:
                    # Create default profile for admin
                    self.profile_manager.create_default_profiles_for_user(admin_user.user_id)
                    self.logger.info("Authentication system initialized with default admin user")
                else:
                    self.logger.error("Failed to create default admin user")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize authentication system: {e}")
            raise
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create session.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session ID if login successful, None otherwise
        """
        try:
            # Authenticate user
            user = self.user_manager.authenticate_user(username, password)
            if not user:
                return None
            
            # Get default profile
            if user.user_id is None:
                self.logger.error("User has no valid user_id")
                return None
            default_profile = self.profile_manager.get_default_profile(user.user_id)
            
            # Create session
            session_id = self.session_manager.create_session(user, default_profile)
            
            self.logger.info(f"User logged in successfully: {username}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Login failed for user {username}: {e}")
            return None
    
    def logout(self) -> bool:
        """
        Logout current user.
        
        Returns:
            True if logout successful
        """
        return self.session_manager.logout()
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.session_manager.is_authenticated()
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user."""
        return self.session_manager.get_current_user()
    
    def get_current_profile(self) -> Optional[UserProfile]:
        """Get current active profile."""
        return self.session_manager.get_current_profile()
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        session = self.session_manager.get_current_session()
        return session.session_id if session else None
    
    def switch_profile(self, profile_id: int) -> bool:
        """
        Switch to a different profile.
        
        Args:
            profile_id: Profile ID to switch to
            
        Returns:
            True if switch successful
        """
        return self.session_manager.switch_profile(profile_id)
    
    def get_user_profiles(self) -> List[UserProfile]:
        """Get all profiles for current user."""
        return self.session_manager.get_user_profiles()
    
    def create_user(self, username: str, password: str, email: str = "", full_name: str = "") -> Optional[User]:
        """
        Create a new user.
        
        Args:
            username: Username
            password: Password
            email: Email (optional)
            full_name: Full name (optional)
            
        Returns:
            Created user or None if failed
        """
        user = self.user_manager.create_user(username, password, email, full_name)
        if user and user.user_id is not None:
            # Create default profile for new user
            self.profile_manager.create_default_profiles_for_user(user.user_id)
        return user
    
    def create_profile(self, profile_name: str, environment_type: str, 
                      preferences: Optional[Dict[str, Any]] = None) -> Optional[UserProfile]:
        """
        Create a new profile for current user.
        
        Args:
            profile_name: Name for the profile
            environment_type: Environment type
            preferences: Profile preferences (optional)
            
        Returns:
            Created profile or None if failed
        """
        current_user = self.get_current_user()
        if not current_user or current_user.user_id is None:
            self.logger.error("No authenticated user to create profile for")
            return None
        
        return self.profile_manager.create_profile(
            user_id=current_user.user_id,
            profile_name=profile_name,
            environment_type=environment_type,
            preferences=preferences
        )
    
    def update_profile(self, profile_id: int, profile_name: Optional[str] = None,
                      environment_type: Optional[str] = None,
                      preferences: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing profile.
        
        Args:
            profile_id: Profile ID to update
            profile_name: New profile name (optional)
            environment_type: New environment type (optional)
            preferences: New preferences (optional)
            
        Returns:
            True if update successful
        """
        return self.profile_manager.update_profile(profile_id, profile_name, environment_type, preferences)
    
    def delete_profile(self, profile_id: int) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            True if deletion successful
        """
        return self.profile_manager.delete_profile(profile_id)
    
    def set_default_profile(self, profile_id: int) -> bool:
        """
        Set a profile as default for current user.
        
        Args:
            profile_id: Profile ID to set as default
            
        Returns:
            True if successful
        """
        current_user = self.get_current_user()
        if not current_user or current_user.user_id is None:
            return False
        
        return self.profile_manager.set_default_profile(current_user.user_id, profile_id)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value from current profile.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        current_profile = self.get_current_profile()
        if not current_profile:
            return default
        
        return current_profile.get_preference(key, default)
    
    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a preference value in current profile.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful
        """
        current_profile = self.get_current_profile()
        if not current_profile or current_profile.profile_id is None:
            return False
        
        return self.profile_manager.set_profile_preference(current_profile.profile_id, key, value)
    
    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Update multiple preferences in current profile.
        
        Args:
            preferences: Dictionary of preferences to update
            
        Returns:
            True if successful
        """
        current_profile = self.get_current_profile()
        if not current_profile or current_profile.profile_id is None:
            return False
        
        return self.profile_manager.update_profile_preferences(current_profile.profile_id, preferences)
    
    def is_current_user_admin(self) -> bool:
        """
        Check if current user is admin.
        
        Returns:
            True if current user is admin
        """
        current_user = self.get_current_user()
        if not current_user:
            return False
        
        return self.user_manager.is_admin_user(current_user)
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change password for current user.
        
        Args:
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        current_user = self.get_current_user()
        if not current_user or current_user.user_id is None:
            return False
        
        # Prevent admin password changes
        if self.user_manager.is_admin_user(current_user):
            self.logger.warning(f"Password change blocked for admin user: {current_user.username}")
            return False
        
        return self.user_manager.change_password(current_user.user_id, old_password, new_password)
    
    def is_using_default_password(self) -> bool:
        """
        Check if current user is using the default password.
        
        Returns:
            True if using default password
        """
        current_user = self.get_current_user()
        if not current_user:
            return False
        
        return self.user_manager.is_using_default_password(current_user)
    
    def get_all_users(self) -> List[User]:
        """Get all users (admin function)."""
        return self.user_manager.get_all_users()
    
    def get_environment_types(self) -> List[str]:
        """Get all available environment types."""
        return EnvironmentType.get_all()
    
    def get_default_preferences_for_environment(self, environment_type: str) -> Dict[str, Any]:
        """Get default preferences for an environment type."""
        return EnvironmentType.get_default_preferences(environment_type)
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate a session ID.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            True if session is valid
        """
        return self.session_manager.validate_session(session_id)
    
    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            True if session loaded successfully
        """
        return self.session_manager.load_session(session_id)
    
    def update_activity(self):
        """Update session activity timestamp."""
        self.session_manager.update_activity()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the user database.
        
        Args:
            backup_path: Path to save backup
            
        Returns:
            True if backup successful
        """
        return self.db_manager.backup_database(backup_path)
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self.get_all_users())
    
    def get_profile_count(self) -> int:
        """Get total number of profiles for current user."""
        return len(self.get_user_profiles())
    
    def has_users(self) -> bool:
        """Check if any users exist."""
        return self.user_manager.has_users()


# Global authentication manager instance
_auth_manager: Optional[AuthenticationManager] = None


def get_auth_manager(db_path: Optional[str] = None) -> AuthenticationManager:
    """
    Get the global authentication manager instance.
    
    Args:
        db_path: Database path (only used for first initialization)
        
    Returns:
        AuthenticationManager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager(db_path)
    return _auth_manager


def reset_auth_manager():
    """Reset the global authentication manager (for testing)."""
    global _auth_manager
    _auth_manager = None