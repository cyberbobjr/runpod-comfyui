<template>
  <div>
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading models.json file...</p>
    </div>

    <div v-else-if="jsonError" class="alert alert-danger">
      {{ jsonError }}
    </div>

    <div v-else>
      <!-- Message de notification -->
      <div
        v-if="saveMessage"
        class="alert"
        :class="saveSuccess ? 'alert-success' : 'alert-danger'"
      >
        {{ saveMessage }}
      </div>

      <!-- Boutons d'action -->
      <div class="d-flex justify-content-end mb-3">
        <button
          class="btn btn-success me-1"
          @click="showAddGroupModal = true"
        >
          <i class="fas fa-plus me-1"></i> Add Group
        </button>
        <button class="btn btn-success me-2" @click="openModelModal()">
          <i class="fas fa-plus me-1"></i>
          Add Model
        </button>
        <button
          class="btn btn-outline-primary"
          @click="fetchJsonData"
          :disabled="isLoading"
        >
          <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': isLoading }"></i>
          Refresh Data
        </button>
      </div>

      <!-- Accordéon principal -->
      <div class="accordion" id="mainAccordion">
        <!-- Configuration de base -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingConfig">
            <button
              class="accordion-button"
              :class="{ collapsed: !isAccordionOpen('mainAccordion', 'collapseConfig') }"
              type="button"
              @click="toggleAccordion('mainAccordion', 'collapseConfig')"
            >
              <i class="fas fa-cog me-2"></i>Base Configuration
            </button>
          </h2>
          <div
            class="accordion-collapse collapse"
            :class="{ show: isAccordionOpen('mainAccordion', 'collapseConfig') }"
          >
            <div class="accordion-body">
              <div class="input-group mb-3">
                <span class="input-group-text"
                  ><i class="fas fa-folder me-1"></i
                ></span>
                <input
                  type="text"
                  class="form-control"
                  v-model="baseDir"
                  placeholder="Path to models directory"
                />
                <button class="btn btn-primary" @click="saveBaseDir">
                  <i class="fas fa-save me-1"></i> Save Base Directory
                </button>
              </div>
              <small class="text-muted d-block mt-2">
                <i class="fas fa-info-circle me-1"></i> This is the base
                directory where models will be stored. Use this path in model
                entries with ${BASE_DIR} variable.
              </small>
            </div>
          </div>
        </div>

        <!-- Gestion des groupes -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingGroups">
            <button
              class="accordion-button"
              :class="{ collapsed: !isAccordionOpen('mainAccordion', 'collapseGroups') }"
              type="button"
              @click="toggleAccordion('mainAccordion', 'collapseGroups')"
            >
              <i class="fas fa-layer-group me-2"></i>Model Groups
            </button>
          </h2>
          <div
            class="accordion-collapse collapse"
            :class="{ show: isAccordionOpen('mainAccordion', 'collapseGroups') }"
          >
            <div class="accordion-body">
              <div class="list-group list-group-flush">
                <div
                  v-for="(models, groupName) in jsonData?.groups"
                  :key="groupName"
                  class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                >
                  <div>
                    <i class="fas fa-folder me-2"></i
                    ><strong>{{ groupName }}</strong>
                    <span class="badge bg-primary ms-2"
                      >{{ models.length }} models</span
                    >
                  </div>
                  <div>
                    <button
                      class="btn btn-sm btn-outline-secondary me-2"
                      @click="prepareEditGroup(groupName)"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteGroup(groupName)"
                    >
                      <i class="fas fa-trash-alt"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Retirer l'accordéon du formulaire d'ajout/édition de modèle -->

        <!-- Liste des modèles par groupe -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingList">
            <button
              class="accordion-button"
              :class="{ collapsed: !isAccordionOpen('mainAccordion', 'collapseList') }"
              type="button"
              @click="toggleAccordion('mainAccordion', 'collapseList')"
            >
              <i class="fas fa-list me-2"></i>Model Entries
            </button>
          </h2>
          <div
            class="accordion-collapse collapse"
            :class="{ show: isAccordionOpen('mainAccordion', 'collapseList') }"
          >
            <div class="accordion-body p-0">
              <div class="accordion" id="modelsAccordion">
                <div
                  v-for="(models, groupName, idx) in jsonData?.groups"
                  :key="groupName"
                  class="accordion-item"
                >
                  <h2 class="accordion-header" :id="`heading-${idx}`">
                    <button
                      class="accordion-button"
                      :class="{ collapsed: !isAccordionOpen('modelsGroups', `collapse-${idx}`) }"
                      type="button"
                      @click="toggleAccordion('modelsGroups', `collapse-${idx}`)"
                    >
                      {{ groupName }}
                      <span class="badge bg-primary ms-2">{{ models.length }} models</span>
                    </button>
                  </h2>
                  <div
                    :id="`collapse-${idx}`"
                    class="accordion-collapse collapse"
                    :class="{ show: isAccordionOpen('modelsGroups', `collapse-${idx}`) }"
                  >
                    <div class="accordion-body p-0">
                      <div class="table-responsive">
                        <table class="table table-bordered mb-0">
                          <thead class="table-light">
                            <tr>
                              <th>Name</th>
                              <th>Type</th>
                              <th>Tags</th>
                              <th>Size</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(model, index) in models" :key="index">
                              <td>
                                <span
                                  :class="{
                                    'text-danger fw-bold': isNSFW(model),
                                  }"
                                >
                                  {{
                                    model.dest
                                      ? model.dest.split("/").pop()
                                      : model.git
                                      ? model.git.split("/").pop()
                                      : "Unnamed"
                                  }}
                                </span>
                              </td>
                              <td>{{ model.type || "-" }}</td>
                              <td>
                                <span
                                  v-for="tag in Array.isArray(model.tags)
                                    ? model.tags
                                    : model.tags
                                    ? [model.tags]
                                    : []"
                                  :key="tag"
                                  class="badge bg-secondary me-1"
                                >
                                  {{ tag }}
                                </span>
                              </td>
                              <td>
                                {{
                                  model.size
                                    ? (model.size / 1024 / 1024).toFixed(2) +
                                      " MB"
                                    : "-"
                                }}
                              </td>
                              <td>
                                <button
                                  class="btn btn-sm btn-outline-primary me-2"
                                  @click="openModelModal(groupName, model)"
                                >
                                  <i class="fas fa-edit"></i>
                                </button>
                                <button
                                  class="btn btn-sm btn-outline-danger"
                                  @click="deleteModelEntry(groupName, model)"
                                >
                                  <i class="fas fa-trash-alt"></i>
                                </button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal pour ajouter un groupe -->
      <div
        class="modal fade"
        id="addGroupModal"
        tabindex="-1"
        :class="{ 'show d-block': showAddGroupModal }"
        :style="{ display: showAddGroupModal ? 'block' : 'none' }"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="fas fa-folder-plus me-2"></i>Add New Group
              </h5>
              <button
                type="button"
                class="btn-close"
                @click="showAddGroupModal = false"
              ></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Group Name</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="newGroupName"
                  placeholder="Enter group name"
                />
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="showAddGroupModal = false"
              >
                <i class="fas fa-times me-1"></i> Cancel
              </button>
              <button type="button" class="btn btn-primary" @click="addGroup">
                <i class="fas fa-plus me-1"></i> Add Group
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="showAddGroupModal" class="modal-backdrop fade show"></div>

      <!-- Modal pour éditer un groupe -->
      <div
        class="modal fade"
        id="editGroupModal"
        tabindex="-1"
        :class="{ 'show d-block': showEditGroupModal }"
        :style="{ display: showEditGroupModal ? 'block' : 'none' }"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="fas fa-edit me-2"></i>Rename Group
              </h5>
              <button
                type="button"
                class="btn-close"
                @click="showEditGroupModal = false"
              ></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">New Group Name</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="newGroupName"
                  placeholder="Enter new group name"
                />
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="showEditGroupModal = false"
              >
                <i class="fas fa-times me-1"></i> Cancel
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="updateGroupName"
              >
                <i class="fas fa-save me-1"></i> Rename Group
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="showEditGroupModal" class="modal-backdrop fade show"></div>

      <!-- Nouvelle Modal pour ajouter/éditer un modèle -->
      <div
        v-if="showModelModal"
        class="modal-overlay"
        @click.self="closeModelModal"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i
                class="fas"
                :class="formData.dest || formData.git ? 'fa-edit' : 'fa-plus'"
              ></i>
              {{
                formData.dest || formData.git ? " Edit Model" : " Add New Model"
              }}
              <span v-if="currentGroup" class="badge bg-info ms-2">{{
                currentGroup
              }}</span>
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeModelModal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <ModelForm
              v-model:formData="modelFormData"
              :groups="jsonData?.groups ? Object.keys(jsonData.groups) : []"
              :isSubmitting="isSubmitting"
              :error="saveMessage && !saveSuccess ? saveMessage : ''"
              @submit="
                formData.dest || formData.git
                  ? updateModelEntry()
                  : addModelEntry()
              "
              @cancel="closeModelModal"
            />
          </div>
        </div>
      </div>
      <div v-if="showModelModal" class="modal-backdrop fade show"></div>
    </div>

    <!-- Modal pour ajouter un groupe -->
    <div
      class="modal fade"
      id="addGroupModal"
      tabindex="-1"
      :class="{ 'show d-block': showAddGroupModal }"
      :style="{ display: showAddGroupModal ? 'block' : 'none' }"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-folder-plus me-2"></i>Add New Group
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="showAddGroupModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Group Name</label>
              <input
                type="text"
                class="form-control"
                v-model="newGroupName"
                placeholder="Enter group name"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showAddGroupModal = false"
            >
              <i class="fas fa-times me-1"></i> Cancel
            </button>
            <button type="button" class="btn btn-primary" @click="addGroup">
              <i class="fas fa-plus me-1"></i> Add Group
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showAddGroupModal" class="modal-backdrop fade show"></div>

    <!-- Modal pour éditer un groupe -->
    <div
      class="modal fade"
      id="editGroupModal"
      tabindex="-1"
      :class="{ 'show d-block': showEditGroupModal }"
      :style="{ display: showEditGroupModal ? 'block' : 'none' }"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-edit me-2"></i>Rename Group
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="showEditGroupModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">New Group Name</label>
              <input
                type="text"
                class="form-control"
                v-model="newGroupName"
                placeholder="Enter new group name"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showEditGroupModal = false"
            >
              <i class="fas fa-times me-1"></i> Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="updateGroupName"
            >
              <i class="fas fa-save me-1"></i> Rename Group
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showEditGroupModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import {
  jsonData,
  jsonError,
  isLoading,
  isSubmitting,
  saveMessage,
  saveSuccess,
  formData,
  modelFormData,
  baseDir,
  currentGroup,
  showAddGroupModal,
  showEditGroupModal,
  showModelModal,
  newGroupName,
  fetchJsonData,
  saveBaseDir,
  addGroup,
  updateGroupName,
  deleteGroup,
  prepareEditGroup,
  openModelModal,
  closeModelModal,
  addModelEntry,
  updateModelEntry,
  deleteModelEntry,
  resetForm,
  useAppLogic,
  isNSFW,
  openAccordions,
  toggleAccordion,
  isAccordionOpen
} from "./JsonEditor.logic.js";
import ModelForm from "./components/ModelForm.vue";

// Initialiser les données au chargement
useAppLogic();
fetchJsonData();
</script>

<style scoped>
/* Style pour les modaux personnalisés */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

/* Matching FilePropertiesTable.vue modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-content {
  /* Increased width for better readability */
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  /* Using Superhero theme colors */
  background-color: #2b3e50;
  color: #fff;
  border-radius: 6px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #4e5d6c;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: 1.5rem;
}

/* Form control styling to match Superhero theme */
.form-control,
.form-select {
  background-color: #4e5d6c;
  border-color: #4e5d6c;
  color: #fff;
}

.form-control:focus,
.form-select:focus {
  background-color: #5d6d7e;
  color: #fff;
  border-color: #5d6d7e;
  box-shadow: 0 0 0 0.25rem rgba(255, 255, 255, 0.25);
}

.form-control:read-only {
  background-color: #3e4d5c;
}

/* Form text helper styling */
.form-text {
  color: #aaa;
}

/* Button styling to match Superhero theme */
.btn-primary {
  background-color: #df691a;
  border-color: #df691a;
}

.btn-primary:hover,
.btn-primary:focus {
  background-color: #b15315;
  border-color: #b15315;
}

.btn-secondary {
  background-color: #4e5d6c;
  border-color: #4e5d6c;
}

.btn-secondary:hover,
.btn-secondary:focus {
  background-color: #3e4d5c;
  border-color: #3e4d5c;
}

/* Ensure the close button is visible */
.btn-close {
  filter: invert(1) grayscale(100%) brightness(200%);
}

/* Alert styling */
.alert-danger {
  background-color: #e74c3c;
  border-color: #e74c3c;
  color: #fff;
}

/* Also apply the same styling to the add/edit group modals */
#addGroupModal .modal-content,
#editGroupModal .modal-content {
  background-color: #2b3e50;
  color: #fff;
}

/* Fix the styling for other group modals */
.modal-fade {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-backdrop {
  z-index: 1040;
}
</style>
