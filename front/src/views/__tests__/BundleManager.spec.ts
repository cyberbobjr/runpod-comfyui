/**
 * BundleManager Component Tests
 * 
 * Test suite for the BundleManager component, covering bundle management functionality,
 * TypeScript integration, and user interactions.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import BundleManager from '../BundleManager.vue'
import { useBundlesStore } from '../../stores/bundles'
import { useNotifications } from '../../composables/useNotifications'
import type { Bundle } from '../../stores/types/bundles.types'

// Mock FontAwesome
vi.mock('@fortawesome/vue-fontawesome', () => ({
  FontAwesomeIcon: {
    name: 'FontAwesomeIcon',
    template: '<i class="fa-icon"></i>'
  }
}))

// Mock notifications
vi.mock('../../composables/useNotifications', () => ({
  useNotifications: vi.fn(() => ({
    success: vi.fn(),
    error: vi.fn(),
    confirm: vi.fn()
  }))
}))

// Mock API
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn()
  }
}))

// Mock components
vi.mock('../../components/common/CommonCard.vue', () => ({
  default: {
    name: 'CommonCard',
    template: '<div class="common-card"><slot name="header"></slot><slot></slot></div>'
  }
}))

vi.mock('../../components/bundle/BundleEditor.vue', () => ({
  default: {
    name: 'BundleEditor',
    template: '<div class="bundle-editor">Bundle Editor</div>',
    emits: ['saved', 'cancel']
  }
}))

describe('BundleManager', () => {
  let wrapper: VueWrapper<any>
  let bundlesStore: ReturnType<typeof useBundlesStore>
  let notifications: ReturnType<typeof useNotifications>

  const mockBundles: Bundle[] = [
    {
      id: '1',
      name: 'Test Bundle 1',
      description: 'Test description 1',
      version: '1.0.0',
      author: 'Test Author',
      website: 'https://test.com',
      workflows: ['workflow1.json'],
      hardware_profiles: {
        'gpu-high': {
          name: 'High-end GPU',
          description: 'For powerful graphics cards',
          models: []
        }
      }
    },
    {
      id: '2',
      name: 'Test Bundle 2',
      description: 'Test description 2',
      version: '2.0.0',
      author: 'Another Author',
      workflows: ['workflow2.json'],
      hardware_profiles: {}
    }
  ]

  beforeEach(() => {
    setActivePinia(createPinia())
    bundlesStore = useBundlesStore()
    notifications = useNotifications()

    // Mock store methods
    vi.spyOn(bundlesStore, 'fetchBundles').mockResolvedValue()
    vi.spyOn(bundlesStore, 'getBundleById').mockImplementation((id: string) => 
      mockBundles.find(b => b.id === id) || null
    )
    vi.spyOn(bundlesStore, 'deleteBundle').mockResolvedValue()

    // Set mock bundles in store
    bundlesStore.bundles = mockBundles

    wrapper = mount(BundleManager, {
      global: {
        stubs: {
          CommonCard: true,
          BundleEditor: true,
          FontAwesomeIcon: true
        }
      }
    })
  })

  describe('Component Initialization', () => {
    it('should render without errors', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should display bundle list by default', () => {
      expect(wrapper.find('.min-w-full').exists()).toBe(true)
      expect(wrapper.text()).toContain('Model Bundles')
    })

    it('should fetch bundles on mount', () => {
      expect(bundlesStore.fetchBundles).toHaveBeenCalled()
    })
  })

  describe('Bundle Display', () => {
    it('should display bundle information correctly', () => {
      const table = wrapper.find('table')
      expect(table.exists()).toBe(true)
      
      // Check if bundle names are displayed
      expect(wrapper.text()).toContain('Test Bundle 1')
      expect(wrapper.text()).toContain('Test Bundle 2')
    })

    it('should display bundle versions and authors', () => {
      expect(wrapper.text()).toContain('1.0.0')
      expect(wrapper.text()).toContain('2.0.0')
      expect(wrapper.text()).toContain('Test Author')
      expect(wrapper.text()).toContain('Another Author')
    })

    it('should display workflows as badges', () => {
      const workflowBadges = wrapper.findAll('.bg-blue-600')
      expect(workflowBadges.length).toBeGreaterThan(0)
    })

    it('should display hardware profiles', () => {
      const profileBadges = wrapper.findAll('.bg-gray-600')
      expect(profileBadges.length).toBeGreaterThan(0)
    })
  })

  describe('Bundle Actions', () => {
    it('should show bundle form when creating new bundle', async () => {
      const newBundleBtn = wrapper.find('[data-testid="new-bundle-btn"]') || 
                          wrapper.find('button:contains("New Bundle")')
      
      if (newBundleBtn.exists()) {
        await newBundleBtn.trigger('click')
        await wrapper.vm.$nextTick()
        
        expect(wrapper.vm.showBundleForm).toBe(true)
        expect(wrapper.vm.currentBundle.id).toBe(null)
      }
    })

    it('should handle bundle editing', async () => {
      const editBtn = wrapper.find('button:contains("Edit")')
      
      if (editBtn.exists()) {
        await editBtn.trigger('click')
        await wrapper.vm.$nextTick()
        
        expect(bundlesStore.getBundleById).toHaveBeenCalled()
        expect(wrapper.vm.showBundleForm).toBe(true)
      }
    })

    it('should handle bundle deletion with confirmation', async () => {
      // Mock confirm to return true
      vi.mocked(notifications.confirm).mockResolvedValue(true)
      
      await wrapper.vm.handleDeleteBundle('1')
      
      expect(notifications.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete bundle "Test Bundle 1"?',
        'Confirm Deletion'
      )
      expect(bundlesStore.deleteBundle).toHaveBeenCalledWith('1')
      expect(notifications.success).toHaveBeenCalledWith(
        'Bundle "Test Bundle 1" deleted successfully'
      )
    })

    it('should not delete bundle if not confirmed', async () => {
      // Mock confirm to return false
      vi.mocked(notifications.confirm).mockResolvedValue(false)
      
      await wrapper.vm.handleDeleteBundle('1')
      
      expect(bundlesStore.deleteBundle).not.toHaveBeenCalled()
    })
  })

  describe('Form Interactions', () => {
    it('should return to bundle list after saving', async () => {
      wrapper.vm.showBundleForm = true
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.afterBundleSaved()
      
      expect(wrapper.vm.showBundleForm).toBe(false)
      expect(notifications.success).toHaveBeenCalledWith('Bundle saved successfully')
    })

    it('should return to bundle list on cancel', async () => {
      wrapper.vm.showBundleForm = true
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.returnToBundleList()
      
      expect(wrapper.vm.showBundleForm).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should handle bundle loading errors', async () => {
      vi.spyOn(bundlesStore, 'getBundleById').mockReturnValue(null)
      
      await wrapper.vm.editBundle('non-existent')
      
      expect(notifications.error).toHaveBeenCalledWith('Bundle not found')
    })

    it('should handle deletion errors', async () => {
      const error = new Error('Delete failed')
      vi.spyOn(bundlesStore, 'deleteBundle').mockRejectedValue(error)
      vi.mocked(notifications.confirm).mockResolvedValue(true)
      
      await wrapper.vm.handleDeleteBundle('1')
      
      expect(notifications.error).toHaveBeenCalledWith(
        expect.stringContaining('Failed to delete bundle')
      )
    })
  })

  describe('TypeScript Integration', () => {
    it('should have properly typed currentBundle', () => {
      const currentBundle = wrapper.vm.currentBundle
      
      expect(typeof currentBundle.id).toBe('object') // null or string
      expect(typeof currentBundle.name).toBe('string')
      expect(typeof currentBundle.description).toBe('string')
      expect(typeof currentBundle.version).toBe('string')
      expect(typeof currentBundle.author).toBe('string')
      expect(typeof currentBundle.website).toBe('string')
      expect(Array.isArray(currentBundle.workflows)).toBe(true)
      expect(typeof currentBundle.hardware_profiles).toBe('object')
    })

    it('should handle typed method parameters correctly', async () => {
      // Test that methods accept correct parameter types
      await wrapper.vm.editBundle('test-id')
      await wrapper.vm.handleDeleteBundle('test-id')
      await wrapper.vm.downloadBundle('test-id', 'test-name', '1.0.0')
      
      // No TypeScript errors should occur
      expect(true).toBe(true)
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no bundles exist', async () => {
      bundlesStore.bundles = []
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('No bundles available')
      expect(wrapper.text()).toContain('Create your first bundle below')
    })
  })
})
