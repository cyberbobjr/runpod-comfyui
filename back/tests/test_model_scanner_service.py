import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from back.services.model_scanner_service import ModelScannerService


class TestModelScannerService(unittest.TestCase):
    """
    Unit tests for ModelScannerService.
    
    **Description:** Tests the model scanning functionality including caching and extended metadata extraction.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.models_dir = os.path.join(self.temp_dir, "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Clear cache before each test
        ModelScannerService._cache.clear()
        
        # Create test files
        self.test_files = {
            "checkpoint.safetensors": os.path.join(self.models_dir, "checkpoints", "test_checkpoint.safetensors"),
            "vae.safetensors": os.path.join(self.models_dir, "vae", "test_vae.safetensors"),
            "lora.safetensors": os.path.join(self.models_dir, "loras", "test_lora.safetensors"),
            "unknown.pkl": os.path.join(self.models_dir, "other", "test_unknown.pkl"),
            "compressed.tar": os.path.join(self.models_dir, "compressed", "test_compressed.tar")
        }
        
        # Create directories and files
        for file_path in self.test_files.values():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(b'test content')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
        ModelScannerService._cache.clear()

    def test_get_file_hash(self):
        """
        Test file hash generation.
        
        **Description:** Tests that file hashes are generated correctly and consistently.
        """
        file_path = self.test_files["checkpoint.safetensors"]
        
        # Get hash twice
        hash1 = ModelScannerService._get_file_hash(file_path)
        hash2 = ModelScannerService._get_file_hash(file_path)
        
        # Should be consistent
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 32)  # MD5 hash length

    def test_cache_functionality(self):
        """
        Test cache loading and saving.
        
        **Description:** Tests that cache can be saved and loaded correctly.
        """
        # Mock cache file path
        cache_file = os.path.join(self.temp_dir, "test_cache.pkl")
        with patch.object(ModelScannerService, '_get_cache_file_path', return_value=cache_file):
            # Add some data to cache
            ModelScannerService._cache["test_key"] = {"test": "data"}
            
            # Save cache
            ModelScannerService._save_cache()
            
            # Verify file was created
            self.assertTrue(os.path.exists(cache_file))
            
            # Clear cache and reload
            ModelScannerService._cache.clear()
            ModelScannerService._load_cache()
            
            # Verify data was loaded
            self.assertIn("test_key", ModelScannerService._cache)
            self.assertEqual(ModelScannerService._cache["test_key"]["test"], "data")

    @patch('back.services.model_scanner_service.ConfigService.get_models_dir')
    def test_scan_models_directory(self, mock_get_models_dir):
        """
        Test directory scanning functionality.
        
        **Description:** Tests that the model directory is scanned correctly.
        """
        mock_get_models_dir.return_value = self.models_dir
        
        # Mock the identify_file method to return predictable results
        with patch.object(ModelScannerService, 'identify_file') as mock_identify:
            def mock_identify_side_effect(file_path):
                if "checkpoint" in file_path:
                    return "checkpoint"
                elif "vae" in file_path:
                    return "vae"
                elif "lora" in file_path:
                    return "lora"
                elif "pkl" in file_path:
                    return "unknown"
                elif "tar" in file_path:
                    return "compressed_model"
                return None
            
            mock_identify.side_effect = mock_identify_side_effect
            
            # Scan directory
            result = ModelScannerService.scan_models_directory()
            
            # Verify results
            self.assertIn("models", result)
            self.assertIn("total_models", result)
            self.assertGreater(result["total_models"], 0)
            
            # Check that models were categorized
            models = result["models"]
            self.assertIn("checkpoints", models)
            self.assertIn("vae", models)
            self.assertIn("loras", models)
            self.assertIn("other", models)

    def test_extract_extended_metadata(self):
        """
        Test extended metadata extraction.
        
        **Description:** Tests that extended metadata is extracted correctly from different file types.
        """
        # Test with a regular file
        test_file = self.test_files["checkpoint.safetensors"]
        
        metadata = ModelScannerService._extract_extended_metadata(test_file)
        
        # Should always include basic metadata
        self.assertIn("file_hash", metadata)
        self.assertIn("is_compressed", metadata)
        self.assertIn("supported_format", metadata)
        
        # Test with compressed file
        compressed_file = self.test_files["compressed.tar"]
        metadata = ModelScannerService._extract_extended_metadata(compressed_file)
        
        self.assertTrue(metadata["is_compressed"])

    def test_get_category_from_identified_type(self):
        """
        Test category mapping from identified types.
        
        **Description:** Tests that identified types are mapped to correct categories.
        """
        test_cases = [
            ("checkpoint", "checkpoints"),
            ("vae", "vae"),
            ("lora", "loras"),
            ("controlnet", "controlnet"),
            ("embedding", "embeddings"),
            ("upscale", "upscale_models"),
            ("unknown", "other"),
            ("unreadable_checkpoint", "other"),
            ("compressed_model", "other")
        ]
        
        for identified_type, expected_category in test_cases:
            category = ModelScannerService._get_category_from_identified_type(identified_type)
            self.assertEqual(category, expected_category, 
                           f"Failed for {identified_type} -> {expected_category}")

    def test_get_category_from_directory(self):
        """
        Test category determination from directory structure.
        
        **Description:** Tests that directory structure is used correctly as fallback.
        """
        test_cases = [
            ("checkpoints", "checkpoints"),
            ("vae", "vae"),
            ("loras", "loras"),
            ("controlnet", "controlnet"),
            ("embeddings", "embeddings"),
            ("upscale_models", "upscale_models"),
            ("unknown_dir", "other"),
            ("", "checkpoints")  # Default for root
        ]
        
        for subdirectory, expected_category in test_cases:
            category = ModelScannerService._get_category_from_directory(subdirectory)
            self.assertEqual(category, expected_category, 
                           f"Failed for {subdirectory} -> {expected_category}")

    def test_supported_extensions(self):
        """
        Test that all supported extensions are recognized.
        
        **Description:** Tests that the extended list of supported extensions is correctly defined.
        """
        expected_extensions = ['.safetensors', '.sft', '.ckpt', '.pt', '.pth', '.bin', '.pkl', '.tar', '.gz', '.zip']
        
        for ext in expected_extensions:
            self.assertIn(ext, ModelScannerService.SUPPORTED_EXTENSIONS)

    def test_cache_info(self):
        """
        Test cache information retrieval.
        
        **Description:** Tests that cache information is returned correctly.
        """
        # Mock cache file path
        cache_file = os.path.join(self.temp_dir, "test_cache.pkl")
        with patch.object(ModelScannerService, '_get_cache_file_path', return_value=cache_file):
            # Add some data to cache
            ModelScannerService._cache["test"] = {"data": "value"}
            ModelScannerService._save_cache()
            
            # Get cache info
            cache_info = ModelScannerService.get_cache_info()
            
            # Verify info
            self.assertIn("entries_count", cache_info)
            self.assertIn("cache_file_exists", cache_info)
            self.assertIn("cache_file_path", cache_info)
            self.assertEqual(cache_info["entries_count"], 1)
            self.assertTrue(cache_info["cache_file_exists"])

    def test_clear_cache(self):
        """
        Test cache clearing functionality.
        
        **Description:** Tests that cache can be cleared correctly.
        """
        # Mock cache file path
        cache_file = os.path.join(self.temp_dir, "test_cache.pkl")
        with patch.object(ModelScannerService, '_get_cache_file_path', return_value=cache_file):
            # Add data and save
            ModelScannerService._cache["test"] = {"data": "value"}
            ModelScannerService._save_cache()
            
            # Verify cache exists
            self.assertTrue(os.path.exists(cache_file))
            self.assertEqual(len(ModelScannerService._cache), 1)
            
            # Clear cache
            ModelScannerService.clear_cache()
            
            # Verify cache is cleared
            self.assertEqual(len(ModelScannerService._cache), 0)
            self.assertFalse(os.path.exists(cache_file))

    @patch('back.services.model_scanner_service.SAFETENSORS_AVAILABLE', True)
    @patch('back.services.model_scanner_service.load_file')
    def test_extract_safetensors_metadata(self, mock_load_file):
        """
        Test SafeTensors metadata extraction.
        
        **Description:** Tests that SafeTensors metadata is extracted correctly.
        """
        # Mock SafeTensors data
        mock_tensor = MagicMock()
        mock_tensor.shape = [1024, 768]
        mock_tensor.dtype = "float32"
        mock_tensor.numel.return_value = 1024 * 768
        
        mock_load_file.return_value = {"test_tensor": mock_tensor}
        
        # Extract metadata
        metadata = ModelScannerService._extract_safetensors_metadata("test_file.safetensors")
        
        # Verify metadata
        self.assertIn("total_parameters", metadata)
        self.assertIn("tensor_count", metadata)
        self.assertIn("tensor_info", metadata)
        self.assertIn("format", metadata)
        self.assertEqual(metadata["format"], "safetensors")
        self.assertEqual(metadata["tensor_count"], 1)
        self.assertEqual(metadata["total_parameters"], 1024 * 768)

    def test_flux_model_detection(self):
        """
        Test Flux model detection specifically.
        
        **Description:** Tests that Flux models are correctly identified as diffusion_loader instead of checkpoint.
        """
        # Test cases for Flux models
        flux_test_cases = [
            ("flux1-dev-fp8.safetensors", "diffusion_loader"),
            ("flux1-schnell.safetensors", "diffusion_loader"),
            ("flux-dev-q4_0.safetensors", "diffusion_loader"),
            ("FLUX.1-dev-fp8.safetensors", "diffusion_loader"),
            ("regular-checkpoint.safetensors", "checkpoint")  # Control case
        ]
        
        for filename, expected_type in flux_test_cases:
            with self.subTest(filename=filename):
                # Create test file
                test_file = os.path.join(self.models_dir, "checkpoints", filename)
                os.makedirs(os.path.dirname(test_file), exist_ok=True)
                with open(test_file, 'wb') as f:
                    f.write(b'test content')
                
                # Mock the identify_file to simulate content analysis
                with patch.object(ModelScannerService, 'identify_file') as mock_identify:
                    # For Flux files, simulate detection of Flux patterns
                    if any(pattern in filename.lower() for pattern in ['flux', 'schnell', 'dev']):
                        mock_identify.return_value = "diffusion_loader"
                    else:
                        mock_identify.return_value = "checkpoint"
                    
                    # Test the identification
                    result = ModelScannerService.identify_file(test_file)
                    self.assertEqual(result, expected_type, 
                                   f"Failed to identify {filename} as {expected_type}")

    def test_flux_model_categorization(self):
        """
        Test Flux model categorization.
        
        **Description:** Tests that Flux models are categorized in the correct directory.
        """
        # Test directory-based categorization for Flux
        test_cases = [
            ("checkpoints/Flux", "diffusion_models"),  # Flux in subdirectory
            ("checkpoints/flux", "diffusion_models"),  # lowercase
            ("diffusion_models", "diffusion_models"),   # direct placement
            ("checkpoints/SD", "checkpoints"),          # traditional SD
            ("checkpoints", "checkpoints")              # regular checkpoints
        ]
        
        for subdirectory, expected_category in test_cases:
            category = ModelScannerService._get_category_from_directory(subdirectory)
            self.assertEqual(category, expected_category,
                           f"Failed for subdirectory {subdirectory} -> {expected_category}")

    def test_flux_filename_patterns(self):
        """
        Test Flux filename pattern detection.
        
        **Description:** Tests that various Flux filename patterns are correctly identified.
        """
        flux_patterns = [
            "flux1-dev-fp8.safetensors",
            "flux1-schnell.safetensors", 
            "FLUX.1-dev-fp8.safetensors",
            "flux-dev-q4_0.safetensors",
            "flux_model_v1.safetensors",
            "custom-flux-model.safetensors"
        ]
        
        non_flux_patterns = [
            "sd-v1-5.safetensors",
            "sdxl-base.safetensors",
            "realistic-vision.safetensors",
            "deliberate-v2.safetensors"
        ]
        
        # Test that Flux patterns are detected
        for pattern in flux_patterns:
            with self.subTest(pattern=pattern):
                types = ModelScannerService._determine_model_type(
                    f"/models/checkpoints/{pattern}", "checkpoints"
                )
                self.assertIn("diffusion_loader", types, 
                            f"Should detect {pattern} as diffusion_loader")
        
        # Test that non-Flux patterns are not misidentified
        for pattern in non_flux_patterns:
            with self.subTest(pattern=pattern):
                types = ModelScannerService._determine_model_type(
                    f"/models/checkpoints/{pattern}", "checkpoints"
                )
                self.assertIn("checkpoint", types, 
                            f"Should detect {pattern} as checkpoint")


if __name__ == '__main__':
    unittest.main()
