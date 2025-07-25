"""
Session management for user authentication.
"""
import uuid
import logging
from typing import Optional
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import UserSession, User, UserProfile


class SessionManager:
    """Manages user sessions and authentication state."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize session manager."""
        self.db_manager = db_manager
        self.logger = logging.getLogger("ProjectBudgetinator.session")
        self.current_session: Optional[UserSession] = None
        self.current_user: Optional[User] = None
        self.current_profile: Optional[UserProfile] = None
    
    def create_session(self, user: User, profile: Optional[UserProfile] = None) -> str:
        """
        Create a new session for a user.
        
        Args:
            user: User to create session for
            profile: Optional profile to set as current
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        if user.user_id is None:
            raise ValueError("User must have a valid user_id")
            
        session = UserSession(
            session_id=session_id,
            user_id=user.user_id,
            current_profile_id=profile.profile_id if profile else None,
            login_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        if self.db_manager.create_session(session):
            self.current_session = session
            self.current_user = user
            self.current_profile = profile
            
            # Update user's last login
            self.db_manager.update_user_last_login(user.user_id)
            
            self.logger.info(f"Created session for user: {user.username}")
            return session_id
        else:
            self.logger.error(f"Failed to create session for user: {user.username}")
            raise Exception("Failed to create session")
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        return self.db_manager.get_session(session_id)
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session is still active and not expired.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            True if session is valid
        """
        session = self.db_manager.get_session(session_id)
        if not session:
            return False
        
        if session.is_expired():
            self.db_manager.delete_session(session_id)
            return False
        
        # Update activity
        self.db_manager.update_session_activity(session_id)
        return True
    
    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session as current session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            True if session loaded successfully
        """
        if not self.validate_session(session_id):
            return False
        
        session = self.db_manager.get_session(session_id)
        if not session:
            return False
        
        # Load user
        user = self.db_manager.get_user_by_id(session.user_id)
        if not user:
            self.logger.error(f"User not found for session: {session_id}")
            return False
        
        # Load current profile if set
        profile = None
        if session.current_profile_id:
            profile = self.db_manager.get_profile_by_id(session.current_profile_id)
        
        self.current_session = session
        self.current_user = user
        self.current_profile = profile
        
        self.logger.info(f"Loaded session for user: {user.username}")
        return True
    
    def switch_profile(self, profile_id: int) -> bool:
        """
        Switch to a different profile in the current session.
        
        Args:
            profile_id: Profile ID to switch to
            
        Returns:
            True if profile switched successfully
        """
        if not self.current_session or not self.current_user:
            self.logger.error("No active session to switch profile")
            return False
        
        # Verify profile belongs to current user
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile or profile.user_id != self.current_user.user_id:
            self.logger.error(f"Profile {profile_id} not found or doesn't belong to user")
            return False
        
        # Update session
        if self.db_manager.update_session_profile(self.current_session.session_id, profile_id):
            self.current_session.current_profile_id = profile_id
            self.current_profile = profile
            self.logger.info(f"Switched to profile: {profile.profile_name}")
            return True
        
        return False
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user."""
        return self.current_user
    
    def get_current_profile(self) -> Optional[UserProfile]:
        """Get current active profile."""
        return self.current_profile
    
    def get_current_session(self) -> Optional[UserSession]:
        """Get current session."""
        return self.current_session
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return (self.current_session is not None and 
                self.current_user is not None and
                not self.current_session.is_expired())
    
    def logout(self) -> bool:
        """
        Logout current user and cleanup session.
        
        Returns:
            True if logout successful
        """
        if not self.current_session:
            return True
        
        session_id = self.current_session.session_id
        username = self.current_user.username if self.current_user else "unknown"
        
        # Delete session from database
        success = self.db_manager.delete_session(session_id)
        
        # Clear current state
        self.current_session = None
        self.current_user = None
        self.current_profile = None
        
        if success:
            self.logger.info(f"User logged out: {username}")
        else:
            self.logger.warning(f"Failed to cleanup session for user: {username}")
        
        return success
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        return self.db_manager.cleanup_expired_sessions()
    
    def get_user_profiles(self) -> list:
        """Get all profiles for current user."""
        if not self.current_user or self.current_user.user_id is None:
            return []
        
        return self.db_manager.get_user_profiles(self.current_user.user_id)
    
    def get_default_profile(self) -> Optional[UserProfile]:
        """Get default profile for current user."""
        profiles = self.get_user_profiles()
        for profile in profiles:
            if profile.is_default:
                return profile
        
        # If no default set, return first profile
        return profiles[0] if profiles else None
    
    def update_activity(self) -> None:
        """Update session activity timestamp."""
        if self.current_session:
            self.db_manager.update_session_activity(self.current_session.session_id)
            self.current_session.update_activity()