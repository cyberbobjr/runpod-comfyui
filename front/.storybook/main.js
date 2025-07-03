

/** @type { import('@storybook/vue3-vite').StorybookConfig } */
import { mergeConfig } from 'vite';
import autoStoryGenerator from '@takuma-ru/auto-story-generator';

const config = {
  staticDirs: ['../public'],
  core: { builder: '@storybook/builder-vite' },
  stories: [
    "../src/**/*.mdx",
    "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"
  ],
  addons: [
    "@chromatic-com/storybook",
    "@storybook/addon-docs",
    "@storybook/addon-onboarding",
    "@storybook/addon-a11y",
    "@storybook/addon-vitest"
  ],
  framework: {
    "name": "@storybook/vue3-vite",
    "options": {}
  },
  viteFinal: (config) => mergeConfig(config, {
    plugins: [
      autoStoryGenerator.vite({
        preset: 'vue',
        imports: ['../src/components/**/*.vue'],
      }),
    ],
  }),
};
export default config;