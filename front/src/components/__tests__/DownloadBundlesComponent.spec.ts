import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createPinia } from 'pinia';
import DownloadBundlesComponent from '../DownloadBundlesComponent.vue';

// Mock API service
vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  }
}));

// Mock Pinia bundles store
const mockUploadBundleZip = vi.fn().mockResolvedValue({ ok: true, bundle_id: '1' });
vi.mock('../stores/bundles', () => ({
  useBundlesStore: () => ({
    bundles: [
      {
        id: '1',
        name: 'Test Bundle',
        description: 'A test bundle',
        hardware_profiles: { cpu: { models: [{ dest: 'model1.safetensors' }] } },
        workflows: ['wf1'],
      }
    ],
    isLoading: false,
    fetchBundles: vi.fn(),
    fetchInstalledBundles: vi.fn(),
    deleteBundle: vi.fn(),
    uploadBundleZip: mockUploadBundleZip,
    isBundleInstalled: vi.fn().mockReturnValue(false),
  }),
}));

// Mock Pinia models store
vi.mock('../stores/models', () => ({
  useModelsStore: () => ({
    fetchModels: vi.fn(),
    isModelInstalled: vi.fn().mockReturnValue(false),
  }),
}));

// Mock notifications composable
vi.mock('@/composables/useNotifications', () => ({
  useNotifications: () => ({
    success: vi.fn(),
    error: vi.fn(),
    confirm: vi.fn().mockResolvedValue(true),
  }),
}));

describe('DownloadBundlesComponent', () => {
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
  });

  it('renders uploaded bundles', async () => {
    const wrapper = mount(DownloadBundlesComponent, {
      global: {
        plugins: [pinia],
        stubs: {
          CommonCard: true,
          CommonModal: true,
          AccordionComponent: true,
          ButtonDropdownComponent: true,
          FontAwesomeIcon: true,
        },
      },
    });
    await flushPromises();
    expect(wrapper.text()).toContain('Test Bundle');
    expect(wrapper.text()).toContain('A test bundle');
  });

  it('uploads a bundle successfully', async () => {
    const wrapper = mount(DownloadBundlesComponent, {
      global: {
        plugins: [pinia],
        stubs: {
          CommonCard: true,
          CommonModal: true,
          AccordionComponent: true,
          ButtonDropdownComponent: true,
          FontAwesomeIcon: true,
        },
      },
    });
    await flushPromises();

    const file = new File(['content'], 'test.zip', { type: 'application/zip' });
    const fileInput = wrapper.find('input[type="file"]');
    
    // This is a simplified way to simulate a file selection
    // In a real scenario, you might need a more complex approach if this doesn't work
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      writable: false,
    });

    await fileInput.trigger('change');
    await flushPromises();

    expect(mockUploadBundleZip).toHaveBeenCalledWith(file);
  });

  it('shows bundle details modal when Details is clicked', async () => {
    const wrapper = mount(DownloadBundlesComponent, {
      global: {
        plugins: [pinia],
        stubs: {
          CommonCard: true,
          CommonModal: true,
          AccordionComponent: true,
          ButtonDropdownComponent: true,
          FontAwesomeIcon: true,
        },
      },
    });
    await flushPromises();
    const detailsBtn = wrapper.find('button[title="View bundle details"]');
    expect(detailsBtn.exists()).toBe(true);
    await detailsBtn.trigger('click');
    await flushPromises();
    expect(wrapper.text()).toContain('Bundle Details: Test Bundle');
  });
});
