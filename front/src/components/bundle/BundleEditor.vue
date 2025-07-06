<template>
  <!-- Create/Edit Bundle Form -->
  <div class="space-y-6">
    <!-- Bundle Editor Header -->
    <CommonCard>
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <button
            type="button"
            class="btn btn-xs btn-secondary mr-4"
            @click="emitCancel"
            title="Return to bundle list"
          >
            <FontAwesomeIcon icon="arrow-left" class="mr-1" />Back
          </button>
          <h2 class="text-xl font-semibold text-text-light">
            <FontAwesomeIcon icon="box-open" class="mr-2" />
            <span v-if="currentBundle.id"
              >Edit Bundle: {{ currentBundle.name }}</span
            >
            <span v-else>Create New Bundle</span>
          </h2>
        </div>
        <div class="flex items-center space-x-2">
          <span
            v-if="currentBundle.id"
            class="text-sm text-blue-600 flex items-center"
          >
            <FontAwesomeIcon icon="edit" class="mr-1" />Editing
          </span>
          <span v-else class="text-sm text-green-600 flex items-center">
            <FontAwesomeIcon icon="plus" class="mr-1" />Creating
          </span>
        </div>
      </div>
    </CommonCard>

    <form @submit.prevent="handleSaveBundle" class="space-y-6">
      <!-- General Information Card -->
      <CommonCard>
        <template #header>
          <h4 class="text-lg font-medium text-text-light flex items-center">
            <FontAwesomeIcon icon="info-circle" class="mr-2" />General
            Information
          </h4>
        </template>

        <div class="space-y-4">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="form-label flex items-center">
                <FontAwesomeIcon icon="tag" class="mr-2" />UUID
              </label>
              <input
                type="text"
                class="form-input w-full"
                v-model="currentBundle.id"
                readonly
              />
            </div>
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
              <FontAwesomeIcon icon="info" class="mr-2" />Description
            </label>
            <textarea
              class="form-input w-full"
              v-model="currentBundle.description"
              rows="3"
              placeholder="Describe your bundle..."
            ></textarea>
          </div>
        </div>
      </CommonCard>

      <!-- Workflows Card -->
      <CommonCard>
        <template #header>
          <h4 class="text-lg font-medium text-text-light flex items-center">
            <FontAwesomeIcon icon="sitemap" class="mr-2" />Workflows
            <span
              v-if="currentBundle.workflows.length > 0"
              class="ml-2 text-sm text-blue-600"
            >
              ({{ currentBundle.workflows.length }} selected)
            </span>
          </h4>
        </template>

        <div class="space-y-4">
          <!-- Selected Workflows Display -->
          <div
            class="bg-background-soft border border-border rounded-lg p-3 min-h-[60px]"
          >
            <div
              v-if="currentBundle.workflows.length > 0"
              class="flex flex-wrap gap-2"
            >
              <span
                v-for="workflow in currentBundle.workflows"
                :key="workflow"
                class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-600 text-white group"
              >
                <FontAwesomeIcon icon="file-code" class="mr-1" />{{ workflow }}
                <button
                  type="button"
                  class="tag"
                  @click.stop="removeWorkflowFromSelection(workflow)"
                  title="Remove workflow"
                >
                  <FontAwesomeIcon icon="times" />
                </button>
              </span>
            </div>
            <div v-else class="text-text-muted text-sm flex items-center">
              <FontAwesomeIcon icon="info-circle" class="mr-1" />No workflows
              selected. Choose from the dropdown below.
            </div>
          </div>

          <!-- Workflow Dropdown -->
          <FormDropdownComponent
            label="Add Workflows"
            :icon="faPlusCircle"
            :items="availableWorkflows"
            @select="addWorkflowToSelection"
          >
          </FormDropdownComponent>

          <!-- Missing Workflows -->
          <div
            v-if="missingWorkflows.length > 0"
            class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
          >
            <div class="text-yellow-600 mb-2 flex items-center">
              <FontAwesomeIcon icon="exclamation-triangle" class="mr-1" />
              <strong>Missing workflows:</strong>
              <span class="ml-1 text-sm"
                >These workflows are referenced in this bundle but are not
                available in the system.</span
              >
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
          <div class="flex">
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
      </CommonCard>

      <!-- Hardware Profiles / Models Card -->
      <CommonCard>
        <div
          class="flex justify-between items-center cursor-pointer p-1 -m-1 rounded hover:bg-background-soft transition-colors"
          @click="showModelsSection = !showModelsSection"
        >
          <h4 class="text-lg font-medium text-text-light flex items-center">
            <FontAwesomeIcon icon="server" class="mr-2" />Hardware Profiles &
            Models
            <span
              v-if="Object.keys(currentBundle.hardware_profiles).length > 0"
              class="ml-2 text-sm text-green-600"
            >
              ({{ Object.keys(currentBundle.hardware_profiles).length }}
              profiles)
            </span>
          </h4>
          <FontAwesomeIcon
            :icon="showModelsSection ? 'chevron-up' : 'chevron-down'"
            class="text-text-muted"
          />
        </div>

        <div v-if="showModelsSection" class="mt-4">
          <!-- Profile Tabs -->
          <div class="border border-border rounded-lg overflow-hidden">
            <!-- Tab Headers -->
            <div class="bg-background-mute border-b border-border">
              <div class="flex overflow-x-auto">
                <div
                  v-for="(profile, name) in currentBundle.hardware_profiles"
                  :key="name"
                  class="flex-shrink-0 border-r border-border relative"
                >
                  <div class="flex items-center">
                    <button
                      type="button"
                      class="flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center min-w-0"
                      :class="
                        activeProfileTab === name
                          ? 'bg-background text-text-light border-b-2 border-primary'
                          : 'text-text-muted hover:text-text-light hover:bg-background-soft'
                      "
                      @click="activeProfileTab = name"
                    >
                      <div class="flex items-center min-w-0 mr-2">
                        <FontAwesomeIcon
                          icon="microchip"
                          class="mr-2 flex-shrink-0"
                        />
                        <span class="truncate">{{ name }}</span>
                        <span class="ml-1 text-xs opacity-75 flex-shrink-0"
                          >({{
                            formatFileSize(getProfileTotalSize(profile))
                          }})</span
                        >
                      </div>
                    </button>

                    <!-- Profile Actions Button -->
                    <button
                      type="button"
                      class="ml-2 p-1 text-xs text-text-muted hover:text-text-light hover:bg-background-soft rounded flex-shrink-0 profile-actions-container"
                      @click.stop="toggleProfileActions(name, $event)"
                      title="Profile actions"
                    >
                      <FontAwesomeIcon icon="cogs" />
                    </button>
                  </div>
                </div>

                <!-- Add Profile Tab -->
                <button
                  type="button"
                  class="flex-shrink-0 px-4 py-3 text-sm font-medium text-text-muted hover:text-text-light hover:bg-background-soft transition-colors flex items-center"
                  @click="addHardwareProfile"
                >
                  <FontAwesomeIcon icon="plus" class="mr-1" />
                </button>
              </div>
            </div>

            <!-- Tab Content -->
            <div
              v-if="
                activeProfileTab &&
                currentBundle.hardware_profiles[activeProfileTab]
              "
              class="p-4 space-y-4"
            >
              <!-- Profile Description -->
              <div>
                <label class="form-label flex items-center">
                  <FontAwesomeIcon icon="info" class="mr-2" />Description
                </label>
                <input
                  type="text"
                  class="form-input w-full"
                  v-model="
                    currentBundle.hardware_profiles[activeProfileTab]
                      .description
                  "
                  placeholder="Profile description"
                />
              </div>

              <!-- Profile Stats -->
              <div
                class="bg-background-soft border border-border rounded-lg p-3"
              >
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div class="flex items-center">
                    <FontAwesomeIcon icon="cubes" class="mr-2 text-primary" />
                    <span class="text-text-muted">Models:</span>
                    <span class="ml-1 font-medium text-text-light">
                      {{
                        currentBundle.hardware_profiles[activeProfileTab].models
                          ?.length || 0
                      }}
                    </span>
                  </div>
                  <div class="flex items-center">
                    <FontAwesomeIcon
                      icon="database"
                      class="mr-2 text-primary"
                    />
                    <span class="text-text-muted">Total Size:</span>
                    <span class="ml-1 font-medium text-text-light">
                      {{
                        formatFileSize(
                          getProfileTotalSize(
                            currentBundle.hardware_profiles[activeProfileTab]
                          )
                        )
                      }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Model Selection for this Profile -->
              <div>
                <div class="flex justify-between items-center mb-2">
                  <label class="form-label flex items-center mb-0">
                    <FontAwesomeIcon icon="cubes" class="mr-2" />Models for this
                    Profile
                  </label>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline"
                    @click="showModelSelector(activeProfileTab)"
                  >
                    <FontAwesomeIcon icon="plus-circle" class="mr-1" />Add
                    Models
                  </button>
                </div>

                <!-- Selected Models Display -->
                <div
                  class="bg-background-soft border border-border rounded-lg p-3 min-h-[60px] mb-2"
                >
                  <div
                    v-if="
                      currentBundle.hardware_profiles[activeProfileTab]
                        .models &&
                      currentBundle.hardware_profiles[activeProfileTab].models
                        .length > 0
                    "
                    class="space-y-2"
                  >
                    <div
                      v-for="(model, index) in currentBundle.hardware_profiles[
                        activeProfileTab
                      ].models"
                      :key="index"
                      class="flex items-center justify-between p-2 bg-background rounded border"
                    >
                      <div class="flex-1 min-w-0">
                        <div
                          class="text-sm font-medium text-text-light truncate"
                        >
                          {{ getModelDisplayName(model) }}
                        </div>
                        <div class="text-xs text-text-muted">
                          <span class="inline-flex items-center mr-2">
                            <FontAwesomeIcon icon="tag" class="mr-1" />{{
                              model.type
                            }}
                          </span>
                          <span
                            v-if="model.tags && model.tags.length > 0"
                            class="inline-flex items-center mr-2"
                          >
                            <FontAwesomeIcon icon="tags" class="mr-1" />{{
                              model.tags.join(", ")
                            }}
                          </span>
                          <span
                            v-if="model.size"
                            class="inline-flex items-center"
                          >
                            <FontAwesomeIcon icon="database" class="mr-1" />{{
                              formatFileSize(model.size)
                            }}
                          </span>
                        </div>
                      </div>
                      <button
                        type="button"
                        class="ml-2 text-red-600 hover:text-red-800"
                        @click="removeModelFromProfile(activeProfileTab, index)"
                        title="Remove model"
                      >
                        <FontAwesomeIcon icon="trash-alt" />
                      </button>
                    </div>
                  </div>
                  <div v-else class="text-text-muted text-sm flex items-center">
                    <FontAwesomeIcon icon="info-circle" class="mr-1" />No models
                    selected for this profile.
                  </div>
                </div>
              </div>
            </div>

            <!-- No Profiles Message -->
            <div
              v-if="Object.keys(currentBundle.hardware_profiles).length === 0"
              class="p-8 text-center"
            >
              <FontAwesomeIcon
                icon="server"
                class="text-4xl text-text-muted mb-4"
              />
              <h4 class="text-lg font-medium text-text-light mb-2">
                No Hardware Profiles
              </h4>
              <p class="text-text-muted mb-4">
                Create your first hardware profile to start adding models.
              </p>
              <button
                type="button"
                class="btn btn-primary"
                @click="addHardwareProfile"
              >
                <FontAwesomeIcon icon="plus-circle" class="mr-1" />Create First
                Profile
              </button>
            </div>
          </div>
        </div>
      </CommonCard>

      <!-- Form Buttons -->
      <CommonCard>
        <div class="flex justify-between items-center">
          <button type="button" class="btn btn-secondary" @click="emitCancel">
            <FontAwesomeIcon icon="arrow-left" class="mr-1" />Back
          </button>
          <div class="flex space-x-3">
            <button
              type="button"
              class="btn btn-outline"
              @click="resetBundleForm"
            >
              <FontAwesomeIcon icon="undo" class="mr-1" />Reset Form
            </button>
            <button type="submit" class="btn btn-primary">
              <FontAwesomeIcon
                :icon="currentBundle.id ? 'save' : 'plus'"
                class="mr-1"
              />
              {{ currentBundle.id ? "Update" : "Create" }} Bundle
            </button>
          </div>
        </div>
      </CommonCard>
    </form>
  </div>

  <!-- Profile Actions Dropdown (positioned fixed outside all containers) -->
  <div
    v-if="profileActionsOpen"
    class="fixed bg-background border border-border rounded shadow-lg z-[9999] min-w-[150px] profile-actions-container"
    :style="{
      top: dropdownPosition.top,
      left: dropdownPosition.left,
    }"
    @click.stop
  >
    <button
      type="button"
      class="w-full px-3 py-2 text-left text-sm text-text-light hover:bg-background-soft flex items-center"
      @click="startRenameProfile(profileActionsOpen)"
    >
      <FontAwesomeIcon icon="edit" class="mr-2" />Rename
    </button>
    <button
      type="button"
      class="w-full px-3 py-2 text-left text-sm text-text-light hover:bg-background-soft flex items-center"
      @click="cloneProfile(profileActionsOpen)"
    >
      <FontAwesomeIcon icon="copy" class="mr-2" />Clone
    </button>
    <button
      type="button"
      class="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center"
      @click="removeHardwareProfile(profileActionsOpen)"
    >
      <FontAwesomeIcon icon="trash-alt" class="mr-2" />Delete
    </button>
  </div>

  <!-- Model Selector Modal -->
  <ModelSelectorModal
    v-if="showModelSelectorModal"
    :show="showModelSelectorModal"
    :currentProfileName="currentProfileName"
    :groupedModels="models"
    :selectedModels="selectedModels"
    :popularTags="popularTags"
    @close="closeModelSelector"
    @apply-selection="applyModelSelection"
    @update:selectedModels="selectedModels = $event"
  />

  <!-- Rename Profile Modal -->
  <div
    v-if="showRenameModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]"
  >
    <div class="bg-background rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="flex justify-between items-center p-4 border-b border-border">
        <h3 class="text-lg font-semibold text-text-light">Rename Profile</h3>
        <button
          type="button"
          class="text-text-muted hover:text-text-light"
          @click="cancelRenameProfile"
        >
          <FontAwesomeIcon icon="times" class="text-xl" />
        </button>
      </div>

      <div class="p-4">
        <label class="form-label flex items-center mb-2">
          <FontAwesomeIcon icon="tag" class="mr-2" />Profile Name
        </label>
        <input
          ref="renameProfileInput"
          type="text"
          class="form-input w-full"
          v-model="newProfileName"
          @keyup.enter="confirmRenameProfile"
          @keyup.escape="cancelRenameProfile"
          placeholder="Enter new profile name"
        />
      </div>

      <div
        class="flex justify-end space-x-3 p-4 border-t border-border bg-background-mute"
      >
        <button
          type="button"
          class="btn btn-secondary"
          @click="cancelRenameProfile"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="confirmRenameProfile"
          :disabled="!newProfileName.trim()"
        >
          <FontAwesomeIcon icon="save" class="mr-1" />Rename
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useBundlesStore } from "@/stores/bundles";
import { useWorkflowsStore } from "@/stores/workflows";
import { useNotifications } from "@/composables/useNotifications";
import { useModelsStore } from "@/stores/models";
import CommonCard from "@/components/common/CommonCard.vue";
import FormDropdownComponent from "@/components/common/FormDropdownComponent.vue";
import ModelSelectorModal from "@/components/common/ModelSelectorModal.vue";
import { storeToRefs } from "pinia";
import { faPlusCircle } from "@fortawesome/free-solid-svg-icons";

const props = defineProps({
  bundleId: {
    type: [String, null],
    default: "",
  },
});

const emit = defineEmits(["saved", "cancel"]);

const { success, error, confirm } = useNotifications();
const bundleStore = useBundlesStore();
const workflowsStore = useWorkflowsStore();
const modelsStore = useModelsStore();
const { workflows } = storeToRefs(workflowsStore);
const { models } = storeToRefs(modelsStore);

const showModelsSection = ref(true);
const dropdownPosition = ref({ top: "0px", left: "0px" });
const showRenameModal = ref(false);
const newProfileName = ref("");
const profileActionsOpen = ref("");
const showWorkflowDropdown = ref(false);
const showModelSelectorModal = ref(false);
const currentProfileName = ref("");
const selectedModels = ref([]);
const showFilterSection = ref(false);
const renamingProfile = ref("");
const activeProfileTab = ref("");
const modelFilter = ref("");
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

// Charger le bundle si bundleId fourni
onMounted(async () => {
  if (props.bundleId) {
    const b = bundleStore.getBundleById(props.bundleId);
    currentBundle.value = {
      id: b.id,
      name: b.name,
      description: b.description,
      version: b.version || "1.0.0",
      author: b.author || "",
      website: b.website || "",
      workflows: b.workflows || [],
      hardware_profiles: b.hardware_profiles || {},
    };
  }
  await workflowsStore.fetchWorkflows();
  await modelsStore.fetchModels();

  // Auto-select first hardware profile if any exist
  const profileNames = Object.keys(currentBundle.value.hardware_profiles);
  if (profileNames.length > 0) {
    activeProfileTab.value = profileNames[0];
  }

  // Close dropdowns when clicking outside
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".relative")) {
      closeDropdowns();
    }
    // Close profile actions dropdown
    closeProfileActions(event);
  });
});
// Close dropdowns when clicking outside
const closeDropdowns = () => {
  showWorkflowDropdown.value = false;
  profileActionsOpen.value = "";
};
// Close profile actions when clicking outside
const closeProfileActions = (event) => {
  // Check if click is outside of any profile actions dropdown
  if (!event.target.closest(".profile-actions-container")) {
    profileActionsOpen.value = "";
  }
};

// Computed for missing workflows
const missingWorkflows = computed(() => {
  if (!currentBundle.value.workflows) return [];

  return currentBundle.value.workflows.filter(
    (workflow) => !workflows.value.includes(workflow)
  );
});

// Computed for available workflows (not yet selected)
const availableWorkflows = computed(() => {
  return workflows.value.filter(
    (workflow) => !currentBundle.value.workflows.includes(workflow)
  );
});

// Computed for popular tags
const popularTags = computed(() => {
  const tagCounts = {};

  for (const models of Object.values(models.value)) {
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

const removeWorkflowFromBundle = async (workflow) => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to remove "${workflow}" from this bundle?`,
      "Confirm Removal"
    );

    if (confirmed) {
      const index = currentBundle.value.workflows.indexOf(workflow);
      if (index !== -1) {
        currentBundle.value.workflows.splice(index, 1);
        success(`Workflow "${workflow}" removed from bundle`);
      }
    }
  } catch (err) {
    error("Failed to remove workflow from bundle: " + err.message);
  }
};

const closeModelSelector = () => {
  showModelSelectorModal.value = false;
  currentProfileName.value = "";
  selectedModels.value = [];
  modelFilter.value = "";
  showFilterSection.value = false;
};

const handleWorkflowUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    await uploadWorkflow(file);
    event.target.value = "";
  }
};

const triggerWorkflowUpload = () => {
  document.getElementById("workflow-file").click();
};

const getModelDisplayName = (model) => {
  if (model.dest) {
    return model.dest.split("/").pop();
  }
  if (model.url) {
    return model.url.split("/").pop();
  }
  return "Unknown model";
};

const formatFileSize = (bytes) => {
  if (!bytes) return "Unknown size";
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const showModelSelector = (profileName) => {
  currentProfileName.value = profileName;
  selectedModels.value = [
    ...(currentBundle.value.hardware_profiles[profileName]?.models || []),
  ];
  modelFilter.value = "";
  showFilterSection.value = false;
  showModelSelectorModal.value = true;
};

const applyModelSelection = () => {
  if (!currentBundle.value.hardware_profiles[currentProfileName.value]) {
    currentBundle.value.hardware_profiles[currentProfileName.value] = {
      description: "",
      models: [],
    };
  }

  currentBundle.value.hardware_profiles[currentProfileName.value].models = [
    ...selectedModels.value,
  ];
  closeModelSelector();
};

const removeModelFromProfile = (profileName, modelIndex) => {
  if (currentBundle.value.hardware_profiles[profileName]?.models) {
    currentBundle.value.hardware_profiles[profileName].models.splice(
      modelIndex,
      1
    );
  }
};

// Calculate total size of a profile
const getProfileTotalSize = (profile) => {
  if (!profile.models || profile.models.length === 0) {
    return 0;
  }

  return profile.models.reduce((total, model) => {
    return total + (model.size || 0);
  }, 0);
};

// Toggle profile actions dropdown
const toggleProfileActions = (profileName, event) => {
  if (profileActionsOpen.value === profileName) {
    profileActionsOpen.value = "";
  } else {
    profileActionsOpen.value = profileName;

    // Calculate position for the dropdown
    const buttonRect = event.target.getBoundingClientRect();
    dropdownPosition.value = {
      top: buttonRect.bottom + window.scrollY + 4 + "px",
      left: buttonRect.right - 150 + "px", // 150px is the min-width of dropdown
    };
  }
};

// Start renaming a profile
const startRenameProfile = (profileName) => {
  renamingProfile.value = profileName;
  newProfileName.value = profileName;
  profileActionsOpen.value = "";
  showRenameModal.value = true;

  // Focus the input after the modal opens
  nextTick(() => {
    const input = document.querySelector('input[ref="renameProfileInput"]');
    if (input) {
      input.focus();
      input.select();
    }
  });
};

// Confirm renaming a profile
const confirmRenameProfile = () => {
  if (renamingProfile.value && newProfileName.value.trim()) {
    const trimmedName = newProfileName.value.trim();
    if (trimmedName !== renamingProfile.value) {
      updateProfileName(renamingProfile.value, trimmedName);
    }
  }
  cancelRenameProfile();
};

// Cancel renaming a profile
const cancelRenameProfile = () => {
  renamingProfile.value = "";
  newProfileName.value = "";
  showRenameModal.value = false;
};

const cloneProfile = (profileName) => {
  const profile = currentBundle.value.hardware_profiles[profileName];
  if (!profile) return;

  // Find a unique name for the cloned profile
  let clonedName = `${profileName} Copy`;
  let counter = 1;

  while (currentBundle.value.hardware_profiles[clonedName]) {
    clonedName = `${profileName} Copy ${counter}`;
    counter++;
  }

  // Clone the profile
  currentBundle.value.hardware_profiles[clonedName] = {
    description: profile.description,
    models: [...(profile.models || [])],
  };

  // Switch to the new profile tab
  activeProfileTab.value = clonedName;
  profileActionsOpen.value = "";

  success(`Profile "${profileName}" cloned as "${clonedName}"`);
};

const addHardwareProfile = () => {
  // Find a unique name for the new profile
  let profileName = "New Profile";
  let counter = 1;

  while (currentBundle.value.hardware_profiles[profileName]) {
    profileName = `New Profile ${counter}`;
    counter++;
  }

  currentBundle.value.hardware_profiles[profileName] = {
    description: "",
    models: [],
  };

  // Switch to the new profile tab
  activeProfileTab.value = profileName;
  profileActionsOpen.value = "";
};

const removeHardwareProfile = async (name) => {
  try {
    const confirmed = await confirm(
      `Are you sure you want to delete profile "${name}"?`,
      "Confirm Delete"
    );
    if (confirmed) {
      delete currentBundle.value.hardware_profiles[name];

      // Switch to another tab if the deleted one was active
      if (activeProfileTab.value === name) {
        const remainingProfiles = Object.keys(
          currentBundle.value.hardware_profiles
        );
        activeProfileTab.value =
          remainingProfiles.length > 0 ? remainingProfiles[0] : "";
      }

      profileActionsOpen.value = "";
      success(`Profile "${name}" deleted successfully`);
    }
  } catch (err) {
    error("Failed to delete profile: " + err.message);
  }
};

const updateProfileName = (oldName, newName) => {
  // Trim and validate the new name
  const trimmedName = newName.trim();

  // If name is empty or unchanged, do nothing
  if (!trimmedName || trimmedName === oldName) {
    renamingProfile.value = "";
    return;
  }

  // Check if the new name already exists
  if (currentBundle.value.hardware_profiles[trimmedName]) {
    error(`Profile name "${trimmedName}" already exists`);
    return;
  }

  // Create new profile with the new name
  const profileData = currentBundle.value.hardware_profiles[oldName];
  currentBundle.value.hardware_profiles[trimmedName] = {
    description: profileData.description,
    models: [...(profileData.models || [])],
  };

  // Remove the old profile
  delete currentBundle.value.hardware_profiles[oldName];

  // Switch to the new profile tab
  activeProfileTab.value = trimmedName;
  profileActionsOpen.value = "";

  success(`Profile renamed from "${oldName}" to "${trimmedName}"`);
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

function emitCancel() {
  resetBundleForm();
  emit("cancel");
}

async function handleSaveBundle() {
  try {
    const bundleData = {
      name: currentBundle.value.name,
      description: currentBundle.value.description,
      version: currentBundle.value.version,
      author: currentBundle.value.author || null,
      website: currentBundle.value.website || null,
      workflows: currentBundle.value.workflows,
      hardware_profiles: currentBundle.value.hardware_profiles,
    };
    if (currentBundle.value.id) {
      await bundleStore.updateBundle(currentBundle.value.id, bundleData);
      success(`Bundle "${currentBundle.value.name}" updated successfully`);
    } else {
      const newBundleData = await bundleStore.createBundle(bundleData);
      currentBundle.value.id = newBundleData.id; // Update local bundle with new ID
      success(`Bundle "${currentBundle.value.name}" created successfully`);
    }
    await bundleStore.fetchBundles(); // Ensure store is updated
    // emit("saved");
  } catch (err) {
    error(
      "Failed to save bundle: " + (err.response?.data?.detail || err.message)
    );
  }
}

const uploadWorkflow = async (file) => {
  try {
    await workflowsStore.uploadWorkflow(file);
    success(`Workflow "${file.name}" uploaded successfully`);
  } catch (err) {
    console.error("Error uploading workflow:", err);
    error(
      "Failed to upload workflow: " +
        (err.response?.data?.detail || err.message)
    );
  }
};

function resetBundleForm() {
  currentBundle.value = {
    id: "",
    name: "",
    description: "",
    version: "1.0.0",
    author: "",
    website: "",
    workflows: [],
    hardware_profiles: {},
  };
}
</script>
<style scoped>
.tag {
  @apply ml-2 w-4 h-4 flex items-center justify-center rounded-full bg-blue-500 hover:bg-red-500 text-white text-xs transition-colors duration-200 flex-shrink-0;
}
</style>
