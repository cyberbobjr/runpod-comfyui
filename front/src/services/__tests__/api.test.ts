/**
 * API Service Tests - TypeScript
 * 
 * Comprehensive test suite for the API service to ensure
 * TypeScript conversion maintains functionality.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

import api, { 
  getAuthToken, 
  setAuthToken, 
  removeAuthToken, 
  TOKEN_STORAGE_KEY 
} from '../api';
import type { 
  ApiResponse, 
  ApiErrorResponse,
  BundleApiResponse,
  ModelApiResponse 
} from '../types/api.types';

/**
 * API Service Test Suite
 */
export class ApiServiceTestSuite {
  /**
   * Test authentication token management
   */
  testTokenManagement(): boolean {
    console.log('Testing token management...');
    
    try {
      // Test setting and getting token
      const testToken = 'test-token-123';
      setAuthToken(testToken);
      
      const retrievedToken = getAuthToken();
      if (retrievedToken !== testToken) {
        throw new Error('Token retrieval failed');
      }
      
      // Test token removal
      removeAuthToken();
      const removedToken = getAuthToken();
      if (removedToken !== null) {
        throw new Error('Token removal failed');
      }
      
      console.log('✅ Token management tests passed');
      return true;
    } catch (error) {
      console.error('❌ Token management tests failed:', error);
      return false;
    }
  }

  /**
   * Test API instance configuration
   */
  testApiConfiguration(): boolean {
    console.log('Testing API configuration...');
    
    try {
      // Check if API instance exists
      if (!api) {
        throw new Error('API instance not created');
      }
      
      // Check default configuration
      if (!api.defaults.baseURL) {
        throw new Error('Base URL not configured');
      }
      
      if (api.defaults.timeout !== 10000) {
        throw new Error('Timeout not configured correctly');
      }
      
      // Check default headers
      const headers = api.defaults.headers;
      if (!headers || !headers['Content-Type'] || !headers['Accept']) {
        throw new Error('Default headers not configured');
      }
      
      console.log('✅ API configuration tests passed');
      return true;
    } catch (error) {
      console.error('❌ API configuration tests failed:', error);
      return false;
    }
  }

  /**
   * Test custom downloadFile method
   */
  testDownloadFileMethod(): boolean {
    console.log('Testing downloadFile method...');
    
    try {
      // Check if downloadFile method exists
      if (typeof api.downloadFile !== 'function') {
        throw new Error('downloadFile method not found');
      }
      
      console.log('✅ downloadFile method exists');
      return true;
    } catch (error) {
      console.error('❌ downloadFile method test failed:', error);
      return false;
    }
  }

  /**
   * Test TypeScript type compatibility
   */
  testTypeScriptTypes(): boolean {
    console.log('Testing TypeScript type compatibility...');
    
    try {
      // Test API response typing
      const mockApiResponse: ApiResponse<BundleApiResponse[]> = {
        data: [{
          id: 'test-bundle',
          name: 'Test Bundle',
          description: 'A test bundle',
          version: '1.0.0',
          hardware_profiles: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }],
        status: 200,
        success: true,
        message: 'Success'
      };
      
      // Test error response typing
      const mockErrorResponse: ApiErrorResponse = {
        message: 'Test error',
        status: 400,
        detail: 'Detailed error message'
      };
      
      // Test model response typing
      const mockModelResponse: ModelApiResponse = {
        groups: {
          'checkpoints': [{
            dest: '/models/checkpoint.safetensors',
            url: 'https://example.com/model.safetensors',
            exists: true,
            size: 1024
          }]
        }
      };
      
      // If we get here, types are working
      console.log('✅ TypeScript types test passed');
      return true;
    } catch (error) {
      console.error('❌ TypeScript types test failed:', error);
      return false;
    }
  }

  /**
   * Test interceptors functionality
   */
  testInterceptors(): boolean {
    console.log('Testing interceptors...');
    
    try {
      // Check if interceptors are configured
      if (!api.interceptors.request || !api.interceptors.response) {
        throw new Error('Interceptors not configured');
      }
      
      console.log('✅ Interceptors test passed');
      return true;
    } catch (error) {
      console.error('❌ Interceptors test failed:', error);
      return false;
    }
  }

  /**
   * Run all tests
   */
  runAllTests(): boolean {
    console.log('🧪 Running API Service TypeScript Tests...\n');
    
    const tests = [
      this.testTokenManagement(),
      this.testApiConfiguration(),
      this.testDownloadFileMethod(),
      this.testTypeScriptTypes(),
      this.testInterceptors()
    ];
    
    const passedTests = tests.filter(result => result).length;
    const totalTests = tests.length;
    
    console.log(`\n📊 Test Results: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
      console.log('🎉 All API service tests passed! TypeScript migration successful.');
      return true;
    } else {
      console.log('⚠️ Some tests failed. Please review the API service implementation.');
      return false;
    }
  }
}

/**
 * Factory function to create and run tests
 */
export function runApiServiceTests(): boolean {
  const testSuite = new ApiServiceTestSuite();
  return testSuite.runAllTests();
}

export default ApiServiceTestSuite;
