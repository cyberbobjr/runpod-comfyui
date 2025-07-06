"""
Tests for the Model Scanner Router

These tests validate the model scanner API endpoints including:
- Model directory scanning
- Model summary statistics
- Model search functionality
- Category and type information
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, Mock

from back.routers.model_scanner_router import router as model_scanner_router


def create_test_app():
    """Create a test FastAPI app with the model scanner router."""
    app = FastAPI()
    app.include_router(model_scanner_router)
    return app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_test_app()
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for tests."""
    with patch("back.routers.model_scanner_router.protected") as mock_protected:
        mock_protected.return_value = {"user_id": "test_user"}
        yield mock_protected


class TestModelScannerRouter:
    """Test cases for ModelScannerRouter"""
    
    @patch('back.routers.model_scanner_router.ModelScannerService.scan_models_directory')
    def test_scan_models_directory_success(self, mock_scan, client, mock_auth):
        """Test successful model directory scanning"""
        # Mock successful scan results
        mock_scan.return_value = {
            "models_directory": "/fake/models",
            "total_models": 5,
            "models": {
                "checkpoints": [
                    {
                        "name": "model1.safetensors",
                        "path": "/fake/models/checkpoints/model1.safetensors",
                        "relative_path": "checkpoints/model1.safetensors",
                        "subdirectory": "checkpoints",
                        "size": 2000000000,
                        "size_mb": 2000.0,
                        "extension": ".safetensors",
                        "type": ["checkpoint", "diffusion_loader"],
                        "exists": True
                    }
                ],
                "vae": [
                    {
                        "name": "vae1.safetensors",
                        "path": "/fake/models/vae/vae1.safetensors",
                        "relative_path": "vae/vae1.safetensors",
                        "subdirectory": "vae",
                        "size": 500000000,
                        "size_mb": 500.0,
                        "extension": ".safetensors",
                        "type": ["vae"],
                        "exists": True
                    }
                ]
            }
        }
        
        response = client.get("/api/models/scanner/scan")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["models_directory"] == "/fake/models"
        assert data["total_models"] == 5
        assert "models" in data
        assert "checkpoints" in data["models"]
        assert "vae" in data["models"]
        assert len(data["models"]["checkpoints"]) == 1
        assert len(data["models"]["vae"]) == 1
        
        # Check model details
        checkpoint = data["models"]["checkpoints"][0]
        assert checkpoint["name"] == "model1.safetensors"
        assert checkpoint["type"] == ["checkpoint", "diffusion_loader"]
        assert checkpoint["size_mb"] == 2000.0
    
    @patch('back.routers.model_scanner_router.ModelScannerService.scan_models_directory')
    def test_scan_models_directory_error(self, mock_scan, client, mock_auth):
        """Test model directory scanning with error"""
        # Mock error result
        mock_scan.return_value = {
            "error": "Models directory not found: /fake/models"
        }
        
        response = client.get("/api/models/scanner/scan")
        
        assert response.status_code == 500
        data = response.json()
        assert "Models directory not found" in data["detail"]
    
    @patch('back.routers.model_scanner_router.ModelScannerService.get_model_summary')
    def test_get_model_summary_success(self, mock_summary, client, mock_auth):
        """Test successful model summary retrieval"""
        # Mock summary results
        mock_summary.return_value = {
            "total_models": 10,
            "models_directory": "/fake/models",
            "categories": {
                "checkpoints": {
                    "count": 5,
                    "total_size_mb": 10000.0
                },
                "vae": {
                    "count": 3,
                    "total_size_mb": 1500.0
                },
                "clip": {
                    "count": 2,
                    "total_size_mb": 600.0
                }
            }
        }
        
        response = client.get("/api/models/scanner/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_models"] == 10
        assert data["models_directory"] == "/fake/models"
        assert "categories" in data
        assert "checkpoints" in data["categories"]
        assert "vae" in data["categories"]
        assert "clip" in data["categories"]
        
        # Check category details
        checkpoints = data["categories"]["checkpoints"]
        assert checkpoints["count"] == 5
        assert checkpoints["total_size_mb"] == 10000.0
    
    @patch('back.routers.model_scanner_router.ModelScannerService.get_model_summary')
    def test_get_model_summary_error(self, mock_summary, client, mock_auth):
        """Test model summary with error"""
        # Mock error result
        mock_summary.return_value = {
            "error": "Error scanning models directory"
        }
        
        response = client.get("/api/models/scanner/summary")
        
        assert response.status_code == 500
        data = response.json()
        assert "Error scanning models directory" in data["detail"]
    
    @patch('back.routers.model_scanner_router.ModelScannerService.search_models')
    def test_search_models_success(self, mock_search, client, mock_auth):
        """Test successful model search"""
        # Mock search results
        mock_search.return_value = {
            "query": "stable",
            "category": None,
            "matches": {
                "checkpoints": [
                    {
                        "name": "stable_diffusion_v1.safetensors",
                        "path": "/fake/models/checkpoints/stable_diffusion_v1.safetensors",
                        "relative_path": "checkpoints/stable_diffusion_v1.safetensors",
                        "subdirectory": "checkpoints",
                        "size": 2000000000,
                        "size_mb": 2000.0,
                        "extension": ".safetensors",
                        "type": ["checkpoint", "diffusion_loader"],
                        "exists": True
                    }
                ],
                "loras": [
                    {
                        "name": "stable_lora.safetensors",
                        "path": "/fake/models/loras/stable_lora.safetensors",
                        "relative_path": "loras/stable_lora.safetensors",
                        "subdirectory": "loras",
                        "size": 100000000,
                        "size_mb": 100.0,
                        "extension": ".safetensors",
                        "type": ["lora"],
                        "exists": True
                    }
                ]
            },
            "total_matches": 2
        }
        
        response = client.get("/api/models/scanner/search?query=stable")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == "stable"
        assert data["category"] is None
        assert data["total_matches"] == 2
        assert "matches" in data
        assert "checkpoints" in data["matches"]
        assert "loras" in data["matches"]
        assert len(data["matches"]["checkpoints"]) == 1
        assert len(data["matches"]["loras"]) == 1
    
    @patch('back.routers.model_scanner_router.ModelScannerService.search_models')
    def test_search_models_with_category(self, mock_search, client, mock_auth):
        """Test model search with category filter"""
        # Mock search results
        mock_search.return_value = {
            "query": "stable",
            "category": "checkpoints",
            "matches": {
                "checkpoints": [
                    {
                        "name": "stable_diffusion_v1.safetensors",
                        "path": "/fake/models/checkpoints/stable_diffusion_v1.safetensors",
                        "relative_path": "checkpoints/stable_diffusion_v1.safetensors",
                        "subdirectory": "checkpoints",
                        "size": 2000000000,
                        "size_mb": 2000.0,
                        "extension": ".safetensors",
                        "type": ["checkpoint", "diffusion_loader"],
                        "exists": True
                    }
                ]
            },
            "total_matches": 1
        }
        
        response = client.get("/api/models/scanner/search?query=stable&category=checkpoints")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == "stable"
        assert data["category"] == "checkpoints"
        assert data["total_matches"] == 1
        assert "checkpoints" in data["matches"]
        assert len(data["matches"]) == 1  # Only checkpoints category
    
    def test_search_models_invalid_query(self, client, mock_auth):
        """Test model search with invalid query"""
        # Test with empty query
        response = client.get("/api/models/scanner/search?query=")
        assert response.status_code == 400
        
        # Test with very short query
        response = client.get("/api/models/scanner/search?query=a")
        assert response.status_code == 400
        
        # Test without query parameter
        response = client.get("/api/models/scanner/search")
        assert response.status_code == 422  # Validation error
    
    @patch('back.routers.model_scanner_router.ModelScannerService.search_models')
    def test_search_models_error(self, mock_search, client, mock_auth):
        """Test model search with error"""
        # Mock error result
        mock_search.return_value = {
            "error": "Error during search"
        }
        
        response = client.get("/api/models/scanner/search?query=test")
        
        assert response.status_code == 500
        data = response.json()
        assert "Error during search" in data["detail"]
    
    def test_get_model_categories(self, client, mock_auth):
        """Test getting model categories"""
        response = client.get("/api/models/scanner/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert "category_descriptions" in data
        assert isinstance(data["categories"], list)
        assert isinstance(data["category_descriptions"], dict)
        
        # Check that expected categories are present
        categories = data["categories"]
        assert "checkpoints" in categories
        assert "vae" in categories
        assert "clip" in categories
        assert "loras" in categories
        assert "other" in categories
        
        # Check that descriptions are provided
        descriptions = data["category_descriptions"]
        assert "checkpoints" in descriptions
        assert "vae" in descriptions
        assert "clip" in descriptions
        assert "loras" in descriptions
        assert "other" in descriptions
    
    def test_get_model_types(self, client, mock_auth):
        """Test getting model type information"""
        response = client.get("/api/models/scanner/types")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "supported_extensions" in data
        assert "model_classifications" in data
        assert "directory_mapping" in data
        
        # Check supported extensions
        extensions = data["supported_extensions"]
        assert isinstance(extensions, list)
        assert ".safetensors" in extensions
        assert ".sft" in extensions
        assert ".ckpt" in extensions
        
        # Check model classifications
        classifications = data["model_classifications"]
        assert isinstance(classifications, dict)
        assert "checkpoint" in classifications
        assert "vae" in classifications
        assert "clip" in classifications
        assert "diffusion_loader" in classifications
        
        # Check directory mapping
        directory_mapping = data["directory_mapping"]
        assert isinstance(directory_mapping, dict)
        assert "checkpoints" in directory_mapping
        assert "vae" in directory_mapping
        assert "clip" in directory_mapping
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        # Test without authentication
        with patch("back.routers.model_scanner_router.protected") as mock_protected:
            mock_protected.side_effect = Exception("Not authenticated")
            
            response = client.get("/api/models/scanner/scan")
            assert response.status_code == 500  # FastAPI converts unhandled exceptions to 500
            
            response = client.get("/api/models/scanner/summary")
            assert response.status_code == 500
            
            response = client.get("/api/models/scanner/search?query=test")
            assert response.status_code == 500
            
            response = client.get("/api/models/scanner/categories")
            assert response.status_code == 500
            
            response = client.get("/api/models/scanner/types")
            assert response.status_code == 500
