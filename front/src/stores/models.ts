import { defineStore } from "pinia";
import api from "../services/api"; // Assuming you have an api.js file for API requests
import {
  type Model,
  type DownloadProgress,
  type BundleInstallation,
  type ModelDownload,
  type ActiveInstallation,
  type ModelFilterCriteria,
  type ModelEntry,
  type ModelsState,
  type DownloadsApiResponse,
  type CompleteModelsApiResponse,
  getModelId,
} from "./types/models.types";
import { stat } from "fs";

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
    downloadProgress: new Map<string, DownloadProgress>(),
    _downloadPollingInterval: null,
    // Bundle installation tracking
    bundleInstallations: new Map<string, BundleInstallation>(),
    _bundlePollingInterval: null,
    // Model download tracking for UI display
    modelDownloads: new Map<string, ModelDownload>(),
  }),

  // === GETTERS ===
  getters: {
    installedModels: (state: ModelsState) : Set<string> => {
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
        const prog = state.downloadProgress.get(modelId);
        return prog
          ? prog.status === "downloading" && prog.progress < 100
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
     * Get download progress for a model
     * @returns {Function} Function that takes modelId and returns progress object
     */
    getDownloadProgress:
      (state: ModelsState) =>
      (modelId: string): DownloadProgress | null => {
        return state.downloadProgress.get(modelId) || null;
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

    /**
     * Get all active installations (bundles + models)
     * @returns {Array} List of active installations
     */
    activeInstallations: (state: ModelsState): ActiveInstallation[] => {
      const bundleInstallations = Array.from(
        state.bundleInstallations.entries()
      )
        .filter(
          ([_, installation]) =>
            installation.status !== "completed" &&
            installation.status !== "cancelled"
        )
        .map(([installationId, installation]) => ({
          downloadId: installationId,
          bundleId: installation.bundleId,
          bundleName: installation.bundleName,
          profiles: installation.profiles,
          status: installation.status,
          progress: installation.progress,
          currentStep: installation.currentStep,
          startTime: installation.startTime,
          errors: installation.errors,
        }));

      const modelDownloadsList = Array.from(state.modelDownloads.entries()).map(
        ([downloadId, download]) => ({
          downloadId,
          bundleId: download.modelId,
          bundleName: download.modelName,
          profiles: ["download"],
          status: download.status,
          progress: download.progress,
          currentStep: download.currentStep,
          startTime: download.startTime,
          errors: download.errors,
        })
      );

      return [...bundleInstallations, ...modelDownloadsList];
    },

    /**
     * Check if there are active installations
     * @returns {Boolean} True if there are active installations
     */
    hasActiveInstallations: (state: ModelsState): boolean => {
      const hasActiveDownloads = Array.from(
        state.downloadProgress.values()
      ).some((p) => p.status === "downloading");
      const hasActiveBundles = Array.from(
        state.bundleInstallations.values()
      ).some((b) => b.status === "installing");
      return hasActiveDownloads || hasActiveBundles;
    },

    /**
     * Get raw downloads data (equivalent to rawDownloads in useInstallProgress)
     * @returns {Object} Raw downloads data from API
     */
    rawDownloads: (state: ModelsState): DownloadProgress[] => {
      // Convert Map to array of values for components that need an array
      return Array.from(state.downloadProgress.values());
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
        this.refreshDownloadProgress,
        intervalMs
      );
      // Initial fetch
      this.refreshDownloadProgress();
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
     * Refresh download progress from backend and update downloadProgress state
     */
    async refreshDownloadProgress(): Promise<void> {
      try {
        const response = await api.get<DownloadsApiResponse>("/downloads/");
        const downloads = response.data || {};
        // Update downloadProgress with backend state
        this.downloadProgress = new Map(Object.entries(downloads));

        // Update model downloads and clean up finished ones
        await this.updateModelDownloadProgress();
      } catch (error: any) {
        this.setError(error.message);
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
    async fetchAllDownloads(): Promise<DownloadsApiResponse> {
      try {
        const response = await api.get<DownloadsApiResponse>("/downloads/");
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
     * Get download progress for a model
     * @param {Object} entry - Model entry to check progress
     * @returns {Promise} Progress info
     */
    async fetchDownloadProgress(entry: ModelEntry): Promise<DownloadProgress> {
      try {
        const response = await api.post("/downloads/progress", entry);
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
     * Update download progress for a model
     * @param {String} modelId - The model ID
     * @param {Number} progress - Progress percentage (0-100)
     * @param {String} status - Download status
     */
    updateDownloadProgress(
      modelId: string,
      progress: number,
      status: DownloadProgress["status"] = "downloading"
    ): void {
      this.downloadProgress.set(modelId, {
        progress,
        status,
        error: null,
      });
    },

    /**
     * Cancel model download
     * @param {String} modelId - The model ID to cancel
     */
    async cancelDownload(modelId: string): Promise<void> {
      try {
        await api.post(`/models/download/${modelId}/cancel`);
        // Remove download progress
        this.downloadProgress.delete(modelId);
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
      this.downloadProgress = new Map();
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
      bundleName: string,
      profiles: string[]
    ): Promise<string> {
      const installationId = `${bundleId}_${Date.now()}`;

      this.bundleInstallations.set(installationId, {
        bundleId,
        bundleName,
        profiles,
        status: "starting",
        progress: 0,
        currentStep: "Initializing installation...",
        steps: [],
        errors: [],
        startTime: Date.now(),
      });

      try {
        // Start installation for each profile
        for (const profile of profiles) {
          await api.post("/bundles/install", {
            bundle_id: bundleId,
            profile: profile,
          });
        }

        // Start polling for progress
        this.startBundlePolling(installationId);

        return installationId;
      } catch (err: any) {
        const installation = this.bundleInstallations.get(installationId);
        if (installation) {
          installation.status = "error";
          installation.errors.push(err.response?.data?.detail || err.message);
        }
        throw err;
      }
    },

    /**
     * Start bundle polling
     * @param {String} installationId - Installation ID to track
     */
    startBundlePolling(installationId: string): void {
      if (this._bundlePollingInterval) return;

      this._bundlePollingInterval = setInterval(async () => {
        try {
          await this.updateBundleInstallationProgress(installationId);
        } catch (err: any) {
          console.error("Error polling bundle installation progress:", err);
        }
      }, 1000);
    },

    /**
     * Update bundle installation progress
     * @param {String} installationId - Installation ID to update
     */
    async updateBundleInstallationProgress(
      installationId: string
    ): Promise<void> {
      const installation = this.bundleInstallations.get(installationId);
      if (
        !installation ||
        installation.status === "completed" ||
        installation.status === "error"
      ) {
        return;
      }

      try {
        // Check download status
        const downloadsResponse = await api.get("/downloads/");
        const downloads = downloadsResponse.data || {};

        // Check if bundle is installed
        const installedResponse = await api.get("/bundles/installed/");
        const installedBundles = installedResponse.data || [];

        const isInstalled = installedBundles.some(
          (b: any) =>
            b.id === installation.bundleId &&
            installation.profiles.includes(b.profile)
        );

        // Calculate progress based on downloads
        const downloadKeys = Object.keys(downloads);
        const activeDownloads = downloadKeys.filter(
          (key) => downloads[key].status === "downloading"
        );

        if (activeDownloads.length > 0) {
          const totalProgress = activeDownloads.reduce(
            (sum, key) => sum + (downloads[key].progress || 0),
            0
          );
          const avgProgress = Math.floor(
            totalProgress / activeDownloads.length
          );

          installation.status = "downloading";
          installation.progress = Math.min(avgProgress, 95);
          installation.currentStep = `Downloading models... (${activeDownloads.length} active)`;
        } else if (isInstalled) {
          installation.status = "completed";
          installation.progress = 100;
          installation.currentStep = "Installation completed successfully";

          this.stopBundlePolling();

          setTimeout(() => {
            this.removeBundleInstallation(installationId);
          }, 5000);
        } else {
          installation.status = "installing";
          installation.progress = Math.min(installation.progress + 1, 90);
          installation.currentStep = "Installing models and workflows...";
        }
      } catch (err: any) {
        installation.status = "error";
        installation.errors.push(err.response?.data?.detail || err.message);
        this.setError(
          `Installation failed for bundle "${installation.bundleName}": ${err.message}`
        );
        this.stopBundlePolling();
      }
    },

    /**
     * Stop bundle polling
     */
    stopBundlePolling(): void {
      if (this._bundlePollingInterval) {
        clearInterval(this._bundlePollingInterval);
        this._bundlePollingInterval = null;
      }
    },

    /**
     * Cancel bundle installation
     * @param {String} installationId - Installation ID to cancel
     */
    cancelBundleInstallation(installationId: string): void {
      const installation = this.bundleInstallations.get(installationId);
      if (installation) {
        installation.status = "cancelled";
        installation.currentStep = "Installation cancelled";

        setTimeout(() => {
          this.removeBundleInstallation(installationId);
        }, 2000);
      }
    },

    /**
     * Remove bundle installation
     * @param {String} installationId - Installation ID to remove
     */
    removeBundleInstallation(installationId: string): void {
      this.bundleInstallations.delete(installationId);

      if (this.bundleInstallations.size === 0) {
        this.stopBundlePolling();
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
     */
    async updateModelDownloadProgress(): Promise<void> {
      try {
        console.log("Polling /downloads...");
        const response = await api.get("/downloads");
        const downloads = response.data || {};

        console.log(
          "Current downloads from API:",
          Object.keys(downloads).length,
          "items"
        );

        // Update downloadProgress with fresh data
        this.downloadProgress = new Map(Object.entries(downloads));

        // Process each download detected by the API
        for (const [modelId, downloadInfo] of Object.entries(downloads) as [
          string,
          DownloadProgress
        ][]) {
          console.log(
            `Processing download ${modelId}:`,
            downloadInfo.status,
            downloadInfo.progress + "%"
          );

          // Handle active downloads
          if (
            downloadInfo.status === "downloading" ||
            (downloadInfo.progress < 100 && downloadInfo.status !== "stopped")
          ) {
            let found = false;
            for (const [
              downloadId,
              download,
            ] of this.modelDownloads.entries()) {
              if (download.modelId === modelId) {
                download.progress = downloadInfo.progress || 0;
                download.currentStep = `Downloading... ${download.progress}%`;
                download.status = "downloading";
                found = true;
                break;
              }
            }

            if (!found) {
              const downloadId = `${modelId}_detected_${Date.now()}`;

              let modelName = modelId;
              try {
                const modelsResponse = await api.get("/jsonmodels/");
                const allModels: Model[] = [];
                for (const [group, entries] of Object.entries(
                  modelsResponse.data.groups || {}
                )) {
                  (entries as any[]).forEach((model: any) => {
                    allModels.push({
                      ...model,
                      group,
                      id: `${group}_${model.url.split("/").pop()}`,
                    });
                  });
                }
                const model = allModels.find(
                  (m) => (m.dest || m.git) === modelId
                );
                if (model) {
                  modelName = model.name || model.id;
                }
              } catch (err) {
                console.warn("Could not fetch model name for", modelId);
              }

              this.modelDownloads.set(downloadId, {
                modelId,
                modelName,
                status: "downloading",
                progress: downloadInfo.progress || 0,
                currentStep: `Downloading... ${downloadInfo.progress || 0}%`,
                startTime: Date.now(),
                errors: [],
              });
            }
          }
          // Handle stopped downloads
          else if (downloadInfo.status === "stopped") {
            for (const [
              downloadId,
              download,
            ] of this.modelDownloads.entries()) {
              if (download.modelId === modelId) {
                download.status = "cancelled";
                download.currentStep = "Download stopped";

                setTimeout(() => {
                  this.removeModelDownload(downloadId);
                }, 2000);
                break;
              }
            }
          }
        }

        // Clean up completed downloads
        for (const [downloadId, download] of this.modelDownloads.entries()) {
          const apiDownload = downloads[download.modelId];

          if (!apiDownload) {
            if (download.status === "cancelled") {
              console.log(
                `Download ${download.modelId} already marked as cancelled`
              );
            } else {
              console.log(
                `Download ${download.modelId} completed, marking as finished`
              );
              download.status = "completed";
              download.progress = 100;
              download.currentStep = "Download completed successfully";

              setTimeout(() => {
                this.removeModelDownload(downloadId);
              }, 3000);
            }
          }
        }

        // Stop polling if no downloads
        if (
          Object.keys(downloads).length === 0 &&
          this.modelDownloads.size === 0
        ) {
          console.log("No downloads detected, attempting to stop polling");
          this.stopDownloadPolling();
        } else {
          console.log(
            "Continuing polling - downloads found:",
            Object.keys(downloads).length,
            "managed:",
            this.modelDownloads.size
          );
        }
      } catch (error: any) {
        console.error("Error updating model download progress:", error);
      }
    },

    /**
     * Cancel model download
     * @param {String} downloadId - Download ID or model ID to cancel
     */
    async cancelModelDownload(downloadId: string): Promise<void> {
      let download = this.modelDownloads.get(downloadId);
      let actualModelId = downloadId;

      if (download) {
        actualModelId = download.modelId;
      } else {
        for (const [id, dl] of this.modelDownloads.entries()) {
          if (dl.modelId === downloadId) {
            download = dl;
            downloadId = id;
            actualModelId = dl.modelId;
            break;
          }
        }
      }

      if (download) {
        try {
          await api.post("/models/stop_download", {
            model_id: actualModelId,
            dest: actualModelId,
            git: actualModelId,
          });

          download.status = "cancelled";
          download.currentStep = "Download cancelled";

          setTimeout(() => {
            this.removeModelDownload(downloadId);
          }, 2000);
        } catch (error: any) {
          console.error("Error cancelling download:", error);
          this.setError("Failed to cancel download");

          download.status = "cancelled";
          download.currentStep = "Download cancelled (forced)";

          setTimeout(() => {
            this.removeModelDownload(downloadId);
          }, 2000);
        }
      } else {
        console.warn("Download not found for cancellation:", downloadId);
      }
    },

    /**
     * Remove model download
     * @param {String} downloadId - Download ID to remove
     */
    removeModelDownload(downloadId: string): void {
      this.modelDownloads.delete(downloadId);

      if (this.modelDownloads.size === 0) {
        this.stopDownloadPolling();
      }
    },

    /**
     * Restore active downloads on startup
     */
    async restoreActiveDownloads(): Promise<void> {
      try {
        const response = await api.get("/downloads");
        const downloads = response.data || {};

        for (const [modelId, downloadInfo] of Object.entries(downloads) as [
          string,
          DownloadProgress
        ][]) {
          if (
            downloadInfo.status === "downloading" &&
            downloadInfo.progress < 100
          ) {
            const downloadId = `${modelId}_restored_${Date.now()}`;
            this.modelDownloads.set(downloadId, {
              modelId,
              modelName: modelId,
              status: "downloading",
              progress: downloadInfo.progress || 0,
              currentStep: `Downloading... ${downloadInfo.progress || 0}%`,
              startTime: Date.now(),
              errors: [],
            });
          }
        }

        if (this.modelDownloads.size > 0) {
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
    async refreshDownloads(): Promise<Record<string, DownloadProgress>> {
      try {
        const response = await api.get("/downloads");
        const downloads = response.data || {};

        this.downloadProgress = new Map(Object.entries(downloads));

        return downloads;
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
  BundleInstallation,
  ModelDownload,
  ActiveInstallation,
  ModelFilterCriteria,
  ModelEntry,
  ModelsState,
} from "./types/models.types";
