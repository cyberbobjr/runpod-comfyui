<template>
  <div v-if="dialogs.length > 0">
    <div
      v-for="dialog in dialogs"
      :key="dialog.id"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-black bg-opacity-50"
        @click="closeDialog(dialog.id, false)"
      ></div>
      
      <!-- Dialog -->
      <div class="relative bg-background-soft rounded-lg border border-border shadow-xl max-w-md w-full">
        <!-- Header -->
        <div class="p-6 border-b border-border">
          <h3 class="text-lg font-semibold text-text-light">{{ dialog.title }}</h3>
        </div>
        
        <!-- Content -->
        <div class="p-6">
          <p class="text-text-light mb-4">{{ dialog.message }}</p>
          
          <!-- Input for prompt type -->
          <input
            v-if="dialog.type === 'prompt'"
            v-model="dialog.inputValue"
            ref="promptInput"
            class="form-input"
            :placeholder="dialog.placeholder || ''"
            @keyup.enter="handleConfirm(dialog)"
          >
        </div>
        
        <!-- Actions -->
        <div class="p-6 border-t border-border flex justify-end space-x-3">
          <button
            @click="closeDialog(dialog.id, false)"
            class="btn btn-default"
          >
            {{ dialog.cancelText || 'Cancel' }}
          </button>
          <button
            @click="handleConfirm(dialog)"
            class="btn btn-primary"
          >
            {{ dialog.confirmText || 'OK' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { useNotifications } from '../composables/useNotifications'

const { dialogs, closeDialog } = useNotifications()
const promptInput = ref(null)

const handleConfirm = (dialog) => {
  if (dialog.type === 'prompt') {
    closeDialog(dialog.id, dialog.inputValue || dialog.defaultValue || '')
  } else {
    closeDialog(dialog.id, true)
  }
}

// Auto-focus on prompt input
const focusPromptInput = async () => {
  await nextTick()
  if (promptInput.value) {
    promptInput.value.focus()
  }
}

// Initialize input value for prompt dialogs
dialogs.value.forEach(dialog => {
  if (dialog.type === 'prompt') {
    dialog.inputValue = dialog.defaultValue || ''
    focusPromptInput()
  }
})
</script>
