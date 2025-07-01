import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
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
  faLayerGroup
} from '@fortawesome/free-solid-svg-icons'

// Add icons to the library
library.add(
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
  faLayerGroup
)
import './assets/main.css'
import { initializeStores } from './stores'

const app = createApp(App)
const pinia = createPinia()

// Enregistrer FontAwesome globalement
app.component('FontAwesomeIcon', FontAwesomeIcon)
app.use(pinia)
app.use(router)

app.mount('#app')
await initializeStores()
