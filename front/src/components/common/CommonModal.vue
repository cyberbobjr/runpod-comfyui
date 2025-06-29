<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-background rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden mx-4">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 border-b border-border">
        <h3 class="text-lg font-semibold text-text-light">
          <slot name="title">Modal Title</slot>
        </h3>
        <button type="button" class="text-text-muted hover:text-text-light" @click="$emit('close')">
          <slot name="close-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </slot>
        </button>
      </div>
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[70vh]">
        <slot />
      </div>
      <!-- Footer -->
      <div class="flex justify-end space-x-3 p-4 border-t border-border bg-background-mute">
        <slot name="footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ### CommonModal
 * **Description:** A reusable modal dialog component with slots for title, content, and footer.
 * Provides a flexible modal overlay with customizable header, content area, and footer.
 * 
 * **Props:**
 * - `show` (Boolean, required): Controls the visibility of the modal
 * 
 * **Emits:**
 * - `close`: Emitted when the modal requests to be closed (via close button or overlay click)
 * 
 * **Slots:**
 * - `title`: Modal title text (default: "Modal Title")
 * - `close-icon`: Custom close icon (default: X icon)
 * - `default`: Main modal content
 * - `footer`: Footer content with action buttons (default: Close button)
 * 
 * **Features:**
 * - Overlay background with semi-transparent black
 * - Responsive design (max-width: 4xl, max-height: 80vh)
 * - Scrollable content area
 * - Automatic z-index layering (z-50)
 * - Keyboard and click handling for closing
 * 
 * **Usage Example:**
 * ```vue
 * <CommonModal :show="showModal" @close="showModal = false">
 *   <template #title>Bundle Details</template>
 *   <div>Modal content goes here</div>
 *   <template #footer>
 *     <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
 *     <button class="btn btn-primary" @click="save">Save</button>
 *   </template>
 * </CommonModal>
 * ```
 */
defineProps({
  show: {
    type: Boolean,
    required: true
  }
});

// Emit the close event when modal needs to be closed
defineEmits(['close']);
</script>
