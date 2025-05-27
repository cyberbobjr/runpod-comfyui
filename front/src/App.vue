<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { 
  faDownload, 
  faBoxesStacked, 
  faFolder, 
  faFileCode, 
  faGear 
} from '@fortawesome/free-solid-svg-icons';
import NotificationContainer from './components/NotificationContainer.vue'
import DialogContainer from './components/DialogContainer.vue'
import InstallProgressIndicator from './components/InstallProgressIndicator.vue'
import { useNotifications } from './composables/useNotifications'

const route = useRoute()
const router = useRouter()
const { loadPersistentNotifications } = useNotifications()

// Check if the user is authenticated
const isAuthenticated = computed(() => {
  return !!localStorage.getItem('auth_token')
})

// Check if current route requires authentication
const showHeader = computed(() => {
  return isAuthenticated.value && route.meta.requiresAuth
})

// Logout function
const handleLogout = () => {
  // Remove token from localStorage
  localStorage.removeItem('auth_token')
  // Navigate to login page
  router.push({ name: 'login' })
}

// Get current active tab based on route
const activeTab = computed(() => {
  return route.name || 'download-bundles'
})

// Watch for active tab changes to navigate
const handleTabChange = (name) => {
  router.push({ name });
}

// Tabs definition
const tabs = [
  { 
    name: 'download-bundles', 
    label: 'Install bundles', 
    icon: faDownload,
  },
  { 
    name: 'download-models', 
    label: 'Install models', 
    icon: faDownload,
  },
  { 
    name: 'manage-bundles', 
    label: 'Manage bundles', 
    icon: faBoxesStacked,
  },
  { 
    name: 'file-explorer', 
    label: 'File Explorer', 
    icon: faFolder,
  },
  { 
    name: 'json-editor', 
    label: 'JSON Editor', 
    icon: faFileCode,
  },
  { 
    name: 'settings', 
    label: 'Settings', 
    icon: faGear,
  }
];

// Load persistent notifications on app startup
onMounted(() => {
  // Les notifications persistantes sont maintenant chargées automatiquement 
  // lors de la première utilisation du composable useNotifications
})
</script>

<template>
  <div class="app-container">
    <!-- Header bar that appears only when logged in -->
    <header v-if="showHeader" class="bg-background-soft text-text-light flex justify-between items-center py-4 shadow-md border-b border-border">
      <h1 class="text-2xl font-semibold ml-4">ComfyUI Model Manager</h1>
      <button 
        @click="handleLogout" 
        class="btn bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors mr-4"
      >
        Logout
      </button>
    </header>
    
    <!-- Navigation tabs that appear only when logged in -->
    <div v-if="showHeader" class="border-b border-border bg-background-soft w-full">
      <div class="flex overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          @click="handleTabChange(tab.name)"
          :class="[
            'flex items-center px-6 py-4 transition-colors focus:outline-none whitespace-nowrap',
            activeTab === tab.name
              ? 'text-primary border-b-2 border-primary bg-background-mute'
              : 'text-text-light-muted hover:bg-background-mute hover:text-text-light'
          ]"
        >
          <FontAwesomeIcon 
            :icon="tab.icon" 
            class="mr-3 text-lg" 
            :class="{ 'text-primary': activeTab === tab.name }"
          />
          <span class="text-sm font-medium">{{ tab.label }}</span>
        </button>
      </div>
    </div>
    
    <div class="view-container flex-1 overflow-auto bg-background w-full">
      <RouterView />
    </div>
    
    <!-- Notification and Dialog containers -->
    <NotificationContainer />
    <DialogContainer />
    
    <!-- Global Install Progress Indicator -->
    <InstallProgressIndicator />
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  background-color: #0f2537; /* Direct color instead of Tailwind class for reliability */
  color: #ffffff;
}

body {
  font-family: sans-serif;
}

#app {
  width: 100vw;
  min-height: 100vh;
  height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: none;
  padding: 0;
  margin: 0;
  overflow-x: hidden;
}

.app-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 0;
  height: 100%;
  max-width: 100%;
  /* Adding max-width and centering for large screens */
  margin: 0 auto;
}

/* Media query for large screens */
@media (min-width: 1280px) {
  .app-container {
    max-width: 1280px; /* Limiting width on large screens */
  }
}

.view-container {
  flex: 1 1 auto;
  width: 100%;
  min-height: 0;
  overflow: auto;
}
</style>
