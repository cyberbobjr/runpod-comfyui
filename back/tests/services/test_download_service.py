import pytest
from unittest.mock import patch, MagicMock
from back.services.download_service import DownloadService


class TestDownloadService:
    """
    Test cases for the DownloadService class.
    
    **Description:** Unit tests for download service functionality.
    """
    
    def test_get_model_id(self):
        """
        Test model ID generation.
        
        **Description:** Verifies that model IDs are generated correctly.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        # Test with dest
        entry_with_dest = {"dest": "/path/to/model.safetensors"}
        model_id = DownloadService.get_model_id(entry_with_dest)
        assert model_id == "/path/to/model.safetensors"
        
        # Test with git
        entry_with_git = {"git": "https://github.com/user/repo.git"}
        model_id = DownloadService.get_model_id(entry_with_git)
        assert model_id == "https://github.com/user/repo.git"
    
    def test_get_progress_idle(self):
        """
        Test progress retrieval for idle models.
        
        **Description:** Verifies that idle models return correct progress.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        model_id = "non_existent_model"
        progress = DownloadService.get_progress(model_id)
        
        expected = {"progress": 0, "status": "idle"}
        assert progress == expected
    
    def test_stop_download_no_active(self):
        """
        Test stopping download when none is active.
        
        **Description:** Verifies behavior when trying to stop non-existent download.
        **Parameters:** None
        **Returns:** None (test assertion)
        """
        entry = {"dest": "/path/to/model.safetensors"}
        result = DownloadService.stop_download(entry)
        
        expected = {"ok": False, "msg": "No active download for this model"}
        assert result == expected
