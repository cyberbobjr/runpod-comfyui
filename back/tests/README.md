# Test for DownloadManager

- **Location:** `/back/tests/test_download_manager.py`
- **Goal:** Provide unit tests for the DownloadManager service, including HTTP/HTTPS download logic with mocked network requests. Ensures no real network calls are made and verifies correct file creation, skipping, and progress reporting behaviors.
- **Test file:** `/back/tests/test_download_manager.py`

This test covers:
- Simulated HTTP/HTTPS downloads (mocked requests)
- File existence and skipping logic
- Progress and status reporting
- Integration with ModelManager path resolution
