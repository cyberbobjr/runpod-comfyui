<template>
  <div class="card bg-background shadow">
    <div v-if="title || $slots.header" class="border-b border-border px-4 py-3">
      <h3 v-if="title">{{ title }}</h3>
      <slot name="header" />
    </div>
    <div class="p-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="border-t border-border px-4 py-3">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ### CommonCard
 * **Description:** A simple card container component for grouping content with consistent styling.
 * Provides a clean, elevated container with rounded corners, shadow, and padding for content organization.
 * 
 * **Props:**
 * - `title` (String, optional): Title to display in the card header
 * 
 * **Slots:**
 * - `header` (optional): Header content displayed at the top of the card with a bottom border
 * - `default`: Main content to display inside the card body
 * - `footer` (optional): Footer content displayed at the bottom of the card with a top border
 * 
 * **Features:**
 * - Consistent styling with design system colors
 * - Rounded corners (rounded-lg)
 * - Subtle shadow for elevation
 * - Standard padding (p-4) for main content
 * - Optional title prop for simple header text
 * - Optional header section with border separator
 * - Optional footer section with border separator
 * - Header renders when title prop or header slot content is provided
 * - Background color from theme (bg-background)
 * 
 * **Usage Example:**
 * ```vue
 * <!-- Using title prop -->
 * <CommonCard title="Settings">
 *   <p>Card content goes here with any HTML elements</p>
 * </CommonCard>
 * 
 * <!-- Using header slot for custom content -->
 * <CommonCard>
 *   <template #header>
 *     <div class="flex justify-between items-center">
 *       <h3 class="text-lg font-semibold">Custom Header</h3>
 *       <button class="btn btn-sm">Action</button>
 *     </div>
 *   </template>
 *   
 *   <p>Card content goes here with any HTML elements</p>
 *   
 *   <template #footer>
 *     <div class="flex justify-end space-x-2">
 *       <button class="btn btn-secondary">Cancel</button>
 *       <button class="btn btn-primary">Save</button>
 *     </div>
 *   </template>
 * </CommonCard>
 * ```
 */

/**
 * Component props interface
 */
interface Props {
  /** Title to display in the card header */
  title?: string;
}

// Define props with TypeScript
defineProps<Props>();
</script>
