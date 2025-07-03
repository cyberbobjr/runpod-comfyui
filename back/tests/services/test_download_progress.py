import unittest
from back.services.download_manager import DownloadProgress

class TestDownloadProgress(unittest.TestCase):
    def test_to_dict_and_from_dict(self):
        dp = DownloadProgress(progress=42, status="downloading", dest_path="/tmp/file.bin", finished_time=123.45, error="err")
        d = dp.to_dict()
        self.assertEqual(d["progress"], 42)
        self.assertEqual(d["status"], "downloading")
        self.assertEqual(d["dest_path"], "/tmp/file.bin")
        self.assertEqual(d["finished_time"], 123.45)
        self.assertEqual(d["error"], "err")
        dp2 = DownloadProgress.from_dict(d)
        self.assertEqual(dp2.progress, 42)
        self.assertEqual(dp2.status, "downloading")
        self.assertEqual(dp2.dest_path, "/tmp/file.bin")
        self.assertEqual(dp2.finished_time, 123.45)
        self.assertEqual(dp2.error, "err")

if __name__ == "__main__":
    unittest.main()
