#!/usr/bin/env python3
"""
Integration test for the Model Scanner API endpoints
"""
import sys
import os
import tempfile
from pathlib import Path
import torch

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from back.services.model_scanner_service import ModelScannerService
from back.routers.model_scanner_router import router
from fastapi.testclient import TestClient
from fastapi import FastAPI

def test_api_endpoints():
    """Test the API endpoints with a mock app"""
    print("Testing Model Scanner API endpoints...")
    
    # Create a test app
    app = FastAPI()
    app.include_router(router)
    
    # Create a test client
    client = TestClient(app)
    
    # Test the summary endpoint
    response = client.get("/api/models/scanner/summary")
    print(f"✓ Summary endpoint status: {response.status_code}")
    if response.status_code == 200:
        print(f"  - Response: {response.json()}")
    
    # Test the scan endpoint
    response = client.get("/api/models/scanner/scan")
    print(f"✓ Scan endpoint status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Total models: {data.get('total_models', 0)}")
        print(f"  - Categories: {list(data.get('models', {}).keys())}")
    
    # Test the search endpoint
    response = client.get("/api/models/scanner/search?query=test")
    print(f"✓ Search endpoint status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Total matches: {data.get('total_matches', 0)}")
    
    # Test the categories endpoint
    response = client.get("/api/models/scanner/categories")
    print(f"✓ Categories endpoint status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Categories: {list(data.keys())}")
    
    # Test the types endpoint
    response = client.get("/api/models/scanner/types")
    print(f"✓ Types endpoint status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Types: {list(data.keys())}")
    
    print("\nAll API endpoint tests completed! ✓")

if __name__ == "__main__":
    test_api_endpoints()
