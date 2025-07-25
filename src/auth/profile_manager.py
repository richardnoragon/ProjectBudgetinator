"""
Profile management functionality.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import UserProfile, EnvironmentType


class ProfileManager:
    """Manages user profiles and environment-specific preferences."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize profile manager."""
        self.db_manager = db_manager
        self.logger = logging.getLogger("ProjectBudgetinator.profile_manager")
    
    def create_profile(self, user_id: int, profile_name: str, environment_type: str, 
                      preferences: Optional[Dict[str, Any]] = None, is_default: bool = False) -> Optional[UserProfile]:
        """
        Create a new user profile.
        
        Args:
            user_id: User ID
            profile_name: Name for the profile
            environment_type: Type of environment (Development, Testing, etc.)
            preferences: Profile preferences (optional)
            is_default: Whether this should be the default profile
            
        Returns:
            Created profile or None if creation failed
        """
        # Validate input
        if not profile_name or not profile_name.strip():
            self.logger.error("Profile name cannot be empty")
            return None
        
        profile_name = profile_name.strip()
        
        # Validate environment type
        if environment_type not in EnvironmentType.get_all():
            self.logger.error(f"Invalid environment type: {environment_type}")
            return None
        
        # Check if user already has 5 profiles
        existing_profiles = self.db_manager.get_user_profiles(user_id)
        if len(existing_profiles) >= 5:
            self.logger.error(f"User {user_id} already has maximum number of profiles (5)")
            return None
        
        # Check if profile name already exists for this user
        for profile in existing_profiles:
            if profile.profile_name.lower() == profile_name.lower():
                self.logger.error(f"Profile name already exists: {profile_name}")
                return None
        
        # Get default preferences for environment type
        if preferences is None:
            preferences = EnvironmentType.get_default_preferences(environment_type)
        
        # If this is the first profile for the user, make it default
        if not existing_profiles:
            is_default = True
        
        # Create profile object
        profile = UserProfile(
            user_id=user_id,
            profile_name=profile_name,
            environment_type=environment_type,
            preferences_data=preferences,
            is_default=is_default,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        profile_id = self.db_manager.create_profile(profile)
        if profile_id:
            profile.profile_id = profile_id
            
            # If this is set as default, update other profiles
            if is_default:
                self.db_manager.set_default_profile(user_id, profile_id)
            
            self.logger.info(f"Created profile: {profile_name} for user {user_id}")
            return profile
        
        return None
    
    def get_user_profiles(self, user_id: int) -> List[UserProfile]:
        """Get all profiles for a user."""
        return self.db_manager.get_user_profiles(user_id)
    
    def get_profile_by_id(self, profile_id: int) -> Optional[UserProfile]:
        """Get profile by ID."""
        return self.db_manager.get_profile_by_id(profile_id)
    
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
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            self.logger.error(f"Profile not found: {profile_id}")
            return False
        
        # Update fields if provided
        if profile_name is not None:
            profile_name = profile_name.strip()
            if not profile_name:
                self.logger.error("Profile name cannot be empty")
                return False
            
            # Check if new name conflicts with existing profiles
            user_profiles = self.db_manager.get_user_profiles(profile.user_id)
            for p in user_profiles:
                if p.profile_id != profile_id and p.profile_name.lower() == profile_name.lower():
                    self.logger.error(f"Profile name already exists: {profile_name}")
                    return False
            
            profile.profile_name = profile_name
        
        if environment_type is not None:
            if environment_type not in EnvironmentType.get_all():
                self.logger.error(f"Invalid environment type: {environment_type}")
                return False
            profile.environment_type = environment_type
        
        if preferences is not None:
            profile.preferences_data = preferences
        
        profile.updated_at = datetime.now()
        
        # Save to database
        if self.db_manager.update_profile(profile):
            self.logger.info(f"Updated profile: {profile.profile_name}")
            return True
        
        return False
    
    def delete_profile(self, profile_id: int) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            True if deletion successful
        """
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            self.logger.error(f"Profile not found: {profile_id}")
            return False
        
        # Check if this is the only profile for the user
        user_profiles = self.db_manager.get_user_profiles(profile.user_id)
        if len(user_profiles) <= 1:
            self.logger.error("Cannot delete the only profile for a user")
            return False
        
        # If this is the default profile, set another as default
        if profile.is_default:
            for p in user_profiles:
                if p.profile_id != profile_id and p.profile_id is not None:
                    self.db_manager.set_default_profile(profile.user_id, p.profile_id)
                    break
        
        # Delete from database
        if self.db_manager.delete_profile(profile_id):
            self.logger.info(f"Deleted profile: {profile.profile_name}")
            return True
        
        return False
    
    def set_default_profile(self, user_id: int, profile_id: int) -> bool:
        """
        Set a profile as default for a user.
        
        Args:
            user_id: User ID
            profile_id: Profile ID to set as default
            
        Returns:
            True if successful
        """
        # Verify profile belongs to user
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile or profile.user_id != user_id:
            self.logger.error(f"Profile {profile_id} not found or doesn't belong to user {user_id}")
            return False
        
        if self.db_manager.set_default_profile(user_id, profile_id):
            self.logger.info(f"Set default profile: {profile.profile_name} for user {user_id}")
            return True
        
        return False
    
    def get_default_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Get the default profile for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Default profile or None if not found
        """
        profiles = self.db_manager.get_user_profiles(user_id)
        for profile in profiles:
            if profile.is_default:
                return profile
        
        # If no default set, return first profile
        return profiles[0] if profiles else None
    
    def update_profile_preferences(self, profile_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Update preferences for a profile.
        
        Args:
            profile_id: Profile ID
            preferences: New preferences dictionary
            
        Returns:
            True if update successful
        """
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            self.logger.error(f"Profile not found: {profile_id}")
            return False
        
        profile.update_preferences(preferences)
        
        if self.db_manager.update_profile(profile):
            self.logger.info(f"Updated preferences for profile: {profile.profile_name}")
            return True
        
        return False
    
    def get_profile_preference(self, profile_id: int, key: str, default: Any = None) -> Any:
        """
        Get a specific preference value from a profile.
        
        Args:
            profile_id: Profile ID
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            return default
        
        return profile.get_preference(key, default)
    
    def set_profile_preference(self, profile_id: int, key: str, value: Any) -> bool:
        """
        Set a specific preference value in a profile.
        
        Args:
            profile_id: Profile ID
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful
        """
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            self.logger.error(f"Profile not found: {profile_id}")
            return False
        
        profile.set_preference(key, value)
        
        if self.db_manager.update_profile(profile):
            self.logger.debug(f"Set preference {key}={value} for profile: {profile.profile_name}")
            return True
        
        return False
    
    def create_default_profiles_for_user(self, user_id: int) -> List[UserProfile]:
        """
        Create default profiles for a new user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of created profiles
        """
        created_profiles = []
        
        # Create a default "Personal" profile
        personal_profile = self.create_profile(
            user_id=user_id,
            profile_name="Personal",
            environment_type=EnvironmentType.PERSONAL,
            is_default=True
        )
        
        if personal_profile:
            created_profiles.append(personal_profile)
            self.logger.info(f"Created default Personal profile for user {user_id}")
        
        return created_profiles
    
    def clone_profile(self, source_profile_id: int, new_name: str, user_id: Optional[int] = None) -> Optional[UserProfile]:
        """
        Clone an existing profile.
        
        Args:
            source_profile_id: Profile ID to clone
            new_name: Name for the new profile
            user_id: User ID for the new profile (defaults to same user)
            
        Returns:
            Cloned profile or None if failed
        """
        source_profile = self.db_manager.get_profile_by_id(source_profile_id)
        if not source_profile:
            self.logger.error(f"Source profile not found: {source_profile_id}")
            return None
        
        target_user_id = user_id or source_profile.user_id
        
        # Clone the profile
        cloned_profile = self.create_profile(
            user_id=target_user_id,
            profile_name=new_name,
            environment_type=source_profile.environment_type,
            preferences=source_profile.preferences_data.copy() if source_profile.preferences_data else None,
            is_default=False
        )
        
        if cloned_profile:
            self.logger.info(f"Cloned profile {source_profile.profile_name} to {new_name}")
        
        return cloned_profile
    
    def export_profile(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Export profile data for backup/transfer.
        
        Args:
            profile_id: Profile ID to export
            
        Returns:
            Profile data dictionary or None if not found
        """
        profile = self.db_manager.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        return {
            'profile_name': profile.profile_name,
            'environment_type': profile.environment_type,
            'preferences_data': profile.preferences_data,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None
        }
    
    def import_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Import profile data.
        
        Args:
            user_id: User ID to import profile for
            profile_data: Profile data dictionary
            
        Returns:
            Imported profile or None if failed
        """
        try:
            return self.create_profile(
                user_id=user_id,
                profile_name=profile_data['profile_name'],
                environment_type=profile_data['environment_type'],
                preferences=profile_data.get('preferences_data'),
                is_default=False
            )
        except Exception as e:
            self.logger.error(f"Failed to import profile: {e}")
            return None