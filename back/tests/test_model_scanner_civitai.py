import unittest
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from back.services.model_scanner_service import ModelScannerService
from back.utils.hash_utils import HashUtils


class TestModelScannerCivitAIEnhancement(unittest.TestCase):
    """
    Test suite for CivitAI enhancement functionality in ModelScannerService.
    
    **Purpose:** Tests the integration between ModelScannerService and CivitAI API
    for identifying unknown models.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_model_path = os.path.join(self.temp_dir, "test_model.safetensors")
        
        # Create a dummy model file
        with open(self.test_model_path, 'wb') as f:
            f.write(b"dummy model content for testing")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_model_path):
            os.remove(self.test_model_path)
        os.rmdir(self.temp_dir)
    
    def test_hash_utils_autov2(self):
        """Test HashUtils AutoV2 algorithm."""
        hash_result = HashUtils.get_file_hash(self.test_model_path, 'AutoV2')
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
    
    def test_hash_utils_autov1(self):
        """Test HashUtils AutoV1 algorithm."""
        hash_result = HashUtils.get_file_hash(self.test_model_path, 'AutoV1')
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
    
    def test_hash_utils_sha256(self):
        """Test HashUtils SHA256 algorithm."""
        hash_result = HashUtils.get_file_hash(self.test_model_path, 'SHA256')
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
    
    def test_hash_utils_crc32(self):
        """Test HashUtils CRC32 algorithm."""
        hash_result = HashUtils.get_file_hash(self.test_model_path, 'CRC32')
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 8)  # CRC32 hex length
    
    def test_hash_utils_multiple_hashes(self):
        """Test HashUtils multiple hash computation."""
        algorithms = ['AutoV2', 'SHA256', 'CRC32']
        results = HashUtils.get_multiple_hashes(self.test_model_path, algorithms)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 3)
        
        for algo in algorithms:
            self.assertIn(algo, results)
            self.assertIsInstance(results[algo], str)
    
    def test_hash_utils_nonexistent_file(self):
        """Test HashUtils with non-existent file."""
        hash_result = HashUtils.get_file_hash("/non/existent/file.safetensors", 'AutoV2')
        self.assertIsNone(hash_result)
    
    def test_hash_utils_unsupported_algorithm(self):
        """Test HashUtils with unsupported algorithm."""
        hash_result = HashUtils.get_file_hash(self.test_model_path, 'UNSUPPORTED')
        self.assertIsNone(hash_result)
    
    @patch('back.services.model_scanner_service.TokenService.get_tokens')
    @patch('back.services.model_scanner_service.CivitAIClient')
    def test_enhance_model_with_civitai_success(self, mock_civitai_client, mock_get_tokens):
        """Test successful CivitAI enhancement of unknown model."""
        # Mock token service
        mock_get_tokens.return_value = {"civitai_token": "test_token"}
        
        # Mock CivitAI client
        mock_client = Mock()
        mock_civitai_client.return_value = mock_client
        
        # Mock successful API response
        mock_civitai_response = {
            "id": 12345,
            "name": "Test Model Version",
            "baseModel": "SD 1.5",
            "downloadUrl": "https://example.com/model.safetensors",
            "model": {
                "id": 67890,
                "name": "Test Model",
                "type": "Checkpoint",
                "description": "A test model",
                "tags": ["test", "model"],
                "nsfw": False,
                "creator": {"username": "testuser"},
                "stats": {"downloadCount": 1000}
            },
            "images": [{"url": "https://example.com/image.jpg"}],
            "files": []
        }
        mock_client.get_model_version_by_hash.return_value = mock_civitai_response
        
        # Test model info
        model_info = {
            "name": "unknown_model.safetensors",
            "path": self.test_model_path,
            "category": "other"
        }
        
        # Test enhancement
        result = ModelScannerService._enhance_model_with_civitai(model_info)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "checkpoints")
        self.assertIn("civitai_info", result)
        
        civitai_info = result["civitai_info"]
        self.assertEqual(civitai_info["model_id"], 67890)
        self.assertEqual(civitai_info["model_name"], "Test Model")
        self.assertEqual(civitai_info["model_type"], "checkpoint")
        self.assertEqual(civitai_info["version_id"], 12345)
        self.assertEqual(civitai_info["creator"], "testuser")
        self.assertEqual(civitai_info["hash_algorithm"], "AutoV2")
        self.assertIn("hash_value", civitai_info)
    
    @patch('back.services.model_scanner_service.TokenService.get_tokens')
    def test_enhance_model_with_civitai_no_token(self, mock_get_tokens):
        """Test CivitAI enhancement when no token is available."""
        # Mock no token
        mock_get_tokens.return_value = {"civitai_token": None}
        
        model_info = {
            "name": "unknown_model.safetensors",
            "path": self.test_model_path,
            "category": "other"
        }
        
        result = ModelScannerService._enhance_model_with_civitai(model_info)
        self.assertIsNone(result)
    
    @patch('back.services.model_scanner_service.TokenService.get_tokens')
    @patch('back.services.model_scanner_service.CivitAIClient')
    def test_enhance_model_with_civitai_not_found(self, mock_civitai_client, mock_get_tokens):
        """Test CivitAI enhancement when model is not found."""
        # Mock token service
        mock_get_tokens.return_value = {"civitai_token": "test_token"}
        
        # Mock CivitAI client
        mock_client = Mock()
        mock_civitai_client.return_value = mock_client
        mock_client.get_model_version_by_hash.return_value = None
        
        model_info = {
            "name": "unknown_model.safetensors",
            "path": self.test_model_path,
            "category": "other"
        }
        
        result = ModelScannerService._enhance_model_with_civitai(model_info)
        self.assertIsNone(result)
        
        # Verify only one API call was made
        self.assertEqual(mock_client.get_model_version_by_hash.call_count, 1)
    
    def test_map_civitai_type_to_category(self):
        """Test CivitAI type mapping to internal categories."""
        test_cases = [
            ("checkpoint", "checkpoints"),
            ("textualinversion", "embeddings"),
            ("hypernetwork", "hypernetworks"),
            ("lora", "loras"),
            ("controlnet", "controlnet"),
            ("upscaler", "upscale_models"),
            ("vae", "vae"),
            ("unknown_type", "other")
        ]
        
        for civitai_type, expected_category in test_cases:
            result = ModelScannerService._map_civitai_type_to_category(civitai_type)
            self.assertEqual(result, expected_category)
    
    @patch('back.services.model_scanner_service.TokenService.get_tokens')
    @patch('back.services.model_scanner_service.CivitAIClient')
    @patch('back.services.model_scanner_service.time.sleep')
    def test_enhance_model_with_civitai_rate_limiting(self, mock_sleep, mock_civitai_client, mock_get_tokens):
        """Test that 3-second rate limiting is applied after CivitAI API calls."""
        # Mock token service
        mock_get_tokens.return_value = {"civitai_token": "test_token"}
        
        # Mock CivitAI client
        mock_client = Mock()
        mock_civitai_client.return_value = mock_client
        mock_client.get_model_version_by_hash.return_value = None
        
        model_info = {
            "name": "unknown_model.safetensors",
            "path": self.test_model_path,
            "category": "other"
        }
        
        ModelScannerService._enhance_model_with_civitai(model_info)
        
        # Verify that sleep was called with 3 seconds for rate limiting
        mock_sleep.assert_called_once_with(3)
    
    @patch('back.services.model_scanner_service.TokenService.get_tokens')
    @patch('back.services.model_scanner_service.CivitAIClient')
    @patch('back.services.model_scanner_service.time.sleep')
    def test_enhance_model_with_civitai_single_api_call(self, mock_sleep, mock_civitai_client, mock_get_tokens):
        """Test that only one API call is made to CivitAI."""
        # Mock token service
        mock_get_tokens.return_value = {"civitai_token": "test_token"}
        
        # Mock CivitAI client
        mock_client = Mock()
        mock_civitai_client.return_value = mock_client
        mock_client.get_model_version_by_hash.return_value = None
        
        model_info = {
            "name": "unknown_model.safetensors",
            "path": self.test_model_path,
            "category": "other"
        }
        
        ModelScannerService._enhance_model_with_civitai(model_info)
        
        # Verify that only one API call was made
        self.assertEqual(mock_client.get_model_version_by_hash.call_count, 1)
        # Verify that sleep was called for rate limiting
        mock_sleep.assert_called_once_with(3)


if __name__ == '__main__':
    unittest.main()
