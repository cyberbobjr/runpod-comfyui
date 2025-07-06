"""
Tests for the ComfyUI router

These tests validate that the ComfyUI workflow generation and execution API works correctly.
Tests cover workflow generation, execution, model registry, and status checking.
"""

import pytest
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, Mock, MagicMock

# Import the router to test
from back.routers.comfy_router import router as comfy_router
from back.services.comfy_workflow_builder import GenerationParams, LoRA


# Create a test app
def create_test_app():
    """Create a test FastAPI app with the comfy router."""
    app = FastAPI()
    app.include_router(comfy_router)
    return app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_test_app()
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for tests."""
    with patch("back.routers.comfy_router.protected") as mock_protected:
        mock_protected.return_value = {"user_id": "test_user"}
        yield mock_protected


@pytest.fixture
def mock_comfy_client():
    """Mock ComfyClient for tests."""
    with patch("back.routers.comfy_router.comfy_client") as mock_client:
        mock_client.send_prompt.return_value = "test_prompt_id"
        mock_client.wait_for_completion.return_value = {
            "outputs": {
                "9": {
                    "images": [
                        {"filename": "ComfyUI_00001_.png"},
                        {"filename": "ComfyUI_00002_.png"}
                    ]
                }
            }
        }
        mock_client.get_output_images.return_value = [
            "ComfyUI_00001_.png",
            "ComfyUI_00002_.png"
        ]
        mock_client.base_url = "http://127.0.0.1:8188"
        yield mock_client


@pytest.fixture
def sample_generation_params():
    """Sample generation parameters for testing."""
    return GenerationParams(
        model_key="sdxl",
        prompt="A beautiful landscape",
        negative_prompt="blurry, low quality",
        sampler="euler",
        steps=20,
        cfg=7.5,
        width=1024,
        height=1024,
        seed=42
    )


@pytest.fixture
def sample_loras():
    """Sample LoRA list for testing."""
    return [
        LoRA(name="lora1.safetensors", strength=0.8),
        LoRA(name="lora2.safetensors", strength=0.6)
    ]


class TestComfyRouterModels:
    """Test model registry endpoints."""

    def test_get_available_models_success(self, client, mock_auth):
        """Test successful retrieval of available models."""
        response = client.get("/api/comfy/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "sdxl" in data["models"]
        assert "flux-dev" in data["models"]
        assert "hivision" in data["models"]

    def test_get_available_models_unauthorized(self, client):
        """Test unauthorized access to models endpoint."""
        with patch("back.routers.comfy_router.protected", side_effect=Exception("Unauthorized")):
            response = client.get("/api/comfy/models")
            assert response.status_code == 500


class TestComfyRouterWorkflowGeneration:
    """Test workflow generation endpoints."""

    def test_generate_workflow_basic(self, client, mock_auth, sample_generation_params):
        """Test basic workflow generation."""
        response = client.post(
            "/api/comfy/workflow/generate",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data
        assert "prompt" in data["workflow"]

    def test_generate_workflow_with_loras(self, client, mock_auth, sample_generation_params, sample_loras):
        """Test workflow generation with LoRAs."""
        # Update params with LoRAs
        sample_generation_params.loras = sample_loras
        
        response = client.post(
            "/api/comfy/workflow/generate",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data

    def test_generate_workflow_with_controlnet(self, client, mock_auth, sample_generation_params):
        """Test workflow generation with ControlNet."""
        # Update params with ControlNet settings
        sample_generation_params.controlnet_image = "/path/to/image.jpg"
        sample_generation_params.controlnet_preprocessor = "canny"
        sample_generation_params.controlnet_model = "control_canny.safetensors"
        
        response = client.post(
            "/api/comfy/workflow/generate",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data

    def test_generate_workflow_invalid_model(self, client, mock_auth):
        """Test workflow generation with invalid model."""
        invalid_params = GenerationParams(
            model_key="invalid_model",
            prompt="Test prompt"
        )
        
        response = client.post(
            "/api/comfy/workflow/generate",
            json=invalid_params.dict()
        )
        
        assert response.status_code == 400
        assert "Unknown model key" in response.json()["detail"]


class TestComfyRouterWorkflowExecution:
    """Test workflow execution endpoints."""

    def test_execute_workflow_success(self, client, mock_auth, mock_comfy_client):
        """Test successful workflow execution."""
        workflow = {"prompt": {"test": "workflow"}}
        
        response = client.post(
            "/api/comfy/workflow/execute",
            json=workflow
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prompt_id" in data
        assert "images" in data
        assert "result" in data
        assert data["prompt_id"] == "test_prompt_id"
        assert len(data["images"]) == 2

    def test_execute_workflow_timeout(self, client, mock_auth):
        """Test workflow execution timeout."""
        with patch("back.routers.comfy_router.comfy_client") as mock_client:
            mock_client.send_prompt.return_value = "test_prompt_id"
            mock_client.wait_for_completion.side_effect = TimeoutError("Timeout")
            
            workflow = {"prompt": {"test": "workflow"}}
            response = client.post(
                "/api/comfy/workflow/execute",
                json=workflow
            )
            
            assert response.status_code == 504
            assert "timeout" in response.json()["detail"].lower()

    def test_execute_workflow_connection_error(self, client, mock_auth):
        """Test workflow execution with connection error."""
        import requests
        
        with patch("back.routers.comfy_router.comfy_client") as mock_client:
            mock_client.send_prompt.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            workflow = {"prompt": {"test": "workflow"}}
            response = client.post(
                "/api/comfy/workflow/execute",
                json=workflow
            )
            
            assert response.status_code == 500
            assert "unavailable" in response.json()["detail"].lower()


class TestComfyRouterGenerateAndExecute:
    """Test combined generation and execution endpoint."""

    def test_generate_and_execute_success(self, client, mock_auth, mock_comfy_client, sample_generation_params):
        """Test successful workflow generation and execution."""
        response = client.post(
            "/api/comfy/generate-and-execute",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prompt_id" in data
        assert "workflow" in data
        assert "images" in data
        assert "result" in data
        assert data["prompt_id"] == "test_prompt_id"
        assert len(data["images"]) == 2

    def test_generate_and_execute_invalid_model(self, client, mock_auth, mock_comfy_client):
        """Test generate and execute with invalid model."""
        invalid_params = GenerationParams(
            model_key="invalid_model",
            prompt="Test prompt"
        )
        
        response = client.post(
            "/api/comfy/generate-and-execute",
            json=invalid_params.dict()
        )
        
        assert response.status_code == 400
        assert "Unknown model key" in response.json()["detail"]

    def test_generate_and_execute_with_options(self, client, mock_auth, mock_comfy_client, sample_generation_params):
        """Test generate and execute with various options."""
        # Update params with options
        sample_generation_params.init_image = "/path/to/init.jpg"
        sample_generation_params.outpaint_padding = 128
        sample_generation_params.wait = True
        
        response = client.post(
            "/api/comfy/generate-and-execute",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data
        assert "images" in data

    def test_generate_and_execute_no_wait(self, client, mock_auth, mock_comfy_client, sample_generation_params):
        """Test generate and execute with wait=False."""
        # Set wait to False for immediate return
        sample_generation_params.wait = False
        
        response = client.post(
            "/api/comfy/generate-and-execute",
            json=sample_generation_params.dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
        assert "prompt_id" in data
        # Should not have images when wait=False
        assert "images" not in data


class TestComfyRouterStatus:
    """Test status checking endpoints."""

    def test_get_status_success(self, client, mock_auth):
        """Test successful status check."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"system": "stats"}
        
        with patch("back.routers.comfy_router.requests.get", return_value=mock_response):
            response = client.get("/api/comfy/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "available"
            assert "base_url" in data
            assert "system_stats" in data

    def test_get_status_unavailable(self, client, mock_auth):
        """Test status check when ComfyUI is unavailable."""
        import requests
        
        with patch("back.routers.comfy_router.requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")):
            response = client.get("/api/comfy/status")
            
            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()


class TestComfyRouterErrorHandling:
    """Test error handling across all endpoints."""

    def test_authentication_required(self, client):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("GET", "/api/comfy/models"),
            ("GET", "/api/comfy/status"),
            ("GET", "/api/comfy/result/test_prompt_id"),
            ("POST", "/api/comfy/workflow/generate"),
            ("POST", "/api/comfy/workflow/execute"),
            ("POST", "/api/comfy/generate-and-execute")
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            # Should fail due to missing authentication
            assert response.status_code in [401, 422, 500]  # Various auth failure codes

    def test_invalid_json_payload(self, client, mock_auth):
        """Test handling of invalid JSON payloads."""
        response = client.post(
            "/api/comfy/workflow/generate",
            json={"invalid": "payload"}
        )
        
        assert response.status_code == 422  # Validation error


class TestComfyRouterResultRetrieval:
    """Test result retrieval endpoints."""

    def test_get_result_by_prompt_id_success(self, client, mock_auth):
        """Test successful result retrieval by prompt_id."""
        prompt_id = "test_prompt_123"
        mock_history = {
            prompt_id: {
                "outputs": {
                    "9": {
                        "images": [
                            {"filename": "ComfyUI_00001_.png"},
                            {"filename": "ComfyUI_00002_.png"}
                        ]
                    }
                },
                "status": {"status_str": "completed"}
            }
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_history
        
        with patch("back.routers.comfy_router.requests.get", return_value=mock_response):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["prompt_id"] == prompt_id
            assert "images" in data
            assert len(data["images"]) == 2
            assert "result" in data
            assert data["status"] == "completed"
            
            # Check image URL format
            for image_url in data["images"]:
                assert "view?filename=" in image_url
                assert image_url.startswith("http://127.0.0.1:8188")

    def test_get_result_by_prompt_id_not_found(self, client, mock_auth):
        """Test result retrieval with non-existent prompt_id."""
        prompt_id = "non_existent_prompt"
        mock_history = {}  # Empty history
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_history
        
        with patch("back.routers.comfy_router.requests.get", return_value=mock_response):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 404
            assert "not found in history" in response.json()["detail"].lower()

    def test_get_result_by_prompt_id_no_images(self, client, mock_auth):
        """Test result retrieval for prompt with no images."""
        prompt_id = "test_prompt_no_images"
        mock_history = {
            prompt_id: {
                "outputs": {
                    "1": {
                        "text": ["some text output"]  # No images key
                    }
                },
                "status": {"status_str": "completed"}
            }
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_history
        
        with patch("back.routers.comfy_router.requests.get", return_value=mock_response):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["prompt_id"] == prompt_id
            assert data["images"] == []  # Empty images list
            assert "result" in data

    def test_get_result_by_prompt_id_comfy_unavailable(self, client, mock_auth):
        """Test result retrieval when ComfyUI is unavailable."""
        import requests
        
        prompt_id = "test_prompt_123"
        
        with patch("back.routers.comfy_router.requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()

    def test_get_result_by_prompt_id_server_error(self, client, mock_auth):
        """Test result retrieval with server error."""
        prompt_id = "test_prompt_123"
        
        with patch("back.routers.comfy_router.requests.get", side_effect=Exception("Server error")):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 500
            assert "error retrieving result" in response.json()["detail"].lower()

    def test_get_result_by_prompt_id_multiple_nodes(self, client, mock_auth):
        """Test result retrieval with multiple output nodes."""
        prompt_id = "test_prompt_multi"
        mock_history = {
            prompt_id: {
                "outputs": {
                    "9": {
                        "images": [
                            {"filename": "ComfyUI_00001_.png"}
                        ]
                    },
                    "10": {
                        "images": [
                            {"filename": "ComfyUI_00002_.png"},
                            {"filename": "ComfyUI_00003_.png"}
                        ]
                    }
                },
                "status": {"status_str": "completed"}
            }
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_history
        
        with patch("back.routers.comfy_router.requests.get", return_value=mock_response):
            response = client.get(f"/api/comfy/result/{prompt_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["images"]) == 3  # Total from both nodes
            
            # Check all images are present
            filenames = [url.split("filename=")[1] for url in data["images"]]
            assert "ComfyUI_00001_.png" in filenames
            assert "ComfyUI_00002_.png" in filenames
            assert "ComfyUI_00003_.png" in filenames
