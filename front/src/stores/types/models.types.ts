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
 * Download progress information
 */
export interface DownloadProgress {
  progress: number;
  status: "downloading" | "completed" | "stopped" | "error" | "cancelled";
  error?: string | null;
  startTime?: number;
  endTime?: number;
}

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
 * Model download tracking for UI display
 */
export interface ModelDownload {
  modelId: string;
  modelName: string;
  status: "downloading" | "completed" | "cancelled" | "error";
  progress: number;
  currentStep: string;
  startTime: number;
  errors: string[];
}

/**
 * Active installation item for UI display
 */
export interface ActiveInstallation {
  downloadId: string;
  bundleId: string;
  bundleName: string;
  profiles: string[];
  status: string;
  progress: number;
  currentStep: string;
  startTime: number;
  errors: string[];
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
  downloadProgress: Map<string, DownloadProgress>;
  _downloadPollingInterval: any | null;
  bundleInstallations: Map<string, BundleInstallation>;
  _bundlePollingInterval: any | null;
  modelDownloads: Map<string, ModelDownload>;
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

export interface DownloadsApiResponse {
  [modelId: string]: DownloadProgress;
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
  return model.dest || model.git || '';
};
