import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ComfyUIView from '@/views/ComfyUIView.vue'
import { useComfyUIStore } from '@/stores/comfyui'

// Mock the composables
vi.mock('@/composables/useComfySocket', () => ({
  useComfySocket: vi.fn(() => ({
    previewImage: { value: null },
    finalImage: { value: null }
  }))
}))

// Mock FontAwesome icons
vi.mock('@fortawesome/vue-fontawesome', () => ({
  FontAwesomeIcon: {
    name: 'FontAwesomeIcon',
    template: '<i class="fa-icon"></i>'
  }
}))

// Mock the API service
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('ComfyUIView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the component correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    expect(wrapper.find('.comfyui-page').exists()).toBe(true)
    expect(wrapper.find('.generation-form-panel').exists()).toBe(true)
    expect(wrapper.text()).toContain('ComfyUI Generation')
  })

  it('shows collapsed form when isFormCollapsed is true', async () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    // Find and click the collapse button
    const collapseButton = wrapper.find('button[title="Collapse Form"]')
    await collapseButton.trigger('click')

    // Check that the form is now collapsed
    expect(wrapper.find('.generation-form-panel').classes()).toContain('w-12')
  })

  it('shows server status correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    
    // Test offline status
    store.isServerAvailable = false
    expect(wrapper.text()).toContain('ComfyUI Server Offline')
    
    // Test online status
    store.isServerAvailable = true
    expect(wrapper.text()).toContain('ComfyUI Server Online')
  })

  it('shows loading state correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    store.loading = true
    store.isGenerating = false

    expect(wrapper.text()).toContain('Loading...')
  })

  it('shows error state correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    store.error = 'Test error message'

    expect(wrapper.text()).toContain('Error')
    expect(wrapper.text()).toContain('Test error message')
  })

  it('shows generation state correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    store.isGenerating = true

    expect(wrapper.text()).toContain('Initializing generation...')
  })

  it('shows final results correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    store.finalImages = ['image1.png', 'image2.png']

    const images = wrapper.findAll('img[alt*="Generated image"]')
    expect(images.length).toBe(2)
  })

  it('shows empty state correctly', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Ready to Generate')
    expect(wrapper.text()).toContain('Fill in the generation parameters')
  })

  it('disables generate button when conditions are not met', () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const generateButton = wrapper.find('button[type="submit"]')
    expect(generateButton.attributes('disabled')).toBeDefined()
  })

  it('enables generate button when all conditions are met', async () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    store.isServerAvailable = true
    store.models = { 'flux-dev': { model_type: 'flux', filename: 'flux.safetensors' } }
    
    // Set form state via component data
    const component = wrapper.vm as any
    component.formState.params.prompt = 'Test prompt'
    component.formState.params.model_key = 'flux-dev'
    
    await wrapper.vm.$nextTick()
    
    const generateButton = wrapper.find('button[type="submit"]')
    expect(generateButton.attributes('disabled')).toBeUndefined()
  })

  it('handles form submission correctly', async () => {
    const wrapper = mount(ComfyUIView, {
      global: {
        stubs: {
          FontAwesomeIcon: true,
          AccordionComponent: true,
          FormDropdownComponent: true,
          CommonModal: true
        }
      }
    })

    const store = useComfyUIStore()
    const generateAndExecuteSpy = vi.spyOn(store, 'generateAndExecute').mockResolvedValue({
      prompt_id: 'test-123',
      status: 'submitted'
    })

    // Set up form state
    const component = wrapper.vm as any
    component.formState.params.prompt = 'Test prompt'
    component.formState.params.model_key = 'flux-dev'
    
    // Submit form
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(generateAndExecuteSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        prompt: 'Test prompt',
        model_key: 'flux-dev',
        wait: false
      })
    )
  })
})
