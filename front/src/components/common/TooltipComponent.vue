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

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  position: {
    type: String,
    default: 'top',
    validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  },
  delay: {
    type: Number,
    default: 500
  }
})

const visible = ref(false)
const triggerRef = ref(null)
const tooltipStyle = ref({})
let timeoutId = null

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

function showTooltip() {
  timeoutId = setTimeout(async () => {
    visible.value = true
    await nextTick()
    calculatePosition()
  }, props.delay)
}

function hideTooltip() {
  if (timeoutId) {
    clearTimeout(timeoutId)
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
