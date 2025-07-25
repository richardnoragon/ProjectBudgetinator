#!/usr/bin/env python3
"""
Debug script for authentication system.
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_auth_system():
    """Test the authentication system step by step."""
    print("=== Authentication System Debug ===")
    
    try:
        print("1. Testing database manager...")
        from database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        print("   ✓ Database manager created")
        
        print("2. Database automatically initialized in constructor")
        print("   ✓ Database initialized")
        
        print("3. Testing user manager...")
        from auth.user_manager import UserManager
        user_manager = UserManager(db_manager)
        print("   ✓ User manager created")
        
        print("4. Testing admin user creation...")
        admin_data = {
            'username': 'admin',
            'password': 'pbi',
            'full_name': 'Administrator',
            'email': 'admin@projectbudgetinator.com'
        }
        
        # Check if admin user already exists
        existing_user = user_manager.get_user_by_username('admin')
        if existing_user:
            print("   ✓ Admin user already exists")
        else:
            admin_user = user_manager.create_user(admin_data)
            if admin_user:
                print("   ✓ Admin user created successfully")
            else:
                print("   ✗ Failed to create admin user")
                return False
        
        print("5. Testing authentication...")
        auth_result = user_manager.authenticate_user('admin', 'pbi')
        if auth_result:
            print("   ✓ Authentication successful")
            print(f"   User ID: {auth_result.user_id}")
            print(f"   Username: {auth_result.username}")
        else:
            print("   ✗ Authentication failed")
            return False
        
        print("6. Testing profile manager...")
        from auth.profile_manager import ProfileManager
        profile_manager = ProfileManager(db_manager)
        print("   ✓ Profile manager created")
        
        print("7. Testing default profile creation...")
        profiles = profile_manager.get_user_profiles(auth_result.user_id)
        if not profiles:
            default_profile_data = {
                'profile_name': 'Default',
                'environment_type': 'Development',
                'preferences_data': {'description': 'Default development profile'}
            }
            default_profile = profile_manager.create_profile(auth_result.user_id, default_profile_data)
            if default_profile:
                print("   ✓ Default profile created")
            else:
                print("   ✗ Failed to create default profile")
                return False
        else:
            print(f"   ✓ User has {len(profiles)} existing profiles")
        
        print("8. Testing auth manager...")
        from auth.auth_manager import AuthenticationManager
        auth_manager = AuthenticationManager()
        print("   ✓ Auth manager created")
        
        print("9. Testing full authentication flow...")
        login_result = auth_manager.login('admin', 'pbi')
        if login_result:
            print("   ✓ Full authentication flow successful")
            current_user = auth_manager.get_current_user()
            current_profile = auth_manager.get_current_profile()
            print(f"   Current user: {current_user.username if current_user else 'None'}")
            print(f"   Current profile: {current_profile.profile_name if current_profile else 'None'}")
        else:
            print("   ✗ Full authentication flow failed")
            return False
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_system()
    if not success:
        sys.exit(1)