/**
 * Bundles Store Types
 *
 * Type definitions for the bundles store, including all bundle-related
 * interfaces and types used throughout the application.
 *
 * @author TypeScript Migration
 * @version 1.0.0
 */

import { Model } from "./models.types";

export interface BundleStatus {
  status: string;
  text: string;
  color: string;
}
/**
 * Bundle interface
 */
export interface Bundle {
  id: string;
  name: string;
  description?: string;
  version: string;
  author?: string;
  website?: string;
  workflows?: string[];
  hardware_profiles?: Record<string, HardwareProfile>;
  installDate?: string;
  updateDate?: string;
}

/**
 * Installed bundle interface
 */
/**
 * InstalledBundle interface
 *
 * Represents an installed bundle as returned by the /bundles/installed API route.
 * Each object contains the bundle metadata and installation details.
 */
export interface InstalledBundle {
  bundle_id: string;
  profile: string;
  installed_at: string;
  status: string;
  installed_models: string[];
  failed_models: string[];
}

/**
 * Hardware profile interface
 */
export interface HardwareProfile {
  name: string;
  description?: string;
  models: Model[];
}

/**
 * Install progress interface
 */
export interface InstallProgress {
  bundleId: string;
  status: "pending" | "downloading" | "installing" | "completed" | "failed";
  progress: number;
  message?: string;
  currentFile?: string;
  totalFiles?: number;
  completedFiles?: number;
  error?: string;
}

/**
 * Bundle installation options
 */
export interface BundleInstallOptions {
  profile?: string;
  overwrite?: boolean;
  skipExisting?: boolean;
  validateHash?: boolean;
}

/**
 * Bundle filter options
 */
export interface BundleFilterOptions {
  category?: string;
  tags?: string[];
  installed?: boolean;
  search?: string;
  sortBy?: "name" | "date" | "size" | "category";
  sortOrder?: "asc" | "desc";
}

/**
 * Bundle store state interface
 */
export interface BundlesStoreState {
  bundles: Bundle[];
  installedBundles: InstalledBundle[];
  loading: boolean;
  installedLoading: boolean;
  error: string | null;
  installedError: string | null;
  selectedBundles: Bundle[];
  installProgress: Record<string, InstallProgress>;
  bundleCategories: string[];
}

/**
 * Bundle API response types
 */
export interface BundleApiResponse {
  data: Bundle[];
  message?: string;
  total?: number;
}

export interface InstalledBundleApiResponse {
  data: InstalledBundle[];
  message?: string;
  total?: number;
}

/**
 * Bundle operation result
 */
export interface BundleOperationResult {
  success: boolean;
  message?: string;
  error?: string;
  bundleId?: string;
}
