<template>
  <div class="container py-4">
    <h2>File Manager</h2>
    <div class="mb-2">
      <button class="btn btn-secondary btn-sm" @click="goUp" :disabled="!currentPath">
        Up
      </button>
      <span class="ms-2">Current: <code>{{ currentPath || '/' }}</code></span>
      <button class="btn btn-outline-primary btn-sm ms-2" @click="refresh">
        Refresh
      </button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger py-2 px-3">{{ errorMsg }}</div>
    <div class="row">
      <div class="col-md-6">
        <h5>Directories</h5>
        <ul class="list-group mb-3">
          <li v-for="dir in dirs" :key="dir" class="list-group-item d-flex justify-content-between align-items-center">
            <span @click="goToDir(dir)" style="cursor:pointer;">
              <i class="bi bi-folder-fill text-warning"></i> {{ dir }}
            </span>
            <button class="btn btn-danger btn-sm" @click="deleteFileOrDir(dir)">Delete</button>
          </li>
          <li v-if="dirs.length === 0" class="list-group-item text-muted">No directories</li>
        </ul>
        <h5>Files</h5>
        <ul class="list-group">
          <li v-for="file in files" :key="file" class="list-group-item d-flex justify-content-between align-items-center">
            <span @click="selectFile(file)" style="cursor:pointer;">
              <i class="bi bi-file-earmark"></i> {{ file }}
            </span>
            <div>
              <button class="btn btn-danger btn-sm me-1" @click="deleteFileOrDir(file)">Delete</button>
              <button class="btn btn-secondary btn-sm" @click="promptRename(file)">Rename</button>
              <button class="btn btn-info btn-sm ms-1" @click="promptCopy(file)">Copy</button>
            </div>
          </li>
          <li v-if="files.length === 0" class="list-group-item text-muted">No files</li>
        </ul>
      </div>
      <div class="col-md-6">
        <div v-if="fileProps" class="card">
          <div class="card-body">
            <h5 class="card-title">File Properties</h5>
            <ul class="list-unstyled">
              <li><strong>Name:</strong> {{ fileProps.name }}</li>
              <li><strong>Path:</strong> {{ fileProps.path }}</li>
              <li><strong>Size:</strong> {{ formatSize(fileProps.size) }}</li>
              <li><strong>Created:</strong> {{ formatDate(fileProps.created) }}</li>
              <li><strong>Modified:</strong> {{ formatDate(fileProps.modified) }}</li>
              <li><strong>Type:</strong> 
                <span v-if="fileProps.is_dir">Directory</span>
                <span v-else-if="fileProps.is_file">File</span>
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="text-muted">Select a file to see its properties.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  currentPath, dirs, files, selectedFile, fileProps, errorMsg, refreshKey,
  fetchDirs, fetchFiles, refresh, goToDir, goUp, selectFile,
  fetchFileProps, deleteFileOrDir, renameFileOrDir, copyFile,
  formatDate, formatSize
} from './FileManager.logic.js'
import { ref } from 'vue'

const renameInput = ref('')
const copyInput = ref('')

function promptRename(file) {
  const newName = window.prompt('Rename to:', file)
  if (newName && newName !== file) {
    renameFileOrDir(file, newName)
  }
}

function promptCopy(file) {
  const newName = window.prompt('Copy to (filename):', file + '.copy')
  if (newName && newName !== file) {
    copyFile(file, newName)
  }
}

// Initial load
refresh()
</script>

<style scoped>
.bi-folder-fill, .bi-file-earmark {
  margin-right: 0.5em;
}
</style>
