<template>
  <div class="space-y-6 p-4 bg-background">
    <!-- Upload Progress Bar -->
    <div v-if="uploadProgress.isUploading" class="fixed top-0 left-0 right-0 z-50 bg-background border-b border-border shadow-lg">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center">
            <i class="fas fa-upload text-primary mr-2"></i>
            <span class="text-sm font-medium text-text-light">
              Uploading {{ uploadProgress.fileName }}...
            </span>
          </div>
          <span class="text-sm text-text-light">{{ uploadProgress.percentage }}%</span>
        </div>
        <div class="w-full bg-background-soft rounded-full h-2">
          <div 
            class="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
            :style="{ width: uploadProgress.percentage + '%' }"
          ></div>
        </div>
        <div class="mt-1 text-xs text-text-muted">
          {{ formatBytes(uploadProgress.loaded) }} / {{ formatBytes(uploadProgress.total) }}
        </div>
      </div>
    </div>

    <!-- File Manager Card -->
    <div class="card">
      <!-- Header -->
<h2 class="text-xl font-semibold text-text-light mb-4">File Manager</h2>

      <!-- Error Message -->
      <div v-if="errorMsg" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mx-4 mt-4">
        {{ errorMsg }}
      </div>

      <!-- Main Content -->
      <div class="flex-1 flex overflow-hidden p-4 space-x-4">
        <!-- Folder Tree Panel -->
        <div class="w-1/3 flex flex-col">
          <div class="border border-border rounded-lg p-4 h-full flex flex-col">
            <div class="flex items-center justify-between mb-4">
              <h5 class="text-lg font-medium">Folders</h5>
              <button
                @click="initFolderStructure"
                class="btn btn-sm btn-outline text-sm"
              >
                <i class="fas fa-refresh mr-1"></i>
                Reload
              </button>
            </div>
            
            <div v-if="!treeReady" class="flex-1 flex items-center justify-center">
              <div class="text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
                <small class="text-text-muted">Loading folders...</small>
              </div>
            </div>
            
            <div v-else class="flex-1 overflow-y-auto">
              <FolderTreeComponent
                :folders="folderStructure"
                :current-path="currentPath"
                @select-folder="navigateToFolder"
              />
            </div>
          </div>
        </div>

        <!-- File Details Panel -->
        <div class="w-2/3">
          <DirectoryDetailsComponent
            :current-path="currentPath"
            :files="files"
            :dirs="dirs"
            :selected-file="selectedFile"
            :file-props="fileProps"
            @go-up="handleGoUp"
            @refresh="refresh"
            @file-upload="handleFileUpload"
            @create-directory="promptCreateDirectory"
            @navigate-to-folder="navigateToFolder"
            @select-file="selectFile"
            @rename="promptRename"
            @delete="handleDeleteFileOrDir"
            @download="downloadFile"
            @copy="promptCopy"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useNotifications } from '../composables/useNotifications'
import api from '../services/api'
import FolderTreeComponent from './file-manager/FolderTreeComponent.vue'
import DirectoryDetailsComponent from './file-manager/DirectoryDetailsComponent.vue'

// Notifications
const { success, error, warning, confirm, prompt } = useNotifications()

// Reactive state
const currentPath = ref('')
const dirs = ref([])
const files = ref([])
const selectedFile = ref(null)
const fileProps = ref(null)
const errorMsg = ref('')
const folderStructure = ref([])
const treeReady = ref(false)
const uploadProgress = ref({
  isUploading: false,
  percentage: 0,
  loaded: 0,
  total: 0,
  fileName: ''
})

// Helper functions
function joinPath(...parts) {
  return parts.filter(Boolean).join('/').replace(/\/+/g, '/')
}

// Helper function to format bytes
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// API functions
async function fetchFiles() {
  errorMsg.value = ''
  try {
    const response = await api.get(`/file/list_files?path=${encodeURIComponent(currentPath.value)}`)
    files.value = response.data.files
  } catch (err) {
    errorMsg.value = 'Failed to list files'
    console.error('Error fetching files:', err)
  }
}

async function fetchSubdirectories() {
  errorMsg.value = ''
  try {
    const response = await api.get(`/file/list_dirs?path=${encodeURIComponent(currentPath.value)}`)
    dirs.value = Array.isArray(response.data) ? response.data.map(dir => ({
      name: dir.name,
      path: dir.path,
      children: dir.children || []
    })) : []
  } catch (err) {
    errorMsg.value = 'Failed to list subdirectories'
    dirs.value = []
    console.error('Error fetching subdirectories:', err)
  }
}

async function fetchAllDirs() {
  errorMsg.value = ''
  try {
    const response = await api.get('/file/list_all_dirs')
    folderStructure.value = Array.isArray(response.data) ? response.data.map(dir => ({
      name: dir.name,
      path: dir.path,
      children: dir.children || []
    })) : []
    return true
  } catch (err) {
    errorMsg.value = 'Failed to fetch directory structure'
    console.error('Error fetching all directories:', err)
    return false
  }
}

async function fetchFileProps(fileName) {
  errorMsg.value = ''
  const path = joinPath(currentPath.value, fileName)
  try {
    const response = await api.get(`/file/properties?path=${encodeURIComponent(path)}`)
    fileProps.value = response.data
  } catch (err) {
    errorMsg.value = 'Failed to get file properties'
    fileProps.value = null
    console.error('Error fetching file properties:', err)
  }
}

// Actions
async function initFolderStructure() {
  treeReady.value = false
  const success = await fetchAllDirs()
  if (!success) {
    errorMsg.value = "Failed to load folders. Please try again."
  }
  treeReady.value = true
}

async function refresh() {
  const dirSuccess = await fetchAllDirs()
  await fetchFiles()
  await fetchSubdirectories()
  fileProps.value = null
  selectedFile.value = null
  return dirSuccess
}

function navigateToFolder(path) {
  fileProps.value = null
  selectedFile.value = null
  currentPath.value = path.replace(/\\/g, '/')
  fetchFiles()
  fetchSubdirectories()
}

function handleGoUp() {
  const currentPathString = currentPath.value || ""
  let parentPath = ""
  
  if (currentPathString) {
    const normalizedPath = currentPathString.replace(/\\/g, "/")
    const lastSlashIndex = normalizedPath.lastIndexOf("/")
    if (lastSlashIndex > 0) {
      parentPath = normalizedPath.substring(0, lastSlashIndex)
    }
  }
  
  navigateToFolder(parentPath)
}

async function selectFile(file) {
  selectedFile.value = file
  const fileName = typeof file === 'string' ? file : file.name
  await fetchFileProps(fileName)
}

async function promptRename(file) {
  const originalName = typeof file === "string" ? file : file.name
  const newName = await prompt(`Rename "${originalName}" to:`, 'Rename File/Directory', originalName)
  
  if (newName !== null && newName !== originalName) {
    await renameFileOrDir(file, newName)
  }
}

async function promptCopy(file) {
  const fileName = typeof file === "string" ? file : file.name
  const defaultCopyName = fileName.includes('.') 
    ? fileName.substring(0, fileName.lastIndexOf('.')) + ".copy" + fileName.substring(fileName.lastIndexOf('.'))
    : fileName + ".copy"

  const newName = await prompt(`Copy "${fileName}" to (filename):`, 'Copy File/Directory', defaultCopyName)

  if (newName !== null && newName !== fileName) {
    await copyFile(file, newName)
  }
}

async function promptCreateDirectory() {
  const dirName = await prompt('Enter the name of the new directory:', 'Create Directory', 'New Folder')

  if (dirName !== null && dirName.trim() !== "") {
    const success = await createDirectory(dirName.trim())
    if (success) {
      await initFolderStructure()
      await fetchSubdirectories()
      await fetchFiles()
    }
  }
}

async function renameFileOrDir(oldFile, newName) {
  const oldName = typeof oldFile === 'string' ? oldFile : oldFile.name
  errorMsg.value = ''
  const src = joinPath(currentPath.value, oldName)
  const dst = joinPath(currentPath.value, newName)
  
  try {
    await api.post('/file/rename', { src, dst })
    await refresh()
    success('File renamed successfully')
  } catch (err) {
    errorMsg.value = 'Failed to rename'
    error('Failed to rename file')
    console.error('Error renaming file:', err)
  }
}

async function copyFile(srcFile, dstName) {
  const srcName = typeof srcFile === 'string' ? srcFile : srcFile.name
  errorMsg.value = ''
  const src = joinPath(currentPath.value, srcName)
  const dst = joinPath(currentPath.value, dstName)
  
  try {
    await api.post('/file/copy', { src, dst })
    await refresh()
    success('File copied successfully')
  } catch (err) {
    errorMsg.value = 'Failed to copy'
    error('Failed to copy file')
    console.error('Error copying file:', err)
  }
}

async function createDirectory(dirName) {
  errorMsg.value = ''
  const path = joinPath(currentPath.value, dirName)
  
  try {
    await api.post('/file/create_dir', { path })
    await fetchSubdirectories()
    success('Directory created successfully')
    return true
  } catch (err) {
    errorMsg.value = 'Failed to create directory'
    error('Failed to create directory')
    console.error('Error creating directory:', err)
    return false
  }
}

async function handleDeleteFileOrDir(item) {
  const fileName = typeof item === 'string' ? item : item.name
  const confirmed = await confirm(`Delete "${fileName}"?`, 'Confirm Deletion')
  
  if (!confirmed) return
  
  errorMsg.value = ''
  const path = joinPath(currentPath.value, fileName)
  
  try {
    await api.post('/file/delete', { path })
    await fetchSubdirectories()
    await fetchFiles()
    fileProps.value = null
    selectedFile.value = null
    success('Item deleted successfully')
    
    if (typeof item === "string" || item.type === "directory") {
      await initFolderStructure()
    }
  } catch (err) {
    errorMsg.value = 'Failed to delete'
    error('Failed to delete item')
    console.error('Error deleting item:', err)
  }
}

async function downloadFile(file) {
  if (!file && !selectedFile.value) return
  
  const fileName = file 
    ? (typeof file === 'string' ? file : file.name)
    : selectedFile.value.name
  
  const path = joinPath(currentPath.value, fileName)
  
  try {
    await api.downloadFile(path, fileName)
  } catch (err) {
    error('Download failed: ' + (err.message || 'Unknown error'))
    console.error('Download error:', err)
  }
}

async function handleFileUpload(event) {
  const fileInput = event.target
  if (fileInput.files && fileInput.files.length > 0) {
    const file = fileInput.files[0]
    
    // Initialize progress
    uploadProgress.value = {
      isUploading: true,
      percentage: 0,
      loaded: 0,
      total: file.size,
      fileName: file.name
    }
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('path', currentPath.value)
      
      await api.post('/file/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          uploadProgress.value = {
            ...uploadProgress.value,
            percentage,
            loaded: progressEvent.loaded
          }
        }
      })
      
      // Upload successful - use persistent notification
      await fetchSubdirectories()
      await fetchFiles()
      fileInput.value = ''
      success(`File "${file.name}" uploaded successfully`, 5000, true)
      
    } catch (err) {
      // Upload failed - use persistent notification
      error(`Upload failed for "${file.name}": ` + (err.response?.data?.detail || err.message || 'Unknown error'), 8000, true)
      console.error('Upload error:', err)
    } finally {
      // Reset progress after a short delay to allow user to see completion
      setTimeout(() => {
        uploadProgress.value.isUploading = false
      }, 1000)
    }
  }
}
watch(currentPath, async () => {
  await fetchSubdirectories()
  await fetchFiles()
  fileProps.value = null
  selectedFile.value = null
})

// Event listener for models.json updates
const handleModelsJsonUpdate = async () => {
  await fetchFiles()
  // If a file is selected, refresh its properties to update registration status
  if (selectedFile.value) {
    const fileName = typeof selectedFile.value === 'string' ? selectedFile.value : selectedFile.value.name
    await fetchFileProps(fileName)
  }
}

// Lifecycle
onMounted(async () => {
  await initFolderStructure()
  await fetchFiles()
  await fetchSubdirectories()
  
  // Listen for models.json updates
  document.addEventListener('models-json-updated', handleModelsJsonUpdate)
})

onUnmounted(() => {
  // Cleanup event listener
  document.removeEventListener('models-json-updated', handleModelsJsonUpdate)
})
</script>

<style scoped>
/* Ajoutez ici vos styles personnalisés */
</style>