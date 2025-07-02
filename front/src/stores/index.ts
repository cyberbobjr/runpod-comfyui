/**
 * Centralized export file for all Pinia stores - TypeScript Version
 *
 * This file exports all stores for easy importing throughout the application
 * and provides utilities for store initialization and management.
 *
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { useAuthStore } from "./auth";
import { useBundlesStore } from "./bundles";
import { useModelsStore } from "./models";
import { useUIStore } from "./ui";
import { useWorkflowsStore } from "./workflows";

// Re-export Pinia for convenience
export { createPinia, setActivePinia } from "pinia";

/**
 * Initialize all stores
 *
 * **Description:** Sets up stores with their initial data, handling authentication state and loading data accordingly.
 * **Parameters:** None
 * **Returns:** Promise that resolves when all stores are initialized
 *
 * @returns {Promise<void>} Promise that resolves when all stores are initialized
 */
export async function initializeStores(): Promise<void> {
  try {
    const authStore = useAuthStore();
    const modelsStore = useModelsStore();
    const bundlesStore = useBundlesStore();
    const workflowsStore = useWorkflowsStore();
    const uiStore = useUIStore();

    // Initialize UI first
    uiStore.initializeUI();

    // Initialize data stores if user is authenticated
    if (authStore.isAuthenticated) {
      await Promise.all([
        modelsStore.fetchModels(),
        bundlesStore.fetchBundles(),
        bundlesStore.fetchInstalledBundles(),
        workflowsStore.fetchWorkflows(),
      ]);
    }

    console.log("All stores initialized successfully");
  } catch (error: any) {
    console.error("Error initializing stores:", error);
    throw error;
  }
}

/**
 * Reset all stores to their initial state
 *
 * **Description:** Resets all stores to their initial state, useful for logout or app reset scenarios.
 * **Parameters:** None
 * **Returns:** void
 */
export function resetAllStores(): void {
  try {
    // Use require for synchronous imports in reset scenario
    const authStore = useAuthStore();
    const modelsStore = useModelsStore();
    const bundlesStore = useBundlesStore();
    const workflowsStore = useWorkflowsStore();
    const uiStore = useUIStore();

    // Logout user (this resets auth store)
    authStore.logout();

    // Clear all data stores
    modelsStore.clearModels();
    bundlesStore.clearBundles();
    workflowsStore.clearWorkflows();

    // Reset UI state
    uiStore.resetUIState();

    console.log("All stores reset successfully");
  } catch (error: any) {
    console.error("Error resetting stores:", error);
    throw error;
  }
}

/**
 * Store initialization status type
 */
export interface StoreInitializationStatus {
  isInitializing: boolean;
  initialized: boolean;
  error: string | null;
}

/**
 * Get store initialization status
 *
 * **Description:** Returns the current initialization status of all stores.
 * **Parameters:** None
 * **Returns:** Store initialization status object
 */
export function getStoreInitializationStatus(): StoreInitializationStatus {
  // This could be extended to track actual initialization state
  // For now, return a basic implementation
  return {
    isInitializing: false,
    initialized: true,
    error: null,
  };
}
