/**
 * Main application entry point - TypeScript Version
 * 
 * This file bootstraps the Vue 3 application with:
 * - Pinia store management
 * - Vue Router
 * - FontAwesome icon library
 * - Global CSS styles
 * - Store initialization
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import type { App as VueApp } from 'vue';
// @ts-ignore - Vue component import
import App from './App.vue';
import router from './router';

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import { 
  faDownload,
  faCubes, 
  faBoxesStacked, 
  faFolder, 
  faFileCode, 
  faGear,
  faCheckCircle,
  faExclamationCircle,
  faExclamationTriangle,
  faInfoCircle,
  faTimes,
  faArrowUp,
  faArrowLeft,
  faSync,
  faUpload,
  faFolderPlus,
  faFolderOpen,
  faPencil,
  faTrash,
  faFileLines,
  faCopy,
  faBoxOpen,
  faTag,
  faInfo,
  faSitemap,
  faCube,
  faServer,
  faCogs,
  faEdit,
  faTrashAlt,
  faPlusCircle,
  faChevronUp,
  faChevronDown,
  faMicrochip,
  faMinusCircle,
  faSave,
  faUndo,
  faExternalLinkAlt,
  faKey,
  faLock,
  faUser,
  faUserEdit,
  faShieldAlt,
  faEye,
  faEyeSlash,
  faSpinner,
  faCodeBranch,
  faGlobe,
  faFilter,
  faSearch,
  faTags,
  faDatabase,
  faTimesCircle,
  faPlus,
  faLayerGroup,
  faSliders
} from '@fortawesome/free-solid-svg-icons';

// Import global styles
import './assets/main.css';
import { initializeStores } from './stores/index';
import { initializeApp } from './core/app-initialization';

/**
 * Array of FontAwesome icons to register
 */
const iconsToRegister: IconDefinition[] = [
  faDownload,
  faCubes, 
  faBoxesStacked, 
  faFolder, 
  faFileCode, 
  faGear,
  faCheckCircle,
  faExclamationCircle,
  faExclamationTriangle,
  faInfoCircle,
  faTimes,
  faArrowUp,
  faArrowLeft,
  faSync,
  faUpload,
  faFolderPlus,
  faFolderOpen,
  faPencil,
  faTrash,
  faFileLines,
  faCopy,
  faBoxOpen,
  faTag,
  faInfo,
  faSitemap,
  faCube,
  faServer,
  faCogs,
  faEdit,
  faTrashAlt,
  faPlusCircle,
  faChevronUp,
  faChevronDown,
  faMicrochip,
  faMinusCircle,
  faSave,
  faUndo,
  faExternalLinkAlt,
  faKey,
  faLock,
  faUser,
  faUserEdit,
  faShieldAlt,
  faEye,
  faEyeSlash,
  faSpinner,
  faCodeBranch,
  faGlobe,
  faFilter,
  faSearch,
  faTags,
  faDatabase,
  faTimesCircle,
  faPlus,
  faLayerGroup,
  faSliders
];

/**
 * Bootstrap the Vue application
 * 
 * **Description:** Initializes and configures the Vue application with all required plugins and libraries.
 * **Parameters:** None
 * **Returns:** Promise that resolves when the application is fully initialized
 */
async function bootstrapApp(): Promise<void> {
  try {
    // Add icons to the FontAwesome library
    library.add(...iconsToRegister);

    // Create Vue app instance
    const app: VueApp = createApp(App);
    const pinia = createPinia();

    // Register FontAwesome component globally
    app.component('FontAwesomeIcon', FontAwesomeIcon);
    
    // Configure plugins
    app.use(pinia);
    app.use(router);

    // Mount the application
    app.mount('#app');
    initializeApp(router);
    // Initialize stores after app is mounted
    await initializeStores();

    console.log('Application bootstrapped successfully');
  } catch (error) {
    console.error('Failed to bootstrap application:', error);
    throw error;
  }
}

// Bootstrap the application
bootstrapApp().catch((error: Error) => {
  console.error('Application failed to start:', error);
});
