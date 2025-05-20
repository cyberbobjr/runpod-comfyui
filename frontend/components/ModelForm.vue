<template>
  <form @submit.prevent="onSubmit">
    <div class="mb-3">
      <label for="group" class="form-label">Group</label>
      <select id="group" v-model="formData.group" class="form-select" required>
        <option value="" disabled>Select a group</option>
        <option v-for="group in groups" :key="group" :value="group">
          {{ group }}
        </option>
      </select>
    </div>
    
    <div class="mb-3">
      <label for="type" class="form-label">Model Type</label>
      <div class="input-group">
        <select 
          id="type" 
          v-model="selectedModelType" 
          class="form-select" 
          :class="{ 'rounded-end': selectedModelType !== 'custom' }"
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
          class="form-control" 
          placeholder="Enter custom type"
          @input="updateCustomType"
        >
      </div>
      <div class="form-text">Type of model (e.g., checkpoint, lora, textual inversion)</div>
    </div>
    
    <div class="mb-3">
      <label for="url" class="form-label">Download URL</label>
      <input type="url" class="form-control" id="url" v-model="formData.entry.url" required>
      <div class="form-text">Direct download link for the model</div>
    </div>
    
    <div class="mb-3">
      <label for="src" class="form-label">Source Page</label>
      <input type="url" class="form-control" id="src" v-model="formData.entry.src">
      <div class="form-text">Reference page where the model was found</div>
    </div>
    
    <div class="mb-3">
      <label for="tags" class="form-label">Tags (comma separated)</label>
      <input type="text" class="form-control" id="tags" v-model="localTags">
      <div class="form-text">e.g. stable-diffusion, lora, inpainting</div>
    </div>

    <div class="mb-3">
      <label for="dest" class="form-label">Destination Path</label>
      <input 
        type="text" 
        id="dest"
        class="form-control" 
        v-model="formData.entry.dest"
        placeholder="${BASE_DIR}/category/model.safetensors"
      >
      <div class="form-text">Path where the model will be stored. Use ${BASE_DIR} to reference the base directory.</div>
    </div>
    
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
    
    <div class="mt-4 d-flex justify-content-end">
      <button type="button" class="btn btn-secondary me-2" @click="onCancel">
        <i class="fas fa-times me-1"></i> Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
        <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        <i class="fas" :class="formData.entry.dest || formData.entry.git ? 'fa-save' : 'fa-plus'"></i>
        {{ formData.entry.dest || formData.entry.git ? ' Update' : ' Add' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

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
});

const emit = defineEmits(['submit', 'cancel', 'update:formData']);

const localTags = ref('');
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

// Initialize local tags from formData
onMounted(() => {
  if (props.formData?.entry?.tags?.length) {
    if (Array.isArray(props.formData.entry.tags)) {
      localTags.value = props.formData.entry.tags.join(', ');
    } else {
      localTags.value = props.formData.entry.tags;
    }
  }

  // Initialize selected model type
  if (props.formData?.entry?.type) {
    if (modelTypes.value.includes(props.formData.entry.type)) {
      selectedModelType.value = props.formData.entry.type;
    } else if (props.formData.entry.type) {
      selectedModelType.value = 'custom';
      customModelType.value = props.formData.entry.type;
    }
  }
});

// Handle type dropdown change
const handleTypeChange = () => {
  if (selectedModelType.value === 'custom') {
    updateFormData('type', customModelType.value);
  } else {
    updateFormData('type', selectedModelType.value);
  }
};

// Update entry type when custom type changes
const updateCustomType = () => {
  updateFormData('type', customModelType.value);
};

// Handle form actions
const onSubmit = () => {
  emit('submit');
};

const onCancel = () => {
  emit('cancel');
};

// Update form data when tags change
watch(localTags, (newValue) => {
  if (!newValue) {
    updateFormData('tags', []);
    return;
  }
  
  const tagsArray = newValue
    .split(',')
    .map(tag => tag.trim())
    .filter(tag => tag.length > 0);
  
  updateFormData('tags', tagsArray);
});

// Helper to update the form data model
const updateFormData = (field, value) => {
  const updatedFormData = { ...props.formData };
  if (!updatedFormData.entry) {
    updatedFormData.entry = {};
  }
  updatedFormData.entry = { ...updatedFormData.entry, [field]: value };
  emit('update:formData', updatedFormData);
};
</script>
