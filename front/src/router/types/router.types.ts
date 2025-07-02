/**
 * Router Types and Interfaces
 * 
 * Type definitions for router configuration, route meta properties,
 * and navigation utilities.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

import type { RouteLocationRaw, RouteRecordRaw } from 'vue-router';

/**
 * Extended route meta interface for application-specific properties
 */
export interface AppRouteMeta {
  /** Route requires authentication */
  requiresAuth?: boolean;
  /** Route is only for guest users (not authenticated) */
  guest?: boolean;
  /** Page title for document.title */
  title?: string;
  /** Page description for meta tags */
  description?: string;
  /** Custom layout to use for this route */
  layout?: string;
  /** Breadcrumb configuration */
  breadcrumb?: BreadcrumbItem[];
  /** Page-specific permissions */
  permissions?: string[];
  /** Hide this route from navigation menus */
  hidden?: boolean;
  /** Route category for grouping */
  category?: string;
  /** Custom icon for navigation */
  icon?: string;
}

/**
 * Breadcrumb item configuration
 */
export interface BreadcrumbItem {
  label: string;
  to?: RouteLocationRaw;
  disabled?: boolean;
}

/**
 * Navigation result with error handling
 */
export interface NavigationResult {
  success: boolean;
  error?: Error;
  route?: string;
}

/**
 * Route configuration with typed meta
 */
export interface AppRouteRecord {
  path: string;
  name?: string;
  component?: any;
  redirect?: RouteLocationRaw;
  meta?: AppRouteMeta;
  children?: AppRouteRecord[];
  [key: string]: any;
}

/**
 * Authentication state interface
 */
export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user?: UserInfo;
}

/**
 * User information for authentication
 */
export interface UserInfo {
  id: string;
  username: string;
  email?: string;
  roles: string[];
  permissions: string[];
}

/**
 * Navigation guard context
 */
export interface GuardContext {
  isAuthenticated: boolean;
  userRoles: string[];
  userPermissions: string[];
}

/**
 * Route names as string literal types for type safety
 */
export type RouteNames = 
  | 'install'
  | 'manage-bundles'
  | 'file-explorer'
  | 'json-editor'
  | 'settings'
  | 'login'
  | 'not-found';

/**
 * Tab names for the install page
 */
export type InstallTabNames = 'bundles' | 'models';

/**
 * Navigation options for programmatic navigation
 */
export interface NavigationOptions {
  replace?: boolean;
  preserveQuery?: boolean;
  preserveHash?: boolean;
}

/**
 * Route change event data
 */
export interface RouteChangeEvent {
  from: {
    name: string | null;
    path: string;
    meta: AppRouteMeta;
  };
  to: {
    name: string | null;
    path: string;
    meta: AppRouteMeta;
  };
  timestamp: Date;
}

/**
 * Navigation middleware function type
 */
export type NavigationMiddleware = (
  context: GuardContext,
  to: any,
  from: any
) => boolean | string | RouteLocationRaw;

/**
 * Router configuration options
 */
export interface RouterConfig {
  baseUrl?: string;
  enableLogging?: boolean;
  enableAnalytics?: boolean;
  defaultRedirect?: RouteLocationRaw;
}

/**
 * Type guards for route checking
 */
export const isAuthenticatedRoute = (meta?: AppRouteMeta): boolean => {
  return meta?.requiresAuth === true;
};

export const isGuestRoute = (meta?: AppRouteMeta): boolean => {
  return meta?.guest === true;
};

export const hasPermission = (meta?: AppRouteMeta, userPermissions: string[] = []): boolean => {
  if (!meta?.permissions || meta.permissions.length === 0) {
    return true;
  }
  return meta.permissions.some(permission => userPermissions.includes(permission));
};

/**
 * Route validation utilities
 */
export const validateRouteAccess = (
  meta: AppRouteMeta,
  context: GuardContext
): { allowed: boolean; reason?: string } => {
  // Check authentication requirement
  if (isAuthenticatedRoute(meta) && !context.isAuthenticated) {
    return { allowed: false, reason: 'authentication_required' };
  }
  
  // Check guest-only restriction
  if (isGuestRoute(meta) && context.isAuthenticated) {
    return { allowed: false, reason: 'authenticated_users_not_allowed' };
  }
  
  // Check permissions
  if (!hasPermission(meta, context.userPermissions)) {
    return { allowed: false, reason: 'insufficient_permissions' };
  }
  
  return { allowed: true };
};
