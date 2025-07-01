/**
 * Version information for the frontend application.
 * This file is automatically updated during the build process.
 */

export const version = "2.2.0";
export const build = "20250701-1551";
export const buildDate = "2025-07-01T15:51:22Z";
export const description = "Minor release with new features";

/**
 * Get the complete version information from the API.
 * @returns {Promise<Object>} Promise that resolves to version information
 */
export async function fetchVersionInfo() {
  try {
    const response = await fetch('/api/version');
    return await response.json();
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
 * @returns {string} Version string (e.g., "v2.0.0")
 */
export function getVersionString() {
  return `v${version}`;
}

/**
 * Get a detailed version string with build info.
 * @returns {string} Detailed version string (e.g., "v2.0.0 (build 20250622-1430)")
 */
export function getDetailedVersionString() {
  return `v${version} (build ${build})`;
}

export default {
  version,
  build,
  buildDate,
  description,
  fetchVersionInfo,
  getVersionString,
  getDetailedVersionString
};
