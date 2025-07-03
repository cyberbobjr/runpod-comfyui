<template>
  <!-- Progress Indicators Container -->
  <div
    v-if="downloadsSummary.total > 0"
    class="fixed bottom-4 right-4 z-50 space-y-2"
  >
    <!-- Header (always visible, même en minimized) -->
    <div class="bg-background border border-border rounded-lg shadow-lg">
      <div
        class="flex items-center justify-between p-3 cursor-pointer"
        @click="toggleMinimized"
      >
        <div class="flex items-center space-x-2">
          <FontAwesomeIcon :icon="faDownload" class="text-blue-500" />
          <span class="font-medium text-text-light text-sm">
            Downloads ({{ downloadsSummary.total }})
          </span>
          <div class="flex space-x-1">
            <span
              v-if="downloadsSummary.downloading > 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-500 text-white"
            >
              {{ downloadsSummary.downloading }}
            </span>
            <span
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
            @click.stop="toggleMinimized"
            class="text-text-muted hover:text-text-light p-1"
            :title="isMinimized ? 'Restore' : 'Minimize'"
          >
            <FontAwesomeIcon :icon="isMinimized ? faChevronUp : faMinus" />
          </button>
        </div>
      </div>

      <!-- Detailed List (animated expand/collapse) -->
      <Transition
        name="fade-slide"
        enter-active-class="transition-all duration-300 ease-in-out"
        leave-active-class="transition-all duration-300 ease-in-out"
        enter-from-class="opacity-0 max-h-0 scale-y-95"
        enter-to-class="opacity-100 max-h-[1000px] scale-y-100"
        leave-from-class="opacity-100 max-h-[1000px] scale-y-100"
        leave-to-class="opacity-0 max-h-0 scale-y-95"
      >
        <div v-if="!isMinimized" class="border-t border-border overflow-hidden">
          <div
            v-for="installation in downloadProgress"
            :key="installation.model_id"
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
                    installation.status === DownloadStatus.DOWNLOADING
                      ? 'animate-spin'
                      : '',
                  ]"
                />
                <span
                  class="font-medium text-text-light text-sm truncate max-w-[200px]"
                  :title="installation.model_id"
                >
                  {{ installation.model_id }}
                </span>
              </div>
              <button
                @click="handleRemove(installation)"
                class="text-text-muted hover:text-text-light text-sm"
                v-if="
                  installation.status === DownloadStatus.DONE ||
                  installation.status === DownloadStatus.ERROR ||
                  installation.status === DownloadStatus.STOPPED
                "
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
              <div class="w-full bg-background-mute rounded-full h-1.5">
                <div
                  class="h-1.5 rounded-full transition-all duration-300"
                  :class="{
                    'bg-blue-500':
                      installation.status === DownloadStatus.DOWNLOADING,
                    'bg-green-500': installation.status === DownloadStatus.DONE,
                    'bg-orange-500':
                      installation.status === DownloadStatus.STOPPED,
                    'bg-red-500': installation.status === DownloadStatus.ERROR,
                  }"
                  :style="{ width: `${installation.progress}%` }"
                ></div>
              </div>
            </div>

            <!-- Current Step -->
            <div class="text-xs text-text-muted mb-2 truncate">
              {{ installation.progress }}%
            </div>

            <!-- Time and Actions -->
            <div
              class="flex justify-between items-center text-xs text-text-muted"
            >
              <span>{{ formatElapsedTime(installation.start_time!) }}</span>
              <button
                v-if="installation.status === DownloadStatus.DOWNLOADING"
                @click="handleCancel(installation)"
                class="text-red-500 text-xs px-2 py-1 border border-red-500 rounded hover:bg-red-500 hover:text-white transition-colors"
              >
                Cancel
              </button>
            </div>

            <!-- Errors -->
            <div v-if="installation.error" class="mt-2">
              <div class="text-xs text-red-400">
                <div class="mb-1">
                  {{ installation.error }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>
<script setup lang="ts">
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import {
  faDownload,
  faCheckCircle,
  faExclamationCircle,
  faTimes,
  faSpinner,
  faChevronUp,
  faMinus,
} from "@fortawesome/free-solid-svg-icons";
import { useModelsStore } from "../stores/models";
import { DownloadProgress, DownloadStatus } from "../stores/types/models.types";
import { storeToRefs } from "pinia";
import { onMounted, ref, computed } from "vue";

const modelsStore = useModelsStore();
const { downloadProgress } = storeToRefs(modelsStore);

// État pour gérer l'expansion/réduction de la popup
const isMinimized = ref<boolean>(false);

// Interface pour le résumé des téléchargements
interface DownloadsSummary {
  total: number;
  downloading: number;
  completed: number;
  cancelled: number;
  errors: number;
}

// Computed pour le résumé des téléchargements
const downloadsSummary = computed<DownloadsSummary>(() => {
  const total = downloadProgress.value.length;
  const downloading = downloadProgress.value.filter(
    (i) => i.status === DownloadStatus.DOWNLOADING
  ).length;
  const completed = downloadProgress.value.filter(
    (i) => i.status === DownloadStatus.DONE
  ).length;
  const cancelled = downloadProgress.value.filter(
    (i) => i.status === DownloadStatus.STOPPED
  ).length;
  const errors = downloadProgress.value.filter(
    (i) => i.status === DownloadStatus.ERROR
  ).length;

  return { total, downloading, completed, cancelled, errors };
});

const getStatusIcon = (status: DownloadStatus) => {
  switch (status) {
    case DownloadStatus.DOWNLOADING:
      return faSpinner;
    case DownloadStatus.DONE:
      return faCheckCircle;
    case DownloadStatus.STOPPED:
      return faTimes;
    case DownloadStatus.ERROR:
      return faExclamationCircle;
    default:
      return faSpinner;
  }
};

const getStatusColor = (status: DownloadStatus): string => {
  switch (status) {
    case DownloadStatus.DOWNLOADING:
      return "text-blue-500";
    case DownloadStatus.DONE:
      return "text-green-500";
    case DownloadStatus.STOPPED:
      return "text-orange-500";
    case DownloadStatus.ERROR:
      return "text-red-500";
    default:
      return "text-gray-500";
  }
};

const formatElapsedTime = (startTime: number): string => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
};

const toggleMinimized = (): void => {
  isMinimized.value = !isMinimized.value;
};

// Handle cancellation based on type
const handleCancel = async (installation: DownloadProgress): Promise<void> => {
  try {
    if (installation.status === DownloadStatus.DOWNLOADING) {
      await modelsStore.cancelModelDownload(installation.model_id);
    }
  } catch (error) {
    console.error("Error cancelling:", error);
  }
};

// Handle removal based on type
const handleRemove = (installation: DownloadProgress): void => {
  if (
    installation.status === DownloadStatus.DONE ||
    installation.status === DownloadStatus.ERROR
  ) {
    // Model download - use downloadId if available, otherwise bundleId
    modelsStore.removeProgressByModelId(installation.model_id);
  }
};

// Restore active downloads on component mount
onMounted(async (): Promise<void> => {
  await modelsStore.restoreActiveDownloads();
});
</script>
