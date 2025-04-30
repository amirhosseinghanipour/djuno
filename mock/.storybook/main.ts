import type { StorybookConfig } from '@storybook/html-vite';

const config: StorybookConfig = {
  stories: ['../components/**/*.stories.ts'],
  addons: ['@storybook/addon-essentials', '@storybook/addon-controls'],
  framework: {
    name: '@storybook/html-vite',
    options: {}
  }
};

export default config;
