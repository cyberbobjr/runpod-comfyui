/**
 * Application Initialization
 *
 * This file handles the initialization of global services including ApiConfig
 */
import { ApiConfigOptions, initializeApiConfig } from "@/services/api";
import { TOKENSTORAGEKEY } from "@/services/types/api.types";

/**
 * Initialize the application with all required services
 * @param app - Vue application instance
 * @param router - Vue Router instance
 * @param options - Optional configuration options
 */
export const initializeApp = (
  router: any,
  options?: {
    api?: Partial<ApiConfigOptions>;
    // Add other service configurations here
  }
): void => {
  // Initialize API service
  initializeApiService(router, options?.api);

  // Initialize other services here
  // initializeAuthService();
  // initializeNotificationService();

  console.log("✅ Application initialization complete");
};

/**
 * Initialize the API configuration for the application
 * @param router - Vue Router instance
 * @param customOptions - Optional custom configuration
 */
export const initializeApiService = (
  router: any,
  customOptions?: Partial<ApiConfigOptions>
): void => {
  const isDevelopment = import.meta.env.MODE === "development";

  const defaultOptions: ApiConfigOptions = {
    baseURL: isDevelopment
      ? "http://localhost:8082/api"
      : window.location.origin + "/api",
    timeout: 10000,
    tokenStorageKey: TOKENSTORAGEKEY,
    router: router,
  };

  const finalOptions = { ...defaultOptions, ...customOptions };

  console.log("🚀 Initializing API service with config:", {
    baseURL: finalOptions.baseURL,
    timeout: finalOptions.timeout,
    tokenStorageKey: finalOptions.tokenStorageKey,
    hasRouter: !!finalOptions.router,
  });

  initializeApiConfig(finalOptions);
};



/**
 * Development-specific initialization
 */
export const initializeDevEnvironment = (): void => {
  if (import.meta.env.MODE === "development") {
    console.log("🔧 Development mode detected");

    // Add development-specific configurations
    // Enable debug logging, mock services, etc.
  }
};

/**
 * Production-specific initialization
 */
export const initializeProductionEnvironment = (): void => {
  if (import.meta.env.MODE === "production") {
    console.log("🚀 Production mode detected");

    // Add production-specific configurations
    // Disable console.log, enable error reporting, etc.
  }
};
