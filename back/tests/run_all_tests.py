#!/usr/bin/env python3
"""
Test script to verify all back tests run correctly from the tests directory.
"""

import sys
import os

# Add the back directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Run all test modules in the back/tests directory."""
    print("Running all back/tests...")
    
    # Test the main workflow builder functionality
    print("\n1. Testing ComfyWorkflowBuilder...")
    try:
        from test_comfy_workflow_builder import TestComfyWorkflowBuilder, TestModelLoaderFactory
        import unittest
        
        # Create test suite
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestComfyWorkflowBuilder))
        suite.addTest(unittest.makeSuite(TestModelLoaderFactory))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"✓ Workflow builder tests: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        
    except Exception as e:
        print(f"✗ Error running workflow builder tests: {e}")
    
    # Test the custom loader example
    print("\n2. Testing custom loader example...")
    try:
        from test_custom_loader_example import demonstrate_custom_loader
        demonstrate_custom_loader()
        print("✓ Custom loader example passed")
    except Exception as e:
        print(f"✗ Error running custom loader example: {e}")
    
    # Test the legacy workflow builder
    print("\n3. Testing legacy workflow builder...")
    try:
        from test_workflow_builder_legacy import main
        main()
        print("✓ Legacy workflow builder tests passed")
    except Exception as e:
        print(f"✗ Error running legacy workflow builder tests: {e}")

if __name__ == "__main__":
    run_all_tests()
