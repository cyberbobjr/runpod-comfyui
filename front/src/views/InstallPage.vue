<template>
  <div class="install-page p-4 bg-background min-h-screen">
    <!-- Tabs Navigation -->
    <div class="bg-background-soft border border-border rounded-lg">
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faDownload, 
  faBoxOpen, 
  faCubes 
} from '@fortawesome/free-solid-svg-icons'

// Import components
import DownloadBundlesComponent from '../components/DownloadBundlesComponent.vue'
import DownloadModelsComponent from '../components/DownloadModelsComponent.vue'

// Router
const route = useRoute()
const router = useRouter()

// Active tab state
const activeTab = ref('bundles')

// Set initial tab based on query parameter or default to bundles
onMounted(() => {
  const tab = route.query.tab
  if (tab === 'models' || tab === 'bundles') {
    activeTab.value = tab
  }
})

// Watch for route changes to update active tab
watch(() => route.query.tab, (newTab) => {
  if (newTab === 'models' || newTab === 'bundles') {
    activeTab.value = newTab
  }
})

// Handle tab click and update URL
const handleTabClick = (tab) => {
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
