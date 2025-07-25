"""
Password utilities for secure password handling.
"""
import hashlib
import secrets
import string
from typing import Tuple


class PasswordUtils:
    """Utilities for password hashing and validation."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt
        """
        # Generate a random salt
        salt = secrets.token_hex(32)
        
        # Hash the password with salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Return salt + hash (salt is first 64 characters)
        return salt + password_hash
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored hash to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        if len(hashed_password) < 64:
            return False
            
        # Extract salt (first 64 characters) and hash (remaining)
        salt = hashed_password[:64]
        stored_hash = hashed_password[64:]
        
        # Hash the provided password with the stored salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Compare hashes
        return password_hash == stored_hash
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """
        Generate a random password.
        
        Args:
            length: Length of password to generate
            
        Returns:
            Random password string
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 3:
            return False, "Password must be at least 3 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # For this application, we'll keep password requirements simple
        # since the default is "pbi" and users may not want complex passwords
        return True, ""
    
    @staticmethod
    def is_default_password(password: str) -> bool:
        """
        Check if password is the default password.
        
        Args:
            password: Password to check
            
        Returns:
            True if it's the default password
        """
        return password.lower() == "pbi"