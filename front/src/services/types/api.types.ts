/**
 * API Types and Interfaces
 * 
 * Comprehensive type definitions for API responses and requests
 * used throughout the application.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
  success: boolean;
}

/**
 * API Error response structure
 */
export interface ApiErrorResponse {
  message: string;
  detail?: string;
  status: number;
  code?: string;
  errors?: Record<string, string[]>;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Paginated API response
 */
export interface PaginatedApiResponse<T = any> extends ApiResponse<T[]> {
  meta: PaginationMeta;
}

/**
 * File upload response
 */
export interface FileUploadResponse {
  filename: string;
  path: string;
  size: number;
  mimetype: string;
  uploadedAt: string;
}

/**
 * Authentication token response
 */
export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  user?: UserInfo;
}

/**
 * User information structure
 */
export interface UserInfo {
  id: string;
  username: string;
  email?: string;
  roles: string[];
  preferences?: Record<string, any>;
}

/**
 * Bundle API response types
 */
export interface BundleApiResponse {
  id: string;
  name: string;
  description?: string;
  version?: string;
  hardware_profiles?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * Model API response types
 */
export interface ModelApiResponse {
  groups: Record<string, ModelEntryApiResponse[]>;
}

export interface ModelEntryApiResponse {
  dest?: string;
  url?: string;
  git?: string;
  exists: boolean;
  size?: number;
  filename?: string;
  checksum?: string;
}

/**
 * Download progress API response
 */
export interface DownloadProgressApiResponse {
  id: string;
  progress: number;
  status: 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled';
  total_size?: number;
  downloaded_size?: number;
  error?: string;
  started_at: string;
  completed_at?: string;
}

/**
 * Bundle installation API response
 */
export interface BundleInstallationApiResponse {
  bundle_id: string;
  profile: string;
  status: 'pending' | 'installing' | 'completed' | 'failed';
  progress: number;
  installed_at?: string;
  error?: string;
}

/**
 * System status API response
 */
export interface SystemStatusApiResponse {
  status: 'healthy' | 'degraded' | 'down';
  version: string;
  uptime: number;
  disk_usage: {
    total: number;
    used: number;
    free: number;
    percentage: number;
  };
  memory_usage: {
    total: number;
    used: number;
    free: number;
    percentage: number;
  };
}

/**
 * Generic list response
 */
export type ListApiResponse<T> = T[];

/**
 * Generic success response
 */
export interface SuccessApiResponse {
  success: true;
  message?: string;
}

/**
 * Request configuration with common options
 */
export interface ApiRequestConfig {
  timeout?: number;
  headers?: Record<string, string>;
  params?: Record<string, any>;
  signal?: AbortSignal;
}

/**
 * File download configuration
 */
export interface FileDownloadConfig {
  path: string;
  filename: string;
  mimeType?: string;
}

/**
 * API method types for type-safe API calls
 */
export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Type guard for API error responses
 */
export function isApiError(response: any): response is ApiErrorResponse {
  return response && typeof response === 'object' && 'message' in response && 'status' in response;
}

/**
 * Type guard for successful API responses
 */
export function isApiSuccess<T>(response: any): response is ApiResponse<T> {
  return response && typeof response === 'object' && 'data' in response && 'success' in response;
}
