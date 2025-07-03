import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import InstallProgressIndicator from '../components/InstallProgressIndicator.vue';

/**
 * InstallProgressIndicator Unit Tests
 *
 * These tests cover the main states and props of the InstallProgressIndicator component.
 */
describe('InstallProgressIndicator', () => {
  it('renders idle state correctly', () => {
    const wrapper = mount(InstallProgressIndicator, {
      props: { progress: 0, status: 'idle', message: 'Waiting to start installation...' }
    });
    expect(wrapper.text()).toContain('Waiting to start installation...');
  });

  it('renders in-progress state with progress', () => {
    const wrapper = mount(InstallProgressIndicator, {
      props: { progress: 45, status: 'in-progress', message: 'Installing...' }
    });
    expect(wrapper.text()).toContain('Installing...');
    expect(wrapper.html()).toContain('45');
  });

  it('renders completed state', () => {
    const wrapper = mount(InstallProgressIndicator, {
      props: { progress: 100, status: 'completed', message: 'Installation complete!' }
    });
    expect(wrapper.text()).toContain('Installation complete!');
  });

  it('renders error state', () => {
    const wrapper = mount(InstallProgressIndicator, {
      props: { progress: 60, status: 'error', message: 'An error occurred during installation.' }
    });
    expect(wrapper.text()).toContain('An error occurred during installation.');
  });
});
