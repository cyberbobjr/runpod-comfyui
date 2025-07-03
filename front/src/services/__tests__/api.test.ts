/**
 * Unit tests for API Service
 * 
 * Demonstrates how to mock the ApiConfig class for testing
 */

import { describe, it, expect, vi, beforeEach, type MockedFunction } from 'vitest';
import type { Router } from 'vue-router';
import { ApiConfig } from '../api';

// Mock axios
vi.mock('axios');

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.URL
Object.defineProperty(window, 'URL', {
  value: {
    createObjectURL: vi.fn(() => 'mock-url'),
    revokeObjectURL: vi.fn(),
  },
});

// Mock document methods
Object.defineProperty(document, 'createElement', {
  value: vi.fn(() => ({
    href: '',
    download: '',
    style: { display: '' },
    click: vi.fn(),
  })),
});

Object.defineProperty(document.body, 'appendChild', {
  value: vi.fn(),
});

Object.defineProperty(document.body, 'removeChild', {
  value: vi.fn(),
});

describe('ApiConfig', () => {
  let apiConfig: ApiConfig;
  let mockRouter: Router;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Create a mock router
    mockRouter = {
      currentRoute: {
        value: {
          name: 'home',
          fullPath: '/dashboard',
        },
      },
      push: vi.fn().mockResolvedValue(undefined),
    } as any;

    // Create a new ApiConfig instance for each test
    apiConfig = new ApiConfig({
      baseURL: 'http://test-api.com/api',
      timeout: 5000,
      tokenStorageKey: 'test_token',
      router: mockRouter,
    });
  });

  describe('Token Management', () => {
    it('should get auth token from localStorage', () => {
      const mockToken = 'test-token-123';
      localStorageMock.getItem.mockReturnValue(mockToken);

      const token = apiConfig.getAuthToken();

      expect(localStorageMock.getItem).toHaveBeenCalledWith('test_token');
      expect(token).toBe(mockToken);
    });

    it('should set auth token in localStorage', () => {
      const testToken = 'new-token-456';

      apiConfig.setAuthToken(testToken);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('test_token', testToken);
    });

    it('should remove auth token from localStorage', () => {
      apiConfig.removeAuthToken();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('test_token');
    });

    it('should return the correct token storage key', () => {
      const key = apiConfig.getTokenStorageKey();
      expect(key).toBe('test_token');
    });
  });

  describe('Router Management', () => {
    it('should set router instance', () => {
      const newMockRouter = { push: vi.fn() } as any;
      
      apiConfig.setRouter(newMockRouter);
      
      // Since router is private, we can test indirectly by checking if it's used
      expect(() => apiConfig.setRouter(newMockRouter)).not.toThrow();
    });
  });

  describe('API Instance', () => {
    it('should return axios instance', () => {
      const apiInstance = apiConfig.getApiInstance();
      
      expect(apiInstance).toBeDefined();
      expect(typeof apiInstance.get).toBe('function');
      expect(typeof apiInstance.post).toBe('function');
      expect(typeof apiInstance.downloadFile).toBe('function');
    });

    it('should have download file method', () => {
      const apiInstance = apiConfig.getApiInstance();
      
      expect(apiInstance.downloadFile).toBeDefined();
      expect(typeof apiInstance.downloadFile).toBe('function');
    });
  });

  describe('Mocking Examples', () => {
    it('should allow easy mocking of ApiConfig for testing', () => {
      // Example 1: Mock the entire ApiConfig class
      const MockApiConfig = vi.fn().mockImplementation(() => ({
        getAuthToken: vi.fn().mockReturnValue('mock-token'),
        setAuthToken: vi.fn(),
        removeAuthToken: vi.fn(),
        getApiInstance: vi.fn().mockReturnValue({
          get: vi.fn().mockResolvedValue({ data: 'mock-data' }),
          post: vi.fn().mockResolvedValue({ data: 'mock-post' }),
          downloadFile: vi.fn().mockResolvedValue(true),
        }),
        setRouter: vi.fn(),
        getTokenStorageKey: vi.fn().mockReturnValue('mock_token'),
      }));

      const mockApiConfig = new MockApiConfig();
      
      expect(mockApiConfig.getAuthToken()).toBe('mock-token');
      expect(mockApiConfig.getTokenStorageKey()).toBe('mock_token');
    });

    it('should allow partial mocking of methods', () => {
      // Example 2: Spy on specific methods
      const getTokenSpy = vi.spyOn(apiConfig, 'getAuthToken').mockReturnValue('spy-token');
      const setTokenSpy = vi.spyOn(apiConfig, 'setAuthToken');

      apiConfig.setAuthToken('test-token');
      const token = apiConfig.getAuthToken();

      expect(setTokenSpy).toHaveBeenCalledWith('test-token');
      expect(getTokenSpy).toHaveBeenCalled();
      expect(token).toBe('spy-token');
    });
  });
});

/**
 * Example of how to use ApiConfig in your components with dependency injection
 */
export class TestableComponent {
  private apiConfig: ApiConfig;

  constructor(apiConfig?: ApiConfig) {
    // Use provided ApiConfig or create default one
    this.apiConfig = apiConfig || new ApiConfig();
  }

  async fetchUserData(userId: string) {
    const api = this.apiConfig.getApiInstance();
    try {
      const response = await api.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      throw error;
    }
  }

  async downloadUserFile(filePath: string, filename: string) {
    const api = this.apiConfig.getApiInstance();
    return await api.downloadFile(filePath, filename);
  }
}

// Test for the TestableComponent
describe('TestableComponent', () => {
  it('should allow easy testing with mocked ApiConfig', async () => {
    // Create a mock ApiConfig
    const mockApiConfig = {
      getApiInstance: vi.fn().mockReturnValue({
        get: vi.fn().mockResolvedValue({ data: { id: 1, name: 'John Doe' } }),
        downloadFile: vi.fn().mockResolvedValue(true),
      }),
    } as any;

    const component = new TestableComponent(mockApiConfig);
    
    const userData = await component.fetchUserData('123');
    const downloadResult = await component.downloadUserFile('/path/to/file', 'file.pdf');
    
    expect(userData).toEqual({ id: 1, name: 'John Doe' });
    expect(downloadResult).toBe(true);
    expect(mockApiConfig.getApiInstance().get).toHaveBeenCalledWith('/users/123');
    expect(mockApiConfig.getApiInstance().downloadFile).toHaveBeenCalledWith('/path/to/file', 'file.pdf');
  });
})
