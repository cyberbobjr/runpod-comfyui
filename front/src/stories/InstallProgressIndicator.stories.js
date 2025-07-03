import InstallProgressIndicator from '../components/InstallProgressIndicator.vue';
import { http, HttpResponse } from 'msw';

export default {
    title: 'InstallProgressIndicator',
    component: InstallProgressIndicator,
    decorators: [],
};

export const WithDownloads = {
    parameters: {
        msw: {
            handlers: {
                downloads: http.get('/api/downloads', (req, res, ctx) => {
                    if (req.headers.get('x-msw-mock') !== 'true') {
                        return res(ctx.status(401), ctx.json({ message: 'Unauthorized' }));
                    }
                    return res(
                        ctx.delay(500),
                        ctx.json({ downloadProgress: [ /* ... */] })
                    );
                }),
            },
        },
    },
    render: () => ({
        components: { InstallProgressIndicator },
        template: '<InstallProgressIndicator />',
    }),
};
