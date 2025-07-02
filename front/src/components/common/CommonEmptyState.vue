<template>
  <div class="flex flex-col items-center py-10">
    <slot name="icon">
      <svg xmlns="http://www.w3.org/2000/svg" class="text-4xl text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
    </slot>
    <h3 class="text-lg font-semibold text-text-light">
      <slot name="title">No Data</slot>
    </h3>
    <p class="text-text-muted mt-1">
      <slot name="description">There is nothing to display here.</slot>
    </p>
    <div class="mt-4">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ### CommonEmptyState
 * **Description:** A component for displaying empty states when there is no data to show.
 * Provides a centered layout with icon, title, description, and optional action button
 * to guide users when content is unavailable or loading.
 * 
 * **Props:** None
 * 
 * **Slots:**
 * - `icon` (optional): Custom icon to display (default: clock icon)
 * - `title` (optional): Title text (default: "No Data")
 * - `description` (optional): Description text (default: "There is nothing to display here.")
 * - `action` (optional): Action button or element to help users take next steps
 * 
 * **Features:**
 * - Centered flex layout with proper spacing
 * - Responsive design with padding (py-10)
 * - Consistent typography hierarchy
 * - Default fallback content for all slots
 * - Theme-consistent colors (text-text-light, text-text-muted)
 * 
 * **Usage Example:**
 * ```vue
 * <CommonEmptyState>
 *   <template #icon>
 *     <FontAwesomeIcon :icon="faBoxOpen" class="text-4xl text-gray-500 mb-4" />
 *   </template>
 *   <template #title>No Bundles Found</template>
 *   <template #description>Upload a bundle file to get started with model management.</template>
 *   <template #action>
 *     <button class="btn btn-primary" @click="uploadBundle">
 *       <FontAwesomeIcon :icon="faUpload" class="mr-2" />
 *       Upload Bundle
 *     </button>
 *   </template>
 * </CommonEmptyState>
 * ```
 */

// This component has no props, only slots
</script>
