<template>
  <div>
    <div class="card shadow-sm mb-4">
      <!-- Unification du header avec FileManager -->
      <div class="card-header bg-primary">
        <h2 class="mb-0 text-white">Bundle Manager</h2>
      </div>
      <div class="card-body">
        <!-- ...existing code for bundle list... -->
        <h4 class="card-title">
          <i class="fas fa-box-open me-2"></i>Model Bundles
        </h4>
        <p class="card-text">
          <i class="fas fa-info-circle me-2"></i>Create predefined bundles of models with associated workflows.
        </p>
        <!-- Bundle List -->
        <div v-if="Object.keys(bundles).length > 0" class="mb-4">
          <h5><i class="fas fa-list me-2"></i>Available Bundles</h5>
          <div class="table-responsive">
            <table class="table table-bordered">
              <thead class="table-light">
                <tr>
                  <th><i class="fas fa-tag me-1"></i>Name</th>
                  <th><i class="fas fa-info me-1"></i>Description</th>
                  <th><i class="fas fa-sitemap me-1"></i>Workflows</th>
                  <th><i class="fas fa-cubes me-1"></i>Models</th>
                  <th><i class="fas fa-server me-1"></i>Hardware Profiles</th>
                  <th><i class="fas fa-cogs me-1"></i>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(bundle, name) in bundles" :key="name">
                  <td>{{ name }}</td>
                  <td>{{ bundle.description }}</td>
                  <td>
                    <div class="d-flex flex-wrap gap-1">
                      <span v-for="workflow in bundle.workflows || [bundle.workflow]" :key="workflow" class="badge bg-info">
                        <i class="fas fa-file-code me-1"></i>{{ workflow }}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span v-for="model in bundle.models" :key="model" class="badge bg-primary me-1">
                      <i class="fas fa-cube me-1"></i>{{ model }}
                    </span>
                  </td>
                  <td>
                    <span v-for="(profile, profileName) in bundle.hardware_profiles" :key="profileName" class="badge bg-secondary me-1">
                      <i class="fas fa-microchip me-1"></i>{{ profileName }}
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary me-1" @click="editBundle(name)">
                      <i class="fas fa-edit me-1"></i>Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteBundle(name)">
                      <i class="fas fa-trash-alt me-1"></i>Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>No bundles available. Create your first bundle below.
        </div>
      </div>
    </div>
    <!-- Nouvelle card pour le formulaire de création/édition -->
    <div class="card mb-4">
      <div class="card-header">
        <i class="fas" :class="currentBundle.name ? 'fa-edit' : 'fa-plus-circle'" me-2></i>
        {{ currentBundle.name ? 'Edit Bundle' : 'Create New Bundle' }}
      </div>
      <div class="card-body">
        <form @submit.prevent="handleSaveBundle">
          <!-- Basic Info -->
          <div class="mb-3 row">
            <label class="col-sm-2 col-form-label"><i class="fas fa-tag me-2"></i>Name:</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                class="form-control" 
                v-model="currentBundle.name"
                :disabled="!!currentBundle.name && Object.keys(bundles).includes(currentBundle.name)"
                required
              />
            </div>
          </div>
          <div class="mb-3 row">
            <label class="col-sm-2 col-form-label"><i class="fas fa-info-circle me-2"></i>Description:</label>
            <div class="col-sm-10">
              <input 
                type="text" 
                class="form-control" 
                v-model="currentBundle.bundle.description"
                required
              />
            </div>
          </div>
          <!-- Workflow Selection -->
          <div class="mb-3 row">
            <label class="col-sm-2 col-form-label"><i class="fas fa-sitemap me-2"></i>Workflows:</label>
            <div class="col-sm-10">
              <div class="mb-2">
                <div class="form-control h-auto" style="min-height: 100px;">
                  <!-- Workflows disponibles -->
                  <div v-for="workflow in workflows" :key="workflow" class="form-check">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      :id="`workflow-${workflow}`"
                      :value="workflow"
                      v-model="currentBundle.bundle.workflows"
                    />
                    <label class="form-check-label" :for="`workflow-${workflow}`">
                      <i class="fas fa-file-code me-1"></i>{{ workflow }}
                    </label>
                  </div>
                  
                  <!-- Workflows manquants (non disponibles dans la liste) -->
                  <div v-if="missingWorkflows.length > 0" class="mt-3 pt-3 border-top">
                    <div class="text-warning mb-2">
                      <i class="fas fa-exclamation-triangle me-1"></i>
                      <strong>Missing workflows:</strong> 
                      These workflows are referenced in this bundle but are not available in the system.
                    </div>
                    <div v-for="workflow in missingWorkflows" :key="workflow" class="d-flex align-items-center mb-1">
                      <span class="badge bg-warning me-2">
                        <i class="fas fa-file-code me-1"></i>{{ workflow }}
                      </span>
                      <button 
                        type="button" 
                        class="btn btn-sm btn-outline-danger" 
                        @click="removeWorkflowFromBundle(workflow)"
                      >
                        <i class="fas fa-times"></i> Remove from bundle
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Upload New Workflow -->
              <div class="input-group">
                <input 
                  type="file" 
                  class="form-control" 
                  id="workflow-file"
                  @change="handleWorkflowUpload"
                  accept=".json"
                />
                <button class="btn btn-outline-secondary" type="button" @click="triggerWorkflowUpload">
                  <i class="fas fa-upload me-1"></i>Upload New Workflow
                </button>
              </div>
            </div>
          </div>
          
          <!-- Model Groups Selection -->
          <div class="mb-3 row">
            <label class="col-sm-2 col-form-label"><i class="fas fa-cubes me-2"></i>Model Groups:</label>
            <div class="col-sm-10">
              <div class="form-control h-auto" style="min-height: 100px;">
                <div v-for="group in Object.keys(groupedModels)" :key="group" class="form-check">
                  <input 
                    type="checkbox" 
                    class="form-check-input" 
                    :id="`group-${group}`"
                    :value="group"
                    v-model="currentBundle.bundle.models"
                  />
                  <label class="form-check-label" :for="`group-${group}`">
                    <i class="fas fa-cube me-1"></i>{{ group }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Hardware Profiles -->
          <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="mb-0"><i class="fas fa-server me-2"></i>Hardware Profiles</h6>
              <button type="button" class="btn btn-sm btn-outline-success" @click="addHardwareProfile">
                <i class="fas fa-plus-circle me-1"></i>Add Profile
              </button>
            </div>
            
            <div v-for="(profile, name) in currentBundle.bundle.hardware_profiles" :key="name" class="card mb-3">
              <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="fas fa-microchip me-1"></i>{{ name }}</span>
                <button type="button" class="btn btn-sm btn-outline-danger" @click="removeHardwareProfile(name)">
                  <i class="fas fa-trash-alt me-1"></i>Remove
                </button>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label"><i class="fas fa-info me-2"></i>Description:</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="profile.description"
                  />
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label"><i class="fas fa-plus-circle me-2"></i>Include Tags:</label>
                    <textarea 
                      class="form-control"
                      v-model="profileIncludeTags[name]"
                      placeholder="Enter tags separated by commas"
                      rows="2"
                    ></textarea>
                  </div>
                  
                  <div class="col-md-6 mb-3">
                    <label class="form-label"><i class="fas fa-minus-circle me-2"></i>Exclude Tags:</label>
                    <textarea 
                      class="form-control"
                      v-model="profileExcludeTags[name]"
                      placeholder="Enter tags separated by commas"
                      rows="2"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Form Buttons -->
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">
              <i class="fas" :class="currentBundle.name && Object.keys(bundles).includes(currentBundle.name) ? 'fa-save' : 'fa-plus'" me-1></i>
              {{ currentBundle.name && Object.keys(bundles).includes(currentBundle.name) ? 'Update' : 'Create' }} Bundle
            </button>
            <button type="button" class="btn btn-secondary" @click="resetBundleForm">
              <i class="fas fa-undo me-1"></i>Reset Form
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import {
  bundles, workflows, currentBundle, loadBundles, loadWorkflows,
  saveBundle, deleteBundle, editBundle, resetBundleForm,
  uploadWorkflow, deleteWorkflow, addHardwareProfile, removeHardwareProfile,
  confirm, alert
} from '../ModelManager.logic.js';
import { groupedModels, fetchModels } from '../App.logic.js';

// Track tag inputs with reactive objects
const profileIncludeTags = ref({});
const profileExcludeTags = ref({});

// Watch pour mettre à jour les tags à partir des profils hardware
watch(
  () => currentBundle.value.bundle.hardware_profiles,
  (profiles) => {
    // Mettre à jour les champs de texte pour inclure/exclure les tags
    for (const [profileName, profileData] of Object.entries(profiles)) {
      if (profileData.model_filters) {
        // Initialiser les champs de texte s'ils n'existent pas encore
        if (!profileIncludeTags.value[profileName]) {
          profileIncludeTags.value[profileName] = '';
        }
        if (!profileExcludeTags.value[profileName]) {
          profileExcludeTags.value[profileName] = '';
        }
        
        // Convertir les tableaux de tags en chaînes pour l'interface
        if (Array.isArray(profileData.model_filters.include_tags)) {
          profileIncludeTags.value[profileName] = profileData.model_filters.include_tags.join(', ');
        }
        
        if (Array.isArray(profileData.model_filters.exclude_tags)) {
          profileExcludeTags.value[profileName] = profileData.model_filters.exclude_tags.join(', ');
        }
      }
    }
  },
  { immediate: true, deep: true }
);

// Watch pour mettre à jour les tags dans les profils à partir des champs de texte
watch(
  [profileIncludeTags, profileExcludeTags],
  ([newIncludeTags, newExcludeTags]) => {
    for (const [profileName, tagsString] of Object.entries(newIncludeTags)) {
      if (currentBundle.value.bundle.hardware_profiles[profileName]) {
        if (!currentBundle.value.bundle.hardware_profiles[profileName].model_filters) {
          currentBundle.value.bundle.hardware_profiles[profileName].model_filters = {
            include_tags: [],
            exclude_tags: []
          };
        }
        
        // Convertir la chaîne en tableau, en supprimant les espaces vides
        currentBundle.value.bundle.hardware_profiles[profileName].model_filters.include_tags = 
          tagsString.split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0);
      }
    }
    
    for (const [profileName, tagsString] of Object.entries(newExcludeTags)) {
      if (currentBundle.value.bundle.hardware_profiles[profileName]) {
        if (!currentBundle.value.bundle.hardware_profiles[profileName].model_filters) {
          currentBundle.value.bundle.hardware_profiles[profileName].model_filters = {
            include_tags: [],
            exclude_tags: []
          };
        }
        
        // Convertir la chaîne en tableau, en supprimant les espaces vides
        currentBundle.value.bundle.hardware_profiles[profileName].model_filters.exclude_tags = 
          tagsString.split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0);
      }
    }
  },
  { deep: true }
);

// Computed pour trouver les workflows dans le bundle qui ne sont pas dans la liste des workflows disponibles
const missingWorkflows = computed(() => {
  if (!currentBundle.value.bundle.workflows) return [];
  
  return currentBundle.value.bundle.workflows.filter(
    workflow => !workflows.value.includes(workflow)
  );
});

// Method to remove a missing workflow from the bundle
const removeWorkflowFromBundle = async (workflow) => {
  console.log("Remove workflow button clicked for:", workflow);
  
  try {
    // Add a small delay to ensure the component is ready (100ms)
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const confirmed = await confirm({
      title: 'Confirm Removal',
      message: `Are you sure you want to remove "${workflow}" from this bundle?`,
      confirmLabel: 'Remove',
      cancelLabel: 'Cancel'
    });
    
    console.log("Confirmation result:", confirmed);
    
    if (confirmed) {
      const index = currentBundle.value.bundle.workflows.indexOf(workflow);
      console.log("Found workflow at index:", index);
      
      if (index !== -1) {
        currentBundle.value.bundle.workflows.splice(index, 1);
        console.log("Workflow removed, new workflows array:", currentBundle.value.bundle.workflows);
      }
    }
  } catch (error) {
    console.error('Error in removeWorkflowFromBundle:', error);
    await alert({
      title: 'Error',
      message: 'Failed to remove workflow from bundle: ' + error.message,
      confirmLabel: 'OK',
      hideCancel: true
    });
  }
};

// Handle workflow file upload
const handleWorkflowUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    await uploadWorkflow(file);
    await loadWorkflows(); // Reload workflows after upload
    event.target.value = ''; // Reset the input
  }
};

// Helper function to trigger file input click
const triggerWorkflowUpload = () => {
  document.getElementById('workflow-file').click();
};

// Ensure backward compatibility with single workflow
watch(() => currentBundle.value, (bundle) => {
  // Convert single workflow to array for backward compatibility
  if (bundle && bundle.bundle) {
    if (bundle.bundle.workflow && !bundle.bundle.workflows) {
      currentBundle.value.bundle.workflows = [bundle.bundle.workflow];
      delete currentBundle.value.bundle.workflow;
    }
  }
}, { deep: true, immediate: true });

// Handle form submission for saving bundles
const handleSaveBundle = async () => {
  try {
    // Call the imported saveBundle function
    await saveBundle();
  } catch (error) {
    console.error('Failed to save bundle:', error);
    alert('Failed to save bundle');
  }
};

// Load data on component mount
onMounted(async () => {
  await Promise.all([
    loadBundles(),
    loadWorkflows(),
    fetchModels()  // Ajout de fetchModels pour charger les données des modèles
  ]);
  
  // Initialize workflows array for backward compatibility
  if (!currentBundle.value.bundle.workflows) {
    currentBundle.value.bundle.workflows = currentBundle.value.bundle.workflow ? 
      [currentBundle.value.bundle.workflow] : [];
    
    // Remove old single workflow property if it exists
    if (currentBundle.value.bundle.workflow) {
      delete currentBundle.value.bundle.workflow;
    }
  }
});
</script>

<style scoped>
/* Aligne verticalement les cellules du tableau des bundles dans le BundleManager */
.table-bordered td,
.table-bordered th {
  vertical-align: middle !important;
}
</style>