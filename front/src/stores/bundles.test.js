import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBundlesStore } from '../bundles.js'

// Mock the API service
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}))

import api from '../../services/api'

describe('Bundles Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty bundles arrays', () => {
      const store = useBundlesStore()
      expect(store.bundles).toEqual([])
      expect(store.installedBundles).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.installedLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.installedError).toBe(null)
    })
  })

  describe('Getters', () => {
    it('should group bundles by category', () => {
      const store = useBundlesStore()
      store.bundles = [
        { id: '1', name: 'Bundle 1', category: 'Models' },
        { id: '2', name: 'Bundle 2', category: 'Workflows' },
        { id: '3', name: 'Bundle 3', category: 'Models' },
        { id: '4', name: 'Bundle 4' } // No category
      ]

      const grouped = store.bundlesByCategory
      expect(grouped.Models).toHaveLength(2)
      expect(grouped.Workflows).toHaveLength(1)
      expect(grouped.Uncategorized).toHaveLength(1)
    })

    it('should return available categories', () => {
      const store = useBundlesStore()
      store.bundles = [
        { category: 'Models' },
        { category: 'Workflows' },
        { category: 'Models' },
        {} // No category
      ]

      const categories = store.availableCategories
      expect(categories).toEqual(['Models', 'Workflows', 'Uncategorized'])
    })

    it('should check if bundle is installed', () => {
      const store = useBundlesStore()
      store.installedBundles = [
        { id: 'bundle1' },
        { id: 'bundle2' }
      ]

      expect(store.isBundleInstalled('bundle1')).toBe(true)
      expect(store.isBundleInstalled('bundle3')).toBe(false)
    })

    it('should return updatable bundles', () => {
      const store = useBundlesStore()
      store.bundles = [
        { id: 'bundle1', version: '2.0.0' },
        { id: 'bundle2', version: '1.5.0' },
        { id: 'bundle3', version: '1.0.0' }
      ]
      store.installedBundles = [
        { id: 'bundle1', version: '1.0.0' }, // Can be updated
        { id: 'bundle2', version: '1.5.0' }, // Same version
        { id: 'bundle4', version: '1.0.0' }  // Not in available bundles
      ]

      const updatable = store.updatableBundles
      expect(updatable).toHaveLength(1)
      expect(updatable[0].id).toBe('bundle1')
    })
  })

  describe('Actions', () => {
    describe('fetchBundles', () => {
      it('should fetch bundles successfully', async () => {
        const mockBundles = [
          { id: 'bundle1', name: 'Test Bundle', version: '1.0.0' }
        ]

        api.get.mockResolvedValueOnce({
          data: mockBundles
        })

        const store = useBundlesStore()
        await store.fetchBundles()

        expect(store.bundles).toEqual(mockBundles)
        expect(store.loading).toBe(false)
        expect(store.error).toBe(null)
      })

      it('should handle fetch bundles error', async () => {
        api.get.mockRejectedValueOnce(new Error('Network error'))

        const store = useBundlesStore()
        
        await expect(store.fetchBundles()).rejects.toThrow('Network error')
        expect(store.bundles).toEqual([])
        expect(store.loading).toBe(false)
        expect(store.error).toBe('Network error')
      })
    })

    describe('fetchInstalledBundles', () => {
      it('should fetch installed bundles successfully', async () => {
        const mockInstalledBundles = [
          { id: 'bundle1', name: 'Installed Bundle', version: '1.0.0' }
        ]

        api.get.mockResolvedValueOnce({
          data: mockInstalledBundles
        })

        const store = useBundlesStore()
        await store.fetchInstalledBundles()

        expect(store.installedBundles).toEqual(mockInstalledBundles)
        expect(store.installedLoading).toBe(false)
        expect(store.installedError).toBe(null)
      })
    })

    describe('installBundle', () => {
      it('should install bundle successfully', async () => {
        const bundle = { id: 'bundle1', name: 'Test Bundle' }
        const mockResponse = { success: true, message: 'Bundle installed' }

        // Mock install response
        api.post.mockResolvedValueOnce({
          data: mockResponse
        })

        // Mock fetchInstalledBundles call
        api.get.mockResolvedValueOnce({
          data: [bundle]
        })

        const store = useBundlesStore()
        const result = await store.installBundle(bundle)

        expect(api.post).toHaveBeenCalledWith('/bundles/install', { bundle })
        expect(result).toEqual(mockResponse)
        expect(store.installProgress['bundle1']).toMatchObject({
          status: 'completed',
          progress: 100
        })
      })

      it('should handle install error', async () => {
        const bundle = { id: 'bundle1', name: 'Test Bundle' }
        api.post.mockRejectedValueOnce(new Error('Install failed'))

        const store = useBundlesStore()
        
        await expect(store.installBundle(bundle)).rejects.toThrow('Install failed')
        expect(store.installProgress['bundle1']).toMatchObject({
          status: 'error',
          error: 'Install failed'
        })
      })
    })

    describe('uninstallBundle', () => {
      it('should uninstall bundle successfully', async () => {
        const bundle = { id: 'bundle1', name: 'Test Bundle' }
        const mockResponse = { success: true }

        api.delete.mockResolvedValueOnce({
          data: mockResponse
        })

        // Mock fetchInstalledBundles call
        api.get.mockResolvedValueOnce({
          data: []
        })

        const store = useBundlesStore()
        store.selectedBundles = [bundle]
        
        const result = await store.uninstallBundle(bundle)

        expect(api.delete).toHaveBeenCalledWith('/bundles/uninstall/bundle1')
        expect(result).toEqual(mockResponse)
        expect(store.selectedBundles).not.toContain(bundle)
      })
    })

    describe('Bundle Selection', () => {
      it('should toggle bundle selection', () => {
        const store = useBundlesStore()
        const bundle = { id: 'bundle1', name: 'Test Bundle' }

        // Select bundle
        store.toggleBundleSelection(bundle)
        expect(store.selectedBundles).toContain(bundle)

        // Deselect bundle
        store.toggleBundleSelection(bundle)
        expect(store.selectedBundles).not.toContain(bundle)
      })

      it('should select bundles by category', () => {
        const store = useBundlesStore()
        store.bundles = [
          { id: '1', category: 'Models' },
          { id: '2', category: 'Workflows' },
          { id: '3', category: 'Models' }
        ]

        store.selectBundlesByCategory('Models')
        expect(store.selectedBundles).toHaveLength(2)
        expect(store.selectedBundles.map(b => b.id)).toEqual(['1', '3'])
      })

      it('should clear selected bundles', () => {
        const store = useBundlesStore()
        store.selectedBundles = [
          { id: 'bundle1' },
          { id: 'bundle2' }
        ]

        store.clearSelectedBundles()
        expect(store.selectedBundles).toEqual([])
      })
    })

    describe('Bundle Utilities', () => {
      it('should get bundle by ID', () => {
        const store = useBundlesStore()
        const bundle1 = { id: 'bundle1', name: 'Bundle 1' }
        const bundle2 = { id: 'bundle2', name: 'Bundle 2' }
        store.bundles = [bundle1, bundle2]

        expect(store.getBundleById('bundle1')).toEqual(bundle1)
        expect(store.getBundleById('bundle3')).toBe(null)
      })

      it('should search bundles', () => {
        const store = useBundlesStore()
        store.bundles = [
          { id: '1', name: 'Flux Bundle', author: 'John' },
          { id: '2', name: 'Stable Bundle', author: 'Jane' },
          { id: '3', description: 'Contains flux models' }
        ]

        const results = store.searchBundles('flux')
        expect(results).toHaveLength(2)
        expect(results.map(b => b.id)).toEqual(['1', '3'])
      })

      it('should filter bundles by criteria', () => {
        const store = useBundlesStore()
        store.bundles = [
          { id: '1', category: 'Models' },
          { id: '2', category: 'Workflows' },
          { id: '3', category: 'Models' }
        ]
        store.installedBundles = [{ id: '1' }]

        const modelBundles = store.filterBundles({ category: 'Models' })
        expect(modelBundles).toHaveLength(2)

        const installedBundles = store.filterBundles({ installed: true })
        expect(installedBundles).toHaveLength(1)
        expect(installedBundles[0].id).toBe('1')
      })
    })

    describe('Progress Management', () => {
      it('should update install progress', () => {
        const store = useBundlesStore()
        
        store.updateInstallProgress('bundle1', 75, 'installing')
        
        expect(store.installProgress['bundle1']).toMatchObject({
          progress: 75,
          status: 'installing',
          error: null
        })
      })

      it('should cancel installation', async () => {
        api.post.mockResolvedValueOnce({
          data: { success: true }
        })

        const store = useBundlesStore()
        store.installProgress['bundle1'] = { progress: 50 }
        
        await store.cancelInstallation('bundle1')
        
        expect(api.post).toHaveBeenCalledWith('/bundles/install/bundle1/cancel')
        expect(store.installProgress['bundle1']).toBeUndefined()
      })
    })

    describe('Batch Operations', () => {
      it('should install selected bundles', async () => {
        const bundles = [
          { id: 'bundle1', name: 'Bundle 1' },
          { id: 'bundle2', name: 'Bundle 2' }
        ]

        // Mock install responses
        bundles.forEach(() => {
          api.post.mockResolvedValueOnce({
            data: { success: true }
          })
          // Mock fetchInstalledBundles calls
          api.get.mockResolvedValueOnce({
            data: []
          })
        })

        const store = useBundlesStore()
        store.selectedBundles = bundles

        await store.installSelectedBundles()

        expect(api.post).toHaveBeenCalledTimes(2) // 2 installs
        expect(api.get).toHaveBeenCalledTimes(2) // 2 fetches
        expect(store.selectedBundles).toEqual([])
      })

      it('should update all bundles', async () => {
        const store = useBundlesStore()
        store.bundles = [
          { id: 'bundle1', version: '2.0.0' },
          { id: 'bundle2', version: '1.5.0' }
        ]
        store.installedBundles = [
          { id: 'bundle1', version: '1.0.0' },
          { id: 'bundle2', version: '1.0.0' }
        ]

        // Mock update responses
        api.post.mockResolvedValueOnce({
          data: { success: true }
        })
        api.post.mockResolvedValueOnce({
          data: { success: true }
        })
        
        // Mock fetchInstalledBundles calls
        api.get.mockResolvedValueOnce({
          data: []
        })
        api.get.mockResolvedValueOnce({
          data: []
        })

        await store.updateAllBundles()

        expect(api.post).toHaveBeenCalledTimes(2) // 2 updates
        expect(api.get).toHaveBeenCalledTimes(2) // 2 fetches
      })
    })
  })
})
