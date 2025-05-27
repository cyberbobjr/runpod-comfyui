import { ref } from 'vue'

const notifications = ref([])
const dialogs = ref([])

let notificationId = 0
let dialogId = 0

// Clé localStorage pour les notifications persistantes
const PERSISTENT_NOTIFICATIONS_KEY = 'persistent_notifications'

// Charger les notifications persistantes au démarrage
const loadPersistentNotifications = () => {
  try {
    const stored = localStorage.getItem(PERSISTENT_NOTIFICATIONS_KEY)
    if (stored) {
      const persistentNotifs = JSON.parse(stored)
      // Filtrer les notifications expirées (plus de 30 secondes)
      const now = Date.now()
      const validNotifs = persistentNotifs.filter(notif => 
        (now - notif.timestamp) < 30000
      )
      
      // Ajouter aux notifications actuelles
      validNotifs.forEach(notif => {
        notifications.value.push({
          ...notif,
          id: ++notificationId
        })
      })
      
      // Nettoyer le localStorage des notifications expirées
      if (validNotifs.length !== persistentNotifs.length) {
        savePersistentNotifications(validNotifs)
      }
    }
  } catch (error) {
    console.error('Error loading persistent notifications:', error)
  }
}

// Sauvegarder une notification persistante
const savePersistentNotification = (notification) => {
  try {
    const stored = localStorage.getItem(PERSISTENT_NOTIFICATIONS_KEY)
    let notifications = stored ? JSON.parse(stored) : []
    
    // Ajouter la nouvelle notification avec timestamp
    notifications.push({
      ...notification,
      timestamp: Date.now(),
      id: undefined // Retirer l'ID pour éviter les conflits
    })
    
    // Garder seulement les 10 dernières notifications
    if (notifications.length > 10) {
      notifications = notifications.slice(-10)
    }
    
    localStorage.setItem(PERSISTENT_NOTIFICATIONS_KEY, JSON.stringify(notifications))
  } catch (error) {
    console.error('Error saving persistent notification:', error)
  }
}

// Sauvegarder toutes les notifications persistantes
const savePersistentNotifications = (notifications) => {
  try {
    localStorage.setItem(PERSISTENT_NOTIFICATIONS_KEY, JSON.stringify(notifications))
  } catch (error) {
    console.error('Error saving persistent notifications:', error)
  }
}

// Nettoyer les notifications persistantes
const clearPersistentNotifications = () => {
  try {
    localStorage.removeItem(PERSISTENT_NOTIFICATIONS_KEY)
  } catch (error) {
    console.error('Error clearing persistent notifications:', error)
  }
}

export function useNotifications() {
  // Charger les notifications persistantes au premier appel
  if (notifications.value.length === 0) {
    loadPersistentNotifications()
  }

  // Notifications (remplace alert)
  const showNotification = (message, type = 'info', duration = 4000, persistent = false) => {
    const id = ++notificationId
    const notification = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      visible: true,
      persistent
    }
    
    notifications.value.push(notification)
    
    // Sauvegarder en persistant si demandé
    if (persistent) {
      savePersistentNotification(notification)
    }
    
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
    
    return id
  }
  
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  // Dialogues (remplace confirm et prompt)
  const showDialog = (options) => {
    return new Promise((resolve) => {
      const id = ++dialogId
      const dialog = {
        id,
        ...options,
        visible: true,
        resolve
      }
      
      dialogs.value.push(dialog)
    })
  }
  
  const closeDialog = (id, result = null) => {
    const index = dialogs.value.findIndex(d => d.id === id)
    if (index > -1) {
      const dialog = dialogs.value[index]
      dialog.resolve(result)
      dialogs.value.splice(index, 1)
    }
  }
  
  // Méthodes de convenance avec support de persistance
  const success = (message, duration, persistent = false) => showNotification(message, 'success', duration, persistent)
  const error = (message, duration, persistent = false) => showNotification(message, 'error', duration, persistent)
  const warning = (message, duration, persistent = false) => showNotification(message, 'warning', duration, persistent)
  const info = (message, duration, persistent = false) => showNotification(message, 'info', duration, persistent)
  
  const confirm = (message, title = 'Confirmation') => {
    return showDialog({
      type: 'confirm',
      title,
      message,
      confirmText: 'Confirm',
      cancelText: 'Cancel'
    })
  }
  
  const prompt = (message, title = 'Input Required', defaultValue = '') => {
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
