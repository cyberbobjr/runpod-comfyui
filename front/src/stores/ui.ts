/**
 * UI Store - TypeScript Version
 * 
 * Pinia store for managing UI state and notifications.
 * Handles application UI state, notifications, modals, and user preferences.
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { defineStore } from 'pinia';
import type {
  UIStoreState,
  Notification,
  NotificationAction,
  Breadcrumb,
  ModalData,
  UserPreferences,
  ThemeConfig
} from './types/ui.types';

export const useUIStore = defineStore('ui', {
  // === STATE ===
  state: (): UIStoreState => ({
    // Navigation and layout
    sidebarOpen: true,
    mobileMenuOpen: false,
    currentView: 'dashboard',
    breadcrumbs: [],
    
    // Theme and preferences
    darkMode: localStorage.getItem('darkMode') === 'true' || false,
    language: localStorage.getItem('language') || 'en',
    compactMode: localStorage.getItem('compactMode') === 'true' || false,
    
    // Notifications
    notifications: [],
    notificationCounter: 0,
    
    // Modals and dialogs
    activeModal: null,
    modalData: null,
    dialogsOpen: new Set(),
    
    // Loading states
    globalLoading: false,
    loadingMessage: '',
    progressValue: 0,
    progressVisible: false,
    
    // Error handling
    globalError: null,
    errorDialogOpen: false
  }),

  // === GETTERS ===
  getters: {
    /**
     * Get unread notifications count
     * 
     * **Description:** Returns the number of unread notifications.
     * **Returns:** Number of unread notifications
     */
    unreadNotificationsCount(): number {
      return this.notifications.filter((n: Notification) => !n.read).length;
    },

    /**
     * Get recent notifications (last 10)
     * 
     * **Description:** Returns the 10 most recent notifications, sorted by timestamp.
     * **Returns:** Array of recent notifications
     */
    recentNotifications(): Notification[] {
      return this.notifications
        .slice()
        .sort((a: Notification, b: Notification) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )
        .slice(0, 10);
    },

    /**
     * Check if any modal is open
     * 
     * **Description:** Returns true if any modal is currently open.
     * **Returns:** True if any modal is open
     */
    hasOpenModal(): boolean {
      return this.activeModal !== null;
    },

    /**
     * Check if any dialog is open
     * 
     * **Description:** Returns true if any dialog is currently open.
     * **Returns:** True if any dialog is open
     */
    hasOpenDialog(): boolean {
      return this.dialogsOpen.size > 0;
    },

    /**
     * Get current theme classes
     * 
     * **Description:** Returns CSS classes for the current theme configuration.
     * **Returns:** CSS classes for current theme
     */
    themeClasses(): string {
      const classes: string[] = [];
      if (this.darkMode) classes.push('dark');
      if (this.compactMode) classes.push('compact');
      return classes.join(' ');
    }
  },

  // === ACTIONS ===
  actions: {
    // === Navigation Actions ===

    /**
     * Set current view
     * 
     * **Description:** Sets the current active view in the application.
     * **Parameters:**
     * - `view` (string): The view name to set as current
     * **Returns:** void
     */
    setCurrentView(view: string): void {
      this.currentView = view;
    },

    /**
     * Toggle sidebar
     * 
     * **Description:** Toggles the sidebar open/closed state.
     * **Parameters:** None
     * **Returns:** void
     */
    toggleSidebar(): void {
      this.sidebarOpen = !this.sidebarOpen;
    },

    /**
     * Toggle mobile menu
     * 
     * **Description:** Toggles the mobile menu open/closed state.
     * **Parameters:** None
     * **Returns:** void
     */
    toggleMobileMenu(): void {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },

    /**
     * Set breadcrumbs
     * 
     * **Description:** Sets the breadcrumb navigation trail.
     * **Parameters:**
     * - `breadcrumbs` (Breadcrumb[]): Array of breadcrumb items
     * **Returns:** void
     */
    setBreadcrumbs(breadcrumbs: Breadcrumb[]): void {
      this.breadcrumbs = breadcrumbs;
    },

    // === Theme Actions ===

    /**
     * Toggle dark mode
     * 
     * **Description:** Toggles dark mode on/off and persists the setting.
     * **Parameters:** None
     * **Returns:** void
     */
    toggleDarkMode(): void {
      this.darkMode = !this.darkMode;
      localStorage.setItem('darkMode', this.darkMode.toString());
    },

    /**
     * Set language
     * 
     * **Description:** Sets the application language and persists the setting.
     * **Parameters:**
     * - `language` (string): Language code to set
     * **Returns:** void
     */
    setLanguage(language: string): void {
      this.language = language;
      localStorage.setItem('language', language);
    },

    /**
     * Toggle compact mode
     * 
     * **Description:** Toggles compact UI mode on/off and persists the setting.
     * **Parameters:** None
     * **Returns:** void
     */
    toggleCompactMode(): void {
      this.compactMode = !this.compactMode;
      localStorage.setItem('compactMode', this.compactMode.toString());
    },

    // === Notification Actions ===

    /**
     * Add notification
     * 
     * **Description:** Adds a new notification to the notification list.
     * **Parameters:**
     * - `notification` (Omit<Notification, 'id' | 'timestamp'>): Notification data
     * **Returns:** The created notification ID
     */
    addNotification(notification: Omit<Notification, 'id' | 'timestamp'>): string {
      const id = `notification-${this.notificationCounter++}`;
      const newNotification: Notification = {
        ...notification,
        id,
        timestamp: new Date().toISOString(),
        read: false
      };
      this.notifications.push(newNotification);
      return id;
    },

    /**
     * Remove notification
     * 
     * **Description:** Removes a notification by its ID.
     * **Parameters:**
     * - `id` (string): Notification ID to remove
     * **Returns:** void
     */
    removeNotification(id: string): void {
      const index = this.notifications.findIndex((n: Notification) => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },

    /**
     * Mark notification as read
     * 
     * **Description:** Marks a notification as read.
     * **Parameters:**
     * - `id` (string): Notification ID to mark as read
     * **Returns:** void
     */
    markNotificationAsRead(id: string): void {
      const notification = this.notifications.find((n: Notification) => n.id === id);
      if (notification) {
        notification.read = true;
      }
    },

    /**
     * Clear all notifications
     * 
     * **Description:** Removes all notifications from the list.
     * **Parameters:** None
     * **Returns:** void
     */
    clearAllNotifications(): void {
      this.notifications = [];
    },

    // === Modal Actions ===

    /**
     * Open modal
     * 
     * **Description:** Opens a modal with the specified configuration.
     * **Parameters:**
     * - `modalName` (string): Name of the modal to open
     * - `data` (ModalData, optional): Modal configuration data
     * **Returns:** void
     */
    openModal(modalName: string, data?: ModalData): void {
      this.activeModal = modalName;
      this.modalData = data || null;
    },

    /**
     * Close modal
     * 
     * **Description:** Closes the currently active modal.
     * **Parameters:** None
     * **Returns:** void
     */
    closeModal(): void {
      this.activeModal = null;
      this.modalData = null;
    },

    /**
     * Open dialog
     * 
     * **Description:** Opens a dialog and adds it to the open dialogs set.
     * **Parameters:**
     * - `dialogId` (string): Unique identifier for the dialog
     * **Returns:** void
     */
    openDialog(dialogId: string): void {
      this.dialogsOpen.add(dialogId);
    },

    /**
     * Close dialog
     * 
     * **Description:** Closes a dialog and removes it from the open dialogs set.
     * **Parameters:**
     * - `dialogId` (string): Unique identifier for the dialog
     * **Returns:** void
     */
    closeDialog(dialogId: string): void {
      this.dialogsOpen.delete(dialogId);
    },

    // === Loading Actions ===

    /**
     * Set global loading
     * 
     * **Description:** Sets the global loading state and optional message.
     * **Parameters:**
     * - `loading` (boolean): Loading state
     * - `message` (string, optional): Loading message
     * **Returns:** void
     */
    setGlobalLoading(loading: boolean, message?: string): void {
      this.globalLoading = loading;
      this.loadingMessage = message || '';
    },

    /**
     * Set progress
     * 
     * **Description:** Sets the progress bar state and value.
     * **Parameters:**
     * - `visible` (boolean): Whether progress bar is visible
     * - `value` (number, optional): Progress value (0-100)
     * - `message` (string, optional): Progress message
     * **Returns:** void
     */
    setProgress(visible: boolean, value?: number, message?: string): void {
      this.progressVisible = visible;
      if (value !== undefined) this.progressValue = value;
      if (message !== undefined) this.loadingMessage = message;
    },

    // === Error Actions ===

    /**
     * Set global error
     * 
     * **Description:** Sets a global error message and optionally shows error dialog.
     * **Parameters:**
     * - `error` (string | null): Error message or null to clear
     * - `showDialog` (boolean, optional): Whether to show error dialog
     * **Returns:** void
     */
    setGlobalError(error: string | null, showDialog?: boolean): void {
      this.globalError = error;
      if (showDialog) {
        this.errorDialogOpen = true;
      }
    },

    /**
     * Clear global error
     * 
     * **Description:** Clears the global error and closes error dialog.
     * **Parameters:** None
     * **Returns:** void
     */
    clearGlobalError(): void {
      this.globalError = null;
      this.errorDialogOpen = false;
    },

    // === Initialization ===

    /**
     * Initialize UI
     * 
     * **Description:** Initializes the UI store with saved preferences.
     * **Parameters:** None
     * **Returns:** void
     */
    initializeUI(): void {
      // Load saved preferences from localStorage
      const savedDarkMode = localStorage.getItem('darkMode');
      if (savedDarkMode !== null) {
        this.darkMode = savedDarkMode === 'true';
      }

      const savedLanguage = localStorage.getItem('language');
      if (savedLanguage) {
        this.language = savedLanguage;
      }

      const savedCompactMode = localStorage.getItem('compactMode');
      if (savedCompactMode !== null) {
        this.compactMode = savedCompactMode === 'true';
      }
    },

    /**
     * Reset UI state
     * 
     * **Description:** Resets the UI store to its initial state.
     * **Parameters:** None
     * **Returns:** void
     */
    resetUIState(): void {
      this.sidebarOpen = true;
      this.mobileMenuOpen = false;
      this.currentView = 'dashboard';
      this.breadcrumbs = [];
      this.notifications = [];
      this.notificationCounter = 0;
      this.activeModal = null;
      this.modalData = null;
      this.dialogsOpen.clear();
      this.globalLoading = false;
      this.loadingMessage = '';
      this.progressValue = 0;
      this.progressVisible = false;
      this.globalError = null;
      this.errorDialogOpen = false;
    }
  }
});
