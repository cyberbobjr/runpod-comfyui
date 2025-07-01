import { defineStore } from 'pinia'

/**
 * Store Pinia for managing AI models
 * Handles all operations related to AI models in the ComfyUI application
 */
export const useModelsStore = defineStore('models', {
  // === STATE ===
  state: () => ({
    models: [],
    loading: false,
    error: null,
    selectedModels: [],
    downloadProgress: {},
    installedModels: new Set()
  }),

  // === GETTERS ===
  getters: {
    /**
     * Get models grouped by type
     * @returns {Object} Models grouped by their type (clip, vae, unet, etc.)
     */
    modelsByType: (state) => {
      const grouped = {}
      state.models.forEach(model => {
        if (!grouped[model.type]) {
          grouped[model.type] = []
        }
        grouped[model.type].push(model)
      })
      return grouped
    },

    /**
     * Get models grouped by tags
     * @returns {Object} Models grouped by their tags
     */
    modelsByTags: (state) => {
      const grouped = {}
      state.models.forEach(model => {
        if (model.tags && model.tags.length > 0) {
          model.tags.forEach(tag => {
            if (!grouped[tag]) {
              grouped[tag] = []
            }
            grouped[tag].push(model)
          })
        }
      })
      return grouped
    },

    /**
     * Get available model types
     * @returns {Array} List of unique model types
     */
    availableModelTypes: (state) => {
      return [...new Set(state.models.map(model => model.type))]
    },

    /**
     * Get available model tags
     * @returns {Array} List of unique model tags
     */
    availableModelTags: (state) => {
      const tags = new Set()
      state.models.forEach(model => {
        if (model.tags) {
          model.tags.forEach(tag => tags.add(tag))
        }
      })
      return [...tags]
    },

    /**
     * Get models by group name
     * @returns {Function} Function that takes groupName and returns models
     */
    modelsByGroup: (state) => (groupName) => {
      return state.models.filter(model => model.group === groupName)
    },

    /**
     * Check if a model is selected
     * @returns {Function} Function that takes modelId and returns boolean
     */
    isModelSelected: (state) => (modelId) => {
      return state.selectedModels.some(model => model.id === modelId)
    },

    /**
     * Check if a model is installed
     * @returns {Function} Function that takes modelId and returns boolean
     */
    isModelInstalled: (state) => (modelId) => {
      return state.installedModels.has(modelId)
    },

    /**
     * Get download progress for a model
     * @returns {Function} Function that takes modelId and returns progress object
     */
    getDownloadProgress: (state) => (modelId) => {
      return state.downloadProgress[modelId] || null
    },

    /**
     * Get selected models count
     * @returns {Number} Number of selected models
     */
    selectedModelsCount: (state) => {
      return state.selectedModels.length
    },

    /**
     * Get total models count
     * @returns {Number} Total number of models
     */
    totalModelsCount: (state) => {
      return state.models.length
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Fetch models from the API
     * @returns {Promise} Promise that resolves when models are loaded
     */
    async fetchModels() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/models')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()

        // Parse models from the groups structure
        const allModels = []
        if (data.groups) {
          Object.keys(data.groups).forEach(groupName => {
            data.groups[groupName].forEach(model => {
              allModels.push({
                ...model,
                group: groupName,
                id: `${groupName}_${model.url.split('/').pop()}`
              })
            })
          })
        }

        this.models = allModels
      } catch (error) {
        this.error = error.message
        console.error('Error fetching models:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Download a specific model
     * @param {Object} model - The model to download
     * @returns {Promise} Promise that resolves when download is complete
     */
    async downloadModel(model) {
      try {
        // Initialize download progress
        this.downloadProgress[model.id] = {
          progress: 0,
          status: 'starting',
          error: null
        }

        const response = await fetch('/api/models/download', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ model })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()

        // Update download progress
        this.downloadProgress[model.id] = {
          progress: 100,
          status: 'completed',
          error: null
        }

        // Add to installed models
        this.installedModels.add(model.id)

        return result
      } catch (error) {
        // Update download progress with error
        this.downloadProgress[model.id] = {
          progress: 0,
          status: 'error',
          error: error.message
        }
        console.error('Error downloading model:', error)
        throw error
      }
    },

    /**
     * Update download progress for a model
     * @param {String} modelId - The model ID
     * @param {Number} progress - Progress percentage (0-100)
     * @param {String} status - Download status
     */
    updateDownloadProgress(modelId, progress, status = 'downloading') {
      this.downloadProgress[modelId] = {
        progress,
        status,
        error: null
      }
    },

    /**
     * Cancel model download
     * @param {String} modelId - The model ID to cancel
     */
    async cancelDownload(modelId) {
      try {
        const response = await fetch(`/api/models/download/${modelId}/cancel`, {
          method: 'POST'
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Remove download progress
        delete this.downloadProgress[modelId]
      } catch (error) {
        console.error('Error canceling download:', error)
        throw error
      }
    },

    /**
     * Toggle model selection
     * @param {Object} model - The model to toggle
     */
    toggleModelSelection(model) {
      const index = this.selectedModels.findIndex(m => m.id === model.id)
      if (index > -1) {
        this.selectedModels.splice(index, 1)
      } else {
        this.selectedModels.push(model)
      }
    },

    /**
     * Select multiple models
     * @param {Array} models - Array of models to select
     */
    selectModels(models) {
      models.forEach(model => {
        if (!this.isModelSelected(model.id)) {
          this.selectedModels.push(model)
        }
      })
    },

    /**
     * Deselect multiple models
     * @param {Array} models - Array of models to deselect
     */
    deselectModels(models) {
      models.forEach(model => {
        const index = this.selectedModels.findIndex(m => m.id === model.id)
        if (index > -1) {
          this.selectedModels.splice(index, 1)
        }
      })
    },

    /**
     * Select all models
     */
    selectAllModels() {
      this.selectedModels = [...this.models]
    },

    /**
     * Clear all selected models
     */
    clearSelectedModels() {
      this.selectedModels = []
    },

    /**
     * Select models by type
     * @param {String} type - Model type to select
     */
    selectModelsByType(type) {
      const modelsOfType = this.models.filter(model => model.type === type)
      this.selectModels(modelsOfType)
    },

    /**
     * Select models by tag
     * @param {String} tag - Model tag to select
     */
    selectModelsByTag(tag) {
      const modelsWithTag = this.models.filter(model => 
        model.tags && model.tags.includes(tag)
      )
      this.selectModels(modelsWithTag)
    },

    /**
     * Download selected models
     * @returns {Promise} Promise that resolves when all downloads are complete
     */
    async downloadSelectedModels() {
      const downloadPromises = this.selectedModels.map(model => 
        this.downloadModel(model)
      )
      
      try {
        await Promise.all(downloadPromises)
        this.clearSelectedModels()
      } catch (error) {
        console.error('Error downloading selected models:', error)
        throw error
      }
    },

    /**
     * Delete a model
     * @param {Object} model - The model to delete
     * @returns {Promise} Promise that resolves when model is deleted
     */
    async deleteModel(model) {
      try {
        const response = await fetch(`/api/models/${model.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Remove from installed models
        this.installedModels.delete(model.id)

        // Remove from selected models if selected
        this.deselectModels([model])

        return await response.json()
      } catch (error) {
        console.error('Error deleting model:', error)
        throw error
      }
    },

    /**
     * Get model by ID
     * @param {String} modelId - The model ID to find
     * @returns {Object|null} The model object or null if not found
     */
    getModelById(modelId) {
      return this.models.find(model => model.id === modelId) || null
    },

    /**
     * Search models by name or description
     * @param {String} query - Search query
     * @returns {Array} Array of matching models
     */
    searchModels(query) {
      if (!query) return this.models

      const lowercaseQuery = query.toLowerCase()
      return this.models.filter(model => 
        (model.name && model.name.toLowerCase().includes(lowercaseQuery)) ||
        (model.description && model.description.toLowerCase().includes(lowercaseQuery)) ||
        (model.tags && model.tags.some(tag => 
          tag.toLowerCase().includes(lowercaseQuery)
        ))
      )
    },

    /**
     * Filter models by criteria
     * @param {Object} criteria - Filter criteria
     * @returns {Array} Array of filtered models
     */
    filterModels(criteria) {
      let filteredModels = this.models

      if (criteria.type) {
        filteredModels = filteredModels.filter(model => model.type === criteria.type)
      }

      if (criteria.tags && criteria.tags.length > 0) {
        filteredModels = filteredModels.filter(model => 
          model.tags && criteria.tags.some(tag => model.tags.includes(tag))
        )
      }

      if (criteria.group) {
        filteredModels = filteredModels.filter(model => model.group === criteria.group)
      }

      if (criteria.installed !== undefined) {
        filteredModels = filteredModels.filter(model => 
          this.isModelInstalled(model.id) === criteria.installed
        )
      }

      return filteredModels
    },

    /**
     * Refresh models data
     * @returns {Promise} Promise that resolves when refresh is complete
     */
    async refreshModels() {
      return await this.fetchModels()
    },

    /**
     * Clear all models data
     */
    clearModels() {
      this.models = []
      this.selectedModels = []
      this.downloadProgress = {}
      this.error = null
    },

    /**
     * Set models error
     * @param {String} errorMessage - Error message to set
     */
    setError(errorMessage) {
      this.error = errorMessage
    },

    /**
     * Clear models error
     */
    clearError() {
      this.error = null
    }
  }
})
