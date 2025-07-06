<template>
    <div class="bg-background-soft border border-border">
      <!-- Tab Headers -->
      <div class="border-b border-border">
        <nav class="flex space-x-0" aria-label="Tabs">
          <button
            @click="handleTabClick('bundles')"
            :class="[
              'px-6 py-4 text-sm font-medium border-b-2 transition-colors duration-200',
              activeTab === 'bundles'
                ? 'border-primary text-primary bg-primary bg-opacity-10'
                : 'border-transparent text-text-muted hover:text-text-light hover:border-border'
            ]"
          >
            <FontAwesomeIcon :icon="faBoxOpen" class="mr-2" />
            Install Bundles
          </button>
          <button
            @click="handleTabClick('models')"
            :class="[
              'px-6 py-4 text-sm font-medium border-b-2 transition-colors duration-200',
              activeTab === 'models'
                ? 'border-primary text-primary bg-primary bg-opacity-10'
                : 'border-transparent text-text-muted hover:text-text-light hover:border-border'
            ]"
          >
            <FontAwesomeIcon :icon="faCubes" class="mr-2" />
            Install Models
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Bundles Tab -->
        <div v-if="activeTab === 'bundles'" class="tab-pane">
          <DownloadBundlesComponent />
        </div>

        <!-- Models Tab -->
        <div v-if="activeTab === 'models'" class="tab-pane">
          <DownloadModelsComponent />
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faBoxOpen, 
  faCubes 
} from '@fortawesome/free-solid-svg-icons'
import type { InstallTabType } from './types/views.types'

// Import components
import DownloadBundlesComponent from '../components/DownloadBundlesComponent.vue'
// @ts-ignore - TODO: Convert DownloadModelsComponent to TypeScript
import DownloadModelsComponent from '../components/DownloadModelsComponent.vue'

// Router
const route = useRoute()
const router = useRouter()

// Active tab state with proper typing
const activeTab = ref<InstallTabType>('bundles')

/**
 * Set initial tab based on query parameter or default to bundles
 * Validates the tab parameter to ensure it's a valid InstallTabType
 */
onMounted(() => {
  const tab = route.query.tab as string
  if (tab === 'models' || tab === 'bundles') {
    activeTab.value = tab as InstallTabType
  }
})

/**
 * Watch for route changes to update active tab
 * Ensures the tab parameter is valid before updating state
 */
watch(() => route.query.tab, (newTab) => {
  if (typeof newTab === 'string' && (newTab === 'models' || newTab === 'bundles')) {
    activeTab.value = newTab as InstallTabType
  }
})

/**
 * Handle tab click and update URL with query parameter
 * @param tab - The tab to activate (bundles or models)
 */
const handleTabClick = (tab: InstallTabType): void => {
  activeTab.value = tab
  router.push({ 
    name: 'install', 
    query: { tab } 
  })
}
</script>

<style scoped>
/* Ensure smooth transitions */
.tab-content {
  min-height: 400px;
}

/* Custom tab styling */
.tab-content > div {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
