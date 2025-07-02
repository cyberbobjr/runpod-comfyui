/**
 * Views Types and Interfaces
 * 
 * Type definitions for all Vue views/pages in the application.
 * Contains interfaces for form data, authentication, and page-specific types.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

/**
 * Tab names for the InstallPage
 */
export type InstallTabType = 'bundles' | 'models';

/**
 * PlaceholderView component props
 */
export interface PlaceholderViewProps {
  /** The name of the feature that's coming soon */
  feature?: string;
}

/**
 * Login form data interface
 */
export interface LoginFormData {
  username: string;
  password: string;
}

/**
 * Login form validation errors
 */
export interface LoginFormErrors {
  username: string;
  password: string;
}

/**
 * Authentication credentials for login
 */
export interface AuthCredentials {
  username: string;
  password: string;
}

/**
 * User authentication response
 */
export interface AuthResponse {
  token: string;
  user: AuthUser;
  expires_in?: number;
  refresh_token?: string;
}

/**
 * Authenticated user information
 */
export interface AuthUser {
  id: string;
  username: string;
  email?: string;
  roles: string[];
  permissions: string[];
  last_login?: string;
  created_at?: string;
}

/**
 * Authentication error response
 */
export interface AuthError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

/**
 * Route query parameters for navigation
 */
export interface RouteQueryParams {
  tab?: InstallTabType;
  redirect?: string;
  [key: string]: string | undefined;
}

/**
 * Form validation result
 */
export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Loading states for different operations
 */
export interface LoadingStates {
  login: boolean;
  logout: boolean;
  refresh: boolean;
  submit: boolean;
}

/**
 * Page meta information
 */
export interface PageMeta {
  title: string;
  description?: string;
  keywords?: string[];
  requiresAuth?: boolean;
  breadcrumb?: BreadcrumbItem[];
}

/**
 * Breadcrumb navigation item
 */
export interface BreadcrumbItem {
  label: string;
  path?: string;
  active?: boolean;
}

/**
 * Tab configuration for pages with tabs
 */
export interface TabConfig {
  id: string;
  label: string;
  icon?: string;
  component?: any;
  disabled?: boolean;
  hidden?: boolean;
}

/**
 * Page layout configuration
 */
export interface PageLayout {
  sidebar?: boolean;
  header?: boolean;
  footer?: boolean;
  padding?: boolean;
  maxWidth?: string;
}

/**
 * Notification configuration
 */
export interface NotificationConfig {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  persistent?: boolean;
}

/**
 * Form field configuration
 */
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'password' | 'email' | 'number' | 'textarea' | 'select' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  validation?: FormFieldValidation;
  options?: FormFieldOption[];
}

/**
 * Form field validation rules
 */
export interface FormFieldValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

/**
 * Form field option for select/radio inputs
 */
export interface FormFieldOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

/**
 * Page component props interface
 */
export interface PageProps {
  title?: string;
  subtitle?: string;
  layout?: PageLayout;
  meta?: PageMeta;
}

/**
 * Error boundary information
 */
export interface ErrorInfo {
  message: string;
  stack?: string;
  component?: string;
  props?: Record<string, any>;
  timestamp: Date;
}

/**
 * Type guards for form validation
 */
export const isValidLoginForm = (form: Partial<LoginFormData>): form is LoginFormData => {
  return !!(form.username && form.password);
};

export const isAuthError = (error: any): error is AuthError => {
  return error && typeof error === 'object' && 'message' in error;
};

/**
 * Utility functions for form handling
 */
export const createEmptyLoginForm = (): LoginFormData => ({
  username: '',
  password: ''
});

export const createEmptyLoginErrors = (): LoginFormErrors => ({
  username: '',
  password: ''
});

/**
 * Validation utilities
 */
export const validateRequired = (value: string, fieldName: string): string => {
  return !value?.trim() ? `Please enter your ${fieldName}` : '';
};

export const validateEmail = (email: string): string => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return email && !emailRegex.test(email) ? 'Please enter a valid email address' : '';
};

export const validateMinLength = (value: string, minLength: number, fieldName: string): string => {
  return value && value.length < minLength 
    ? `${fieldName} must be at least ${minLength} characters long` 
    : '';
};
