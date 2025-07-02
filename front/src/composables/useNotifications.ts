/**
 * useNotifications Composable
 * 
 * A Vue 3 composable for managing notifications and dialogs with TypeScript support.
 * Provides functionality for showing success, error, warning, and info notifications,
 * as well as confirmation and prompt dialogs with persistent storage support.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

import { ref } from 'vue'

/**
 * Notification types
 */
export type NotificationType = 'success' | 'error' | 'warning' | 'info'

/**
 * Dialog types  
 */
export type DialogType = 'confirm' | 'prompt' | 'alert'

/**
 * Notification interface
 */
export interface Notification {
  id: number
  message: string
  type: NotificationType
  duration?: number
  persistent?: boolean
  timestamp?: number
}

/**
 * Dialog interface
 */
export interface Dialog {
  id: number
  type: DialogType
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  defaultValue?: string
  resolve: (result: any) => void
  reject: (reason?: any) => void
}

/**
 * Dialog options interface
 */
export interface DialogOptions {
  type: DialogType
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  defaultValue?: string
}

/**
 * Persistent notification interface for localStorage
 */
interface PersistentNotification {
  message: string
  type: NotificationType
  duration?: number
  timestamp: number
}

/**
 * useNotifications composable return type
 */
export interface UseNotificationsReturn {
  notifications: typeof notifications
  dialogs: typeof dialogs
  showNotification: (message: string, type?: NotificationType, duration?: number, persistent?: boolean) => void
  removeNotification: (id: number) => void
  showDialog: (options: DialogOptions) => Promise<any>
  closeDialog: (id: number, result?: any) => void
  success: (message: string, duration?: number, persistent?: boolean) => void
  error: (message: string, duration?: number, persistent?: boolean) => void
  warning: (message: string, duration?: number, persistent?: boolean) => void
  info: (message: string, duration?: number, persistent?: boolean) => void
  confirm: (message: string, title?: string) => Promise<boolean>
  prompt: (message: string, title?: string, defaultValue?: string) => Promise<string | null>
  loadPersistentNotifications: () => void
  clearPersistentNotifications: () => void
}

const notifications = ref<Notification[]>([])
const dialogs = ref<Dialog[]>([])

let notificationId = 0
let dialogId = 0

// localStorage key for persistent notifications
const PERSISTENT_NOTIFICATIONS_KEY = 'persistent_notifications'

/**
 * Load persistent notifications from localStorage on startup
 */
const loadPersistentNotifications = (): void => {
  try {
    const stored = localStorage.getItem(PERSISTENT_NOTIFICATIONS_KEY)
    if (stored) {
      const persistentNotifs: PersistentNotification[] = JSON.parse(stored)
      // Filter expired notifications (older than 30 seconds)
      const now = Date.now()
      const validNotifs = persistentNotifs.filter(notif => 
        (now - notif.timestamp) < 30000
      )
      
      // Add to current notifications
      validNotifs.forEach(notif => {
        notifications.value.push({
          ...notif,
          id: ++notificationId
        })
      })
      
      // Clean localStorage of expired notifications
      if (validNotifs.length !== persistentNotifs.length) {
        savePersistentNotifications(validNotifs)
      }
    }
  } catch (error) {
    console.error('Error loading persistent notifications:', error)
  }
}

/**
 * Save a persistent notification to localStorage
 * @param notification - The notification to save
 */
const savePersistentNotification = (notification: Omit<Notification, 'id'>): void => {
  try {
    const stored = localStorage.getItem(PERSISTENT_NOTIFICATIONS_KEY)
    let notifications: PersistentNotification[] = stored ? JSON.parse(stored) : []
    
    // Add new notification with timestamp
    notifications.push({
      message: notification.message,
      type: notification.type,
      duration: notification.duration,
      timestamp: Date.now()
    })
    
    // Keep only last 10 notifications to avoid localStorage bloat
    if (notifications.length > 10) {
      notifications = notifications.slice(-10)
    }
    
    localStorage.setItem(PERSISTENT_NOTIFICATIONS_KEY, JSON.stringify(notifications))
  } catch (error) {
    console.error('Error saving persistent notification:', error)
  }
}

/**
 * Save persistent notifications array to localStorage
 * @param notifications - Array of notifications to save
 */
const savePersistentNotifications = (notifications: PersistentNotification[]): void => {
  try {
    localStorage.setItem(PERSISTENT_NOTIFICATIONS_KEY, JSON.stringify(notifications))
  } catch (error) {
    console.error('Error saving persistent notifications:', error)
  }
}

/**
 * Clear all persistent notifications from localStorage
 */
const clearPersistentNotifications = (): void => {
  try {
    localStorage.removeItem(PERSISTENT_NOTIFICATIONS_KEY)
  } catch (error) {
    console.error('Error clearing persistent notifications:', error)
  }
}

/**
 * Main useNotifications composable function
 * @returns Object with notification and dialog management functions
 */
export const useNotifications = (): UseNotificationsReturn => {
  /**
   * Show a notification
   * @param message - The notification message
   * @param type - The notification type
   * @param duration - Duration in milliseconds (default: 5000)
   * @param persistent - Whether to save to localStorage
   */
  const showNotification = (
    message: string, 
    type: NotificationType = 'info', 
    duration: number = 5000, 
    persistent: boolean = false
  ): void => {
    const notification: Notification = {
      id: ++notificationId,
      message,
      type,
      duration,
      persistent,
      timestamp: Date.now()
    }
    
    notifications.value.push(notification)
    
    // Save to localStorage if persistent
    if (persistent) {
      savePersistentNotification(notification)
    }
    
    // Auto-remove after duration (unless duration is 0)
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, duration)
    }
  }
  
  /**
   * Remove a notification by ID
   * @param id - The notification ID to remove
   */
  const removeNotification = (id: number): void => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  /**
   * Show a dialog and return a promise
   * @param options - Dialog configuration options
   * @returns Promise that resolves with the dialog result
   */
  const showDialog = (options: DialogOptions): Promise<any> => {
    return new Promise((resolve, reject) => {
      const dialog: Dialog = {
        id: ++dialogId,
        ...options,
        resolve,
        reject
      }
      
      dialogs.value.push(dialog)
    })
  }
  
  /**
   * Close a dialog with optional result
   * @param id - The dialog ID to close
   * @param result - The result to resolve with
   */
  const closeDialog = (id: number, result?: any): void => {
    const index = dialogs.value.findIndex(d => d.id === id)
    if (index > -1) {
      const dialog = dialogs.value[index]
      dialog.resolve(result)
      dialogs.value.splice(index, 1)
    }
  }
  
  // Convenience methods with persistence support
  const success = (message: string, duration?: number, persistent: boolean = false): void => 
    showNotification(message, 'success', duration, persistent)
    
  const error = (message: string, duration?: number, persistent: boolean = false): void => 
    showNotification(message, 'error', duration, persistent)
    
  const warning = (message: string, duration?: number, persistent: boolean = false): void => 
    showNotification(message, 'warning', duration, persistent)
    
  const info = (message: string, duration?: number, persistent: boolean = false): void => 
    showNotification(message, 'info', duration, persistent)
  
  /**
   * Show a confirmation dialog
   * @param message - The confirmation message
   * @param title - The dialog title
   * @returns Promise that resolves to true if confirmed, false if cancelled
   */
  const confirm = (message: string, title: string = 'Confirmation'): Promise<boolean> => {
    return showDialog({
      type: 'confirm',
      title,
      message,
      confirmText: 'Confirm',
      cancelText: 'Cancel'
    })
  }
  
  /**
   * Show a prompt dialog
   * @param message - The prompt message
   * @param title - The dialog title  
   * @param defaultValue - The default input value
   * @returns Promise that resolves to the input value or null if cancelled
   */
  const prompt = (
    message: string, 
    title: string = 'Input Required', 
    defaultValue: string = ''
  ): Promise<string | null> => {
    return showDialog({
      type: 'prompt',
      title,
      message,
      defaultValue,
      confirmText: 'OK',
      cancelText: 'Cancel'
    })
  }
  
  return {
    notifications,
    dialogs,
    showNotification,
    removeNotification,
    showDialog,
    closeDialog,
    success,
    error,
    warning,
    info,
    confirm,
    prompt,
    loadPersistentNotifications,
    clearPersistentNotifications
  }
}
