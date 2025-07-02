/**
 * Version information for the frontend application.
 * This file is automatically updated during the build process.
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import api from '../services/api';

/**
 * Version information interface
 */
export interface VersionInfo {
  version: string;
  build: string;
  buildDate: string;
  description: string;
}

/**
 * API version response interface
 */
export interface ApiVersionResponse {
  version?: string;
  build?: string;
  buildDate?: string;
  description?: string;
  [key: string]: any;
}

// Static version information
export const version: string = "2.2.0";
export const build: string = "20250701-1551";
export const buildDate: string = "2025-07-01T15:51:22Z";
export const description: string = "Minor release with new features";

/**
 * Get the complete version information from the API.
 * 
 * **Description:** Fetches version information from the backend API with fallback to static values.
 * **Parameters:** None
 * **Returns:** Promise that resolves to version information object
 * 
 * @returns {Promise<VersionInfo>} Promise that resolves to version information
 */
export async function fetchVersionInfo(): Promise<VersionInfo> {
  try {
    const response = await api.get<ApiVersionResponse>('/auth/version');
    return {
      version: response.data?.version || version,
      build: response.data?.build || build,
      buildDate: response.data?.buildDate || buildDate,
      description: response.data?.description || description
    };
  } catch (error) {
    console.warn('Could not fetch version info from API:', error);
    return {
      version,
      build,
      buildDate,
      description
    };
  }
}

/**
 * Get a simple version string for display.
 * 
 * **Description:** Returns a formatted version string with 'v' prefix.
 * **Parameters:** None
 * **Returns:** Version string in format "v2.0.0"
 * 
 * @returns {string} Version string (e.g., "v2.0.0")
 */
export function getVersionString(): string {
  return `v${version}`;
}

/**
 * Get a detailed version string with build info.
 * 
 * **Description:** Returns a detailed version string including build information.
 * **Parameters:** None
 * **Returns:** Detailed version string in format "v2.0.0 (build 20250622-1430)"
 * 
 * @returns {string} Detailed version string (e.g., "v2.0.0 (build 20250622-1430)")
 */
export function getDetailedVersionString(): string {
  return `v${version} (build ${build})`;
}

/**
 * Get formatted build date.
 * 
 * **Description:** Returns the build date in a human-readable format.
 * **Parameters:** None
 * **Returns:** Formatted date string
 * 
 * @returns {string} Formatted build date
 */
export function getFormattedBuildDate(): string {
  return new Date(buildDate).toLocaleString();
}

/**
 * Check if the current version is newer than a given version.
 * 
 * **Description:** Compares the current version with a provided version string using semantic versioning.
 * **Parameters:**
 * - `compareVersion` (string): Version string to compare against (e.g., "2.1.0")
 * **Returns:** Boolean indicating if current version is newer
 * 
 * @param {string} compareVersion - Version string to compare against
 * @returns {boolean} True if current version is newer
 */
export function isVersionNewer(compareVersion: string): boolean {
  const parseVersion = (v: string): number[] => {
    return v.replace(/^v/, '').split('.').map(num => parseInt(num, 10));
  };

  const current = parseVersion(version);
  const compare = parseVersion(compareVersion);

  for (let i = 0; i < Math.max(current.length, compare.length); i++) {
    const currentPart = current[i] || 0;
    const comparePart = compare[i] || 0;

    if (currentPart > comparePart) return true;
    if (currentPart < comparePart) return false;
  }

  return false;
}

/**
 * Default export object with all version utilities
 */
export default {
  version,
  build,
  buildDate,
  description,
  fetchVersionInfo,
  getVersionString,
  getDetailedVersionString,
  getFormattedBuildDate,
  isVersionNewer
} as const;
