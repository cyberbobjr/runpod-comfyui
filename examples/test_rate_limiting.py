#!/usr/bin/env python3
"""
Test script to demonstrate the 3-second rate limiting behavior.
"""

import sys
import os
import time
import tempfile
from unittest.mock import patch, Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.services.model_scanner_service import ModelScannerService
from back.services.token_service import TokenService


def test_rate_limiting_behavior():
    """Test that the rate limiting actually works."""
    print("Testing CivitAI rate limiting behavior")
    print("=" * 50)
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.safetensors') as tmp:
        tmp.write(b"test content for rate limiting")
        test_file = tmp.name
    
    try:
        # Mock the token service and CivitAI client
        with patch('back.services.model_scanner_service.TokenService.get_tokens') as mock_tokens, \
             patch('back.services.model_scanner_service.CivitAIClient') as mock_client_class, \
             patch('back.services.model_scanner_service.time.sleep') as mock_sleep:
            
            # Setup mocks
            mock_tokens.return_value = {"civitai_token": "test_token"}
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_model_version_by_hash.return_value = None
            
            # Create test model info
            model_info = {
                "name": "test_model.safetensors",
                "path": test_file,
                "category": "other"
            }
            
            print("Calling _enhance_model_with_civitai...")
            start_time = time.time()
            
            # Call the method
            result = ModelScannerService._enhance_model_with_civitai(model_info)
            
            end_time = time.time()
            
            print(f"Method returned: {result}")
            print(f"Execution time: {end_time - start_time:.3f}s")
            print()
            
            # Verify the mocks were called correctly
            print("Verifying rate limiting:")
            if mock_sleep.called:
                print(f"✓ time.sleep() was called {mock_sleep.call_count} time(s)")
                calls = mock_sleep.call_args_list
                for i, call in enumerate(calls):
                    print(f"  Call {i+1}: sleep({call[0][0]} seconds)")
            else:
                print("✗ time.sleep() was not called")
            
            print()
            print("Verifying API calls:")
            if mock_client.get_model_version_by_hash.called:
                print(f"✓ CivitAI API was called {mock_client.get_model_version_by_hash.call_count} time(s)")
            else:
                print("✗ CivitAI API was not called")
            
            # Test with successful API response
            print("\n" + "=" * 50)
            print("Testing with successful API response...")
            
            # Reset mocks
            mock_sleep.reset_mock()
            mock_client.reset_mock()
            
            # Mock successful response
            mock_client.get_model_version_by_hash.return_value = {
                "id": 12345,
                "name": "Test Model Version",
                "baseModel": "SD 1.5",
                "model": {
                    "id": 67890,
                    "name": "Test Model",
                    "type": "Checkpoint",
                    "description": "A test model",
                    "tags": ["test"],
                    "nsfw": False,
                    "creator": {"username": "testuser"},
                    "stats": {}
                },
                "images": [],
                "files": []
            }
            
            start_time = time.time()
            result = ModelScannerService._enhance_model_with_civitai(model_info)
            end_time = time.time()
            
            print(f"Method returned enhanced model: {result is not None}")
            print(f"Execution time: {end_time - start_time:.3f}s")
            
            if result and 'civitai_info' in result:
                print(f"✓ Model enhanced with CivitAI data")
                print(f"  Model name: {result['civitai_info']['model_name']}")
                print(f"  Category: {result['category']}")
            
            print("\nVerifying rate limiting with success:")
            if mock_sleep.called:
                print(f"✓ time.sleep() was called {mock_sleep.call_count} time(s)")
                calls = mock_sleep.call_args_list
                for i, call in enumerate(calls):
                    print(f"  Call {i+1}: sleep({call[0][0]} seconds)")
            else:
                print("✗ time.sleep() was not called")
                
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
    
    print("\n" + "=" * 50)
    print("Rate limiting test completed!")


if __name__ == "__main__":
    test_rate_limiting_behavior()
