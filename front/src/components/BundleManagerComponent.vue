<template>
  <!-- Bundle List Card -->
  <CommonCard v-if="!showBundleForm">
    <template #header>
      <h3><FontAwesomeIcon icon="box-open" class="mr-2" />Model Bundles</h3>
    </template>
    <p class="text-text-muted mb-4 flex items-center">
      <FontAwesomeIcon icon="info-circle" class="mr-2" />Create predefined
      bundles of models with associated workflows.
    </p>

    <!-- Bundle List -->
    <div v-if="Object.keys(bundles).length > 0" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-border">
        <thead class="bg-background-mute">
          <tr>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="tag" class="mr-1" />Name
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="code-branch" class="mr-1" />Version
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="user" class="mr-1" />Author
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="info" class="mr-1" />Description
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="sitemap" class="mr-1" />Workflows
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="server" class="mr-1" />Hardware Profiles
            </th>
            <th
              class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
            >
              <FontAwesomeIcon icon="cogs" class="mr-1" />Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-background-soft divide-y divide-border">
          <tr
            v-for="bundle in bundles"
            :key="bundle.id"
            class="hover:bg-background-mute"
          >
            <td class="px-4 py-3 text-text-light">{{ bundle.name }}</td>
            <td class="px-4 py-3 text-text-light">
              {{ bundle.version || "1.0.0" }}
            </td>
            <td class="px-4 py-3 text-text-light">
              {{ bundle.author || "N/A" }}
            </td>
            <td class="px-4 py-3 text-text-light">
              {{ bundle.description }}
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="workflow in bundle.workflows || []"
                  :key="workflow"
                  class="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-600 text-white"
                >
                  <FontAwesomeIcon icon="file-code" class="mr-1" />{{
                    workflow
                  }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="(profile, profileName) in bundle.hardware_profiles ||
                  {}"
                  :key="profileName"
                  class="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-600 text-white"
                >
                  <FontAwesomeIcon icon="microchip" class="mr-1" />{{
                    profileName
                  }}
                  ({{ profile.models?.length || 0 }} models)
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
                  class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                  @click="
                    downloadBundle(bundle.id, bundle.name, bundle.version)
                  "
                  title="Download bundle as ZIP"
                >
                  <FontAwesomeIcon icon="download" class="mr-1" />Download
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
    <div
      v-else
      class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded flex items-start"
    >
      <FontAwesomeIcon icon="info-circle" class="mr-2 mt-0.5" />
      <span>No bundles available. Create your first bundle below.</span>
    </div>

    <!-- New Bundle Button -->
    <div class="mt-4 flex justify-end">
      <button type="button" class="btn btn-primary" @click="createNewBundle">
        <FontAwesomeIcon icon="plus-circle" class="mr-1" />New Bundle
      </button>
    </div>
  </CommonCard>

  <BundleEditor
    v-if="showBundleForm"
    :bundle-id="currentBundle.id"
    @saved="afterBundleSaved"
    @cancel="returnToBundleList"
  />
</template>

<script setup>
import { ref,  onMounted } from "vue";
import { useNotifications } from "../composables/useNotifications";
import api from "../services/api";
import { useBundlesStore } from "../stores/bundles";
import CommonCard from "./common/CommonCard.vue";
import BundleEditor from "./bundle/BundleEditor.vue";
import { storeToRefs } from "pinia";

const { success, error, confirm } = useNotifications();
const bundleStore = useBundlesStore();

// State
const { bundles } = storeToRefs(bundleStore);
const showBundleForm = ref(false);

const currentBundle = ref({
  id: "",
  name: "",
  description: "",
  version: "1.0.0",
  author: "",
  website: "",
  workflows: [],
  hardware_profiles: {},
});

// Methods
const createNewBundle = () => {
  currentBundle.value.id = null;
  showBundleForm.value = true;
};

const afterBundleSaved = () => {
  showBundleForm.value = false;
  success("Bundle saved successfully");
};

const returnToBundleList = () => {
  showBundleForm.value = false;
};

// Lifecycle
onMounted(async () => {
  await Promise.all([bundleStore.fetchBundles()]);
});

const editBundle = async (bundleId) => {
  try {
    const bundle = bundleStore.getBundleById(bundleId); // Ensure store is updated

    currentBundle.value = {
      id: bundle.id,
      name: bundle.name,
      description: bundle.description,
      version: bundle.version || "1.0.0",
      author: bundle.author || "",
      website: bundle.website || "",
      workflows: bundle.workflows || [],
      hardware_profiles: bundle.hardware_profiles || {},
    };

    showBundleForm.value = true;
  } catch (err) {
    console.error("Error loading bundle for editing:", err);
    error("Failed to load bundle for editing");
  }
};

const handleDeleteBundle = async (bundleId) => {
  try {
    const bundle = bundles.value.find((b) => b.id === bundleId);
    const bundleName = bundle ? bundle.name : bundleId;

    const confirmed = await confirm(
      `Are you sure you want to delete bundle "${bundleName}"?`,
      "Confirm Deletion"
    );
    if (confirmed) {
      await bundleStore.deleteBundle(bundleId); // Use store method to delete
      success(`Bundle "${bundleName}" deleted successfully`);
    }
  } catch (err) {
    console.error("Error deleting bundle:", err);
    error(
      "Failed to delete bundle: " + (err.response?.data?.detail || err.message)
    );
  }
};

const downloadBundle = async (bundleId, bundleName, bundleVersion) => {
  try {
    const response = await api.get(`/bundles/download/${bundleId}`, {
      responseType: "blob",
    });

    // Create blob URL and trigger download
    const blob = new Blob([response.data], { type: "application/zip" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `bundle_${bundleName.replace(/\s+/g, "_")}_v${
      bundleVersion || "1.0.0"
    }.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    success(`Bundle "${bundleName}" downloaded successfully`);
  } catch (err) {
    console.error("Error downloading bundle:", err);
    error(
      "Failed to download bundle: " +
        (err.response?.data?.detail || err.message)
    );
  }
};
</script>

<style scoped>
/* Aligne verticalement les cellules du tableau des bundles dans le BundleManager */
.table-bordered td,
.table-bordered th {
  vertical-align: middle !important;
}

/* Fix for profile tabs layout */
.profile-tab {
  min-width: 200px;
  max-width: 300px;
}

/* Ensure dropdown appears above other content */
.profile-actions-dropdown {
  z-index: 1000;
}
</style>
