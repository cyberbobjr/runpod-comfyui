<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { 
  faDownload, 
  faCheckCircle, 
  faExclamationCircle, 
  faTimes,
  faSpinner,
  faCog,
  faChevronDown,
  faChevronUp,
  faMinus
} from '@fortawesome/free-solid-svg-icons';
import { useInstallProgress } from '../composables/useInstallProgress';
import { onMounted, ref, computed } from 'vue';

const { 
  activeInstallations, 
  cancelInstallation, 
  removeInstallation,
  cancelModelDownload,
  removeModelDownload,
  restoreActiveDownloads
} = useInstallProgress();

// État pour gérer l'expansion/réduction de la popup
const isExpanded = ref(true);
const isMinimized = ref(false);

// Computed pour le résumé des téléchargements
const downloadsSummary = computed(() => {
  const total = activeInstallations.value.length;
  const downloading = activeInstallations.value.filter(i => i.status === 'downloading').length;
  const completed = activeInstallations.value.filter(i => i.status === 'completed').length;
  const cancelled = activeInstallations.value.filter(i => i.status === 'cancelled').length;
  const errors = activeInstallations.value.filter(i => i.status === 'error').length;
  
  return { total, downloading, completed, cancelled, errors };
});

const getStatusIcon = (status) => {
  switch (status) {
    case 'downloading': return faDownload;
    case 'installing': return faCog;
    case 'completed': return faCheckCircle;
    case 'cancelled': return faTimes;
    case 'error': return faExclamationCircle;
    default: return faSpinner;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'downloading': return 'text-blue-500';
    case 'installing': return 'text-yellow-500';
    case 'completed': return 'text-green-500';
    case 'cancelled': return 'text-orange-500';
    case 'error': return 'text-red-500';
    default: return 'text-gray-500';
  }
};

const formatElapsedTime = (startTime) => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const toggleMinimized = () => {
  isMinimized.value = !isMinimized.value;
  if (!isMinimized.value) {
    isExpanded.value = true; // Si on déminimise, on expand automatiquement
  }
};

// Nouveau: gérer l'annulation selon le type
const handleCancel = async (installation) => {
  try {
    if (installation.profiles && installation.profiles.includes('download') && installation.profiles.length === 1) {
      // C'est un téléchargement de modèle - utiliser downloadId si disponible, sinon bundleId
      const idToCancel = installation.downloadId || installation.bundleId;
      await cancelModelDownload(idToCancel);
    } else {
      // C'est une installation de bundle
      await cancelInstallation(installation.bundleId);
    }
  } catch (error) {
    console.error('Error cancelling:', error);
  }
};

// Nouveau: gérer la suppression selon le type
const handleRemove = (installation) => {
  if (installation.profiles && installation.profiles.includes('download') && installation.profiles.length === 1) {
    // C'est un téléchargement de modèle - utiliser downloadId si disponible, sinon bundleId
    const idToRemove = installation.downloadId || installation.bundleId;
    removeModelDownload(idToRemove);
  } else {
    // C'est une installation de bundle
    removeInstallation(installation.bundleId);
  }
};

// Restaurer les téléchargements actifs au montage du composant
onMounted(async () => {
  await restoreActiveDownloads();
});
</script>

<template>
  <!-- Progress Indicators Container -->
  <div 
    v-if="activeInstallations.length > 0" 
    class="fixed bottom-4 right-4 z-50 space-y-2"
    :class="isMinimized ? 'max-w-xs' : 'max-w-sm'"
  >
    <!-- Header (always visible, même en minimized) -->
    <div class="bg-background border border-border rounded-lg shadow-lg">
      <div class="flex items-center justify-between p-3 cursor-pointer" @click="toggleMinimized">
        <div class="flex items-center space-x-2">
          <FontAwesomeIcon 
            :icon="faDownload" 
            class="text-blue-500"
          />
          <span class="font-medium text-text-light text-sm">
            Downloads ({{ downloadsSummary.total }})
          </span>
          <div class="flex space-x-1">
            <span 
              v-if="downloadsSummary.downloading > 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-500 text-white"
            >
              {{ downloadsSummary.downloading }}
            </span>            <span 
              v-if="downloadsSummary.completed > 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-500 text-white"
            >
              ✓{{ downloadsSummary.completed }}
            </span>
            <span 
              v-if="downloadsSummary.cancelled > 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-orange-500 text-white"
            >
              ✕{{ downloadsSummary.cancelled }}
            </span>
            <span 
              v-if="downloadsSummary.errors > 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-500 text-white"
            >
              !{{ downloadsSummary.errors }}
            </span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button 
            v-if="!isMinimized"
            @click.stop="toggleExpanded"
            class="text-text-muted hover:text-text-light p-1"
            :title="isExpanded ? 'Collapse' : 'Expand'"
          >
            <FontAwesomeIcon :icon="isExpanded ? faChevronUp : faChevronDown" />
          </button>
          <button 
            @click.stop="toggleMinimized"
            class="text-text-muted hover:text-text-light p-1"
            :title="isMinimized ? 'Restore' : 'Minimize'"
          >
            <FontAwesomeIcon :icon="isMinimized ? faChevronUp : faMinus" />
          </button>
        </div>
      </div>

      <!-- Detailed List (only when not minimized and expanded) -->
      <div v-if="!isMinimized && isExpanded" class="border-t border-border">
        <div 
          v-for="installation in activeInstallations" 
          :key="installation.bundleId"
          class="p-4 border-b border-border last:border-b-0"
        >
          <!-- Header -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <FontAwesomeIcon 
                :icon="getStatusIcon(installation.status)" 
                :class="[
                  'mr-2 text-sm',
                  getStatusColor(installation.status),
                  installation.status === 'starting' || installation.status === 'installing' ? 'animate-spin' : ''
                ]"
              />
              <span class="font-medium text-text-light text-sm truncate max-w-[200px]" :title="installation.bundleName">
                {{ installation.bundleName }}
              </span>
            </div>            <button 
              @click="handleRemove(installation)"
              class="text-text-muted hover:text-text-light text-sm"
              v-if="installation.status === 'completed' || installation.status === 'error' || installation.status === 'cancelled'"
            >
              <FontAwesomeIcon :icon="faTimes" />
            </button>
          </div>

          <!-- Progress Bar -->
          <div class="mb-3">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-text-muted">Progress</span>
              <span class="text-text-light">{{ installation.progress }}%</span>
            </div>
            <div class="w-full bg-background-mute rounded-full h-1.5">              <div 
                class="h-1.5 rounded-full transition-all duration-300"
                :class="{
                  'bg-blue-500': installation.status === 'downloading',
                  'bg-yellow-500': installation.status === 'installing',
                  'bg-green-500': installation.status === 'completed',
                  'bg-orange-500': installation.status === 'cancelled',
                  'bg-red-500': installation.status === 'error'
                }"
                :style="{ width: `${installation.progress}%` }"
              ></div>
            </div>
          </div>

          <!-- Current Step -->
          <div class="text-xs text-text-muted mb-2 truncate">
            {{ installation.currentStep }}
          </div>

          <!-- Profiles (only for bundles, not individual model downloads) -->
          <div 
            v-if="installation.profiles && !(installation.profiles.includes('download') && installation.profiles.length === 1)"
            class="flex flex-wrap gap-1 mb-2"
          >
            <span 
              v-for="profile in installation.profiles" 
              :key="profile"
              class="inline-flex items-center px-2 py-1 rounded text-xs bg-primary text-white"
            >
              {{ profile }}
            </span>
          </div>

          <!-- Time and Actions -->
          <div class="flex justify-between items-center text-xs text-text-muted">
            <span>{{ formatElapsedTime(installation.startTime) }}</span>
            <button 
              v-if="installation.status === 'downloading' || installation.status === 'installing'"
              @click="handleCancel(installation)"
              class="text-red-500 hover:text-red-400 text-xs px-2 py-1 border border-red-500 rounded hover:bg-red-500 hover:text-white transition-colors"
            >
              Cancel
            </button>
          </div>

          <!-- Errors -->
          <div v-if="installation.errors.length > 0" class="mt-2">
            <div class="text-xs text-red-400">
              <div v-for="error in installation.errors" :key="error" class="mb-1">
                {{ error }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
