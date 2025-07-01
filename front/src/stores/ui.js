import { defineStore } from 'pinia'

/**
 * Store Pinia for managing UI state and notifications
 * Handles application UI state, notifications, modals, and user preferences
 */
export const useUIStore = defineStore('ui', {
  // === STATE ===
  state: () => ({
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
     * @returns {Number} Number of unread notifications
     */
    unreadNotificationsCount: (state) => {
      return state.notifications.filter(n => !n.read).length
    },

    /**
     * Get recent notifications (last 10)
     * @returns {Array} Array of recent notifications
     */
    recentNotifications: (state) => {
      return state.notifications
        .slice()
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 10)
    },

    /**
     * Check if any modal is open
     * @returns {Boolean} True if any modal is open
     */
    hasOpenModal: (state) => {
      return state.activeModal !== null
    },

    /**
     * Check if any dialog is open
     * @returns {Boolean} True if any dialog is open
     */
    hasOpenDialog: (state) => {
      return state.dialogsOpen.size > 0
    },

    /**
     * Get current theme classes
     * @returns {String} CSS classes for current theme
     */
    themeClasses: (state) => {
      const classes = []
      if (state.darkMode) classes.push('dark')
      if (state.compactMode) classes.push('compact')
      return classes.join(' ')
    }
  },

  // === ACTIONS ===
  actions: {
    // === Navigation Actions ===

    /**
     * Set current view
     * @param {String} view - The view name to set as current
     */
    setCurrentView(view) {
      this.currentView = view
    },

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
    },

    /**
     * Set breadcrumbs
     * @param {Array} crumbs - Array of breadcrumb objects
     */
    setBreadcrumbs(crumbs) {
      this.breadcrumbs = crumbs
    },

    /**
     * Add breadcrumb
     * @param {Object} crumb - Breadcrumb object with name and path
     */
    addBreadcrumb(crumb) {
      this.breadcrumbs.push(crumb)
    },

    /**
     * Clear breadcrumbs
     */
    clearBreadcrumbs() {
      this.breadcrumbs = []
    },

    // === Theme and Preferences Actions ===

    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      localStorage.setItem('darkMode', this.darkMode.toString())
    },

    /**
     * Set dark mode
     * @param {Boolean} enabled - Whether to enable dark mode
     */
    setDarkMode(enabled) {
      this.darkMode = enabled
      localStorage.setItem('darkMode', enabled.toString())
    },

    /**
     * Toggle compact mode
     */
    toggleCompactMode() {
      this.compactMode = !this.compactMode
      localStorage.setItem('compactMode', this.compactMode.toString())
    },

    /**
     * Set language
     * @param {String} lang - Language code (e.g., 'en', 'fr')
     */
    setLanguage(lang) {
      this.language = lang
      localStorage.setItem('language', lang)
    },

    // === Notification Actions ===

    /**
     * Add notification
     * @param {Object} notification - Notification object
     * @returns {String} Notification ID
     */
    addNotification(notification) {
      const id = `notification_${Date.now()}_${this.notificationCounter++}`
      const newNotification = {
        id,
        timestamp: new Date().toISOString(),
        read: false,
        type: 'info',
        persistent: false,
        ...notification
      }
      
      this.notifications.unshift(newNotification)
      
      // Auto-remove non-persistent notifications after 5 seconds
      if (!newNotification.persistent) {
        setTimeout(() => {
          this.removeNotification(id)
        }, 5000)
      }
      
      return id
    },

    /**
     * Add success notification
     * @param {String} message - Success message
     * @param {Object} options - Additional options
     * @returns {String} Notification ID
     */
    addSuccessNotification(message, options = {}) {
      return this.addNotification({
        type: 'success',
        title: 'Success',
        message,
        ...options
      })
    },

    /**
     * Add error notification
     * @param {String} message - Error message
     * @param {Object} options - Additional options
     * @returns {String} Notification ID
     */
    addErrorNotification(message, options = {}) {
      return this.addNotification({
        type: 'error',
        title: 'Error',
        message,
        persistent: true,
        ...options
      })
    },

    /**
     * Add warning notification
     * @param {String} message - Warning message
     * @param {Object} options - Additional options
     * @returns {String} Notification ID
     */
    addWarningNotification(message, options = {}) {
      return this.addNotification({
        type: 'warning',
        title: 'Warning',
        message,
        ...options
      })
    },

    /**
     * Add info notification
     * @param {String} message - Info message
     * @param {Object} options - Additional options
     * @returns {String} Notification ID
     */
    addInfoNotification(message, options = {}) {
      return this.addNotification({
        type: 'info',
        title: 'Information',
        message,
        ...options
      })
    },

    /**
     * Remove notification
     * @param {String} id - Notification ID to remove
     */
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    /**
     * Mark notification as read
     * @param {String} id - Notification ID to mark as read
     */
    markNotificationAsRead(id) {
      const notification = this.notifications.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
    },

    /**
     * Mark all notifications as read
     */
    markAllNotificationsAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true
      })
    },

    /**
     * Clear all notifications
     */
    clearAllNotifications() {
      this.notifications = []
    },

    /**
     * Clear read notifications
     */
    clearReadNotifications() {
      this.notifications = this.notifications.filter(n => !n.read)
    },

    // === Modal and Dialog Actions ===

    /**
     * Open modal
     * @param {String} modalName - Name of the modal to open
     * @param {Object} data - Data to pass to the modal
     */
    openModal(modalName, data = null) {
      this.activeModal = modalName
      this.modalData = data
    },

    /**
     * Close modal
     */
    closeModal() {
      this.activeModal = null
      this.modalData = null
    },

    /**
     * Open dialog
     * @param {String} dialogName - Name of the dialog to open
     */
    openDialog(dialogName) {
      this.dialogsOpen.add(dialogName)
    },

    /**
     * Close dialog
     * @param {String} dialogName - Name of the dialog to close
     */
    closeDialog(dialogName) {
      this.dialogsOpen.delete(dialogName)
    },

    /**
     * Check if dialog is open
     * @param {String} dialogName - Name of the dialog to check
     * @returns {Boolean} True if dialog is open
     */
    isDialogOpen(dialogName) {
      return this.dialogsOpen.has(dialogName)
    },

    /**
     * Close all dialogs
     */
    closeAllDialogs() {
      this.dialogsOpen.clear()
    },

    // === Loading Actions ===

    /**
     * Set global loading state
     * @param {Boolean} loading - Whether app is loading
     * @param {String} message - Loading message
     */
    setGlobalLoading(loading, message = '') {
      this.globalLoading = loading
      this.loadingMessage = message
    },

    /**
     * Set progress
     * @param {Number} value - Progress value (0-100)
     * @param {Boolean} visible - Whether progress bar is visible
     */
    setProgress(value, visible = true) {
      this.progressValue = Math.max(0, Math.min(100, value))
      this.progressVisible = visible
    },

    /**
     * Hide progress bar
     */
    hideProgress() {
      this.progressVisible = false
      this.progressValue = 0
    },

    // === Error Handling Actions ===

    /**
     * Set global error
     * @param {Error|String} error - Error object or message
     * @param {Boolean} showDialog - Whether to show error dialog
     */
    setGlobalError(error, showDialog = true) {
      this.globalError = error
      if (showDialog) {
        this.errorDialogOpen = true
      }
    },

    /**
     * Clear global error
     */
    clearGlobalError() {
      this.globalError = null
      this.errorDialogOpen = false
    },

    /**
     * Handle API error
     * @param {Error} error - Error object from API
     */
    handleApiError(error) {
      const message = error.message || 'An unexpected error occurred'
      this.addErrorNotification(message)
      this.setGlobalError(error, false)
    },

    // === Utility Actions ===

    /**
     * Reset UI state to defaults
     */
    resetUIState() {
      this.sidebarOpen = true
      this.mobileMenuOpen = false
      this.currentView = 'dashboard'
      this.breadcrumbs = []
      this.notifications = []
      this.activeModal = null
      this.modalData = null
      this.dialogsOpen.clear()
      this.globalLoading = false
      this.loadingMessage = ''
      this.progressValue = 0
      this.progressVisible = false
      this.globalError = null
      this.errorDialogOpen = false
    },

    /**
     * Initialize UI store
     */
    initializeUI() {
      // Apply saved theme preferences
      if (this.darkMode) {
        document.documentElement.classList.add('dark')
      }
      
      // Set up any global UI event listeners
      window.addEventListener('beforeunload', () => {
        // Save any pending UI state before page unload
      })
    },

    /**
     * Update notification settings
     * @param {Object} settings - Notification settings object
     */
    updateNotificationSettings(settings) {
      // Store notification preferences
      localStorage.setItem('notificationSettings', JSON.stringify(settings))
    },

    /**
     * Get notification settings
     * @returns {Object} Notification settings object
     */
    getNotificationSettings() {
      const stored = localStorage.getItem('notificationSettings')
      return stored ? JSON.parse(stored) : {
        showSuccess: true,
        showError: true,
        showWarning: true,
        showInfo: true,
        autoHide: true,
        duration: 5000
      }
    }
  }
})
