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
            v-model="(dialog as any).inputValue"
            ref="promptInput"
            class="form-input"
            :placeholder="(dialog as any).placeholder || ''"
            @keyup.enter="handleConfirm(dialog as DialogWithInput)"
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
            @click="handleConfirm(dialog as DialogWithInput)"
            class="btn btn-primary"
          >
            {{ dialog.confirmText || 'OK' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNotifications } from '@/composables/useNotifications';
import { nextTick, ref } from 'vue'

/**
 * DialogContainer Component
 * -----------------------------------------------------------------------------
 * Renders dialog/modal overlays for alerts, confirmations, and prompts.
 * Integrates with the useNotifications composable to display system dialogs.
 *
 * ## Features & Behavior
 * - Displays multiple dialogs in a stack (z-index layering)
 * - Supports three dialog types: alert, confirm, and prompt
 * - Auto-focuses on prompt input fields
 * - Backdrop click closes dialog with "cancel" response
 * - Enter key confirms prompt dialogs
 * - Responsive design with max-width constraints
 * - Uses project design system styling
 *
 * ## Dialog Types
 * - **alert**: Simple message with OK button
 * - **confirm**: Message with Cancel/OK buttons, returns boolean
 * - **prompt**: Message with input field, returns string value
 *
 * ## Integration
 * Uses the `useNotifications` composable which provides:
 * - `dialogs`: Reactive array of active dialogs
 * - `closeDialog(id, result)`: Function to close dialog with result
 *
 * ## Methods
 * ### handleConfirm
 * **Description:** Handles confirmation action for all dialog types.
 * **Parameters:**
 * - `dialog` (DialogWithInput): The dialog object to confirm.
 * **Returns:** void
 *
 * ### focusPromptInput
 * **Description:** Auto-focuses the prompt input field after rendering.
 * **Parameters:** None
 * **Returns:** Promise<void>
 */

// Define the base dialog interface
interface BaseDialog {
  id:  number;
  type: 'alert' | 'confirm' | 'prompt';
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  defaultValue?: string;
}

// Extend the base Dialog interface with component-specific properties
interface DialogWithInput extends BaseDialog {
  placeholder?: string;
  inputValue?: string;
}

const { dialogs, closeDialog } = useNotifications()
const promptInput = ref<HTMLInputElement>()

// Cast dialogs to extended type for template usage
const dialogsWithInput = dialogs as any; // Temporary casting to avoid template binding issues

/**
 * ### handleConfirm
 * **Description:** Handles confirmation action for all dialog types.
 * **Parameters:**
 * - `dialog` (DialogWithInput): The dialog object to confirm.
 */
const handleConfirm = (dialog: DialogWithInput): void => {
  if (dialog.type === 'prompt') {
    closeDialog(dialog.id, dialog.inputValue || dialog.defaultValue || '')
  } else {
    closeDialog(dialog.id, true)
  }
}

/**
 * ### focusPromptInput
 * **Description:** Auto-focuses the prompt input field after rendering.
 */
const focusPromptInput = async (): Promise<void> => {
  await nextTick()
  if (promptInput.value) {
    promptInput.value.focus()
  }
}

// Initialize input value for prompt dialogs
dialogs.value.forEach((dialog: BaseDialog) => {
  const dialogWithInput = dialog as DialogWithInput;
  if (dialogWithInput.type === 'prompt') {
    dialogWithInput.inputValue = dialogWithInput.defaultValue || ''
    focusPromptInput()
  }
})
</script>
