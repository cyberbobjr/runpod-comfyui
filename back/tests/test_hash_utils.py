import unittest
import tempfile
import os
from back.utils.hash_utils import HashUtils


class TestHashUtils(unittest.TestCase):
    """
    Test suite for HashUtils utility class.
    
    **Purpose:** Tests various hashing algorithms for model files including
    CivitAI-specific hash algorithms (AutoV1, AutoV2) and standard algorithms.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files of different sizes
        self.small_file = os.path.join(self.temp_dir, "small.bin")
        self.large_file = os.path.join(self.temp_dir, "large.bin")
        
        # Small file (less than 8KB)
        with open(self.small_file, 'wb') as f:
            f.write(b"A" * 1024)  # 1KB file
        
        # Large file (more than 16KB)
        with open(self.large_file, 'wb') as f:
            f.write(b"B" * 10240)  # 10KB of 'B's
            f.write(b"C" * 10240)  # 10KB of 'C's in the middle
            f.write(b"D" * 10240)  # 10KB of 'D's at the end
    
    def tearDown(self):
        """Clean up test fixtures."""
        for file_path in [self.small_file, self.large_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)
    
    def test_autov1_small_file(self):
        """Test AutoV1 algorithm with small file."""
        hash_result = HashUtils.get_file_hash(self.small_file, 'AutoV1')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_autov1_large_file(self):
        """Test AutoV1 algorithm with large file."""
        hash_result = HashUtils.get_file_hash(self.large_file, 'AutoV1')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_autov2_small_file(self):
        """Test AutoV2 algorithm with small file."""
        hash_result = HashUtils.get_file_hash(self.small_file, 'AutoV2')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_autov2_large_file(self):
        """Test AutoV2 algorithm with large file."""
        hash_result = HashUtils.get_file_hash(self.large_file, 'AutoV2')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_autov1_vs_autov2_difference(self):
        """Test that AutoV1 and AutoV2 produce different hashes for large files."""
        autov1_hash = HashUtils.get_file_hash(self.large_file, 'AutoV1')
        autov2_hash = HashUtils.get_file_hash(self.large_file, 'AutoV2')
        
        self.assertNotEqual(autov1_hash, autov2_hash)
    
    def test_autov1_vs_autov2_same_for_small_files(self):
        """Test that AutoV1 and AutoV2 produce same hashes for small files."""
        autov1_hash = HashUtils.get_file_hash(self.small_file, 'AutoV1')
        autov2_hash = HashUtils.get_file_hash(self.small_file, 'AutoV2')
        
        # For files smaller than 8KB, AutoV1 and AutoV2 should be the same
        self.assertEqual(autov1_hash, autov2_hash)
    
    def test_sha256_algorithm(self):
        """Test SHA256 algorithm."""
        hash_result = HashUtils.get_file_hash(self.small_file, 'SHA256')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)  # SHA256 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_crc32_algorithm(self):
        """Test CRC32 algorithm."""
        hash_result = HashUtils.get_file_hash(self.small_file, 'CRC32')
        
        self.assertIsNotNone(hash_result)
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 8)  # CRC32 hex length
        self.assertTrue(hash_result.isupper())  # Should be uppercase
    
    def test_blake3_algorithm(self):
        """Test Blake3 algorithm if available."""
        try:
            hash_result = HashUtils.get_file_hash(self.small_file, 'Blake3')
            
            if hash_result is not None:  # Blake3 is available
                self.assertIsInstance(hash_result, str)
                self.assertEqual(len(hash_result), 64)  # Blake3 hex length
                self.assertTrue(hash_result.isupper())  # Should be uppercase
        except ImportError:
            # Blake3 not available, test should pass
            pass
    
    def test_unsupported_algorithm(self):
        """Test unsupported algorithm returns None."""
        hash_result = HashUtils.get_file_hash(self.small_file, 'UNSUPPORTED')
        self.assertIsNone(hash_result)
    
    def test_nonexistent_file(self):
        """Test non-existent file returns None."""
        hash_result = HashUtils.get_file_hash("/non/existent/file.bin", 'AutoV2')
        self.assertIsNone(hash_result)
    
    def test_multiple_hashes_default(self):
        """Test multiple hashes with default algorithms."""
        results = HashUtils.get_multiple_hashes(self.small_file)
        
        self.assertIsInstance(results, dict)
        self.assertIn('AutoV2', results)
        self.assertIn('SHA256', results)
        self.assertEqual(len(results), 2)
    
    def test_multiple_hashes_custom_algorithms(self):
        """Test multiple hashes with custom algorithms."""
        algorithms = ['AutoV1', 'AutoV2', 'SHA256', 'CRC32']
        results = HashUtils.get_multiple_hashes(self.small_file, algorithms)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 4)
        
        for algo in algorithms:
            self.assertIn(algo, results)
            self.assertIsInstance(results[algo], str)
    
    def test_multiple_hashes_with_unsupported(self):
        """Test multiple hashes with mix of supported and unsupported algorithms."""
        algorithms = ['AutoV2', 'UNSUPPORTED', 'SHA256']
        results = HashUtils.get_multiple_hashes(self.small_file, algorithms)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 2)  # Only supported algorithms
        self.assertIn('AutoV2', results)
        self.assertIn('SHA256', results)
        self.assertNotIn('UNSUPPORTED', results)
    
    def test_hash_consistency(self):
        """Test that hashes are consistent across multiple calls."""
        file_path = self.small_file
        
        # Generate same hash multiple times
        hash1 = HashUtils.get_file_hash(file_path, 'AutoV2')
        hash2 = HashUtils.get_file_hash(file_path, 'AutoV2')
        hash3 = HashUtils.get_file_hash(file_path, 'AutoV2')
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash2, hash3)
    
    def test_supported_algorithms_constant(self):
        """Test that supported algorithms constant is properly defined."""
        expected_algorithms = ['AutoV1', 'AutoV2', 'SHA256', 'CRC32', 'Blake3']
        self.assertEqual(HashUtils.SUPPORTED_ALGORITHMS, expected_algorithms)
    
    def test_empty_file(self):
        """Test hashing of empty file."""
        empty_file = os.path.join(self.temp_dir, "empty.bin")
        with open(empty_file, 'wb') as f:
            pass  # Create empty file
        
        try:
            hash_result = HashUtils.get_file_hash(empty_file, 'AutoV2')
            self.assertIsNotNone(hash_result)
            self.assertIsInstance(hash_result, str)
            self.assertEqual(len(hash_result), 64)
        finally:
            if os.path.exists(empty_file):
                os.remove(empty_file)


if __name__ == '__main__':
    unittest.main()
