import { ref } from 'vue'
import { apiFetch, handle401, token } from './App.logic.js'
import { useConfirm } from './plugins/confirm-dialog'

const currentPath = ref('')
const dirs = ref([]); // Ensure this is initialized as an empty array
// Modification de la variable files pour stocker les objets au lieu de simples noms
const files = ref([])
const selectedFile = ref(null)
const fileProps = ref(null)
const errorMsg = ref('')
const refreshKey = ref(0)
const folderStructure = ref([]); // Ensure this is initialized as an empty array
const expandedFolders = ref({})

// Dialog handlers
const { confirm, alert } = useConfirm();

// Active le mode DEBUG
const DEBUG = true;

function joinPath(...parts) {
    return parts.filter(Boolean).join('/').replace(/\/+/g, '/')
}

async function fetchDirs() {
    errorMsg.value = ''
    const res = await apiFetch(`/file/list_dirs?path=${encodeURIComponent(currentPath.value)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to list directories'
        return
    }
    // Nouveau format : tableau d'objets {label, path, children}
    const data = await res.json()
    dirs.value = data
}

async function fetchDirsForPath(path) {
    // For recursive tree structure
    const res = await apiFetch(`/file/list_dirs?path=${encodeURIComponent(path)}`)
    if (!res.ok) return []
    // Expect "name" instead of "label"
    const data = await res.json()
    return data.map(dir => ({
        name: dir.name,
        path: dir.path,
        children: dir.children
    }))
}

async function fetchAllDirs() {
    errorMsg.value = '';
    try {
        console.log('Fetching all directories...');
        const res = await apiFetch('/file/list_all_dirs');
        if (handle401(res)) return false;
        if (!res.ok) {
            errorMsg.value = 'Failed to fetch directory structure: ' + (res.statusText || res.status);
            console.error('API Error:', res.status, res.statusText);
            return false;
        }

        const data = await res.json();
        console.log('Received folder structure:', data);
        folderStructure.value = Array.isArray(data) ? data.map(dir => ({
            name: dir.name,
            path: dir.path,
            children: dir.children || [] // Ensure children is always an array
        })) : []; // Fallback to an empty array if data is not valid

        // Initialize expansion state for all folders
        if (!Object.keys(expandedFolders.value).length) {
            preExpandFolders();
        }

        return true;
    } catch (error) {
        console.error('Error fetching directory structure:', error);
        errorMsg.value = 'Error loading folders: ' + (error.message || 'Unknown error');
        return false;
    }
}

// Helper function to pre-expand all folders
function preExpandFolders() {
    // Reset expansion state
    expandedFolders.value = {
        '': true  // Only set root path to expanded
    }; 
    
    // Instead of expanding all folders by default, we'll keep them collapsed
    // but we still need to traverse the structure to identify all folders
    function registerFoldersRecursive(folders) {
        if (!Array.isArray(folders)) return;
        
        for (const folder of folders) {
            if (folder && folder.path) {
                // Set all folders to collapsed (not adding them to expandedFolders)
                // except for root which is already set to true
                expandedFolders.value[folder.path] = false;
                
                if (Array.isArray(folder.children)) {
                    registerFoldersRecursive(folder.children);
                }
            }
        }
    }
    
    registerFoldersRecursive(folderStructure.value);
    console.log('Initialized folder states with root expanded:', Object.keys(expandedFolders.value).length, 'folders');
}

async function fetchFiles() {
    errorMsg.value = ''
    
    if (DEBUG) {
        console.log(`[DEBUG] Fetching files for path: ${currentPath.value}`);
    }
    
    const res = await apiFetch(`/file/list_files?path=${encodeURIComponent(currentPath.value)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to list files'
        return
    }
    
    const data = await res.json()
    files.value = data.files
    
    if (DEBUG) {
        console.log(`[DEBUG] Received ${files.value.length} files:`);
        console.log(`[DEBUG] Registered files: ${files.value.filter(f => f.is_registered).length}`);
        console.log(`[DEBUG] Sample of registered files:`, files.value.filter(f => f.is_registered).slice(0, 3));
    }
}

async function refresh() {
    // Save current expansion states
    const savedExpansionState = {...expandedFolders.value};
    
    // Fetch directory structure
    const dirSuccess = await fetchAllDirs();
    
    // Restore expansion states after refresh
    if (dirSuccess) {
        // Always ensure root is expanded
        expandedFolders.value[''] = true;
        
        // Restore any previously toggled states
        if (Object.keys(savedExpansionState).length > 0) {
            for (const path in savedExpansionState) {
                if (path !== '') { // Skip root as we've already set it
                    expandedFolders.value[path] = savedExpansionState[path];
                }
            }
        }
    }
    
    await fetchFiles();
    fileProps.value = null;
    selectedFile.value = null;
    refreshKey.value++;
    
    console.log('After refresh, expanded folders:', 
                Object.entries(expandedFolders.value).filter(([k,v]) => v === true).length);
    
    return dirSuccess
}

async function goToDir(dir) {
    currentPath.value = joinPath(currentPath.value, dir)
    await refresh()
}

async function goUp() {
    if (!currentPath.value) return
    
    console.log('Going up from path:', currentPath.value);
    
    // Normaliser le chemin pour gérer à la fois les slash et backslash
    const normalizedPath = currentPath.value.replace(/\\/g, '/');
    
    // Séparer le chemin actuel en segments
    const pathParts = normalizedPath.split('/').filter(Boolean);
    
    console.log('Path parts:', pathParts);
    
    if (pathParts.length > 0) {
        // Supprimer le dernier segment pour remonter d'un niveau
        pathParts.pop();
        currentPath.value = pathParts.join('/');
        
        console.log('Going up to:', currentPath.value);
    } else {
        // Si nous sommes déjà à la racine, ne rien faire
        currentPath.value = '';
        console.log('Already at root, setting empty path');
    }
    
    // Rafraîchir la liste des fichiers pour le nouveau répertoire
    await fetchFiles();
    
    // Effacer les propriétés du fichier sélectionné
    fileProps.value = null;
    selectedFile.value = null;
}

async function selectFile(file) {
    if (DEBUG) {
        console.log(`[DEBUG] Selecting file:`, file);
    }
    
    selectedFile.value = file
    const fileName = typeof file === 'string' ? file : file.name;
    await fetchFileProps(fileName)
}

async function fetchFileProps(fileName) {
    errorMsg.value = ''
    const path = joinPath(currentPath.value, fileName)
    
    if (DEBUG) {
        console.log(`[DEBUG] Fetching properties for file: ${path}`);
    }
    
    const res = await apiFetch(`/file/properties?path=${encodeURIComponent(path)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to get file properties'
        fileProps.value = null
        return
    }
    fileProps.value = await res.json()
    
    if (DEBUG) {
        console.log(`[DEBUG] File properties received:`, fileProps.value);
    }
}

async function deleteFileOrDir(file) {
    // Adaptation pour le nouvel objet file
    const fileName = typeof file === 'string' ? file : file.name;
    
    if (DEBUG) {
        console.log(`[DEBUG] Deleting file/dir: ${fileName}`);
    }
    
    errorMsg.value = '';
    const path = joinPath(currentPath.value, fileName);
    
    const confirmed = await confirm({
        title: 'Confirm Deletion',
        message: `Delete "${fileName}"?`,
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel'
    });
    
    if (!confirmed) return;
    
    const res = await apiFetch('/file/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
    });
    if (handle401(res)) return;
    if (!res.ok) {
        errorMsg.value = 'Failed to delete';
        return;
    }
    await fetchSubdirectories(); // Refresh the subdirectories after deletion
    await fetchFiles(); // Refresh the files in the current directory
    fileProps.value = null; // Clear file properties
    selectedFile.value = null; // Clear selected file
    console.log('[DEBUG] Directory refreshed after deletion.');
}

async function renameFileOrDir(oldFile, newName) {
    // Adaptation pour le nouvel objet file
    const oldName = typeof oldFile === 'string' ? oldFile : oldFile.name;
    
    if (DEBUG) {
        console.log(`[DEBUG] Renaming file/dir from ${oldName} to ${newName}`);
    }
    
    errorMsg.value = ''
    const src = joinPath(currentPath.value, oldName)
    const dst = joinPath(currentPath.value, newName)
    const res = await apiFetch('/file/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ src, dst })
    })
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to rename'
        return
    }
    await refresh()
}

async function copyFile(srcFile, dstName) {
    // Adaptation pour le nouvel objet file
    const srcName = typeof srcFile === 'string' ? srcFile : srcFile.name;
    
    if (DEBUG) {
        console.log(`[DEBUG] Copying file from ${srcName} to ${dstName}`);
    }
    
    errorMsg.value = ''
    const src = joinPath(currentPath.value, srcName)
    const dst = joinPath(currentPath.value, dstName)
    const res = await apiFetch('/file/copy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ src, dst })
    })
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to copy'
        return
    }
    await refresh()
}

function toggleFolder(path) {
    console.log('Toggling folder expansion for:', path);
    if (expandedFolders.value[path] === undefined) {
        expandedFolders.value[path] = true;
    } else {
        expandedFolders.value[path] = !expandedFolders.value[path];
    }
    console.log('New state for folder:', path, expandedFolders.value[path]);
}

function isFolderExpanded(path) {
    return expandedFolders.value[path] === true;
}

function formatDate(dateStr) {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleString()
}

function formatSize(size) {
    if (typeof size !== 'number') return size
    if (size >= 1e9) return (size / 1e9).toFixed(2) + ' GB'
    if (size >= 1e6) return (size / 1e6).toFixed(2) + ' MB'
    if (size >= 1e3) return (size / 1e3).toFixed(2) + ' KB'
    return size + ' B'
}

async function navigateToFolder(path) {
    // Clear the file properties when navigating to another folder
    fileProps.value = null;
    selectedFile.value = null;
    
    // Ensure consistent path format (using forward slashes)
    currentPath.value = path.replace(/\\/g, '/');
    console.log('Navigated to normalized path:', currentPath.value);
    
    await fetchFiles();
}

// Fonction pour télécharger un fichier (adaptée pour le nouvel objet file)
async function downloadFile(file) {
    if (!file && !selectedFile.value) return;
    
    // Déterminer le nom de fichier
    const fileName = file 
        ? (typeof file === 'string' ? file : file.name)
        : selectedFile.value.name;
    
    if (DEBUG) {
        console.log(`[DEBUG] Downloading file: ${fileName}`);
    }
    
    const path = joinPath(currentPath.value, fileName);
    const downloadUrl = `/api/file/download?path=${encodeURIComponent(path)}&token=${token.value}`;
    
    // Créer un lien temporaire et déclencher le téléchargement
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Fonction pour uploader un fichier
async function uploadFile(fileObj) {
    if (!fileObj) return;
    
    errorMsg.value = '';
    
    const formData = new FormData();
    formData.append('file', fileObj);
    formData.append('path', currentPath.value);
    
    try {
        const res = await apiFetch('/file/upload', {
            method: 'POST',
            body: formData,
            // Ne pas définir Content-Type, il sera automatiquement défini avec le bon boundary
            headers: {
                // Le token est ajouté automatiquement par apiFetch
            }
        });
        
        if (handle401(res)) return;
        
        if (!res.ok) {
            errorMsg.value = 'Failed to upload file';
            return;
        }
        
        await refresh();
        return await res.json();
    } catch (error) {
        console.error('Upload error:', error);
        errorMsg.value = `Upload failed: ${error.message || 'Unknown error'}`;
    }
}

// Fonction pour vérifier si un fichier est enregistré dans models.json
// function isRegisteredModel(filePath) {
//     if (!registeredModelPaths.value.length) return false;
    
//     // Normaliser le chemin du fichier
//     const normalizedPath = joinPath(currentPath.value, filePath).replace(/\\/g, '/');
    
//     // Vérifier si le chemin est dans la liste des modèles enregistrés
//     return registeredModelPaths.value.some(path => {
//         // Parfois la comparaison échoue à cause de ./ ou de / au début
//         return path === normalizedPath || 
//                path === './' + normalizedPath || 
//                './' + path === normalizedPath;
//     });
// }

// Fonction pour charger la liste des modèles enregistrés
// async function fetchRegisteredModels() {
//     try {
//         const res = await apiFetch('/file/models_info');
//         if (handle401(res)) return;
        
//         if (!res.ok) {
//             console.error('Failed to fetch models info:', res.statusText);
//             return;
//         }
        
//         const data = await res.json();
//         registeredModelPaths.value = data.paths || [];
//         console.log('Registered models paths loaded:', registeredModelPaths.value.length);
//     } catch (error) {
//         console.error('Error fetching models info:', error);
//     }
// }

async function fetchSubdirectories() {
    errorMsg.value = '';
    try {
        console.log(`[DEBUG] Fetching subdirectories for path: ${currentPath.value}`);
        const res = await apiFetch(`/file/list_dirs?path=${encodeURIComponent(currentPath.value)}`);
        if (handle401(res)) return;
        if (!res.ok) {
            errorMsg.value = 'Failed to list subdirectories';
            dirs.value = []; // Reset dirs to an empty array on failure
            console.error('[DEBUG] Failed to fetch subdirectories:', res.status, res.statusText);
            return;
        }
        const data = await res.json();
        console.log('[DEBUG] Subdirectories fetched:', data);
        dirs.value = Array.isArray(data) ? data.map(dir => ({
            name: dir.name,
            path: dir.path,
            children: dir.children || []
        })) : []; // Fallback to an empty array if data is invalid
        console.log('[DEBUG] Updated dirs array:', dirs.value);
    } catch (error) {
        console.error('[DEBUG] Error fetching subdirectories:', error);
        errorMsg.value = 'Error loading subdirectories: ' + (error.message || 'Unknown error');
        dirs.value = []; // Reset dirs to an empty array on error
    }
}

async function createDirectory(dirName) {
    errorMsg.value = '';
    const path = joinPath(currentPath.value, dirName);
    const res = await apiFetch('/file/create_dir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
    });
    if (handle401(res)) return;
    if (!res.ok) {
        errorMsg.value = 'Failed to create directory';
        return;
    }
    await fetchSubdirectories();
}

export {
    currentPath, dirs, files, selectedFile, fileProps, errorMsg, refreshKey,
    fetchDirs, fetchDirsForPath, fetchFiles, refresh, goToDir, goUp, selectFile,
    fetchFileProps, deleteFileOrDir, renameFileOrDir, copyFile,
    formatDate, formatSize, fetchAllDirs, folderStructure, 
    toggleFolder, isFolderExpanded, expandedFolders, navigateToFolder,
    downloadFile, uploadFile,
    fetchSubdirectories, createDirectory,
    confirm, alert
}
