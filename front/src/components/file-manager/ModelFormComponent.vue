<template>
  <form @submit.prevent="onSubmit" class="space-y-4">
    <div>
      <label for="group" class="block text-sm font-medium text-text-light mb-1">Group</label>
      <select 
        id="group" 
        v-model="formData.group" 
        class="form-select w-full" 
        required
      >
        <option value="" disabled>Select a group</option>
        <option v-for="group in groups" :key="group" :value="group">
          {{ group }}
        </option>
      </select>
    </div>
    
    <div>
      <label for="type" class="block text-sm font-medium text-text-light mb-1">Model Type</label>
      <div class="flex">
        <select 
          id="type" 
          v-model="selectedModelType" 
          class="form-select flex-1"
          :class="{ 'rounded-r-none': selectedModelType === 'custom' }"
          @change="handleTypeChange"
        >
          <option value="">-- Select Type (optional) --</option>
          <option v-for="type in modelTypes" :key="type" :value="type">
            {{ type }}
          </option>
          <option value="custom">Custom type...</option>
        </select>
        <input 
          v-if="selectedModelType === 'custom'" 
          type="text" 
          v-model="customModelType" 
          class="form-input flex-1 rounded-l-none border-l-0" 
          placeholder="Enter custom type"
          @input="updateCustomType"
        >
      </div>
      <p class="text-sm text-text-muted mt-1">Type of model (e.g., checkpoint, lora, textual inversion)</p>
    </div>
    
    <div>
      <label for="url" class="block text-sm font-medium text-text-light mb-1">Download URL</label>
      <input 
        type="url" 
        class="form-input w-full" 
        id="url" 
        v-model="formData.entry.url" 
        required
      >
      <p class="text-sm text-text-muted mt-1">Direct download link for the model</p>
    </div>
    
    <div>
      <label for="src" class="block text-sm font-medium text-text-light mb-1">Source Page</label>
      <input 
        type="url" 
        class="form-input w-full" 
        id="src" 
        v-model="formData.entry.src"
      >
      <p class="text-sm text-text-muted mt-1">Reference page where the model was found</p>
    </div>
    
    <div>
      <label for="tags" class="block text-sm font-medium text-text-light mb-1">Tags (comma separated)</label>
      <input 
        type="text" 
        class="form-input w-full" 
        id="tags" 
        v-model="localTags"
      >
      <p class="text-sm text-text-muted mt-1">e.g. stable-diffusion, lora, inpainting</p>
    </div>

    <div>
      <label for="dest" class="block text-sm font-medium text-text-light mb-1">Destination Path</label>
      <div class="flex items-center">
        <span class="bg-background-mute text-text-muted px-3 py-2 rounded-l border border-r-0 border-border text-sm">
          ${BASE_DIR}/
        </span>
        <input 
          type="text" 
          id="dest"
          class="form-input flex-1 rounded-l-none border-l-0" 
          v-model="localDestPath"
          @input="updateDestPath"
          placeholder="category/model.safetensors"
        >
      </div>
      <p class="text-sm text-text-muted mt-1">Path relative to the base directory where the model will be stored.</p>
    </div>
    
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {{ error }}
    </div>
    
    <div class="flex justify-end space-x-3 pt-4">
      <button type="button" class="btn btn-secondary" @click="onCancel">
        <i class="fas fa-times mr-1"></i> Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
        <i class="fas" :class="formData.entry.dest || formData.entry.git ? 'fa-save' : 'fa-plus'"></i>
        {{ formData.entry.dest || formData.entry.git ? ' Update' : ' Add' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  formData: {
    type: Object,
    required: true
  },
  groups: {
    type: Array,
    default: () => []
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['submit', 'cancel', 'update:formData'])

const localTags = ref('')
const selectedModelType = ref('')
const customModelType = ref('')
const localDestPath = ref('')

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
])

// Initialize form data
onMounted(() => {
  if (props.formData?.entry?.tags?.length) {
    if (Array.isArray(props.formData.entry.tags)) {
      localTags.value = props.formData.entry.tags.join(', ')
    } else {
      localTags.value = props.formData.entry.tags
    }
  }

  if (props.formData?.entry?.type) {
    if (modelTypes.value.includes(props.formData.entry.type)) {
      selectedModelType.value = props.formData.entry.type
    } else if (props.formData.entry.type) {
      selectedModelType.value = 'custom'
      customModelType.value = props.formData.entry.type
    }
  }

  // Initialize destination path without ${BASE_DIR} prefix
  if (props.formData?.entry?.dest) {
    localDestPath.value = props.formData.entry.dest.replace(/^\$\{BASE_DIR\}\//, '')
  }
})

// Handle type changes
const handleTypeChange = () => {
  if (selectedModelType.value === 'custom') {
    updateFormData('type', customModelType.value)
  } else {
    updateFormData('type', selectedModelType.value)
  }
}

const updateCustomType = () => {
  updateFormData('type', customModelType.value)
}

// Update destination path with ${BASE_DIR} prefix
const updateDestPath = () => {
  const fullPath = localDestPath.value ? `\${BASE_DIR}/${localDestPath.value}` : ''
  updateFormData('dest', fullPath)
}

// Form actions
const onSubmit = () => {
  emit('submit')
}

const onCancel = () => {
  emit('cancel')
}

// Update form data when tags change
watch(localTags, (newValue) => {
  if (!newValue) {
    updateFormData('tags', [])
    return
  }
  
  const tagsArray = newValue
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0)
  
  updateFormData('tags', tagsArray)
})

// Helper to update form data
const updateFormData = (field, value) => {
  const updatedFormData = { ...props.formData }
  if (!updatedFormData.entry) {
    updatedFormData.entry = {}
  }
  updatedFormData.entry = { ...updatedFormData.entry, [field]: value }
  emit('update:formData', updatedFormData)
}
</script>
