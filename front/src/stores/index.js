/**
 * Centralized export file for all Pinia stores
 * This file exports all stores for easy importing throughout the application
 */

// Import all stores
export { useModelsStore } from './models.js'
export { useBundlesStore } from './bundles.js'
export { useWorkflowsStore } from './workflows.js'
export { useAuthStore } from './auth.js'
export { useUIStore } from './ui.js'

// Re-export Pinia for convenience
export { createPinia, setActivePinia } from 'pinia'

/**
 * Initialize all stores
 * Call this function to set up stores with their initial data
 * @returns {Promise} Promise that resolves when all stores are initialized
 */
export async function initializeStores() {
  try {
    // Get store instances
    const { useAuthStore } = await import('./auth.js')
    const { useModelsStore } = await import('./models.js')
    const { useBundlesStore } = await import('./bundles.js')
    const { useWorkflowsStore } = await import('./workflows.js')
    const { useUIStore } = await import('./ui.js')
    
    const authStore = useAuthStore()
    const modelsStore = useModelsStore()
    const bundlesStore = useBundlesStore()
    const workflowsStore = useWorkflowsStore()
    const uiStore = useUIStore()
    
    // Initialize UI first
    uiStore.initializeUI()
       
    // Initialize data stores if user is authenticated
    if (authStore.isAuthenticated) {
      await Promise.all([
        modelsStore.fetchModels(),
        bundlesStore.fetchBundles(),
        bundlesStore.fetchInstalledBundles(),
        workflowsStore.fetchWorkflows()
      ])
    }
    
    console.log('All stores initialized successfully')
  } catch (error) {
    console.error('Error initializing stores:', error)
  }
}

/**
 * Reset all stores to their initial state
 * Useful for logout or app reset scenarios
 */
export function resetAllStores() {
  const { useAuthStore } = require('./auth.js')
  const { useModelsStore } = require('./models.js')
  const { useBundlesStore } = require('./bundles.js')
  const { useWorkflowsStore } = require('./workflows.js')
  const { useUIStore } = require('./ui.js')
  
  const authStore = useAuthStore()
  const modelsStore = useModelsStore()
  const bundlesStore = useBundlesStore()
  const workflowsStore = useWorkflowsStore()
  const uiStore = useUIStore()
  
  // Logout user (this resets auth store)
  authStore.logout()
  
  // Clear all data stores
  modelsStore.clearModels()
  bundlesStore.clearBundles()
  workflowsStore.clearWorkflows()
  
  // Reset UI state
  uiStore.resetUIState()
  
  console.log('All stores reset successfully')
}
