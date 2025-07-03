<template>
  <CommonCard>
    <template #header>
      <div class="flex">      <h3>
        <FontAwesomeIcon :icon="faCog" class="mr-2" />
        JSON Editor
      </h3>
        <button
          type="button"
          class="btn btn-xs btn-default ml-auto"
          @click="fetchData"
          :disabled="loading"
        >
          <span v-if="loading" class="flex items-center justify-center">
            <FontAwesomeIcon
              :icon="faSpinner"
              class="animate-spin -ml-1 mr-2 h-3 w-3 text-white"
            />
            Refreshing...
          </span>
          <span v-else class="flex items-center">
            <FontAwesomeIcon :icon="faSync" class="w-3 h-3 mr-2" />
            Refresh
          </span>
        </button>
        <button
          type="button"
          class="btn btn-xs btn-default ml-2"
          @click="openAddGroupModal"
        >
          <span class="flex items-center">
            <FontAwesomeIcon :icon="faPlus" class="w-3 h-3 mr-2" />
            Add Group
          </span>
        </button>
        <button
          type="button"
          class="btn btn-xs btn-primary ml-2"
          @click="openAddModelModal()"
        >
          <span class="flex items-center">
            <FontAwesomeIcon :icon="faPlus" class="w-3 h-3 mr-2" />
            Add Model
          </span>
        </button>
      </div>
    </template>
    <div>
      <!-- Loading/Error -->
      <div
        v-if="loading"
        class="flex justify-center items-center min-h-[200px]"
      >
        <div class="flex flex-col items-center">
          <div
            class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"
          ></div>
          <p class="mt-2 text-text-light">Loading models.json file...</p>
        </div>
      </div>

      <div
        v-else-if="error"
        class="bg-red-900 text-white p-4 rounded-md border border-red-700 flex items-start"
      >
        <FontAwesomeIcon
          :icon="faExclamationTriangle"
          class="w-5 h-5 mr-2 mt-0.5 flex-shrink-0"
        />
        <span>{{ error }}</span>
      </div>

      <template v-else>
        <!-- Success/Error Message -->
        <div
          v-if="message"
          :class="{
            'bg-green-900 text-white border-green-700':
              messageType === 'success',
            'bg-red-900 text-white border-red-700': messageType === 'error',
          }"
          class="p-4 rounded-md border flex items-start"
        >
          <FontAwesomeIcon
            v-if="messageType === 'success'"
            :icon="faCheck"
            class="w-5 h-5 mr-2 mt-0.5"
          />
          <FontAwesomeIcon
            v-else
            :icon="faExclamationTriangle"
            class="w-5 h-5 mr-2 mt-0.5"
          />
          <span>{{ message }}</span>
          <button @click="message = ''" class="ml-auto">
            <FontAwesomeIcon :icon="faTimes" class="w-4 h-4" />
          </button>
        </div>

        <!-- Group Management -->
        <AccordionComponent
          title="Model Groups"
          icon="layer-group"
          :default-open="true"
          size="m"
        >
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-border">
              <thead class="bg-background-mute">
                <tr>
                  <th
                    class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                  >
                    <div class="flex items-center">
                      <FontAwesomeIcon :icon="faSort" class="w-4 h-4 mr-2" />
                      Order
                    </div>
                  </th>
                  <th
                    class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                  >
                    Name
                  </th>
                  <th
                    class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-background-soft divide-y divide-border">
                <template
                  v-for="(group, index) in sortableGroupList"
                  :key="group.name"
                >
                  <!-- Drop indicator above -->
                  <tr
                    v-if="dragOverIndex === index && dropPosition === 'above'"
                    class="h-1"
                  >
                    <td colspan="3" class="p-0">
                      <div
                        class="h-1 bg-blue-500 rounded-full mx-4 shadow-lg animate-pulse"
                      ></div>
                    </td>
                  </tr>

                  <!-- Group row -->
                  <tr
                    class="hover:bg-background-mute cursor-move transition-all duration-200 ease-in-out relative"
                    :class="{
                      'bg-blue-50 dark:bg-blue-900/20 shadow-lg scale-[0.98]':
                        draggedIndex === index,
                      'bg-green-50 dark:bg-green-900/20':
                        dragOverIndex === index && draggedIndex !== index,
                      'transform translate-y-0.5':
                        dragOverIndex === index && dropPosition === 'below',
                      'transform -translate-y-0.5':
                        dragOverIndex === index && dropPosition === 'above',
                      'opacity-40': isDragging && draggedIndex === index,
                      'z-10': draggedIndex === index,
                    }"
                    draggable="true"
                    @dragstart="onDragStart(index, $event)"
                    @dragover="onDragOver($event)"
                    @drop="onDrop(index, $event)"
                    @dragend="onDragEnd"
                    @dragenter="onDragEnter(index, $event)"
                    @dragleave="onDragLeave"
                  >
                    <td class="px-4 py-3 text-center">
                      <div
                        class="flex items-center justify-center text-text-light-muted"
                      >
                        <FontAwesomeIcon
                          :icon="faGripLines"
                          class="w-5 h-5 transition-transform duration-200"
                          :class="{
                            'scale-110 text-blue-500': draggedIndex === index,
                          }"
                        />
                      </div>
                    </td>
                    <td class="px-4 py-3 text-text-light">
                      <span
                        class="transition-all duration-200"
                        :class="{
                          'font-semibold text-blue-600 dark:text-blue-400':
                            draggedIndex === index,
                        }"
                      >
                        {{ group.name }}
                      </span>
                    </td>
                    <td class="px-4 py-3">
                      <div class="flex space-x-2">
                        <button
                          type="button"
                          class="px-3 py-1 bg-btn-default text-white rounded hover:bg-btn-default-hover text-sm transition-all duration-150"
                          @click="openEditGroupModal(group.name)"
                          :disabled="isDragging"
                        >
                          Rename
                        </button>
                        <button
                          type="button"
                          class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm transition-all duration-150"
                          @click="deleteGroup(group.name)"
                          :disabled="isDragging"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>

                  <!-- Drop indicator below -->
                  <tr
                    v-if="dragOverIndex === index && dropPosition === 'below'"
                    class="h-1"
                  >
                    <td colspan="3" class="p-0">
                      <div
                        class="h-1 bg-blue-500 rounded-full mx-4 shadow-lg animate-pulse"
                      ></div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </AccordionComponent>
        <!-- Models by Group -->
        <AccordionComponent
          title="Models by Group"
          icon="cubes"
          :default-open="true"
          class="mt-6"
          size="m"
        >
          <div v-if="sortableGroupList.length" class="space-y-4">
            <AccordionComponent
              v-for="group in sortableGroupList"
              :key="group.name"
              :title="`${group.name} (${group.models.length})`"
              icon="folder"
              :default-open="false"
              size="xs"
            >
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-border">
                  <thead class="bg-background-mute">
                    <tr>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        Name
                      </th>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        Type
                      </th>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        URL
                      </th>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        Tags
                      </th>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        Size
                      </th>
                      <th
                        class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider"
                      >
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-background-soft divide-y divide-border">
                    <tr
                      v-for="model in group.models"
                      :key="model.dest || model.git"
                      class="hover:bg-background-mute"
                    >
                      <td class="px-4 py-3">
                        <span
                          :class="{ 'text-red-500 font-bold': isNSFW(model) }"
                        >
                          {{ getModelName(model) }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-text-light">
                        {{ model.type }}
                      </td>
                      <td class="px-4 py-3">
                        <a
                          v-if="model.src"
                          :href="model.src"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="text-blue-400 hover:text-blue-300"
                          :title="model.src"
                        >
                          <FontAwesomeIcon
                            icon="external-link-alt"
                            class="w-4 h-4"
                          />
                        </a>
                        <span v-else class="text-text-light-muted">-</span>
                      </td>
                      <td class="px-4 py-3">
                        <div class="flex flex-wrap gap-1">
                          <span
                            v-for="tag in getTags(model)"
                            :key="tag"
                            class="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-700 text-white"
                          >
                            {{ tag }}
                          </span>
                        </div>
                      </td>
                      <td class="px-4 py-3 text-text-light">
                        {{
                          model.size
                            ? (model.size / 1024 / 1024).toFixed(2) + " MB"
                            : "-"
                        }}
                      </td>
                      <td class="px-4 py-3">
                        <div class="flex space-x-2">
                          <button
                            type="button"
                            class="px-3 py-1 bg-btn-default text-white rounded hover:bg-btn-default-hover text-sm"
                            @click="openEditModelModal(model)"
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                            @click="deleteModel(model)"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </AccordionComponent>
          </div>
          <div
            v-else
            class="flex flex-col items-center justify-center py-12 text-text-light-muted"
          >
            <FontAwesomeIcon :icon="faArchive" class="w-16 h-16 mb-4" />
            <p class="text-lg">No model groups.</p>
          </div>
        </AccordionComponent>
      </template>

      <!-- Modal: Add/Edit Group -->
      <div v-if="showGroupModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div
          class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
        >
          <div
            class="fixed inset-0 transition-opacity"
            @click="showGroupModal = false"
          >
            <div class="absolute inset-0 bg-black opacity-50"></div>
          </div>

          <span
            class="hidden sm:inline-block sm:align-middle sm:h-screen"
          ></span
          >&#8203;

          <div
            class="inline-block align-bottom bg-background-soft rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
          >
            <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg font-medium leading-6 text-text-light mb-4">
                {{ groupModalTitle }}
              </h3>

              <form @submit.prevent="submitGroupForm">
                <div class="mb-4">
                  <label for="group-name" class="form-label">Group Name</label>
                  <input
                    id="group-name"
                    v-model="groupForm.name"
                    type="text"
                    class="form-input w-full"
                    required
                  />
                </div>
              </form>
            </div>

            <div
              class="bg-background-mute px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"
            >
              <button
                type="button"
                class="btn btn-primary ml-2"
                @click="submitGroupForm"
                :disabled="savingGroup"
              >
                <span
                  v-if="savingGroup"
                  class="flex items-center justify-center"
                >
                  <FontAwesomeIcon
                    :icon="faSpinner"
                    class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  />
                  Saving...
                </span>
                <span v-else>{{ groupModalEdit ? "Rename" : "Add" }}</span>
              </button>
              <button
                type="button"
                class="btn btn-default"
                @click="showGroupModal = false"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal: Add/Edit Model -->
      <div v-if="showModelModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div
          class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
        >
          <div
            class="fixed inset-0 transition-opacity"
            @click="showModelModal = false"
          >
            <div class="absolute inset-0 bg-black opacity-50"></div>
          </div>

          <span
            class="hidden sm:inline-block sm:align-middle sm:h-screen"
          ></span
          >&#8203;

          <div
            class="inline-block align-bottom bg-background-soft rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
          >
            <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg font-medium leading-6 text-text-light mb-4">
                {{ modelModalTitle }}
              </h3>

              <form @submit.prevent="submitModelForm" class="space-y-4">
                <div>
                  <label class="form-label"
                    >Group Name <span class="text-red-500">*</span></label
                  >
                  <select v-model="modelForm.group" class="form-input" required>
                    <option value="" disabled>Select a group</option>
                    <option
                      v-for="group in sortableGroupList"
                      :key="group.name"
                      :value="group.name"
                    >
                      {{ group.name }}
                    </option>
                  </select>
                </div>

                <!-- Source Type Selection -->
                <div>
                  <label class="form-label">Source Type</label>
                  <div class="flex space-x-4">
                    <label class="flex items-center">
                      <input
                        v-model="modelForm.sourceType"
                        type="radio"
                        value="url"
                        class="form-radio"
                      />
                      <span class="ml-2 text-text-light">URL Download</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        v-model="modelForm.sourceType"
                        type="radio"
                        value="git"
                        class="form-radio"
                      />
                      <span class="ml-2 text-text-light">Git Repository</span>
                    </label>
                  </div>
                </div>

                <!-- URL Fields (shown when sourceType is 'url') -->
                <template v-if="modelForm.sourceType === 'url'">
                  <div>
                    <label class="form-label">URL</label>
                    <input
                      v-model="modelForm.url"
                      type="text"
                      class="form-input"
                      placeholder="Model URL"
                    />
                  </div>

                  <div>
                    <label class="form-label"
                      >Source (Descriptive Page URL)</label
                    >
                    <input
                      v-model="modelForm.src"
                      type="text"
                      class="form-input"
                      placeholder="URL of the model's descriptive page"
                    />
                  </div>
                  <div>
                    <label class="form-label"
                      >Destination <span class="text-red-500">*</span></label
                    >
                    <input
                      v-model="modelForm.dest"
                      type="text"
                      class="form-input"
                      placeholder="Destination path"
                      required
                    />
                  </div>
                </template>

                <!-- Git Field (shown when sourceType is 'git') -->
                <template v-if="modelForm.sourceType === 'git'">
                  <div>
                    <label class="form-label">Git Repository URL</label>
                    <input
                      v-model="modelForm.git"
                      type="text"
                      class="form-input"
                      placeholder="Git repository URL"
                      required
                    />
                  </div>
                </template>

                <div class="relative">
                  <label class="form-label">Type</label>
                  <div class="relative">
                    <input
                      v-model="modelForm.type"
                      type="text"
                      class="form-input pr-10"
                      placeholder="Model type"
                      @focus="onTypeInputFocus"
                      @blur="onTypeInputBlur"
                      @input="onTypeInputChange"
                    />
                    <button
                      type="button"
                      class="absolute inset-y-0 right-0 flex items-center px-3 text-text-light-muted hover:text-text-light transition-colors"
                      @click="showTypeDropdown = !showTypeDropdown"
                    >
                      <FontAwesomeIcon :icon="faChevronDown" class="w-4 h-4" />
                    </button>

                    <!-- Dropdown -->
                    <div
                      v-if="showTypeDropdown"
                      class="absolute z-10 w-full mt-1 bg-background-soft border border-border rounded-md shadow-lg max-h-48 overflow-y-auto type-dropdown"
                    >
                      <!-- Existing types -->
                      <div v-if="getAllExistingTypes.length > 0" class="p-2">
                        <div class="text-xs text-text-light-muted mb-2">
                          Existing types:
                        </div>
                        <button
                          v-for="type in filteredTypes"
                          :key="type"
                          type="button"
                          @click="selectType(type)"
                          class="w-full text-left px-3 py-2 text-sm text-text-light hover:bg-background-mute rounded transition-colors type-dropdown-item"
                        >
                          {{ type }}
                        </button>
                      </div>

                      <!-- Add custom type option -->
                      <div
                        v-if="
                          typeSearchQuery &&
                          !getAllExistingTypes.includes(typeSearchQuery)
                        "
                        class="border-t border-border p-2"
                      >
                        <button
                          type="button"
                          @click="addCustomType"
                          class="w-full text-left px-3 py-2 text-sm text-blue-400 hover:bg-background-mute rounded transition-colors flex items-center type-dropdown-item"
                        >
                          <FontAwesomeIcon :icon="faPlus" class="w-4 h-4 mr-2" />
                          Add "{{ typeSearchQuery }}"
                        </button>
                      </div>

                      <!-- No types found -->
                      <div
                        v-if="getAllExistingTypes.length === 0"
                        class="p-4 text-center text-text-light-muted text-sm"
                      >
                        No existing types found
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <label class="form-label">Tags</label>
                  <div class="space-y-2">
                    <!-- Existing tags selection -->
                    <div v-if="getAllExistingTags.length > 0" class="mb-2">
                      <label class="text-xs text-text-light-muted mb-1 block"
                        >Select from existing tags:</label
                      >
                      <div class="flex flex-wrap gap-1">
                        <button
                          v-for="tag in getAllExistingTags"
                          :key="tag"
                          type="button"
                          @click="addExistingTag(tag)"
                          :disabled="modelForm.tags.includes(tag)"
                          :class="{
                            'bg-blue-600 text-white':
                              !modelForm.tags.includes(tag),
                            'bg-gray-400 text-gray-600 cursor-not-allowed':
                              modelForm.tags.includes(tag),
                          }"
                          class="px-2 py-1 rounded text-xs hover:bg-blue-700 transition-colors"
                        >
                          {{ tag }}
                        </button>
                      </div>
                    </div>

                    <!-- Selected tags and input for new tags -->
                    <div
                      class="flex flex-wrap gap-2 p-2 border border-border rounded"
                    >
                      <div
                        v-for="(tag, index) in modelForm.tags"
                        :key="index"
                        class="bg-background-mute px-2 py-1 rounded flex items-center"
                      >
                        <span class="text-text-light mr-2">{{ tag }}</span>
                        <button
                          type="button"
                          @click="removeTag(index)"
                          class="text-text-light-muted hover:text-text-light"
                        >
                          <FontAwesomeIcon :icon="faTimes" class="w-4 h-4" />
                        </button>
                      </div>
                      <input
                        v-model="newTag"
                        @keydown.enter.prevent="addTag"
                        type="text"
                        class="bg-transparent border-none focus:outline-none text-text-light flex-1"
                        placeholder="Add a new tag..."
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label class="form-label">Comments</label>
                  <textarea
                    v-model="modelForm.comments"
                    class="form-input"
                    rows="3"
                    placeholder="Additional comments about this model..."
                  ></textarea>
                </div>

                <!-- Hash and Size fields only shown during edit -->
                <template v-if="modelModalEdit">
                  <div>
                    <label class="form-label">Hash</label>
                    <input
                      v-model="modelForm.hash"
                      type="text"
                      class="form-input"
                      placeholder="Hash"
                    />
                  </div>

                  <div>
                    <label class="form-label">Size (bytes)</label>
                    <input
                      v-model.number="modelForm.size"
                      type="number"
                      min="0"
                      class="form-input"
                    />
                  </div>
                </template>
              </form>
            </div>

            <div
              class="bg-background-mute px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"
            >
              <button
                type="button"
                class="btn btn-primary ml-2"
                @click="submitModelForm"
                :disabled="savingModel"
              >
                <span
                  v-if="savingModel"
                  class="flex items-center justify-center"
                >
                  <FontAwesomeIcon :icon="faSpinner" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" />
                  Saving...
                </span>
                <span v-else>{{ modelModalEdit ? "Save" : "Add" }}</span>
              </button>
              <button
                type="button"
                class="btn btn-default"
                @click="showModelModal = false"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </CommonCard>
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  computed,
  onMounted,
  watch,
  type Ref,
  type ComputedRef,
} from "vue";
import { useNotifications } from "@/composables/useNotifications";
import api from "../services/api.js";
import AccordionComponent from "@/components/common/AccordionComponent.vue";
import CommonCard from "@/components/common/CommonCard.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import {
  faCog,
  faSpinner,
  faSync,
  faPlus,
  faExclamationTriangle,
  faCheck,
  faTimes,
  faSort,
  faGripLines,
  faFolder,
  faEdit,
  faTrash,
  faArchive,
  faDownload,
  faSave,
  faEye,
  faEyeSlash,
  faLayerGroup,
  faCubes,
  faChevronDown,
} from "@fortawesome/free-solid-svg-icons";

// Type definitions
interface JsonModel {
  url?: string;
  src?: string;
  dest?: string;
  git?: string;
  type?: string;
  tags?: string[];
  hash?: string;
  size?: number | null;
  comments?: string;
  [key: string]: any;
}

interface JsonGroup {
  name: string;
  models: JsonModel[];
}

interface JsonData {
  config: Record<string, any>;
  groups: Record<string, JsonModel[]>;
}

interface ModelForm {
  group: string;
  url: string;
  src: string;
  dest: string;
  git: string;
  type: string;
  tags: string[];
  hash: string;
  size: number | null;
  comments: string;
  sourceType: "url" | "git";
}

interface GroupForm {
  name: string;
}

interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
  message?: string;
}

type MessageType = "success" | "error";
type DropPosition = "above" | "below" | null;

// --- State ---
const { success, error: showError } = useNotifications();
const loading: Ref<boolean> = ref(false);
const error: Ref<string> = ref("");
const message: Ref<string> = ref("");
const messageType: Ref<MessageType> = ref("success");
const newTag: Ref<string> = ref("");

// Type selector state
const showTypeDropdown: Ref<boolean> = ref(false);
const typeSearchQuery: Ref<string> = ref("");
const filteredTypes: ComputedRef<string[]> = computed(() => {
  if (!typeSearchQuery.value) {
    return getAllExistingTypes.value;
  }
  return getAllExistingTypes.value.filter((type: string) =>
    type.toLowerCase().includes(typeSearchQuery.value.toLowerCase())
  );
});

const data: Ref<JsonData> = ref({ config: {}, groups: {} });

// Drag and drop state
const draggedIndex: Ref<number | null> = ref(null);
const dragOverIndex: Ref<number | null> = ref(null);
const dropPosition: Ref<DropPosition> = ref(null);
const isDragging: Ref<boolean> = ref(false);
const groupOrder: Ref<string[]> = ref([]);

// Groupes
const groupList: ComputedRef<JsonGroup[]> = computed(() =>
  Object.entries(data.value.groups || {}).map(([name, models]) => ({
    name,
    models: Array.isArray(models) ? models : [],
  }))
);

// Sortable group list that respects the custom order
const sortableGroupList: ComputedRef<JsonGroup[]> = computed(() => {
  const groups = groupList.value;
  if (groupOrder.value.length === 0) {
    return groups;
  }

  // Sort groups according to the custom order
  const orderedGroups: JsonGroup[] = [];
  const remainingGroups = [...groups];

  // Add groups in the specified order
  groupOrder.value.forEach((groupName: string) => {
    const groupIndex = remainingGroups.findIndex((g) => g.name === groupName);
    if (groupIndex !== -1) {
      orderedGroups.push(remainingGroups[groupIndex]);
      remainingGroups.splice(groupIndex, 1);
    }
  });

  // Add any remaining groups that aren't in the order array
  orderedGroups.push(...remainingGroups);

  return orderedGroups;
});

// Group Modal
const showGroupModal: Ref<boolean> = ref(false);
const groupModalEdit: Ref<boolean> = ref(false);
const groupModalTitle: ComputedRef<string> = computed(() =>
  groupModalEdit.value ? "Rename Group" : "Add Group"
);
const groupForm: GroupForm = reactive({ name: "" });
let groupEditOldName: string = "";

// Model Modal
const showModelModal: Ref<boolean> = ref(false);
const modelModalEdit: Ref<boolean> = ref(false);
const modelModalTitle: ComputedRef<string> = computed(() =>
  modelModalEdit.value ? "Edit Model" : "Add Model"
);
const modelForm: ModelForm = reactive({
  group: "",
  url: "",
  src: "",
  dest: "",
  git: "",
  type: "",
  tags: [],
  hash: "",
  size: null,
  comments: "",
  sourceType: "url", // "url" or "git"
});
const savingGroup: Ref<boolean> = ref(false);
const savingModel: Ref<boolean> = ref(false);

// Expanded Groups for individual model group accordions (not needed anymore since AccordionComponent handles its own state)
// const expandedGroups = ref([]);

// No longer needed since AccordionComponent handles its own toggle state
// const toggleSection = (section) => {
//   const index = expandedSections.value.indexOf(section);
//   if (index > -1) {
//     expandedSections.value.splice(index, 1);
//   } else {
//     expandedSections.value.push(section);
//   }
// };

// const toggleGroup = (name) => {
//   const index = expandedGroups.value.indexOf(name);
//   if (index > -1) {
//     expandedGroups.value.splice(index, 1);
//   } else {
//     expandedGroups.value.push(name);
//   }
// };

// Helper functions
const getModelName = (model: JsonModel): string => {
  return model.dest
    ? model.dest.split("/").pop() || "Unnamed"
    : model.git
      ? model.git.split("/").pop() || "Unnamed"
      : "Unnamed";
};

const isNSFW = (model: JsonModel): boolean => {
  return (
    Array.isArray(model.tags) &&
    model.tags.some((t: string) => t.toLowerCase() === "nsfw")
  );
};

const getTags = (model: JsonModel): string[] => {
  if (!model.tags) return [];
  return Array.isArray(model.tags) ? model.tags : [model.tags];
};

// Get all existing tags from all models
const getAllExistingTags: ComputedRef<string[]> = computed(() => {
  const allTags = new Set<string>();
  sortableGroupList.value.forEach((group: JsonGroup) => {
    group.models.forEach((model: JsonModel) => {
      const tags = getTags(model);
      tags.forEach((tag: string) => allTags.add(tag));
    });
  });
  return Array.from(allTags).sort();
});

// Get all existing types from all models
const getAllExistingTypes: ComputedRef<string[]> = computed(() => {
  const allTypes = new Set<string>();
  sortableGroupList.value.forEach((group: JsonGroup) => {
    group.models.forEach((model: JsonModel) => {
      if (model.type && model.type.trim()) {
        allTypes.add(model.type.trim());
      }
    });
  });
  return Array.from(allTypes).sort();
});

// Tag functions
const addTag = (): void => {
  if (newTag.value.trim() && !modelForm.tags.includes(newTag.value.trim())) {
    modelForm.tags.push(newTag.value.trim());
    newTag.value = "";
  }
};

const addExistingTag = (tag: string): void => {
  if (!modelForm.tags.includes(tag)) {
    modelForm.tags.push(tag);
  }
};

const removeTag = (index: number): void => {
  modelForm.tags.splice(index, 1);
};

// Type selector functions
const selectType = (type: string): void => {
  modelForm.type = type;
  showTypeDropdown.value = false;
  typeSearchQuery.value = "";
};

const addCustomType = (): void => {
  if (typeSearchQuery.value.trim()) {
    modelForm.type = typeSearchQuery.value.trim();
    showTypeDropdown.value = false;
    typeSearchQuery.value = "";
  }
};

const onTypeInputFocus = (): void => {
  showTypeDropdown.value = true;
  typeSearchQuery.value = "";
};

const onTypeInputBlur = (): void => {
  // Delay hiding to allow click on dropdown items
  setTimeout(() => {
    showTypeDropdown.value = false;
  }, 200);
};

const onTypeInputChange = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  modelForm.type = target.value;
  typeSearchQuery.value = target.value;
  showTypeDropdown.value = true;
};

// Watch for source type changes to clear irrelevant fields
watch(
  () => modelForm.sourceType,
  (newType) => {
    if (newType === "url") {
      modelForm.git = "";
      // Ensure dest has default value if empty
      if (!modelForm.dest) {
        modelForm.dest = "${BASE_DIR}/models/";
      }
    } else if (newType === "git") {
      modelForm.url = "";
      modelForm.src = "";
      modelForm.dest = "";
    }
  }
);

// Helper function to extract error message from API error
const getErrorMessage = (
  error: unknown,
  defaultMessage: string = "An error occurred"
): string => {
  if (error && typeof error === "object") {
    const apiError = error as ApiError;
    return (
      apiError.response?.data?.detail || apiError.message || defaultMessage
    );
  }
  return defaultMessage;
};

// --- Drag and Drop Methods ---
/**
 * Handle drag start event
 */
const onDragStart = (index: number, event: DragEvent): void => {
  draggedIndex.value = index;
  isDragging.value = true;

  const target = event.target as HTMLElement;

  // Create a custom drag image (ghost effect)
  const dragElement = target.cloneNode(true) as HTMLElement;
  dragElement.style.transform = "rotate(3deg)";
  dragElement.style.opacity = "0.8";
  dragElement.style.backgroundColor = "rgba(59, 130, 246, 0.1)";
  dragElement.style.border = "2px dashed #3b82f6";
  dragElement.style.borderRadius = "8px";
  dragElement.style.boxShadow = "0 10px 25px rgba(0, 0, 0, 0.3)";
  dragElement.style.transition = "all 0.2s ease";

  // Position the ghost element off-screen temporarily
  dragElement.style.position = "absolute";
  dragElement.style.top = "-1000px";
  dragElement.style.left = "-1000px";
  document.body.appendChild(dragElement);

  // Set the custom drag image
  if (event.dataTransfer) {
    event.dataTransfer.setDragImage(dragElement, 50, 25);
  }

  // Clean up the temporary element after drag starts
  setTimeout(() => {
    if (document.body.contains(dragElement)) {
      document.body.removeChild(dragElement);
    }
  }, 0);

  // Style the original element during drag
  target.style.opacity = "0.4";
  target.style.transform = "scale(0.98)";
  target.style.transition = "all 0.2s ease";

  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/html", "");
  }
};

/**
 * Handle drag over event
 */
const onDragOver = (event: DragEvent): void => {
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = "move";
  }
};

/**
 * Handle drag enter event
 */
const onDragEnter = (index: number, event: DragEvent): void => {
  if (draggedIndex.value === null || draggedIndex.value === index) {
    return;
  }

  dragOverIndex.value = index;

  // Determine drop position based on mouse position
  const target = event.target as HTMLElement;
  const rect = target.closest("tr")?.getBoundingClientRect();
  if (rect) {
    const mouseY = event.clientY;
    const elementCenter = rect.top + rect.height / 2;

    if (mouseY < elementCenter) {
      dropPosition.value = "above";
    } else {
      dropPosition.value = "below";
    }
  }
};

/**
 * Handle drag leave event
 */
const onDragLeave = (event: DragEvent): void => {
  // Only clear if we're actually leaving the row, not just moving between child elements
  const relatedTarget = event.relatedTarget as HTMLElement | null;
  const target = event.target as HTMLElement;
  const currentRow = target.closest("tr");

  if (!relatedTarget || !currentRow?.contains(relatedTarget)) {
    setTimeout(() => {
      // Double-check we're still not hovering over the row
      if (currentRow && !currentRow.matches(":hover")) {
        dragOverIndex.value = null;
        dropPosition.value = null;
      }
    }, 50);
  }
};

/**
 * Handle drop event
 */
const onDrop = (targetIndex: number, event: DragEvent): void => {
  event.preventDefault();

  if (draggedIndex.value === null || draggedIndex.value === targetIndex) {
    onDragEnd(event);
    return;
  }

  // Calculate the actual target index based on drop position
  let actualTargetIndex = targetIndex;
  if (dropPosition.value === "below") {
    actualTargetIndex = targetIndex + 1;
  }

  // Adjust for the fact that we're removing an item first
  if (draggedIndex.value < actualTargetIndex) {
    actualTargetIndex -= 1;
  }

  // Reorder the groups
  const newOrder = [...sortableGroupList.value.map((g: JsonGroup) => g.name)];
  const draggedItem = newOrder[draggedIndex.value];

  // Remove the dragged item from its original position
  newOrder.splice(draggedIndex.value, 1);

  // Insert the dragged item at the new position
  newOrder.splice(actualTargetIndex, 0, draggedItem);

  // Update the group order
  groupOrder.value = newOrder;

  // Save the new order to the backend
  saveGroupOrder();

  // Reset drag state
  onDragEnd(event);
};

/**
 * Handle drag end event
 */
const onDragEnd = (event: DragEvent): void => {
  // Reset the visual state of the dragged element
  const target = event.target as HTMLElement;
  if (target) {
    target.style.opacity = "1";
    target.style.transform = "scale(1)";
    target.style.transition = "all 0.2s ease";
  }

  // Reset all drag state
  draggedIndex.value = null;
  dragOverIndex.value = null;
  dropPosition.value = null;
  isDragging.value = false;
};

/**
 * Save the group order to the backend
 */
const saveGroupOrder = async (): Promise<void> => {
  try {
    await api.put("/jsonmodels/group-order", { order: groupOrder.value });
    message.value = "Group order updated";
    messageType.value = "success";
  } catch (e) {
    message.value = getErrorMessage(e, "Failed to save group order");
    messageType.value = "error";
  }
};

// --- API Calls ---
async function fetchData(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    const res = await api.get("/jsonmodels/");
    const json = res.data || {};
    data.value = json;

    // Fetch group order if it exists
    try {
      const orderRes = await api.get("/jsonmodels/group-order");
      if (orderRes.data && Array.isArray(orderRes.data.order)) {
        groupOrder.value = orderRes.data.order;
      }
    } catch (orderError) {
      // If group order endpoint doesn't exist or fails, just use default order
      console.warn(
        "Could not fetch group order:",
        getErrorMessage(orderError, "Unknown error")
      );
      groupOrder.value = [];
    }

    // No longer need to manage expandedGroups since AccordionComponent handles its own state
  } catch (e) {
    error.value = getErrorMessage(e, "Loading error");
  } finally {
    loading.value = false;
  }
}

// --- Group CRUD ---
function openAddGroupModal(): void {
  groupModalEdit.value = false;
  groupForm.name = "";
  showGroupModal.value = true;
}

function openEditGroupModal(name: string): void {
  groupModalEdit.value = true;
  groupForm.name = name;
  groupEditOldName = name;
  showGroupModal.value = true;
}

async function submitGroupForm(): Promise<void> {
  savingGroup.value = true;
  try {
    if (groupModalEdit.value) {
      await api.put("/jsonmodels/groups", {
        old_group: groupEditOldName,
        new_group: groupForm.name,
      });
      message.value = "Group renamed";
    } else {
      await api.post("/jsonmodels/groups", { group: groupForm.name });
      message.value = "Group added";
    }
    messageType.value = "success";
    showGroupModal.value = false;
    await fetchData();
  } catch (e) {
    message.value = getErrorMessage(e);
    messageType.value = "error";
  } finally {
    savingGroup.value = false;
  }
}

async function deleteGroup(name: string): Promise<void> {
  if (!confirm(`Delete group "${name}"?`)) return;
  try {
    await api.delete("/jsonmodels/groups", { data: { group: name } });
    message.value = "Group deleted";
    messageType.value = "success";
    await fetchData();
  } catch (e) {
    message.value = getErrorMessage(e);
    messageType.value = "error";
  }
}

// --- Model CRUD ---
function openAddModelModal(groupName: string = ""): void {
  modelModalEdit.value = false;
  Object.assign(modelForm, {
    group: groupName,
    url: "",
    src: "",
    dest: "${BASE_DIR}/models/",
    git: "",
    type: "",
    tags: [],
    hash: "",
    size: null,
    comments: "",
    sourceType: "url",
  });

  // Reset type selector state
  showTypeDropdown.value = false;
  typeSearchQuery.value = "";

  showModelModal.value = true;
}

function openEditModelModal(row: JsonModel): void {
  modelModalEdit.value = true;
  const hasUrl = !!(row.url || row.src);
  const hasGit = !!row.git;

  Object.assign(modelForm, {
    group: findGroupOfModel(row),
    url: row.url || "",
    src: row.src || "",
    dest: row.dest || "",
    git: row.git || "",
    type: row.type || "",
    tags: Array.isArray(row.tags) ? [...row.tags] : row.tags ? [row.tags] : [],
    hash: row.hash || "",
    size: row.size || null,
    comments: row.comments || "",
    sourceType: hasGit ? "git" : "url",
  });

  // Reset type selector state
  showTypeDropdown.value = false;
  typeSearchQuery.value = "";

  showModelModal.value = true;
}

function findGroupOfModel(model: JsonModel): string {
  for (const g of sortableGroupList.value) {
    if (
      g.models.some(
        (m: JsonModel) => (m.dest || m.git) === (model.dest || model.git)
      )
    ) {
      return g.name;
    }
  }
  return "";
}

async function submitModelForm(): Promise<void> {
  // Validate required fields
  if (!modelForm.group) {
    message.value = "Group is required";
    messageType.value = "error";
    return;
  }

  if (modelForm.sourceType === "url" && !modelForm.dest) {
    message.value = "Destination is required for URL downloads";
    messageType.value = "error";
    return;
  }

  if (modelForm.sourceType === "git" && !modelForm.git) {
    message.value = "Git repository URL is required";
    messageType.value = "error";
    return;
  }

  savingModel.value = true;
  try {
    const entry: Partial<JsonModel> = {
      type: modelForm.type,
      tags: modelForm.tags,
      comments: modelForm.comments,
    };

    // Add fields based on source type
    if (modelForm.sourceType === "url") {
      if (modelForm.url) entry.url = modelForm.url;
      if (modelForm.src) entry.src = modelForm.src;
      entry.dest = modelForm.dest; // Required field, always include
    } else if (modelForm.sourceType === "git") {
      entry.git = modelForm.git; // Required field, always include
    }

    // Add hash and size only if in edit mode and they have values
    if (modelModalEdit.value) {
      if (modelForm.hash) entry.hash = modelForm.hash;
      if (modelForm.size) entry.size = modelForm.size;
    }

    if (modelModalEdit.value) {
      await api.put("/jsonmodels/entry", { group: modelForm.group, entry });
      message.value = "Model modified";
      success("Model updated successfully", 5000, true);
    } else {
      await api.post("/jsonmodels/entry", { group: modelForm.group, entry });
      message.value = "Model added";
      success("Model added successfully", 5000, true);
    }

    messageType.value = "success";
    showModelModal.value = false;
    await fetchData();
  } catch (e) {
    const errorMessage = getErrorMessage(e);
    message.value = errorMessage;
    messageType.value = "error";
    showError(`Model operation failed: ${errorMessage}`, 8000, true);
  } finally {
    savingModel.value = false;
  }
}

async function deleteModel(row: JsonModel): Promise<void> {
  if (!confirm("Delete this model?")) return;
  try {
    await api.delete("/jsonmodels/entry", {
      data: {
        group: findGroupOfModel(row),
        entry: { dest: row.dest, git: row.git },
      },
    });
    message.value = "Model deleted";
    messageType.value = "success";
    await fetchData();
  } catch (e) {
    message.value = getErrorMessage(e);
    messageType.value = "error";
  }
}

// --- Mount ---
onMounted(fetchData);
</script>

<style scoped>
/* Drag and drop styles */
.cursor-move {
  cursor: move;
}

.cursor-move:hover {
  background-color: rgba(59, 130, 246, 0.1);
}

.cursor-move:active {
  background-color: rgba(59, 130, 246, 0.2);
}

/* Dragging state */
tr[draggable="true"]:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

/* Drag over indicator */
tr.bg-blue-100 {
  background-color: rgba(59, 130, 246, 0.1) !important;
  border: 2px dashed #3b82f6;
}

.dark tr.bg-blue-900 {
  background-color: rgba(59, 130, 246, 0.2) !important;
  border: 2px dashed #60a5fa;
}

/* Smooth transitions */
tbody tr {
  transition:
    background-color 0.15s ease,
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

/* Drag and drop enhancements */
.dragging-row {
  opacity: 0.4;
  transform: scale(0.98);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.drag-over-row {
  background-color: rgba(34, 197, 94, 0.1);
  transform: scale(1.02);
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
}

.drop-indicator {
  height: 2px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  animation: shimmer 1.5s infinite;
  margin: 0 1rem;
  border-radius: 1px;
}

@keyframes shimmer {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

/* Ghost element styling (for better visual feedback) */
.drag-ghost {
  transform: rotate(3deg);
  opacity: 0.8;
  background-color: rgba(59, 130, 246, 0.1);
  border: 2px dashed #3b82f6;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

/* Disable pointer events on buttons during drag */
tr.dragging-row button {
  pointer-events: none;
  opacity: 0.5;
}

/* Type selector styles */
.type-dropdown {
  backdrop-filter: blur(8px);
  background-color: rgba(var(--background-soft-rgb), 0.95);
}

.type-dropdown-item {
  transition: all 0.15s ease;
}

.type-dropdown-item:hover {
  background-color: rgba(var(--background-mute-rgb), 0.8);
  transform: translateX(2px);
}

/* Custom scrollbar for type dropdown */
.type-dropdown::-webkit-scrollbar {
  width: 6px;
}

.type-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.type-dropdown::-webkit-scrollbar-thumb {
  background-color: rgba(var(--text-light-rgb), 0.3);
  border-radius: 3px;
}

.type-dropdown::-webkit-scrollbar-thumb:hover {
  background-color: rgba(var(--text-light-rgb), 0.5);
}

/* Optional: custom styles to harmonize with the UI */
</style>
