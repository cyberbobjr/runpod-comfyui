import { vi } from 'vitest';

// Mock the global window object to avoid ReferenceError in tests
vi.stubGlobal('window', {
    location: {
        origin: 'http://localhost'
    }
});
