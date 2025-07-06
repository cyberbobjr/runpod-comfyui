#!/usr/bin/env python3
"""
Example script demonstrating CivitAI model enhancement functionality.

This script shows how to:
1. Set up CivitAI token
2. Hash model files using various algorithms
3. Enhance unknown models using CivitAI API
4. Handle rate limiting and errors gracefully

Usage:
    python examples/civitai_enhancement_example.py
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.utils.hash_utils import HashUtils
from back.services.model_scanner_service import ModelScannerService
from back.services.token_service import TokenService
from back.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def create_sample_model_file(file_path: str, content: bytes = None) -> str:
    """Create a sample model file for testing."""
    if content is None:
        # Create sample content that simulates a model file
        content = b"SAMPLE_MODEL_HEADER" + b"A" * 8192 + b"MIDDLE_CONTENT" + b"B" * 8192 + b"SAMPLE_MODEL_FOOTER"
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return file_path


def demonstrate_hash_algorithms():
    """Demonstrate different hashing algorithms."""
    print("=" * 60)
    print("HASH ALGORITHMS DEMONSTRATION")
    print("=" * 60)
    
    # Create temporary model file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.safetensors') as tmp:
        sample_file = tmp.name
    
    try:
        create_sample_model_file(sample_file)
        
        print(f"Sample file created: {sample_file}")
        print(f"File size: {os.path.getsize(sample_file)} bytes")
        print()
        
        # Test individual algorithms
        print("Individual Hash Results:")
        print("-" * 30)
        
        algorithms = ['AutoV1', 'AutoV2', 'SHA256', 'CRC32']
        for algorithm in algorithms:
            start_time = time.time()
            hash_value = HashUtils.get_file_hash(sample_file, algorithm)
            end_time = time.time()
            
            if hash_value:
                print(f"{algorithm:>8}: {hash_value} (took {end_time - start_time:.3f}s)")
            else:
                print(f"{algorithm:>8}: Failed to compute hash")
        
        # Test Blake3 if available
        try:
            blake3_hash = HashUtils.get_file_hash(sample_file, 'Blake3')
            if blake3_hash:
                print(f"{'Blake3':>8}: {blake3_hash}")
        except Exception as e:
            print(f"{'Blake3':>8}: Not available ({str(e)})")
        
        print()
        
        # Test multiple hashes
        print("Multiple Hash Results:")
        print("-" * 30)
        
        start_time = time.time()
        multi_hashes = HashUtils.get_multiple_hashes(sample_file, algorithms)
        end_time = time.time()
        
        for algo, hash_value in multi_hashes.items():
            print(f"{algo:>8}: {hash_value}")
        
        print(f"Total time for multiple hashes: {end_time - start_time:.3f}s")
        print()
        
    finally:
        if os.path.exists(sample_file):
            os.unlink(sample_file)


def demonstrate_civitai_type_mapping():
    """Demonstrate CivitAI type mapping."""
    print("=" * 60)
    print("CIVITAI TYPE MAPPING DEMONSTRATION")
    print("=" * 60)
    
    test_types = [
        'checkpoint', 'textualinversion', 'hypernetwork', 'lora', 
        'controlnet', 'upscaler', 'vae', 'poses', 'wildcards', 
        'unknown_type', 'motionmodule'
    ]
    
    print("CivitAI Type -> Internal Category:")
    print("-" * 40)
    
    for civitai_type in test_types:
        category = ModelScannerService._map_civitai_type_to_category(civitai_type)
        print(f"{civitai_type:>15} -> {category}")
    
    print()


def demonstrate_token_management():
    """Demonstrate token management."""
    print("=" * 60)
    print("TOKEN MANAGEMENT DEMONSTRATION")
    print("=" * 60)
    
    # Get current tokens
    current_tokens = TokenService.get_tokens()
    print("Current tokens:")
    print(f"  HuggingFace: {'Set' if current_tokens.get('hf_token') else 'Not set'}")
    print(f"  CivitAI: {'Set' if current_tokens.get('civitai_token') else 'Not set'}")
    print()
    
    # Show env file path
    env_path = TokenService.get_env_file_path()
    print(f"Environment file path: {env_path}")
    print(f"Environment file exists: {os.path.exists(env_path)}")
    print()
    
    if current_tokens.get('civitai_token'):
        print("✓ CivitAI token is configured - model enhancement will work")
    else:
        print("⚠ CivitAI token not configured - model enhancement will be skipped")
        print("  To set up CivitAI token:")
        print("  1. Get your API key from https://civitai.com/user/account")
        print("  2. Add CIVITAI_TOKEN=your_token_here to your .env file")
        print("  3. Or use: TokenService.set_tokens(hf_token=None, civitai_token='your_token')")
    
    print()


def demonstrate_model_enhancement():
    """Demonstrate model enhancement with CivitAI."""
    print("=" * 60)
    print("MODEL ENHANCEMENT DEMONSTRATION")
    print("=" * 60)
    
    # Check if CivitAI token is available
    tokens = TokenService.get_tokens()
    if not tokens.get('civitai_token'):
        print("⚠ CivitAI token not available - skipping actual API calls")
        print("  This demonstration will show the structure without making real API calls")
        print()
        
        # Create mock model info
        mock_model_info = {
            "name": "unknown_model.safetensors",
            "path": "/path/to/unknown_model.safetensors",
            "category": "other",
            "size": 2048000000,
            "size_gb": 2.048
        }
        
        print("Mock model info (category='other'):")
        for key, value in mock_model_info.items():
            print(f"  {key}: {value}")
        print()
        
        print("If CivitAI token were available, the enhancement would:")
        print("1. Compute file hash using AutoV2 algorithm")
        print("2. Query CivitAI API once with the computed hash")
        print("3. Wait 3 seconds to be respectful to CivitAI servers")
        print("4. If found, enhance model info with:")
        print("   - Correct category (checkpoints, loras, etc.)")
        print("   - Model name and description")
        print("   - Creator information")
        print("   - Tags and metadata")
        print("   - Download statistics")
        print("   - Preview images")
        print()
        
        return
    
    # Create a temporary model file for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.safetensors') as tmp:
        sample_file = tmp.name
    
    try:
        create_sample_model_file(sample_file)
        
        # Create model info
        model_info = {
            "name": os.path.basename(sample_file),
            "path": sample_file,
            "category": "other",
            "size": os.path.getsize(sample_file),
            "size_mb": round(os.path.getsize(sample_file) / (1024 * 1024), 2)
        }
        
        print("Original model info:")
        for key, value in model_info.items():
            print(f"  {key}: {value}")
        print()
        
        print("Attempting CivitAI enhancement...")
        print("(This will take at least 3 seconds due to respectful rate limiting)")
        
        # Attempt enhancement
        enhanced_model = ModelScannerService._enhance_model_with_civitai(model_info)
        
        if enhanced_model:
            print("✓ Model successfully enhanced with CivitAI data!")
            print()
            print("Enhanced model info:")
            for key, value in enhanced_model.items():
                if key == 'civitai_info':
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("⚠ Model not found in CivitAI database")
            print("  This is expected for our test file")
        
        print()
        
    finally:
        if os.path.exists(sample_file):
            os.unlink(sample_file)


def main():
    """Main demonstration function."""
    print("CivitAI Model Enhancement Demonstration")
    print("=" * 60)
    print()
    
    # Run demonstrations
    demonstrate_hash_algorithms()
    demonstrate_civitai_type_mapping()
    demonstrate_token_management()
    demonstrate_model_enhancement()
    
    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Set up your CivitAI token in the .env file")
    print("2. Run model scanning on your actual models directory")
    print("3. Check the logs for enhancement results")
    print("4. Verify that unknown models are properly categorized")
    print()


if __name__ == "__main__":
    main()
