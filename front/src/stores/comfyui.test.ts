import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useComfyUIStore } from '@/stores/comfyui'
import type { GenerationParams } from '@/stores/types/comfyui.types'

// Mock the API service
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('ComfyUI Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useComfyUIStore()
      
      expect(store.models).toEqual({})
      expect(store.currentParams).toBeNull()
      expect(store.currentWorkflow).toBeNull()
      expect(store.isGenerating).toBe(false)
      expect(store.currentPromptId).toBeNull()
      expect(store.previewImage).toBeNull()
      expect(store.finalImages).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.serverStatus).toBeNull()
      expect(store.isServerAvailable).toBe(false)
    })
  })

  describe('Getters', () => {
    it('should return correct model options', () => {
      const store = useComfyUIStore()
      
      store.models = {
        'flux-dev': { model_type: 'flux', filename: 'flux1-dev-fp8.safetensors' },
        'sdxl': { model_type: 'checkpoint', filename: 'sd_xl_base_1.0.safetensors' }
      }
      
      const options = store.modelOptions
      expect(options).toHaveLength(2)
      expect(options[0]).toEqual({
        value: 'flux-dev',
        label: 'FLUX-DEV',
        type: 'flux'
      })
      expect(options[1]).toEqual({
        value: 'sdxl',
        label: 'SDXL',
        type: 'checkpoint'
      })
    })

    it('should return correct sampler options', () => {
      const store = useComfyUIStore()
      const samplers = store.samplerOptions
      
      expect(samplers).toContain({ value: 'euler', label: 'Euler' })
      expect(samplers).toContain({ value: 'dpmpp_2m', label: 'DPM++ 2M' })
      expect(samplers.length).toBeGreaterThan(5)
    })

    it('should calculate canGenerate correctly', () => {
      const store = useComfyUIStore()
      
      // Initially false
      expect(store.canGenerate).toBe(false)
      
      // Set server available
      store.isServerAvailable = true
      expect(store.canGenerate).toBe(false) // Still false because no currentParams
      
      // Set current params
      store.currentParams = {
        model_key: 'flux-dev',
        prompt: 'test prompt'
      } as GenerationParams
      expect(store.canGenerate).toBe(true)
      
      // Set generating
      store.isGenerating = true
      expect(store.canGenerate).toBe(false)
    })

    it('should return correct generation progress', () => {
      const store = useComfyUIStore()
      
      expect(store.generationProgress).toBe('Ready')
      
      store.isGenerating = true
      expect(store.generationProgress).toBe('Initializing...')
      
      store.previewImage = 'data:image/png;base64,test'
      expect(store.generationProgress).toBe('Generating...')
    })
  })

  describe('Actions', () => {
    it('should get default parameters correctly', () => {
      const store = useComfyUIStore()
      
      store.models = {
        'flux-dev': { model_type: 'flux', filename: 'flux1-dev-fp8.safetensors' }
      }
      
      const defaults = store.getDefaultParams()
      
      expect(defaults.model_key).toBe('flux-dev')
      expect(defaults.prompt).toBe('')
      expect(defaults.sampler).toBe('euler')
      expect(defaults.steps).toBe(30)
      expect(defaults.cfg).toBe(7.5)
      expect(defaults.width).toBe(1024)
      expect(defaults.height).toBe(1024)
      expect(defaults.enable_tea_cache).toBe(true)
    })

    it('should reset generation state', () => {
      const store = useComfyUIStore()
      
      // Set some state
      store.currentParams = {} as GenerationParams
      store.currentWorkflow = { test: 'workflow' }
      store.currentPromptId = 'test-123'
      store.previewImage = 'test-image'
      store.finalImages = ['image1', 'image2']
      store.isGenerating = true
      store.error = 'Test error'
      
      // Reset
      store.resetGeneration()
      
      // Verify reset
      expect(store.currentParams).toBeNull()
      expect(store.currentWorkflow).toBeNull()
      expect(store.currentPromptId).toBeNull()
      expect(store.previewImage).toBeNull()
      expect(store.finalImages).toEqual([])
      expect(store.isGenerating).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should set preview image', () => {
      const store = useComfyUIStore()
      const testImage = 'data:image/png;base64,test'
      
      store.setPreviewImage(testImage)
      expect(store.previewImage).toBe(testImage)
    })

    it('should set final images', () => {
      const store = useComfyUIStore()
      const testImages = ['image1.png', 'image2.png']
      
      store.setFinalImages(testImages)
      expect(store.finalImages).toEqual(testImages)
      expect(store.isGenerating).toBe(false)
    })

    it('should set and clear error', () => {
      const store = useComfyUIStore()
      const testError = 'Test error message'
      
      store.setError(testError)
      expect(store.error).toBe(testError)
      expect(store.isGenerating).toBe(false)
      
      store.clearError()
      expect(store.error).toBeNull()
    })
  })
})
