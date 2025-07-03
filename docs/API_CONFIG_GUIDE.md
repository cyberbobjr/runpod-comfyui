# API Configuration Guide

## Overview

The API service has been refactored into a class-based architecture (`ApiConfig`) to improve testability and maintainability. This guide explains how to use the new `ApiConfig` class and how to mock it in tests.

## Basic Usage

### Using the Default Instance

For backward compatibility, you can still use the API service as before:

```typescript
import api, { getAuthToken, setAuthToken } from '@/services/api';

// Use the API instance
const response = await api.get('/users');

// Manage tokens
setAuthToken('your-token');
const token = getAuthToken();
```

### Creating Custom Instances

You can create custom `ApiConfig` instances with different configurations:

```typescript
import { ApiConfig } from '@/services/api';

// Create a custom API configuration
const customApiConfig = new ApiConfig({
  baseURL: 'https://api.example.com',
  timeout: 15000,
  tokenStorageKey: 'custom_token',
  router: yourVueRouter
});

// Get the axios instance
const apiInstance = customApiConfig.getApiInstance();
```

## Configuration Options

### ApiConfigOptions Interface

```typescript
interface ApiConfigOptions {
  baseURL?: string;          // Custom base URL for API requests
  timeout?: number;          // Request timeout in milliseconds (default: 10000)
  tokenStorageKey?: string;  // localStorage key for auth token (default: "auth_token")
  router?: Router;           // Vue Router instance for navigation
}
```

### Example Configurations

```typescript
// Development configuration
const devApiConfig = new ApiConfig({
  baseURL: 'http://localhost:3000/api',
  timeout: 5000,
  tokenStorageKey: 'dev_token'
});

// Production configuration  
const prodApiConfig = new ApiConfig({
  baseURL: 'https://api.myapp.com',
  timeout: 10000,
  tokenStorageKey: 'prod_token'
});

// Testing configuration
const testApiConfig = new ApiConfig({
  baseURL: 'http://mock-api.test',
  timeout: 1000,
  tokenStorageKey: 'test_token'
});
```

## Testing with Mocks

### Method 1: Mock the Entire Class

```typescript
import { vi } from 'vitest';
import { ApiConfig } from '@/services/api';

// Create a mock implementation
const MockApiConfig = vi.fn().mockImplementation(() => ({
  getAuthToken: vi.fn().mockReturnValue('mock-token'),
  setAuthToken: vi.fn(),
  removeAuthToken: vi.fn(),
  getApiInstance: vi.fn().mockReturnValue({
    get: vi.fn().mockResolvedValue({ data: 'mock-data' }),
    post: vi.fn().mockResolvedValue({ data: 'success' }),
    downloadFile: vi.fn().mockResolvedValue(true),
  }),
  setRouter: vi.fn(),
  getTokenStorageKey: vi.fn().mockReturnValue('mock_token'),
}));

// Use in tests
const mockApiConfig = new MockApiConfig();
```

### Method 2: Spy on Specific Methods

```typescript
import { vi } from 'vitest';
import { ApiConfig } from '@/services/api';

describe('Component Tests', () => {
  let apiConfig: ApiConfig;

  beforeEach(() => {
    apiConfig = new ApiConfig();
  });

  it('should handle authentication', () => {
    const getTokenSpy = vi.spyOn(apiConfig, 'getAuthToken').mockReturnValue('test-token');
    const setTokenSpy = vi.spyOn(apiConfig, 'setAuthToken');

    // Test your component logic
    apiConfig.setAuthToken('new-token');
    const token = apiConfig.getAuthToken();

    expect(setTokenSpy).toHaveBeenCalledWith('new-token');
    expect(token).toBe('test-token');
  });
});
```

### Method 3: Dependency Injection

```typescript
export class UserService {
  private apiConfig: ApiConfig;

  constructor(apiConfig?: ApiConfig) {
    this.apiConfig = apiConfig || new ApiConfig();
  }

  async getUser(id: string) {
    const api = this.apiConfig.getApiInstance();
    const response = await api.get(`/users/${id}`);
    return response.data;
  }
}

// In tests
describe('UserService', () => {
  it('should fetch user data', async () => {
    const mockApiConfig = {
      getApiInstance: vi.fn().mockReturnValue({
        get: vi.fn().mockResolvedValue({ data: { id: '1', name: 'John' } })
      })
    } as any;

    const userService = new UserService(mockApiConfig);
    const user = await userService.getUser('1');

    expect(user).toEqual({ id: '1', name: 'John' });
  });
});
```

## API Methods

### Token Management

```typescript
const apiConfig = new ApiConfig();

// Get current auth token
const token = apiConfig.getAuthToken();

// Set auth token
apiConfig.setAuthToken('your-jwt-token');

// Remove auth token
apiConfig.removeAuthToken();

// Get the storage key being used
const storageKey = apiConfig.getTokenStorageKey();
```

### Router Management

```typescript
import { router } from '@/router';

const apiConfig = new ApiConfig();

// Set router for automatic redirects on 401 errors
apiConfig.setRouter(router);
```

### API Instance Access

```typescript
const apiConfig = new ApiConfig();
const api = apiConfig.getApiInstance();

// Standard Axios methods
const response = await api.get('/data');
await api.post('/data', payload);
await api.put('/data/1', updatePayload);
await api.delete('/data/1');

// Custom download method
const success = await api.downloadFile('/path/to/file.pdf', 'downloaded-file.pdf');
```

## Migration Guide

### From Old API Service

If you were using the old API service:

```typescript
// Old way
import api, { getAuthToken, setAuthToken } from '@/services/api';

// New way (still works - backward compatible)
import api, { getAuthToken, setAuthToken } from '@/services/api';

// Or use the class directly
import { ApiConfig } from '@/services/api';
const apiConfig = new ApiConfig();
```

### Benefits of the New Architecture

1. **Better Testability**: Easy to mock and test individual components
2. **Dependency Injection**: Can inject different configurations for different environments
3. **Isolation**: Each instance is independent, avoiding global state issues
4. **Type Safety**: Full TypeScript support with proper interfaces
5. **Flexibility**: Can create multiple API configurations for different services

## Best Practices

1. **Use dependency injection** in your components/services for better testability
2. **Create environment-specific configurations** for development, staging, and production
3. **Mock at the class level** rather than individual methods for cleaner tests
4. **Use the default instance** for simple use cases to maintain backward compatibility
5. **Document your custom configurations** when creating specialized API instances

## Example: Complete Component Integration

```typescript
// services/UserService.ts
import { ApiConfig } from '@/services/api';

export class UserService {
  constructor(private apiConfig = new ApiConfig()) {}

  async fetchUsers() {
    const api = this.apiConfig.getApiInstance();
    const response = await api.get('/users');
    return response.data;
  }

  async createUser(userData: any) {
    const api = this.apiConfig.getApiInstance();
    const response = await api.post('/users', userData);
    return response.data;
  }
}

// components/UserComponent.vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { UserService } from '@/services/UserService';

const userService = new UserService();
const users = ref([]);

onMounted(async () => {
  users.value = await userService.fetchUsers();
});
</script>

// tests/UserService.test.ts
import { describe, it, expect, vi } from 'vitest';
import { UserService } from '@/services/UserService';

describe('UserService', () => {
  it('should fetch users', async () => {
    const mockApiConfig = {
      getApiInstance: vi.fn().mockReturnValue({
        get: vi.fn().mockResolvedValue({ data: [{ id: 1, name: 'John' }] })
      })
    } as any;

    const userService = new UserService(mockApiConfig);
    const result = await userService.fetchUsers();

    expect(result).toEqual([{ id: 1, name: 'John' }]);
  });
});
```

This architecture provides a clean, testable, and maintainable approach to API management in your application.
