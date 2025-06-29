<template>
  <div class="card bg-background rounded-lg shadow p-4">
    <slot />
  </div>
</template>

<script setup>
/**
 * ### CommonCard
 * **Description:** A simple card container component for grouping content with consistent styling.
 * Provides a clean, elevated container with rounded corners, shadow, and padding for content organization.
 * 
 * **Props:** None
 * 
 * **Slots:**
 * - `default`: Content to display inside the card
 * 
 * **Features:**
 * - Consistent styling with design system colors
 * - Rounded corners (rounded-lg)
 * - Subtle shadow for elevation
 * - Standard padding (p-4)
 * - Background color from theme (bg-background)
 * 
 * **Usage Example:**
 * ```vue
 * <CommonCard>
 *   <h3 class="text-lg font-semibold mb-4">Card Title</h3>
 *   <p>Card content goes here with any HTML elements</p>
 *   <div class="mt-4">
 *     <button class="btn btn-primary">Action Button</button>
 *   </div>
 * </CommonCard>
 * ```
 */
</script>
