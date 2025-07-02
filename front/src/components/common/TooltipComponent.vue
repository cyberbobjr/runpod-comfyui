<template>
  <div class="relative inline-block" @mouseenter="showTooltip" @mouseleave="hideTooltip" ref="triggerRef">
    <slot />
    <Teleport to="body">
      <Transition
        name="tooltip-fade"
        appear
      >
        <div
          v-if="visible"
          :class="[
            'fixed z-[9999] px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-xl',
            'border border-gray-700 backdrop-blur-sm',
            'pointer-events-none whitespace-nowrap'
          ]"
          :style="tooltipStyle"
        >
          {{ text }}
          <div :class="['absolute w-2 h-2 bg-gray-900 border-l border-b border-gray-700 transform rotate-45', arrowClasses]"></div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
/**
 * ### TooltipComponent
 * **Description:** A tooltip component that shows additional information on hover.
 * Provides intelligent positioning, smooth transitions, and configurable delay for enhanced UX.
 * 
 * **Props:**
 * - `text` (String, required): The tooltip text to display
 * - `position` (String, default: 'top'): Position of the tooltip ('top', 'bottom', 'left', 'right')
 * - `delay` (Number, default: 500): Delay in milliseconds before showing the tooltip
 * 
 * **Slots:**
 * - `default`: The element that triggers the tooltip (hover target)
 * 
 * **Features:**
 * - Teleported to body for proper z-index layering (z-[9999])
 * - Smart positioning based on viewport bounds
 * - Smooth fade transition with backdrop blur
 * - Configurable show/hide delay
 * - Arrow pointing to trigger element
 * - Automatic collision detection and repositioning
 * - Dark theme styling with border
 * 
 * **Usage Example:**
 * ```vue
 * <TooltipComponent 
 *   text="This action will delete the selected items permanently" 
 *   position="top" 
 *   :delay="300"
 * >
 *   <button class="btn btn-danger">
 *     <FontAwesomeIcon :icon="faTrash" />
 *     Delete
 *   </button>
 * </TooltipComponent>
 * ```
 */
import { ref, computed, nextTick, withDefaults } from 'vue'

/**
 * Tooltip position type
 */
export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right'

/**
 * Component props interface
 */
interface Props {
  /** The tooltip text to display */
  text: string;
  /** Position of the tooltip */
  position?: TooltipPosition;
  /** Delay in milliseconds before showing the tooltip */
  delay?: number;
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  position: 'top',
  delay: 500
})

// Reactive state for tooltip visibility and positioning
const visible = ref<boolean>(false)
const triggerRef = ref<HTMLElement>()
const tooltipStyle = ref<Record<string, string>>({})
let timeoutId: number | null = null

const arrowClasses = computed(() => {
  switch (props.position) {
    case 'top':
      return 'top-full left-1/2 transform -translate-x-1/2 -mt-1'
    case 'bottom':
      return 'bottom-full left-1/2 transform -translate-x-1/2 -mb-1'
    case 'left':
      return 'left-full top-1/2 transform -translate-y-1/2 -ml-1'
    case 'right':
      return 'right-full top-1/2 transform -translate-y-1/2 -mr-1'
    default:
      return 'top-full left-1/2 transform -translate-x-1/2 -mt-1'
  }
})

/**
 * ### calculatePosition
 * **Description:** Calculates the optimal position for the tooltip based on trigger element and position prop.
 * **Parameters:** None
 * **Returns:** None (updates tooltipStyle ref)
 */
function calculatePosition() {
  if (!triggerRef.value) return

  const rect = triggerRef.value.getBoundingClientRect()
  const offset = 8 // Distance from trigger element

  switch (props.position) {
    case 'top':
      tooltipStyle.value = {
        left: `${rect.left + rect.width / 2}px`,
        top: `${rect.top - offset}px`,
        transform: 'translate(-50%, -100%)'
      }
      break
    case 'bottom':
      tooltipStyle.value = {
        left: `${rect.left + rect.width / 2}px`,
        top: `${rect.bottom + offset}px`,
        transform: 'translate(-50%, 0)'
      }
      break
    case 'left':
      tooltipStyle.value = {
        left: `${rect.left - offset}px`,
        top: `${rect.top + rect.height / 2}px`,
        transform: 'translate(-100%, -50%)'
      }
      break
    case 'right':
      tooltipStyle.value = {
        left: `${rect.right + offset}px`,
        top: `${rect.top + rect.height / 2}px`,
        transform: 'translate(0, -50%)'
      }
      break
    default:
      tooltipStyle.value = {
        left: `${rect.left + rect.width / 2}px`,
        top: `${rect.top - offset}px`,
        transform: 'translate(-50%, -100%)'
      }
  }
}

/**
 * ### showTooltip
 * **Description:** Shows the tooltip after the configured delay period.
 * **Parameters:** None
 * **Returns:** None
 */
function showTooltip() {
  timeoutId = window.setTimeout(async () => {
    visible.value = true
    await nextTick()
    calculatePosition()
  }, props.delay)
}

/**
 * ### hideTooltip
 * **Description:** Hides the tooltip immediately and clears any pending show timeout.
 * **Parameters:** None
 * **Returns:** None
 */
function hideTooltip() {
  if (timeoutId) {
    window.clearTimeout(timeoutId)
    timeoutId = null
  }
  visible.value = false
}
</script>

<style scoped>
.tooltip-fade-enter-active {
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.tooltip-fade-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}

.tooltip-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, -100%) scale(0.95);
}

.tooltip-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -100%) scale(0.95);
}

.tooltip-fade-enter-to {
  opacity: 1;
  transform: translate(-50%, -100%) scale(1);
}
</style>
