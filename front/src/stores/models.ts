import { defineStore } from "pinia";
import api from "../services/api"; // Assuming you have an api.js file for API requests
import {
  type Model,
  type DownloadProgress,
  type ModelFilterCriteria,
  type ModelEntry,
  type ModelsState,
  type CompleteModelsApiResponse,
  getModelId,
  DownloadStatus,
} from "./types/models.types";

/**
 * # Models Store Documentation
 *
 * Pinia store for managing AI models, bundle installations, and download tracking in ComfyUI.
 * This store centralizes all operations related to model management including downloading,
 * installation progress tracking, selection management, and API interactions.
 *
 * ## State Variables (Public)
 *
 * ### models
 * **Description:** Array containing all available AI models from the API.
 * **Type:** Array<Model>
 * **Usage Example:**
 * ```typescript
 * const modelsStore = useModelsStore()
 * console.log(modelsStore.models) // Display all models
 * const checkpointModels = modelsStore.models.filter(m => m.type === 'checkpoint')
 * ```
 *
 * ### loading
 * **Description:** Boolean indicating if models are currently being fetched from the API.
 * **Type:** boolean
 * **Usage Example:**
 * ```typescript
 * const { loading } = storeToRefs(modelsStore)
 * // In template: <div v-if="loading">Loading models...</div>
 * ```
 *
 * ### error
 * **Description:** Error message string when API operations fail, null when no error.
 * **Type:** string | null
 * **Usage Example:**
 * ```typescript
 * const { error } = storeToRefs(modelsStore)
 * // In template: <div v-if="error" class="error">{{ error }}</div>
 * ```
 *
 * ### selectedModels
 * **Description:** Array of models currently selected by the user for batch operations.
 * **Type:** Array<Model>
 * **Usage Example:**
 * ```typescript
 * console.log(`${modelsStore.selectedModels.length} models selected`)
 * // Download all selected models
 * await modelsStore.downloadSelectedModels()
 * ```
 *
 * ### downloadProgress
 * **Description:** Map containing real-time download progress data from the API.
 * **Type:** Map<string, DownloadProgress>
 * **Usage Example:**
 * ```typescript
 * const progress = modelsStore.downloadProgress.get('model_id')
 * if (progress) {
 *   console.log(`Download at ${progress.progress}% - Status: ${progress.status}`)
 * }
 * ```
 *
 * ### installedModels
 * **Description:** Set containing IDs of models that are installed locally.
 * **Type:** Set<string>
 * **Usage Example:**
 * ```typescript
 * if (modelsStore.installedModels.has('stable-diffusion-v1-5')) {
 *   console.log('Model is already installed')
 * }
 * ```
 *
 * ### bundleInstallations
 * **Description:** Map tracking active bundle installation processes with detailed progress.
 * **Type:** Map<string, BundleInstallation>
 * **Usage Example:**
 * ```typescript
 * const installation = modelsStore.bundleInstallations.get('bundle_123_1672531200000')
 * if (installation) {
 *   console.log(`Bundle installation: ${installation.progress}% - ${installation.currentStep}`)
 * }
 * ```
 *
 * ### modelDownloads
 * **Description:** Map tracking individual model download processes for UI display.
 * **Type:** Map<string, ModelDownload>
 * **Usage Example:**
 * ```typescript
 * for (const [downloadId, download] of modelsStore.modelDownloads.entries()) {
 *   console.log(`${download.modelName}: ${download.progress}%`)
 * }
 * ```
 */
export const useModelsStore = defineStore("models", {
  // === STATE ===
  state: (): ModelsState => ({
    models: [],
    loading: false,
    error: null,
    selectedModels: [],
    downloadProgress: [],
    _downloadPollingInterval: null,
  }),

  // === GETTERS ===
  getters: {
    installedModels: (state: ModelsState): Set<string> => {
      return state.models.reduce((set, model) => {
        if (!!model.exists) set.add(getModelId(model));
        return set;
      }, new Set<string>());
    },
    /**
     * Check if a model is currently downloading (progress < 100 and status is 'downloading')
     * @returns {Function} Function that takes modelId and returns boolean
     */
    isModelDownloading:
      (state: ModelsState) =>
      (modelId: string): boolean => {
        const prog = state.downloadProgress.find(
          (progress) => progress.model_id === modelId
        );
        return prog
          ? prog.status === DownloadStatus.DOWNLOADING && prog.progress < 100
          : false;
      },

    /**
     * Get models grouped by type
     * @returns {Object} Models grouped by their type (clip, vae, unet, etc.)
     */
    modelsByType: (state: ModelsState): Record<string, Model[]> => {
      const grouped: Record<string, Model[]> = {};
      state.models.forEach((model) => {
        if (!grouped[model.type]) {
          grouped[model.type] = [];
        }
        grouped[model.type].push(model);
      });
      return grouped;
    },

    /**
     * Get models grouped by tags
     * @returns {Object} Models grouped by their tags
     */
    modelsByTags: (state: ModelsState): Record<string, Model[]> => {
      const grouped: Record<string, Model[]> = {};
      state.models.forEach((model) => {
        if (model.tags && model.tags.length > 0) {
          model.tags.forEach((tag) => {
            if (!grouped[tag]) {
              grouped[tag] = [];
            }
            grouped[tag].push(model);
          });
        }
      });
      return grouped;
    },

    /**
     * Get available model types
     * @returns {Array} List of unique model types
     */
    availableModelTypes: (state: ModelsState): string[] => {
      return Array.from(new Set(state.models.map((model) => model.type)));
    },

    /**
     * Get available model tags
     * @returns {Array} List of unique model tags
     */
    availableModelTags: (state: ModelsState): string[] => {
      const tags = new Set<string>();
      state.models.forEach((model) => {
        if (model.tags) {
          model.tags.forEach((tag) => tags.add(tag));
        }
      });
      return Array.from(tags);
    },

    /**
     * Get models by group name
     * @returns {Function} Function that takes groupName and returns models
     */
    modelsByGroup:
      (state: ModelsState) =>
      (groupName: string): Model[] => {
        return state.models.filter((model) => model.group === groupName);
      },

    /**
     * Check if a model is selected
     * @returns {Function} Function that takes modelId and returns boolean
     */
    isModelSelected:
      (state: ModelsState) =>
      (modelId: string): boolean => {
        return state.selectedModels.some((model) => model.id === modelId);
      },

    /**
     * Get selected models count
     * @returns {Number} Number of selected models
     */
    selectedModelsCount: (state: ModelsState): number => {
      return state.selectedModels.length;
    },

    /**
     * Get total models count
     * @returns {Number} Total number of models
     */
    totalModelsCount: (state: ModelsState): number => {
      return state.models.length;
    },

    getProgressByModelId:
      (state: ModelsState) =>
      (modelId: string): DownloadProgress | undefined => {
        return state.downloadProgress.find(
          (progress) => progress.model_id === modelId
        );
      },

    removeProgressByModelId:
      (state: ModelsState) =>
      (modelId: string): void => {
        const index = state.downloadProgress.findIndex(
          (progress) => progress.model_id === modelId
        );
        if (index !== -1) {
          state.downloadProgress.splice(index, 1);
        }
      },
  },

  // === ACTIONS ===
  actions: {
    /**
     * Check if a model is installed
     * @returns {Function} Function that takes modelId (string) or model (Model object) and returns boolean
     */
    isModelInstalled(modelOrId: string | Model): boolean {
      let modelId: string;
      if (typeof modelOrId === "string") {
        modelId = modelOrId;
      } else {
        modelId = getModelId(modelOrId);
      }
      // `this` est correctement typé ici
      return modelId ? this.installedModels.has(modelId) : false;
    },
    /**
     * Start polling the backend for download progress and update the store
     * @param {Number} intervalMs - Polling interval in ms (default: 2000)
     */
    startDownloadPolling(intervalMs: number = 2000): void {
      if (this._downloadPollingInterval) return;
      this._downloadPollingInterval = setInterval(
        this.updateModelDownloadProgress,
        intervalMs
      );
      // Initial fetch
      this.updateModelDownloadProgress();
    },

    /**
     * Stop polling the backend for download progress
     */
    stopDownloadPolling(): void {
      if (this._downloadPollingInterval) {
        clearInterval(this._downloadPollingInterval);
        this._downloadPollingInterval = null;
      }
    },

    /**
     * Fetch models from the API
     * @returns {Promise} Promise that resolves when models are loaded
     */
    async fetchModels(): Promise<void> {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get<CompleteModelsApiResponse>(
          "/jsonmodels/"
        );
        const data = response.data;

        // Parse models from the groups structure
        const allModels: Model[] = [];
        if (data.groups) {
          Object.keys(data.groups).forEach((groupName) => {
            data.groups[groupName].forEach((model: Model) => {
              allModels.push({
                ...model,
                group: groupName,
                id: `${groupName}_${model.url.split("/").pop()}`,
              });
            });
          });
        }

        this.models = allModels;
      } catch (error: any) {
        this.error = error.message;
        console.error("Error fetching models:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch all ongoing downloads from the backend
     * @returns {Promise} Promise resolving to all downloads status
     */
    async fetchAllDownloads(): Promise<DownloadProgress[]> {
      try {
        const response = await api.get<DownloadProgress[]>("/downloads");
        return response.data;
      } catch (error: any) {
        this.setError(error.message);
        throw error;
      }
    },

    /**
     * Start downloading one or more models
     * @param {Object|Array} entries - Model entry or list of entries
     * @returns {Promise} Download status result(s)
     */
    async startDownload(entries: ModelEntry | ModelEntry[]): Promise<any> {
      try {
        const response = await api.post("/downloads/start", entries);
        return response.data;
      } catch (error: any) {
        this.setError(error.message);
        throw error;
      }
    },

    /**
     * Stop an ongoing download
     * @param {Object} entry - Model entry to stop
     * @returns {Promise} Operation status
     */
    async stopDownload(entry: ModelEntry): Promise<any> {
      try {
        const response = await api.post("/downloads/stop", entry);
        return response.data;
      } catch (error: any) {
        this.setError(error.message);
        throw error;
      }
    },

    /**
     * Delete one or more models
     * @param {Object|Array} entries - Model entry or list of entries
     * @returns {Promise} Deletion status result(s)
     */
    async deleteModels(entries: ModelEntry | ModelEntry[]): Promise<any> {
      try {
        const response = await api.delete("/downloads/", { data: entries });
        return response.data;
      } catch (error: any) {
        this.setError(error.message);
        throw error;
      }
    },

    /**
     * Cancel model download
     * @param {String} modelId - The model ID to cancel
     */
    async cancelDownload(modelId: string): Promise<void> {
      try {
        await api.post(`/models/download/${modelId}/cancel`);
        // Remove download progress
        this.removeProgressByModelId(modelId);
      } catch (error: any) {
        console.error("Error canceling download:", error);
        throw error;
      }
    },

    /**
     * Toggle model selection
     * @param {Object} model - The model to toggle
     */
    toggleModelSelection(model: Model): void {
      const index = this.selectedModels.findIndex(
        (m: Model) => m.id === model.id
      );
      if (index > -1) {
        this.selectedModels.splice(index, 1);
      } else {
        this.selectedModels.push(model);
      }
    },

    /**
     * Select multiple models
     * @param {Array} models - Array of models to select
     */
    selectModels(models: Model[]): void {
      models.forEach((model: Model) => {
        if (!this.isModelSelected(model.id)) {
          this.selectedModels.push(model);
        }
      });
    },

    /**
     * Deselect multiple models
     * @param {Array} models - Array of models to deselect
     */
    deselectModels(models: Model[]): void {
      models.forEach((model: Model) => {
        const index = this.selectedModels.findIndex(
          (m: Model) => m.id === model.id
        );
        if (index > -1) {
          this.selectedModels.splice(index, 1);
        }
      });
    },

    /**
     * Select all models
     */
    selectAllModels(): void {
      this.selectedModels = [...this.models];
    },

    /**
     * Clear all selected models
     */
    clearSelectedModels(): void {
      this.selectedModels = [];
    },

    /**
     * Select models by type
     * @param {String} type - Model type to select
     */
    selectModelsByType(type: string): void {
      const modelsOfType = this.models.filter(
        (model: Model) => model.type === type
      );
      this.selectModels(modelsOfType);
    },

    /**
     * Select models by tag
     * @param {String} tag - Model tag to select
     */
    selectModelsByTag(tag: string): void {
      const modelsWithTag = this.models.filter(
        (model: Model) => model.tags && model.tags.includes(tag)
      );
      this.selectModels(modelsWithTag);
    },

    /**
     * Download selected models
     * @returns {Promise} Promise that resolves when all downloads are complete
     */
    async downloadSelectedModels(): Promise<void> {
      const downloadPromises = this.selectedModels.map((model: Model) =>
        this.startDownload({
          model_id: model.id,
          dest: model.dest,
          git: model.git,
          url: model.url,
        })
      );

      try {
        await Promise.all(downloadPromises);
        this.clearSelectedModels();
      } catch (error: any) {
        console.error("Error downloading selected models:", error);
        throw error;
      }
    },

    /**
     * Delete a model
     * @param {Object} model - The model to delete
     * @returns {Promise} Promise that resolves when model is deleted
     */
    async deleteModel(model: Model): Promise<any> {
      try {
        const response = await api.delete(`/models/${model.id}`);
        // Remove from installed models
        this.installedModels.delete(model.id);
        // Remove from selected models if selected
        this.deselectModels([model]);
        return response.data;
      } catch (error: any) {
        console.error("Error deleting model:", error);
        throw error;
      }
    },

    /**
     * Get model by ID
     * @param {String} modelId - The model ID to find
     * @returns {Object|null} The model object or null if not found
     */
    getModelById(modelId: string): Model | null {
      return this.models.find((model: Model) => model.id === modelId) || null;
    },

    /**
     * Search models by name or description
     * @param {String} query - Search query
     * @returns {Array} Array of matching models
     */
    searchModels(query: string): Model[] {
      if (!query) return this.models;

      const lowercaseQuery = query.toLowerCase();
      return this.models.filter(
        (model: Model) =>
          (model.name && model.name.toLowerCase().includes(lowercaseQuery)) ||
          (model.description &&
            model.description.toLowerCase().includes(lowercaseQuery)) ||
          (model.tags &&
            model.tags.some((tag: string) =>
              tag.toLowerCase().includes(lowercaseQuery)
            ))
      );
    },

    /**
     * Filter models by criteria
     * @param {Object} criteria - Filter criteria
     * @returns {Array} Array of filtered models
     */
    filterModels(criteria: ModelFilterCriteria): Model[] {
      let filteredModels = this.models;

      if (criteria.type) {
        filteredModels = filteredModels.filter(
          (model: Model) => model.type === criteria.type
        );
      }

      if (criteria.tags && criteria.tags.length > 0) {
        filteredModels = filteredModels.filter(
          (model: Model) =>
            model.tags &&
            criteria.tags!.some((tag: string) => model.tags!.includes(tag))
        );
      }

      if (criteria.group) {
        filteredModels = filteredModels.filter(
          (model: Model) => model.group === criteria.group
        );
      }

      if (criteria.installed !== undefined) {
        filteredModels = filteredModels.filter(
          (model: Model) =>
            this.isModelInstalled(model.id) === criteria.installed
        );
      }

      return filteredModels;
    },

    /**
     * Refresh models data
     * @returns {Promise} Promise that resolves when refresh is complete
     */
    async refreshModels(): Promise<void> {
      return await this.fetchModels();
    },

    /**
     * Clear all models data
     */
    clearModels(): void {
      this.models = [];
      this.selectedModels = [];
      this.downloadProgress = [];
      this.error = null;
    },

    /**
     * Set models error
     * @param {String} errorMessage - Error message to set
     */
    setError(errorMessage: string): void {
      this.error = errorMessage;
    },

    /**
     * Clear models error
     */
    clearError(): void {
      this.error = null;
    },

    // === BUNDLE INSTALLATION MANAGEMENT ===

    /**
     * Start bundle installation
     * @param {String} bundleId - Bundle ID to install
     * @param {String} bundleName - Bundle name for display
     * @param {Array} profiles - List of profiles to install
     * @returns {String} Installation ID
     */
    async startBundleInstallation(
      bundleId: string,
      profiles: string[]
    ): Promise<string> {
      // Simplified: Only trigger the download of all models in the bundle, and rely on updateModelDownloadProgress for progress tracking.
      // This avoids duplicating download tracking logic and UI.
      try {
        // Start installation for each profile (triggers backend to download models)
        for (const profile of profiles) {
          await api.post("/bundles/install", {
            bundle_id: bundleId,
            profile: profile,
          });
        }
        // No custom polling or bundleInstallations tracking: rely on updateModelDownloadProgress for all download progress UI.
        return bundleId;
      } catch (err: any) {
        this.setError(err.response?.data?.detail || err.message);
        throw err;
      }
    },

    // === MODEL DOWNLOAD MANAGEMENT ===

    /**
     * Start model download tracking
     * @param {String} modelId - Model ID to track
     * @param {String} modelName - Model name for display
     * @returns {String} Model ID
     */
    async startModelDownloadTracking(
      modelId: string,
      modelName: string
    ): Promise<string> {
      console.log(`Starting download tracking for ${modelId}`);

      this.startDownloadPolling();

      return modelId;
    },

    /**
     * Update model download progress from API
     *
     * Description:
     * Polls the backend API ("/downloads") to retrieve the current download status for all models, updates the store's download progress map, and synchronizes the UI-tracked downloads (modelDownloads) with the backend state. This method is responsible for:
     * - Fetching the latest download progress for all models from the backend.
     * - Updating the downloadProgress map with the latest data.
     * - Iterating through each download to update or add entries in modelDownloads for UI tracking.
     * - Handling active downloads (progress < 100 and not stopped), stopped downloads, and cleaning up completed or cancelled downloads.
     * - Stopping polling if there are no active downloads left.
     *
     * Returns: Promise<void>
     *
     * Example usage:
     *   await store.updateModelDownloadProgress();
     */
    async updateModelDownloadProgress(): Promise<void> {
      try {
        // Fetch the latest download status for all models from the backend
        this.downloadProgress = await this.fetchAllDownloads();
        // Stop polling if no downloads
        if (this.downloadProgress.length === 0) {
          this.stopDownloadPolling();
          this.refreshModels()
        }
      } catch (error: any) {
        this.setError(error.message);
        console.error("Error updating model download progress:", error);
      }
    },

    /**
     * Cancel model download
     * @param {String} downloadId - Download ID or model ID to cancel
     */
    async cancelModelDownload(downloadId: string): Promise<void> {
      let isModelDownloading = this.isModelDownloading(downloadId);

      if (isModelDownloading) {
        try {
          await api.post("/downloads/stop", { dest: downloadId });
          this.removeProgressByModelId(downloadId);
        } catch (error: any) {
          console.error("Error cancelling download:", error);
          this.setError("Failed to cancel download");
        }
      } else {
        console.warn("Download not found for cancellation:", downloadId);
      }
    },

    /**
     * Restore active downloads on startup
     */
    async restoreActiveDownloads(): Promise<void> {
      try {
        const downloads: DownloadProgress[] = await this.fetchAllDownloads();
        const isDownloadingInProgress = downloads.some(
          (download) =>
            download.status === DownloadStatus.DOWNLOADING && download.progress < 100
        );

        if (isDownloadingInProgress) {
          this.startDownloadPolling();
        }
      } catch (error: any) {
        console.error("Error restoring active downloads:", error);
      }
    },

    /**
     * Force refresh downloads from API
     * @returns {Object} Downloads data
     */
    async refreshDownloads(): Promise<void> {
      try {
        this.downloadProgress = await this.fetchAllDownloads();
      } catch (error: any) {
        console.error("Error refreshing downloads:", error);
        this.setError("Failed to refresh downloads");
        throw error;
      }
    },

    /**
     * Start global download polling
     */
    startGlobalDownloadPolling(): void {
      if (!this._downloadPollingInterval) {
        this.startDownloadPolling();
      } else {
        console.log("Download polling already active");
      }
    },
  },
});

// Re-export types for external use
export type {
  Model,
  DownloadProgress,
  ModelFilterCriteria,
  ModelEntry,
  ModelsState,
} from "./types/models.types";
