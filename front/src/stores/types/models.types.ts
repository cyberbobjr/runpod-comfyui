/**
 * Type definitions for the Models Store
 * Contains all interfaces and types used in the models management system
 */

/**
 * Model object structure
 * @TODO : clean deprecated fields and ensure consistency
 */
export interface Model {
  name?: string;
  type: string;
  description?: string;
  group: string;
  url: string;
  dest?: string;
  git?: string;
  tags?: string[];
  src?: string;
  hash?: string;
  size?: number;
  comments?: string;
  filename?: string;
  [key: string]: any;
  exists?: boolean;
}

/**
 * Download progress information returned by the /downloads API
 */
/**
 * Enum for download status values
 */
export enum DownloadStatus {
  DOWNLOADING = "downloading",
  DONE = "done",
  STOPPED = "stopped",
  ERROR = "error",
  IDLE = "idle"
}

/**
 * Download progress information returned by the /downloads API
 */
export interface DownloadProgress {
  model_id : string;
  /** Download progress percentage (0-100) */
  progress: number;
  /** Download status (see DownloadStatus enum) */
  status: DownloadStatus;
  /** Destination file or directory path */
  dest_path?: string | null;
  /** Timestamp when download started (seconds since epoch) */
  start_time?: number | null;
  /** Timestamp when download finished (seconds since epoch) */
  finished_time?: number | null;
  /** Error message if any */
  error?: string | null;
}

/**
 * API response for /downloads endpoint
 * Maps modelId to DownloadProgress object
 */
// API response for /downloads endpoint (Record of modelId to DownloadProgress)
export type DownloadsApiResponse = DownloadProgress[];

/**
 * Bundle installation tracking
 */
export interface BundleInstallation {
  bundleId: string;
  bundleName: string;
  profiles: string[];
  status:
    | "starting"
    | "installing"
    | "downloading"
    | "completed"
    | "error"
    | "cancelled";
  progress: number;
  currentStep: string;
  steps: string[];
  errors: string[];
  startTime: number;
  endTime?: number;
}


/**
 * Filter criteria for models
 */
export interface ModelFilterCriteria {
  type?: string;
  tags?: string[];
  group?: string;
  installed?: boolean;
}

/**
 * Model download entry for API calls
 */
export interface ModelEntry {
  model_id?: string;
  dest?: string;
  git?: string;
  url?: string;
  filename?: string;
}

/**
 * Store state interface
 */
export interface ModelsState {
  models: Model[];
  loading: boolean;
  error: string | null;
  selectedModels: Model[];
  downloadProgress: DownloadProgress[];
  _downloadPollingInterval: any | null;
}

/**
 * Configuration object for models API response
 */
export interface ModelsConfig {
  BASE_DIR: string;
  group_order: string[];
}

/**
 * Complete API response structure for /api/models/
 */
export interface CompleteModelsApiResponse {
  config: ModelsConfig;
  groups: Record<string, Model[]>;
}

/**
 * API Response types
 */
export interface ModelsApiResponse {
  groups: Record<string, any[]>;
}

export interface InstalledBundlesApiResponse {
  id: string;
  profile: string;
  [key: string]: any;
}

/**
 * Utility function to get model ID from Model object
 * @param model - Model object
 * @returns Model ID calculated from dest or git property
 */
export const getModelId = (model: Model): string => {
  return model.dest || model.git || "";
};
