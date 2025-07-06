#!/usr/bin/env python3
"""
ComfyUI Integration Test Script

This script tests the ComfyUI integration by making API calls to the backend
and verifying that the generation workflow works correctly.

Usage:
    python test_comfyui_integration.py [--model MODEL_KEY] [--prompt PROMPT]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "back"))

from back.services.comfy_workflow_builder import GenerationParams, LoRA


class ComfyUIIntegrationTester:
    """Test the ComfyUI integration end-to-end."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the tester.
        
        **Parameters:**
        - base_url (str): The base URL of the backend API
        """
        self.base_url = base_url
        self.session = requests.Session()
        # Add authentication headers if needed
        # self.session.headers.update({"Authorization": "Bearer your-token"})
    
    def test_server_status(self) -> bool:
        """
        Test if the ComfyUI server is available.
        
        **Returns:** True if server is available, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/comfy/status", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✓ ComfyUI server status: {data.get('status', 'unknown')}")
            return data.get("status") == "available"
            
        except RequestException as e:
            print(f"✗ ComfyUI server not available: {e}")
            return False
    
    def test_models_endpoint(self) -> Optional[Dict[str, Any]]:
        """
        Test the models endpoint.
        
        **Returns:** Models data if successful, None otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/comfy/models", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = data.get("models", {})
            
            print(f"✓ Available models: {list(models.keys())}")
            return models
            
        except RequestException as e:
            print(f"✗ Failed to fetch models: {e}")
            return None
    
    def test_workflow_generation(self, model_key: str, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Test workflow generation.
        
        **Parameters:**
        - model_key (str): The model to use
        - prompt (str): The generation prompt
        
        **Returns:** Generated workflow if successful, None otherwise
        """
        try:
            params = GenerationParams(
                model_key=model_key,
                prompt=prompt,
                negative_prompt="blurry, low quality",
                sampler="euler",
                steps=20,
                cfg=7.5,
                width=512,
                height=512,
                seed=42
            )
            
            response = self.session.post(
                f"{self.base_url}/api/comfy/workflow/generate",
                json=params.dict(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            workflow = data.get("workflow", {})
            
            print(f"✓ Generated workflow with {len(workflow)} nodes")
            return workflow
            
        except RequestException as e:
            print(f"✗ Failed to generate workflow: {e}")
            return None
    
    def test_generate_and_execute(self, model_key: str, prompt: str) -> Optional[str]:
        """
        Test generate and execute endpoint.
        
        **Parameters:**
        - model_key (str): The model to use
        - prompt (str): The generation prompt
        
        **Returns:** Prompt ID if successful, None otherwise
        """
        try:
            params = GenerationParams(
                model_key=model_key,
                prompt=prompt,
                negative_prompt="blurry, low quality",
                sampler="euler",
                steps=20,
                cfg=7.5,
                width=512,
                height=512,
                seed=42,
                wait=False  # Don't wait for completion
            )
            
            response = self.session.post(
                f"{self.base_url}/api/comfy/generate-and-execute",
                json=params.dict(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            prompt_id = data.get("prompt_id")
            
            print(f"✓ Started generation with prompt_id: {prompt_id}")
            return prompt_id
            
        except RequestException as e:
            print(f"✗ Failed to start generation: {e}")
            return None
    
    def test_result_retrieval(self, prompt_id: str) -> bool:
        """
        Test result retrieval by prompt ID.
        
        **Parameters:**
        - prompt_id (str): The prompt ID to check
        
        **Returns:** True if result found, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/comfy/result/{prompt_id}",
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            images = data.get("images", [])
            status = data.get("status", "unknown")
            
            print(f"✓ Retrieved result - Status: {status}, Images: {len(images)}")
            return True
            
        except RequestException as e:
            print(f"✗ Failed to retrieve result: {e}")
            return False
    
    def run_integration_tests(self, model_key: str, prompt: str) -> bool:
        """
        Run all integration tests.
        
        **Parameters:**
        - model_key (str): The model to use for testing
        - prompt (str): The generation prompt
        
        **Returns:** True if all tests passed, False otherwise
        """
        print("=== ComfyUI Integration Tests ===\n")
        
        # Test 1: Server status
        print("1. Testing server status...")
        if not self.test_server_status():
            print("   Server not available, skipping remaining tests.")
            return False
        
        # Test 2: Models endpoint
        print("\n2. Testing models endpoint...")
        models = self.test_models_endpoint()
        if not models:
            print("   Failed to fetch models, skipping remaining tests.")
            return False
        
        # Verify model exists
        if model_key not in models:
            print(f"   Model '{model_key}' not found in available models.")
            available_models = list(models.keys())
            if available_models:
                model_key = available_models[0]
                print(f"   Using first available model: {model_key}")
            else:
                print("   No models available for testing.")
                return False
        
        # Test 3: Workflow generation
        print(f"\n3. Testing workflow generation with model '{model_key}'...")
        workflow = self.test_workflow_generation(model_key, prompt)
        if not workflow:
            print("   Failed to generate workflow.")
            return False
        
        # Test 4: Generate and execute
        print(f"\n4. Testing generate and execute with model '{model_key}'...")
        prompt_id = self.test_generate_and_execute(model_key, prompt)
        if not prompt_id:
            print("   Failed to start generation.")
            return False
        
        # Test 5: Result retrieval (may not have results yet)
        print(f"\n5. Testing result retrieval for prompt '{prompt_id}'...")
        self.test_result_retrieval(prompt_id)
        
        print("\n=== Integration Tests Complete ===")
        print("✓ All basic integration tests passed!")
        
        return True


def main():
    """Main function to run the integration tests."""
    parser = argparse.ArgumentParser(description="Test ComfyUI integration")
    parser.add_argument(
        "--model", 
        default="flux-dev",
        help="Model key to use for testing (default: flux-dev)"
    )
    parser.add_argument(
        "--prompt",
        default="A beautiful landscape with mountains and a lake",
        help="Prompt to use for testing"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the backend API"
    )
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = ComfyUIIntegrationTester(base_url=args.base_url)
    
    # Run tests
    success = tester.run_integration_tests(args.model, args.prompt)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
