<template>
  <div class="space-y-6 p-4 bg-background">
    <!-- Loading/Error -->
    <div v-if="loading" class="flex justify-center items-center min-h-[200px]">
      <div class="flex flex-col items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        <p class="mt-2 text-text-light">Loading models.json file...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="bg-red-900 text-white p-4 rounded-md border border-red-700 flex items-start">
      <svg class="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>{{ error }}</span>
    </div>

    <template v-else>
      <!-- Success/Error Message -->
      <div v-if="message" 
           :class="{
             'bg-green-900 text-white border-green-700': messageType === 'success',
             'bg-red-900 text-white border-red-700': messageType === 'error'
           }"
           class="p-4 rounded-md border flex items-start">
        <svg v-if="messageType === 'success'" class="w-5 h-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <svg v-else class="w-5 h-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>{{ message }}</span>
        <button @click="message = ''" class="ml-auto">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>      <!-- Group Management -->
      <AccordionComponent 
        title="Model Groups" 
        icon="layer-group"
        :default-open="true"
        class="mt-6"
      >
        <div class="flex justify-end space-x-4 mb-4">
          <button type="button" class="btn btn-default" @click="fetchData" :disabled="loading">
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refreshing...
            </span>
            <span v-else>Refresh</span>
          </button>
          <button type="button" class="btn btn-primary" @click="openAddGroupModal">
            Add Group
          </button>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-border">
            <thead class="bg-background-mute">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Name</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-background-soft divide-y divide-border">
              <tr v-for="group in groupList" :key="group.name" class="hover:bg-background-mute">
                <td class="px-4 py-3 text-text-light">{{ group.name }}</td>
                <td class="px-4 py-3">
                  <div class="flex space-x-2">
                    <button
                      type="button"
                      class="px-3 py-1 bg-btn-default text-white rounded hover:bg-btn-default-hover text-sm"
                      @click="openEditGroupModal(group.name)"
                    >
                      Rename
                    </button>
                    <button
                      type="button"
                      class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                      @click="deleteGroup(group.name)"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </AccordionComponent>      <!-- Models by Group -->
      <AccordionComponent 
        title="Models by Group" 
        icon="cubes"
        :default-open="true"
        class="mt-6"
      >
        <div class="flex justify-end mb-4">
          <button 
            type="button" 
            class="btn btn-primary"
            @click="openAddModelModal()"
          >
            Add Model
          </button>
        </div>
        
        <div v-if="groupList.length" class="space-y-4">
          <AccordionComponent 
            v-for="group in groupList" 
            :key="group.name"
            :title="`${group.name} (${group.models.length})`" 
            icon="folder"
            :default-open="false"
          >
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-border">
                <thead class="bg-background-mute">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Name</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Type</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">URL</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Tags</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Size</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-text-light uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-background-soft divide-y divide-border">
                  <tr v-for="model in group.models" :key="model.dest || model.git" class="hover:bg-background-mute">
                    <td class="px-4 py-3">
                      <span :class="{ 'text-red-500 font-bold': isNSFW(model) }">
                        {{ getModelName(model) }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-text-light">{{ model.type }}</td>
                    <td class="px-4 py-3">
                      <a 
                        v-if="model.src" 
                        :href="model.src" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="text-blue-400 hover:text-blue-300"
                        :title="model.src"
                      >
                        <FontAwesomeIcon icon="external-link-alt" class="w-4 h-4" />
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
                      {{ model.size ? (model.size / 1024 / 1024).toFixed(2) + " MB" : "-" }}
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
        <div v-else class="flex flex-col items-center justify-center py-12 text-text-light-muted">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
          </svg>
          <p class="text-lg">No model groups.</p>
        </div>
      </AccordionComponent>
    </template>

    <!-- Modal: Add/Edit Group -->
    <div v-if="showGroupModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" @click="showGroupModal = false">
          <div class="absolute inset-0 bg-black opacity-50"></div>
        </div>

        <span class="hidden sm:inline-block sm:align-middle sm:h-screen"></span>&#8203;

        <div class="inline-block align-bottom bg-background-soft rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
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
          
          <div class="bg-background-mute px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button" 
              class="btn btn-primary ml-2"
              @click="submitGroupForm"
              :disabled="savingGroup"
            >
              <span v-if="savingGroup" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
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
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" @click="showModelModal = false">
          <div class="absolute inset-0 bg-black opacity-50"></div>
        </div>

        <span class="hidden sm:inline-block sm:align-middle sm:h-screen"></span>&#8203;

        <div class="inline-block align-bottom bg-background-soft rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg font-medium leading-6 text-text-light mb-4">
              {{ modelModalTitle }}
            </h3>
            
            <form @submit.prevent="submitModelForm" class="space-y-4">
              <div>
                <label class="form-label">Group Name</label>
                <select v-model="modelForm.group" class="form-input" required>
                  <option value="" disabled>Select a group</option>
                  <option v-for="group in groupList" :key="group.name" :value="group.name">
                    {{ group.name }}
                  </option>
                </select>
              </div>
              
              <div>
                <label class="form-label">URL</label>
                <input v-model="modelForm.url" type="text" class="form-input" placeholder="Model URL" />
              </div>
              
              <div>
                <label class="form-label">Destination</label>
                <input v-model="modelForm.dest" type="text" class="form-input" placeholder="Destination path" />
              </div>
              
              <div>
                <label class="form-label">Git</label>
                <input v-model="modelForm.git" type="text" class="form-input" placeholder="Git repository URL" />
              </div>
              
              <div>
                <label class="form-label">Type</label>
                <input v-model="modelForm.type" type="text" class="form-input" placeholder="Model type" />
              </div>
              
              <div>
                <label class="form-label">Tags</label>
                <div class="flex flex-wrap gap-2 p-2 border border-border rounded">
                  <div v-for="(tag, index) in modelForm.tags" :key="index" class="bg-background-mute px-2 py-1 rounded flex items-center">
                    <span class="text-text-light mr-2">{{ tag }}</span>
                    <button type="button" @click="removeTag(index)" class="text-text-light-muted hover:text-text-light">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                  <input
                    v-model="newTag"
                    @keydown.enter.prevent="addTag"
                    type="text"
                    class="bg-transparent border-none focus:outline-none text-text-light flex-1"
                    placeholder="Add a tag..."
                  />
                </div>
              </div>
              
              <div>
                <label class="form-label">Hash</label>
                <input v-model="modelForm.hash" type="text" class="form-input" placeholder="Hash" />
              </div>
              
              <div>
                <label class="form-label">Size (bytes)</label>
                <input v-model.number="modelForm.size" type="number" min="0" class="form-input" />
              </div>
            </form>
          </div>
          
          <div class="bg-background-mute px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button" 
              class="btn btn-primary ml-2"
              @click="submitModelForm"
              :disabled="savingModel"
            >
              <span v-if="savingModel" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
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
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useNotifications } from "../composables/useNotifications";
import api from "../services/api.js";
import AccordionComponent from "./common/AccordionComponent.vue";

// --- State ---
const { success, error: showError } = useNotifications();
const loading = ref(false);
const error = ref("");
const message = ref("");
const messageType = ref("success");
const newTag = ref("");

const data = ref({ config: {}, groups: {} });

// Groupes
const groupList = computed(() =>
  Object.entries(data.value.groups || {}).map(([name, models]) => ({
    name,
    models: Array.isArray(models) ? models : [],
  }))
);

// Group Modal
const showGroupModal = ref(false);
const groupModalEdit = ref(false);
const groupModalTitle = computed(() =>
  groupModalEdit.value ? "Rename Group" : "Add Group"
);
const groupForm = reactive({ name: "" });
let groupEditOldName = "";

// Model Modal
const showModelModal = ref(false);
const modelModalEdit = ref(false);
const modelModalTitle = computed(() =>
  modelModalEdit.value ? "Edit Model" : "Add Model"
);
const modelForm = reactive({
  group: "",
  url: "",
  dest: "",
  git: "",
  type: "",
  tags: [],
  hash: "",
  size: null,
});
const savingGroup = ref(false);
const savingModel = ref(false);

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
const getModelName = (model) => {
  return model.dest 
    ? model.dest.split("/").pop()
    : model.git
    ? model.git.split("/").pop()
    : "Unnamed";
};

const isNSFW = (model) => {
  return Array.isArray(model.tags) &&
    model.tags.some((t) => t.toLowerCase() === "nsfw");
};

const getTags = (model) => {
  if (!model.tags) return [];
  return Array.isArray(model.tags) ? model.tags : [model.tags];
};

// Tag functions
const addTag = () => {
  if (newTag.value.trim()) {
    modelForm.tags.push(newTag.value.trim());
    newTag.value = "";
  }
};

const removeTag = (index) => {
  modelForm.tags.splice(index, 1);
};

// --- API Calls ---
async function fetchData() {
  loading.value = true;
  error.value = "";
  try {    const res = await api.get("/jsonmodels/");
    const json = res.data || {};
    data.value = json;
    
    // No longer need to manage expandedGroups since AccordionComponent handles its own state
  } catch (e) {
    error.value =
      e?.response?.data?.detail || e.message || "Loading error";
  } finally {
    loading.value = false;
  }
}

// --- Group CRUD ---
function openAddGroupModal() {
  groupModalEdit.value = false;
  groupForm.name = "";
  showGroupModal.value = true;
}

function openEditGroupModal(name) {
  groupModalEdit.value = true;
  groupForm.name = name;
  groupEditOldName = name;
  showGroupModal.value = true;
}

async function submitGroupForm() {
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
    message.value = e?.response?.data?.detail || e.message;
    messageType.value = "error";
  } finally {
    savingGroup.value = false;
  }
}

async function deleteGroup(name) {
  if (!confirm(`Delete group "${name}"?`)) return;
  try {
    await api.delete("/jsonmodels/groups", { data: { group: name } });
    message.value = "Group deleted";
    messageType.value = "success";
    await fetchData();
  } catch (e) {
    message.value = e?.response?.data?.detail || e.message;
    messageType.value = "error";
  }
}

// --- Model CRUD ---
function openAddModelModal(groupName = "") {
  modelModalEdit.value = false;
  Object.assign(modelForm, {
    group: groupName,
    url: "",
    dest: "",
    git: "",
    type: "",
    tags: [],
    hash: "",
    size: null,
  });
  showModelModal.value = true;
}

function openEditModelModal(row) {
  modelModalEdit.value = true;
  Object.assign(modelForm, {
    group: findGroupOfModel(row),
    url: row.url || "",
    dest: row.dest || "",
    git: row.git || "",
    type: row.type || "",
    tags: Array.isArray(row.tags) ? [...row.tags] : row.tags ? [row.tags] : [],
    hash: row.hash || "",
    size: row.size || null,
  });
  showModelModal.value = true;
}

function findGroupOfModel(model) {
  for (const g of groupList.value) {
    if (g.models.some((m) => (m.dest || m.git) === (model.dest || model.git))) {
      return g.name;
    }
  }
  return "";
}

async function submitModelForm() {
  savingModel.value = true;
  try {
    const entry = {
      url: modelForm.url,
      dest: modelForm.dest,
      git: modelForm.git,
      type: modelForm.type,
      tags: modelForm.tags,
      hash: modelForm.hash,
      size: modelForm.size,
    };
    
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
    const errorMessage = e?.response?.data?.detail || e.message;
    message.value = errorMessage;
    messageType.value = "error";
    showError(`Model operation failed: ${errorMessage}`, 8000, true);
  } finally {
    savingModel.value = false;
  }
}

async function deleteModel(row) {
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
    message.value = e?.response?.data?.detail || e.message;
    messageType.value = "error";
  }
}

// --- Mount ---
onMounted(fetchData);
</script>

<style scoped>
/* Optional: custom styles to harmonize with the UI */
</style>
