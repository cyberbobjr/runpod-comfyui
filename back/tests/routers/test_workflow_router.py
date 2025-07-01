"""
Tests for the refactored workflow router

These tests validate that the workflow management API works correctly
after the refactoring from monolithic api_workflows.py to the new structure.
"""

import pytest
import tempfile
import json
import os
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, Mock

# Import the router to test
from back.routers.workflow_router import router as workflow_router


# Create a test app
def create_test_app():
    """Create a test FastAPI app with the workflow router."""
    app = FastAPI()
    app.include_router(workflow_router)
    return app


@pytest.fixture
def client():
    """Create a test client."""
    app = create_test_app()
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication for tests."""
    with patch("back.routers.workflow_router.protected") as mock_protected:
        mock_protected.return_value = {"user_id": "test_user"}
        yield mock_protected


@pytest.fixture
def temp_workflows_dir():
    """Create a temporary directory for workflow tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("back.services.workflow_service.ModelManager.get_workflows_dir") as mock_get_dir:
            mock_get_dir.return_value = temp_dir
            yield temp_dir


def test_list_workflows_empty(client, mock_auth, temp_workflows_dir):
    """Test listing workflows when directory is empty."""
    response = client.get("/api/workflows/")
    
    assert response.status_code == 200
    assert response.json() == []


def test_list_workflows_with_files(client, mock_auth, temp_workflows_dir):
    """Test listing workflows when directory contains files."""
    # Create test workflow files
    workflow1 = {"test": "workflow1"}
    workflow2 = {"test": "workflow2"}
    
    with open(os.path.join(temp_workflows_dir, "test1.json"), "w") as f:
        json.dump(workflow1, f)
    
    with open(os.path.join(temp_workflows_dir, "test2.json"), "w") as f:
        json.dump(workflow2, f)
    
    # Create a non-json file (should be ignored)
    with open(os.path.join(temp_workflows_dir, "readme.txt"), "w") as f:
        f.write("This is not a workflow")
    
    response = client.get("/api/workflows/")
    
    assert response.status_code == 200
    workflows = response.json()
    assert len(workflows) == 2
    assert "test1.json" in workflows
    assert "test2.json" in workflows
    assert "readme.txt" not in workflows


def test_get_workflow_content(client, mock_auth, temp_workflows_dir):
    """Test getting workflow content."""
    workflow_content = {"nodes": [], "links": [], "version": "1.0"}
    
    with open(os.path.join(temp_workflows_dir, "test.json"), "w") as f:
        json.dump(workflow_content, f)
    
    response = client.get("/api/workflows/test.json")
    
    assert response.status_code == 200
    assert response.json() == workflow_content


def test_get_workflow_not_found(client, mock_auth, temp_workflows_dir):
    """Test getting non-existent workflow."""
    response = client.get("/api/workflows/nonexistent.json")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_workflow(client, mock_auth, temp_workflows_dir):
    """Test deleting a workflow."""
    workflow_content = {"test": "workflow"}
    
    workflow_path = os.path.join(temp_workflows_dir, "test.json")
    with open(workflow_path, "w") as f:
        json.dump(workflow_content, f)
    
    assert os.path.exists(workflow_path)
    
    response = client.delete("/api/workflows/test.json")
    
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert "deleted successfully" in response.json()["message"]
    assert not os.path.exists(workflow_path)


def test_delete_workflow_not_found(client, mock_auth, temp_workflows_dir):
    """Test deleting non-existent workflow."""
    response = client.delete("/api/workflows/nonexistent.json")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_workflow_info(client, mock_auth, temp_workflows_dir):
    """Test getting workflow information."""
    workflow_content = {"test": "workflow"}
    
    with open(os.path.join(temp_workflows_dir, "test.json"), "w") as f:
        json.dump(workflow_content, f)
    
    response = client.get("/api/workflows/test.json/info")
    
    assert response.status_code == 200
    info = response.json()
    assert info["filename"] == "test.json"
    assert info["is_valid"] is True
    assert "size" in info
    assert "modified" in info


def test_workflow_validation_valid(client, mock_auth, temp_workflows_dir):
    """Test validating a valid workflow."""
    workflow_content = {"nodes": [], "links": []}
    
    with open(os.path.join(temp_workflows_dir, "test.json"), "w") as f:
        json.dump(workflow_content, f)
    
    response = client.get("/api/workflows/test.json/validate")
    
    assert response.status_code == 200
    validation = response.json()
    assert validation["is_valid"] is True
    assert len(validation["errors"]) == 0


def test_workflow_validation_invalid(client, mock_auth, temp_workflows_dir):
    """Test validating an invalid workflow."""
    # Create invalid JSON file
    with open(os.path.join(temp_workflows_dir, "invalid.json"), "w") as f:
        f.write("{ invalid json content")
    
    response = client.get("/api/workflows/invalid.json/validate")
    
    assert response.status_code == 200
    validation = response.json()
    assert validation["is_valid"] is False
    assert len(validation["errors"]) > 0


if __name__ == "__main__":
    # Run basic tests
    print("Running basic workflow router tests...")
    
    # Simple import test
    try:
        from back.routers.workflow_router import router
        print("✓ Workflow router import successful")
    except ImportError as e:
        print(f"✗ Workflow router import failed: {e}")
    
    # Service import test
    try:
        from back.services.workflow_service import WorkflowService
        print("✓ Workflow service import successful")
    except ImportError as e:
        print(f"✗ Workflow service import failed: {e}")
    
    # Models import test
    try:
        from back.models.workflow_models import WorkflowInfo
        print("✓ Workflow models import successful")
    except ImportError as e:
        print(f"✗ Workflow models import failed: {e}")
    
    print("Basic tests completed!")
