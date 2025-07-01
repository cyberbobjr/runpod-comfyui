import { defineStore } from 'pinia'

/**
 * Store Pinia for managing workflows
 * Handles all operations related to ComfyUI workflows
 */
export const useWorkflowsStore = defineStore('workflows', {
  // === STATE ===
  state: () => ({
    workflows: [],
    currentWorkflow: null,
    selectedWorkflow: null,
    loading: false,
    error: null,
    executionHistory: [],
    executionStatus: {},
    workflowCategories: [],
    recentWorkflows: []
  }),

  // === GETTERS ===
  getters: {
    /**
     * Get workflows grouped by category
     * @returns {Object} Workflows grouped by their category
     */
    workflowsByCategory: (state) => {
      const grouped = {}
      state.workflows.forEach(workflow => {
        const category = workflow.category || 'Uncategorized'
        if (!grouped[category]) {
          grouped[category] = []
        }
        grouped[category].push(workflow)
      })
      return grouped
    },

    /**
     * Get available workflow categories
     * @returns {Array} List of unique workflow categories
     */
    availableCategories: (state) => {
      const categories = new Set()
      state.workflows.forEach(workflow => {
        categories.add(workflow.category || 'Uncategorized')
      })
      return [...categories]
    },

    /**
     * Check if a workflow is currently loaded
     * @returns {Function} Function that takes workflowId and returns boolean
     */
    isWorkflowLoaded: (state) => (workflowId) => {
      return state.currentWorkflow && state.currentWorkflow.id === workflowId
    },

    /**
     * Check if a workflow is currently selected
     * @returns {Function} Function that takes workflowId and returns boolean
     */
    isWorkflowSelected: (state) => (workflowId) => {
      return state.selectedWorkflow && state.selectedWorkflow.id === workflowId
    },

    /**
     * Get execution status for a workflow
     * @returns {Function} Function that takes workflowId and returns status object
     */
    getExecutionStatus: (state) => (workflowId) => {
      return state.executionStatus[workflowId] || null
    },

    /**
     * Get workflows by author
     * @returns {Function} Function that takes author and returns workflows
     */
    workflowsByAuthor: (state) => (author) => {
      return state.workflows.filter(workflow => workflow.author === author)
    },

    /**
     * Get favorite workflows
     * @returns {Array} Array of favorite workflows
     */
    favoriteWorkflows: (state) => {
      return state.workflows.filter(workflow => workflow.isFavorite)
    },

    /**
     * Get recently used workflows (last 10)
     * @returns {Array} Array of recently used workflows
     */
    getRecentWorkflows: (state) => {
      return state.recentWorkflows.slice(0, 10)
    },

    /**
     * Check if workflow has unsaved changes
     * @returns {Boolean} True if current workflow has unsaved changes
     */
    hasUnsavedChanges: (state) => {
      return state.currentWorkflow && state.currentWorkflow.hasUnsavedChanges
    },

    /**
     * Get total workflows count
     * @returns {Number} Total number of workflows
     */
    totalWorkflowsCount: (state) => {
      return state.workflows.length
    },

    /**
     * Get execution history count
     * @returns {Number} Number of executions in history
     */
    executionHistoryCount: (state) => {
      return state.executionHistory.length
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Fetch workflows from the API
     * @returns {Promise} Promise that resolves when workflows are loaded
     */
    async fetchWorkflows() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/workflows')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.workflows = await response.json()
      } catch (error) {
        this.error = error.message
        console.error('Error fetching workflows:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Load a specific workflow
     * @param {Object} workflow - The workflow to load
     * @returns {Promise} Promise that resolves when workflow is loaded
     */
    async loadWorkflow(workflow) {
      try {
        const response = await fetch(`/api/workflows/${workflow.id}`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const workflowData = await response.json()
        
        this.currentWorkflow = {
          ...workflowData,
          hasUnsavedChanges: false
        }
        this.selectedWorkflow = workflow

        // Add to recent workflows
        this.addToRecentWorkflows(workflow)

        return workflowData
      } catch (error) {
        console.error('Error loading workflow:', error)
        throw error
      }
    },

    /**
     * Save a workflow
     * @param {Object} workflowData - The workflow data to save
     * @param {String} name - The name for the workflow
     * @param {Object} options - Additional save options
     * @returns {Promise} Promise that resolves when workflow is saved
     */
    async saveWorkflow(workflowData, name, options = {}) {
      try {
        const response = await fetch('/api/workflows/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 
            workflow: workflowData, 
            name,
            ...options
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()

        // Update current workflow if it was saved
        if (this.currentWorkflow) {
          this.currentWorkflow.hasUnsavedChanges = false
          this.currentWorkflow.id = result.id
          this.currentWorkflow.name = name
        }

        // Refresh workflows after successful save
        await this.fetchWorkflows()

        return result
      } catch (error) {
        console.error('Error saving workflow:', error)
        throw error
      }
    },

    /**
     * Save current workflow
     * @param {String} name - The name for the workflow
     * @returns {Promise} Promise that resolves when workflow is saved
     */
    async saveCurrentWorkflow(name) {
      if (!this.currentWorkflow) {
        throw new Error('No workflow is currently loaded')
      }

      return await this.saveWorkflow(this.currentWorkflow, name)
    },

    /**
     * Update an existing workflow
     * @param {String} workflowId - ID of workflow to update
     * @param {Object} workflowData - Updated workflow data
     * @returns {Promise} Promise that resolves when workflow is updated
     */
    async updateWorkflow(workflowId, workflowData) {
      try {
        const response = await fetch(`/api/workflows/${workflowId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(workflowData)
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()

        // Update current workflow if it matches
        if (this.currentWorkflow && this.currentWorkflow.id === workflowId) {
          this.currentWorkflow = {
            ...this.currentWorkflow,
            ...workflowData,
            hasUnsavedChanges: false
          }
        }

        // Refresh workflows after successful update
        await this.fetchWorkflows()

        return result
      } catch (error) {
        console.error('Error updating workflow:', error)
        throw error
      }
    },

    /**
     * Delete a workflow
     * @param {Object} workflow - The workflow to delete
     * @returns {Promise} Promise that resolves when workflow is deleted
     */
    async deleteWorkflow(workflow) {
      try {
        const response = await fetch(`/api/workflows/${workflow.id}`, {
          method: 'DELETE'
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Clear current workflow if it was the deleted one
        if (this.currentWorkflow && this.currentWorkflow.id === workflow.id) {
          this.currentWorkflow = null
          this.selectedWorkflow = null
        }

        // Remove from recent workflows
        this.removeFromRecentWorkflows(workflow.id)

        // Refresh workflows after successful deletion
        await this.fetchWorkflows()

        return await response.json()
      } catch (error) {
        console.error('Error deleting workflow:', error)
        throw error
      }
    },

    /**
     * Duplicate a workflow
     * @param {Object} workflow - The workflow to duplicate
     * @param {String} newName - Name for the duplicated workflow
     * @returns {Promise} Promise that resolves when workflow is duplicated
     */
    async duplicateWorkflow(workflow, newName) {
      try {
        const response = await fetch(`/api/workflows/${workflow.id}/duplicate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: newName })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Refresh workflows after successful duplication
        await this.fetchWorkflows()

        return await response.json()
      } catch (error) {
        console.error('Error duplicating workflow:', error)
        throw error
      }
    },

    /**
     * Execute a workflow
     * @param {Object} workflow - The workflow to execute
     * @param {Object} inputs - Input parameters for execution
     * @returns {Promise} Promise that resolves when execution starts
     */
    async executeWorkflow(workflow, inputs = {}) {
      try {
        // Set execution status to running
        this.executionStatus[workflow.id] = {
          status: 'running',
          startTime: new Date().toISOString(),
          progress: 0,
          error: null
        }

        const response = await fetch('/api/workflows/execute', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 
            workflowId: workflow.id, 
            inputs 
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const result = await response.json()

        // Add to execution history
        this.executionHistory.unshift({
          id: result.executionId,
          workflowId: workflow.id,
          workflowName: workflow.name,
          startTime: new Date().toISOString(),
          status: 'running',
          inputs
        })

        return result
      } catch (error) {
        // Set execution status to error
        this.executionStatus[workflow.id] = {
          status: 'error',
          error: error.message,
          endTime: new Date().toISOString()
        }
        console.error('Error executing workflow:', error)
        throw error
      }
    },

    /**
     * Cancel workflow execution
     * @param {String} executionId - ID of execution to cancel
     * @returns {Promise} Promise that resolves when execution is cancelled
     */
    async cancelExecution(executionId) {
      try {
        const response = await fetch(`/api/workflows/execute/${executionId}/cancel`, {
          method: 'POST'
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Update execution status
        const execution = this.executionHistory.find(e => e.id === executionId)
        if (execution) {
          execution.status = 'cancelled'
          execution.endTime = new Date().toISOString()
        }

        return await response.json()
      } catch (error) {
        console.error('Error canceling execution:', error)
        throw error
      }
    },

    /**
     * Update execution status
     * @param {String} executionId - Execution ID
     * @param {Object} status - Status update object
     */
    updateExecutionStatus(executionId, status) {
      const execution = this.executionHistory.find(e => e.id === executionId)
      if (execution) {
        Object.assign(execution, status)
      }

      // Also update workflow execution status if available
      if (status.workflowId && this.executionStatus[status.workflowId]) {
        Object.assign(this.executionStatus[status.workflowId], status)
      }
    },

    /**
     * Mark workflow as favorite
     * @param {String} workflowId - ID of workflow to favorite
     */
    async toggleFavorite(workflowId) {
      try {
        const workflow = this.workflows.find(w => w.id === workflowId)
        if (!workflow) return

        const newFavoriteStatus = !workflow.isFavorite

        const response = await fetch(`/api/workflows/${workflowId}/favorite`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ isFavorite: newFavoriteStatus })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        // Update local state
        workflow.isFavorite = newFavoriteStatus
      } catch (error) {
        console.error('Error toggling favorite:', error)
        throw error
      }
    },

    /**
     * Add workflow to recent workflows
     * @param {Object} workflow - Workflow to add to recent
     */
    addToRecentWorkflows(workflow) {
      // Remove if already exists
      this.recentWorkflows = this.recentWorkflows.filter(w => w.id !== workflow.id)
      
      // Add to beginning
      this.recentWorkflows.unshift({
        ...workflow,
        lastUsed: new Date().toISOString()
      })

      // Keep only last 20
      this.recentWorkflows = this.recentWorkflows.slice(0, 20)
    },

    /**
     * Remove workflow from recent workflows
     * @param {String} workflowId - ID of workflow to remove
     */
    removeFromRecentWorkflows(workflowId) {
      this.recentWorkflows = this.recentWorkflows.filter(w => w.id !== workflowId)
    },

    /**
     * Clear current workflow
     */
    clearCurrentWorkflow() {
      this.currentWorkflow = null
      this.selectedWorkflow = null
    },

    /**
     * Mark current workflow as having unsaved changes
     */
    markAsModified() {
      if (this.currentWorkflow) {
        this.currentWorkflow.hasUnsavedChanges = true
      }
    },

    /**
     * Get workflow by ID
     * @param {String} workflowId - The workflow ID to find
     * @returns {Object|null} The workflow object or null if not found
     */
    getWorkflowById(workflowId) {
      return this.workflows.find(workflow => workflow.id === workflowId) || null
    },

    /**
     * Search workflows by name or description
     * @param {String} query - Search query
     * @returns {Array} Array of matching workflows
     */
    searchWorkflows(query) {
      if (!query) return this.workflows

      const lowercaseQuery = query.toLowerCase()
      return this.workflows.filter(workflow => 
        (workflow.name && workflow.name.toLowerCase().includes(lowercaseQuery)) ||
        (workflow.description && workflow.description.toLowerCase().includes(lowercaseQuery)) ||
        (workflow.author && workflow.author.toLowerCase().includes(lowercaseQuery))
      )
    },

    /**
     * Filter workflows by criteria
     * @param {Object} criteria - Filter criteria
     * @returns {Array} Array of filtered workflows
     */
    filterWorkflows(criteria) {
      let filteredWorkflows = this.workflows

      if (criteria.category) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
          (workflow.category || 'Uncategorized') === criteria.category
        )
      }

      if (criteria.author) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
          workflow.author === criteria.author
        )
      }

      if (criteria.favorite) {
        filteredWorkflows = filteredWorkflows.filter(workflow => 
          workflow.isFavorite
        )
      }

      return filteredWorkflows
    },

    /**
     * Refresh workflows data
     * @returns {Promise} Promise that resolves when refresh is complete
     */
    async refreshWorkflows() {
      return await this.fetchWorkflows()
    },

    /**
     * Clear all workflows data
     */
    clearWorkflows() {
      this.workflows = []
      this.currentWorkflow = null
      this.selectedWorkflow = null
      this.executionHistory = []
      this.executionStatus = {}
      this.recentWorkflows = []
      this.error = null
    },

    /**
     * Set workflows error
     * @param {String} errorMessage - Error message to set
     */
    setError(errorMessage) {
      this.error = errorMessage
    },

    /**
     * Clear workflows error
     */
    clearError() {
      this.error = null
    }
  }
})
