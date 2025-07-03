/**
 * Bundles Store - TypeScript Version
 * 
 * Pinia store for managing bundles and installed bundles.
 * Handles all operations related to bundles in the ComfyUI application.
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { defineStore } from 'pinia';
import api from '../services/api';
import type {
  Bundle,
  InstalledBundle,
  BundlesStoreState,
  InstallProgress,
  BundleInstallOptions,
  BundleFilterOptions,
} from './types/bundles.types';

export const useBundlesStore = defineStore('bundles', {
  // === STATE ===
  state: (): BundlesStoreState => ({
    bundles: [],
    installedBundles: [],
    loading: false,
    installedLoading: false,
    error: null,
    installedError: null,
    selectedBundles: [],
    installProgress: {},
    bundleCategories: []
  }),

  // === GETTERS ===
  getters: {
    /**
     * Check if a bundle is installed
     * 
     * **Description:** Returns a function that checks if a bundle is installed.
     * **Returns:** Function that takes bundleId and returns boolean
     */
    isBundleInstalled(): (bundleId: string, profile : string) => boolean {
      return (bundleId: string, profile : string): boolean => {
        return this.installedBundles.some((installedBundle: InstalledBundle) => installedBundle.bundle_id === bundleId && installedBundle.profile === profile && installedBundle.status === 'completed');
      };
    },

    /**
     * Check if a bundle is selected
     * 
     * **Description:** Returns a function that checks if a bundle is selected.
     * **Returns:** Function that takes bundleId and returns boolean
     */
    isBundleSelected(): (bundleId: string) => boolean {
      return (bundleId: string): boolean => {
        return this.selectedBundles.some((bundle: Bundle) => bundle.id === bundleId);
      };
    },

    /**
     * Get install progress for a bundle
     * 
     * **Description:** Returns a function that gets install progress for a bundle.
     * **Returns:** Function that takes bundleId and returns progress object or null
     */
    getInstallProgress(): (bundleId: string) => InstallProgress | null {
      return (bundleId: string): InstallProgress | null => {
        return this.installProgress[bundleId] || null;
      };
    },

    /**
     * Get selected bundles count
     * 
     * **Description:** Returns the number of selected bundles.
     * **Returns:** Number of selected bundles
     */
    selectedBundlesCount(): number {
      return this.selectedBundles.length;
    },

    /**
     * Get total bundles count
     * 
     * **Description:** Returns the total number of available bundles.
     * **Returns:** Total number of available bundles
     */
    totalBundlesCount(): number {
      return this.bundles.length;
    },

    /**
     * Get installed bundles count
     * 
     * **Description:** Returns the number of installed bundles.
     * **Returns:** Number of installed bundles
     */
    installedBundlesCount(): number {
      return this.installedBundles.length;
    },

    /**
     * Check if any loading operation is in progress
     * 
     * **Description:** Returns true if any loading operation is active.
     * **Returns:** True if any loading operation is active
     */
    isLoading(): boolean {
      return this.loading || this.installedLoading;
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Upload a bundle ZIP file
     *
     * **Description:** Uploads and imports a bundle from a ZIP file to the server, then refreshes the bundles list.
     * **Parameters:**
     * - `file` (File): ZIP file containing bundle data
     * **Returns:** Promise that resolves with the upload response object
     */
    async uploadBundleZip(file: File): Promise<{ ok: boolean; message: string; bundle_id: string }> {
      try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/bundles/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        await this.fetchBundles();
        return response.data;
      } catch (error: any) {
        console.error('Error uploading bundle ZIP:', error);
        throw error;
      }
    },
    /**
     * Delete a bundle by ID
     * 
     * **Description:** Deletes a bundle from the server and refreshes the bundles list.
     * **Parameters:**
     * - `bundleId` (string): The ID of the bundle to delete
     * **Returns:** Promise that resolves when deletion is complete
     */
    async deleteBundle(bundleId: string): Promise<void> {
      try {
        await api.delete(`/bundles/${bundleId}`);
        // Refresh bundles list after deletion
        await this.fetchBundles();
      } catch (error: any) {
        console.error('Error deleting bundle:', error);
        throw error;
      }
    },

    /**
     * Fetch available bundles from the API
     * 
     * **Description:** Loads all available bundles from the server.
     * **Parameters:** None
     * **Returns:** Promise that resolves when bundles are loaded
     */
    async fetchBundles(): Promise<void> {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get<Bundle[]>('/bundles/');
        this.bundles = response.data || [];
      } catch (error: any) {
        this.error = error.message;
        console.error('Error fetching bundles:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch installed bundles from the API
     * 
     * **Description:** Loads all installed bundles from the server.
     * **Parameters:** None
     * **Returns:** Promise that resolves when installed bundles are loaded
     */
    async fetchInstalledBundles(): Promise<void> {
      this.installedLoading = true;
      this.installedError = null;

      try {
        const response = await api.get<InstalledBundle[]>('/bundles/installed');
        this.installedBundles = response.data || [];
      } catch (error: any) {
        this.installedError = error.message;
        console.error('Error fetching installed bundles:', error);
        throw error;
      } finally {
        this.installedLoading = false;
      }
    },

    /**
     * Install a bundle
     * 
     * **Description:** Installs a bundle with optional configuration.
     * **Parameters:**
     * - `bundle` (Bundle): The bundle to install
     * - `options` (BundleInstallOptions, optional): Installation options
     * **Returns:** Promise that resolves when installation is complete
     */
    async installBundle(bundle: Bundle, options?: BundleInstallOptions): Promise<any> {
      try {
        // Initialize install progress
        this.installProgress[bundle.id] = {
          bundleId: bundle.id,
          progress: 0,
          status: 'pending',
          message: 'Starting installation...'
        };

        const response = await api.post('/bundles/install', { bundle, options });

        // Update install progress
        this.installProgress[bundle.id] = {
          bundleId: bundle.id,
          progress: 100,
          status: 'completed',
          message: 'Installation completed'
        };

        // Refresh installed bundles after successful installation
        await this.fetchInstalledBundles();

        return response.data;
      } catch (error: any) {
        // Update install progress with error
        this.installProgress[bundle.id] = {
          bundleId: bundle.id,
          progress: 0,
          status: 'failed',
          error: error.message,
          message: 'Installation failed'
        };
        console.error('Error installing bundle:', error);
        throw error;
      }
    },

    /**
     * Uninstall a bundle
     * 
     * **Description:** Uninstalls a bundle from the system.
     * **Parameters:**
     * - `bundle` (Bundle): The bundle to uninstall
     * **Returns:** Promise that resolves when uninstallation is complete
     */
    async uninstallBundle(bundleId: string, profile : string): Promise<any> {
      try {
        const response = await api.delete(`/bundles/uninstall/${bundleId}`);

        // Refresh installed bundles after successful uninstallation
        await this.fetchInstalledBundles();

        // Remove from selected bundles if selected
        // @TODO : à coder
        // this.deselectBundles([bundle]);

        return response.data;
      } catch (error: any) {
        console.error('Error uninstalling bundle:', error);
        throw error;
      }
    },

    /**
     * Update install progress for a bundle
     * 
     * **Description:** Updates the installation progress for a specific bundle.
     * **Parameters:**
     * - `bundleId` (string): The bundle ID
     * - `progress` (number): Progress percentage (0-100)
     * - `status` (string): Installation status
     * - `message` (string, optional): Progress message
     * **Returns:** void
     */
    updateInstallProgress(
      bundleId: string, 
      progress: number, 
      status: InstallProgress['status'] = 'installing',
      message?: string
    ): void {
      this.installProgress[bundleId] = {
        bundleId,
        progress,
        status,
        message: message || `Installing... ${progress}%`
      };
    },

    /**
     * Cancel bundle installation
     * 
     * **Description:** Cancels an ongoing bundle installation.
     * **Parameters:**
     * - `bundleId` (string): The bundle ID to cancel
     * **Returns:** Promise that resolves when cancellation is complete
     */
    async cancelInstallation(bundleId: string): Promise<void> {
      try {
        await api.post(`/bundles/install/${bundleId}/cancel`);
        // Remove install progress
        delete this.installProgress[bundleId];
      } catch (error: any) {
        console.error('Error canceling installation:', error);
        throw error;
      }
    },

    /**
     * Create a new bundle
     * 
     * **Description:** Creates a new bundle on the server.
     * **Parameters:**
     * - `bundleData` (Partial<Bundle>): The data for the new bundle
     * **Returns:** Promise that resolves with the created bundle
     */
    async createBundle(bundleData: Partial<Bundle>): Promise<Bundle> {
      try {
        const response = await api.post<Bundle>('/bundles/', bundleData);
        // Refresh bundles list after creation
        await this.fetchBundles();
        return response.data;
      } catch (error: any) {
        console.error('Error creating bundle:', error);
        throw error;
      }
    },

    /**
     * Update a bundle
     * 
     * **Description:** Updates an existing bundle on the server.
     * **Parameters:**
     * - `bundleId` (string): The ID of the bundle to update
     * - `bundleData` (Partial<Bundle>): The updated bundle data
     * **Returns:** Promise that resolves with the updated bundle
     */
    async updateBundle(bundleId: string, bundleData: Partial<Bundle>): Promise<Bundle> {
      try {
        const response = await api.put<Bundle>(`/bundles/${bundleId}`, bundleData);
        return response.data;
      } catch (error: any) {
        console.error('Error updating bundle:', error);
        throw error;
      }
    },

    /**
     * Toggle bundle selection
     * 
     * **Description:** Toggles the selection state of a bundle.
     * **Parameters:**
     * - `bundle` (Bundle): The bundle to toggle
     * **Returns:** void
     */
    toggleBundleSelection(bundle: Bundle): void {
      const index = this.selectedBundles.findIndex((b: Bundle) => b.id === bundle.id);
      if (index > -1) {
        this.selectedBundles.splice(index, 1);
      } else {
        this.selectedBundles.push(bundle);
      }
    },

    /**
     * Select multiple bundles
     * 
     * **Description:** Adds multiple bundles to the selection.
     * **Parameters:**
     * - `bundles` (Bundle[]): Array of bundles to select
     * **Returns:** void
     */
    selectBundles(bundles: Bundle[]): void {
      bundles.forEach((bundle: Bundle) => {
        if (!this.isBundleSelected(bundle.id)) {
          this.selectedBundles.push(bundle);
        }
      });
    },

    /**
     * Deselect multiple bundles
     * 
     * **Description:** Removes multiple bundles from the selection.
     * **Parameters:**
     * - `bundles` (Bundle[]): Array of bundles to deselect
     * **Returns:** void
     */
    deselectBundles(bundles: Bundle[]): void {
      bundles.forEach((bundle: Bundle) => {
        const index = this.selectedBundles.findIndex((b: Bundle) => b.id === bundle.id);
        if (index > -1) {
          this.selectedBundles.splice(index, 1);
        }
      });
    },

    /**
     * Select all bundles
     * 
     * **Description:** Selects all available bundles.
     * **Parameters:** None
     * **Returns:** void
     */
    selectAllBundles(): void {
      this.selectedBundles = [...this.bundles];
    },

    /**
     * Clear all selected bundles
     * 
     * **Description:** Clears all selected bundles.
     * **Parameters:** None
     * **Returns:** void
     */
    clearSelectedBundles(): void {
      this.selectedBundles = [];
    },

   

    /**
     * Install selected bundles
     * 
     * **Description:** Installs all currently selected bundles.
     * **Parameters:** None
     * **Returns:** Promise that resolves when all installations are complete
     */
    async installSelectedBundles(): Promise<void> {
      const installPromises = this.selectedBundles.map((bundle: Bundle) => 
        this.installBundle(bundle)
      );
      
      try {
        await Promise.all(installPromises);
        this.clearSelectedBundles();
      } catch (error: any) {
        console.error('Error installing selected bundles:', error);
        throw error;
      }
    },

    /**
     * Get bundle by ID
     * 
     * **Description:** Finds a bundle by its ID.
     * **Parameters:**
     * - `bundleId` (string): The bundle ID to find
     * **Returns:** The bundle object or null if not found
     */
    getBundleById(bundleId: string): Bundle | null {
      return this.bundles.find((bundle: Bundle) => bundle.id === bundleId) || null;
    },

    /**
     * Search bundles by name or description
     * 
     * **Description:** Searches bundles by name, description, or author.
     * **Parameters:**
     * - `query` (string): Search query
     * **Returns:** Array of matching bundles
     */
    searchBundles(query: string): Bundle[] {
      if (!query) return this.bundles;

      const lowercaseQuery = query.toLowerCase();
      return this.bundles.filter((bundle: Bundle) => 
        (bundle.name && bundle.name.toLowerCase().includes(lowercaseQuery)) ||
        (bundle.description && bundle.description.toLowerCase().includes(lowercaseQuery)) ||
        (bundle.author && bundle.author.toLowerCase().includes(lowercaseQuery))
      );
    },

    /**
     * Refresh bundles data
     * 
     * **Description:** Refreshes both available and installed bundles data.
     * **Parameters:** None
     * **Returns:** Promise that resolves when refresh is complete
     */
    async refreshBundles(): Promise<void> {
      await Promise.all([
        this.fetchBundles(),
        this.fetchInstalledBundles()
      ]);
    },

    /**
     * Clear all bundles data
     * 
     * **Description:** Clears all bundles data and resets the store state.
     * **Parameters:** None
     * **Returns:** void
     */
    clearBundles(): void {
      this.bundles = [];
      this.installedBundles = [];
      this.selectedBundles = [];
      this.installProgress = {};
      this.error = null;
      this.installedError = null;
    },

    /**
     * Set bundles error
     * 
     * **Description:** Sets an error message for bundles operations.
     * **Parameters:**
     * - `errorMessage` (string): Error message to set
     * **Returns:** void
     */
    setError(errorMessage: string): void {
      this.error = errorMessage;
    },

    /**
     * Set installed bundles error
     * 
     * **Description:** Sets an error message for installed bundles operations.
     * **Parameters:**
     * - `errorMessage` (string): Error message to set
     * **Returns:** void
     */
    setInstalledError(errorMessage: string): void {
      this.installedError = errorMessage;
    },

    /**
     * Clear bundles errors
     * 
     * **Description:** Clears all error messages.
     * **Parameters:** None
     * **Returns:** void
     */
    clearErrors(): void {
      this.error = null;
      this.installedError = null;
    }
  }
});
