import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

/**
 * Store Pinia for managing models, bundles, installed bundles, and workflows
 * Handles all data operations for the ComfyUI application
 */
export const useDataStore = defineStore('data', () => {
  // === STATE ===
  
  // Models state
  const models = ref([])
  const modelsLoading = ref(false)
  const modelsError = ref(null)
  const selectedModels = ref([])
  
  // Bundles state
  const bundles = ref([])
  const bundlesLoading = ref(false)
  const bundlesError = ref(null)
  const selectedBundles = ref([])
  
  // Installed bundles state
  const installedBundles = ref([])
  const installedBundlesLoading = ref(false)
  const installedBundlesError = ref(null)
  
  // Workflows state
  const workflows = ref([])
  const workflowsLoading = ref(false)
  const workflowsError = ref(null)
  const selectedWorkflow = ref(null)
  const currentWorkflow = ref(null)
  
  // === COMPUTED ===
  
  /**
   * Get models grouped by type
   * @returns {Object} Models grouped by their type (clip, vae, unet, etc.)
   */
  const modelsByType = computed(() => {
    const grouped = {}
    models.value.forEach(model => {
      if (!grouped[model.type]) {
        grouped[model.type] = []
      }
      grouped[model.type].push(model)
    })
    return grouped
  })
  
  /**
   * Get models grouped by tags
   * @returns {Object} Models grouped by their tags
   */
  const modelsByTags = computed(() => {
    const grouped = {}
    models.value.forEach(model => {
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
  })
  
  /**
   * Get available model types
   * @returns {Array} List of unique model types
   */
  const availableModelTypes = computed(() => {
    return [...new Set(models.value.map(model => model.type))]
  })
  
  /**
   * Get available model tags
   * @returns {Array} List of unique model tags
   */
  const availableModelTags = computed(() => {
    const tags = new Set()
    models.value.forEach(model => {
      if (model.tags) {
        model.tags.forEach(tag => tags.add(tag))
      }
    })
    return [...tags]
  })
  
  /**
   * Get installed bundle IDs for quick lookup
   * @returns {Set} Set of installed bundle IDs
   */
  const installedBundleIds = computed(() => {
    return new Set(installedBundles.value.map(bundle => bundle.id))
  })
  
  /**
   * Check if any operation is loading
   * @returns {Boolean} True if any loading operation is in progress
   */
  const isLoading = computed(() => {
    return modelsLoading.value || bundlesLoading.value || 
           installedBundlesLoading.value || workflowsLoading.value
  })
  
  // === ACTIONS ===
  
  // === Models Actions ===
  
  /**
   * Fetch models from the API
   * @returns {Promise} Promise that resolves when models are loaded
   */
  async function fetchModels() {
    modelsLoading.value = true
    modelsError.value = null
    
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
      
      models.value = allModels
    } catch (error) {
      modelsError.value = error.message
      console.error('Error fetching models:', error)
    } finally {
      modelsLoading.value = false
    }
  }
  
  /**
   * Download a specific model
   * @param {Object} model - The model to download
   * @returns {Promise} Promise that resolves when download is complete
   */
  async function downloadModel(model) {
    try {
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
      
      return await response.json()
    } catch (error) {
      console.error('Error downloading model:', error)
      throw error
    }
  }
  
  /**
   * Toggle model selection
   * @param {Object} model - The model to toggle
   */
  function toggleModelSelection(model) {
    const index = selectedModels.value.findIndex(m => m.id === model.id)
    if (index > -1) {
      selectedModels.value.splice(index, 1)
    } else {
      selectedModels.value.push(model)
    }
  }
  
  /**
   * Clear all selected models
   */
  function clearSelectedModels() {
    selectedModels.value = []
  }
  
  // === Bundles Actions ===
  
  /**
   * Fetch available bundles from the API
   * @returns {Promise} Promise that resolves when bundles are loaded
   */
  async function fetchBundles() {
    bundlesLoading.value = true
    bundlesError.value = null
    
    try {
      const response = await fetch('/api/bundles')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      bundles.value = await response.json()
    } catch (error) {
      bundlesError.value = error.message
      console.error('Error fetching bundles:', error)
    } finally {
      bundlesLoading.value = false
    }
  }
  
  /**
   * Install a bundle
   * @param {Object} bundle - The bundle to install
   * @returns {Promise} Promise that resolves when installation is complete
   */
  async function installBundle(bundle) {
    try {
      const response = await fetch('/api/bundles/install', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ bundle })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Refresh installed bundles after successful installation
      await fetchInstalledBundles()
      
      return await response.json()
    } catch (error) {
      console.error('Error installing bundle:', error)
      throw error
    }
  }
  
  /**
   * Toggle bundle selection
   * @param {Object} bundle - The bundle to toggle
   */
  function toggleBundleSelection(bundle) {
    const index = selectedBundles.value.findIndex(b => b.id === bundle.id)
    if (index > -1) {
      selectedBundles.value.splice(index, 1)
    } else {
      selectedBundles.value.push(bundle)
    }
  }
  
  /**
   * Clear all selected bundles
   */
  function clearSelectedBundles() {
    selectedBundles.value = []
  }
  
  // === Installed Bundles Actions ===
  
  /**
   * Fetch installed bundles from the API
   * @returns {Promise} Promise that resolves when installed bundles are loaded
   */
  async function fetchInstalledBundles() {
    installedBundlesLoading.value = true
    installedBundlesError.value = null
    
    try {
      const response = await fetch('/api/bundles/installed')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      installedBundles.value = await response.json()
    } catch (error) {
      installedBundlesError.value = error.message
      console.error('Error fetching installed bundles:', error)
    } finally {
      installedBundlesLoading.value = false
    }
  }
  
  /**
   * Uninstall a bundle
   * @param {Object} bundle - The bundle to uninstall
   * @returns {Promise} Promise that resolves when uninstallation is complete
   */
  async function uninstallBundle(bundle) {
    try {
      const response = await fetch(`/api/bundles/uninstall/${bundle.id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Refresh installed bundles after successful uninstallation
      await fetchInstalledBundles()
      
      return await response.json()
    } catch (error) {
      console.error('Error uninstalling bundle:', error)
      throw error
    }
  }
  
  // === Workflows Actions ===
  
  /**
   * Fetch workflows from the API
   * @returns {Promise} Promise that resolves when workflows are loaded
   */
  async function fetchWorkflows() {
    workflowsLoading.value = true
    workflowsError.value = null
    
    try {
      const response = await fetch('/api/workflows')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      workflows.value = await response.json()
    } catch (error) {
      workflowsError.value = error.message
      console.error('Error fetching workflows:', error)
    } finally {
      workflowsLoading.value = false
    }
  }
  
  /**
   * Load a specific workflow
   * @param {Object} workflow - The workflow to load
   * @returns {Promise} Promise that resolves when workflow is loaded
   */
  async function loadWorkflow(workflow) {
    try {
      const response = await fetch(`/api/workflows/${workflow.id}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const workflowData = await response.json()
      currentWorkflow.value = workflowData
      selectedWorkflow.value = workflow
      return workflowData
    } catch (error) {
      console.error('Error loading workflow:', error)
      throw error
    }
  }
  
  /**
   * Save a workflow
   * @param {Object} workflowData - The workflow data to save
   * @param {String} name - The name for the workflow
   * @returns {Promise} Promise that resolves when workflow is saved
   */
  async function saveWorkflow(workflowData, name) {
    try {
      const response = await fetch('/api/workflows/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          workflow: workflowData, 
          name 
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Refresh workflows after successful save
      await fetchWorkflows()
      
      return await response.json()
    } catch (error) {
      console.error('Error saving workflow:', error)
      throw error
    }
  }
  
  /**
   * Delete a workflow
   * @param {Object} workflow - The workflow to delete
   * @returns {Promise} Promise that resolves when workflow is deleted
   */
  async function deleteWorkflow(workflow) {
    try {
      const response = await fetch(`/api/workflows/${workflow.id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Refresh workflows after successful deletion
      await fetchWorkflows()
      
      // Clear current workflow if it was the deleted one
      if (currentWorkflow.value && currentWorkflow.value.id === workflow.id) {
        currentWorkflow.value = null
        selectedWorkflow.value = null
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error deleting workflow:', error)
      throw error
    }
  }
  
  /**
   * Clear current workflow
   */
  function clearCurrentWorkflow() {
    currentWorkflow.value = null
    selectedWorkflow.value = null
  }
  
  // === Utility Actions ===
  
  /**
   * Initialize the store by fetching all data
   * @returns {Promise} Promise that resolves when all data is loaded
   */
  async function initializeStore() {
    try {
      await Promise.all([
        fetchModels(),
        fetchBundles(),
        fetchInstalledBundles(),
        fetchWorkflows()
      ])
    } catch (error) {
      console.error('Error initializing store:', error)
    }
  }
  
  /**
   * Refresh all data
   * @returns {Promise} Promise that resolves when all data is refreshed
   */
  async function refreshAllData() {
    return await initializeStore()
  }
  
  /**
   * Check if a bundle is installed
   * @param {Object} bundle - The bundle to check
   * @returns {Boolean} True if the bundle is installed
   */
  function isBundleInstalled(bundle) {
    return installedBundleIds.value.has(bundle.id)
  }
  
  /**
   * Get model by ID
   * @param {String} modelId - The model ID to find
   * @returns {Object|null} The model object or null if not found
   */
  function getModelById(modelId) {
    return models.value.find(model => model.id === modelId) || null
  }
  
  /**
   * Get workflow by ID
   * @param {String} workflowId - The workflow ID to find
   * @returns {Object|null} The workflow object or null if not found
   */
  function getWorkflowById(workflowId) {
    return workflows.value.find(workflow => workflow.id === workflowId) || null
  }
  
  // Return all state and actions
  return {
    // State
    models,
    modelsLoading,
    modelsError,
    selectedModels,
    bundles,
    bundlesLoading,
    bundlesError,
    selectedBundles,
    installedBundles,
    installedBundlesLoading,
    installedBundlesError,
    workflows,
    workflowsLoading,
    workflowsError,
    selectedWorkflow,
    currentWorkflow,
    
    // Computed
    modelsByType,
    modelsByTags,
    availableModelTypes,
    availableModelTags,
    installedBundleIds,
    isLoading,
    
    // Actions
    fetchModels,
    downloadModel,
    toggleModelSelection,
    clearSelectedModels,
    fetchBundles,
    installBundle,
    toggleBundleSelection,
    clearSelectedBundles,
    fetchInstalledBundles,
    uninstallBundle,
    fetchWorkflows,
    loadWorkflow,
    saveWorkflow,
    deleteWorkflow,
    clearCurrentWorkflow,
    initializeStore,
    refreshAllData,
    isBundleInstalled,
    getModelById,
    getWorkflowById
  }
})
