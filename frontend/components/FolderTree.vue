<template>
  <div class="folder-tree">
    <!-- Root folder -->
    <div 
      class="folder-item root-folder d-flex align-items-center" 
      :class="{ 
        'selected-folder': !currentPath,
        'has-children': folders && folders.length > 0
      }"
      @click="handleSelect('')"
    >
      <span 
        class="expand-icon" 
        :class="{ 'with-children': folders && folders.length > 0 }"
        @click.stop="rootExpanded = !rootExpanded"
      >
        <i class="fa-solid" :class="rootExpanded ? 'fa-folder-open text-warning' : 'fa-folder text-primary'"></i>
      </span>
      <span>/ (root)</span>
    </div>
    
    <!-- Root folder expanded content -->
    <div v-if="rootExpanded && folders.length > 0" class="root-children">
      <folder-tree-item
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
    <div v-if="!folders || folders.length === 0" class="text-center py-2">
      <small class="text-muted">No folders found</small>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import FolderTreeItem from './FolderTreeItem.vue';

const props = defineProps({
  folders: {
    type: Array,
    default: () => []
  },
  currentPath: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['select-folder']);

// Créons un état persistant pour les dossiers développés
const rootExpanded = ref(true);
// Utilisons un tableau local mais rendons-le persistant entre les rendus
const expandedFolders = ref(JSON.parse(localStorage.getItem('comfyui-expanded-folders') || '[]'));

// Fonction pour sauvegarder l'état des dossiers développés
function saveExpandedState() {
  localStorage.setItem('comfyui-expanded-folders', JSON.stringify(expandedFolders.value));
  console.log('Saved expanded folders state:', expandedFolders.value);
}

// Ouvre tous les dossiers parents d'un chemin donné
function expandParents(path) {
  if (!path) return;
  
  // Gérer les chemins qui utilisent des backslashes
  const normalizedPath = path.replace(/\\/g, '/');
  const parts = normalizedPath.split('/').filter(Boolean);
  let currentPath = '';
  
  // Gardons une trace des modifications pour éviter des sauvegardes multiples
  let modified = false;
  
  for (const part of parts) {
    if (currentPath) {
      currentPath += '/' + part;
    } else {
      currentPath = part;
    }
    
    // Vérifier si ce chemin est déjà dans la liste des dossiers développés
    const alreadyExpanded = expandedFolders.value.some(p => 
      p.replace(/\\/g, '/') === currentPath
    );
    
    if (!alreadyExpanded) {
      expandedFolders.value.push(currentPath);
      modified = true;
      console.log(`Path expanded: ${currentPath}`);
    }
  }
  
  // Sauvegarder l'état uniquement si des modifications ont été apportées
  if (modified) {
    saveExpandedState();
  }
  
  console.log('All expanded folders:', expandedFolders.value);
}

// Gère la sélection d'un dossier
function handleSelect(path) {
  // Normaliser le chemin pour assurer la cohérence
  const normalizedPath = path.replace(/\\/g, '/');
  console.log(`Selected folder: ${normalizedPath}`);
  
  // Étendre tous les dossiers parents du chemin sélectionné
  expandParents(normalizedPath);
  
  // Émettre l'événement avec le chemin sélectionné
  emit('select-folder', path);
}

// Gère l'ouverture/fermeture d'un dossier
function handleToggle(path, forceExpand = false) {
  // Normaliser le chemin pour assurer la cohérence
  const normalizedPath = path.replace(/\\/g, '/');
  
  // Chercher si ce chemin normalisé existe déjà dans la liste
  const index = expandedFolders.value.findIndex(p => 
    p.replace(/\\/g, '/') === normalizedPath
  );
  
  if (forceExpand && index === -1) {
    // Si on force l'expansion et que le dossier n'est pas déjà développé
    expandedFolders.value.push(normalizedPath);
    saveExpandedState();
    console.log(`Folder ${normalizedPath} force-expanded`);
  } else if (!forceExpand) {
    // Basculer normalement
    if (index === -1) {
      expandedFolders.value.push(normalizedPath);
      saveExpandedState();
      console.log(`Folder ${normalizedPath} expanded`);
    } else {
      expandedFolders.value.splice(index, 1);
      saveExpandedState();
      console.log(`Folder ${normalizedPath} collapsed`);
    }
  }
}

// Fonction pour trouver le dossier correspondant à un chemin
function findFolderByPath(path, foldersList) {
  if (!path) return null;
  
  // Normaliser le chemin pour la recherche
  const normalizedSearchPath = path.replace(/\\/g, '/');
  
  // Fonction récursive pour parcourir l'arbre
  function search(folders) {
    if (!folders || !Array.isArray(folders)) return null;
    
    for (const folder of folders) {
      // Normaliser le chemin du dossier courant
      const normalizedFolderPath = folder.path.replace(/\\/g, '/');
      
      // Vérifier si c'est le dossier que nous cherchons
      if (normalizedFolderPath === normalizedSearchPath) {
        return folder;
      }
      
      // Rechercher dans les enfants si nécessaire
      if (folder.children && folder.children.length > 0) {
        const found = search(folder.children);
        if (found) return found;
      }
    }
    return null;
  }
  
  return search(foldersList);
}

// Amélioration du watch pour réagir aux changements de chemin sans tout réinitialiser
watch(() => props.currentPath, (newPath, oldPath) => {
  console.log(`Path changed in FolderTree: ${oldPath} -> ${newPath}`);
  
  if (newPath === '') {
    // S'assurer que le dossier racine est développé
    rootExpanded.value = true;
  } else if (newPath) {
    // S'assurer que les parents du nouveau chemin sont développés
    expandParents(newPath);
  }
}, { immediate: true });

// Initialisation au montage - simplifiée pour éviter des réinitialisations
onMounted(() => {
  console.log('FolderTree mounted, current path:', props.currentPath);
  
  // Si un chemin courant est défini, développer ses parents
  if (props.currentPath) {
    expandParents(props.currentPath);
  }
});
</script>

<style scoped>
.folder-tree {
  overflow-y: auto;
  height: 100%;
}

.folder-item.root-folder {
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.folder-item.root-folder:hover {
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
  color: #df691a;
}

/* Style pour les dossiers avec/sans enfants */
.folder-item.has-children {
  font-weight: bold;
}

.selected-folder {
  background-color: rgba(33, 150, 243, 0.2);
  border: 1px solid rgba(33, 150, 243, 0.5);
}
</style>
