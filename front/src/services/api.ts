/**
 * API Service - TypeScript Version
 * 
 * A comprehensive API service built on Axios with TypeScript support.
 * 
 * Features:
 * - Environment-based base URL configuration
 * - Automatic authentication token handling
 * - Request and response interceptors
 * - Specialized file download functionality
 * - Error handling with automatic redirect for 401 errors
 * - TypeScript interfaces for all API responses
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosRequestConfig, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { Router } from 'vue-router';
import type { 
  ApiResponse, 
  ApiErrorResponse, 
  FileDownloadConfig,
  ApiRequestConfig 
} from './types/api.types';

// Router instance - will be set by the app during initialization
let routerInstance: Router | null = null;

/**
 * Set the router instance for navigation in API interceptors
 * @param router - Vue Router instance
 */
export const setApiRouter = (router: Router): void => {
  routerInstance = router;
};

/**
 * Environment configuration interface
 */
interface EnvironmentConfig {
  isDevelopment: boolean;
  baseURL: string;
}

/**
 * Extended Axios instance with custom methods
 */
interface ExtendedAxiosInstance extends AxiosInstance {
  downloadFile(path: string, filename: string): Promise<boolean>;
}

// Environment configuration
const isDevelopment: boolean = (import.meta as any).env.MODE === 'development';
const baseURL: string = isDevelopment 
  ? 'http://localhost:8082/api' 
  : window.location.origin + '/api';

// Token storage configuration
const TOKEN_STORAGE_KEY: string = 'auth_token';

/**
 * Get authentication token from localStorage
 * @returns The stored token or null if not found
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

/**
 * Set authentication token in localStorage
 * @param token - The authentication token to store
 */
const setAuthToken = (token: string): void => {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
};

/**
 * Remove authentication token from localStorage
 */
const removeAuthToken = (): void => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
};

/**
 * Create Axios instance with default configuration
 */
const api: ExtendedAxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}) as ExtendedAxiosInstance;

/**
 * Request interceptor to add authentication token
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const token = getAuthToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError): Promise<AxiosError> => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => response,
  (error: AxiosError): Promise<AxiosError> => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      console.log('Error 401: Session expired or not authenticated');
      
      // Remove token from localStorage
      removeAuthToken();
      
      // Redirect to login if not already there and router is available
      if (routerInstance && routerInstance.currentRoute.value.name !== 'login') {
        const currentPath = routerInstance.currentRoute.value.fullPath;
        routerInstance.push({ 
          name: 'login', 
          query: { redirect: currentPath }
        }).catch((err: any) => {
          console.error('Navigation error:', err);
        });
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Specialized method for downloading files
 * @param path - The file path on the server
 * @param filename - The desired filename for the download
 * @returns Promise that resolves to true if download succeeds
 * @throws Error if download fails
 */
api.downloadFile = async function(path: string, filename: string): Promise<boolean> {
  try {
    const response: AxiosResponse<Blob> = await this.get(
      `/file/download?path=${encodeURIComponent(path)}`, 
      {
        responseType: 'blob'
      }
    );
    
    // Get MIME type from response headers
    const contentType: string = response.headers['content-type'] || 'application/octet-stream';
    
    // Create blob with correct MIME type
    const blob = new Blob([response.data], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    
    // Create temporary <a> element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    // Add to DOM, click, then remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up blob URL after short delay
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 100);
    
    return true;
  } catch (error: any) {
    console.error('Download error:', error);
    throw error;
  }
};

// Export utility functions and constants
export { 
  TOKEN_STORAGE_KEY, 
  getAuthToken, 
  setAuthToken, 
  removeAuthToken
};

// Re-export API types for convenience
export type {
  ApiResponse,
  ApiErrorResponse,
  FileDownloadConfig,
  ApiRequestConfig
} from './types/api.types';

export default api;
