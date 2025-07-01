<script setup>
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faChevronDown } from "@fortawesome/free-solid-svg-icons";
import { computed, onMounted, onUnmounted, ref, Teleport, Transition } from "vue";

/**
 * DropdownComponent
 * -----------------------------------------------------------------------------
 * A reusable dropdown component with customizable button, icon, size, variant,
 * alignment, and animated dropdown panel. The dropdown content is provided via
 * a slot and can be fully customized.
 *
 * ## Props
 * - buttonText (string, required): The text to display on the dropdown button.
 * - buttonIcon (object, optional): FontAwesome icon object for the button (e.g. faPlus).
 * - size (string, default: 'm'): Button size ('xs', 'm', 'l').
 * - variant (string, default: 'primary'): Button variant ('primary', 'secondary', etc.).
 * - disabled (boolean, default: false): Whether the dropdown button is disabled.
 * - title (string, optional): Tooltip text for the button.
 * - dropdownWidth (number, default: 200): Width of the dropdown panel in pixels.
 * - align (string, default: 'left'): Dropdown alignment relative to button ('left' or 'right').
 *
 * ## Emits
 * - item-selected: Emitted when a dropdown item is selected (payload: item).
 *
 * ## Slots
 * - default (scoped): The dropdown panel content.
 *   Scoped slot props:
 *     - close: Function to close the dropdown.
 *     - handleItemClick: Function to handle item selection (emits 'item-selected' and closes).
 *
 * ## Usage Example
 * <DropdownComponent
 *   button-text="Add Workflow"
 *   :button-icon="faPlus"
 *   size="m"
 *   variant="primary"
 *   :dropdown-width="300"
 *   align="left"
 *   @item-selected="onWorkflowSelected"
 * >
 *   <template #default="{ handleItemClick, close }">
 *     <div v-for="item in items" :key="item.id"
 *          class="p-2 hover:bg-background-soft cursor-pointer rounded"
 *          @click="handleItemClick(item)">
 *       {{ item.name }}
 *     </div>
 *   </template>
 * </DropdownComponent>
 *
 * ## Notes
 * - The dropdown panel is teleported to <body> for correct layering and positioning.
 * - The chevron icon rotates with animation when open.
 * - The dropdown auto-closes on outside click or scroll.
 * - Use the slot's handleItemClick for selection, or close() to close manually.
 */

const props = defineProps({
  buttonText: {
    type: String,
    required: true
  },
  buttonIcon: {
    type: Object,
    default: null
  },
  size: {
    type: String,
    default: 'm',
    validator: (value) => ['xs', 'm', 'l'].includes(value)
  },
  variant: {
    type: String,
    default: 'primary'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  dropdownWidth: {
    type: Number,
    default: 200
  },
  align: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value)
  }
});

const emit = defineEmits(['item-selected']);

// Reactive state
const isOpen = ref(false);
const dropdownPosition = ref({ top: 0, left: 0 });
const dropdownId = ref(`dropdown-${Math.random().toString(36).substr(2, 9)}`);

// Computed classes based on size
const buttonClasses = computed(() => {
  const baseClasses = `btn btn-${props.variant} flex items-center`;
  const sizeClasses = {
    xs: 'text-xs px-2 py-1 h-8',
    m: 'text-sm px-3 py-2 h-10', 
    l: 'text-base px-4 py-3 h-12'
  };
  return `${baseClasses} ${sizeClasses[props.size]}`;
});

const iconSize = computed(() => {
  const sizes = {
    xs: 'text-xs',
    m: 'text-sm',
    l: 'text-base'
  };
  return sizes[props.size];
});

/**
 * ### toggleDropdown
 * **Description:** Toggles the dropdown open/closed state and calculates position.
 * **Parameters:**
 * - `event` (Event): The click event from the button.
 */
const toggleDropdown = (event) => {
  if (props.disabled) return;
  
  if (isOpen.value) {
    closeDropdown();
  } else {
    openDropdown(event);
  }
};

/**
 * ### openDropdown
 * **Description:** Opens the dropdown and calculates its position.
 * **Parameters:**
 * - `event` (Event): The click event from the button.
 */
const openDropdown = (event) => {
  if (event && event.currentTarget) {
    const buttonElement = event.currentTarget;
    const rect = buttonElement.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    let left = rect.left;
    let top = rect.bottom + 4;
    
    // Handle alignment
    if (props.align === 'right') {
      left = rect.right - props.dropdownWidth;
    }
    
    // Adjust if dropdown would overflow viewport horizontally
    if (left + props.dropdownWidth > viewportWidth) {
      left = viewportWidth - props.dropdownWidth - 20;
    }
    if (left < 20) {
      left = 20;
    }
    
    // Adjust if dropdown would overflow viewport vertically
    const estimatedDropdownHeight = 200; // Approximate max height
    if (top + estimatedDropdownHeight > viewportHeight) {
      top = rect.top - estimatedDropdownHeight - 4; // Show above button
      if (top < 20) {
        top = rect.bottom + 4; // Fallback to below
      }
    }
    
    dropdownPosition.value = { top, left };
  }
  
  isOpen.value = true;
};

/**
 * ### closeDropdown
 * **Description:** Closes the dropdown.
 */
const closeDropdown = () => {
  isOpen.value = false;
};

/**
 * ### handleItemClick
 * **Description:** Handles click on a dropdown item and emits the selection.
 * **Parameters:**
 * - `item` (any): The selected item data.
 */
const handleItemClick = (item) => {
  emit('item-selected', item);
  closeDropdown();
};

/**
 * ### handleOutsideClick
 * **Description:** Closes dropdown when clicking outside of it.
 * **Parameters:**
 * - `event` (Event): The click event.
 */
const handleOutsideClick = (event) => {
  if (!event.target) return;
  
  // Don't close if clicking on the button
  const buttonElement = event.target.closest(`[data-dropdown-id="${dropdownId.value}"]`);
  if (buttonElement) return;
  
  // Don't close if clicking inside the dropdown
  const dropdownElement = event.target.closest('.dropdown-content');
  if (dropdownElement && dropdownElement.dataset.dropdownId === dropdownId.value) return;
  
  closeDropdown();
};

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
  window.addEventListener('scroll', closeDropdown);
});

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick);
  window.removeEventListener('scroll', closeDropdown);
});
</script>

<template>
  <div class="relative">
    <!-- Dropdown Button -->
    <button
      @click="toggleDropdown"
      :class="buttonClasses"
      :disabled="disabled"
      :title="title"
      :data-dropdown-id="dropdownId"
    >
      <FontAwesomeIcon 
        v-if="buttonIcon" 
        :icon="buttonIcon" 
        :class="iconSize"
        class="mr-1" 
      />
      {{ buttonText }}
      <FontAwesomeIcon 
        :icon="faChevronDown" 
        :class="iconSize"
        class="ml-1 transition-transform duration-200 ease-in-out"
        :style="{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }"
      />
    </button>

    <!-- Dropdown Content (Teleported to body) -->
    <Teleport to="body">
      <Transition
        name="dropdown"
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div
          v-if="isOpen"
          class="fixed z-50 bg-background border border-border rounded-lg shadow-lg dropdown-content"
          :data-dropdown-id="dropdownId"
          :style="{
            top: dropdownPosition.top + 'px',
            left: dropdownPosition.left + 'px',
            width: dropdownWidth + 'px'
          }"
        >
          <div class="p-2">
            <slot 
              :close="closeDropdown" 
              :handleItemClick="handleItemClick"
            />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
