import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDataStore } from '../data.js'

// Mock fetch globally
global.fetch = vi.fn()

describe('Data Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Models Management', () => {
    it('should initialize with empty models array', () => {
      const store = useDataStore()
      expect(store.models).toEqual([])
      expect(store.modelsLoading).toBe(false)
      expect(store.modelsError).toBe(null)
    })

    it('should fetch models successfully', async () => {
      const mockModelsData = {
        groups: {
          'Flux DEV': [
            {
              url: 'https://example.com/model1.safetensors',
              dest: '/models/clip/model1.safetensors',
              type: 'clip',
              tags: ['base'],
              hash: 'abc123',
              size: 1000000
            }
          ]
        }
      }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockModelsData)
      })

      const store = useDataStore()
      await store.fetchModels()

      expect(store.models).toHaveLength(1)
      expect(store.models[0]).toMatchObject({
        url: 'https://example.com/model1.safetensors',
        type: 'clip',
        group: 'Flux DEV'
      })
      expect(store.modelsLoading).toBe(false)
      expect(store.modelsError).toBe(null)
    })

    it('should handle fetch models error', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'))

      const store = useDataStore()
      await store.fetchModels()

      expect(store.models).toEqual([])
      expect(store.modelsLoading).toBe(false)
      expect(store.modelsError).toBe('Network error')
    })

    it('should toggle model selection', () => {
      const store = useDataStore()
      const model = { id: 'model1', name: 'Test Model' }

      // Select model
      store.toggleModelSelection(model)
      expect(store.selectedModels).toContain(model)

      // Deselect model
      store.toggleModelSelection(model)
      expect(store.selectedModels).not.toContain(model)
    })

    it('should clear selected models', () => {
      const store = useDataStore()
      store.selectedModels = [{ id: 'model1' }, { id: 'model2' }]

      store.clearSelectedModels()
      expect(store.selectedModels).toEqual([])
    })
  })

  describe('Bundles Management', () => {
    it('should initialize with empty bundles arrays', () => {
      const store = useDataStore()
      expect(store.bundles).toEqual([])
      expect(store.installedBundles).toEqual([])
      expect(store.bundlesLoading).toBe(false)
      expect(store.installedBundlesLoading).toBe(false)
    })

    it('should fetch bundles successfully', async () => {
      const mockBundles = [
        { id: 'bundle1', name: 'Test Bundle', version: '1.0.0' }
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockBundles)
      })

      const store = useDataStore()
      await store.fetchBundles()

      expect(store.bundles).toEqual(mockBundles)
      expect(store.bundlesLoading).toBe(false)
      expect(store.bundlesError).toBe(null)
    })

    it('should install bundle successfully', async () => {
      const bundle = { id: 'bundle1', name: 'Test Bundle' }
      const mockResponse = { success: true, message: 'Bundle installed' }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      // Mock fetchInstalledBundles call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([bundle])
      })

      const store = useDataStore()
      const result = await store.installBundle(bundle)

      expect(fetch).toHaveBeenCalledWith('/api/bundles/install', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bundle })
      })
      expect(result).toEqual(mockResponse)
    })

    it('should check if bundle is installed', () => {
      const store = useDataStore()
      store.installedBundles = [{ id: 'bundle1' }, { id: 'bundle2' }]

      expect(store.isBundleInstalled({ id: 'bundle1' })).toBe(true)
      expect(store.isBundleInstalled({ id: 'bundle3' })).toBe(false)
    })
  })

  describe('Workflows Management', () => {
    it('should initialize with empty workflows', () => {
      const store = useDataStore()
      expect(store.workflows).toEqual([])
      expect(store.currentWorkflow).toBe(null)
      expect(store.selectedWorkflow).toBe(null)
    })

    it('should fetch workflows successfully', async () => {
      const mockWorkflows = [
        { id: 'workflow1', name: 'Test Workflow', nodes: [] }
      ]

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWorkflows)
      })

      const store = useDataStore()
      await store.fetchWorkflows()

      expect(store.workflows).toEqual(mockWorkflows)
      expect(store.workflowsLoading).toBe(false)
      expect(store.workflowsError).toBe(null)
    })

    it('should load workflow successfully', async () => {
      const workflow = { id: 'workflow1', name: 'Test Workflow' }
      const mockWorkflowData = { id: 'workflow1', nodes: [], links: [] }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWorkflowData)
      })

      const store = useDataStore()
      const result = await store.loadWorkflow(workflow)

      expect(store.currentWorkflow).toEqual(mockWorkflowData)
      expect(store.selectedWorkflow).toEqual(workflow)
      expect(result).toEqual(mockWorkflowData)
    })

    it('should save workflow successfully', async () => {
      const workflowData = { nodes: [], links: [] }
      const name = 'New Workflow'
      const mockResponse = { success: true, id: 'new-workflow-id' }

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      // Mock fetchWorkflows call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([])
      })

      const store = useDataStore()
      const result = await store.saveWorkflow(workflowData, name)

      expect(fetch).toHaveBeenCalledWith('/api/workflows/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow: workflowData, name })
      })
      expect(result).toEqual(mockResponse)
    })

    it('should clear current workflow', () => {
      const store = useDataStore()
      store.currentWorkflow = { id: 'workflow1' }
      store.selectedWorkflow = { id: 'workflow1' }

      store.clearCurrentWorkflow()

      expect(store.currentWorkflow).toBe(null)
      expect(store.selectedWorkflow).toBe(null)
    })
  })

  describe('Computed Properties', () => {
    it('should group models by type', () => {
      const store = useDataStore()
      store.models = [
        { id: '1', type: 'clip', name: 'Model 1' },
        { id: '2', type: 'vae', name: 'Model 2' },
        { id: '3', type: 'clip', name: 'Model 3' }
      ]

      const grouped = store.modelsByType
      expect(grouped.clip).toHaveLength(2)
      expect(grouped.vae).toHaveLength(1)
    })

    it('should group models by tags', () => {
      const store = useDataStore()
      store.models = [
        { id: '1', tags: ['base', 'flux'], name: 'Model 1' },
        { id: '2', tags: ['base'], name: 'Model 2' },
        { id: '3', tags: ['flux', 'advanced'], name: 'Model 3' }
      ]

      const grouped = store.modelsByTags
      expect(grouped.base).toHaveLength(2)
      expect(grouped.flux).toHaveLength(2)
      expect(grouped.advanced).toHaveLength(1)
    })

    it('should return available model types', () => {
      const store = useDataStore()
      store.models = [
        { type: 'clip' },
        { type: 'vae' },
        { type: 'clip' },
        { type: 'unet' }
      ]

      const types = store.availableModelTypes
      expect(types).toEqual(['clip', 'vae', 'unet'])
    })

    it('should check if any operation is loading', () => {
      const store = useDataStore()
      
      expect(store.isLoading).toBe(false)
      
      store.modelsLoading = true
      expect(store.isLoading).toBe(true)
      
      store.modelsLoading = false
      store.bundlesLoading = true
      expect(store.isLoading).toBe(true)
    })
  })

  describe('Utility Methods', () => {
    it('should get model by ID', () => {
      const store = useDataStore()
      const model1 = { id: 'model1', name: 'Model 1' }
      const model2 = { id: 'model2', name: 'Model 2' }
      store.models = [model1, model2]

      expect(store.getModelById('model1')).toEqual(model1)
      expect(store.getModelById('model3')).toBe(null)
    })

    it('should get workflow by ID', () => {
      const store = useDataStore()
      const workflow1 = { id: 'workflow1', name: 'Workflow 1' }
      const workflow2 = { id: 'workflow2', name: 'Workflow 2' }
      store.workflows = [workflow1, workflow2]

      expect(store.getWorkflowById('workflow1')).toEqual(workflow1)
      expect(store.getWorkflowById('workflow3')).toBe(null)
    })

    it('should initialize store successfully', async () => {
      // Mock all fetch calls
      const mockResponses = [
        { groups: {} }, // models
        [], // bundles
        [], // installed bundles
        []  // workflows
      ]

      mockResponses.forEach((response, index) => {
        fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response)
        })
      })

      const store = useDataStore()
      await store.initializeStore()

      expect(fetch).toHaveBeenCalledTimes(4)
      expect(fetch).toHaveBeenCalledWith('/api/models')
      expect(fetch).toHaveBeenCalledWith('/api/bundles')
      expect(fetch).toHaveBeenCalledWith('/api/bundles/installed')
      expect(fetch).toHaveBeenCalledWith('/api/workflows')
    })
  })
})
