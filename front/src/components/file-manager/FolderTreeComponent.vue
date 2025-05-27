<template>
  <div class="folder-tree h-full overflow-y-auto">
    <!-- Root folder -->
    <div 
      class="folder-item flex items-center p-2 cursor-pointer rounded transition-colors"
      :class="{ 
        'bg-primary/10 border border-primary/20': !currentPath,
        'hover:bg-background-soft': currentPath
      }"
      @click="handleSelect('')"
    >
      <span 
        class="expand-icon w-6 text-center mr-2 cursor-pointer"
        @click.stop="rootExpanded = !rootExpanded"
      >
        <FontAwesomeIcon 
          :icon="rootExpanded ? 'folder-open' : 'folder'" 
          :class="rootExpanded ? 'text-yellow-500' : 'text-blue-500'"
        />
      </span>
      <span class="font-medium">/ (root)</span>
    </div>
    
    <!-- Root folder expanded content -->
    <div v-if="rootExpanded && folders.length > 0" class="ml-4">
      <FolderTreeItem
        v-for="folder in folders"
        :key="folder.path"
        :folder="folder"
        :level="1"
        :current-path="currentPath"
        :expanded-folders="expandedFolders"
        @select="handleSelect"
        @toggle="handleToggle"
      />
    </div>
    
    <!-- Empty state -->
    <div v-if="!folders || folders.length === 0" class="text-center py-4">
      <small class="text-text-muted">No folders found</small>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import FolderTreeItem from './FolderTreeItem.vue'

const props = defineProps({
  folders: {
    type: Array,
    default: () => []
  },
  currentPath: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['select-folder'])

const rootExpanded = ref(true)
const expandedFolders = ref(JSON.parse(localStorage.getItem('comfyui-expanded-folders') || '[]'))

function saveExpandedState() {
  localStorage.setItem('comfyui-expanded-folders', JSON.stringify(expandedFolders.value))
}

function expandParents(path) {
  if (!path) return
  
  const normalizedPath = path.replace(/\\/g, '/')
  const parts = normalizedPath.split('/').filter(Boolean)
  let currentPath = ''
  let modified = false
  
  for (const part of parts) {
    if (currentPath) {
      currentPath += '/' + part
    } else {
      currentPath = part
    }
    
    const alreadyExpanded = expandedFolders.value.some(p => 
      p.replace(/\\/g, '/') === currentPath
    )
    
    if (!alreadyExpanded) {
      expandedFolders.value.push(currentPath)
      modified = true
    }
  }
  
  if (modified) {
    saveExpandedState()
  }
}

function handleSelect(path) {
  const normalizedPath = path.replace(/\\/g, '/')
  expandParents(normalizedPath)
  emit('select-folder', path)
}

function handleToggle(path, forceExpand = false) {
  const normalizedPath = path.replace(/\\/g, '/')
  const index = expandedFolders.value.findIndex(p => 
    p.replace(/\\/g, '/') === normalizedPath
  )
  
  if (forceExpand && index === -1) {
    expandedFolders.value.push(normalizedPath)
    saveExpandedState()
  } else if (!forceExpand) {
    if (index === -1) {
      expandedFolders.value.push(normalizedPath)
      saveExpandedState()
    } else {
      expandedFolders.value.splice(index, 1)
      saveExpandedState()
    }
  }
}

watch(() => props.currentPath, (newPath) => {
  if (newPath === '') {
    rootExpanded.value = true
  } else if (newPath) {
    expandParents(newPath)
  }
}, { immediate: true })

onMounted(() => {
  if (props.currentPath) {
    expandParents(props.currentPath)
  }
})
</script>
