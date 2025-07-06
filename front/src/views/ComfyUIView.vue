<template>
  <div class="comfyui-page h-full flex overflow-hidden">
    <!-- Left Panel - Generation Form -->
    <div
      class="generation-form-panel bg-background-mute border-r border-border transition-all duration-300 ease-in-out overflow-y-auto"
      :class="{ 'w-1/3': !isFormCollapsed, 'w-12': isFormCollapsed }"
    >
      <!-- Collapse Button -->
      <div class="flex justify-between items-center p-4 border-b border-border">
        <h2 v-if="!isFormCollapsed" class="text-lg font-semibold text-text-light">
          ComfyUI Generation
        </h2>
        <button
          @click="toggleFormCollapse"
          class="hover:bg-background-soft rounded-lg transition-colors"
          :title="isFormCollapsed ? 'Expand Form' : 'Collapse Form'"
        >
          <FontAwesomeIcon
            :icon="isFormCollapsed ? faChevronRight : faChevronLeft"
            class="text-text-muted"
          />
        </button>
      </div>

      <!-- Form Content -->
      <div v-if="!isFormCollapsed" class="p-4 space-y-6">
        <!-- Server Status -->
        <div class="mb-4">
          <div
            class="flex items-center gap-2 p-3 rounded-lg"
            :class="comfyStore.isServerAvailable ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
          >
            <FontAwesomeIcon
              :icon="comfyStore.isServerAvailable ? faCheckCircle : faTimesCircle"
            />
            <span class="text-sm font-medium">
              {{ comfyStore.isServerAvailable ? 'ComfyUI Server Online' : 'ComfyUI Server Offline' }}
            </span>
          </div>
        </div>

        <!-- Generation Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Model Selection -->
          <div>
            <label class="block text-sm font-medium text-text-light mb-2">
              Model
            </label>
            <FormDropdownComponent
              label="Select a model"
              :items="comfyStore.modelOptions"
              item-key="value"
              item-label="label"
              placeholder="No models available"
              :disabled="comfyStore.isGenerating"
              @select="(item) => formState.params.model_key = item.value"
            />
          </div>

          <!-- Prompt -->
          <div>
            <label class="block text-sm font-medium text-text-light mb-2">
              Prompt
            </label>
            <textarea
              v-model="formState.params.prompt"
              class="w-full p-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              rows="3"
              placeholder="Enter your prompt here..."
              :disabled="comfyStore.isGenerating"
            />
          </div>

          <!-- Negative Prompt -->
          <div>
            <label class="block text-sm font-medium text-text-light mb-2">
              Negative Prompt
            </label>
            <textarea
              v-model="formState.params.negative_prompt"
              class="w-full p-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              rows="2"
              placeholder="Enter negative prompt (optional)..."
              :disabled="comfyStore.isGenerating"
            />
          </div>

          <!-- Basic Parameters Accordion -->
          <AccordionComponent
            title="Basic Parameters"
            icon="sliders"
            :default-open="true"
          >
            <div class="space-y-4 p-4">
              <!-- Sampler -->
              <div>
                <label class="block text-sm font-medium text-text-light mb-2">
                  Sampler
                </label>
                <FormDropdownComponent
                  label="Select sampler"
                  :items="comfyStore.samplerOptions"
                  item-key="value"
                  item-label="label"
                  placeholder="No samplers available"
                  :disabled="comfyStore.isGenerating"
                  @select="(item) => formState.params.sampler = item.value"
                />
              </div>

              <!-- Steps -->
              <div>
                <label class="block text-sm font-medium text-text-light mb-2">
                  Steps: {{ formState.params.steps }}
                </label>
                <input
                  v-model.number="formState.params.steps"
                  type="range"
                  min="1"
                  max="100"
                  class="w-full accent-primary"
                  :disabled="comfyStore.isGenerating"
                />
              </div>

              <!-- CFG Scale -->
              <div>
                <label class="block text-sm font-medium text-text-light mb-2">
                  CFG Scale: {{ formState.params.cfg }}
                </label>
                <input
                  v-model.number="formState.params.cfg"
                  type="range"
                  min="1"
                  max="20"
                  step="0.1"
                  class="w-full accent-primary"
                  :disabled="comfyStore.isGenerating"
                />
              </div>

              <!-- Dimensions -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-text-light mb-2">
                    Width
                  </label>
                  <input
                    v-model.number="formState.params.width"
                    type="number"
                    min="256"
                    max="2048"
                    step="64"
                    class="w-full p-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                    :disabled="comfyStore.isGenerating"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-text-light mb-2">
                    Height
                  </label>
                  <input
                    v-model.number="formState.params.height"
                    type="number"
                    min="256"
                    max="2048"
                    step="64"
                    class="w-full p-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                    :disabled="comfyStore.isGenerating"
                  />
                </div>
              </div>

              <!-- Seed -->
              <div>
                <label class="block text-sm font-medium text-text-light mb-2">
                  Seed (optional)
                </label>
                <input
                  v-model.number="formState.params.seed"
                  type="number"
                  class="w-full p-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="Random seed"
                  :disabled="comfyStore.isGenerating"
                />
              </div>
            </div>
          </AccordionComponent>

          <!-- Advanced Parameters Accordion -->
          <AccordionComponent
            title="Advanced Parameters"
            icon="cogs"
            :default-open="false"
          >
            <div class="space-y-4 p-4">
              <!-- Optimization Options -->
              <div class="space-y-2">
                <label class="flex items-center gap-2">
                  <input
                    v-model="formState.params.enable_tea_cache"
                    type="checkbox"
                    class="accent-primary"
                    :disabled="comfyStore.isGenerating"
                  />
                  <span class="text-sm text-text-light">Enable TeaCache</span>
                </label>
                <label class="flex items-center gap-2">
                  <input
                    v-model="formState.params.enable_clear_cache"
                    type="checkbox"
                    class="accent-primary"
                    :disabled="comfyStore.isGenerating"
                  />
                  <span class="text-sm text-text-light">Enable Clear Cache</span>
                </label>
                <label class="flex items-center gap-2">
                  <input
                    v-model="formState.params.add_details"
                    type="checkbox"
                    class="accent-primary"
                    :disabled="comfyStore.isGenerating"
                  />
                  <span class="text-sm text-text-light">Add Details</span>
                </label>
              </div>
            </div>
          </AccordionComponent>

          <!-- Generate Button -->
          <div class="pt-4">
            <button
              type="submit"
              class="w-full py-3 px-4 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!comfyStore.canGenerate || !formState.params.prompt || !formState.params.model_key"
            >
              <FontAwesomeIcon
                v-if="comfyStore.isGenerating"
                :icon="faSpinner"
                class="animate-spin mr-2"
              />
              {{ comfyStore.isGenerating ? 'Generating...' : 'Generate Image' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Right Panel - Preview and Results -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-border bg-background-mute">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-text-light">
            {{ comfyStore.generationProgress }}
          </h2>
          <div class="flex items-center gap-2">
            <button
              v-if="comfyStore.currentPromptId"
              @click="refreshResult"
              class="p-2 hover:bg-background-soft rounded-lg transition-colors"
              :disabled="comfyStore.loading"
              title="Refresh Result"
            >
              <FontAwesomeIcon
                :icon="faRefresh"
                class="text-text-muted"
                :class="{ 'animate-spin': comfyStore.loading }"
              />
            </button>
            <button
              v-if="comfyStore.finalImages.length > 0"
              @click="downloadImages"
              class="p-2 hover:bg-background-soft rounded-lg transition-colors"
              title="Download Images"
            >
              <FontAwesomeIcon :icon="faDownload" class="text-text-muted" />
            </button>
          </div>
        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 p-4 overflow-y-auto">
        <!-- Loading State -->
        <div
          v-if="comfyStore.loading && !comfyStore.isGenerating"
          class="flex items-center justify-center h-full"
        >
          <div class="text-center">
            <FontAwesomeIcon :icon="faSpinner" class="animate-spin text-4xl text-primary mb-4" />
            <p class="text-text-muted">Loading...</p>
          </div>
        </div>

        <!-- Error State -->
        <div
          v-else-if="comfyStore.error"
          class="flex items-center justify-center h-full"
        >
          <div class="text-center max-w-md">
            <FontAwesomeIcon :icon="faExclamationCircle" class="text-4xl text-danger mb-4" />
            <p class="text-text-light mb-2">Error</p>
            <p class="text-text-muted text-sm">{{ comfyStore.error }}</p>
            <button
              @click="comfyStore.clearError"
              class="mt-4 px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors"
            >
              Clear Error
            </button>
          </div>
        </div>

        <!-- Generation in Progress -->
        <div
          v-else-if="comfyStore.isGenerating"
          class="flex items-center justify-center h-full"
        >
          <div class="text-center max-w-md">
            <!-- Preview Image -->
            <div
              v-if="previewImage"
              class="mb-4 max-w-lg mx-auto"
            >
              <img
                :src="previewImage"
                alt="Preview"
                class="w-full h-auto rounded-lg shadow-lg"
              />
            </div>
            
            <!-- Generation Status -->
            <div class="flex items-center justify-center gap-2 mb-4">
              <FontAwesomeIcon :icon="faSpinner" class="animate-spin text-2xl text-primary" />
              <span class="text-text-light">
                {{ previewImage ? 'Generating final image...' : 'Initializing generation...' }}
              </span>
            </div>
            
            <!-- Progress Info -->
            <div class="text-sm text-text-muted">
              <p v-if="comfyStore.currentPromptId">
                Prompt ID: {{ comfyStore.currentPromptId }}
              </p>
            </div>
          </div>
        </div>

        <!-- Final Results -->
        <div
          v-else-if="comfyStore.finalImages.length > 0"
          class="space-y-4"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="(image, index) in comfyStore.finalImages"
              :key="index"
              class="relative group"
            >
              <img
                :src="image"
                :alt="`Generated image ${index + 1}`"
                class="w-full h-auto rounded-lg shadow-lg cursor-pointer transition-transform hover:scale-105"
                @click="openImageModal(image)"
              />
              <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click="downloadImage(image, index)"
                  class="p-2 bg-black/50 hover:bg-black/70 text-white rounded-lg transition-colors"
                  title="Download Image"
                >
                  <FontAwesomeIcon :icon="faDownload" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else
          class="flex items-center justify-center h-full"
        >
          <div class="text-center max-w-md">
            <FontAwesomeIcon :icon="faImage" class="text-4xl text-text-muted mb-4" />
            <p class="text-text-light mb-2">Ready to Generate</p>
            <p class="text-text-muted text-sm">
              Fill in the generation parameters and click "Generate Image" to create your artwork.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <CommonModal
      :show="!!selectedImage"
      @close="selectedImage = null"
    >
      <template #title>Generated Image</template>
      <div class="p-4">
        <img
          :src="selectedImage || ''"
          alt="Generated image"
          class="w-full h-auto rounded-lg"
        />
      </div>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faChevronRight,
  faChevronLeft,
  faCheckCircle,
  faTimesCircle,
  faSpinner,
  faRefresh,
  faDownload,
  faExclamationCircle,
  faImage
} from '@fortawesome/free-solid-svg-icons'
import { useComfyUIStore } from '@/stores/comfyui'
import { useComfySocket } from '@/composables/useComfySocket'
import type { GenerationParams, GenerationFormState } from '@/stores/types/comfyui.types'

// Components
import AccordionComponent from '@/components/common/AccordionComponent.vue'
import FormDropdownComponent from '@/components/common/FormDropdownComponent.vue'
import CommonModal from '@/components/common/CommonModal.vue'

// Stores
const comfyStore = useComfyUIStore()

// Reactive state
const isFormCollapsed = ref(false)
const selectedImage = ref<string | null>(null)

// Form state
const formState = reactive<GenerationFormState>({
  params: comfyStore.getDefaultParams(),
  errors: {},
  isValid: true,
  isSubmitting: false,
})

// Socket connection for real-time updates
const socketConnection = ref<{ previewImage: any; finalImage: any } | null>(null)

// Computed properties
const previewImage = computed(() => {
  return socketConnection.value?.previewImage?.value || comfyStore.previewImage
})

/**
 * Toggle form collapse state
 */
const toggleFormCollapse = () => {
  isFormCollapsed.value = !isFormCollapsed.value
}

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  if (!formState.params.prompt || !formState.params.model_key) {
    return
  }

  formState.isSubmitting = true
  
  try {
    // Set wait to false for real-time preview
    const params: GenerationParams = {
      ...formState.params,
      wait: false
    }
    
    const result = await comfyStore.generateAndExecute(params)
    
    // Set up socket connection for real-time updates
    if (result.prompt_id) {
      setupSocketConnection(result.prompt_id)
    }
    
  } catch (error) {
    console.error('Generation failed:', error)
  } finally {
    formState.isSubmitting = false
  }
}

/**
 * Setup socket connection for real-time updates
 */
const setupSocketConnection = (promptId: string) => {
  socketConnection.value = useComfySocket(promptId)
  
  // Watch for final image updates
  const checkFinalImage = () => {
    if (socketConnection.value?.finalImage?.value) {
      comfyStore.setFinalImages([socketConnection.value.finalImage.value])
      socketConnection.value = null
    }
  }
  
  const interval = setInterval(checkFinalImage, 1000)
  
  // Cleanup after 5 minutes
  setTimeout(() => {
    clearInterval(interval)
    socketConnection.value = null
  }, 300000)
}

/**
 * Refresh result from server
 */
const refreshResult = async () => {
  if (!comfyStore.currentPromptId) return
  
  try {
    await comfyStore.getResultByPromptId(comfyStore.currentPromptId)
  } catch (error) {
    console.error('Failed to refresh result:', error)
  }
}

/**
 * Download all images
 */
const downloadImages = () => {
  comfyStore.finalImages.forEach((image, index) => {
    downloadImage(image, index)
  })
}

/**
 * Download single image
 */
const downloadImage = (imageUrl: string, index: number) => {
  const link = document.createElement('a')
  link.href = imageUrl
  link.download = `generated_image_${index + 1}.png`
  link.click()
}

/**
 * Open image in modal
 */
const openImageModal = (imageUrl: string) => {
  selectedImage.value = imageUrl
}

/**
 * Reset form to defaults
 */
const resetForm = () => {
  formState.params = comfyStore.getDefaultParams()
  formState.errors = {}
  formState.isValid = true
}

// Lifecycle hooks
onMounted(async () => {
  await comfyStore.initialize()
  
  // Set first available model as default
  if (comfyStore.modelOptions.length > 0) {
    formState.params.model_key = comfyStore.modelOptions[0].value
  }
})

onUnmounted(() => {
  // Cleanup socket connection
  socketConnection.value = null
})
</script>

<style scoped>
.comfyui-page {
  min-height: 100vh;
}

.generation-form-panel {
  min-height: 100vh;
}

/* Custom scrollbar */
.generation-form-panel::-webkit-scrollbar {
  width: 4px;
}

.generation-form-panel::-webkit-scrollbar-track {
  background: transparent;
}

.generation-form-panel::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.generation-form-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
