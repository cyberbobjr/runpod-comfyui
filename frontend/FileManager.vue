<template>
  <div
    class="container-fluid"
    style="height: 100%; display: flex; flex-direction: column"
  >
    <!-- Card principale englobant toute la navigation -->
    <div
      class="card flex-grow-1"
      style="overflow: hidden; display: flex; flex-direction: column"
    >
      <!-- En-tête de la card avec titre mis en valeur -->
      <div class="card-header bg-primary">
        <h2 class="mb-0 text-white">File Manager</h2>
      </div>

      <div
        class="card-body d-flex flex-grow-1"
        style="overflow: hidden; flex-direction: column"
      >
        <!-- Message d'erreur -->
        <div v-if="errorMsg" class="alert alert-danger py-2 px-3">
          {{ errorMsg }}
        </div>

        <div
          class="row flex-grow-1 w-100"
          style="overflow: hidden; display: flex"
        >
          <!-- Tree view des dossiers -->
          <div
            class="col-md-4"
            style="display: flex; flex-direction: column; height: 100%"
          >
            <div
              class="border rounded p-2"
              style="
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
              "
            >
              <h5>
                Folders
                <button
                  class="btn btn-sm btn-outline-secondary float-end"
                  @click="initFolderStructure"
                >
                  Reload
                </button>
              </h5>
              <div v-if="!treeReady" class="text-center py-3">
                <small>Loading folders...</small>
              </div>
              <div v-else style="flex-grow: 1; overflow-y: auto; height: 0">
                <folder-tree
                  :folders="folderStructure"
                  :current-path="currentPath"
                  @select-folder="navigateToFolder"
                />
              </div>
            </div>
          </div>

          <!-- Liste des fichiers du dossier sélectionné -->
          <div class="col-md-8">
            <directory-details
              :current-path="currentPath"
              :files="files"
              :dirs="dirs"
              :selected-file="selectedFile"
              :file-props="fileProps"
              :format-size="formatSize"
              :format-date="formatDate"
              :shorten-url="shortenUrl"
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
  </div>
</template>

<script setup>
import {
  currentPath,
  files,
  selectedFile,
  fileProps,
  errorMsg,
  fetchFiles,
  refresh,
  selectFile,
  deleteFileOrDir,
  renameFileOrDir,
  copyFile,
  formatDate,
  formatSize,
  fetchAllDirs,
  folderStructure,
  expandedFolders,
  downloadFile,
  uploadFile, // Ajouter l'import manquant ici
  fetchSubdirectories,
  createDirectory,
  dirs,
} from "./FileManager.logic.js";
import { ref, watch, onMounted } from "vue";
import FolderTree from "./components/FolderTree.vue";
import DirectoryDetails from "./components/DirectoryDetails.vue";

// Flag to indicate if folder tree is ready
const treeReady = ref(false);
// Désactiver le mode debug pour la production
const debugInfo = ref(false);
// Control root folder expansion - set to true by default
const rootExpanded = ref(true);
const hoveredItem = ref(null); // Track the currently hovered item

// Navigate to a folder when clicked - simplified version
function navigateToFolder(path) {
  console.log("Navigating to folder:", path);

  // Masquer les propriétés de fichier lors de la navigation
  fileProps.value = null;
  selectedFile.value = null;

  // Éviter de réinitialiser le chemin si c'est le même
  if (currentPath.value !== path) {
    // Mettre à jour le chemin actuel
    currentPath.value = path;

    // Récupérer les fichiers pour le nouveau chemin
    fetchFiles();
    // Récupérer les sous-répertoires
    fetchSubdirectories();
  }
}

// Toggle root folder expansion - separate from regular folder toggling
function toggleRootFolder(event) {
  event.stopPropagation();
  rootExpanded.value = !rootExpanded.value;
  console.log("Root folder expanded:", rootExpanded.value);
}

// Initialize folder structure
async function initFolderStructure() {
  try {
    console.log("Initializing folder structure...");
    treeReady.value = false;
    rootExpanded.value = true; // Ensure root is expanded before loading

    const success = await fetchAllDirs();
    console.log(
      "Folder structure initialized:",
      success,
      folderStructure.value
    );

    if (!success) {
      errorMsg.value = "Failed to load folders. Please try again.";
    }

    treeReady.value = true;
    rootExpanded.value = true; // Make absolutely sure root is expanded after loading

    // Make sure we have proper console logging for debugging
    console.log("Initial expandedFolders state:", expandedFolders.value);
  } catch (error) {
    console.error("Error initializing folder structure:", error);
    errorMsg.value =
      "Failed to load folder structure: " + (error.message || "Unknown error");
    treeReady.value = true; // Set to true to hide loading indicator
  }
}

function promptRename(file) {
  const newName = window.prompt(
    "Rename to:",
    typeof file === "string" ? file : file.name
  );
  if (newName && newName !== (typeof file === "string" ? file : file.name)) {
    renameFileOrDir(file, newName);
  }
}

function promptCopy(file) {
  const fileName = typeof file === "string" ? file : file.name;
  const newName = window.prompt("Copy to (filename):", fileName + ".copy");
  if (newName && newName !== fileName) {
    copyFile(file, newName);
  }
}

// Wrapper function to ensure goUp works as expected
function handleGoUp() {
  console.log("Go up button clicked, current path:", currentPath.value);

  // Déterminer le chemin parent avant de naviguer vers le haut
  const currentPathString = currentPath.value || "";
  let parentPath = "";

  if (currentPathString) {
    // Normaliser les slashes pour cohérence
    const normalizedPath = currentPathString.replace(/\\/g, "/");
    const lastSlashIndex = normalizedPath.lastIndexOf("/");

    if (lastSlashIndex > 0) {
      // Si nous avons un chemin avec des sous-répertoires, prendre le chemin jusqu'au dernier slash
      parentPath = normalizedPath.substring(0, lastSlashIndex);
    }
  }

  console.log("Navigating up to parent path:", parentPath);

  // Utiliser la même fonction de navigation pour assurer la cohérence
  navigateToFolder(parentPath);
}

// Fonction pour raccourcir les URLs pour l'affichage
function shortenUrl(url) {
  if (!url) return "";

  try {
    // Créer un objet URL pour manipuler facilement l'URL
    const urlObj = new URL(url);

    // Raccourcir pour des sites spécifiques
    if (urlObj.hostname.includes("civitai.com")) {
      return "Civitai";
    } else if (urlObj.hostname.includes("huggingface.co")) {
      return "Hugging Face";
    } else if (urlObj.hostname.includes("github.com")) {
      return "GitHub";
    }

    // Pour les autres sites, afficher le nom de domaine
    return urlObj.hostname;
  } catch (e) {
    // Si l'URL n'est pas valide, retourner l'URL originale tronquée
    return url.length > 30 ? url.substring(0, 27) + "..." : url;
  }
}

async function promptCreateDirectory() {
  const dirName = window.prompt("Enter the name of the new directory:");
  if (dirName) {
    const success = await createDirectory(dirName);
    if (success) {
      // Rafraîchir la structure des dossiers pour afficher le nouveau répertoire
      await initFolderStructure();
      // Rafraîchir les fichiers et sous-répertoires du répertoire courant
      await fetchSubdirectories();
      await fetchFiles();
    }
  }
}

// Amélioration de la fonction de suppression pour rafraîchir la vue FolderTree
async function handleDeleteFileOrDir(item) {
  // Exécuter la suppression
  const success = await deleteFileOrDir(item);

  if (success) {
    // Si c'est un répertoire qu'on vient de supprimer
    if (typeof item === "string" || item.type === "directory") {
      console.log("Directory deleted, refreshing folder structure");
      // Rafraîchir la structure d'arborescence complète
      await initFolderStructure();
    }

    // Dans tous les cas, rafraîchir la vue du répertoire courant
    await fetchSubdirectories();
    await fetchFiles();
  }

  return success;
}

// Gérer l'upload de fichier
async function handleFileUpload(event) {
  const fileInput = event.target;
  if (fileInput.files && fileInput.files.length > 0) {
    const file = fileInput.files[0];
    try {
      await uploadFile(file);  // Cette fonction était bien utilisée mais pas importée
      // Après un upload réussi, rafraîchir la structure des dossiers si nécessaire
      await fetchSubdirectories();
      await fetchFiles();
      // Réinitialiser l'input pour permettre de charger le même fichier plusieurs fois
      fileInput.value = '';
    } catch (error) {
      console.error('Upload handling error:', error);
    }
  }
}

// Add a watch to clear file props when changing folders
watch(currentPath, async () => {
  console.log("[DEBUG] Current path changed:", currentPath.value);
  await fetchSubdirectories(); // Ensure subdirectories are fetched when the path changes
  await fetchFiles();
  console.log("[DEBUG] Updated dirs array after path change:", dirs.value); // Use dirs.value to access the reactive array
  // Clear file props when changing directory
  fileProps.value = null;
  selectedFile.value = null;
});

onMounted(async () => {
  console.log("[DEBUG] Component mounted, initializing...");
  rootExpanded.value = true; // Ensure root is expanded on mount
  await initFolderStructure();
  await fetchFiles();
  await fetchSubdirectories(); // Fetch subdirectories on mount
  console.log("[DEBUG] Initial dirs array:", dirs.value); // Use dirs.value to access the reactive array
});
</script>

<style scoped>
@import "./styles/FileManagerStyles.css";
</style>
