import { defineStore } from 'pinia'
import api from '../services/api' // Assuming you have an api.js file for API requests

/**
 * Store Pinia for managing bundles and installed bundles
 * Handles all operations related to bundles in the ComfyUI application
 */
export const useBundlesStore = defineStore('bundles', {
  // === STATE ===
  state: () => ({
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
     * Get bundles grouped by category
     * @returns {Object} Bundles grouped by their category
     */
    bundlesByCategory: (state) => {
      const grouped = {}
      state.bundles.forEach(bundle => {
        const category = bundle.category || 'Uncategorized'
        if (!grouped[category]) {
          grouped[category] = []
        }
        grouped[category].push(bundle)
      })
      return grouped
    },

    /**
     * Get available bundle categories
     * @returns {Array} List of unique bundle categories
     */
    availableCategories: (state) => {
      const categories = new Set()
      state.bundles.forEach(bundle => {
        categories.add(bundle.category || 'Uncategorized')
      })
      return [...categories]
    },

    /**
     * Get installed bundle IDs for quick lookup
     * @returns {Set} Set of installed bundle IDs
     */
    installedBundleIds: (state) => {
      return new Set(state.installedBundles.map(bundle => bundle.id))
    },

    /**
     * Check if a bundle is installed
     * @returns {Function} Function that takes bundleId and returns boolean
     */
    isBundleInstalled: (state) => (bundleId) => {
      return state.installedBundles.some(bundle => bundle.id === bundleId)
    },

    /**
     * Check if a bundle is selected
     * @returns {Function} Function that takes bundleId and returns boolean
     */
    isBundleSelected: (state) => (bundleId) => {
      return state.selectedBundles.some(bundle => bundle.id === bundleId)
    },

    /**
     * Get install progress for a bundle
     * @returns {Function} Function that takes bundleId and returns progress object
     */
    getInstallProgress: (state) => (bundleId) => {
      return state.installProgress[bundleId] || null
    },

    /**
     * Get bundles that can be updated
     * @returns {Array} Array of bundles with available updates
     */
    updatableBundles: (state) => {
      return state.installedBundles.filter(installedBundle => {
        const availableBundle = state.bundles.find(b => b.id === installedBundle.id)
        return availableBundle && availableBundle.version !== installedBundle.version
      })
    },

    /**
     * Get selected bundles count
     * @returns {Number} Number of selected bundles
     */
    selectedBundlesCount: (state) => {
      return state.selectedBundles.length
    },

    /**
     * Get total bundles count
     * @returns {Number} Total number of available bundles
     */
    totalBundlesCount: (state) => {
      return state.bundles.length
    },

    /**
     * Get installed bundles count
     * @returns {Number} Number of installed bundles
     */
    installedBundlesCount: (state) => {
      return state.installedBundles.length
    },

    /**
     * Check if any loading operation is in progress
     * @returns {Boolean} True if any loading operation is active
     */
    isLoading: (state) => {
      return state.loading || state.installedLoading
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Delete a bundle by ID
     * @param {String} bundleId - The ID of the bundle to delete
     * @returns {Promise} Promise that resolves when deletion is complete
     */
    async deleteBundle(bundleId) {
      try {
        await api.delete(`/bundles/${bundleId}`)

        // Refresh bundles list after deletion
        await this.fetchBundles()
      } catch (error) {
        console.error('Error deleting bundle:', error)
        throw error
      }
    },
    /**
     * Fetch available bundles from the API
     * @returns {Promise} Promise that resolves when bundles are loaded
     */
    async fetchBundles() {
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/bundles/')
        this.bundles = response.data
      } catch (error) {
        this.error = error.message
        console.error('Error fetching bundles:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch installed bundles from the API
     * @returns {Promise} Promise that resolves when installed bundles are loaded
     */
    async fetchInstalledBundles() {
      this.installedLoading = true
      this.installedError = null

      try {
        const response = await api.get('/bundles/installed')
        this.installedBundles = response.data
      } catch (error) {
        this.installedError = error.message
        console.error('Error fetching installed bundles:', error)
        throw error
      } finally {
        this.installedLoading = false
      }
    },

    /**
     * Install a bundle
     * @param {Object} bundle - The bundle to install
     * @returns {Promise} Promise that resolves when installation is complete
     */
    async installBundle(bundle) {
      try {
        // Initialize install progress
        this.installProgress[bundle.id] = {
          progress: 0,
          status: 'starting',
          error: null
        }

        const response = await api.post('/bundles/install', { bundle })

        // Update install progress
        this.installProgress[bundle.id] = {
          progress: 100,
          status: 'completed',
          error: null
        }

        // Refresh installed bundles after successful installation
        await this.fetchInstalledBundles()

        return response.data
      } catch (error) {
        // Update install progress with error
        this.installProgress[bundle.id] = {
          progress: 0,
          status: 'error',
          error: error.message
        }
        console.error('Error installing bundle:', error)
        throw error
      }
    },

    /**
     * Uninstall a bundle
     * @param {Object} bundle - The bundle to uninstall
     * @returns {Promise} Promise that resolves when uninstallation is complete
     */
    async uninstallBundle(bundle) {
      try {
        const response = await api.delete(`/bundles/uninstall/${bundle.id}`)

        // Refresh installed bundles after successful uninstallation
        await this.fetchInstalledBundles()

        // Remove from selected bundles if selected
        this.deselectBundles([bundle])

        return response.data
      } catch (error) {
        console.error('Error uninstalling bundle:', error)
        throw error
      }
    },

    /**
     * Update install progress for a bundle
     * @param {String} bundleId - The bundle ID
     * @param {Number} progress - Progress percentage (0-100)
     * @param {String} status - Installation status
     */
    updateInstallProgress(bundleId, progress, status = 'installing') {
      this.installProgress[bundleId] = {
        progress,
        status,
        error: null
      }
    },

    /**
     * Cancel bundle installation
     * @param {String} bundleId - The bundle ID to cancel
     */
    async cancelInstallation(bundleId) {
      try {
        await api.post(`/bundles/install/${bundleId}/cancel`)

        // Remove install progress
        delete this.installProgress[bundleId]
      } catch (error) {
        console.error('Error canceling installation:', error)
        throw error
      }
    },


    /**
     * Create a new bundle
     * @param {Object} bundleData - The data for the new bundle
     * @returns {Promise} Promise that resolves with the created bundle
     */
    async createBundle(bundleData) {
      try {
        const response = await api.post('/bundles/', bundleData)
        // Refresh bundles list after creation
        await this.fetchBundles()
        return response.data
      } catch (error) {
        console.error('Error creating bundle:', error)
        throw error
      }
    },

    /**
     * Update a bundle
     * @param {Object} bundle - The bundle to update (must include id)
     * @returns {Promise} Promise that resolves with the updated bundle
     */
    async updateBundle(bundleId, bundleData) {
      try {
        const response = await api.put(`/bundles/${bundleId}`, bundleData)
        return response.data
      } catch (error) {
        console.error('Error updating bundle:', error)
        throw error
      }
    },

    /**
     * Toggle bundle selection
     * @param {Object} bundle - The bundle to toggle
     */
    toggleBundleSelection(bundle) {
      const index = this.selectedBundles.findIndex(b => b.id === bundle.id)
      if (index > -1) {
        this.selectedBundles.splice(index, 1)
      } else {
        this.selectedBundles.push(bundle)
      }
    },

    /**
     * Select multiple bundles
     * @param {Array} bundles - Array of bundles to select
     */
    selectBundles(bundles) {
      bundles.forEach(bundle => {
        if (!this.isBundleSelected(bundle.id)) {
          this.selectedBundles.push(bundle)
        }
      })
    },

    /**
     * Deselect multiple bundles
     * @param {Array} bundles - Array of bundles to deselect
     */
    deselectBundles(bundles) {
      bundles.forEach(bundle => {
        const index = this.selectedBundles.findIndex(b => b.id === bundle.id)
        if (index > -1) {
          this.selectedBundles.splice(index, 1)
        }
      })
    },

    /**
     * Select all bundles
     */
    selectAllBundles() {
      this.selectedBundles = [...this.bundles]
    },

    /**
     * Clear all selected bundles
     */
    clearSelectedBundles() {
      this.selectedBundles = []
    },

    /**
     * Select bundles by category
     * @param {String} category - Bundle category to select
     */
    selectBundlesByCategory(category) {
      const bundlesInCategory = this.bundles.filter(bundle => 
        (bundle.category || 'Uncategorized') === category
      )
      this.selectBundles(bundlesInCategory)
    },

    /**
     * Install selected bundles
     * @returns {Promise} Promise that resolves when all installations are complete
     */
    async installSelectedBundles() {
      const installPromises = this.selectedBundles.map(bundle => 
        this.installBundle(bundle)
      )
      
      try {
        await Promise.all(installPromises)
        this.clearSelectedBundles()
      } catch (error) {
        console.error('Error installing selected bundles:', error)
        throw error
      }
    },

    /**
     * Update all updatable bundles
     * @returns {Promise} Promise that resolves when all updates are complete
     */
    async updateAllBundles() {
      const updatePromises = this.updatableBundles.map(bundle => 
        this.updateBundle(bundle)
      )
      
      try {
        await Promise.all(updatePromises)
      } catch (error) {
        console.error('Error updating bundles:', error)
        throw error
      }
    },

    /**
     * Get bundle by ID
     * @param {String} bundleId - The bundle ID to find
     * @returns {Object|null} The bundle object or null if not found
     */
    getBundleById(bundleId) {
      return this.bundles.find(bundle => bundle.id === bundleId) || null
    },

    /**
     * Get installed bundle by ID
     * @param {String} bundleId - The bundle ID to find
     * @returns {Object|null} The installed bundle object or null if not found
     */
    getInstalledBundleById(bundleId) {
      return this.installedBundles.find(bundle => bundle.id === bundleId) || null
    },

    /**
     * Search bundles by name or description
     * @param {String} query - Search query
     * @returns {Array} Array of matching bundles
     */
    searchBundles(query) {
      if (!query) return this.bundles

      const lowercaseQuery = query.toLowerCase()
      return this.bundles.filter(bundle => 
        (bundle.name && bundle.name.toLowerCase().includes(lowercaseQuery)) ||
        (bundle.description && bundle.description.toLowerCase().includes(lowercaseQuery)) ||
        (bundle.author && bundle.author.toLowerCase().includes(lowercaseQuery))
      )
    },

    /**
     * Filter bundles by criteria
     * @param {Object} criteria - Filter criteria
     * @returns {Array} Array of filtered bundles
     */
    filterBundles(criteria) {
      let filteredBundles = this.bundles

      if (criteria.category) {
        filteredBundles = filteredBundles.filter(bundle => 
          (bundle.category || 'Uncategorized') === criteria.category
        )
      }

      if (criteria.installed !== undefined) {
        filteredBundles = filteredBundles.filter(bundle => 
          this.isBundleInstalled(bundle.id) === criteria.installed
        )
      }

      if (criteria.updatable) {
        const updatableIds = new Set(this.updatableBundles.map(b => b.id))
        filteredBundles = filteredBundles.filter(bundle => 
          updatableIds.has(bundle.id)
        )
      }

      return filteredBundles
    },

    /**
     * Refresh bundles data
     * @returns {Promise} Promise that resolves when refresh is complete
     */
    async refreshBundles() {
      await Promise.all([
        this.fetchBundles(),
        this.fetchInstalledBundles()
      ])
    },

    /**
     * Clear all bundles data
     */
    clearBundles() {
      this.bundles = []
      this.installedBundles = []
      this.selectedBundles = []
      this.installProgress = {}
      this.error = null
      this.installedError = null
    },

    /**
     * Set bundles error
     * @param {String} errorMessage - Error message to set
     */
    setError(errorMessage) {
      this.error = errorMessage
    },

    /**
     * Set installed bundles error
     * @param {String} errorMessage - Error message to set
     */
    setInstalledError(errorMessage) {
      this.installedError = errorMessage
    },

    /**
     * Clear bundles errors
     */
    clearErrors() {
      this.error = null
      this.installedError = null
    }
  }
})
