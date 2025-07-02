<template>
  <div class="border border-border rounded-lg overflow-hidden">
    <!-- Accordion Header -->
    <div
      class="flex justify-between items-center cursor-pointer bg-background-mute hover:bg-background-soft transition-colors"
      :class="[headerClasses, { 'border-b border-border': isOpen }]"
      @click="toggleAccordion"
    >
      <div class="flex items-center" :class="gapClasses">
        <FontAwesomeIcon
          v-if="icon"
          :icon="icon"
          class="text-secondary"
          :class="iconClasses"
        />
        <h2 class="text-text-light" :class="titleClasses">{{ title }}</h2>
      </div>
      <FontAwesomeIcon
        icon="chevron-down"
        class="text-text-muted transform transition-transform duration-200"
        :class="[chevronClasses, { 'rotate-180': isOpen }]"
      />
    </div>

    <!-- Accordion Content -->
    <div v-if="isOpen" class="bg-background" :class="contentClasses">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, withDefaults } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/**
 * ### AccordionComponent
 * **Description:** A collapsible accordion component with customizable sizes and icons.
 * Provides an expandable/collapsible content area with smooth transitions and consistent styling.
 * 
 * **Props:**
 * - `title` (String, required): The title displayed in the accordion header
 * - `icon` (String, optional): FontAwesome icon name to display next to the title
 * - `defaultOpen` (Boolean, default: false): Whether the accordion is open by default
 * - `size` (String, default: 'm'): Size variant ('xs', 'm', 'l')
 *   - `xs`: Compact size with smaller padding (p-2) and text - ideal for nested content
 *   - `m`: Default size with standard padding (p-4) and text - ideal for main sections
 *   - `l`: Large size with bigger padding (p-6) and text - ideal for prominent sections
 * 
 * **Usage Example:**
 * ```vue
 * <AccordionComponent 
 *   title="Hardware Profiles" 
 *   icon="server" 
 *   size="xs"
 *   :default-open="true"
 *   @toggle="handleToggle"
 * >
 *   <div class="space-y-2">
 *     <p>Hardware profile content</p>
 *     <button class="btn btn-primary">Configure</button>
 *   </div>
 * </AccordionComponent>
 * ```
 */

/**
 * Size variant type
 */
export type AccordionSize = 'xs' | 'm' | 'l'

/**
 * Component props interface
 */
interface Props {
  /** The title displayed in the accordion header */
  title: string;
  /** FontAwesome icon name to display next to the title */
  icon?: string;
  /** Whether the accordion is open by default */
  defaultOpen?: boolean;
  /** Size variant of the accordion */
  size?: AccordionSize;
}

/**
 * Component emits interface
 */
interface Emits {
  /** Emitted when accordion is toggled */
  toggle: [isOpen: boolean];
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  defaultOpen: false,
  size: 'm'
})

// Define emits
const emit = defineEmits<Emits>()

// Reactive state
const isOpen = ref<boolean>(props.defaultOpen)

/**
 * CSS classes for the accordion header based on size
 */
const headerClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'p-2',
    m: 'p-4',
    l: 'p-6'
  }
  return sizeClasses[props.size]
})

/**
 * CSS classes for the accordion content based on size
 */
const contentClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'p-2',
    m: 'p-4',
    l: 'p-6'
  }
  return sizeClasses[props.size]
})

/**
 * CSS classes for the title based on size
 */
const titleClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'text-sm font-medium',
    m: 'text-xl font-semibold',
    l: 'text-2xl font-bold'
  }
  return sizeClasses[props.size]
})

/**
 * CSS classes for the icon based on size
 */
const iconClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'text-sm',
    m: 'text-lg',
    l: 'text-xl'
  }
  return sizeClasses[props.size]
})

/**
 * CSS classes for the chevron based on size
 */
const chevronClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'text-sm',
    m: 'text-base',
    l: 'text-lg'
  }
  return sizeClasses[props.size]
})

/**
 * CSS classes for the gap between icon and title based on size
 */
const gapClasses = computed<string>(() => {
  const sizeClasses: Record<AccordionSize, string> = {
    xs: 'gap-1',
    m: 'gap-2',
    l: 'gap-3'
  }
  return sizeClasses[props.size]
})

/**
 * ### toggleAccordion
 * **Description:** Toggles the accordion open/closed state and emits toggle event.
 * **Parameters:** None
 * **Returns:** None
 * **Emits:** toggle event with current open state
 */
const toggleAccordion = (): void => {
  isOpen.value = !isOpen.value
  emit('toggle', isOpen.value)
}

/**
 * ### open
 * **Description:** Opens the accordion programmatically and emits toggle event.
 * **Parameters:** None
 * **Returns:** None
 * **Emits:** toggle event with true value
 */
const open = (): void => {
  isOpen.value = true
  emit('toggle', isOpen.value)
}

/**
 * ### close
 * **Description:** Closes the accordion programmatically and emits toggle event.
 * **Parameters:** None
 * **Returns:** None
 * **Emits:** toggle event with false value
 */
const close = (): void => {
  isOpen.value = false
  emit('toggle', isOpen.value)
}

// Expose methods for template refs
defineExpose({
  open,
  close,
  toggleAccordion
})
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
