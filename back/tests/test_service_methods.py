#!/usr/bin/env python3
"""
Simple test for the Model Scanner Service without authentication
"""
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from back.services.model_scanner_service import ModelScannerService

def test_service_methods():
    """Test the service methods directly"""
    print("Testing Model Scanner Service methods...")
    
    service = ModelScannerService()
    
    # Test summary method
    try:
        summary = service.get_model_summary()
        print(f"✓ Summary method: {summary.get('total_models', 0)} models found")
        print(f"  - Models directory: {summary.get('models_directory', 'N/A')}")
        categories = summary.get('categories', {})
        if categories:
            print(f"  - Categories with models: {list(categories.keys())}")
    except Exception as e:
        print(f"✗ Summary method failed: {e}")
    
    # Test scan method
    try:
        scan_result = service.scan_models_directory()
        print(f"✓ Scan method: {scan_result.get('total_models', 0)} models found")
        models = scan_result.get('models', {})
        if models:
            print(f"  - Model categories: {list(models.keys())}")
            # Show first few models from each category
            for category, model_list in models.items():
                if model_list:
                    print(f"    - {category}: {len(model_list)} models")
                    if len(model_list) > 0:
                        first_model = model_list[0]
                        print(f"      Example: {first_model.get('name', 'N/A')} ({first_model.get('identified_type', 'N/A')})")
    except Exception as e:
        print(f"✗ Scan method failed: {e}")
    
    # Test search method
    try:
        search_result = service.search_models("test")
        print(f"✓ Search method: {search_result.get('total_matches', 0)} matches found")
    except Exception as e:
        print(f"✗ Search method failed: {e}")
    
    print("\nAll service method tests completed! ✓")

if __name__ == "__main__":
    test_service_methods()
