import { mount } from '@vue/test-utils';
import ModelSelectorModal from '@/components/common/ModelSelectorModal.vue';

describe('ModelSelectorModal', () => {
  const groupedModels = {
    GroupA: [
      { id: 1, name: 'Model 1', tags: ['base'], type: 'A', size: 1024 },
      { id: 2, name: 'Model 2', tags: ['fp8'], type: 'A', size: 2048 },
    ],
    GroupB: [
      { id: 3, name: 'Model 3', tags: ['nsfw'], type: 'B', size: 4096 },
    ],
  };
  const selectedModels = [groupedModels.GroupA[0]];
  const popularTags = ['base', 'fp8', 'nsfw'];

  it('renders and emits close', async () => {
    const wrapper = mount(ModelSelectorModal, {
      props: {
        show: true,
        currentProfileName: 'TestProfile',
        groupedModels,
        selectedModels,
        popularTags,
      },
    });
    expect(wrapper.text()).toContain('Select Models for TestProfile');
    await wrapper.find('button.btn-secondary').trigger('click');
    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('filters models by tag', async () => {
    const wrapper = mount(ModelSelectorModal, {
      props: {
        show: true,
        currentProfileName: 'TestProfile',
        groupedModels,
        selectedModels: [],
        popularTags,
      },
    });
    await wrapper.find('button').trigger('click'); // open filter
    const input = wrapper.find('input[type="text"]');
    await input.setValue('fp8');
    expect(wrapper.text()).toContain('Model 2');
    expect(wrapper.text()).not.toContain('Model 1');
  });

  it('emits apply-selection with selected models', async () => {
    const wrapper = mount(ModelSelectorModal, {
      props: {
        show: true,
        currentProfileName: 'TestProfile',
        groupedModels,
        selectedModels: [],
        popularTags,
      },
    });
    // Select a model
    await wrapper.findAll('input[type="checkbox"]')[0].setValue(true);
    await wrapper.find('button.btn-primary').trigger('click');
    expect(wrapper.emitted('apply-selection')).toBeTruthy();
  });
});
