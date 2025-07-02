<!--
 * DownloadBundlesComponent - TypeScript Vue Component
 * 
 * A comprehensive component for managing bundle downloads, installations, and uploads.
 * 
 * Features:
 * - Upload new bundles to the server
 * - View available and installed bundles
 * - Install/uninstall bundles with hardware profile selection
 * - View detailed bundle information including models and workflows
 * - Search and filter bundles
 * - Real-time status tracking of bundle installations
 * 
 * @remarks
 * This component has been fully migrated to TypeScript with:
 * - Strict type checking for all props, refs, and functions
 * - Comprehensive type definitions in bundles.types.ts
 * - Proper error handling with typed catch blocks
 * - Vue 3 Composition API with TypeScript support
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 *
 * DownloadBundlesComponent - Enhanced with Pinia Store Integration
 * 
 * This component has been updated to use the bundles Pinia store for:
 * - Fetching bundles and installed bundles data
 * - Deleting bundles 
 * - Managing bundle state centrally
 * 
 * The following functions now use store actions:
 * - loadUploadedBundles() -> bundlesStore.fetchBundles()
 * - loadInstalledBundles() -> bundlesStore.fetchInstalledBundles()
 * - deleteUploadedBundle() -> bundlesStore.deleteBundle()
 * 
 * Data access is now through computed properties:
 * - uploadedBundles -> computed(() => bundlesStore.bundles)
 * - installedBundles -> computed(() => bundlesStore.installedBundles)
 * - isStoreLoading -> computed(() => bundlesStore.isLoading)
-->

<template>
  <div class="p-4 bg-background space-y-6">
    <!-- Upload Bundle Card -->
    <CommonCard>
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
        Upload a JSON bundle file to add it to your collection. You can then
        install or manage it below.
      </p>
    </CommonCard>

    <!-- Uploaded Bundles List Card -->
    <CommonCard>
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-text-light flex items-center">
          <FontAwesomeIcon :icon="faBoxOpen" class="mr-2" />
          Uploaded Bundles
        </h2>
        <div class="flex items-center space-x-4">
          <div class="text-sm text-text-muted">
            {{ bundles.length }} bundle{{ bundles.length !== 1 ? "s" : "" }}
            uploaded
          </div>
          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search bundles"
              class="form-input pl-10"
            />
            <span
              class="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-light-muted"
            >
              <FontAwesomeIcon :icon="faSearch" />
            </span>
          </div>
        </div>
      </div>

      <div class="mb-6">
        <p class="text-text-muted mb-4 flex items-center">
          <FontAwesomeIcon :icon="faInfo" class="mr-2" />
          Manage your uploaded bundles: view details, install/uninstall, or
          delete them.
        </p>

        <!-- Loading state using store loading state -->
        <div class="relative min-h-[200px]">
          <div
            v-if="loading || isStoreLoading"
            class="absolute inset-0 flex items-center justify-center bg-background-soft bg-opacity-75 z-10"
          >
            <div class="flex flex-col items-center">
              <div
                class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"
              ></div>
              <span class="mt-2 text-text-light">Processing...</span>
            </div>
          </div>

          <!-- Uploaded Bundles List -->
          <div v-if="filteredBundles.length > 0" class="space-y-4">
            <div
              v-for="bundle in filteredBundles"
              :key="bundle.id"
              class="bg-background-soft border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <!-- Bundle Info -->
                <div class="flex-1">
                  <h4 class="text-lg font-semibold text-text-light mb-2">
                    {{ bundle.name }}
                  </h4>
                  <p
                    v-if="bundle.description"
                    class="text-text-muted text-sm mb-3"
                  >
                    {{ bundle.description }}
                  </p>

                  <!-- Hardware Profiles as Badges -->
                  <div class="mb-4">
                    <h5 class="text-sm font-medium text-text-light mb-2">
                      Hardware Profiles:
                    </h5>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="(
                          profile, profileName
                        ) in bundle.hardware_profiles"
                        :key="profileName"
                        :class="[
                          'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border',
                          getProfileModelStats(bundle, profileName)
                            .installed ===
                            getProfileModelStats(bundle, profileName).total &&
                          getProfileModelStats(bundle, profileName).total > 0
                            ? 'bg-green-100 text-green-800 border-green-200'
                            : getProfileModelStats(bundle, profileName)
                                .installed > 0
                            ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                            : 'bg-blue-100 text-blue-800 border-blue-200',
                        ]"
                      >
                        <FontAwesomeIcon :icon="faServer" class="mr-1" />
                        {{ profileName }}
                        <span class="ml-1">
                          ({{
                            getProfileModelStats(bundle, profileName).installed
                          }}/{{
                            getProfileModelStats(bundle, profileName).total
                          }})
                        </span>
                      </span>
                    </div>
                  </div>

                  <!-- Bundle Status -->
                  <div class="flex items-center text-sm">
                    <span class="mr-4 text-text-muted">
                      Status:
                      <span
                        class="font-medium"
                        :class="getUploadedBundleStatus(bundle).color"
                      >
                        {{ getUploadedBundleStatus(bundle).text }}
                      </span>
                    </span>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center space-x-2 ml-4">
                  <!-- View Details Button -->
                  <button
                    @click="viewBundleDetails(bundle)"
                    class="btn btn-secondary-outline text-sm h-8"
                    title="View bundle details"
                  >
                    <FontAwesomeIcon :icon="faInfo" class="mr-1" />
                    Details
                  </button>

                  <!-- Install/Download Dropdown -->
                  <ButtonDropdownComponent
                    v-if="getAvailableProfiles(bundle).length > 0"
                    button-text="Install"
                    :button-icon="faDownload"
                    size="xs"
                    variant="primary"
                    title="Install bundle profiles"
                    :dropdown-width="250"
                    dropdown-align="left"
                    @item-selected="(item: string) => handleProfileSelection(bundle, item)"
                  >
                    <template #default="{ handleItemClick }">
                      <div class="text-sm font-medium text-text-light mb-2">
                        Select profiles to install:
                      </div>
                      <div
                        v-for="profileName in getAvailableProfiles(bundle)"
                        :key="profileName"
                        class="flex items-center justify-between p-2 hover:bg-background-soft rounded cursor-pointer"
                        @click="handleItemClick(profileName)"
                      >
                        <span class="text-text-light text-sm">{{
                          profileName
                        }}</span>
                        <span class="text-text-muted text-xs">
                          {{
                            bundle.hardware_profiles?.[profileName]?.models
                              ?.length || 0
                          }}
                          models
                        </span>
                      </div>
                      <div class="border-t border-border mt-2 pt-2">
                        <div
                          class="w-full text-left p-2 text-sm text-primary hover:bg-background-soft rounded cursor-pointer"
                          @click="handleItemClick('install-all')"
                        >
                          Install All Profiles
                        </div>
                      </div>
                    </template>
                  </ButtonDropdownComponent>

                  <!-- Uninstall Button -->
                  <button
                    v-if="getInstalledProfiles(bundle).length > 0"
                    @click="uninstallBundle(bundle)"
                    class="btn btn-danger text-sm h-8"
                    title="Uninstall bundle"
                  >
                    <FontAwesomeIcon :icon="faTrashAlt" class="mr-1" />
                    Uninstall
                  </button>

                  <!-- Delete Button -->
                  <button
                    @click="deleteUploadedBundle(bundle)"
                    class="btn btn-danger text-sm h-8"
                    title="Delete bundle file"
                  >
                    <FontAwesomeIcon :icon="faTrashAlt" />
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center text-text-muted py-6">
            No bundles found.
          </div>
        </div>
      </div>
    </CommonCard>

    <!-- Bundle Details Modal -->
    <CommonModal :show="showBundleDetailsModal" @close="closeBundleDetails">
      <template #title> Bundle Details: {{ selectedBundle?.name }} </template>
      <template v-if="selectedBundle">
        <div>
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
                  <dd class="text-text-light">
                    {{ selectedBundle.version || "1.0.0" }}
                  </dd>
                </div>
                <div>
                  <dt class="text-sm text-text-muted">Author:</dt>
                  <dd class="text-text-light">
                    {{ selectedBundle.author || "N/A" }}
                  </dd>
                </div>
                <div v-if="selectedBundle.website">
                  <dt class="text-sm text-text-muted">Website:</dt>
                  <dd class="text-text-light">
                    <a
                      :href="selectedBundle.website"
                      target="_blank"
                      class="text-primary hover:underline"
                    >
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
              <FontAwesomeIcon :icon="faSitemap" class="mr-2" />Workflows ({{
                selectedBundle.workflows?.length || 0
              }})
            </h4>
            <div
              v-if="
                selectedBundle.workflows && selectedBundle.workflows.length > 0
              "
              class="flex flex-wrap gap-2"
            >
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
              <FontAwesomeIcon :icon="faServer" class="mr-2" />Hardware Profiles
              ({{ Object.keys(selectedBundle.hardware_profiles || {}).length }})
            </h4>
            <div
              v-if="
                Object.keys(selectedBundle.hardware_profiles || {}).length > 0
              "
              class="space-y-2"
            >
              <AccordionComponent
                v-for="(
                  profile, profileName
                ) in selectedBundle.hardware_profiles"
                :key="profileName"
                :title="
                  profileName +
                  ' (' +
                  (profile.models?.length || 0) +
                  ' models)'
                "
                icon="server"
                size="xs"
              >
                <div class="px-2 pb-2">
                  <p
                    v-if="profile.description"
                    class="text-text-muted mb-3 mt-2"
                  >
                    {{ profile.description }}
                  </p>
                  <div v-if="profile.models && profile.models.length > 0">
                    <h6 class="text-sm font-medium text-text-light mb-2">
                      Models:
                    </h6>
                    <div
                      class="grid grid-cols-1 gap-2 max-h-60 overflow-y-auto"
                    >
                      <div
                        v-for="(model, index) in profile.models"
                        :key="index"
                        class="flex items-center justify-between p-3 bg-background rounded border text-sm"
                      >
                        <div class="flex-1 min-w-0">
                          <div class="flex items-center">
                            <div
                              class="font-medium text-text-light truncate mr-3"
                            >
                              {{ getModelDisplayName(model) }}
                            </div>
                            <span
                              v-if="isModelInstalled(model)"
                              class="inline-flex items-center px-2 py-1 rounded text-xs bg-green-800 text-white"
                              title="Model is installed on disk"
                            >
                              <FontAwesomeIcon
                                :icon="faCheckCircle"
                                class="mr-1"
                              />
                              Installed
                            </span>
                            <span
                              v-else
                              class="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-600 text-white"
                              title="Model is not installed on disk"
                            >
                              <FontAwesomeIcon
                                :icon="faTimesCircle"
                                class="mr-1"
                              />
                              Not Installed
                            </span>
                          </div>
                          <div class="text-xs text-text-muted mt-1">
                            <span class="inline-flex items-center mr-3">
                              <FontAwesomeIcon :icon="faCubes" class="mr-1" />{{
                                model.type
                              }}
                            </span>
                            <span
                              v-if="model.tags && model.tags.length > 0"
                              class="inline-flex items-center"
                            >
                              Tags: {{ model.tags.join(", ") }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-text-muted text-sm">
                    No models in this profile.
                  </div>
                </div>
              </AccordionComponent>
            </div>
            <p v-else class="text-text-muted">No hardware profiles defined.</p>
          </div>
        </div>
      </template>
    </CommonModal>
  </div>
</template>
<script setup lang="ts">
/**
 * DownloadBundlesComponent
 *
 * Description:
 *   A comprehensive Vue 3 + TypeScript component for managing bundle downloads, installations, and uploads.
 *   Handles uploading, viewing, installing, uninstalling, and deleting bundles, with real-time status and Pinia store integration.
 *
 * Features:
 *   - Upload new bundles to the server
 *   - View available and installed bundles
 *   - Install/uninstall bundles with hardware profile selection
 *   - View detailed bundle information including models and workflows
 *   - Search and filter bundles
 *   - Real-time status tracking of bundle installations
 *
 * Props: None
 * Emits: None (uses Pinia store and composables for state and notifications)
 *
 * Methods:
 *   - uploadBundle(file: File): Promise<void>
 *     Description: Uploads a bundle file to the server and refreshes the bundles list.
 *     Parameters:
 *       - file (File): The bundle file to upload.
 *     Returns: Promise<void>
 *
 *   - handleBundleUpload(event: Event): Promise<void>
 *     Description: Handles the file input change event and triggers bundle upload.
 *     Parameters:
 *       - event (Event): The file input change event.
 *     Returns: Promise<void>
 *
 *   - triggerBundleUpload(): void
 *     Description: Programmatically triggers the file input for uploading a bundle.
 *     Parameters: None
 *     Returns: void
 *
 *   - getUploadedBundleStatus(bundle: Bundle): BundleStatus
 *     Description: Computes the status of an uploaded bundle based on installed profiles.
 *     Parameters:
 *       - bundle (Bundle): The bundle to check status for.
 *     Returns: BundleStatus
 *
 *   - uninstallBundle(bundle: Bundle): Promise<void>
 *     Description: Uninstalls a bundle by making an API call.
 *     Parameters:
 *       - bundle (Bundle): The bundle to uninstall.
 *     Returns: Promise<void>
 *
 *   - viewBundleDetails(bundle: Bundle): void
 *     Description: Opens the modal to view bundle details.
 *     Parameters:
 *       - bundle (Bundle): The bundle to view.
 *     Returns: void
 *
 *   - closeBundleDetails(): void
 *     Description: Closes the bundle details modal.
 *     Parameters: None
 *     Returns: void
 *
 *   - getProfileModelStats(bundle: Bundle, profileName: string): { installed: number; total: number }
 *     Description: Returns the number of installed and total models for a given hardware profile in a bundle.
 *     Parameters:
 *       - bundle (Bundle): The bundle to check.
 *       - profileName (string): The hardware profile name.
 *     Returns: Object with installed and total counts.
 *
 *   - getAvailableProfiles(bundle: Bundle): string[]
 *     Description: Returns a list of hardware profiles available for installation in a bundle.
 *     Parameters:
 *       - bundle (Bundle): The bundle to check.
 *     Returns: Array of profile names.
 *
 *   - getInstalledProfiles(bundle: Bundle): string[]
 *     Description: Returns a list of hardware profiles that are already installed for a bundle.
 *     Parameters:
 *       - bundle (Bundle): The bundle to check.
 *     Returns: Array of profile names.
 *
 *   - handleProfileSelection(bundle: Bundle, profileName: string): Promise<void>
 *     Description: Handles the selection of a hardware profile for installation.
 *     Parameters:
 *       - bundle (Bundle): The bundle to install.
 *       - profileName (string): The selected profile name.
 *     Returns: Promise<void>
 *
 *   - deleteUploadedBundle(bundle: Bundle): Promise<void>
 *     Description: Deletes an uploaded bundle using the Pinia store action.
 *     Parameters:
 *       - bundle (Bundle): The bundle to delete.
 *     Returns: Promise<void>
 *
 * Computed Properties:
 *   - bundles: List of uploaded bundles from the Pinia store.
 *   - isStoreLoading: Boolean indicating if the store is loading data.
 *   - filteredBundles: List of bundles filtered by the search query.
 *
 * State:
 *   - searchQuery: The current search string for filtering bundles.
 *   - loading: Boolean indicating if an upload or action is in progress.
 *   - showBundleDetailsModal: Boolean for showing the bundle details modal.
 *   - selectedBundle: The currently selected bundle for details view.
 *   - openAccordionPanels: Set of open accordion panel names in the modal.
 *
 * Usage:
 *   This component is used for managing bundles in the application, including upload, install, uninstall, and delete operations, with a modern UI and Pinia store integration.
 */
import {
  faBoxOpen,
  faCubes,
  faDownload,
  faInfo,
  faSearch,
  faServer,
  faSitemap,
  faUpload,
  faTrashAlt,
  faCheckCircle,
  faTimesCircle,
  faSync,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { computed, onMounted, ref } from "vue";
import { Model, useModelsStore } from "../stores/models";
import { useBundlesStore } from "../stores/bundles";
import { useNotifications } from "@/composables/useNotifications";
import CommonCard from "./common/CommonCard.vue";
import CommonModal from "./common/CommonModal.vue";
import AccordionComponent from "./common/AccordionComponent.vue";
import ButtonDropdownComponent from "./common/ButtonDropdownComponent.vue";
import { storeToRefs } from "pinia";
import { Bundle, BundleStatus } from "@/stores/types/bundles.types";

const { success, error, confirm } = useNotifications();
const modelsStore = useModelsStore();
const bundlesStore = useBundlesStore();
const searchQuery = ref<string>("");
const loading = ref<boolean>(false);
const showBundleDetailsModal = ref<boolean>(false);
const selectedBundle = ref<Bundle | null>(null);
const openAccordionPanels = ref<Set<string>>(new Set());

// Computed properties for store data access
const { bundles } = storeToRefs(bundlesStore);
const isStoreLoading = computed(() => bundlesStore.isLoading);

const filteredBundles = computed(() => {
  if (!searchQuery.value) {
    return bundles.value;
  }
  return bundles.value.filter((bundle) =>
    bundle.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Upload bundle - updated to refresh store data
const uploadBundle = async (file: File): Promise<void> => {
  loading.value = true;
  try {
    await bundlesStore.uploadBundleZip(file); // Use store action for upload

    success(`Bundle "${file.name}" uploaded successfully`);
  } catch (err: any) {
    error(
      "Failed to upload bundle: " + (err.response?.data?.detail || err.message)
    );
  } finally {
    loading.value = false;
  }
};

// Handle file upload
const handleBundleUpload = async (event: Event): Promise<void> => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    await uploadBundle(file);
    target.value = "";
  }
};

// Trigger file upload
const triggerBundleUpload = (): void => {
  const element = document.getElementById(
    "bundle-upload-file"
  ) as HTMLInputElement;
  element?.click();
};


// Get bundle status for uploaded bundles
const getUploadedBundleStatus = (bundle: Bundle): BundleStatus => {
  const profiles = Object.keys(bundle.hardware_profiles || {});
  const installedProfiles = profiles.filter((profile) =>
    bundlesStore.isBundleInstalled(bundle.id, profile)
  );

  if (installedProfiles.length === 0) {
    return {
      status: "not-installed",
      text: "Not Installed",
      color: "text-gray-400",
    };
  } else if (installedProfiles.length === profiles.length) {
    return {
      status: "fully-installed",
      text: "Fully Installed",
      color: "text-green-500",
    };
  } else {
    return {
      status: "partially-installed",
      text: `Partially Installed (${installedProfiles.length}/${profiles.length})`,
      color: "text-yellow-500",
    };
  }
};

// Uninstall bundle - keeping direct API call due to type incompatibility
const uninstallBundle = async (bundle: Bundle): Promise<void> => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to uninstall bundle "${bundle.name}"?`,
      "Confirm Uninstall"
    );

    if (confirmed) {
      loading.value = true;

      const profiles = Object.keys(bundle.hardware_profiles || {});
      for (const profileName of profiles) {
        if (bundlesStore.isBundleInstalled(bundle.id, profileName)) {
          await bundlesStore.uninstallBundle(bundle.id, profileName);
        }
      }

      success(`Bundle "${bundle.name}" uninstalled successfully`);
      await bundlesStore.fetchInstalledBundles();
    }
  } catch (err: any) {
    error(
      "Failed to uninstall bundle: " +
        (err.response?.data?.detail || err.message)
    );
  } finally {
    loading.value = false;
  }
};

// Delete uploaded bundle using store action
const deleteUploadedBundle = async (bundle: Bundle): Promise<void> => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to delete the uploaded bundle "${bundle.name}"? This will remove it from the server permanently.`,
      "Confirm Delete"
    );

    if (confirmed) {
      loading.value = true;

      await bundlesStore.deleteBundle(bundle.id);

      success(`Bundle "${bundle.name}" deleted successfully`);
      await bundlesStore.fetchInstalledBundles();
    }
  } catch (err: any) {
    error(
      "Failed to delete bundle: " + (err.response?.data?.detail || err.message)
    );
  } finally {
    loading.value = false;
  }
};

// View bundle details
const viewBundleDetails = (bundle: Bundle): void => {
  selectedBundle.value = bundle;
  showBundleDetailsModal.value = true;
};

// Close bundle details modal
const closeBundleDetails = (): void => {
  showBundleDetailsModal.value = false;
  selectedBundle.value = null;
  openAccordionPanels.value.clear();
};

// Get model display name
const getModelDisplayName = (model: Model): string => {
  if (model.dest) {
    return model.dest.split("/").pop() || "Unknown model";
  }
  if (model.url) {
    return model.url.split("/").pop() || "Unknown model";
  }
  return "Unknown model";
};

// Check if a model is installed using the modelsStore
const isModelInstalled = (model: Model): boolean => {
  return modelsStore.isModelInstalled(model);
};

// Load data on component mount using store actions
onMounted(async () => {
  await Promise.all([
    bundlesStore.fetchBundles(),
    bundlesStore.fetchInstalledBundles(),
    modelsStore.fetchModels(),
  ]);
});

// Get available profiles for installation (not already installed)
const getAvailableProfiles = (bundle: Bundle): string[] => {
  const profiles = Object.keys(bundle.hardware_profiles || {});
  return profiles.filter(
    (profile) => !bundlesStore.isBundleInstalled(bundle.id, profile)
  );
};

// Get installed profiles for a bundle
const getInstalledProfiles = (bundle: Bundle): string[] => {
  const profiles = Object.keys(bundle.hardware_profiles || {});
  return profiles.filter((profile) =>
    bundlesStore.isBundleInstalled(bundle.id, profile)
  );
};

// Get model installation count for a specific profile
const getProfileModelStats = (
  bundle: Bundle,
  profileName: string
): { installed: number; total: number } => {
  const profile = bundle.hardware_profiles?.[profileName];
  if (!profile || !profile.models) {
    return { installed: 0, total: 0 };
  }

  const totalModels = profile.models.length;
  const installedModels = profile.models.filter((model: Model) =>
    modelsStore.isModelInstalled(model)
  ).length;

  return { installed: installedModels, total: totalModels };
};

// Handle dropdown item selection for profile installation
const handleProfileSelection = (bundle: Bundle, profileName: string): void => {
  if (profileName === "install-all") {
    installAllProfiles(bundle);
  } else {
    installBundleProfile(bundle, [profileName]);
  }
};

// Install specific profile(s) for a bundle
const installBundleProfile = async (
  bundle: Bundle,
  profilesToInstall: string[]
): Promise<void> => {
  try {
    if (!profilesToInstall || profilesToInstall.length === 0) {
      error("Please select at least one profile to install");
      return;
    }

    // Start installation with progress tracking
    await modelsStore.startBundleInstallation(
      bundle.id,
      bundle.name,
      profilesToInstall
    );

    // Reload installed bundles after a delay
    setTimeout(async () => {
      await bundlesStore.fetchInstalledBundles();
    }, 2000);

    success(
      `Started installation of ${profilesToInstall.length} profile(s) for bundle "${bundle.name}"`
    );
  } catch (err: any) {
    error(
      "Failed to start profile installation: " +
        (err.response?.data?.detail || err.message)
    );
  }
};

// Install all available profiles (existing behavior)
const installAllProfiles = async (bundle: Bundle): Promise<void> => {
  const availableProfiles = getAvailableProfiles(bundle);
  if (availableProfiles.length === 0) {
    success(`Bundle "${bundle.name}" is already fully installed`);
    return;
  }
  await installBundleProfile(bundle, availableProfiles);
};
</script>

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
