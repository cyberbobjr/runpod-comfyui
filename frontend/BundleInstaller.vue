<template>
  <div>
    <!-- Installed Bundles Panel (now at the top) -->
    <div class="card shadow-sm mb-4 installed-bundles-card">
      <div class="card-header bg-success">
        <h5 class="mb-0 text-white"><i class="fas fa-list me-2"></i>Installed Bundles</h5>
      </div>
      <div class="card-body installed-bundles-body">
        <div v-if="installedBundles.length === 0" class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>No bundles installed yet.
        </div>
        <div v-else class="table-responsive installed-bundles-table">
          <table class="table table-bordered">
            <thead class="table-light">
              <tr>
                <th><i class="fas fa-box-open me-1"></i>Bundle</th>
                <th><i class="fas fa-server me-1"></i>Hardware Profile</th>
                <th><i class="fas fa-sitemap me-1"></i>Workflow</th>
                <th><i class="fas fa-check-circle me-1"></i>Status</th>
                <th><i class="fas fa-cogs me-1"></i>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="installation in installedBundlesList" :key="installation.key">
                <td>{{ installation.bundleName }}</td>
                <td>{{ installation.profileName }}</td>
                <td>
                  <div v-if="bundleHasWorkflows(installation.bundleName)" class="d-flex flex-wrap gap-1">
                    <span v-for="(workflow, index) in getBundleWorkflows(installation.bundleName)" :key="index" class="badge bg-info">
                      <i class="fas fa-file-code me-1"></i>{{ workflow }}
                    </span>
                  </div>
                  <span v-else class="text-muted">None</span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="installation.completeStatus ? 'bg-success' : 'bg-warning'"
                  >
                    {{ installation.completeStatus ? 'Complete' : 'Partial' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="uninstallBundleByKey(installation.key)"
                    :disabled="isUninstallingMap[installation.key]"
                  >
                    <i class="fas fa-trash-alt me-1"></i>
                    <span v-if="isUninstallingMap[installation.key]">Uninstalling...</span>
                    <span v-else>Uninstall</span>
                  </button>
                  <div class="dropdown d-inline-block ms-1">
                    <!-- Use unique id for each dropdown -->
                    <button class="btn btn-sm btn-outline-primary dropdown-toggle" type="button"
                      :id="'workflowDropdown-' + installation.key"
                      data-bs-toggle="dropdown" aria-expanded="false">
                      <i class="fas fa-download me-1"></i>Workflows
                    </button>
                    <!-- Retire position-fixed, garde dropdown-menu-end -->
                    <ul class="dropdown-menu dropdown-menu-end workflow-dropdown-menu"
                        :aria-labelledby="'workflowDropdown-' + installation.key">
                      <li v-for="(workflow, index) in getBundleWorkflows(installation.bundleName)" :key="index">
                        <a class="dropdown-item" href="#" @click.prevent="downloadWorkflow(workflow)">
                          <i class="fas fa-file-code me-1"></i>{{ workflow }}
                        </a>
                      </li>
                      <li v-if="getBundleWorkflows(installation.bundleName).length > 1">
                        <hr class="dropdown-divider">
                      </li>
                      <li v-if="getBundleWorkflows(installation.bundleName).length > 1">
                        <a class="dropdown-item" href="#" @click.prevent="downloadAllWorkflows(installation.bundleName)">
                          <i class="fas fa-download me-1"></i>Download All
                        </a>
                      </li>
                    </ul>
                  </div>
                  <!-- Details button -->
                  <button 
                    class="btn btn-sm btn-outline-info ms-1"
                    @click="showBundleDetails(installation.bundleName, installation.profileName)"
                  >
                    <i class="fas fa-info-circle me-1"></i>Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <!-- End Installed Bundles Panel -->

    <!-- Install Bundle Panel (below) -->
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-primary">
        <h2 class="mb-0 text-white">Bundle Installer</h2>
      </div>
      <div class="card-body">
        <h4 class="card-title">
          <i class="fas fa-download me-2"></i>Install Bundles
        </h4>
        <p class="card-text">
          <i class="fas fa-info-circle me-2"></i>Install or uninstall predefined bundles of models.
        </p>

        <!-- Bundle Selection -->
        <div v-if="Object.keys(bundles).length > 0" class="mb-4">
          <div class="row mb-3 align-items-center">
            <div class="col-md-8 mb-2 mb-md-0">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="fas fa-box-open"></i>
                </span>
                <select v-model="selectedBundle" class="form-select">
                  <option value="">Select a bundle to install...</option>
                  <option v-for="(bundle, name) in bundles" :key="name" :value="name">
                    {{ name }} - {{ bundle.description }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="fas fa-server"></i>
                </span>
                <select v-model="selectedProfile" class="form-select" :disabled="!selectedBundle">
                  <option value="">Select hardware profile...</option>
                  <option 
                    v-for="(profile, profileName) in selectedBundleProfiles" 
                    :key="profileName" 
                    :value="profileName"
                  >
                    {{ profileName }} - {{ profile.description }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <div v-if="selectedBundle && selectedProfile" class="mb-4">
            <div class="card">
              <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-0">
                    <i class="fas fa-info-circle me-2"></i>Bundle Installation Details
                  </h5>
                  <div>
                    <button 
                      @click="installBundle" 
                      class="btn btn-primary"
                      :disabled="isInstalling || installedBundles.includes(bundleKey)"
                    >
                      <i class="fas fa-download me-1"></i>
                      <span v-if="isInstalling">Installing...</span>
                      <span v-else-if="installedBundles.includes(bundleKey)">Installed</span>
                      <span v-else>Install Bundle</span>
                    </button>
                    <button 
                      v-if="installedBundles.includes(bundleKey)" 
                      @click="uninstallBundle" 
                      class="btn btn-danger ms-2"
                      :disabled="isUninstalling"
                    >
                      <i class="fas fa-trash-alt me-1"></i>
                      <span v-if="isUninstalling">Uninstalling...</span>
                      <span v-else>Uninstall</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <h6><i class="fas fa-sitemap me-2"></i>Workflows</h6>
                  <div class="ms-4">
                    <div v-if="bundleWorkflows.length > 0">
                      <div v-for="(workflow, index) in bundleWorkflows" :key="index" class="badge bg-info me-2 mb-1">
                        <i class="fas fa-file-code me-1"></i>{{ workflow }}
                      </div>
                    </div>
                    <div v-else class="text-muted">No workflows defined</div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <h6><i class="fas fa-cubes me-2"></i>Models to be installed</h6>
                  <div class="table-responsive">
                    <table class="table table-bordered table-sm">
                      <thead class="table-light">
                        <tr>
                          <th>Model</th>
                          <th>Status</th>
                          <th>Size</th>
                          <th>Tags</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="model in bundleModelsList" :key="model.path">
                          <td>
                            <span :class="{'text-danger': isNSFW(model)}">
                              {{ getModelName(model.path) }}
                            </span>
                          </td>
                          <td>
                            <span 
                              class="badge" 
                              :class="model.exists ? 'bg-success' : 'bg-danger'"
                            >
                              {{ model.exists ? 'Present' : 'Missing' }}
                            </span>
                          </td>
                          <td>{{ formatSize(model.size) }}</td>
                          <td>
                            <span 
                              v-for="tag in model.tags" 
                              :key="tag" 
                              class="badge bg-secondary me-1"
                            >
                              {{ tag }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div>
                  <h6><i class="fas fa-chart-pie me-2"></i>Installation Summary</h6>
                  <div class="d-flex justify-content-between flex-wrap ms-4">
                    <div>
                      <strong>Total Models:</strong> {{ bundleModelsList.length }}
                    </div>
                    <div>
                      <strong>Missing Models:</strong> {{ bundleModelsList.filter(m => !m.exists).length }}
                    </div>
                    <div>
                      <strong>Total Download Size:</strong> {{ formatSize(totalDownloadSize) }}
                    </div>
                    <div v-if="estimatedDownloadTime">
                      <strong>Estimated Time:</strong> {{ estimatedDownloadTime }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>No bundles available. Create bundles in the Bundle Management section.
        </div>
      </div>
    </div>

    <!-- Bundle Details Modal -->
    <div class="modal fade" tabindex="-1" :class="{ show: showDetailsModal }" style="display: block;" v-if="showDetailsModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">
              <i class="fas fa-box-open me-2"></i>
              Bundle Details: {{ detailsBundleName }} <span v-if="detailsProfileName">({{ detailsProfileName }})</span>
            </h5>
            <button type="button" class="btn-close" @click="closeDetailsModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="detailsBundle">
              <div class="mb-3">
                <strong>Description:</strong> {{ detailsBundle.description || 'No description' }}
              </div>
              <div class="mb-3">
                <strong>Workflows:</strong>
                <span v-if="detailsWorkflows.length > 0">
                  <span v-for="(wf, i) in detailsWorkflows" :key="i" class="badge bg-info me-1">
                    <i class="fas fa-file-code me-1"></i>{{ wf }}
                  </span>
                </span>
                <span v-else class="text-muted">None</span>
              </div>
              <div class="mb-3">
                <strong>Models:</strong>
                <div class="table-responsive">
                  <table class="table table-bordered table-sm">
                    <thead class="table-light">
                      <tr>
                        <th>Model</th>
                        <th>Status</th>
                        <th>Size</th>
                        <th>Tags</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="model in detailsModelsList" :key="model.path">
                        <td>
                          <span :class="{'text-danger': isNSFW(model)}">
                            {{ getModelName(model.path) }}
                          </span>
                        </td>
                        <td>
                          <span 
                            class="badge" 
                            :class="model.exists ? 'bg-success' : 'bg-danger'"
                          >
                            {{ model.exists ? 'Present' : 'Missing' }}
                          </span>
                        </td>
                        <td>{{ formatSize(model.size) }}</td>
                        <td>
                          <span 
                            v-for="tag in model.tags" 
                            :key="tag" 
                            class="badge bg-secondary me-1"
                          >
                            {{ tag }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <strong>Summary:</strong>
                <ul>
                  <li>Total Models: {{ detailsModelsList.length }}</li>
                  <li>Missing Models: {{ detailsModelsList.filter(m => !m.exists).length }}</li>
                  <li>Total Download Size: {{ formatSize(detailsModelsList.filter(m => !m.exists).reduce((t, m) => t + (m.size || 0), 0)) }}</li>
                </ul>
              </div>
            </div>
            <div v-else>
              <span class="text-danger">Bundle not found.</span>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeDetailsModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <!-- End Bundle Details Modal -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useBundleInstallerLogic } from './BundleInstaller.logic.js';

const {
  bundles,
  installedBundles,
  selectedBundle,
  selectedProfile,
  isInstalling,
  isUninstalling,
  isUninstallingMap,
  selectedBundleProfiles,
  bundleKey,
  bundleModelsList,
  totalDownloadSize,
  estimatedDownloadTime,
  installedBundlesList,
  installBundle,
  uninstallBundle,
  uninstallBundleByKey,
  bundleWorkflows,
  getModelName,
  isNSFW,
  getBundleWorkflows,
  bundleHasWorkflows,
  downloadWorkflow,
  downloadAllWorkflows,
  formatSize
} = useBundleInstallerLogic();

// --- Details Modal Logic ---
const showDetailsModal = ref(false);
const detailsBundleName = ref('');
const detailsProfileName = ref('');
const detailsBundle = ref(null);

const detailsWorkflows = computed(() => {
  if (!detailsBundle.value) return [];
  if (detailsBundle.value.workflows) return detailsBundle.value.workflows;
  if (detailsBundle.value.workflow) return [detailsBundle.value.workflow];
  return [];
});

const detailsModelsList = computed(() => {
  if (!detailsBundle.value || !detailsProfileName.value) return [];
  const groupedModels = window.groupedModels ? window.groupedModels : {}; // fallback if not imported
  // Try to get groupedModels from logic if possible
  let _groupedModels = groupedModels;
  try {
    // Try to get from logic (if exported)
    _groupedModels = require('./App.logic.js').groupedModels.value;
  } catch {}
  const profile = detailsBundle.value.hardware_profiles?.[detailsProfileName.value];
  if (!profile) return [];
  const profileFilters = profile.model_filters || { include_tags: [], exclude_tags: [] };
  const matchesFilter = (model) => {
    const modelTags = model.entry.tags || [];
    const tagsArray = Array.isArray(modelTags) ? modelTags : [modelTags];
    if (profileFilters.exclude_tags.length > 0) {
      if (profileFilters.exclude_tags.some(tag => tagsArray.includes(tag))) {
        return false;
      }
    }
    if (profileFilters.include_tags.length > 0) {
      return profileFilters.include_tags.some(tag => tagsArray.includes(tag));
    }
    return true;
  };
  const result = [];
  detailsBundle.value.models.forEach(groupName => {
    const modelsInGroup = _groupedModels[groupName] || [];
    modelsInGroup.forEach(model => {
      if (matchesFilter(model)) {
        result.push({
          path: model.entry.dest || model.entry.git,
          exists: model.exists,
          size: model.entry.size || 0,
          tags: model.entry.tags || []
        });
      }
    });
  });
  return result;
});

function showBundleDetails(bundleName, profileName) {
  detailsBundleName.value = bundleName;
  detailsProfileName.value = profileName;
  detailsBundle.value = bundles.value[bundleName] || null;
  showDetailsModal.value = true;
}
function closeDetailsModal() {
  showDetailsModal.value = false;
}
// --- End Details Modal Logic ---
</script>

<style scoped>
/* Permet au dropdown de dépasser du panel sans scroll */
.installed-bundles-card,
.installed-bundles-body,
.installed-bundles-table {
  overflow: visible !important;
}

/* S'assure que le dropdown est au-dessus du panel */
.workflow-dropdown-menu {
  z-index: 2050 !important;
}

/* Aligne verticalement les cellules du tableau des bundles installés */
.installed-bundles-table td,
.installed-bundles-table th {
  vertical-align: middle !important;
}

/* Modal override for Vue (since we don't use Bootstrap JS here) */
.modal {
  display: block;
  background: rgba(0,0,0,0.5);
}
.modal .modal-dialog {
  margin-top: 5vh;
}
.modal.fade:not(.show) {
  display: none;
}
</style>
