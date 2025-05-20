<template>
  <table v-if="fileProps" class="table table-striped table-bordered">
    <tbody>
      <tr>
        <td><i class="fa-solid fa-file"></i> <strong>Name</strong></td>
        <td>{{ fileProps.name }}</td>
      </tr>
      <tr>
        <td><i class="fa-solid fa-folder"></i> <strong>Path</strong></td>
        <td>{{ fileProps.path }}</td>
      </tr>
      <tr>
        <td>
          <i class="fa-solid fa-weight-hanging"></i> <strong>Size</strong>
        </td>
        <td>{{ formatSize(fileProps.size) }}</td>
      </tr>
      <tr>
        <td>
          <i class="fa-solid fa-calendar-plus"></i> <strong>Created</strong>
        </td>
        <td>{{ formatDate(fileProps.created) }}</td>
      </tr>
      <tr>
        <td>
          <i class="fa-solid fa-calendar-check"></i> <strong>Modified</strong>
        </td>
        <td>{{ formatDate(fileProps.modified) }}</td>
      </tr>
      <tr>
        <td><i class="fa-solid fa-tag"></i> <strong>Type</strong></td>
        <td>
          <span v-if="fileProps.is_dir">Directory</span>
          <span v-else-if="fileProps.is_file">File</span>
        </td>
      </tr>
      <tr v-if="selectedFile && selectedFile.source_url">
        <td><i class="fa-solid fa-link"></i> <strong>Source</strong></td>
        <td>
          <a
            :href="selectedFile.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="source-link"
            v-tooltip="'Open this link in a new tab'"
          >
            {{ shortenUrl(selectedFile.source_url) }}
            <i class="fa-solid fa-external-link-alt ms-1"></i>
          </a>
        </td>
      </tr>
      <tr v-if="selectedFile && selectedFile.is_corrupted">
        <td>
          <i class="fa-solid fa-exclamation-triangle"></i>
          <strong>Corruption Info</strong>
        </td>
        <td>
          <div class="alert alert-warning mb-0">
            <strong>Warning:</strong> This file may be corrupted. The file size
            does not match what is expected in models.json.
            <div class="mt-1">
              <div>
                <strong>Expected size:</strong>
                {{ formatSize(selectedFile.expected_size) }}
              </div>
              <div>
                <strong>Actual size:</strong>
                {{ formatSize(selectedFile.actual_size) }}
              </div>
            </div>
          </div>
        </td>
      </tr>
      
      <!-- Add to JSON Button Row -->
      <tr v-if="showAddToJsonButton">
        <td>
          <i class="fa-solid fa-plus-circle"></i>
          <strong>Actions</strong>
        </td>
        <td>
          <button 
            @click="openAddToJsonModal" 
            class="btn btn-sm btn-primary"
            v-tooltip="'Add this model to models.json'"
          >
            <i class="fa-solid fa-file-import me-1"></i> Add to models.json
          </button>
        </td>
      </tr>
    </tbody>
  </table>
  
  <!-- Add to JSON Modal -->
  <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h4 class="modal-title">
          <i class="fas" :class="modelData.entry.dest || modelData.entry.git ? 'fa-edit' : 'fa-plus'"></i>
          {{ modelData.entry.dest || modelData.entry.git ? ' Edit Model' : ' Add Model to models.json' }}
        </h4>
        <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <ModelForm 
          v-model:formData="modelData"
          :groups="modelGroups"
          :isSubmitting="isSubmitting"
          :error="submitError"
          @submit="submitModelData"
          @cancel="closeModal"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { apiFetch, fetchModels } from '../App.logic.js';
import ModelForm from './ModelForm.vue';

const props = defineProps({
  fileProps: Object,
  selectedFile: Object,
  formatSize: Function,
  formatDate: Function,
  shortenUrl: Function,
});

// State for modal and form
const isModalOpen = ref(false);
const isSubmitting = ref(false);
const submitError = ref('');
const modelGroups = ref([]);
const tagsInput = ref('');
const selectedModelType = ref('');
const customModelType = ref('');
const modelTypes = ref([
  'checkpoint',
  'lora',
  'lycoris',
  'hypernetwork',
  'textual-inversion',
  'upscaler',
  'vae',
  'controlnet',
  'other'
]);

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
});

// Computed property to determine if "Add to JSON" button should be visible
const showAddToJsonButton = computed(() => {
  if (!props.fileProps || !props.fileProps.is_file) return false;
  if (!props.fileProps.name.toLowerCase().endsWith('.safetensors')) return false;
  // Check if the model is already in models.json
  // This is done by checking if the selectedFile has information from models.json
  return !(props.selectedFile && props.selectedFile.is_registered);
});

// Fetch available groups when modal opens
const fetchGroups = async () => {
  try {
    // Use the existing apiFetch function that already handles authentication
    const response = await apiFetch('/jsonmodels/groups');
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    modelGroups.value = await response.json();
  } catch (error) {
    console.error('Error fetching model groups:', error);
    submitError.value = 'Failed to load model groups. Please try again.';
  }
};

// Open the modal and initialize data
const openAddToJsonModal = async () => {
  // Reset the form
  submitError.value = '';
  
  // Set initial values
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
  };
  
  // Try to infer model type from file path
  const path = props.fileProps.path.toLowerCase();
  if (path.includes('/lora/')) {
    modelData.value.entry.type = 'lora';
  } else if (path.includes('/lycoris/')) {
    modelData.value.entry.type = 'lycoris';
  } else if (path.includes('/vae/')) {
    modelData.value.entry.type = 'vae';
  } else if (path.includes('/embeddings/') || path.includes('/textual_inversion/')) {
    modelData.value.entry.type = 'textual-inversion';
  } else if (path.includes('/checkpoint/') || path.includes('/model/')) {
    modelData.value.entry.type = 'checkpoint';
  } else if (path.includes('/controlnet/')) {
    modelData.value.entry.type = 'controlnet';
  } else if (path.includes('/upscaler/')) {
    modelData.value.entry.type = 'upscaler';
  } else if (path.includes('/hypernetwork/')) {
    modelData.value.entry.type = 'hypernetwork';
  }
  
  // Fetch available groups
  await fetchGroups();
  
  // Show modal
  isModalOpen.value = true;
};

// Close the modal
const closeModal = () => {
  isModalOpen.value = false;
};

// Submit the form data to add the model to models.json
const submitModelData = async () => {
  isSubmitting.value = true;
  submitError.value = '';
  
  try {
    // Use the existing apiFetch function that already handles authentication
    const response = await apiFetch('/jsonmodels/entry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modelData.value)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || `HTTP error ${response.status}`);
    }
    
    // Close modal on success
    closeModal();
    
    // Refresh the models data
    await fetchModels();
    
    // Emit an event to notify parent components that models.json has been updated
    const event = new CustomEvent('models-json-updated');
    document.dispatchEvent(event);
  } catch (error) {
    console.error('Error adding model to models.json:', error);
    submitError.value = error.message || 'Failed to add model. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-content {
  /* Increased width for better readability */
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  /* Using Superhero theme colors */
  background-color: #2B3E50;
  color: #fff;
  border-radius: 6px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #4E5D6C;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: 1.5rem;
}

/* Form control styling to match Superhero theme */
.form-control, .form-select {
  background-color: #4E5D6C;
  border-color: #4E5D6C;
  color: #fff;
}

.form-control:focus, .form-select:focus {
  background-color: #5D6D7E;
  color: #fff;
  border-color: #5D6D7E;
  box-shadow: 0 0 0 0.25rem rgba(255, 255, 255, 0.25);
}

.form-control:read-only {
  background-color: #3E4D5C;
}

/* Form text helper styling */
.form-text {
  color: #aaa;
}

/* Button styling to match Superhero theme */
.btn-primary {
  background-color: #DF691A;
  border-color: #DF691A;
}

.btn-primary:hover, .btn-primary:focus {
  background-color: #B15315;
  border-color: #B15315;
}

.btn-secondary {
  background-color: #4E5D6C;
  border-color: #4E5D6C;
}

.btn-secondary:hover, .btn-secondary:focus {
  background-color: #3E4D5C;
  border-color: #3E4D5C;
}

/* Ensure the close button is visible */
.btn-close {
  filter: invert(1) grayscale(100%) brightness(200%);
}

/* Alert styling */
.alert-danger {
  background-color: #E74C3C;
  border-color: #E74C3C;
  color: #fff;
}

/* Table cell vertical alignment */
.table td {
  vertical-align: middle;
}
</style>
