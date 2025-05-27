<template>
  <div v-if="fileProps" class="bg-background-soft rounded-lg border border-border overflow-hidden">
    <table class="w-full">
      <tbody class="divide-y divide-border">
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-file mr-2"></i> Name
          </td>
          <td class="px-4 py-3">{{ fileProps.name }}</td>
        </tr>
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-folder mr-2"></i> Path
          </td>
          <td class="px-4 py-3 font-mono text-sm">{{ fileProps.path }}</td>
        </tr>
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-weight-hanging mr-2"></i> Size
          </td>
          <td class="px-4 py-3">{{ formatSize(fileProps.size) }}</td>
        </tr>
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-calendar-plus mr-2"></i> Created
          </td>
          <td class="px-4 py-3">{{ formatDate(fileProps.created) }}</td>
        </tr>
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-calendar-check mr-2"></i> Modified
          </td>
          <td class="px-4 py-3">{{ formatDate(fileProps.modified) }}</td>
        </tr>
        <tr class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-tag mr-2"></i> Type
          </td>
          <td class="px-4 py-3">
            <span v-if="fileProps.is_dir" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Directory
            </span>
            <span v-else-if="fileProps.is_file" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              File
            </span>
          </td>
        </tr>
        <tr v-if="selectedFile && selectedFile.source_url" class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-link mr-2"></i> Source
          </td>
          <td class="px-4 py-3">
            <a
              :href="selectedFile.source_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-primary hover:text-primary/80 inline-flex items-center"
              title="Open this link in a new tab"
            >
              {{ shortenUrl(selectedFile.source_url) }}
              <i class="fas fa-external-link-alt ml-1 text-xs"></i>
            </a>
          </td>
        </tr>
        <tr v-if="selectedFile && selectedFile.is_corrupted" class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-exclamation-triangle mr-2"></i> Corruption Info
          </td>
          <td class="px-4 py-3">
            <div class="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
              <strong>Warning:</strong> This file may be corrupted. The file size does not match what is expected in models.json.
              <div class="mt-2 text-sm">
                <div><strong>Expected size:</strong> {{ formatSize(selectedFile.expected_size) }}</div>
                <div><strong>Actual size:</strong> {{ formatSize(selectedFile.actual_size) }}</div>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="showAddToJsonButton" class="hover:bg-background">
          <td class="px-4 py-3 font-medium text-text-light">
            <i class="fas fa-plus-circle mr-2"></i> Actions
          </td>
          <td class="px-4 py-3">
            <button 
              @click="openAddToJsonModal" 
              class="btn btn-sm btn-primary"
              title="Add this model to models.json"
            >
              <i class="fas fa-file-import mr-1"></i> Add to models.json
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <!-- Add to JSON Modal -->
  <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeModal"></div>
    <div class="relative bg-background rounded-lg border border-border shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-border">
        <h4 class="text-lg font-semibold flex items-center">
          <i class="fas fa-plus mr-2"></i>
          Add Model to models.json
        </h4>
        <button type="button" class="absolute top-4 right-4 text-text-muted hover:text-text-light" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="p-6">
        <ModelFormComponent 
          v-model:formData="modelData"
          :groups="modelGroups"
          :is-submitting="isSubmitting"
          :error="submitError"
          @submit="submitModelData"
          @cancel="closeModal"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNotifications } from '../../composables/useNotifications'
import api from '../../services/api'
import ModelFormComponent from './ModelFormComponent.vue'

const props = defineProps({
  fileProps: Object,
  selectedFile: Object,
})

// Notifications
const { success, error } = useNotifications()

// Modal state
const isModalOpen = ref(false)
const isSubmitting = ref(false)
const submitError = ref('')
const modelGroups = ref([])

const modelData = ref({
  group: '',
  entry: {
    url: '',
    dest: '',
    src: '',
    type: '',
    tags: [],
    size: 0
  }
})

// Computed properties
const showAddToJsonButton = computed(() => {
  if (!props.fileProps || !props.fileProps.is_file) return false
  if (!props.fileProps.name.toLowerCase().endsWith('.safetensors')) return false
  return !(props.selectedFile && props.selectedFile.is_registered)
})

// Helper functions
function formatSize(size) {
  if (typeof size !== 'number') return size
  if (size >= 1e9) return (size / 1e9).toFixed(2) + ' GB'
  if (size >= 1e6) return (size / 1e6).toFixed(2) + ' MB'
  if (size >= 1e3) return (size / 1e3).toFixed(2) + ' KB'
  return size + ' B'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

function shortenUrl(url) {
  if (!url) return ""
  try {
    const urlObj = new URL(url)
    if (urlObj.hostname.includes("civitai.com")) return "Civitai"
    if (urlObj.hostname.includes("huggingface.co")) return "Hugging Face"
    if (urlObj.hostname.includes("github.com")) return "GitHub"
    return urlObj.hostname
  } catch (e) {
    return url.length > 30 ? url.substring(0, 27) + "..." : url
  }
}

// Modal functions
const fetchGroups = async () => {
  try {
    const response = await api.get('/jsonmodels/groups')
    modelGroups.value = response.data
  } catch (error) {
    console.error('Error fetching model groups:', error)
    submitError.value = 'Failed to load model groups. Please try again.'
  }
}

const openAddToJsonModal = async () => {
  submitError.value = ''
  
  // Initialize form data
  modelData.value = {
    group: '',
    entry: {
      url: '',
      dest: props.fileProps.path,
      src: '',
      type: '',
      tags: [],
      size: props.fileProps.size
    }
  }
  
  // Infer model type from path
  const path = props.fileProps.path.toLowerCase()
  if (path.includes('/lora/')) {
    modelData.value.entry.type = 'lora'
  } else if (path.includes('/lycoris/')) {
    modelData.value.entry.type = 'lycoris'
  } else if (path.includes('/vae/')) {
    modelData.value.entry.type = 'vae'
  } else if (path.includes('/embeddings/') || path.includes('/textual_inversion/')) {
    modelData.value.entry.type = 'textual-inversion'
  } else if (path.includes('/checkpoint/') || path.includes('/model/')) {
    modelData.value.entry.type = 'checkpoint'
  } else if (path.includes('/controlnet/')) {
    modelData.value.entry.type = 'controlnet'
  } else if (path.includes('/upscaler/')) {
    modelData.value.entry.type = 'upscaler'
  } else if (path.includes('/hypernetwork/')) {
    modelData.value.entry.type = 'hypernetwork'
  }
  
  await fetchGroups()
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const submitModelData = async () => {
  isSubmitting.value = true
  submitError.value = ''
  
  try {
    const response = await api.post('/jsonmodels/entry', modelData.value)
    closeModal()
    
    // Show persistent success notification
    success('Model successfully added to models.json', 5000, true)
    
    // Emit event to notify parent components
    const event = new CustomEvent('models-json-updated')
    document.dispatchEvent(event)
  } catch (err) {
    console.error('Error adding model to models.json:', err)
    const errorMessage = err.response?.data?.detail || 'Failed to add model. Please try again.'
    submitError.value = errorMessage
    
    // Show persistent error notification
    error(`Failed to add model: ${errorMessage}`, 8000, true)
  } finally {
    isSubmitting.value = false
  }
}
</script>
