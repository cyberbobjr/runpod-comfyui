<template>
  <div class="directory-details flex flex-col h-full">
    <!-- Toolbar -->
    <div class="toolbar-container flex items-center mb-4 p-4 bg-background-soft rounded-lg">
      <span class="mr-4">
        <strong>Current:</strong> 
        <code class="bg-background px-2 py-1 rounded text-sm">{{ currentPath || "/" }}</code>
      </span>
      <TooltipComponent text="Go to parent directory" :delay="300">
        <button
          class="px-3 py-1.5 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors mr-2"
          @click="$emit('go-up')"
          :disabled="!currentPath"
        >
          <FontAwesomeIcon icon="arrow-up" class="mr-1" /> Up
        </button>
      </TooltipComponent>
      <TooltipComponent text="Refresh current directory" :delay="300">
        <button
          class="px-3 py-1.5 text-sm bg-transparent border border-gray-500 text-gray-300 rounded hover:bg-gray-600 hover:text-white transition-colors mr-2"
          @click="$emit('refresh')"
        >
          <FontAwesomeIcon icon="sync" class="mr-1" /> Refresh
        </button>
      </TooltipComponent>
      <div class="ml-auto flex space-x-2">
        <TooltipComponent text="Upload files to this directory" :delay="300">
          <label for="fileUpload" class="inline-flex items-center px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors cursor-pointer">
            <FontAwesomeIcon icon="upload" class="mr-1" /> Upload
            <input
              type="file"
              id="fileUpload"
              class="hidden"
              @change="$emit('file-upload', $event)"
              multiple
              accept=".safetensors,.ckpt,.pt,.pth,.bin"
            />
          </label>
        </TooltipComponent>
        <TooltipComponent text="Create a new folder" :delay="300">
          <button
            class="px-3 py-1.5 text-sm bg-transparent border border-gray-500 text-gray-300 rounded hover:bg-gray-600 hover:text-white transition-colors"
            @click="$emit('create-directory')"
          >
            <FontAwesomeIcon icon="folder-plus" class="mr-1" /> New Folder
          </button>
        </TooltipComponent>
      </div>
    </div>

    <!-- Details Container -->
    <div class="details-container flex-1 overflow-auto space-y-6">
      <!-- Subdirectories Section -->
      <div class="subdirectory-list-container">
        <h5 class="text-lg font-medium mb-3">Subdirectories</h5>
        <div class="bg-background-soft rounded-lg border border-border overflow-hidden">
          <div
            v-for="dir in dirs"
            :key="dir.path"
            class="subdirectory-item flex justify-between items-center p-3 border-b border-border last:border-b-0 hover:bg-background transition-colors cursor-pointer group"
            :class="{ 'bg-primary/10': currentPath === dir.path }"
            @mouseover="hoveredItem = dir.path"
            @mouseleave="hoveredItem = null"
            @dblclick="$emit('navigate-to-folder', dir.path)"
          >
            <TooltipComponent text="Double-click to open this folder" :delay="500">
              <div class="flex items-center">
                <FontAwesomeIcon icon="folder" class="text-primary mr-3" />
                <span>{{ dir.name }}</span>
              </div>
            </TooltipComponent>
            <div
              class="subdirectory-actions flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity"
              :class="{ 'opacity-100': hoveredItem === dir.path || currentPath === dir.path }"
            >
              <TooltipComponent text="Open this folder" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-primary text-white rounded hover:bg-orange-600 transition-colors"
                  @click.stop="$emit('navigate-to-folder', dir.path)"
                >
                  <FontAwesomeIcon icon="folder-open" />
                </button>
              </TooltipComponent>
              <TooltipComponent text="Rename folder" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                  @click.stop="$emit('rename', dir)"
                >
                  <FontAwesomeIcon icon="pencil" />
                </button>
              </TooltipComponent>
              <TooltipComponent text="Delete folder" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  @click.stop="$emit('delete', dir)"
                >
                  <FontAwesomeIcon icon="trash" />
                </button>
              </TooltipComponent>
            </div>
          </div>
          <div
            v-if="!dirs || dirs.length === 0"
            class="text-text-muted text-center py-6"
          >
            <em>No subdirectories in this directory</em>
          </div>
        </div>
      </div>

      <!-- Files Section -->
      <div class="file-list-container">
        <h5 class="text-lg font-medium mb-3">Files</h5>
        <div class="bg-background-soft rounded-lg border border-border overflow-hidden">
          <div
            v-for="file in files"
            :key="file.name"
            class="file-item flex justify-between items-center p-3 border-b border-border last:border-b-0 hover:bg-background transition-colors cursor-pointer group"
            :class="{
              'bg-primary/10': selectedFile === file,
              'border-l-4 border-l-green-500': file.is_registered && !file.is_corrupted,
              'bg-red-50 border-l-4 border-l-red-500': file.is_corrupted,
            }"
            @click="$emit('select-file', file)"
          >
            <div class="flex items-center min-w-0 flex-1">
              <TooltipComponent text="Click to select and view file properties" :delay="500">
                <div class="flex items-center min-w-0">
                  <FontAwesomeIcon icon="file-lines" class="text-primary mr-3 flex-shrink-0" />
                  <span class="truncate">{{ file.name }}</span>
                </div>
              </TooltipComponent>
              <TooltipComponent 
                v-if="file.is_registered && !file.is_corrupted"
                text="This model is registered in models.json and ready to use"
                :delay="300"
              >
                <span
                  class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                >
                  <FontAwesomeIcon icon="check-circle" class="mr-1" />
                  Registered
                </span>
              </TooltipComponent>
              <TooltipComponent 
                v-if="file.is_corrupted"
                :text="`This file may be corrupted. Expected: ${formatSize(file.expected_size)}, Actual: ${formatSize(file.actual_size)}`"
                :delay="300"
              >
                <span
                  class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
                >
                  <FontAwesomeIcon icon="exclamation-triangle" class="mr-1" />
                  Corrupted
                </span>
              </TooltipComponent>
            </div>
            <div class="file-actions flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <TooltipComponent text="Download this file" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-primary text-white rounded hover:bg-orange-600 transition-colors"
                  @click.stop="$emit('download', file)"
                >
                  <FontAwesomeIcon icon="download" />
                </button>
              </TooltipComponent>
              <TooltipComponent text="Rename file" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                  @click.stop="$emit('rename', file)"
                >
                  <FontAwesomeIcon icon="pencil" />
                </button>
              </TooltipComponent>
              <TooltipComponent text="Make a copy of this file" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  @click.stop="$emit('copy', file)"
                >
                  <FontAwesomeIcon icon="copy" />
                </button>
              </TooltipComponent>
              <TooltipComponent text="Delete this file" :delay="300">
                <button
                  class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  @click.stop="$emit('delete', file)"
                >
                  <FontAwesomeIcon icon="trash" />
                </button>
              </TooltipComponent>
            </div>
          </div>
          <div v-if="files.length === 0" class="text-text-muted text-center py-6">
            <em>No files in this directory</em>
          </div>
        </div>
      </div>

      <!-- File Properties Card -->
      <div class="file-properties-container">
        <h5 class="text-lg font-medium mb-3 flex items-center">
          File Properties
          <TooltipComponent 
            v-if="selectedFile && selectedFile.is_registered && !selectedFile.is_corrupted"
            text="This file is referenced in models.json and is ready to use with ComfyUI"
            :delay="300"
          >
            <span
              class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
            >
              Registered Model
            </span>
          </TooltipComponent>
          <TooltipComponent 
            v-if="selectedFile && selectedFile.is_corrupted"
            :text="`This file may be corrupted. Expected: ${formatSize(selectedFile.expected_size)}, Actual: ${formatSize(selectedFile.actual_size)}`"
            :delay="300"
          >
            <span
              class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
            >
              Potentially Corrupted
            </span>
          </TooltipComponent>
        </h5>
        <FilePropertiesComponent
          v-if="fileProps"
          :file-props="fileProps"
          :selected-file="selectedFile"
        />
        <div v-else class="text-text-muted bg-background-soft p-6 rounded-lg text-center">
          Select a file to see its properties.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FilePropertiesComponent from './FilePropertiesComponent.vue'
import TooltipComponent from '../common/TooltipComponent.vue'
import { ref } from 'vue'

const props = defineProps({
  currentPath: String,
  files: Array,
  dirs: Array,
  selectedFile: Object,
  fileProps: Object,
})

const emit = defineEmits([
  'go-up',
  'refresh',
  'file-upload',
  'create-directory',
  'navigate-to-folder',
  'select-file',
  'rename',
  'delete',
  'download',
  'copy',
])

const hoveredItem = ref(null)
</script>
