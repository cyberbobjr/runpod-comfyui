import { setup } from '@storybook/vue3-vite';
import { createPinia } from 'pinia';
import { initialize, mswLoader } from 'msw-storybook-addon';
import { http, HttpResponse } from 'msw';

initialize({ onUnhandledRequest: 'bypass' });
export const decorators = [
  (storyFn, context) => {
    context.parameters.msw.headers = {
      'x-msw-mock': 'true',
      ...(context.parameters.msw.headers ?? {}),
    };
    return storyFn();
  },
];

setup(app => {
  app.use(createPinia());
});
export const loaders = [mswLoader];

const preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: { test: 'todo' },
    msw: {
      handlers: {
        // exemples de handlers globaux
        api: [
          http.get('/api/downloads', () =>
            HttpResponse.json([{ id: 1, name: 'Foo' }])
          ),
        ],
      },
    },
  },
  loaders: [mswLoader],
};

export default preview;
