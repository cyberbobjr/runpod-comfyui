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

import axios from "axios";
import type {
  AxiosInstance,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";
import type { Router } from "vue-router";
import { TOKENSTORAGEKEY } from "./types/api.types";

/**
 * Extended Axios instance with custom methods
 */
interface ExtendedAxiosInstance extends AxiosInstance {
  downloadFile(path: string, filename: string): Promise<boolean>;
}

/**
 * Configuration interface for ApiConfig class
 */
export interface ApiConfigOptions {
  baseURL?: string;
  timeout?: number;
  tokenStorageKey?: string;
  router?: Router;
}
/**
 * Singleton instance holder
 */
let _singletonInstance: ApiConfig | null = null;

/**
 * API Configuration Class
 * 
 * Encapsulates all API configuration, token management, and Axios instance creation.
 * This class is designed to be easily mockable for unit testing.
 */
export class ApiConfig {
  private _api: ExtendedAxiosInstance;
  private _routerInstance: Router | null = null;
  private readonly _tokenStorageKey: string;
  private readonly _isDevelopment: boolean;

  /**
   * Create a new ApiConfig instance
   * @param options - Configuration options for the API
   */
  constructor(options: ApiConfigOptions = {}) {
    this._isDevelopment = (import.meta as any).env.MODE === "development";
    this._tokenStorageKey = options.tokenStorageKey || TOKENSTORAGEKEY;
    
    const baseURL = options.baseURL || this._getDefaultBaseURL();
    const timeout = options.timeout || 10000;
    
    if (options.router) {
      this._routerInstance = options.router;
    }

    this._api = this._createAxiosInstance(baseURL, timeout);
    this._setupInterceptors();
    this._addDownloadFileMethod();
  }

  /**
   * Get the default base URL based on environment
   * @returns The default base URL
   */
  private _getDefaultBaseURL(): string {
    return this._isDevelopment
      ? "http://localhost:8082/api"
      : window.location.origin + "/api";
  }

  /**
   * Create and configure the Axios instance
   * @param baseURL - The base URL for API requests
   * @param timeout - Request timeout in milliseconds
   * @returns Configured Axios instance
   */
  private _createAxiosInstance(baseURL: string, timeout: number): ExtendedAxiosInstance {
    return axios.create({
      baseURL,
      timeout,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    }) as ExtendedAxiosInstance;
  }

  /**
   * Set up request and response interceptors
   */
  private _setupInterceptors(): void {
    // Request interceptor to add authentication token
    this._api.interceptors.request.use(
      (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        const token = this.getAuthToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError): Promise<AxiosError> => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this._api.interceptors.response.use(
      (response: AxiosResponse): AxiosResponse => response,
      (error: AxiosError): Promise<AxiosError> => {
        // Handle 401 Unauthorized errors
        if (error.response && error.response.status === 401) {
          console.log("Error 401: Session expired or not authenticated");

          // Remove token from localStorage
          this.removeAuthToken();

          // Redirect to login if not already there and router is available
          if (
            this._routerInstance &&
            this._routerInstance.currentRoute.value.name !== "login"
          ) {
            const currentPath = this._routerInstance.currentRoute.value.fullPath;
            this._routerInstance
              .push({
                name: "login",
                query: { redirect: currentPath },
              })
              .catch((err: any) => {
                console.error("Navigation error:", err);
              });
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Add the downloadFile method to the Axios instance
   */
  private _addDownloadFileMethod(): void {
    this._api.downloadFile = async (
      path: string,
      filename: string
    ): Promise<boolean> => {
      try {
        const response: AxiosResponse<Blob> = await this._api.get(
          `/file/download?path=${encodeURIComponent(path)}`,
          {
            responseType: "blob",
          }
        );

        // Get MIME type from response headers
        const contentType: string =
          response.headers["content-type"] || "application/octet-stream";

        // Create blob with correct MIME type
        const blob = new Blob([response.data], { type: contentType });
        const url = window.URL.createObjectURL(blob);

        // Create temporary <a> element to trigger download
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        link.style.display = "none";

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
        console.error("Download error:", error);
        throw error;
      }
    };
  }

  /**
   * Set the router instance for navigation in API interceptors
   * @param router - Vue Router instance
   */
  public setRouter(router: Router): void {
    this._routerInstance = router;
  }

  /**
   * Get authentication token from localStorage
   * @returns The stored token or null if not found
   */
  public getAuthToken(): string | null {
    return localStorage.getItem(this._tokenStorageKey);
  }

  /**
   * Set authentication token in localStorage
   * @param token - The authentication token to store
   */
  public setAuthToken(token: string): void {
    localStorage.setItem(this._tokenStorageKey, token);
  }

  /**
   * Remove authentication token from localStorage
   */
  public removeAuthToken(): void {
    localStorage.removeItem(this._tokenStorageKey);
  }

  /**
   * Get the configured Axios instance
   * @returns The Axios instance
   */
  public getApiInstance(): ExtendedAxiosInstance {
    return this._api;
  }

  /**
   * Get the token storage key
   * @returns The token storage key
   */
  public getTokenStorageKey(): string {
    return this._tokenStorageKey;
  }
}


/**
 * Initialize the global ApiConfig singleton
 * @param options - Configuration options for the API
 * @returns The singleton instance
 */
export const initializeApiConfig = (options?: ApiConfigOptions): ApiConfig => {
  if (_singletonInstance) {
    console.warn('ApiConfig singleton already initialized. Use setApiConfigInstance() to override.');
    return _singletonInstance;
  }
  
  _singletonInstance = new ApiConfig(options);
  return _singletonInstance;
};

/**
 * Get the singleton ApiConfig instance
 * @returns The singleton instance
 * @throws Error if not initialized
 */
export const getApiConfigInstance = (): ApiConfig => {
  if (!_singletonInstance) {
    throw new Error('ApiConfig singleton not initialized. Call initializeApiConfig() first.');
  }
  return _singletonInstance;
};

/**
 * Set a custom ApiConfig instance (useful for testing)
 * @param instance - The ApiConfig instance to use
 */
export const setApiConfigInstance = (instance: ApiConfig | null): void => {
  _singletonInstance = instance;
};

/**
 * Reset the singleton (useful for testing cleanup)
 */
export const resetApiConfigInstance = (): void => {
  _singletonInstance = null;
};

/**
 * Check if the singleton is initialized
 * @returns True if initialized, false otherwise
 */
export const isApiConfigInitialized = (): boolean => {
  return _singletonInstance !== null;
};

// Backward compatibility: Create a default instance if singleton not initialized
const getDefaultApiConfig = (): ApiConfig => {
  if (!_singletonInstance) {
    console.warn('ApiConfig singleton not initialized. Creating default instance. Consider calling initializeApiConfig() in your main.ts');
    _singletonInstance = new ApiConfig();
  }
  return _singletonInstance;
};

// Export default instance and its methods for backward compatibility
export const api = new Proxy({} as ExtendedAxiosInstance, {
  get(target, prop) {
    const instance = getDefaultApiConfig().getApiInstance();
    const value = (instance as any)[prop];
    return typeof value === 'function' ? value.bind(instance) : value;
  }
});

// Re-export API types for convenience
export type {
  ApiResponse,
  ApiErrorResponse,
  FileDownloadConfig,
  ApiRequestConfig,
} from "./types/api.types";

// Export both the class and the default instance
export default api;
