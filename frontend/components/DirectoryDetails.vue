<template>
  <div class="directory-details d-flex flex-column h-100">
    <!-- Toolbar -->
    <div class="toolbar-container d-flex align-items-center mb-1">
      <span class="me-2"
        ><strong>Current:</strong> <code>{{ currentPath || "/" }}</code></span
      >
      <button
        class="btn btn-secondary btn-sm ms-2"
        @click="$emit('go-up')"
        :disabled="!currentPath"
      >
        <i class="fa-solid fa-arrow-up"></i> Up
      </button>
      <button
        class="btn btn-outline-primary btn-sm ms-2"
        @click="$emit('refresh')"
      >
        <i class="fa-solid fa-sync"></i> Refresh
      </button>
      <div class="ms-auto">
        <label for="fileUpload" class="btn btn-success btn-sm">
          <i class="fa-solid fa-upload"></i> Upload
          <input
            type="file"
            id="fileUpload"
            class="d-none"
            @change="$emit('file-upload', $event)"
          />
        </label>
        <button
          class="btn btn-outline-success btn-sm ms-2"
          @click="$emit('create-directory')"
        >
          <i class="fa-solid fa-folder-plus"></i> New Folder
        </button>
      </div>
    </div>

    <!-- Details Container -->
    <div class="details-container flex-grow-1 overflow-auto">
      <!-- Subdirectories Section -->
      <div class="subdirectory-list-container mb-2">
        <h5>Subdirectories</h5>
        <div class="subdirectory-list">
          <div
            v-for="dir in dirs"
            :key="dir.path"
            class="subdirectory-item d-flex justify-content-between align-items-center"
            :class="{ 'active-item': currentPath === dir.path }"
            @mouseover="hoveredItem = dir.path"
            @mouseleave="hoveredItem = null"
            @dblclick="$emit('navigate-to-folder', dir.path)"
          >
            <div class="d-flex align-items-center subdirectory-name">
              <i class="fa-solid fa-folder me-2"></i>
              <span>{{ dir.name }}</span>
            </div>
            <div
              class="subdirectory-actions"
              :class="{
                visible: hoveredItem === dir.path || currentPath === dir.path,
              }"
            >
              <button
                class="btn btn-sm btn-outline-primary me-1"
                @click.stop="$emit('navigate-to-folder', dir.path)"
                v-tooltip="'Open this folder'"
              >
                <i class="fa-solid fa-folder-open"></i>
              </button>
              <button
                class="btn btn-sm btn-rename me-1"
                @click.stop="$emit('rename', dir)"
                v-tooltip="'Rename folder'"
              >
                <i class="fa-solid fa-pencil"></i>
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                @click.stop="$emit('delete', dir)"
                v-tooltip="'Delete folder'"
              >
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </div>
          <div
            v-if="!dirs || dirs.length === 0"
            class="text-muted text-center py-3"
          >
            <em>No subdirectories in this directory</em>
          </div>
        </div>
      </div>

      <!-- Existing Files Section -->
      <div class="file-list-container mb-2">
        <h5>Files</h5>
        <div class="file-list">
          <div
            v-for="file in files"
            :key="file.name"
            class="file-item d-flex justify-content-between align-items-center"
            :class="{
              'active-file': selectedFile === file,
              'registered-model': file.is_registered && !file.is_corrupted,
              'corrupted-file': file.is_corrupted,
            }"
            @click="$emit('select-file', file)"
          >
            <div class="d-flex align-items-center file-name">
              <i class="fa-solid fa-file-lines me-2 file-icon"></i>
              <span>{{ file.name }}</span>
              <span
                v-if="file.is_registered && !file.is_corrupted"
                class="badge bg-success ms-2"
                v-tooltip="
                  'This model is registered in models.json and ready to use'
                "
              >
                <i class="fa-solid fa-check-circle"></i>
              </span>
              <span
                v-if="file.is_corrupted"
                class="badge bg-danger ms-2"
                v-tooltip="{
                  content: `This file may be corrupted. Expected size: ${formatSize(
                    file.expected_size
                  )}, Actual size: ${formatSize(file.actual_size)}`,
                  theme: 'light',
                  placement: 'top',
                }"
              >
                <i class="fa-solid fa-exclamation-triangle"></i>
              </span>
            </div>
            <div class="file-actions">
              <button
                class="btn btn-sm btn-outline-primary me-1"
                @click.stop="$emit('download', file)"
                v-tooltip="'Download this file'"
              >
                <i class="fa-solid fa-download"></i>
              </button>
              <button
                class="btn btn-sm btn-rename me-1"
                @click.stop="$emit('rename', file)"
                v-tooltip="'Rename file'"
              >
                <i class="fa-solid fa-pencil"></i>
              </button>
              <button
                class="btn btn-sm btn-outline-info me-1"
                @click.stop="$emit('copy', file)"
                v-tooltip="'Make a copy of this file'"
              >
                <i class="fa-solid fa-copy"></i>
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                @click.stop="$emit('delete', file)"
                v-tooltip="'Delete this file'"
              >
                <i class="fa-solid fa-trash"></i>
              </button>
            </div>
          </div>
          <div v-if="files.length === 0" class="text-muted text-center py-3">
            <em>No files in this directory</em>
          </div>
        </div>
      </div>

      <!-- File Properties Card -->
      <div class="file-properties-container">
        <h5>
          File Properties
          <span
            v-if="
              selectedFile &&
              selectedFile.is_registered &&
              !selectedFile.is_corrupted
            "
            class="badge bg-success ms-2"
            v-tooltip="{
              content:
                'This file is referenced in models.json and is ready to use with ComfyUI',
              placement: 'right',
            }"
          >
            Registered Model
          </span>
          <span
            v-if="selectedFile && selectedFile.is_corrupted"
            class="badge bg-danger ms-2"
            v-tooltip="{
              content: `This file may be corrupted. The file size does not match what is expected in models.json.
                     Expected: ${formatSize(selectedFile.expected_size)} 
                     Actual: ${formatSize(selectedFile.actual_size)}`,
              placement: 'right',
              maxWidth: 350,
            }"
          >
            Potentially Corrupted
          </span>
        </h5>
        <file-properties-table
          v-if="fileProps"
          :file-props="fileProps"
          :selected-file="selectedFile"
          :format-size="formatSize"
          :format-date="formatDate"
          :shorten-url="shortenUrl"
        />
        <div v-else class="text-muted">
          Select a file to see its properties.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FilePropertiesTable from "./FilePropertiesTable.vue";
import { ref } from "vue";

const props = defineProps({
  currentPath: String,
  files: Array,
  dirs: Array,
  selectedFile: Object,
  fileProps: Object,
  formatSize: Function,
  formatDate: Function,
  shortenUrl: Function,
});

const emit = defineEmits([
  "go-up",
  "refresh",
  "file-upload",
  "create-directory",
  "navigate-to-folder",
  "select-file",
  "rename",
  "delete",
  "download",
  "copy",
]);

const hoveredItem = ref(null);
</script>

<style scoped>
.directory-details {
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure the component takes full height of its parent */
}

.toolbar-container {
  flex: 0 0 auto; /* Fix the toolbar height */
}

.details-container {
  flex: 1 1 auto; /* Occupy remaining space */
  overflow-y: auto; /* Add internal scrolling */
  height: 0; /* Ensure it doesn't exceed the parent's height */
}

.subdirectory-list-container,
.file-list-container,
.file-properties-container {
  margin-bottom: 1rem;
}

.subdirectory-list,
.file-list {
  max-height: 100%;
}

.file-properties-container {
  overflow-y: auto;
}

/* Styles pour la liste de fichiers */
.file-list {
  border: 1px solid #4e5d6c; /* Couleur de bordure superhero */
  border-radius: 0.25rem;
  overflow: hidden;
}

.file-item {
  padding: 10px 15px;
  border-bottom: 1px solid #4e5d6c; /* Couleur de bordure superhero */
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: rgba(68, 157, 209, 0.1); /* Bleu superhero plus léger */
}

.active-file {
  background-color: rgba(68, 157, 209, 0.2); /* Bleu superhero */
  border-left: 3px solid #5cb85c; /* Vert superhero */
}

.file-name {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
}

.file-icon {
  color: #5bc0de; /* Bleu clair superhero */
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.file-actions {
  display: flex;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s;
}

.file-item:hover .file-actions {
  visibility: visible;
  opacity: 1;
}

.active-file .file-actions {
  visibility: visible;
  opacity: 1;
}

.corrupted-file {
  background-color: rgba(217, 83, 79, 0.1); /* Rouge superhero plus léger */
}

.corrupted-file .file-icon {
  color: #d9534f; /* Rouge superhero */
}

/* Styles pour les boutons d'actions */
.btn-outline-primary {
  border-color: #5bc0de; /* Bleu clair superhero */
  color: #5bc0de;
}

.btn-outline-primary:hover {
  background-color: #5bc0de;
  color: #2b3e50; /* Fond superhero */
}

/* Style spécifique pour le bouton de renommage - plus visible */
.btn-rename {
  border-color: #f0ad4e; /* Couleur jaune/ambre */
  color: #f0ad4e;
  background-color: rgba(240, 173, 78, 0.1); /* Fond légèrement teinté */
  font-weight: 500; /* Légèrement plus gras */
}

.btn-rename:hover {
  background-color: #f0ad4e;
  color: #fff;
  border-color: #f0ad4e;
}

.btn-outline-danger {
  border-color: #d9534f; /* Rouge superhero */
  color: #d9534f;
}

.btn-outline-danger:hover {
  background-color: #d9534f;
  color: #fff;
}

.btn-outline-secondary {
  border-color: #4e5d6c; /* Gris superhero */
  color: #4e5d6c;
}

.btn-outline-secondary:hover {
  background-color: #4e5d6c;
  color: #fff;
}

.btn-outline-info {
  border-color: #5bc0de; /* Bleu clair superhero */
  color: #5bc0de;
}

.btn-outline-info:hover {
  background-color: #5bc0de;
  color: #2b3e50;
}

.registered-model {
  background-color: rgba(92, 184, 92, 0.1); /* Vert superhero plus léger */
}

.registered-model .file-icon {
  color: #5cb85c; /* Vert superhero */
}

/* Styles personnalisés pour les tooltips Tippy */
:deep(.tippy-box[data-theme~="light"]) {
  background-color: #4e5d6c; /* Fond secondaire superhero */
  color: #fff; /* Texte blanc pour contraste */
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  font-size: 0.95rem;
  padding: 5px;
}

:deep(
    .tippy-box[data-theme~="light"][data-placement^="top"]
      > .tippy-arrow::before
  ) {
  border-top-color: #4e5d6c;
}

:deep(
    .tippy-box[data-theme~="light"][data-placement^="bottom"]
      > .tippy-arrow::before
  ) {
  border-bottom-color: #4e5d6c;
}

:deep(
    .tippy-box[data-theme~="light"][data-placement^="left"]
      > .tippy-arrow::before
  ) {
  border-left-color: #4e5d6c;
}

:deep(
    .tippy-box[data-theme~="light"][data-placement^="right"]
      > .tippy-arrow::before
  ) {
  border-right-color: #4e5d6c;
}

.source-link {
  color: #df691a; /* Orange superhero */
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
}

.source-link:hover {
  color: #ff8d3f; /* Orange plus clair */
  text-decoration: underline;
}

.source-link .fa-external-link-alt {
  font-size: 0.8em;
}

/* Styles supplémentaires pour la card */
.card {
  border-color: #4e5d6c;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header h2 {
  font-weight: 300;
  letter-spacing: 0.5px;
}

/* Ajustement pour la cohérence des cards intérieures */
.card .card {
  border-color: #4e5d6c;
  box-shadow: none;
}

/* Ajustements pour le thème superhero */
.card-header.bg-primary {
  background-color: #df691a !important; /* Orange superhero au lieu du bleu primary */
}

.card-header.bg-primary h2 {
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Subdirectory list styles */
.subdirectory-item {
  padding: 10px 15px;
  border-bottom: 1px solid #4e5d6c; /* Match file list border */
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.subdirectory-item:last-child {
  border-bottom: none;
}

.subdirectory-item:hover {
  background-color: rgba(68, 157, 209, 0.1); /* Match file list hover color */
}

.active-item {
  background-color: rgba(68, 157, 209, 0.2); /* Match file list active color */
  border-left: 3px solid #5cb85c; /* Match file list active border */
}

.subdirectory-name {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
}

.subdirectory-actions {
  display: flex;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.3s;
}

.subdirectory-item:hover .subdirectory-actions,
.active-item .subdirectory-actions {
  visibility: visible;
  opacity: 1;
}
</style>
