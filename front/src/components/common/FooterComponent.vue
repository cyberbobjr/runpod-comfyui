<template>
  <footer class="bg-background-mute border-t border-border py-4 px-6 mt-8">
    <div class="flex justify-between items-center text-sm text-text-muted">
      <!-- Left side - App info -->
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <FontAwesomeIcon icon="cube" class="text-secondary" />
          <span class="font-medium">ComfyUI Model Manager</span>
        </div>
        <div class="flex items-center gap-1" v-if="versionInfo">
          <FontAwesomeIcon icon="tag" class="text-text-muted" />
          <span>{{ versionInfo.version }}</span>
          <span class="text-text-light-muted" v-if="showBuild && versionInfo.build">
            ({{ versionInfo.build }})
          </span>
        </div>
      </div>
      
      <!-- Right side - Additional info -->
      <div class="flex items-center gap-4">
        <div v-if="versionInfo?.buildDate && showBuildDate" class="flex items-center gap-1">
          <FontAwesomeIcon icon="calendar" class="text-text-muted" />
          <span>{{ formatBuildDate(versionInfo.buildDate) }}</span>
        </div>
        <button 
          @click="showVersionModal = true"
          class="flex items-center gap-1 hover:text-text-light transition-colors cursor-pointer"
          title="View detailed version information"
        >
          <FontAwesomeIcon icon="info-circle" />
          <span>About</span>
        </button>
      </div>
    </div>

    <!-- Version Details Modal -->
    <div v-if="showVersionModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div 
          class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          @click="showVersionModal = false"
        ></div>

        <!-- Modal content -->
        <div class="inline-block align-bottom bg-background rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border border-border">
          <div class="bg-background px-6 pt-6 pb-4">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <FontAwesomeIcon icon="cube" class="text-primary text-2xl" />
                <h3 class="text-xl font-bold text-heading">Version Information</h3>
              </div>
              <button 
                @click="showVersionModal = false"
                class="text-text-muted hover:text-text-light transition-colors"
              >
                <FontAwesomeIcon icon="times" class="text-xl" />
              </button>
            </div>

            <div v-if="versionInfo" class="space-y-4">
              <!-- Version -->
              <div class="flex justify-between items-center py-2 border-b border-border">
                <span class="text-text-muted">Version:</span>
                <span class="font-mono text-primary">v{{ versionInfo.version }}</span>
              </div>

              <!-- Build -->
              <div v-if="versionInfo.build" class="flex justify-between items-center py-2 border-b border-border">
                <span class="text-text-muted">Build:</span>
                <span class="font-mono text-text-light">{{ versionInfo.build }}</span>
              </div>

              <!-- Build Date -->
              <div v-if="versionInfo.buildDate" class="flex justify-between items-center py-2 border-b border-border">
                <span class="text-text-muted">Build Date:</span>
                <span class="text-text-light">{{ formatBuildDate(versionInfo.buildDate, true) }}</span>
              </div>

              <!-- Description -->
              <div v-if="versionInfo.description" class="py-2 border-b border-border">
                <span class="text-text-muted block mb-2">Description:</span>
                <span class="text-text-light">{{ versionInfo.description }}</span>
              </div>

              <!-- Components -->
              <div v-if="versionInfo.components" class="py-2">
                <span class="text-text-muted block mb-2">Components:</span>
                <div class="space-y-1">
                  <div 
                    v-for="(componentVersion, componentName) in versionInfo.components" 
                    :key="componentName"
                    class="flex justify-between items-center py-1 px-3 bg-background-soft rounded"
                  >
                    <span class="capitalize text-text-light">{{ componentName }}:</span>
                    <span class="font-mono text-secondary">v{{ componentVersion }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading state -->
            <div v-else class="flex items-center justify-center py-8">
              <FontAwesomeIcon icon="spinner" class="animate-spin text-secondary text-2xl" />
              <span class="ml-3 text-text-muted">Loading version information...</span>
            </div>
          </div>

          <div class="bg-background-mute px-6 py-3">
            <button
              @click="showVersionModal = false"
              class="btn btn-default w-full"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted, withDefaults } from 'vue'
import { fetchVersionInfo } from '../../utils/version'

/**
 * FooterComponent
 * -----------------------------------------------------------------------------
 * Application footer component showing version information and build details.
 * Displays app branding, version info, and provides a detailed version modal with comprehensive system information.
 *
 * ## Props
 * - `showBuild` (boolean, default: false): Whether to show the build number in the footer
 * - `showBuildDate` (boolean, default: false): Whether to show the build date in the footer
 *
 * ## Features & Behavior
 * - App name and branding display
 * - Version information with optional build details
 * - Detailed version modal with component breakdown
 * - Loading states for version data
 * - Responsive layout with proper spacing
 * - Dark theme integration
 * - FontAwesome icons for visual enhancement
 * - Auto-loads version information on component mount
 * - Graceful fallback to default version if API fails
 *
 * ## Methods
 * ### loadVersionInfo
 * **Description:** Load version information from the API with fallback to default values.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### formatBuildDate
 * **Description:** Format the build date for display with optional detailed format.
 * **Parameters:**
 * - `dateString` (string): ISO date string to format
 * - `detailed` (boolean, default: false): Whether to show detailed format with time
 * **Returns:** string - Formatted date string
 *
 * ## Usage Example
 * ```vue
 * <FooterComponent 
 *   :show-build="true" 
 *   :show-build-date="true" 
 * />
 * ```
 */

/**
 * Version info interface
 */
interface VersionInfo {
  version: string;
  build?: string;
  buildDate?: string;
  description?: string;
  components?: Record<string, string>;
}

/**
 * Component props interface
 */
interface Props {
  /** Whether to show the build number in the footer */
  showBuild?: boolean;
  /** Whether to show the build date in the footer */
  showBuildDate?: boolean;
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  showBuild: false,
  showBuildDate: false
})

// Reactive state
const versionInfo = ref<VersionInfo | null>(null)
const showVersionModal = ref<boolean>(false)
const loading = ref<boolean>(false)

/**
 * ### loadVersionInfo
 * **Description:** Load version information from the API with fallback to default values.
 */
const loadVersionInfo = async (): Promise<void> => {
  loading.value = true;
  try {
    versionInfo.value = await fetchVersionInfo();
  } catch (error) {
    console.error('Failed to load version info:', error);
    // Fallback to default version from utils
    versionInfo.value = {
      version: "2.0.0",
      build: "20250622-1430",
      description: "Configuration and Settings Management Refactoring"
    };
  } finally {
    loading.value = false;
  }
}

/**
 * ### formatBuildDate
 * **Description:** Format the build date for display with optional detailed format.
 * **Parameters:**
 * - `dateString` (string): ISO date string to format
 * - `detailed` (boolean, default: false): Whether to show detailed format with time
 * **Returns:** string - Formatted date string
 */
const formatBuildDate = (dateString: string, detailed: boolean = false): string => {
  if (!dateString) return 'Unknown';
  
  try {
    const date = new Date(dateString);
    if (detailed) {
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
      });
    } else {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  } catch (error) {
    return dateString;
  }
}

// Lifecycle hook
onMounted(async () => {
  await loadVersionInfo();
})
</script>

<style scoped>
/* Footer stays at bottom but doesn't use sticky positioning to avoid layout issues */
footer {
  margin-top: auto;
}
</style>
