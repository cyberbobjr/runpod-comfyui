
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from back.services import download_manager

def print_test(msg):
    print(f"\n=== {msg} ===")

class TestDownloadManager(unittest.TestCase):
    """
    Unit tests for DownloadManager. Each test prints details to the console.
    """
    def setUp(self):
        print_test("setUp: Creating temp dir and dummy entry")
        self.base_dir = tempfile.mkdtemp()
        self.dummy_url = "https://example.com/model.bin"
        self.dummy_dest = os.path.join(self.base_dir, "model.bin")
        self.entry = {
            "url": self.dummy_url,
            "dest": self.dummy_dest
        }

    @patch("back.services.download_manager.requests.head")
    @patch("back.services.download_manager.requests.get")
    @patch("back.services.model_manager.ModelManager")
    def test_download_model_http_success(self, mock_model_manager, mock_get, mock_head):
        print_test("test_download_model_http_success: Simulate HTTP download")
        # Simulate HEAD response
        mock_head_resp = MagicMock()
        mock_head_resp.headers = {"content-length": "10"}
        mock_head_resp.raise_for_status = MagicMock()
        mock_head.return_value = mock_head_resp

        # Simulate GET response
        mock_get_resp = MagicMock()
        mock_get_resp.headers = {"content-length": "10"}
        mock_get_resp.status_code = 200
        mock_get_resp.raise_for_status = MagicMock()
        mock_get_resp.iter_content = MagicMock(return_value=[b"12345", b"67890"])
        mock_get_resp.__enter__.return_value = mock_get_resp
        mock_get.return_value = mock_get_resp

        # Simulate ModelManager.resolve_path
        mock_model_manager.resolve_path.side_effect = lambda path, base: path

        # Run download_model (synchronously)
        result = download_manager.DownloadManager.download_model(self.entry, self.base_dir, background=False)
        print(f"Result: {result}")
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["progress"], 100)
        self.assertTrue(os.path.exists(self.dummy_dest))
        with open(self.dummy_dest, "rb") as f:
            data = f.read()
            self.assertEqual(len(data), 10)

    @patch("back.services.download_manager.requests.head")
    @patch("back.services.model_manager.ModelManager")
    def test_download_model_file_already_exists(self, mock_model_manager, mock_head):
        print_test("test_download_model_file_already_exists: File already exists, should skip download")
        # Create a file with the expected size
        with open(self.dummy_dest, "wb") as f:
            f.write(b"0" * 10)
        # Simulate HEAD response
        mock_head_resp = MagicMock()
        mock_head_resp.headers = {"content-length": "10"}
        mock_head_resp.raise_for_status = MagicMock()
        mock_head.return_value = mock_head_resp
        # Simulate ModelManager.resolve_path
        mock_model_manager.resolve_path.side_effect = lambda path, base: path
        # Should skip download
        result = download_manager.DownloadManager.download_model(self.entry, self.base_dir, background=False)
        print(f"Result: {result}")
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["progress"], 100)

    def test_is_file_fully_downloaded(self):
        print_test("test_is_file_fully_downloaded: File exists and matches size")
        with open(self.dummy_dest, "wb") as f:
            f.write(b"1234567890")
        result = download_manager.DownloadManager.is_file_fully_downloaded(self.dummy_dest, 10)
        print(f"is_file_fully_downloaded result: {result}")
        self.assertTrue(result)

        print_test("test_is_file_fully_downloaded: File does not exist")
        os.remove(self.dummy_dest)
        result = download_manager.DownloadManager.is_file_fully_downloaded(self.dummy_dest, 10)
        print(f"is_file_fully_downloaded result: {result}")
        self.assertFalse(result)

    def test_get_progress(self):
        print_test("test_get_progress: Progress for non-existent model_id")
        result = download_manager.DownloadManager.get_progress("nonexistent")
        print(f"get_progress result: {result}")
        self.assertEqual(result["progress"], 0)
        self.assertEqual(result["status"], "idle")

    def test_get_all_progress(self):
        print_test("test_get_all_progress: No active downloads")
        result = download_manager.DownloadManager.get_all_progress()
        print(f"get_all_progress result: {result}")
        self.assertIsInstance(result, list)

    def test_stop_download(self):
        print_test("test_stop_download: Stop non-existent download")
        result = download_manager.DownloadManager.stop_download("nonexistent")
        print(f"stop_download result: {result}")
        self.assertFalse(result)

    def test_cleanup_finished_downloads(self):
        print_test("test_cleanup_finished_downloads: No finished downloads to clean up")
        result = download_manager.DownloadManager.cleanup_finished_downloads()
        print(f"cleanup_finished_downloads result: {result}")
        self.assertIsInstance(result, int)

    def tearDown(self):
        print_test("tearDown: Cleaning up temp dir")
        for root, dirs, files in os.walk(self.base_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.base_dir)

if __name__ == "__main__":
    unittest.main()
