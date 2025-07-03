<template>
  <CommonCard>
    <template #header>
      <h3>
        <FontAwesomeIcon :icon="faFolderOpen" class="mr-2" />
        File Manager
      </h3>
    </template>
    <!-- Upload Progress Bar -->
    <div
      v-if="uploadProgress.isUploading"
      class="fixed top-0 left-0 right-0 z-50 bg-background border-b border-border shadow-lg"
    >
      <div class="px-4 py-3">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center">
            <FontAwesomeIcon :icon="faUpload" class="text-primary mr-2" />
            <span class="text-sm font-medium text-text-light">
              Uploading {{ uploadProgress.fileName }}...
            </span>
          </div>
          <span class="text-sm text-text-light"
            >{{ uploadProgress.percentage }}%</span
          >
        </div>
        <div class="w-full bg-background-soft rounded-full h-2">
          <div
            class="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
            :style="{ width: uploadProgress.percentage + '%' }"
          ></div>
        </div>
        <div class="mt-1 text-xs text-text-muted">
          {{ formatBytes(uploadProgress.loaded) }} /
          {{ formatBytes(uploadProgress.total) }}
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="errorMsg"
      class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mx-4 mt-4"
    >
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
              <FontAwesomeIcon :icon="faRefresh" class="mr-1" />
              Reload
            </button>
          </div>

          <div
            v-if="!treeReady"
            class="flex-1 flex items-center justify-center"
          >
            <div class="text-center">
              <div
                class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"
              ></div>
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
  </CommonCard>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useNotifications } from "@/composables/useNotifications";
import api from "../services/api";
import FolderTreeComponent from "@/components/file-manager/FolderTreeComponent.vue";
import CommonCard from "@/components/common/CommonCard.vue";
import DirectoryDetailsComponent from "@/components/file-manager/DirectoryDetailsComponent.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faFolderOpen, faUpload, faRefresh } from "@fortawesome/free-solid-svg-icons";
import type {
  FileItem,
  DirectoryItem,
  FileProperties,
  UploadProgress,
  FileUploadEvent,
} from "./types/views.types";

// Notifications
const { success, error, confirm, prompt } = useNotifications();

// Reactive state
const currentPath = ref<string>("");
const dirs = ref<DirectoryItem[]>([]);
const files = ref<FileItem[]>([]);
const selectedFile = ref<FileItem | null>(null);
const fileProps = ref<FileProperties | null>(null);
const errorMsg = ref<string>("");
const folderStructure = ref<DirectoryItem[]>([]);
const treeReady = ref<boolean>(false);
const uploadProgress = ref<UploadProgress>({
  isUploading: false,
  percentage: 0,
  loaded: 0,
  total: 0,
  fileName: "",
});

// Helper functions
/**
 * ### joinPath
 * **Description:** Joins multiple path parts into a single normalized path.
 * **Parameters:**
 * - `parts` (...string[]): Path parts to join.
 * **Returns:** A normalized path string.
 */
function joinPath(...parts: string[]): string {
  return parts.filter(Boolean).join("/").replace(/\/+/g, "/");
}

/**
 * ### formatBytes
 * **Description:** Formats byte size into human-readable format.
 * **Parameters:**
 * - `bytes` (number): Number of bytes to format.
 * **Returns:** Formatted size string with appropriate unit.
 */
function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// API functions
/**
 * ### fetchFiles
 * **Description:** Fetches the list of files in the current directory.
 * **Parameters:** None.
 * **Returns:** Promise<void>.
 */
async function fetchFiles(): Promise<void> {
  errorMsg.value = "";
  try {
    const response = await api.get(
      `/file/list_files?path=${encodeURIComponent(currentPath.value)}`
    );
    files.value = response.data.files;
  } catch (err) {
    errorMsg.value = "Failed to list files";
    console.error("Error fetching files:", err);
  }
}

/**
 * ### fetchSubdirectories
 * **Description:** Fetches the list of subdirectories in the current directory.
 * **Parameters:** None.
 * **Returns:** Promise<void>.
 */
async function fetchSubdirectories(): Promise<void> {
  errorMsg.value = "";
  try {
    const response = await api.get(
      `/file/list_dirs?path=${encodeURIComponent(currentPath.value)}`
    );
    dirs.value = Array.isArray(response.data)
      ? response.data.map((dir: any) => ({
          name: dir.name,
          path: dir.path,
          children: dir.children || [],
        }))
      : [];
  } catch (err) {
    errorMsg.value = "Failed to list subdirectories";
    dirs.value = [];
    console.error("Error fetching subdirectories:", err);
  }
}

/**
 * ### fetchAllDirs
 * **Description:** Fetches the complete directory structure for the folder tree.
 * **Parameters:** None.
 * **Returns:** Promise<boolean> indicating success or failure.
 */
async function fetchAllDirs(): Promise<boolean> {
  errorMsg.value = "";
  try {
    const response = await api.get("/file/list_all_dirs");
    folderStructure.value = Array.isArray(response.data)
      ? response.data.map((dir: any) => ({
          name: dir.name,
          path: dir.path,
          children: dir.children || [],
        }))
      : [];
    return true;
  } catch (err) {
    errorMsg.value = "Failed to fetch directory structure";
    console.error("Error fetching all directories:", err);
    return false;
  }
}

/**
 * ### fetchFileProps
 * **Description:** Fetches properties of a specific file.
 * **Parameters:**
 * - `fileName` (string): Name of the file to get properties for.
 * **Returns:** Promise<void>.
 */
async function fetchFileProps(fileName: string): Promise<void> {
  errorMsg.value = "";
  const path = joinPath(currentPath.value, fileName);
  try {
    const response = await api.get(
      `/file/properties?path=${encodeURIComponent(path)}`
    );
    fileProps.value = response.data;
  } catch (err) {
    errorMsg.value = "Failed to get file properties";
    fileProps.value = null;
    console.error("Error fetching file properties:", err);
  }
}

// Actions
/**
 * ### initFolderStructure
 * **Description:** Initializes the folder structure for the tree view.
 * **Parameters:** None.
 * **Returns:** Promise<void>.
 */
async function initFolderStructure(): Promise<void> {
  treeReady.value = false;
  const success = await fetchAllDirs();
  if (!success) {
    errorMsg.value = "Failed to load folders. Please try again.";
  }
  treeReady.value = true;
}

/**
 * ### refresh
 * **Description:** Refreshes all data (directories, files, and folder structure).
 * **Parameters:** None.
 * **Returns:** Promise<boolean> indicating success.
 */
async function refresh(): Promise<boolean> {
  const dirSuccess = await fetchAllDirs();
  await fetchFiles();
  await fetchSubdirectories();
  fileProps.value = null;
  selectedFile.value = null;
  return dirSuccess;
}

/**
 * ### navigateToFolder
 * **Description:** Navigates to a specific folder path.
 * **Parameters:**
 * - `path` (string): Path to navigate to.
 * **Returns:** void.
 */
function navigateToFolder(path: string): void {
  fileProps.value = null;
  selectedFile.value = null;
  currentPath.value = path.replace(/\\/g, "/");
  fetchFiles();
  fetchSubdirectories();
}

/**
 * ### handleGoUp
 * **Description:** Navigates to the parent directory.
 * **Parameters:** None.
 * **Returns:** void.
 */
function handleGoUp(): void {
  const currentPathString = currentPath.value || "";
  let parentPath = "";

  if (currentPathString) {
    const normalizedPath = currentPathString.replace(/\\/g, "/");
    const lastSlashIndex = normalizedPath.lastIndexOf("/");
    if (lastSlashIndex > 0) {
      parentPath = normalizedPath.substring(0, lastSlashIndex);
    }
  }

  navigateToFolder(parentPath);
}

/**
 * ### selectFile
 * **Description:** Selects a file and fetches its properties.
 * **Parameters:**
 * - `file` (FileItem): File to select.
 * **Returns:** Promise<void>.
 */
async function selectFile(file: FileItem): Promise<void> {
  selectedFile.value = file;
  const fileName = typeof file === "string" ? file : file.name;
  await fetchFileProps(fileName);
}

/**
 * ### promptRename
 * **Description:** Prompts user to rename a file or directory.
 * **Parameters:**
 * - `file` (FileItem): File or directory to rename.
 * **Returns:** Promise<void>.
 */
async function promptRename(file: FileItem): Promise<void> {
  const originalName = typeof file === "string" ? file : file.name;
  const newName = await prompt(
    `Rename "${originalName}" to:`,
    "Rename File/Directory",
    originalName
  );

  if (newName !== null && newName !== originalName) {
    await renameFileOrDir(file, newName);
  }
}

/**
 * ### promptCopy
 * **Description:** Prompts user to copy a file or directory.
 * **Parameters:**
 * - `file` (FileItem): File or directory to copy.
 * **Returns:** Promise<void>.
 */
async function promptCopy(file: FileItem): Promise<void> {
  const fileName = typeof file === "string" ? file : file.name;
  const defaultCopyName = fileName.includes(".")
    ? fileName.substring(0, fileName.lastIndexOf(".")) +
      ".copy" +
      fileName.substring(fileName.lastIndexOf("."))
    : fileName + ".copy";

  const newName = await prompt(
    `Copy "${fileName}" to (filename):`,
    "Copy File/Directory",
    defaultCopyName
  );

  if (newName !== null && newName !== fileName) {
    await copyFile(file, newName);
  }
}

/**
 * ### promptCreateDirectory
 * **Description:** Prompts user to create a new directory.
 * **Parameters:** None.
 * **Returns:** Promise<void>.
 */
async function promptCreateDirectory(): Promise<void> {
  const dirName = await prompt(
    "Enter the name of the new directory:",
    "Create Directory",
    "New Folder"
  );

  if (dirName !== null && dirName.trim() !== "") {
    const success = await createDirectory(dirName.trim());
    if (success) {
      await initFolderStructure();
      await fetchSubdirectories();
      await fetchFiles();
    }
  }
}

/**
 * ### renameFileOrDir
 * **Description:** Renames a file or directory.
 * **Parameters:**
 * - `oldFile` (FileItem): File or directory to rename.
 * - `newName` (string): New name for the file or directory.
 * **Returns:** Promise<void>.
 */
async function renameFileOrDir(
  oldFile: FileItem,
  newName: string
): Promise<void> {
  const oldName = typeof oldFile === "string" ? oldFile : oldFile.name;
  errorMsg.value = "";
  const src = joinPath(currentPath.value, oldName);
  const dst = joinPath(currentPath.value, newName);

  try {
    await api.post("/file/rename", { src, dst });
    await refresh();
    success("File renamed successfully");
  } catch (err) {
    errorMsg.value = "Failed to rename";
    error("Failed to rename file");
    console.error("Error renaming file:", err);
  }
}

/**
 * ### copyFile
 * **Description:** Copies a file or directory.
 * **Parameters:**
 * - `srcFile` (FileItem): Source file or directory to copy.
 * - `dstName` (string): Destination name for the copy.
 * **Returns:** Promise<void>.
 */
async function copyFile(srcFile: FileItem, dstName: string): Promise<void> {
  const srcName = typeof srcFile === "string" ? srcFile : srcFile.name;
  errorMsg.value = "";
  const src = joinPath(currentPath.value, srcName);
  const dst = joinPath(currentPath.value, dstName);

  try {
    await api.post("/file/copy", { src, dst });
    await refresh();
    success("File copied successfully");
  } catch (err) {
    errorMsg.value = "Failed to copy";
    error("Failed to copy file");
    console.error("Error copying file:", err);
  }
}

/**
 * ### createDirectory
 * **Description:** Creates a new directory.
 * **Parameters:**
 * - `dirName` (string): Name of the directory to create.
 * **Returns:** Promise<boolean> indicating success.
 */
async function createDirectory(dirName: string): Promise<boolean> {
  errorMsg.value = "";
  const path = joinPath(currentPath.value, dirName);

  try {
    await api.post("/file/create_dir", { path });
    await fetchSubdirectories();
    success("Directory created successfully");
    return true;
  } catch (err) {
    errorMsg.value = "Failed to create directory";
    error("Failed to create directory");
    console.error("Error creating directory:", err);
    return false;
  }
}

/**
 * ### handleDeleteFileOrDir
 * **Description:** Handles deletion of a file or directory with confirmation.
 * **Parameters:**
 * - `item` (FileItem): File or directory to delete.
 * **Returns:** Promise<void>.
 */
async function handleDeleteFileOrDir(item: FileItem): Promise<void> {
  const fileName = typeof item === "string" ? item : item.name;
  const confirmed = await confirm(`Delete "${fileName}"?`, "Confirm Deletion");

  if (!confirmed) return;

  errorMsg.value = "";
  const path = joinPath(currentPath.value, fileName);

  try {
    await api.post("/file/delete", { path });
    await fetchSubdirectories();
    await fetchFiles();
    fileProps.value = null;
    selectedFile.value = null;
    success("Item deleted successfully");

    if (typeof item === "string" || item.type === "directory") {
      await initFolderStructure();
    }
  } catch (err) {
    errorMsg.value = "Failed to delete";
    error("Failed to delete item");
    console.error("Error deleting item:", err);
  }
}

/**
 * ### downloadFile
 * **Description:** Downloads a file to the user's device.
 * **Parameters:**
 * - `file` (FileItem | null): File to download, uses selectedFile if not provided.
 * **Returns:** Promise<void>.
 */
async function downloadFile(file?: FileItem | null): Promise<void> {
  if (!file && !selectedFile.value) return;

  const fileName = file
    ? typeof file === "string"
      ? file
      : file.name
    : selectedFile.value!.name;

  const path = joinPath(currentPath.value, fileName);

  try {
    await api.downloadFile(path, fileName);
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : "Unknown error";
    error("Download failed: " + errorMessage);
    console.error("Download error:", err);
  }
}

/**
 * ### handleFileUpload
 * **Description:** Handles file upload with progress tracking.
 * **Parameters:**
 * - `event` (FileUploadEvent): File upload event containing the selected files.
 * **Returns:** Promise<void>.
 */
async function handleFileUpload(event: FileUploadEvent): Promise<void> {
  const fileInput = event.target;
  if (fileInput.files && fileInput.files.length > 0) {
    const file = fileInput.files[0];

    // Initialize progress
    uploadProgress.value = {
      isUploading: true,
      percentage: 0,
      loaded: 0,
      total: file.size,
      fileName: file.name,
    };

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("path", currentPath.value);

      await api.post("/file/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent: any) => {
          const total = progressEvent.total || file.size;
          const percentage = Math.round((progressEvent.loaded * 100) / total);
          uploadProgress.value = {
            ...uploadProgress.value,
            percentage,
            loaded: progressEvent.loaded,
          };
        },
      });

      // Upload successful - use persistent notification
      await fetchSubdirectories();
      await fetchFiles();
      fileInput.value = "";
      success(`File "${file.name}" uploaded successfully`, 5000, true);
    } catch (err) {
      // Upload failed - use persistent notification
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      const apiError = err as any;
      error(
        `Upload failed for "${file.name}": ` +
          (apiError.response?.data?.detail || errorMessage),
        8000,
        true
      );
      console.error("Upload error:", err);
    } finally {
      // Reset progress after a short delay to allow user to see completion
      setTimeout(() => {
        uploadProgress.value.isUploading = false;
      }, 1000);
    }
  }
}
// Watchers and Lifecycle
watch(currentPath, async (): Promise<void> => {
  await fetchSubdirectories();
  await fetchFiles();
  fileProps.value = null;
  selectedFile.value = null;
});

// Event listener for models.json updates
const handleModelsJsonUpdate = async (): Promise<void> => {
  await fetchFiles();
  // If a file is selected, refresh its properties to update registration status
  if (selectedFile.value) {
    const fileName =
      typeof selectedFile.value === "string"
        ? selectedFile.value
        : selectedFile.value.name;
    await fetchFileProps(fileName);
  }
};

// Lifecycle
onMounted(async (): Promise<void> => {
  await initFolderStructure();
  await fetchFiles();
  await fetchSubdirectories();

  // Listen for models.json updates
  document.addEventListener("models-json-updated", handleModelsJsonUpdate);
});

onUnmounted((): void => {
  // Cleanup event listener
  document.removeEventListener("models-json-updated", handleModelsJsonUpdate);
});
</script>

<style scoped>
/* Ajoutez ici vos styles personnalisés */
</style>
