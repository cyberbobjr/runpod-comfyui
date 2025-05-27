<script setup>
import { faBoxOpen, faCubes, faDownload, faInfo, faSearch, faServer, faSitemap, faUpload, faTrashAlt, faCheckCircle, faTimesCircle, faFileUpload, faSync, faExclamationCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { computed, onMounted, ref } from 'vue';
import { useNotifications } from '../composables/useNotifications';
import api from '../services/api';
import { useInstallProgress } from '../composables/useInstallProgress';

const { success, error, confirm } = useNotifications();
const { startInstallation } = useInstallProgress();
const searchQuery = ref('');
const loading = ref(false);
const uploadedBundles = ref([]);
const installedBundles = ref([]);
const showBundleDetailsModal = ref(false);
const selectedBundle = ref(null);
const openAccordionPanels = ref(new Set());

// Load uploaded bundles
const loadUploadedBundles = async () => {
  try {
    const response = await api.get('/bundles/');
    uploadedBundles.value = response.data || [];
  } catch (err) {
    error('Failed to load uploaded bundles: ' + (err.response?.data?.message || err.message));
  }
};

// Load installed bundles from API
const loadInstalledBundles = async () => {
  try {
    const response = await api.get('/bundles/installed/');
    installedBundles.value = response.data || [];
  } catch (err) {
    error('Failed to load installed bundles: ' + (err.response?.data?.message || err.message));
  }
};

// Check if a bundle is installed
const isBundleInstalled = (bundleId, profile = null) => {
  return installedBundles.value.some(installed => {
    return installed.id === bundleId && (!profile || installed.profile === profile);
  });
};

// Upload bundle
const uploadBundle = async (file) => {
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('bundle_file', file);
    
    await api.post('/bundles/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    success(`Bundle "${file.name}" uploaded successfully`);
    await loadUploadedBundles();
  } catch (err) {
    error('Failed to upload bundle: ' + (err.response?.data?.detail || err.message));
  } finally {
    loading.value = false;
  }
};

// Handle file upload
const handleBundleUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    await uploadBundle(file);
    event.target.value = '';
  }
};

// Trigger file upload
const triggerBundleUpload = () => {
  document.getElementById('bundle-upload-file').click();
};

// Get bundle status for uploaded bundles
const getUploadedBundleStatus = (bundle) => {
  const profiles = Object.keys(bundle.hardware_profiles || {});
  const installedProfiles = profiles.filter(profile => isBundleInstalled(bundle.id, profile));
  
  if (installedProfiles.length === 0) {
    return { status: 'not-installed', text: 'Not Installed' };
  } else if (installedProfiles.length === profiles.length) {
    return { status: 'fully-installed', text: 'Fully Installed' };
  } else {
    return { status: 'partially-installed', text: `Partially Installed (${installedProfiles.length}/${profiles.length})` };
  }
};

// Install uploaded bundle
const installUploadedBundle = async (bundle) => {
  try {
    const profiles = Object.keys(bundle.hardware_profiles || {});
    if (profiles.length === 0) {
      throw new Error('No hardware profile available for this bundle');
    }
    
    // Filtrer les profils non installés
    const profilesToInstall = profiles.filter(profile => 
      !isBundleInstalled(bundle.id, profile)
    );
    
    if (profilesToInstall.length === 0) {
      success(`Bundle "${bundle.name}" is already fully installed`);
      return;
    }
    
    // Démarrer l'installation avec suivi de progression
    await startInstallation(bundle.id, bundle.name, profilesToInstall);
    
    // Recharger la liste des bundles installés après un délai
    setTimeout(async () => {
      await loadInstalledBundles();
    }, 2000);
    
  } catch (err) {
    error('Failed to start installation: ' + (err.response?.data?.detail || err.message));
  }
};

// Uninstall bundle
const uninstallBundle = async (bundle) => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to uninstall bundle "${bundle.name}"?`, 
      'Confirm Uninstall'
    );
    
    if (confirmed) {
      loading.value = true;
      
      const profiles = Object.keys(bundle.hardware_profiles || {});
      for (const profileName of profiles) {
        if (isBundleInstalled(bundle.id, profileName)) {
          await api.post('/bundles/uninstall', {
            bundle_id: bundle.id,
            profile: profileName
          });
        }
      }
      
      success(`Bundle "${bundle.name}" uninstalled successfully`);
      await loadInstalledBundles();
    }
  } catch (err) {
    error('Failed to uninstall bundle: ' + (err.response?.data?.detail || err.message));
  } finally {
    loading.value = false;
  }
};

// Delete uploaded bundle
const deleteUploadedBundle = async (bundle) => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to delete the uploaded bundle "${bundle.name}"? This will remove it from the server permanently.`, 
      'Confirm Delete'
    );
    
    if (confirmed) {
      loading.value = true;
      
      await api.delete(`/bundles/${bundle.id}`);
      
      success(`Bundle "${bundle.name}" deleted successfully`);
      await loadUploadedBundles();
      await loadInstalledBundles();
    }
  } catch (err) {
    error('Failed to delete bundle: ' + (err.response?.data?.detail || err.message));
  } finally {
    loading.value = false;
  }
};

// View bundle details
const viewBundleDetails = (bundle) => {
  selectedBundle.value = bundle;
  showBundleDetailsModal.value = true;
};

// Toggle accordion panel
const toggleAccordionPanel = (profileName) => {
  if (openAccordionPanels.value.has(profileName)) {
    openAccordionPanels.value.delete(profileName);
  } else {
    openAccordionPanels.value.add(profileName);
  }
};

// Close bundle details modal
const closeBundleDetails = () => {
  showBundleDetailsModal.value = false;
  selectedBundle.value = null;
  openAccordionPanels.value.clear();
};

// Get model display name
const getModelDisplayName = (model) => {
  if (model.dest) {
    return model.dest.split('/').pop();
  }
  if (model.url) {
    return model.url.split('/').pop();
  }
  return 'Unknown model';
};

// Filtered bundles based on search
const filteredBundles = computed(() => {
  if (!searchQuery.value) return uploadedBundles.value;
  
  const query = searchQuery.value.toLowerCase();
  return uploadedBundles.value.filter(bundle => 
    bundle.name.toLowerCase().includes(query) || 
    bundle.description.toLowerCase().includes(query) ||
    (bundle.workflows && bundle.workflows.some(wf => wf.toLowerCase().includes(query)))
  );
});

// Load data on component mount
onMounted(async () => {
  await Promise.all([
    loadUploadedBundles(),
    loadInstalledBundles()
  ]);
});
</script>

<template>
  <div class="p-4 bg-background space-y-6">
    <!-- Upload Bundle Card -->
    <div class="card">
      <h3 class="text-lg font-semibold text-text-light mb-4 flex items-center">
        <FontAwesomeIcon :icon="faUpload" class="mr-2" />
        Upload Bundle
      </h3>
      
      <div class="flex items-center space-x-4">
        <input 
          type="file" 
          class="hidden" 
          id="bundle-upload-file"
          @change="handleBundleUpload"
          accept=".json"
        />
        <button 
          class="btn btn-primary" 
          @click="triggerBundleUpload"
          :disabled="loading"
        >
          <FontAwesomeIcon :icon="faUpload" class="mr-1" />Upload Bundle File
        </button>
        <div v-if="loading" class="text-text-muted flex items-center">
          <FontAwesomeIcon :icon="faSync" class="animate-spin mr-1" />
          Processing...
        </div>
      </div>
      
      <p class="text-text-muted mt-2 text-sm flex items-center">
        <FontAwesomeIcon :icon="faInfo" class="mr-1" />
        Upload a JSON bundle file to add it to your collection. You can then install or manage it below.
      </p>
    </div>

    <!-- Uploaded Bundles List Card -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-text-light flex items-center">
          <FontAwesomeIcon :icon="faBoxOpen" class="mr-2" />
          Uploaded Bundles
        </h2>
        <div class="flex items-center space-x-4">
          <div class="text-sm text-text-muted">
            {{ uploadedBundles.length }} bundle{{ uploadedBundles.length !== 1 ? 's' : '' }} uploaded
          </div>
          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search bundles"
              class="form-input pl-10"
            />
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-light-muted">
              <FontAwesomeIcon :icon="faSearch" />
            </span>
          </div>
        </div>
      </div>
      
      <div class="mb-6">
        <p class="text-text-muted mb-4 flex items-center">
          <FontAwesomeIcon :icon="faInfo" class="mr-2" />
          Manage your uploaded bundles: view details, install/uninstall, or delete them.
        </p>
        
        <!-- Loading state -->
        <div class="relative min-h-[200px]">
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-background-soft bg-opacity-75 z-10">
            <div class="flex flex-col items-center">
              <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
              <span class="mt-2 text-text-light">Processing...</span>
            </div>
          </div>
          
          <!-- Uploaded Bundles List -->
          <div v-if="filteredBundles.length > 0" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-border">
              <thead class="bg-background-mute">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                    <FontAwesomeIcon :icon="faBoxOpen" class="mr-1" />Name
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                    <FontAwesomeIcon :icon="faInfo" class="mr-1" />Description
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                    <FontAwesomeIcon :icon="faServer" class="mr-1" />Profiles
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                    <FontAwesomeIcon :icon="faCheckCircle" class="mr-1" />Status
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-background-soft divide-y divide-border">
                <tr v-for="bundle in filteredBundles" :key="bundle.id" class="hover:bg-background-mute">
                  <td class="px-4 py-3">
                    <div class="flex items-center">
                      <FontAwesomeIcon :icon="faBoxOpen" class="mr-2 text-primary" />
                      <div>
                        <span class="text-text-light font-medium">{{ bundle.name }}</span>
                        <div v-if="bundle.author" class="text-xs text-text-muted">by {{ bundle.author }}</div>
                        <div v-if="bundle.version" class="text-xs text-text-muted">v{{ bundle.version }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-text-light max-w-xs">
                    <div class="truncate" :title="bundle.description">{{ bundle.description }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="(profile, profileName) in bundle.hardware_profiles || {}" 
                        :key="profileName" 
                        class="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-600 text-white"
                      >
                        <FontAwesomeIcon :icon="faServer" class="mr-1" />
                        {{ profileName }} ({{ profile.models?.length || 0 }} models)
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3">
                    <span 
                      :class=" [
                        'px-2 py-1 inline-flex text-xs rounded items-center',
                        getUploadedBundleStatus(bundle).status === 'fully-installed' ? 'bg-green-800 text-white' :
                        getUploadedBundleStatus(bundle).status === 'partially-installed' ? 'bg-yellow-700 text-white' :
                        'bg-gray-700 text-white'
                      ]"
                    >
                      <FontAwesomeIcon 
                        :icon="getUploadedBundleStatus(bundle).status === 'fully-installed' ? faCheckCircle :
                               getUploadedBundleStatus(bundle).status === 'partially-installed' ? faExclamationCircle :
                               faTimesCircle" 
                        class="mr-1" 
                      />
                      {{ getUploadedBundleStatus(bundle).text }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex space-x-2">
                      <!-- View Details Button -->
                      <button 
                        @click="viewBundleDetails(bundle)"
                        class="btn btn-sm btn-outline"
                        title="View bundle details"
                      >
                        <FontAwesomeIcon :icon="faInfo" class="mr-1" />
                        Details
                      </button>
                      
                      <!-- Install/Uninstall Button -->
                      <button 
                        v-if="getUploadedBundleStatus(bundle).status === 'not-installed'"
                        @click="installUploadedBundle(bundle)"
                        class="btn btn-sm btn-primary"
                      >
                        <FontAwesomeIcon :icon="faDownload" class="mr-1" />
                        Install
                      </button>
                      <button 
                        v-else
                        @click="uninstallBundle(bundle)"
                        class="btn btn-sm bg-yellow-600 hover:bg-yellow-700 text-white"
                        :disabled="loading"
                      >
                        <FontAwesomeIcon :icon="faTimesCircle" class="mr-1" />
                        Uninstall
                      </button>
                      
                      <!-- Delete Button -->
                      <button 
                        @click="deleteUploadedBundle(bundle)"
                        class="btn btn-sm bg-red-600 hover:bg-red-700 text-white"
                        :disabled="loading"
                        title="Delete bundle permanently"
                      >
                        <FontAwesomeIcon :icon="faTrashAlt" class="mr-1" />
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Empty state -->
          <div v-else class="text-center py-10">
            <div class="flex flex-col items-center">
              <FontAwesomeIcon :icon="faBoxOpen" class="text-4xl text-gray-500 mb-4" />
              <h3 class="text-lg font-semibold text-text-light">No uploaded bundles</h3>
              <p class="text-text-muted mt-1">
                {{ searchQuery ? 'No bundles match your search criteria.' : 'Upload your first bundle using the form above.' }}
              </p>
              <button 
                v-if="!searchQuery"
                class="btn btn-primary mt-4" 
                @click="triggerBundleUpload"
                :disabled="loading"
              >
                <FontAwesomeIcon :icon="faUpload" class="mr-1" />Upload Bundle
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bundle Details Modal -->
    <div v-if="showBundleDetailsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-background rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden mx-4">
        <div class="flex justify-between items-center p-4 border-b border-border">
          <h3 class="text-lg font-semibold text-text-light">Bundle Details: {{ selectedBundle?.name }}</h3>
          <button 
            type="button" 
            class="text-text-muted hover:text-text-light"
            @click="closeBundleDetails"
          >
            <FontAwesomeIcon :icon="faTimesCircle" class="text-xl" />
          </button>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[70vh]" v-if="selectedBundle">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 class="font-medium text-text-light mb-2 flex items-center">
                <FontAwesomeIcon :icon="faInfo" class="mr-2" />Basic Information
              </h4>
              <dl class="space-y-2">
                <div>
                  <dt class="text-sm text-text-muted">Name:</dt>
                  <dd class="text-text-light">{{ selectedBundle.name }}</dd>
                </div>
                <div>
                  <dt class="text-sm text-text-muted">Version:</dt>
                  <dd class="text-text-light">{{ selectedBundle.version || '1.0.0' }}</dd>
                </div>
                <div>
                  <dt class="text-sm text-text-muted">Author:</dt>
                  <dd class="text-text-light">{{ selectedBundle.author || 'N/A' }}</dd>
                </div>
                <div v-if="selectedBundle.website">
                  <dt class="text-sm text-text-muted">Website:</dt>
                  <dd class="text-text-light">
                    <a :href="selectedBundle.website" target="_blank" class="text-primary hover:underline">
                      {{ selectedBundle.website }}
                    </a>
                  </dd>
                </div>
              </dl>
            </div>
            <div>
              <h4 class="font-medium text-text-light mb-2 flex items-center">
                <FontAwesomeIcon :icon="faInfo" class="mr-2" />Description
              </h4>
              <p class="text-text-light">{{ selectedBundle.description }}</p>
            </div>
          </div>

          <!-- Workflows -->
          <div class="mb-6">
            <h4 class="font-medium text-text-light mb-3 flex items-center">
              <FontAwesomeIcon :icon="faSitemap" class="mr-2" />Workflows ({{ selectedBundle.workflows?.length || 0 }})
            </h4>
            <div v-if="selectedBundle.workflows?.length > 0" class="flex flex-wrap gap-2">
              <span 
                v-for="workflow in selectedBundle.workflows" 
                :key="workflow" 
                class="inline-flex items-center px-3 py-1 rounded text-sm bg-blue-600 text-white"
              >
                <FontAwesomeIcon :icon="faSitemap" class="mr-1" />{{ workflow }}
              </span>
            </div>
            <p v-else class="text-text-muted">No workflows defined.</p>
          </div>

          <!-- Hardware Profiles Accordion -->
          <div>
            <h4 class="font-medium text-text-light mb-3 flex items-center">
              <FontAwesomeIcon :icon="faServer" class="mr-2" />Hardware Profiles ({{ Object.keys(selectedBundle.hardware_profiles || {}).length }})
            </h4>
            <div v-if="Object.keys(selectedBundle.hardware_profiles || {}).length > 0" class="space-y-2">
              <div 
                v-for="(profile, profileName) in selectedBundle.hardware_profiles" 
                :key="profileName"
                class="border border-border rounded-lg overflow-hidden"
              >
                <!-- Accordion Header -->
                <button
                  @click="toggleAccordionPanel(profileName)"
                  class="w-full px-4 py-3 bg-background-mute hover:bg-background-soft transition-colors duration-200 flex items-center justify-between text-left"
                >
                  <div class="flex items-center">
                    <FontAwesomeIcon :icon="faServer" class="mr-2 text-primary" />
                    <span class="font-medium text-text-light">{{ profileName }}</span>
                    <span class="ml-2 text-sm text-text-muted">({{ profile.models?.length || 0 }} models)</span>
                  </div>
                  <FontAwesomeIcon 
                    :icon="faDownload" 
                    :class="['transition-transform duration-200', openAccordionPanels.has(profileName) ? 'rotate-180' : '']"
                    class="text-text-muted"
                  />
                </button>
                
                <!-- Accordion Content -->
                <div 
                  v-show="openAccordionPanels.has(profileName)"
                  class="px-4 pb-4 bg-background-soft"
                >
                  <p v-if="profile.description" class="text-text-muted mb-3 mt-2">{{ profile.description }}</p>
                  
                  <!-- Models in this profile -->
                  <div v-if="profile.models?.length > 0">
                    <h6 class="text-sm font-medium text-text-light mb-2">Models:</h6>
                    <div class="grid grid-cols-1 gap-2 max-h-60 overflow-y-auto">
                      <div 
                        v-for="(model, index) in profile.models" 
                        :key="index"
                        class="flex items-center justify-between p-3 bg-background rounded border text-sm"
                      >
                        <div class="flex-1 min-w-0">
                          <div class="font-medium text-text-light truncate">
                            {{ getModelDisplayName(model) }}
                          </div>
                          <div class="text-xs text-text-muted mt-1">
                            <span class="inline-flex items-center mr-3">
                              <FontAwesomeIcon :icon="faCubes" class="mr-1" />{{ model.type }}
                            </span>
                            <span v-if="model.tags && model.tags.length > 0" class="inline-flex items-center">
                              Tags: {{ model.tags.join(', ') }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-text-muted text-sm">No models in this profile.</div>
                </div>
              </div>
            </div>
            <p v-else class="text-text-muted">No hardware profiles defined.</p>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 p-4 border-t border-border bg-background-mute">
          <button 
            type="button" 
            class="btn btn-secondary"
            @click="closeBundleDetails"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.download-bundles {
  padding: 16px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mr-1 {
  margin-right: 4px;
}

.mr-2 {
  margin-right: 8px;
}

.description {
  font-size: 1.2em;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.flex {
  display: flex;
}

.flex-wrap {
  flex-wrap: wrap;
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
