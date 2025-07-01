<!--
###################################################################################################
## ModelSelectorModal.vue
##
## Description:
##   Reusable modal component for selecting models with filtering and grouping. Allows users to select
##   one or more models for a profile, with tag-based filtering and popular tag suggestions.
##
## Props:
##   - show (Boolean, required): Controls modal visibility.
##   - currentProfileName (String): Name of the current profile (displayed in the modal title).
##   - groupedModels (Object, required): Models grouped by type/category. Example:
##         {
##           "SDXL": [ { id, name, tags, ... }, ... ],
##           "Upscale": [ ... ]
##         }
##   - selectedModels (Array, required): Array of currently selected model objects.
##   - popularTags (Array): List of popular tags for quick filtering (optional).
##   - filterPlaceholder (String): Placeholder for the filter input (optional).
##
## Emits:
##   - close: When the modal is closed (Cancel or X button).
##   - update:selectedModels: When the selection changes (checkbox click).
##   - apply-selection: When user confirms selection (Apply Selection button).
##
## Example Usage:
##
## <ModelSelectorModal
##   :show="showModelSelectorModal"
##   :currentProfileName="currentProfileName"
##   :groupedModels="groupedModels"
##   :selectedModels="selectedModels"
##   :popularTags="popularTags"
##   @close="showModelSelectorModal = false"
##   @update:selectedModels="selectedModels = $event"
##   @apply-selection="handleApplySelection"
## />
##
## function handleApplySelection(selected) {
##   // Do something with selected models
## }
##
###################################################################################################
-->
<template>
  <CommonModal :show="show" @close="$emit('close')">
    <template #title>
      Select Models
    </template>
    <template #default>
      <!-- Collapsible Filter Bar -->
      <div class="border-b border-border bg-background-mute">
        <!-- Filter Toggle Header -->
        <button
          type="button"
          class="w-full px-4 py-3 flex items-center justify-between hover:bg-background transition-colors"
          @click="toggleFilterSection"
        >
          <div class="flex items-center">
            <FontAwesomeIcon icon="filter" class="mr-2" />
            <span class="font-medium text-text-light">Filter Models</span>
            <span v-if="modelFilter" class="ml-2 text-sm text-blue-600">
              ({{ filteredModelsCount }} models)
            </span>
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
                <FontAwesomeIcon icon="search" class="mr-2" />Filter by Name or Tags
              </label>
              <input
                type="text"
                class="form-input w-full text-sm"
                v-model="modelFilter"
                :placeholder="filterPlaceholder"
              />
              <p class="text-xs text-text-muted mt-1">
                Type a model name or separate multiple tags with commas. Models matching the name or any of these tags will be shown.
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
          <div v-if="popularTags && popularTags.length > 0" class="mt-3">
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
      <div
        class="p-4 overflow-y-auto"
        :style="{ 'max-height': showFilterSection ? '45vh' : '55vh' }"
      >
        <div
          v-for="(groupModels, groupName) in filteredGroupedModels"
          :key="groupName"
          class="mb-6"
        >
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
                  <span
                    v-if="model.tags && model.tags.length > 0"
                    class="inline-flex items-center mr-2"
                  >
                    <FontAwesomeIcon icon="tags" class="mr-1" />{{ model.tags.join(", ") }}
                  </span>
                  <span v-if="model.size" class="inline-flex items-center">
                    <FontAwesomeIcon icon="database" class="mr-1" />{{ formatFileSize(model.size) }}
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
    </template>
    <template #footer>
      <button type="button" class="btn btn-secondary" @click="$emit('close')">
        Cancel
      </button>
      <button type="button" class="btn btn-primary" @click="applySelection">
        Apply Selection ({{ localSelectedModels.length }} selected)
      </button>
    </template>
  </CommonModal>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import CommonModal from '../common/CommonModal.vue';

export default {
  name: 'ModelSelectorModal',
  components: { FontAwesomeIcon, CommonModal },
  props: {
    show: { type: Boolean, required: true },
    // Deprecated, not used
    currentProfileName: { type: String, default: '' },
    groupedModels: { type: Object, required: true },
    selectedModels: { type: Array, required: true },
    popularTags: { type: Array, default: () => [] },
    filterPlaceholder: { type: String, default: 'Enter tags to filter models (e.g., base, fp8, nsfw...)' },
  },
  emits: ['close', 'update:selectedModels', 'apply-selection'],
  setup(props, { emit }) {
    const showFilterSection = ref(false);
    const modelFilter = ref('');
    const localSelectedModels = ref([...props.selectedModels]);

    watch(() => props.selectedModels, (val) => {
      localSelectedModels.value = [...val];
    });

    /**
     * Filters models by name (substring, case-insensitive) or by tags (comma-separated, case-insensitive).
     * If the filter contains commas, treat as tags; otherwise, treat as name substring.
     */
    const filteredGroupedModels = computed(() => {
      const filter = modelFilter.value.trim().toLowerCase();
      if (!filter) return props.groupedModels;
      const filtered = {};
      if (filter.includes(',')) {
        // Split filter into tags, but also match the full filter as a name substring
        const tags = filter.split(',').map(t => t.trim()).filter(Boolean);
        for (const [group, models] of Object.entries(props.groupedModels)) {
          const groupFiltered = models.filter(model => {
            // Name fields
            const nameFields = [model.displayName, model.name, model.id, model.dest, model.url];
            const nameMatch = nameFields.some(f => f && f.toLowerCase().includes(filter));
            // Tag match: any tag matches any of the tags
            const tagMatch = model.tags && tags.some(tag => model.tags.map(t => t.toLowerCase()).includes(tag));
            return nameMatch || tagMatch;
          });
          if (groupFiltered.length > 0) filtered[group] = groupFiltered;
        }
      } else {
        // Otherwise, treat as name substring or tag substring (case-insensitive)
        for (const [group, models] of Object.entries(props.groupedModels)) {
          const groupFiltered = models.filter(model => {
            const nameFields = [model.displayName, model.name, model.id, model.dest, model.url];
            return nameFields.some(f => f && f.toLowerCase().includes(filter))
              || (model.tags && model.tags.some(tag => tag.toLowerCase().includes(filter)));
          });
          if (groupFiltered.length > 0) filtered[group] = groupFiltered;
        }
      }
      return filtered;
    });

    const filteredModelsCount = computed(() => {
      return Object.values(filteredGroupedModels.value).reduce((acc, arr) => acc + arr.length, 0);
    });

    function toggleFilterSection() {
      showFilterSection.value = !showFilterSection.value;
    }
    function clearModelFilter() {
      modelFilter.value = '';
    }
    function addTagToFilter(tag) {
      const tags = modelFilter.value.split(',').map(t => t.trim()).filter(Boolean);
      if (!tags.includes(tag)) tags.push(tag);
      modelFilter.value = tags.join(', ');
    }
    /**
     * Checks if a model is selected (by unique hash or dest or url fallback).
     * @param {Object} model - Model object
     * @returns {boolean}
     */
    function isModelSelected(model) {
      const getKey = m => m.hash || m.dest || m.url;
      const key = getKey(model);
      return localSelectedModels.value.some(m => getKey(m) === key);
    }
    /**
     * Toggles selection for a single model (by unique hash or dest or url fallback).
     * @param {Object} model - Model object
     */
    function toggleModelSelection(model) {
      // Use hash, then dest, then url as unique identifier
      const getKey = m => m.hash || m.dest || m.url;
      const key = getKey(model);
      const idx = localSelectedModels.value.findIndex(m => getKey(m) === key);
      if (idx === -1) localSelectedModels.value.push(model);
      else localSelectedModels.value.splice(idx, 1);
      emit('update:selectedModels', localSelectedModels.value);
    }
    /**
     * Returns the display name for a model.
     * Uses the file name from 'dest' if no name/displayName/id is present.
     * @param {Object} model - Model object
     * @returns {string} Display name
     */
    function getModelDisplayName(model) {
      if (model.displayName) return model.displayName;
      if (model.name) return model.name;
      if (model.id) return model.id;
      if (model.dest) {
        // Extract file name from dest path
        const match = model.dest.match(/([^/\\]+)$/);
        if (match) return match[1];
      }
      if (model.url) {
        const match = model.url.match(/([^/\\]+)$/);
        if (match) return match[1];
      }
      return 'Unnamed Model';
    }
    /**
     * Formats a file size in bytes to a human-readable string.
     * @param {number} size - File size in bytes
     * @returns {string}
     */
    function formatFileSize(size) {
      if (!size) return '';
      const i = Math.floor(Math.log(size) / Math.log(1024));
      return (size / Math.pow(1024, i)).toFixed(2) + ' ' + ['B', 'KB', 'MB', 'GB', 'TB'][i];
    }
    function applySelection() {
      emit('apply-selection', localSelectedModels.value);
    }

    return {
      showFilterSection,
      modelFilter,
      filteredGroupedModels,
      filteredModelsCount,
      toggleFilterSection,
      clearModelFilter,
      addTagToFilter,
      isModelSelected,
      toggleModelSelection,
      getModelDisplayName,
      formatFileSize,
      applySelection,
      localSelectedModels,
    };
  },
};
</script>
<!--
###################################################################################################
## ModelSelectorModal.vue
##
## Description:
##   Reusable modal component for selecting models with filtering and grouping. Allows users to select
##   one or more models for a profile, with tag-based filtering and popular tag suggestions.
##
## Props:
##   - show (Boolean, required): Controls modal visibility.
##   - currentProfileName (String): Name of the current profile (displayed in the modal title).
##   - groupedModels (Object, required): Models grouped by type/category. Example:
##         {
##           "SDXL": [ { id, name, tags, ... }, ... ],
##           "Upscale": [ ... ]
##         }
##   - selectedModels (Array, required): Array of currently selected model objects.
##   - popularTags (Array): List of popular tags for quick filtering (optional).
##   - filterPlaceholder (String): Placeholder for the filter input (optional).
##
## Emits:
##   - close: When the modal is closed (Cancel or X button).
##   - update:selectedModels: When the selection changes (checkbox click).
##   - apply-selection: When user confirms selection (Apply Selection button).
##
## Example Usage:
##
## <ModelSelectorModal
##   :show="showModelSelectorModal"
##   :currentProfileName="currentProfileName"
##   :groupedModels="groupedModels"
##   :selectedModels="selectedModels"
##   :popularTags="popularTags"
##   @close="showModelSelectorModal = false"
##   @update:selectedModels="selectedModels = $event"
##   @apply-selection="handleApplySelection"
## />
##
## function handleApplySelection(selected) {
##   // Do something with selected models
## }
##
###################################################################################################
-->
-->
