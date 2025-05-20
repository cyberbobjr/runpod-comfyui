import { ref, onMounted, reactive, computed } from 'vue';
import { apiFetch, handle401, token, useAppLogic } from './App.logic.js';

// État des données et UI
const jsonData = ref(null);
const jsonError = ref(null);
const isLoading = ref(false);
const isSubmitting = ref(false);
const saveMessage = ref('');
const saveSuccess = ref(false);
const currentGroup = ref('');
const showAddGroupModal = ref(false);
const showEditGroupModal = ref(false);
const showModelModal = ref(false);
const newGroupName = ref('');
const oldGroupName = ref('');

// État des formulaires
const formData = reactive({
  url: '',
  dest: '',
  git: '',
  type: '',
  tags: '',
  src: '',
  hash: '',
  size: null
});

// Form data that will be used with the ModelForm component
const modelFormData = ref({
  group: '',
  entry: {
    url: '',
    dest: '',
    git: '',
    type: '',
    tags: [],
    src: '',
    hash: '',
    size: null
  }
});

// État pour la base de répertoire
const baseDir = ref('');

// Fonctions utilitaires
const resetForm = () => {
  modelFormData.value = {
    group: '',
    entry: {
      url: '',
      dest: '',
      git: '',
      type: '',
      tags: [],
      src: '',
      hash: '',
      size: null
    }
  };

  // Also reset the reactive object for backward compatibility
  formData.url = '';
  formData.dest = '';
  formData.git = '';
  formData.type = '';
  formData.tags = '';
  formData.src = '';
  formData.hash = '';
  formData.size = null;
};

// Charger les données JSON du modèle
const fetchJsonData = async () => {
  if (!token.value) return;
  
  isLoading.value = true;
  jsonError.value = null;
  
  try {
    const res = await apiFetch('/jsonmodels/');
    if (handle401(res)) return;
    
    if (!res.ok) {
      throw new Error(`Error ${res.status}: ${res.statusText}`);
    }
    
    jsonData.value = await res.json();
    
    // Récupérer la config BASE_DIR
    if (jsonData.value && jsonData.value.config && jsonData.value.config.BASE_DIR) {
      baseDir.value = jsonData.value.config.BASE_DIR;
    }
  } catch (error) {
    console.error('Error fetching JSON data:', error);
    jsonError.value = `Failed to load models: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
};

// Sauvegarder la config BASE_DIR
const saveBaseDir = async () => {
  if (!token.value) return;
  
  try {
    const res = await apiFetch('/jsonmodels/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base_dir: baseDir.value })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      throw new Error(`Error ${res.status}: ${res.statusText}`);
    }
    
    showSaveMessage('Base directory updated successfully!', true);
  } catch (error) {
    console.error('Error saving base directory:', error);
    showSaveMessage(`Failed to update base directory: ${error.message}`, false);
  }
};

// Ajouter un groupe
const addGroup = async () => {
  if (!newGroupName.value.trim()) {
    showSaveMessage('Group name cannot be empty', false);
    return;
  }
  
  try {
    const res = await apiFetch('/jsonmodels/groups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group: newGroupName.value.trim() })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Group added successfully!', true);
    newGroupName.value = '';
    showAddGroupModal.value = false;
  } catch (error) {
    console.error('Error adding group:', error);
    showSaveMessage(`Failed to add group: ${error.message}`, false);
  }
};

// Mettre à jour le nom d'un groupe
const updateGroupName = async () => {
  if (!newGroupName.value.trim() || !oldGroupName.value) {
    showSaveMessage('Group names cannot be empty', false);
    return;
  }
  
  try {
    const res = await apiFetch('/jsonmodels/groups', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        old_group: oldGroupName.value, 
        new_group: newGroupName.value.trim() 
      })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Group renamed successfully!', true);
    newGroupName.value = '';
    oldGroupName.value = '';
    showEditGroupModal.value = false;
  } catch (error) {
    console.error('Error renaming group:', error);
    showSaveMessage(`Failed to rename group: ${error.message}`, false);
  }
};

// Supprimer un groupe
const deleteGroup = async (groupName) => {
  if (!confirm(`Are you sure you want to delete the group "${groupName}" and all its models?`)) {
    return;
  }
  
  try {
    const res = await apiFetch('/jsonmodels/groups', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group: groupName })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Group deleted successfully!', true);
  } catch (error) {
    console.error('Error deleting group:', error);
    showSaveMessage(`Failed to delete group: ${error.message}`, false);
  }
};

// Préparer le formulaire d'édition d'un groupe
const prepareEditGroup = (groupName) => {
  oldGroupName.value = groupName;
  newGroupName.value = groupName;
  showEditGroupModal.value = true;
};

// Fonctions pour gérer la modal de modèle
const openModelModal = (groupName = '', model = null) => {
  resetForm();
  
  if (groupName) {
    currentGroup.value = groupName;
    modelFormData.value.group = groupName;
  }
  
  if (model) {
    // Remplir le formulaire avec les données du modèle
    modelFormData.value.entry = {
      url: model.url || '',
      dest: model.dest || '',
      git: model.git || '',
      type: model.type || '',
      tags: Array.isArray(model.tags) ? model.tags : (model.tags ? [model.tags] : []),
      src: model.src || '',
      hash: model.hash || '',
      size: model.size || null
    };
    
    // Also fill the reactive object for backward compatibility
    formData.url = model.url || '';
    formData.dest = model.dest || '';
    formData.git = model.git || '';
    formData.type = model.type || '';
    formData.tags = Array.isArray(model.tags) ? model.tags.join(', ') : (model.tags || '');
    formData.src = model.src || '';
    formData.hash = model.hash || '';
    formData.size = model.size || null;
  }
  
  showModelModal.value = true;
};

const closeModelModal = () => {
  showModelModal.value = false;
  resetForm();
};

// Ajouter un modèle à un groupe
const addModelEntry = async () => {
  if (!modelFormData.value.group) {
    showSaveMessage('Please select a group first', false);
    return;
  }

  // Validation de base
  if (!modelFormData.value.entry.dest && !modelFormData.value.entry.git) {
    showSaveMessage('Either "dest" or "git" field is required', false);
    return;
  }
  
  if (!modelFormData.value.entry.url && !modelFormData.value.entry.git) {
    showSaveMessage('Either "url" or "git" field is required', false);
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const res = await apiFetch('/jsonmodels/entry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modelFormData.value)
    });
    
    if (handle401(res)) return;
    
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Model added successfully!', true);
    closeModelModal(); // Fermer la modal après ajout réussi
  } catch (error) {
    console.error('Error adding model:', error);
    showSaveMessage(`Failed to add model: ${error.message}`, false);
  } finally {
    isSubmitting.value = false;
  }
};

// Modifier un modèle
const editModelEntry = (groupName, model) => {
  openModelModal(groupName, model);
};

// Mettre à jour un modèle
const updateModelEntry = async () => {
  if (!currentGroup.value) {
    showSaveMessage('Group selection is required', false);
    return;
  }
  
  // Validation des champs obligatoires
  if (!formData.dest && !formData.git) {
    showSaveMessage('Either "dest" or "git" field is required', false);
    return;
  }
  
  // Préparer les données du modèle
  const modelEntry = {
    url: formData.url || undefined,
    dest: formData.dest || undefined,
    git: formData.git || undefined,
    type: formData.type || undefined,
    tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : [],
    src: formData.src || undefined,
    hash: formData.hash || undefined,
    size: formData.size ? parseInt(formData.size, 10) : undefined
    // La propriété headers a été supprimée
  };
  
  try {
    const res = await apiFetch('/jsonmodels/entry', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        group: currentGroup.value, 
        entry: modelEntry 
      })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Model updated successfully!', true);
    closeModelModal(); // Fermer la modal après mise à jour réussie
  } catch (error) {
    console.error('Error updating model:', error);
    showSaveMessage(`Failed to update model: ${error.message}`, false);
  }
};

// Supprimer un modèle
const deleteModelEntry = async (groupName, model) => {
  if (!confirm('Are you sure you want to delete this model entry?')) {
    return;
  }
  
  // Identifiant pour la recherche (dest ou git)
  const modelId = model.dest || model.git;
  if (!modelId) {
    showSaveMessage('Cannot identify the model to delete', false);
    return;
  }
  
  try {
    const res = await apiFetch('/jsonmodels/entry', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group: groupName,
        entry: { dest: model.dest, git: model.git }
      })
    });
    
    if (handle401(res)) return;
    
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || `Error ${res.status}`);
    }
    
    await fetchJsonData();
    showSaveMessage('Model deleted successfully!', true);
  } catch (error) {
    console.error('Error deleting model:', error);
    showSaveMessage(`Failed to delete model: ${error.message}`, false);
  }
};

// Afficher un message de succès/erreur temporaire
const showSaveMessage = (message, isSuccess) => {
  saveMessage.value = message;
  saveSuccess.value = isSuccess;
  
  setTimeout(() => {
    saveMessage.value = '';
  }, 3000);
};

// Vérifie si un modèle a le tag NSFW
const isNSFW = (model) => {
  const tags = model.tags;
  if (!tags) return false;
  if (Array.isArray(tags)) return tags.some(t => t.toLowerCase() === 'nsfw');
  return String(tags).toLowerCase().includes('nsfw');
};

// Exporter les fonctions et variables
export {
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
  editModelEntry,
  updateModelEntry,
  deleteModelEntry,
  resetForm,
  useAppLogic,
  isNSFW
};
