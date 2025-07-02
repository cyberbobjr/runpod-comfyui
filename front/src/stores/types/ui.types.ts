/**
 * UI Store Types
 * 
 * Type definitions for the UI store, including all UI-related
 * interfaces and types used throughout the application.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

/**
 * Notification interface
 */
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  persistent?: boolean;
  action?: NotificationAction;
  icon?: string;
  duration?: number;
}

/**
 * Notification action interface
 */
export interface NotificationAction {
  label: string;
  callback: () => void;
  style?: 'primary' | 'secondary' | 'danger';
}

/**
 * Breadcrumb interface
 */
export interface Breadcrumb {
  label: string;
  route?: string;
  active?: boolean;
  icon?: string;
}

/**
 * Modal data interface
 */
export interface ModalData {
  title?: string;
  component?: string;
  props?: Record<string, any>;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  persistent?: boolean;
}

/**
 * Progress state interface
 */
export interface ProgressState {
  visible: boolean;
  value: number;
  message: string;
  indeterminate?: boolean;
}

/**
 * UI store state interface
 */
export interface UIStoreState {
  // Navigation and layout
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  currentView: string;
  breadcrumbs: Breadcrumb[];
  
  // Theme and preferences
  darkMode: boolean;
  language: string;
  compactMode: boolean;
  
  // Notifications
  notifications: Notification[];
  notificationCounter: number;
  
  // Modals and dialogs
  activeModal: string | null;
  modalData: ModalData | null;
  dialogsOpen: Set<string>;
  
  // Loading states
  globalLoading: boolean;
  loadingMessage: string;
  progressValue: number;
  progressVisible: boolean;
  
  // Error handling
  globalError: string | null;
  errorDialogOpen: boolean;
}

/**
 * Theme configuration interface
 */
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'auto';
  primaryColor?: string;
  accentColor?: string;
  fontSize?: 'sm' | 'md' | 'lg';
}

/**
 * User preferences interface
 */
export interface UserPreferences {
  theme: ThemeConfig;
  language: string;
  compactMode: boolean;
  animations: boolean;
  autoSave: boolean;
  notifications: {
    enabled: boolean;
    sound: boolean;
    desktop: boolean;
  };
}
