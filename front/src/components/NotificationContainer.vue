<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <transition-group name="notification" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'max-w-sm w-full bg-background-soft border rounded-lg shadow-lg p-4 flex items-start space-x-3',
          notificationStyles[notification.type]
        ]"
      >
        <div class="flex-shrink-0">
          <FontAwesomeIcon 
            :icon="notificationIcons[notification.type]" 
            :class="iconStyles[notification.type]"
            class="w-5 h-5"
          />
        </div>
        <div class="flex-1 text-text-light">
          <p class="text-sm">{{ notification.message }}</p>
        </div>
        <button
          @click="removeNotification(notification.id)"
          class="flex-shrink-0 text-text-light-muted hover:text-text-light transition-colors"
        >
          <FontAwesomeIcon icon="times" class="w-4 h-4" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { useNotifications, type NotificationType } from '@/composables/useNotifications'

const { notifications, removeNotification } = useNotifications()

/**
 * Notification icon mapping by type
 */
const notificationIcons: Record<NotificationType, string> = {
  success: 'check-circle',
  error: 'exclamation-circle',
  warning: 'exclamation-triangle',
  info: 'info-circle'
}

/**
 * Notification border styles by type
 */
const notificationStyles: Record<NotificationType, string> = {
  success: 'border-green-500',
  error: 'border-red-500',
  warning: 'border-yellow-500',
  info: 'border-blue-500'
}

/**
 * Notification icon color styles by type
 */
const iconStyles: Record<NotificationType, string> = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500'
}
</script>

<style scoped>
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
