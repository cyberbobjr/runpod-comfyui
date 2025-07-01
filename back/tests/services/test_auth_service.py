import pytest
import tempfile
import os
from back.services.auth_service import AuthService


class TestAuthService:
    """
    Test cases for the AuthService class.
    
    **Description:** Unit tests for authentication service functionality.
    """
    
    def test_hash_password(self):
        """
        Test password hashing functionality.
        
        **Description:** Verifies that passwords are properly hashed.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        password = "test_password"
        hashed = AuthService.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) == 44  # Base64 encoded 32-byte hash
    
    def test_verify_password(self):
        """
        Test password verification functionality.
        
        **Description:** Verifies that password verification works correctly.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        password = "test_password"
        hashed = AuthService.hash_password(password)
        
        # Correct password should verify
        assert AuthService.verify_password(password, hashed) is True
        
        # Incorrect password should not verify
        assert AuthService.verify_password("wrong_password", hashed) is False
    
    def test_is_password_hashed(self):
        """
        Test password hash detection.
        
        **Description:** Verifies that the service can detect hashed passwords.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        plain_password = "plain_text"
        hashed_password = AuthService.hash_password("test")
        
        assert AuthService.is_password_hashed(plain_password) is False
        assert AuthService.is_password_hashed(hashed_password) is True
    
    def test_create_and_decode_jwt(self):
        """
        Test JWT token creation and decoding.
        
        **Description:** Verifies JWT token lifecycle functionality.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        username = "test_user"
        
        # Create token
        token = AuthService.create_jwt(username)
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token
        decoded_username = AuthService.decode_jwt(token)
        assert decoded_username == username
        
        # Invalid token should return None
        invalid_decoded = AuthService.decode_jwt("invalid_token")
        assert invalid_decoded is None
