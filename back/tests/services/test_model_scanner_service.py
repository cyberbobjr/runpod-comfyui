"""
Tests for the Model Scanner Service

These tests validate the model scanning functionality including:
- Directory scanning and model discovery
- Model categorization and classification
- File analysis and metadata extraction
- Advanced model identification
- Search functionality
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from back.services.model_scanner_service import ModelScannerService


class TestModelScannerService:
    """Test cases for ModelScannerService"""
    
    @pytest.fixture
    def temp_models_dir(self):
        """Create a temporary directory with mock model files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create model directory structure
            models_dir = os.path.join(temp_dir, "models")
            os.makedirs(models_dir)
            
            # Create subdirectories
            checkpoints_dir = os.path.join(models_dir, "checkpoints")
            vae_dir = os.path.join(models_dir, "vae")
            clip_dir = os.path.join(models_dir, "clip")
            loras_dir = os.path.join(models_dir, "loras")
            
            os.makedirs(checkpoints_dir)
            os.makedirs(vae_dir)
            os.makedirs(clip_dir)
            os.makedirs(loras_dir)
            
            # Create mock model files
            test_files = [
                os.path.join(checkpoints_dir, "model1.safetensors"),
                os.path.join(checkpoints_dir, "model2.ckpt"),
                os.path.join(vae_dir, "vae1.safetensors"),
                os.path.join(vae_dir, "vae2.sft"),
                os.path.join(clip_dir, "clip1.safetensors"),
                os.path.join(loras_dir, "lora1.safetensors"),
                os.path.join(loras_dir, "lora2.pt"),
            ]
            
            for file_path in test_files:
                with open(file_path, "w") as f:
                    f.write("mock model data")
            
            yield models_dir
    
    def test_identify_file_without_dependencies(self):
        """Test identify_file when torch/safetensors are not available"""
        with patch('back.services.model_scanner_service.TORCH_AVAILABLE', False), \
             patch('back.services.model_scanner_service.SAFETENSORS_AVAILABLE', False):
            
            result = ModelScannerService.identify_file("/fake/model.safetensors")
            assert result is None
            
            result = ModelScannerService.identify_file("/fake/model.ckpt")
            assert result is None
    
    @patch('back.services.model_scanner_service.TORCH_AVAILABLE', True)
    @patch('back.services.model_scanner_service.SAFETENSORS_AVAILABLE', True)
    def test_identify_file_with_mocked_torch(self):
        """Test identify_file with mocked torch loading"""
        with patch('back.services.model_scanner_service.torch') as mock_torch, \
             patch('back.services.model_scanner_service.safe_open') as mock_safe_open:
            
            # Mock checkpoint file
            mock_torch.load.return_value = {
                'model.diffusion_model.input_blocks.0.weight': 'data',
                'cond_stage_model.transformer.text_model.embeddings.position_embedding.weight': 'data',
                'first_stage_model.decoder.conv_out.weight': 'data'
            }
            
            result = ModelScannerService.identify_file("/fake/model.ckpt")
            assert result == 'checkpoint'
            
            # Mock LoRA file
            mock_torch.load.return_value = {
                'lora_down.weight': 'data',
                'lora_up.weight': 'data'
            }
            
            result = ModelScannerService.identify_file("/fake/lora.pt")
            assert result == 'lora'
    
    def test_map_identified_type_to_classification(self):
        """Test mapping of identified types to classification system"""
        assert ModelScannerService._map_identified_type_to_classification('checkpoint') == ['checkpoint', 'diffusion_loader']
        assert ModelScannerService._map_identified_type_to_classification('vae') == ['vae']
        assert ModelScannerService._map_identified_type_to_classification('lora') == ['lora']
        assert ModelScannerService._map_identified_type_to_classification('unknown') == ['unknown']
        assert ModelScannerService._map_identified_type_to_classification('nonexistent_type') == ['unknown']
    
    @patch('back.services.model_scanner_service.ConfigService.get_models_dir')
    def test_scan_models_directory_success(self, mock_get_models_dir, temp_models_dir):
        """Test successful model directory scanning"""
        mock_get_models_dir.return_value = temp_models_dir
        
        result = ModelScannerService.scan_models_directory()
        
        assert "error" not in result
        assert "models_directory" in result
        assert "total_models" in result
        assert "models" in result
        assert result["models_directory"] == temp_models_dir
        assert result["total_models"] > 0
        
        # Check that models are categorized
        models = result["models"]
        assert "checkpoints" in models
        assert "vae" in models
        assert "clip" in models
        assert "loras" in models
        
        # Check that we found the expected files
        assert len(models["checkpoints"]) >= 2
        assert len(models["vae"]) >= 2
        assert len(models["clip"]) >= 1
        assert len(models["loras"]) >= 2
    
    @patch('back.services.model_scanner_service.ConfigService.get_models_dir')
    def test_scan_models_directory_not_found(self, mock_get_models_dir):
        """Test scanning when models directory doesn't exist"""
        mock_get_models_dir.return_value = "/nonexistent/path"
        
        result = ModelScannerService.scan_models_directory()
        
        assert "error" in result
        assert "Models directory not found" in result["error"]
        assert "models" in result
        assert result["models"] == {}
    
    @patch('back.services.model_scanner_service.ConfigService.get_models_dir')
    def test_analyze_model_file(self, mock_get_models_dir, temp_models_dir):
        """Test individual model file analysis"""
        mock_get_models_dir.return_value = temp_models_dir
        
        # Test with a specific file
        test_file = os.path.join(temp_models_dir, "checkpoints", "model1.safetensors")
        
        result = ModelScannerService._analyze_model_file(test_file, temp_models_dir)
        
        assert result["name"] == "model1.safetensors"
        assert result["path"] == test_file
        assert result["relative_path"] == os.path.join("checkpoints", "model1.safetensors")
        assert result["subdirectory"] == "checkpoints"
        assert result["extension"] == ".safetensors"
        assert result["exists"] is True
        assert result["size"] > 0
        assert result["size_mb"] > 0
        assert isinstance(result["type"], list)
    
    def test_categorize_model(self):
        """Test model categorization logic"""
        models_dir = "/fake/models"
        
        # Test advanced identification takes priority
        category = ModelScannerService._categorize_model(
            "/fake/models/unknown/model.safetensors", 
            models_dir, 
            identified_type="checkpoint"
        )
        assert category == "checkpoints"
        
        # Test directory-based fallback
        category = ModelScannerService._categorize_model(
            "/fake/models/checkpoints/model.safetensors", 
            models_dir
        )
        assert category == "checkpoints"
        
        # Test VAE categorization
        vae_path = "/fake/models/vae/vae.safetensors"
        category = ModelScannerService._categorize_model(vae_path, models_dir, "vae")
        assert category == "vae"
        
        # Test CLIP categorization
        clip_path = "/fake/models/clip/clip.safetensors"
        category = ModelScannerService._categorize_model(clip_path, models_dir, "clip")
        assert category == "clip"
        
        # Test LoRA categorization
        lora_path = "/fake/models/loras/lora.safetensors"
        category = ModelScannerService._categorize_model(lora_path, models_dir, "lora")
        assert category == "loras"
        
        # Test unknown categorization
        unknown_path = "/fake/models/unknown/model.safetensors"
        category = ModelScannerService._categorize_model(unknown_path, models_dir, "unknown")
        assert category == "other"
    
    def test_determine_model_type(self):
        """Test model type determination"""
        # Test checkpoint types
        types = ModelScannerService._determine_model_type("/fake/checkpoints/model.safetensors", "checkpoints")
        assert "checkpoint" in types
        assert "diffusion_loader" in types
        
        # Test VAE types
        types = ModelScannerService._determine_model_type("/fake/vae/vae.safetensors", "vae")
        assert "vae" in types
        
        # Test CLIP types
        types = ModelScannerService._determine_model_type("/fake/clip/clip.safetensors", "clip")
        assert "clip" in types
        
        # Test LoRA types
        types = ModelScannerService._determine_model_type("/fake/loras/lora.safetensors", "loras")
        assert "lora" in types
        
        # Test filename-based detection
        types = ModelScannerService._determine_model_type("/fake/models/my_vae_model.safetensors", "models")
        assert "vae" in types
    
    @patch('back.services.model_scanner_service.ModelScannerService.scan_models_directory')
    def test_get_model_summary(self, mock_scan):
        """Test model summary generation"""
        # Mock scan results
        mock_scan.return_value = {
            "models_directory": "/fake/models",
            "total_models": 5,
            "models": {
                "checkpoints": [
                    {"name": "model1.safetensors", "size_mb": 2000.0},
                    {"name": "model2.ckpt", "size_mb": 1500.0}
                ],
                "vae": [
                    {"name": "vae1.safetensors", "size_mb": 500.0}
                ],
                "clip": [
                    {"name": "clip1.safetensors", "size_mb": 300.0}
                ],
                "loras": [
                    {"name": "lora1.safetensors", "size_mb": 100.0}
                ]
            }
        }
        
        result = ModelScannerService.get_model_summary()
        
        assert result["total_models"] == 5
        assert result["models_directory"] == "/fake/models"
        assert "categories" in result
        
        categories = result["categories"]
        assert "checkpoints" in categories
        assert categories["checkpoints"]["count"] == 2
        assert categories["checkpoints"]["total_size_mb"] == 3500.0
        
        assert "vae" in categories
        assert categories["vae"]["count"] == 1
        assert categories["vae"]["total_size_mb"] == 500.0
    
    @patch('back.services.model_scanner_service.ModelScannerService.scan_models_directory')
    def test_search_models(self, mock_scan):
        """Test model search functionality"""
        # Mock scan results
        mock_scan.return_value = {
            "models_directory": "/fake/models",
            "total_models": 4,
            "models": {
                "checkpoints": [
                    {"name": "stable_diffusion_v1.safetensors", "relative_path": "checkpoints/stable_diffusion_v1.safetensors"},
                    {"name": "realistic_vision.ckpt", "relative_path": "checkpoints/realistic_vision.ckpt"}
                ],
                "vae": [
                    {"name": "vae_stable.safetensors", "relative_path": "vae/vae_stable.safetensors"}
                ],
                "loras": [
                    {"name": "stable_lora.safetensors", "relative_path": "loras/stable_lora.safetensors"}
                ]
            }
        }
        
        # Test search without category filter
        result = ModelScannerService.search_models("stable")
        
        assert result["query"] == "stable"
        assert result["category"] is None
        assert result["total_matches"] == 3
        
        matches = result["matches"]
        assert "checkpoints" in matches
        assert "vae" in matches
        assert "loras" in matches
        assert len(matches["checkpoints"]) == 1
        assert len(matches["vae"]) == 1
        assert len(matches["loras"]) == 1
        
        # Test search with category filter
        result = ModelScannerService.search_models("stable", "checkpoints")
        
        assert result["query"] == "stable"
        assert result["category"] == "checkpoints"
        assert result["total_matches"] == 1
        
        matches = result["matches"]
        assert "checkpoints" in matches
        assert "vae" not in matches
        assert "loras" not in matches
    
    @patch('back.services.model_scanner_service.ModelScannerService.scan_models_directory')
    def test_search_models_with_error(self, mock_scan):
        """Test search when scan returns error"""
        mock_scan.return_value = {
            "error": "Models directory not found"
        }
        
        result = ModelScannerService.search_models("test")
        
        assert "error" in result
        assert result["error"] == "Models directory not found"
    
    def test_model_types_constants(self):
        """Test that model type constants are properly defined"""
        assert hasattr(ModelScannerService, 'MODEL_TYPES')
        assert hasattr(ModelScannerService, 'SUPPORTED_EXTENSIONS')
        
        model_types = ModelScannerService.MODEL_TYPES
        assert isinstance(model_types, dict)
        assert "checkpoints" in model_types
        assert "vae" in model_types
        assert "clip" in model_types
        assert "loras" in model_types
        
        extensions = ModelScannerService.SUPPORTED_EXTENSIONS
        assert isinstance(extensions, list)
        assert '.safetensors' in extensions
        assert '.sft' in extensions
        assert '.ckpt' in extensions
