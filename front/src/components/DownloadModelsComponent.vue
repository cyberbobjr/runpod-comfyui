<template>
  <div class="download-models-container w-full p-4 space-y-4">
    <!-- Supprimer la card "Active Downloads" -->

    <!-- Model Manager Card -->
    <div
      class="models-card bg-background-soft border border-border rounded-lg shadow-md"
    >
      <div class="flex items-center justify-between p-4 border-b border-border">
        <div class="flex items-center gap-2">
          <svg
            class="w-6 h-6 text-white"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
            />
          </svg>
          <span class="text-lg font-bold text-white">Model Manager</span>
        </div>
        <div class="header-actions flex gap-2">
          <button
            :disabled="!hasSelectedToDelete"
            @click="confirmDeleteSelected"
            :class="[
              'px-4 py-2 rounded text-sm font-medium transition-colors',
              hasSelectedToDelete
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed',
            ]"
          >
            Delete selected
          </button>
          <button
            :disabled="!hasSelectedToDownload"
            @click="confirmDownloadSelected"
            :class="[
              'px-4 py-2 rounded text-sm font-medium transition-colors',
              hasSelectedToDownload
                ? 'bg-primary hover:bg-primary-dark text-white'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed',
            ]"
          >
            Download selected
          </button>
        </div>
      </div>

      <div class="p-4 space-y-4">
        <!-- Filter Section -->
        <div
          class="filter-section bg-background-mute border border-border rounded-lg p-4 space-y-3"
        >
          <div class="flex items-center gap-2 mb-2">
            <svg
              class="w-5 h-5 text-text-light"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z"
              />
            </svg>
            <span class="font-medium text-text-light">Filters</span>
            <button
              v-if="filterText || selectedTagFilters.length > 0"
              @click="clearFilters"
              class="ml-auto px-2 py-1 text-xs bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
            >
              Clear All
            </button>
          </div>

          <!-- Search Input -->
          <div class="relative">
            <input
              v-model="filterText"
              type="text"
              placeholder="Search by name or tags..."
              class="w-full px-3 py-2 pl-10 bg-background border border-border rounded-md text-text-light placeholder-text-light-muted focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <svg
              class="absolute left-3 top-2.5 w-4 h-4 text-text-light-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>

          <!-- Tag Filters -->
          <div v-if="allTags.length > 0" class="space-y-2">
            <span class="text-sm font-medium text-text-light"
              >Filter by tags:</span
            >
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in allTags"
                :key="tag"
                @click="toggleTagFilter(tag)"
                :class="[
                  'px-3 py-1 text-xs rounded-full border transition-colors',
                  selectedTagFilters.includes(tag)
                    ? 'bg-primary text-white border-primary'
                    : 'bg-background border-border text-text-light hover:bg-background-mute',
                ]"
              >
                {{ tag }}
                <span v-if="selectedTagFilters.includes(tag)" class="ml-1"
                  >×</span
                >
              </button>
            </div>
          </div>

          <!-- Filter Summary -->
          <div
            v-if="filterText || selectedTagFilters.length > 0"
            class="text-xs text-text-light-muted"
          >
            Showing {{ filteredModels.length }} of {{ models.length }} models
            <span v-if="filterText"> matching "{{ filterText }}"</span>
            <span v-if="selectedTagFilters.length > 0">
              with tags: {{ selectedTagFilters.join(", ") }}</span
            >
          </div>
        </div>

        <div
          v-if="Object.keys(filteredGroupedModels).length === 0"
          class="text-center text-text-light-muted py-8"
        >
          {{
            filterText || selectedTagFilters.length > 0
              ? "No models match the current filters."
              : "No models found."
          }}
        </div>
        <div v-else class="space-y-4">
          <AccordionComponent
            v-for="(groupModels, groupName) in filteredGroupedModels"
            :key="groupName"
            :title="groupName"
            :size="'xs'"
            :defaultOpen="expandedGroups.includes(groupName)"
            @toggle="(isOpen) => handleGroupToggle(groupName, isOpen)"
          >
            <div class="table-responsive">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead class="bg-background-mute">
                    <tr>
                      <th class="p-2 text-left">
                        <input
                          type="checkbox"
                          :checked="allChecked(groupModels)"
                          @change="
                            (e) => toggleAll(groupModels, (e.target as HTMLInputElement)?.checked || false)
                          "
                          :disabled="
                            groupModels.every((row) => isDownloading(row))
                          "
                          class="rounded"
                        />
                      </th>
                      <th class="p-2 text-left text-text-light">Name</th>
                      <th class="p-2 text-left text-text-light">Tags</th>
                      <th class="p-2 text-left text-text-light">Type</th>
                      <th class="p-2 text-left text-text-light">Size</th>
                      <th class="p-2 text-left text-text-light">Source</th>
                      <th class="p-2 text-left text-text-light">Present</th>
                      <th class="p-2 text-left text-text-light">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="model in groupModels"
                      :key="modelKey(model)"
                      :class="[
                        'border-b border-border hover:bg-background-mute transition-colors',
                        isDownloading(model) ? 'is-downloading' : '',
                      ]"
                    >
                      <td class="p-2">
                        <input
                          type="checkbox"
                          :checked="selected[modelKey(model)] || false"
                          @change="
                            (e) => handleRowCheck(model, (e.target as HTMLInputElement)?.checked || false)
                          "
                          :disabled="isDownloading(model)"
                          class="rounded"
                        />
                      </td>
                      <td class="p-2">
                        <span
                          :class="[
                            'font-medium',
                            isDownloading(model) ? 'opacity-50' : '',
                            isNSFW(model) ? 'text-red-400' : 'text-text-light',
                          ]"
                        >
                          {{ lastPath(model.dest) || model.git }}
                        </span>
                      </td>
                      <td class="p-2">
                        <div
                          v-if="model.tags && model.tags.length"
                          class="flex flex-wrap gap-1"
                        >
                          <span
                            v-for="tag in Array.isArray(model.tags)
                              ? model.tags
                              : [model.tags]"
                            :key="tag"
                            class="px-2 py-1 bg-blue-600 text-white text-xs rounded"
                          >
                            {{ tag }}
                          </span>
                        </div>
                        <span v-else class="text-text-light-muted">-</span>
                      </td>
                      <td class="p-2 text-text-light">
                        {{ model.type || groupName }}
                      </td>
                      <td class="p-2 text-text-light">
                        {{ model.size ? formatSize(model.size) : "-" }}
                      </td>
                      <td class="p-2">
                        <a
                          v-if="model.src"
                          :href="model.src"
                          target="_blank"
                          rel="noopener"
                          class="text-primary hover:text-primary-light underline"
                        >
                          Link
                        </a>
                        <span v-else class="text-text-light-muted">-</span>
                      </td>
                      <td class="p-2">
                        <span
                          :class="[
                            'px-2 py-1 text-xs rounded',
                            model.exists
                              ? 'bg-green-600 text-white'
                              : 'bg-red-600 text-white',
                          ]"
                        >
                          {{ model.exists ? "Yes" : "No" }}
                        </span>
                      </td>
                      <td class="p-2">
                        <div class="flex gap-2">
                          <button
                            v-if="!model.exists"
                            @click="confirmDownload(model)"
                            :disabled="isDownloading(model)"
                            :class="[
                              'px-3 py-1 rounded text-sm transition-colors',
                              isDownloading(model)
                                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                : 'bg-primary hover:bg-primary-dark text-white',
                            ]"
                          >
                            Download
                          </button>
                          <button
                            v-if="model.exists"
                            @click="confirmDelete(model)"
                            :disabled="isDownloading(model)"
                            :class="[
                              'px-3 py-1 rounded text-sm transition-colors',
                              isDownloading(model)
                                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                : 'bg-red-600 hover:bg-red-700 text-white',
                            ]"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </AccordionComponent>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from "vue";
import { useNotifications } from "../composables/useNotifications";
import AccordionComponent from "./common/AccordionComponent.vue";
import { useModelsStore } from "../stores/models";
import { storeToRefs } from "pinia";

/**
 * DownloadModelsComponent
 * -----------------------------------------------------------------------------
 * Main component for managing model downloads, deletion, and organization.
 * Provides a comprehensive interface for browsing, filtering, and managing AI models.
 *
 * ## Features & Behavior
 * - Model browsing with search and tag filtering
 * - Bulk selection and operations (download/delete)
 * - Real-time download progress tracking
 * - Grouped model organization with accordion layout
 * - NSFW content filtering and indication
 * - Integration with models store for state management
 * - Centralized download polling and status updates
 * - Responsive design with modern UI components
 * - Auto-refresh on download completion
 * - Intelligent download conflict detection
 *
 * ## State Management
 * - Uses Pinia models store for global state
 * - Local state for UI selections and filters
 * - Real-time synchronization with download progress
 * - Automatic refresh on download completion
 * - Reactive filter system with computed properties
 *
 * ## Methods
 * ### fetchModels
 * **Description:** Fetches the latest models list from the API.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### handleGroupToggle
 * **Description:** Handles accordion group expand/collapse state.
 * **Parameters:**
 * - `groupName` (string): Name of the group to toggle.
 * - `isOpen` (boolean): Whether the group should be open.
 * **Returns:** void
 *
 * ### handleRowCheck
 * **Description:** Handles individual model selection checkbox.
 * **Parameters:**
 * - `model` (ModelItem): The model object.
 * - `checked` (boolean): Whether the model is selected.
 * **Returns:** void
 *
 * ### toggleTagFilter
 * **Description:** Toggles a tag filter on/off.
 * **Parameters:**
 * - `tag` (string): The tag to toggle.
 * **Returns:** void
 *
 * ### clearFilters
 * **Description:** Clears all search and tag filters.
 * **Parameters:** None
 * **Returns:** void
 *
 * ### modelKey
 * **Description:** Returns unique identifier for a model.
 * **Parameters:**
 * - `model` (ModelItem): The model object.
 * **Returns:** string - Unique key for the model
 *
 * ### lastPath
 * **Description:** Extracts filename from a path string.
 * **Parameters:**
 * - `path` (string, optional): The path string.
 * **Returns:** string - The filename or empty string
 *
 * ### formatSize
 * **Description:** Formats file size in human-readable format.
 * **Parameters:**
 * - `size` (number, optional): Size in bytes.
 * **Returns:** string - Formatted size string
 *
 * ### isNSFW
 * **Description:** Checks if a model is marked as NSFW.
 * **Parameters:**
 * - `model` (ModelItem): The model object.
 * **Returns:** boolean - True if model is NSFW
 *
 * ### isDownloading
 * **Description:** Checks if a model is currently downloading.
 * **Parameters:**
 * - `model` (ModelItem): The model object.
 * **Returns:** boolean - True if model is downloading
 *
 * ### allChecked
 * **Description:** Checks if all models in a group are selected.
 * **Parameters:**
 * - `groupModels` (ModelItem[]): Array of models in the group.
 * **Returns:** boolean - True if all are selected
 *
 * ### toggleAll
 * **Description:** Toggles selection for all models in a group.
 * **Parameters:**
 * - `groupModels` (ModelItem[]): Array of models in the group.
 * - `checked` (boolean): Whether to select or deselect all.
 * **Returns:** void
 *
 * ### unselectModels
 * **Description:** Removes models from selection.
 * **Parameters:**
 * - `modelsList` (ModelItem | ModelItem[]): Model(s) to unselect.
 * **Returns:** void
 *
 * ### confirmDeleteSelected
 * **Description:** Shows confirmation dialog and deletes selected models.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### confirmDownloadSelected
 * **Description:** Shows confirmation dialog and downloads selected models.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### deleteModels
 * **Description:** Deletes one or more models with error handling.
 * **Parameters:**
 * - `modelsToDelete` (ModelItem | ModelItem[]): Model(s) to delete.
 * **Returns:** Promise<void>
 *
 * ### downloadModels
 * **Description:** Downloads one or more models with error handling and progress tracking.
 * **Parameters:**
 * - `modelsToDownload` (ModelItem | ModelItem[]): Model(s) to download.
 * **Returns:** Promise<void>
 *
 * ### confirmDownload
 * **Description:** Shows confirmation dialog and downloads a single model.
 * **Parameters:**
 * - `model` (ModelItem): The model to download.
 * **Returns:** Promise<void>
 *
 * ### confirmDelete
 * **Description:** Shows confirmation dialog and deletes a single model.
 * **Parameters:**
 * - `model` (ModelItem): The model to delete.
 * **Returns:** Promise<void>
 *
 * ## Computed Properties
 * - `allTags`: Array of all available tags from models
 * - `filteredModels`: Models filtered by search text and tags
 * - `filteredGroupedModels`: Filtered models grouped by category
 * - `selectedToDelete`: Models selected for deletion
 * - `selectedToDownload`: Models selected for download
 * - `hasSelectedToDelete`: Whether any models are selected for deletion
 * - `hasSelectedToDownload`: Whether any models are selected for download
 *
 * ## Integration Notes
 * - Integrates with useModelsStore for state management
 * - Uses useNotifications for user feedback
 * - Coordinates with InstallProgressIndicator for download status
 * - Supports AccordionComponent for grouped layout
 * - Follows project design system and Tailwind CSS conventions
 */
interface ModelItem {
  url?: string;
  git?: string;
  dest?: string;
  group?: string;
  tags?: string | string[];
  exists?: boolean;
  size?: number;
  [key: string]: any;
}

/**
 * Download progress interface
 */
interface DownloadProgress {
  progress: number;
  status?: string;
  [key: string]: any;
}

/**
 * Configuration interface
 */
interface Config {
  group_order?: string[];
  [key: string]: any;
}

/**
 * Selected models record type
 */
type SelectedModels = Record<string, boolean>;

/**
 * Grouped models type
 */
type GroupedModels = Record<string, ModelItem[]>;

const modelsStore = useModelsStore();

// --- State ---
const { models, rawDownloads } = storeToRefs(modelsStore);
const selected = ref<SelectedModels>({});
const config = ref<Config>({});

// --- Filter state ---
const filterText = ref<string>("");
const selectedTagFilters = ref<string[]>([]);

// --- Notifications system ---
const { showNotification, showDialog } = useNotifications();

// --- Use centralized downloads data instead of local downloads ---
const downloads = rawDownloads as any; // Type assertion to handle store structure

// --- Fetch models ---
const fetchModels = async (): Promise<void> => {
  try {
    await modelsStore.fetchModels();
    selected.value = { ...selected.value };
  } catch (e) {
    // handled by store error
  }
};

// --- Rafraîchir la liste des modèles à la fin d'un téléchargement ---
let previousDownloads: any = {};
watchEffect(() => {
  // Pour chaque modèle en cours de téléchargement précédemment
  for (const key in previousDownloads) {
    // Si le téléchargement a disparu OU est passé à 100%
    if (
      !(key in downloads.value) ||
      (downloads.value[key] && downloads.value[key].progress === 100)
    ) {
      // Rafraîchir la liste des modèles et mettre à jour previousDownloads
      fetchModels();
      break;
    }
  }
  // Mettre à jour previousDownloads pour la prochaine comparaison
  previousDownloads = { ...downloads.value };
});

// --- Additional state for UI ---
const expandedGroups = ref<string[]>([]);

const handleGroupToggle = (groupName: string, isOpen: boolean): void => {
  const index = expandedGroups.value.indexOf(groupName);
  if (isOpen && index === -1) {
    expandedGroups.value.push(groupName);
  } else if (!isOpen && index > -1) {
    expandedGroups.value.splice(index, 1);
  }
};

const handleRowCheck = (model: ModelItem, checked: boolean): void => {
  const key = modelKey(model);
  if (checked) {
    selected.value[key] = true;
  } else {
    delete selected.value[key];
  }
  // Force reactivity update
  selected.value = { ...selected.value };
};

// --- Computed properties for filtering ---
const allTags = computed((): string[] => {
  const tags = new Set<string>();
  (models.value as ModelItem[]).forEach((model) => {
    if (model.tags) {
      if (Array.isArray(model.tags)) {
        model.tags.forEach((tag) => tags.add(tag));
      } else {
        tags.add(model.tags);
      }
    }
  });
  return Array.from(tags).sort();
});

const filteredModels = computed((): ModelItem[] => {
  let filtered = models.value as ModelItem[];

  // Filter by text (name or tags)
  if (filterText.value.trim()) {
    const searchText = filterText.value.toLowerCase().trim();
    filtered = filtered.filter((model) => {
      const name = (lastPath(model.dest) || model.git || "").toLowerCase();
      const tags = model.tags
        ? (Array.isArray(model.tags)
            ? model.tags.join(" ")
            : model.tags
          ).toLowerCase()
        : "";
      return name.includes(searchText) || tags.includes(searchText);
    });
  }

  // Filter by selected tags
  if (selectedTagFilters.value.length > 0) {
    filtered = filtered.filter((model) => {
      if (!model.tags) return false;
      const modelTags = Array.isArray(model.tags) ? model.tags : [model.tags];
      return selectedTagFilters.value.every((filterTag) =>
        modelTags.some((tag) => tag.toLowerCase() === filterTag.toLowerCase())
      );
    });
  }

  return filtered;
});

const filteredGroupedModels = computed((): GroupedModels => {
  const groups: GroupedModels = {};
  filteredModels.value.forEach((model) => {
    const group = model.group || "Other";
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(model);
  });

  // Trier les groupes selon l'ordre défini dans la configuration
  const sortedGroups: GroupedModels = {};
  const groupOrder = config.value.group_order || [];

  // D'abord, ajouter les groupes dans l'ordre défini
  groupOrder.forEach((groupName: string) => {
    if (groups[groupName]) {
      sortedGroups[groupName] = groups[groupName];
    }
  });

  // Ensuite, ajouter les groupes qui ne sont pas dans group_order (par ordre alphabétique)
  const remainingGroups = Object.keys(groups)
    .filter((groupName) => !groupOrder.includes(groupName))
    .sort();
  remainingGroups.forEach((groupName) => {
    sortedGroups[groupName] = groups[groupName];
  });

  return sortedGroups;
});

// --- Filter actions ---
const toggleTagFilter = (tag: string): void => {
  const index = selectedTagFilters.value.indexOf(tag);
  if (index > -1) {
    selectedTagFilters.value.splice(index, 1);
  } else {
    selectedTagFilters.value.push(tag);
  }
};

const clearFilters = (): void => {
  filterText.value = "";
  selectedTagFilters.value = [];
};

// --- Helpers ---
const modelKey = (model: ModelItem): string => model.url || model.git || '';
const lastPath = (path?: string): string => path?.split("/").pop() || "";
const formatSize = (size?: number): string => {
  if (!size) return "-";
  if (size > 1e9) return (size / 1e9).toFixed(2) + " GB";
  if (size > 1e6) return (size / 1e6).toFixed(2) + " MB";
  if (size > 1e3) return (size / 1e3).toFixed(2) + " KB";
  return size + " B";
};
const isNSFW = (model: ModelItem): boolean => {
  const tags = model.tags;
  if (!tags) return false;
  if (Array.isArray(tags)) return tags.includes("nsfw");
  return tags === "nsfw";
};
const isDownloading = (model: ModelItem): boolean => !!downloads.value[modelKey(model)];

// --- Selection logic ---
const allChecked = (groupModels: ModelItem[]): boolean =>
  groupModels
    .filter((m) => !isDownloading(m))
    .every((m) => selected.value[modelKey(m)]);
const toggleAll = (groupModels: ModelItem[], checked: boolean): void => {
  for (const m of groupModels) {
    if (!isDownloading(m)) {
      selected.value[modelKey(m)] = checked;
    }
  }
};

const selectedToDelete = computed((): ModelItem[] =>
  (models.value as ModelItem[]).filter((m) => selected.value[modelKey(m)] && m.exists)
);
const selectedToDownload = computed((): ModelItem[] =>
  (models.value as ModelItem[]).filter(
    (m) =>
      selected.value[modelKey(m)] && !m.exists && !downloads.value[modelKey(m)]
  )
);

// Debug: log computed values
watchEffect(() => {
  console.log(
    "selectedToDelete:",
    selectedToDelete.value.map((m) => modelKey(m))
  );
  console.log(
    "selectedToDownload:",
    selectedToDownload.value.map((m) => modelKey(m))
  );
});

const hasSelectedToDelete = computed(() => selectedToDelete.value.length > 0);
const hasSelectedToDownload = computed(
  () => selectedToDownload.value.length > 0
);

// --- Actions ---
function unselectModels(modelsList: ModelItem | ModelItem[]): void {
  const models = Array.isArray(modelsList) ? modelsList : [modelsList];
  for (const m of models) {
    delete selected.value[modelKey(m)];
  }
  selected.value = { ...selected.value };
}

const confirmDeleteSelected = async (): Promise<void> => {
  if (!selectedToDelete.value.length) return;

  const result = await showDialog({
    title: "Delete selected models",
    message: `Are you sure you want to delete ${selectedToDelete.value.length} model(s)?`,
    type: "confirm",
    confirmText: "Delete",
    cancelText: "Cancel",
  });

  if (result) {
    await deleteModels(selectedToDelete.value);
    unselectModels(selectedToDelete.value);
  }
};

const confirmDownloadSelected = async (): Promise<void> => {
  if (!selectedToDownload.value.length) return;

  const result = await showDialog({
    title: "Download selected models",
    message: `Download ${selectedToDownload.value.length} model(s)?`,
    type: "confirm",
    confirmText: "Download",
    cancelText: "Cancel",
  });

  if (result) {
    await downloadModels(selectedToDownload.value);
    unselectModels(selectedToDownload.value);
  }
};

// Fonction unique pour supprimer un ou plusieurs modèles
async function deleteModels(modelsToDelete: ModelItem | ModelItem[]): Promise<void> {
  try {
    const res = await modelsStore.deleteModels(modelsToDelete);
    const results = Array.isArray(res) ? res : [res];
    let errors = results.filter((r: any) => r && r.ok === false);
    if (errors.length) {
      errors.forEach((r: any) =>
        showNotification(r.msg || "Delete failed", "error")
      );
    } else {
      showNotification(
        Array.isArray(modelsToDelete) && modelsToDelete.length > 1
          ? "Selected models deleted"
          : "Model deleted",
        "success"
      );
    }
    await fetchModels();
  } catch (error) {
    showNotification("Delete operation failed", "error");
  }
}

// Fonction unique pour télécharger un ou plusieurs modèles
async function downloadModels(modelsToDownload: ModelItem | ModelItem[]): Promise<void> {
  try {
    const modelsArray = Array.isArray(modelsToDownload)
      ? modelsToDownload
      : [modelsToDownload];
    // Vérifier qu'aucun des modèles n'est déjà en cours de téléchargement
    const alreadyDownloading = modelsArray.filter((model) =>
      isDownloading(model)
    );
    if (alreadyDownloading.length > 0) {
      showNotification(
        `Some models are already downloading: ${alreadyDownloading
          .map((m) => lastPath(m.dest) || m.git)
          .join(", ")}`,
        "warning"
      );
      return;
    }
    modelsStore.startGlobalDownloadPolling();
    const res = await modelsStore.startDownload(modelsToDownload);
    const results = Array.isArray(res) ? res : [res];
    let errors = results.filter((r: any) => r && r.ok === false);
    if (errors.length) {
      errors.forEach((r: any) =>
        showNotification(r.msg || "Download failed", "error")
      );
    } else {
      showNotification(
        Array.isArray(modelsToDownload) && modelsToDownload.length > 1
          ? "Selected models downloading"
          : "Download started",
        "success"
      );
      setTimeout(async () => {
        await modelsStore.refreshDownloads();
        console.log(
          "Downloads refreshed after POST, current downloads:",
          Object.keys(rawDownloads.value)
        );
      }, 1000);
    }
    await fetchModels();
  } catch (error) {
    showNotification("Download operation failed", "error");
  }
}

const confirmDownload = async (model: ModelItem): Promise<void> => {
  // Vérifier si le modèle est déjà en cours de téléchargement
  if (isDownloading(model)) {
    showNotification(
      `Model "${lastPath(model.dest) || model.git}" is already downloading`,
      "warning"
    );
    return;
  }

  const result = await showDialog({
    title: "Download model",
    message: `Download model "${lastPath(model.dest) || model.git}"?`,
    type: "confirm",
    confirmText: "Download",
    cancelText: "Cancel",
  });

  if (result) {
    await downloadModels(model);
  }
};

const confirmDelete = async (model: ModelItem): Promise<void> => {
  const result = await showDialog({
    title: "Delete model",
    message: `Delete model "${lastPath(model.dest) || model.git}"?`,
    type: "confirm",
    confirmText: "Delete",
    cancelText: "Cancel",
  });

  if (result) {
    await deleteModels(model);
  }
};

// --- Simplified polling (now uses centralized polling) ---
// Polling is now managed by the models store
// Nous n'avons plus besoin de polling séparé ici

onMounted(async () => {
  await fetchModels(); // Configuration is now extracted directly from /jsonmodels/
  await modelsStore.refreshDownloads();

  // Start global download polling
  modelsStore.startGlobalDownloadPolling();

  // Note: Download polling is now managed by the models store
  // restoreActiveDownloads() is called by InstallProgressIndicator
});
</script>

<script lang="ts">
// Pour l'import dynamique dans HomeView
export default {
  name: "DownloadModelsComponent",
};
</script>

<style scoped>
.download-models-container {
  width: 100%;
}

.download-item {
  display: grid;
  grid-template-columns: 1fr 1.5fr auto;
  align-items: center;
  gap: 16px;
  width: 100%;
  min-height: 40px;
  padding: 8px 12px;
}

.download-name {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.download-progress {
  min-width: 120px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.download-btn {
  padding: 4px 8px;
  font-size: 0.75rem;
  min-width: 60px;
  white-space: nowrap;
}

.spacer {
  margin-bottom: 18px;
}

.models-card {
  width: 100%;
}

.is-downloading {
  opacity: 0.5;
  pointer-events: none;
}

/* Responsive adjustments */
.table-responsive {
  width: 100%;
  overflow-x: auto;
}

/* Small screens */
@media (max-width: 768px) {
  .download-item {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto;
    gap: 8px;
  }

  .download-progress {
    min-width: 100%;
  }

  .header-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .table-responsive table {
    font-size: 0.75rem;
  }

  .table-responsive th,
  .table-responsive td {
    padding: 0.5rem 0.25rem;
  }
}

/* Medium screens */
@media (min-width: 769px) and (max-width: 1024px) {
  .download-item {
    grid-template-columns: 1fr 2fr auto;
    grid-template-rows: auto auto;
    gap: 12px;
  }
}

.tag-filter {
  display: inline-block;
  padding: 4px 8px;
  font-size: 0.875rem;
  border-radius: 9999px;
  transition: background-color 0.3s;
}
</style>
