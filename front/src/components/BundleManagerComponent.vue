<template>
  <div class="space-y-6 p-4 bg-background">
    <!-- Bundle List Card -->
    <div class="card">
      <h2 class="text-xl font-semibold text-text-light mb-4">Bundle Manager</h2>
      
      <div class="mb-6">
        <h4 class="text-lg font-medium text-text-light mb-2 flex items-center">
          <FontAwesomeIcon icon="box-open" class="mr-2" />Model Bundles
        </h4>
        <p class="text-text-muted mb-4 flex items-center">
          <FontAwesomeIcon icon="info-circle" class="mr-2" />Create predefined bundles of models with associated workflows.
        </p>
        
        <!-- Bundle List -->
        <div v-if="Object.keys(bundles).length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-border">
            <thead class="bg-background-mute">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="tag" class="mr-1" />Name
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="code-branch" class="mr-1" />Version
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="user" class="mr-1" />Author
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="info" class="mr-1" />Description
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="sitemap" class="mr-1" />Workflows
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="server" class="mr-1" />Hardware Profiles
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                  <FontAwesomeIcon icon="cogs" class="mr-1" />Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-background-soft divide-y divide-border">
              <tr v-for="bundle in bundles" :key="bundle.id" class="hover:bg-background-mute">
                <td class="px-4 py-3 text-text-light">{{ bundle.name }}</td>
                <td class="px-4 py-3 text-text-light">{{ bundle.version || '1.0.0' }}</td>
                <td class="px-4 py-3 text-text-light">{{ bundle.author || 'N/A' }}</td>
                <td class="px-4 py-3 text-text-light">{{ bundle.description }}</td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="workflow in bundle.workflows || []" 
                      :key="workflow" 
                      class="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-600 text-white"
                    >
                      <FontAwesomeIcon icon="file-code" class="mr-1" />{{ workflow }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="(profile, profileName) in bundle.hardware_profiles || {}" 
                      :key="profileName" 
                      class="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-600 text-white"
                    >
                      <FontAwesomeIcon icon="microchip" class="mr-1" />{{ profileName }} ({{ profile.models?.length || 0 }} models)
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex space-x-1">
                    <button 
                      class="px-3 py-1 text-xs bg-btn-default text-white rounded hover:bg-btn-default-hover transition-colors"
                      @click="editBundle(bundle.id)"
                    >
                      <FontAwesomeIcon icon="edit" class="mr-1" />Edit
                    </button>
                    <button 
                      class="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                      @click="handleDeleteBundle(bundle.id)"
                    >
                      <FontAwesomeIcon icon="trash-alt" class="mr-1" />Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded flex items-start">
          <FontAwesomeIcon icon="info-circle" class="mr-2 mt-0.5" />
          <span>No bundles available. Create your first bundle below.</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Bundle Card -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-text-light flex items-center">
          <FontAwesomeIcon :icon="currentBundle.id ? 'edit' : 'plus-circle'" class="mr-2" />
          {{ currentBundle.id ? 'Edit Bundle' : 'Create New Bundle' }}
        </h3>
        <button 
          v-if="currentBundle.id"
          type="button" 
          class="btn btn-outline"
          @click="createNewBundle"
        >
          <FontAwesomeIcon icon="plus-circle" class="mr-1" />New Bundle
        </button>
      </div>
      
      <form @submit.prevent="handleSaveBundle" class="space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label flex items-center">
              <FontAwesomeIcon icon="tag" class="mr-2" />Name
            </label>
            <input 
              type="text" 
              class="form-input w-full" 
              v-model="currentBundle.name"
              required
            />
          </div>
          <div>
            <label class="form-label flex items-center">
              <FontAwesomeIcon icon="code-branch" class="mr-2" />Version
            </label>
            <input 
              type="text" 
              class="form-input w-full" 
              v-model="currentBundle.version"
              placeholder="1.0.0"
              pattern="^\d+\.\d+\.\d+$"
              title="Version must be in x.y.z format (e.g., 1.0.0)"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="form-label flex items-center">
              <FontAwesomeIcon icon="user" class="mr-2" />Author
            </label>
            <input 
              type="text" 
              class="form-input w-full" 
              v-model="currentBundle.author"
              placeholder="Bundle author"
            />
          </div>
          <div>
            <label class="form-label flex items-center">
              <FontAwesomeIcon icon="globe" class="mr-2" />Website
            </label>
            <input 
              type="url" 
              class="form-input w-full" 
              v-model="currentBundle.website"
              placeholder="https://example.com"
            />
          </div>
        </div>

        <div>
          <label class="form-label flex items-center">
            <FontAwesomeIcon icon="info-circle" class="mr-2" />Description
          </label>
          <textarea 
            class="form-input w-full" 
            v-model="currentBundle.description"
            rows="3"
          ></textarea>
        </div>

        <!-- Workflow Selection -->
        <div>
          <label class="form-label flex items-center">
            <FontAwesomeIcon icon="sitemap" class="mr-2" />Workflows
          </label>
          
          <!-- Selected Workflows Display -->
          <div class="bg-background-soft border border-border rounded-lg p-3 min-h-[60px] mb-2">
            <div v-if="currentBundle.workflows.length > 0" class="flex flex-wrap gap-2">
              <span 
                v-for="workflow in currentBundle.workflows" 
                :key="workflow" 
                class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-600 text-white group"
              >
                <FontAwesomeIcon icon="file-code" class="mr-1" />{{ workflow }}
                <button 
                  type="button" 
                  class="ml-2 w-4 h-4 flex items-center justify-center rounded-full bg-blue-500 hover:bg-red-500 text-white text-xs transition-colors duration-200 flex-shrink-0"
                  @click.stop="removeWorkflowFromSelection(workflow)"
                  title="Remove workflow"
                >
                  <FontAwesomeIcon icon="times" />
                </button>
              </span>
            </div>
            <div v-else class="text-text-muted text-sm flex items-center">
              <FontAwesomeIcon icon="info-circle" class="mr-1" />No workflows selected. Choose from the dropdown below.
            </div>
          </div>
          
          <!-- Workflow Dropdown -->
          <div class="relative">
            <button 
              type="button"
              class="form-input w-full text-left flex items-center justify-between"
              @click="showWorkflowDropdown = !showWorkflowDropdown"
            >
              <span class="flex items-center">
                <FontAwesomeIcon icon="plus-circle" class="mr-2" />Add Workflows
              </span>
              <FontAwesomeIcon :icon="showWorkflowDropdown ? 'chevron-up' : 'chevron-down'" />
            </button>
            
            <div 
              v-if="showWorkflowDropdown" 
              class="absolute z-10 w-full mt-1 bg-background-soft border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div v-if="availableWorkflows.length > 0" class="p-2">
                <div 
                  v-for="workflow in availableWorkflows" 
                  :key="workflow"
                  class="flex items-center px-3 py-2 hover:bg-background-mute cursor-pointer rounded"
                  @click="addWorkflowToSelection(workflow)"
                >
                  <FontAwesomeIcon icon="file-code" class="mr-2 text-blue-600" />
                  <span>{{ workflow }}</span>
                </div>
              </div>
              <div v-else class="p-4 text-text-muted text-center">
                <FontAwesomeIcon icon="info-circle" class="mr-1" />All workflows are already selected
              </div>
            </div>
          </div>
          
          <!-- Missing Workflows -->
          <div v-if="missingWorkflows.length > 0" class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div class="text-yellow-600 mb-2 flex items-center">
              <FontAwesomeIcon icon="exclamation-triangle" class="mr-1" />
              <strong>Missing workflows:</strong> 
              <span class="ml-1 text-sm">These workflows are referenced in this bundle but are not available in the system.</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="workflow in missingWorkflows" 
                :key="workflow" 
                class="inline-flex items-center px-2 py-1 rounded text-xs bg-yellow-100 text-yellow-800 group"
              >
                <FontAwesomeIcon icon="file-code" class="mr-1" />{{ workflow }}
                <button 
                  type="button" 
                  class="ml-2 w-4 h-4 flex items-center justify-center rounded-full bg-yellow-400 hover:bg-red-500 text-yellow-800 hover:text-white text-xs transition-colors duration-200 flex-shrink-0"
                  @click.stop="removeWorkflowFromBundle(workflow)"
                  title="Remove missing workflow"
                >
                  <FontAwesomeIcon icon="times" />
                </button>
              </span>
            </div>
          </div>
          
          <!-- Upload New Workflow -->
          <div class="mt-3 flex">
            <input 
              type="file" 
              class="form-input flex-1 rounded-r-none" 
              id="workflow-file"
              @change="handleWorkflowUpload"
              accept=".json"
            />
            <button 
              class="btn btn-outline rounded-l-none border-l-0" 
              type="button" 
              @click="triggerWorkflowUpload"
            >
              <FontAwesomeIcon icon="upload" class="mr-1" />Upload New Workflow
            </button>
          </div>
        </div>
        
        <!-- Hardware Profiles -->
        <div>
          <div class="flex justify-between items-center mb-4">
            <label class="form-label flex items-center mb-0">
              <FontAwesomeIcon icon="server" class="mr-2" />Hardware Profiles
            </label>
            <button 
              type="button" 
              class="btn btn-sm btn-primary"
              @click="addHardwareProfile"
            >
              <FontAwesomeIcon icon="plus-circle" class="mr-1" />Add Profile
            </button>
          </div>
          
          <div class="space-y-4">
            <div 
              v-for="(profile, name) in currentBundle.hardware_profiles" 
              :key="name" 
              class="border border-border rounded-lg overflow-hidden"
            >
              <div class="bg-background-mute px-4 py-3 flex justify-between items-center">
                <div class="flex items-center flex-1 mr-4">
                  <FontAwesomeIcon icon="microchip" class="mr-2 text-text-light" />
                  <div class="flex-1 flex items-center">
                    <input 
                      type="text" 
                      class="bg-transparent border-none text-text-light font-medium focus:outline-none focus:bg-background focus:border focus:border-border focus:rounded px-2 py-1 flex-1"
                      :value="name"
                      @blur="updateProfileName(name, $event.target.value)"
                      @keyup.enter="$event.target.blur()"
                      @keyup.escape="$event.target.value = name; $event.target.blur()"
                      placeholder="Profile name"
                    />
                    <span class="ml-2 text-sm text-text-muted">({{ profile.models?.length || 0 }} models)</span>
                  </div>
                </div>
                <button 
                  type="button" 
                  class="btn btn-sm bg-red-600 hover:bg-red-700 text-white"
                  @click="removeHardwareProfile(name)"
                >
                  <FontAwesomeIcon icon="trash-alt" class="mr-1" />Remove
                </button>
              </div>
              <div class="p-4 space-y-4">
                <div>
                  <label class="form-label flex items-center">
                    <FontAwesomeIcon icon="info" class="mr-2" />Description
                  </label>
                  <input 
                    type="text" 
                    class="form-input w-full" 
                    v-model="profile.description"
                    placeholder="Profile description"
                  />
                </div>
                
                <!-- Model Selection for this Profile -->
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <label class="form-label flex items-center mb-0">
                      <FontAwesomeIcon icon="cubes" class="mr-2" />Models for this Profile
                    </label>
                    <button 
                      type="button" 
                      class="btn btn-sm btn-outline"
                      @click="showModelSelector(name)"
                    >
                      <FontAwesomeIcon icon="plus-circle" class="mr-1" />Add Models
                    </button>
                  </div>
                  
                  <!-- Selected Models Display -->
                  <div class="bg-background-soft border border-border rounded-lg p-3 min-h-[60px] mb-2">
                    <div v-if="profile.models && profile.models.length > 0" class="space-y-2">
                      <div 
                        v-for="(model, index) in profile.models" 
                        :key="index"
                        class="flex items-center justify-between p-2 bg-background rounded border"
                      >
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium text-text-light truncate">
                            {{ getModelDisplayName(model) }}
                          </div>
                          <div class="text-xs text-text-muted">
                            <span class="inline-flex items-center mr-2">
                              <FontAwesomeIcon icon="tag" class="mr-1" />{{ model.type }}
                            </span>
                            <span v-if="model.tags && model.tags.length > 0" class="inline-flex items-center">
                              <FontAwesomeIcon icon="tags" class="mr-1" />{{ model.tags.join(', ') }}
                            </span>
                          </div>
                        </div>
                        <button 
                          type="button" 
                          class="ml-2 text-red-600 hover:text-red-800"
                          @click="removeModelFromProfile(name, index)"
                          title="Remove model"
                        >
                          <FontAwesomeIcon icon="trash-alt" />
                        </button>
                      </div>
                    </div>
                    <div v-else class="text-text-muted text-sm flex items-center">
                      <FontAwesomeIcon icon="info-circle" class="mr-1" />No models selected for this profile.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Form Buttons -->
        <div class="flex justify-end space-x-3 pt-4">
          <button type="button" class="btn btn-secondary" @click="resetBundleForm">
            <FontAwesomeIcon icon="undo" class="mr-1" />Reset Form
          </button>
          <button type="submit" class="btn btn-primary">
            <FontAwesomeIcon :icon="currentBundle.id ? 'save' : 'plus'" class="mr-1" />
            {{ currentBundle.id ? 'Update' : 'Create' }} Bundle
          </button>
        </div>
      </form>
    </div>

    <!-- Model Selector Modal -->
    <div v-if="showModelSelectorModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-background rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden mx-4">
        <div class="flex justify-between items-center p-4 border-b border-border">
          <h3 class="text-lg font-semibold text-text-light">Select Models for {{ currentProfileName }}</h3>
          <button 
            type="button" 
            class="text-text-muted hover:text-text-light"
            @click="closeModelSelector"
          >
            <FontAwesomeIcon icon="times" class="text-xl" />
          </button>
        </div>
        
        <!-- Collapsible Filter Bar -->
        <div class="border-b border-border bg-background-mute">
          <!-- Filter Toggle Header -->
          <button 
            type="button"
            class="w-full px-4 py-3 flex items-center justify-between hover:bg-background transition-colors"
            @click="showFilterSection = !showFilterSection"
          >
            <div class="flex items-center">
              <FontAwesomeIcon icon="filter" class="mr-2" />
              <span class="font-medium text-text-light">Filter Models</span>
              <span v-if="modelFilter" class="ml-2 text-sm text-blue-600">({{ filteredModelsCount }} models)</span>
            </div>
            <FontAwesomeIcon 
              :icon="showFilterSection ? 'chevron-up' : 'chevron-down'" 
              class="text-text-muted"
            />
          </button>
          
          <!-- Collapsible Filter Content -->
          <div v-if="showFilterSection" class="px-4 pb-4">
            <div class="flex items-center space-x-4">
              <div class="flex-1">
                <label class="form-label text-sm flex items-center mb-1">
                  <FontAwesomeIcon icon="search" class="mr-2" />Filter by Tags
                </label>
                <input 
                  type="text" 
                  class="form-input w-full text-sm" 
                  v-model="modelFilter"
                  placeholder="Enter tags to filter models (e.g., base, fp8, nsfw...)"
                />
                <p class="text-xs text-text-muted mt-1">
                  Separate multiple tags with commas. Models matching any of these tags will be shown.
                </p>
              </div>
              <div class="flex flex-col">
                <button 
                  type="button" 
                  class="btn btn-sm btn-outline mb-2"
                  @click="clearModelFilter"
                  :disabled="!modelFilter"
                >
                  <FontAwesomeIcon icon="times" class="mr-1" />Clear
                </button>
                <div class="text-xs text-text-muted text-center">
                  {{ filteredModelsCount }} models
                </div>
              </div>
            </div>
            
            <!-- Popular Tags -->
            <div v-if="popularTags.length > 0" class="mt-3">
              <label class="text-xs text-text-muted mb-2 block">Popular tags:</label>
              <div class="flex flex-wrap gap-1">
                <button 
                  v-for="tag in popularTags" 
                  :key="tag"
                  type="button"
                  class="px-2 py-1 text-xs rounded bg-gray-200 hover:bg-gray-300 text-gray-700 transition-colors"
                  @click="addTagToFilter(tag)"
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-4 overflow-y-auto" :style="{ 'max-height': showFilterSection ? '45vh' : '55vh' }">
          <div v-for="(groupModels, groupName) in filteredGroupedModels" :key="groupName" class="mb-6">
            <h4 class="text-md font-medium text-text-light mb-3 flex items-center">
              <FontAwesomeIcon icon="folder" class="mr-2" />{{ groupName }}
              <span class="ml-2 text-sm text-text-muted">({{ groupModels.length }} models)</span>
            </h4>
            <div class="grid grid-cols-1 gap-2">
              <div 
                v-for="(model, index) in groupModels" 
                :key="index"
                class="flex items-center p-3 border border-border rounded hover:bg-background-mute cursor-pointer"
                @click="toggleModelSelection(model)"
              >
                <input 
                  type="checkbox" 
                  :checked="isModelSelected(model)"
                  class="mr-3"
                  @click.stop
                />
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-text-light">
                    {{ getModelDisplayName(model) }}
                  </div>
                  <div class="text-xs text-text-muted">
                    <span class="inline-flex items-center mr-2">
                      <FontAwesomeIcon icon="tag" class="mr-1" />{{ model.type }}
                    </span>
                    <span v-if="model.tags && model.tags.length > 0" class="inline-flex items-center mr-2">
                      <FontAwesomeIcon icon="tags" class="mr-1" />{{ model.tags.join(', ') }}
                    </span>
                    <span v-if="model.size" class="inline-flex items-center">
                      <FontAwesomeIcon icon="weight" class="mr-1" />{{ formatFileSize(model.size) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- No Results Message -->
          <div v-if="Object.keys(filteredGroupedModels).length === 0" class="text-center py-8">
            <FontAwesomeIcon icon="search" class="text-4xl text-text-muted mb-4" />
            <h4 class="text-lg font-medium text-text-light mb-2">No models found</h4>
            <p class="text-text-muted">
              No models match the current filter criteria. Try adjusting your tag filters.
            </p>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 p-4 border-t border-border bg-background-mute">
          <button 
            type="button" 
            class="btn btn-secondary"
            @click="closeModelSelector"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary"
            @click="applyModelSelection"
          >
            Apply Selection ({{ selectedModels.length }} selected)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNotifications } from '../composables/useNotifications';
import api from '../services/api';

const { success, error, confirm } = useNotifications();

// State
const bundles = ref([]);
const workflows = ref([]);
const groupedModels = ref({});
const showWorkflowDropdown = ref(false);
const showModelSelectorModal = ref(false);
const currentProfileName = ref('');
const selectedModels = ref([]);
const modelFilter = ref('');
const showFilterSection = ref(false);

const currentBundle = ref({
  id: '',
  name: '',
  description: '',
  version: '1.0.0',
  author: '',
  website: '',
  workflows: [],
  hardware_profiles: {}
});

// Computed for missing workflows
const missingWorkflows = computed(() => {
  if (!currentBundle.value.workflows) return [];
  
  return currentBundle.value.workflows.filter(
    workflow => !workflows.value.includes(workflow)
  );
});

// Computed for available workflows (not yet selected)
const availableWorkflows = computed(() => {
  return workflows.value.filter(workflow => 
    !currentBundle.value.workflows.includes(workflow)
  );
});

// Computed for filtered models based on tag filter
const filteredGroupedModels = computed(() => {
  if (!modelFilter.value.trim()) {
    return groupedModels.value;
  }
  
  const filterTags = modelFilter.value
    .split(',')
    .map(tag => tag.trim().toLowerCase())
    .filter(tag => tag.length > 0);
  
  if (filterTags.length === 0) {
    return groupedModels.value;
  }
  
  const filtered = {};
  
  for (const [groupName, models] of Object.entries(groupedModels.value)) {
    const filteredModels = models.filter(model => {
      if (!model.tags || model.tags.length === 0) return false;
      
      const modelTags = model.tags.map(tag => tag.toLowerCase());
      return filterTags.some(filterTag => 
        modelTags.some(modelTag => modelTag.includes(filterTag))
      );
    });
    
    if (filteredModels.length > 0) {
      filtered[groupName] = filteredModels;
    }
  }
  
  return filtered;
});

// Computed for popular tags
const popularTags = computed(() => {
  const tagCounts = {};
  
  for (const models of Object.values(groupedModels.value)) {
    for (const model of models) {
      if (model.tags && model.tags.length > 0) {
        for (const tag of model.tags) {
          tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        }
      }
    }
  }
  
  return Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([tag]) => tag);
});

// Computed for filtered models count
const filteredModelsCount = computed(() => {
  return Object.values(filteredGroupedModels.value)
    .reduce((total, models) => total + models.length, 0);
});

// API Functions
const loadBundles = async () => {
  try {
    const response = await api.get('/bundles/');
    bundles.value = response.data || [];
  } catch (err) {
    console.error('Error loading bundles:', err);
    error('Failed to load bundles');
  }
};

const loadWorkflows = async () => {
  try {
    const response = await api.get('/workflows/');
    workflows.value = response.data || [];
  } catch (err) {
    console.error('Error loading workflows:', err);
    error('Failed to load workflows');
  }
};

const loadModels = async () => {
  try {
    const response = await api.get('/jsonmodels/');
    groupedModels.value = response.data?.groups || {};
  } catch (err) {
    console.error('Error loading models:', err);
    error('Failed to load model groups');
  }
};

const saveBundle = async () => {
  try {
    if (currentBundle.value.id) {
      // Update existing bundle
      const bundleData = {
        name: currentBundle.value.name,
        description: currentBundle.value.description,
        version: currentBundle.value.version,
        author: currentBundle.value.author || null,
        website: currentBundle.value.website || null,
        workflows: currentBundle.value.workflows,
        hardware_profiles: currentBundle.value.hardware_profiles
      };
      
      await api.put(`/bundles/${currentBundle.value.id}`, bundleData);
      success(`Bundle "${currentBundle.value.name}" updated successfully`, 5000, true);
      
      // Only reload bundles list, keep form populated for continued editing
      await loadBundles();
    } else {
      // Create new bundle
      const bundleData = {
        name: currentBundle.value.name,
        description: currentBundle.value.description,
        version: currentBundle.value.version,
        author: currentBundle.value.author || null,
        website: currentBundle.value.website || null,
        workflows: currentBundle.value.workflows,
        hardware_profiles: currentBundle.value.hardware_profiles
      };
      
      await api.post('/bundles/', bundleData);
      success(`Bundle "${currentBundle.value.name}" created successfully`, 5000, true);
      
      // After creating, reload bundles and reset form
      await loadBundles();
      resetBundleForm();
    }
  } catch (err) {
    console.error('Error saving bundle:', err);
    error('Failed to save bundle: ' + (err.response?.data?.detail || err.message), 8000, true);
  }
};

const uploadWorkflow = async (file) => {
  try {
    const formData = new FormData();
    formData.append('workflow_file', file);
    
    await api.post('/workflows/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    success(`Workflow "${file.name}" uploaded successfully`);
    await loadWorkflows(); // Reload workflows
  } catch (err) {
    console.error('Error uploading workflow:', err);
    error('Failed to upload workflow: ' + (err.response?.data?.detail || err.message));
  }
};

// Methods
const createNewBundle = () => {
  resetBundleForm();
};

const removeWorkflowFromBundle = async (workflow) => {
  try {
    const confirmed = await confirm(`Are you sure you want to remove "${workflow}" from this bundle?`, 'Confirm Removal');
    
    if (confirmed) {
      const index = currentBundle.value.workflows.indexOf(workflow);
      if (index !== -1) {
        currentBundle.value.workflows.splice(index, 1);
        success(`Workflow "${workflow}" removed from bundle`);
      }
    }
  } catch (err) {
    error('Failed to remove workflow from bundle: ' + err.message);
  }
};

const handleWorkflowUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    await uploadWorkflow(file);
    event.target.value = '';
  }
};

const triggerWorkflowUpload = () => {
  document.getElementById('workflow-file').click();
};

const getModelDisplayName = (model) => {
  if (model.dest) {
    return model.dest.split('/').pop();
  }
  if (model.url) {
    return model.url.split('/').pop();
  }
  return 'Unknown model';
};

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown size';
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const showModelSelector = (profileName) => {
  currentProfileName.value = profileName;
  selectedModels.value = [...(currentBundle.value.hardware_profiles[profileName]?.models || [])];
  modelFilter.value = '';
  showFilterSection.value = false;
  showModelSelectorModal.value = true;
};

const closeModelSelector = () => {
  showModelSelectorModal.value = false;
  currentProfileName.value = '';
  selectedModels.value = [];
  modelFilter.value = '';
  showFilterSection.value = false;
};

const clearModelFilter = () => {
  modelFilter.value = '';
};

const addTagToFilter = (tag) => {
  const currentTags = modelFilter.value
    .split(',')
    .map(t => t.trim())
    .filter(t => t.length > 0);
  
  if (!currentTags.includes(tag)) {
    currentTags.push(tag);
    modelFilter.value = currentTags.join(', ');
  }
};

const toggleModelSelection = (model) => {
  const index = selectedModels.value.findIndex(m => 
    m.url === model.url && m.dest === model.dest
  );
  
  if (index !== -1) {
    selectedModels.value.splice(index, 1);
  } else {
    selectedModels.value.push({ ...model });
  }
};

const isModelSelected = (model) => {
  return selectedModels.value.some(m => 
    m.url === model.url && m.dest === model.dest
  );
};

const applyModelSelection = () => {
  if (!currentBundle.value.hardware_profiles[currentProfileName.value]) {
    currentBundle.value.hardware_profiles[currentProfileName.value] = {
      description: '',
      models: []
    };
  }
  
  currentBundle.value.hardware_profiles[currentProfileName.value].models = [...selectedModels.value];
  closeModelSelector();
};

const removeModelFromProfile = (profileName, modelIndex) => {
  if (currentBundle.value.hardware_profiles[profileName]?.models) {
    currentBundle.value.hardware_profiles[profileName].models.splice(modelIndex, 1);
  }
};

const updateProfileName = (oldName, newName) => {
  // Trim and validate the new name
  const trimmedName = newName.trim();
  
  // If name is empty or unchanged, do nothing
  if (!trimmedName || trimmedName === oldName) {
    return;
  }
  
  // Check if the new name already exists
  if (currentBundle.value.hardware_profiles[trimmedName]) {
    error(`Profile name "${trimmedName}" already exists`);
    return;
  }
  
  // Create new profile with the new name
  const profileData = currentBundle.value.hardware_profiles[oldName];
  currentBundle.value.hardware_profiles[trimmedName] = profileData;
  
  // Remove the old profile
  delete currentBundle.value.hardware_profiles[oldName];
  
  success(`Profile renamed from "${oldName}" to "${trimmedName}"`);
};

const addHardwareProfile = () => {
  // Find a unique name for the new profile
  let profileName = 'New Profile';
  let counter = 1;
  
  while (currentBundle.value.hardware_profiles[profileName]) {
    profileName = `New Profile ${counter}`;
    counter++;
  }
  
  currentBundle.value.hardware_profiles[profileName] = {
    description: '',
    models: []
  };
};

const removeHardwareProfile = (name) => {
  delete currentBundle.value.hardware_profiles[name];
};

const editBundle = async (bundleId) => {
  try {
    const response = await api.get(`/bundles/${bundleId}`);
    const bundle = response.data;
    
    currentBundle.value = {
      id: bundle.id,
      name: bundle.name,
      description: bundle.description,
      version: bundle.version || '1.0.0',
      author: bundle.author || '',
      website: bundle.website || '',
      workflows: bundle.workflows || [],
      hardware_profiles: bundle.hardware_profiles || {}
    };
  } catch (err) {
    console.error('Error loading bundle for editing:', err);
    error('Failed to load bundle for editing');
  }
};

const handleDeleteBundle = async (bundleId) => {
  try {
    const bundle = bundles.value.find(b => b.id === bundleId);
    const bundleName = bundle ? bundle.name : bundleId;
    
    const confirmed = await confirm(`Are you sure you want to delete bundle "${bundleName}"?`, 'Confirm Deletion');
    if (confirmed) {
      await api.delete(`/bundles/${bundleId}`);
      success(`Bundle "${bundleName}" deleted successfully`);
      await loadBundles();
    }
  } catch (err) {
    console.error('Error deleting bundle:', err);
    error('Failed to delete bundle: ' + (err.response?.data?.detail || err.message));
  }
};

const resetBundleForm = () => {
  currentBundle.value = {
    id: '',
    name: '',
    description: '',
    version: '1.0.0',
    author: '',
    website: '',
    workflows: [],
    hardware_profiles: {}
  };
  closeDropdowns();
};

const handleSaveBundle = async () => {
  await saveBundle();
};

// Methods for workflow selection
const addWorkflowToSelection = (workflow) => {
  if (!currentBundle.value.workflows.includes(workflow)) {
    currentBundle.value.workflows.push(workflow);
  }
  showWorkflowDropdown.value = false;
};

const removeWorkflowFromSelection = (workflow) => {
  const index = currentBundle.value.workflows.indexOf(workflow);
  if (index !== -1) {
    currentBundle.value.workflows.splice(index, 1);
  }
};

// Close dropdowns when clicking outside
const closeDropdowns = () => {
  showWorkflowDropdown.value = false;
};

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadBundles(),
    loadWorkflows(),
    loadModels()
  ]);
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.relative')) {
      closeDropdowns();
    }
  });
});
</script>

<style scoped>
/* Aligne verticalement les cellules du tableau des bundles dans le BundleManager */
.table-bordered td,
.table-bordered th {
  vertical-align: middle !important;
}
</style>