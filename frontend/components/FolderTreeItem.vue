<template>
  <div 
    class="folder-item d-flex align-items-center" 
    :class="{ 
      'selected-folder': isCurrentPathSelected,
      'has-children': hasChildren,
      'no-children': !hasChildren 
    }"
    :style="{ paddingLeft: `${level * 16}px` }"
    @click="handleSelect"
  >
    <span 
      class="expand-icon" 
      :class="{ 'with-children': hasChildren, 'no-children': !hasChildren }"
      @click.stop="handleToggle"
    >
      <i class="fa-solid" :class="[
        hasChildren 
          ? (isExpanded ? 'fa-folder-open text-warning' : 'fa-folder text-primary') 
          : 'fa-folder text-secondary'
      ]"></i>
    </span>
    <span :class="{ 'text-muted': !hasChildren }">{{ folder.name }}</span>
  </div>
  
  <div v-if="isExpanded && hasChildren" class="folder-children">
    <folder-tree-item
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
import { computed } from 'vue';

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
});

const emit = defineEmits(['select', 'toggle']);

// Normaliser le chemin du dossier pour la comparaison
const normalizedFolderPath = computed(() => props.folder.path.replace(/\\/g, '/'));

// Vérifier si le dossier est développé en utilisant le chemin normalisé
const isExpanded = computed(() => {
  // Normaliser tous les chemins pour la comparaison
  const normalizedPath = normalizedFolderPath.value;
  
  // Vérifier si le chemin normalisé est dans la liste des dossiers développés
  return props.expandedFolders.some(path => {
    const expandedPath = typeof path === 'string' ? path.replace(/\\/g, '/') : '';
    return expandedPath === normalizedPath;
  });
});

// Vérifier si le dossier a des enfants
const hasChildren = computed(() => {
  return props.folder.children && props.folder.children.length > 0;
});

// Calculer si ce dossier est sélectionné en normalisant les chemins pour la comparaison
const isCurrentPathSelected = computed(() => {
  if (!props.currentPath) return false;
  
  const normalizedCurrentPath = props.currentPath.replace(/\\/g, '/');
  const normalizedFolderPath = props.folder.path.replace(/\\/g, '/');
  return normalizedCurrentPath === normalizedFolderPath;
});

function handleSelect() {
  // Émettre l'événement de sélection
  emit('select', props.folder.path);
}

function handleToggle(event) {
  if (event) {
    event.stopPropagation();
  }
  // Si le dossier a des enfants, on peut le basculer
  if (hasChildren.value) {
    emit('toggle', props.folder.path);
  }
}
</script>

<style scoped>
.folder-item {
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
}

.folder-item:hover {
  background-color: rgba(90, 120, 154, 0.2);
}

.expand-icon {
  width: 25px;
  display: inline-block;
  cursor: pointer;
  margin-right: 5px;
  text-align: center;
  font-size: 1.1rem;
  line-height: 1;
}

.expand-icon.with-children {
  cursor: pointer;
}

.expand-icon.no-children {
  cursor: default;
  opacity: 0.7;
}

/* Style différent pour les dossiers avec/sans enfants */
.folder-item.has-children {
  font-weight: bold;
}

.folder-item.no-children {
  font-weight: normal;
}

.folder-children {
  margin-left: 0;
}

.selected-folder {
  background-color: rgba(33, 150, 243, 0.2);
  border: 1px solid rgba(33, 150, 243, 0.5);
}
</style>
