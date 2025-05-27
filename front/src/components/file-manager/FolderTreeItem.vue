<template>
  <div 
    class="folder-item flex items-center p-2 cursor-pointer rounded transition-colors"
    :class="{ 
      'bg-primary/10 border border-primary/20': isCurrentPathSelected,
      'hover:bg-background-soft': !isCurrentPathSelected,
      'font-medium': hasChildren,
      'font-normal': !hasChildren
    }"
    :style="{ paddingLeft: `${level * 16}px` }"
    @click="handleSelect"
  >
    <span 
      class="expand-icon w-6 text-center mr-2"
      :class="{ 
        'cursor-pointer': hasChildren, 
        'cursor-default opacity-50': !hasChildren 
      }"
      @click.stop="hasChildren ? handleToggle($event) : null"
    >
      <FontAwesomeIcon 
        :icon="getIconName" 
        :class="getIconColorClass"
      />
    </span>
    <span :class="{ 'text-text-muted': !hasChildren }">{{ folder.name }}</span>
  </div>
  
  <div v-if="isExpanded && hasChildren" class="folder-children">
    <FolderTreeItem
      v-for="child in folder.children"
      :key="child.path"
      :folder="child"
      :level="level + 1"
      :current-path="currentPath"
      :expanded-folders="expandedFolders"
      @select="$emit('select', $event)"
      @toggle="$emit('toggle', $event)"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  folder: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  currentPath: {
    type: String,
    default: ''
  },
  expandedFolders: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select', 'toggle'])

const normalizedFolderPath = computed(() => props.folder.path.replace(/\\/g, '/'))

const isExpanded = computed(() => {
  const normalizedPath = normalizedFolderPath.value
  return props.expandedFolders.some(path => {
    const expandedPath = typeof path === 'string' ? path.replace(/\\/g, '/') : ''
    return expandedPath === normalizedPath
  })
})

const hasChildren = computed(() => {
  return props.folder.children && props.folder.children.length > 0
})

const isCurrentPathSelected = computed(() => {
  if (!props.currentPath) return false
  const normalizedCurrentPath = props.currentPath.replace(/\\/g, '/')
  const normalizedFolderPath = props.folder.path.replace(/\\/g, '/')
  return normalizedCurrentPath === normalizedFolderPath
})

const getIconName = computed(() => {
  if (!hasChildren.value) {
    return 'folder'
  }
  
  if (isExpanded.value) {
    return 'folder-open'
  } else {
    return 'folder'
  }
})

const getIconColorClass = computed(() => {
  if (!hasChildren.value) {
    return 'text-gray-400'
  }
  
  if (isExpanded.value) {
    return 'text-yellow-500'
  } else {
    return 'text-blue-500'
  }
})

function handleSelect() {
  emit('select', props.folder.path)
}

function handleToggle(event) {
  if (event) {
    event.stopPropagation()
  }
  if (hasChildren.value) {
    emit('toggle', props.folder.path)
  }
}
</script>
