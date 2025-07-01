import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useModelsStore } from '../models.js'

// Mock fetch globally
global.fetch = vi.fn()

describe('Models Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty models array', () => {
      const store = useModelsStore()
      expect(store.models).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.selectedModels).toEqual([])
    })
  })

  describe('Getters', () => {
    it('should group models by type', () => {
      const store = useModelsStore()
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
      const store = useModelsStore()
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
      const store = useModelsStore()
      store.models = [
        { type: 'clip' },
        { type: 'vae' },
        { type: 'clip' },
        { type: 'unet' }
      ]

      const types = store.availableModelTypes
      expect(types).toEqual(['clip', 'vae', 'unet'])
    })

    it('should check if model is selected', () => {
      const store = useModelsStore()
      const model = { id: 'model1', name: 'Test Model' }
      store.selectedModels = [model]

      expect(store.isModelSelected('model1')).toBe(true)
      expect(store.isModelSelected('model2')).toBe(false)
    })
  })

  describe('Actions', () => {
    describe('fetchModels', () => {
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

        const store = useModelsStore()
        await store.fetchModels()

        expect(store.models).toHaveLength(1)
        expect(store.models[0]).toMatchObject({
          url: 'https://example.com/model1.safetensors',
          type: 'clip',
          group: 'Flux DEV'
        })
        expect(store.loading).toBe(false)
        expect(store.error).toBe(null)
      })

      it('should handle fetch models error', async () => {
        fetch.mockRejectedValueOnce(new Error('Network error'))

        const store = useModelsStore()
        
        await expect(store.fetchModels()).rejects.toThrow('Network error')
        expect(store.models).toEqual([])
        expect(store.loading).toBe(false)
        expect(store.error).toBe('Network error')
      })
    })

    describe('downloadModel', () => {
      it('should download model successfully', async () => {
        const model = { id: 'model1', name: 'Test Model' }
        const mockResponse = { success: true, message: 'Model downloaded' }

        fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })

        const store = useModelsStore()
        const result = await store.downloadModel(model)

        expect(fetch).toHaveBeenCalledWith('/api/models/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model })
        })
        expect(result).toEqual(mockResponse)
        expect(store.installedModels.has('model1')).toBe(true)
      })

      it('should handle download error', async () => {
        const model = { id: 'model1', name: 'Test Model' }
        fetch.mockRejectedValueOnce(new Error('Download failed'))

        const store = useModelsStore()
        
        await expect(store.downloadModel(model)).rejects.toThrow('Download failed')
        expect(store.downloadProgress['model1']).toMatchObject({
          status: 'error',
          error: 'Download failed'
        })
      })
    })

    describe('Model Selection', () => {
      it('should toggle model selection', () => {
        const store = useModelsStore()
        const model = { id: 'model1', name: 'Test Model' }

        // Select model
        store.toggleModelSelection(model)
        expect(store.selectedModels).toContain(model)

        // Deselect model
        store.toggleModelSelection(model)
        expect(store.selectedModels).not.toContain(model)
      })

      it('should select multiple models', () => {
        const store = useModelsStore()
        const models = [
          { id: 'model1', name: 'Model 1' },
          { id: 'model2', name: 'Model 2' }
        ]

        store.selectModels(models)
        expect(store.selectedModels).toHaveLength(2)
        expect(store.selectedModels).toEqual(models)
      })

      it('should clear selected models', () => {
        const store = useModelsStore()
        store.selectedModels = [
          { id: 'model1' }, 
          { id: 'model2' }
        ]

        store.clearSelectedModels()
        expect(store.selectedModels).toEqual([])
      })

      it('should select all models', () => {
        const store = useModelsStore()
        store.models = [
          { id: 'model1' },
          { id: 'model2' },
          { id: 'model3' }
        ]

        store.selectAllModels()
        expect(store.selectedModels).toHaveLength(3)
        expect(store.selectedModels).toEqual(store.models)
      })
    })

    describe('Model Utilities', () => {
      it('should get model by ID', () => {
        const store = useModelsStore()
        const model1 = { id: 'model1', name: 'Model 1' }
        const model2 = { id: 'model2', name: 'Model 2' }
        store.models = [model1, model2]

        expect(store.getModelById('model1')).toEqual(model1)
        expect(store.getModelById('model3')).toBe(null)
      })

      it('should search models', () => {
        const store = useModelsStore()
        store.models = [
          { id: '1', name: 'Flux Model', description: 'AI model' },
          { id: '2', name: 'Stable Diffusion', description: 'Image generation' },
          { id: '3', name: 'CLIP', tags: ['flux', 'text'] }
        ]

        const results = store.searchModels('flux')
        expect(results).toHaveLength(2)
        expect(results.map(m => m.id)).toEqual(['1', '3'])
      })

      it('should filter models by criteria', () => {
        const store = useModelsStore()
        store.models = [
          { id: '1', type: 'clip', tags: ['base'] },
          { id: '2', type: 'vae', tags: ['base'] },
          { id: '3', type: 'clip', tags: ['advanced'] }
        ]

        const clipModels = store.filterModels({ type: 'clip' })
        expect(clipModels).toHaveLength(2)

        const baseModels = store.filterModels({ tags: ['base'] })
        expect(baseModels).toHaveLength(2)
      })
    })

    describe('Download Management', () => {
      it('should update download progress', () => {
        const store = useModelsStore()
        
        store.updateDownloadProgress('model1', 50, 'downloading')
        
        expect(store.downloadProgress['model1']).toMatchObject({
          progress: 50,
          status: 'downloading',
          error: null
        })
      })

      it('should cancel download', async () => {
        const mockResponse = { success: true }
        fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })

        const store = useModelsStore()
        store.downloadProgress['model1'] = { progress: 50 }
        
        await store.cancelDownload('model1')
        
        expect(fetch).toHaveBeenCalledWith('/api/models/download/model1/cancel', {
          method: 'POST'
        })
        expect(store.downloadProgress['model1']).toBeUndefined()
      })
    })
  })
})
