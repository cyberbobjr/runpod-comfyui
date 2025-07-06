import hashlib
import logging
from typing import Optional
from pathlib import Path

# Initialize logger
logger = logging.getLogger(__name__)

# Try to import blake3 if available
try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False
    logger.debug("blake3 not available, using standard hashlib algorithms")

# Try to import zlib for CRC32
try:
    import zlib
    CRC32_AVAILABLE = True
except ImportError:
    CRC32_AVAILABLE = False
    logger.debug("zlib not available, CRC32 will not be supported")


class HashUtils:
    """
    Utility class for file hashing operations.
    
    **Purpose:** Provides various hashing algorithms for model files including:
    - AutoV1 and AutoV2 (CivitAI specific algorithms)
    - SHA256 (standard secure hash)
    - CRC32 (fast checksum)
    - Blake3 (modern fast hash)
    
    **SRP Responsibility:** File hashing operations only.
    """
    
    SUPPORTED_ALGORITHMS = ['AutoV1', 'AutoV2', 'SHA256', 'CRC32', 'Blake3']
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'AutoV2') -> Optional[str]:
        """
        Generates a hash for a file using the specified algorithm.
        
        **Description:** Creates a hash of a file using CivitAI compatible algorithms.
        **Parameters:**
        - `file_path` (str): Path to the file to hash
        - `algorithm` (str): Hash algorithm to use ('AutoV1', 'AutoV2', 'SHA256', 'CRC32', 'Blake3')
        **Returns:** str containing the file hash or None if failed
        """
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            return None


        if algorithm not in HashUtils.SUPPORTED_ALGORITHMS:
            logger.error(f"Unsupported algorithm: {algorithm}. Supported: {HashUtils.SUPPORTED_ALGORITHMS}")
            return None
        
        try:
            if algorithm == 'AutoV1':
                return HashUtils._hash_autov1(file_path)
            elif algorithm == 'AutoV2':
                return HashUtils._hash_autov2(file_path)
            elif algorithm == 'SHA256':
                return HashUtils._hash_sha256(file_path)
            elif algorithm == 'CRC32':
                return HashUtils._hash_crc32(file_path)
            elif algorithm == 'Blake3':
                return HashUtils._hash_blake3(file_path)
        except Exception as e:
            logger.error(f"Error hashing file {file_path} with {algorithm}: {str(e)}")
            return None
    
    @staticmethod
    def _hash_autov1(file_path: str) -> str:
        """
        CivitAI AutoV1 hashing algorithm.
        
        **Description:** Implements CivitAI's AutoV1 algorithm (SHA256 of first 8KB).
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the AutoV1 hash
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read first 8KB (8192 bytes)
            chunk = f.read(8192)
            if chunk:
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest().upper()
    
    @staticmethod
    def _hash_autov2(file_path: str) -> str:
        """
        CivitAI AutoV2 hashing algorithm.
        
        **Description:** Implements CivitAI's AutoV2 algorithm (SHA256 of header + footer).
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the AutoV2 hash
        """
        import hashlib

        with open(file_path, "rb") as file:
            m = hashlib.sha256()
            file.seek(0x100000)  # Skip the first 1MB
            m.update(file.read(0x10000))  # Read the next 64KB
            return m.hexdigest()[:8].upper()  # Return the first 8 characters of the hash
    
    @staticmethod
    def _hash_sha256(file_path: str) -> str:
        """
        Standard SHA256 hash of entire file.
        
        **Description:** Computes SHA256 hash of the complete file.
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the SHA256 hash
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest().upper()
    
    @staticmethod
    def _hash_crc32(file_path: str) -> str:
        """
        CRC32 checksum of entire file.
        
        **Description:** Computes CRC32 checksum of the complete file.
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the CRC32 checksum
        """
        if not CRC32_AVAILABLE:
            raise ImportError("zlib not available for CRC32")
        
        crc = 0
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                crc = zlib.crc32(chunk, crc)
        
        # Convert to unsigned 32-bit integer and format as hex
        return f"{crc & 0xffffffff:08X}"
    
    @staticmethod
    def _hash_blake3(file_path: str) -> str:
        """
        Blake3 hash of entire file.
        
        **Description:** Computes Blake3 hash of the complete file.
        **Parameters:**
        - `file_path` (str): Path to the file
        **Returns:** str containing the Blake3 hash
        """
        if not BLAKE3_AVAILABLE:
            raise ImportError("blake3 not available")
        
        hasher = blake3.blake3()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest().upper()
    
    @staticmethod
    def get_multiple_hashes(file_path: str, algorithms: Optional[list] = None) -> dict:
        """
        Generates multiple hashes for a file using different algorithms.
        
        **Description:** Computes multiple hashes for the same file efficiently.
        **Parameters:**
        - `file_path` (str): Path to the file
        - `algorithms` (Optional[list]): List of algorithms to use, defaults to ['AutoV2', 'SHA256']
        **Returns:** dict containing algorithm -> hash mappings
        """
        if algorithms is None:
            algorithms = ['AutoV2', 'SHA256']
        
        results = {}
        for algorithm in algorithms:
            if algorithm in HashUtils.SUPPORTED_ALGORITHMS:
                hash_value = HashUtils.get_file_hash(file_path, algorithm)
                if hash_value:
                    results[algorithm] = hash_value
            else:
                logger.warning(f"Skipping unsupported algorithm: {algorithm}")
        
        return results
