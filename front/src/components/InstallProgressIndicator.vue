<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { 
  faDownload, 
  faCheckCircle, 
  faExclamationCircle, 
  faTimes,
  faSpinner,
  faCog
} from '@fortawesome/free-solid-svg-icons';
import { useInstallProgress } from '../composables/useInstallProgress';
import { onMounted } from 'vue';

const { 
  activeInstallations, 
  cancelInstallation, 
  removeInstallation,
  cancelModelDownload,
  removeModelDownload,
  restoreActiveDownloads
} = useInstallProgress();

const getStatusIcon = (status) => {
  switch (status) {
    case 'downloading': return faDownload;
    case 'installing': return faCog;
    case 'completed': return faCheckCircle;
    case 'error': return faExclamationCircle;
    default: return faSpinner;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'downloading': return 'text-blue-500';
    case 'installing': return 'text-yellow-500';
    case 'completed': return 'text-green-500';
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

// Nouveau: gérer l'annulation selon le type
const handleCancel = (installation) => {
  if (installation.profiles && installation.profiles.includes('download') && installation.profiles.length === 1) {
    // C'est un téléchargement de modèle
    cancelModelDownload(installation.bundleId);
  } else {
    // C'est une installation de bundle
    cancelInstallation(installation.bundleId);
  }
};

// Nouveau: gérer la suppression selon le type
const handleRemove = (installation) => {
  if (installation.profiles && installation.profiles.includes('download') && installation.profiles.length === 1) {
    // C'est un téléchargement de modèle
    removeModelDownload(installation.bundleId);
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
    class="fixed bottom-4 right-4 z-50 space-y-2 max-w-sm"
  >
    <div 
      v-for="installation in activeInstallations" 
      :key="installation.bundleId"
      class="bg-background border border-border rounded-lg shadow-lg p-4 min-w-[320px]"
    >
      <!-- Header -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center">
          <FontAwesomeIcon 
            :icon="getStatusIcon(installation.status)" 
            :class="[
              'mr-2',
              getStatusColor(installation.status),
              installation.status === 'starting' || installation.status === 'installing' ? 'animate-spin' : ''
            ]"
          />
          <span class="font-medium text-text-light">{{ installation.bundleName }}</span>
        </div>
        <button 
          @click="handleRemove(installation)"
          class="text-text-muted hover:text-text-light"
          v-if="installation.status === 'completed' || installation.status === 'error'"
        >
          <FontAwesomeIcon :icon="faTimes" />
        </button>
      </div>

      <!-- Progress Bar -->
      <div class="mb-3">
        <div class="flex justify-between text-sm mb-1">
          <span class="text-text-muted">Progress</span>
          <span class="text-text-light">{{ installation.progress }}%</span>
        </div>
        <div class="w-full bg-background-mute rounded-full h-2">
          <div 
            class="h-2 rounded-full transition-all duration-300"
            :class="{
              'bg-blue-500': installation.status === 'downloading',
              'bg-yellow-500': installation.status === 'installing',
              'bg-green-500': installation.status === 'completed',
              'bg-red-500': installation.status === 'error'
            }"
            :style="{ width: `${installation.progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Current Step -->
      <div class="text-sm text-text-muted mb-2">
        {{ installation.currentStep }}
      </div>

      <!-- Profiles -->
      <div class="flex flex-wrap gap-1 mb-2">
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
          class="text-red-500 hover:text-red-400"
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
</template>
