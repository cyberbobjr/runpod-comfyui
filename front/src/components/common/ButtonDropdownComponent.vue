<script setup lang="ts">
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faChevronDown } from "@fortawesome/free-solid-svg-icons";
import {
  computed,
  onMounted,
  onUnmounted,
  ref,
  Teleport,
  Transition,
  withDefaults
} from "vue";
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import type { ComponentSize, ComponentVariant } from "../types/common.types";

/**
 * ButtonDropdownComponent
 * -----------------------------------------------------------------------------
 * A split button component: left side is a main action button, right side is a dropdown toggle with chevron.
 * Dropdown content is provided via slot and can be fully customized.
 *
 * ## Props
 * - `buttonText` (string, required): The text to display on the main button.
 * - `buttonIcon` (IconDefinition, optional): FontAwesome icon object for the main button (e.g. faPlus).
 * - `size` (string, default: 'm'): Button size ('xs', 'm', 'l').
 * - `variant` (string, default: 'primary'): Button variant ('primary', 'secondary', 'danger', etc.).
 * - `disabled` (boolean, default: false): Whether the button is disabled.
 * - `title` (string, optional): Tooltip text for the main button.
 * - `dropdownAlign` (string, default: 'left'): Dropdown alignment relative to the whole button ('left' or 'right').
 *   - 'left': The dropdown's left edge aligns with the button's left edge.
 *   - 'right': The dropdown's right edge aligns with the button's right edge.
 *
 * ## Features & Behavior
 * - The split button is visually consistent: the split (chevron) button uses the same background, text, and hover color as the main button, but is visually non-active.
 * - The vertical separator between the main and split button uses a darker variant color for visual clarity.
 * - The dropdown width automatically adapts to its content (no fixed width).
 * - The dropdown aligns to the left or right of the whole button according to the `dropdownAlign` prop.
 * - The dropdown is teleported to <body> for correct layering and positioning.
 * - The chevron icon rotates with animation when open.
 * - The dropdown auto-closes on outside click or scroll.
 * - The dropdown is scrollable if its content is too long (max-h-64, overflow-auto).
 * - All styling uses Tailwind CSS and the project design system.
 *
 * ## Emits
 * - `item-selected`: Emitted when a dropdown item is selected (payload: item).
 * - `click`: Emitted when the left (main) button is clicked.
 *
 * ## Slots
 * - `default` (scoped): The dropdown panel content.
 *   Scoped slot props:
 *     - `close`: Function to close the dropdown.
 *     - `handleItemClick`: Function to handle item selection (emits 'item-selected' and closes).
 *
 * ## Usage Example
 * ```vue
 * <ButtonDropdownComponent
 *   button-text="Add Workflow"
 *   :button-icon="faPlus"
 *   size="m"
 *   variant="primary"
 *   dropdown-align="right"
 *   @item-selected="onWorkflowSelected"
 *   @click="onMainClick"
 * >
 *   <template #default="{ handleItemClick, close }">
 *     <div v-for="item in items" :key="item.id"
 *          class="p-2 hover:bg-background-soft cursor-pointer rounded"
 *          @click="handleItemClick(item)">
 *       {{ item.name }}
 *     </div>
 *   </template>
 * </ButtonDropdownComponent>
 * ```
 */

/**
 * Dropdown alignment type
 */
export type DropdownAlign = 'left' | 'right'

/**
 * Dropdown position interface
 */
interface DropdownPosition {
  top: number;
  left: number;
  buttonWidth?: number;
}

/**
 * Component props interface
 */
interface Props {
  /** The text to display on the main button */
  buttonText: string;
  /** FontAwesome icon object for the main button */
  buttonIcon?: IconDefinition;
  /** Button size variant */
  size?: ComponentSize;
  /** Button variant style */
  variant?: ComponentVariant;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Tooltip text for the main button */
  title?: string;
  /** Dropdown alignment relative to the whole button */
  dropdownAlign?: DropdownAlign;
}

/**
 * Component emits interface
 */
interface Emits {
  /** Emitted when a dropdown item is selected */
  'item-selected': [item: any];
  /** Emitted when the left (main) button is clicked */
  'click': [event: MouseEvent];
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  size: 'm',
  variant: 'primary',
  disabled: false,
  title: '',
  dropdownAlign: 'left'
})

// Define emits
const emit = defineEmits<Emits>()

// Reactive state
const isOpen = ref<boolean>(false)
const dropdownPosition = ref<DropdownPosition>({ top: 0, left: 0 })
const dropdownId = ref<string>(`dropdown-${Math.random().toString(36).substr(2, 9)}`)
const dropdownRef = ref<HTMLElement>()
const splitButtonRef = ref<HTMLElement>() // Add splitButtonRef for the root container

// Computed classes based on size
const buttonClasses = computed((): string => {
  const baseClasses = `btn btn-${props.variant} flex items-center justify-center`;
  const sizeClasses: Record<ComponentSize, string> = {
    xs: "text-xs px-2 py-1 h-8",
    m: "text-sm px-3 py-2 h-10",
    l: "text-base px-4 py-3 h-12",
  };
  return `${baseClasses} ${sizeClasses[props.size]}`;
});

const splitButtonLeftClasses = computed((): string => {
  // Remove right border radius for left button
  return `${buttonClasses.value} rounded-r-none border-r-0`;
});
// Helper to get Tailwind color classes for variants
function getVariantHoverBg(variant: ComponentVariant): string {
  switch (variant) {
    case "primary":
      return "hover:bg-primary-dark";
    case "secondary":
      return "hover:bg-secondary-dark";
    case "danger":
      return "hover:bg-danger-dark";
    default:
      return "hover:bg-background-soft";
  }
}

function getVariantBorderDarker(variant: ComponentVariant): string {
  switch (variant) {
    case "primary":
      return "border-primary-darker";
    case "secondary":
      return "border-secondary-darker";
    case "danger":
      return "border-danger-darker";
    default:
      return "border-border";
  }
}

const splitButtonRightClasses = computed((): string => {
  // Remove left border radius for right button, add no ring/outline, but keep variant bg and text, and match hover color
  return `${buttonClasses.value} rounded-l-none px-2 w-10 flex items-center justify-center split-button shadow-none focus:ring-0 focus:outline-none active:bg-inherit ${getVariantHoverBg(props.variant)} ${getVariantBorderDarker(props.variant)}`;
});

const iconSize = computed((): string => {
  const sizes: Record<ComponentSize, string> = {
    xs: "text-xs",
    m: "text-sm",
    l: "text-base",
  };
  return sizes[props.size];
});

/**
 * ### toggleDropdown
 * **Description:** Toggles the dropdown open/closed state and calculates position.
 * **Parameters:**
 * - `event` (MouseEvent): The click event from the chevron button.
 */
const toggleDropdown = (event: MouseEvent): void => {
  if (props.disabled) return;
  if (isOpen.value) {
    closeDropdown();
  } else {
    openDropdown(event);
  }
};

/**
 * ### handleMainClick
 * **Description:** Emits the click event for the main (left) button.
 * **Parameters:**
 * - `event` (MouseEvent): The click event from the main button.
 */
const handleMainClick = (event: MouseEvent): void => {
  if (props.disabled) return;
  emit("click", event);
};

/**
 * ### openDropdown
 * **Description:** Opens the dropdown and calculates its position.
 * **Parameters:**
 * - `event` (MouseEvent): The click event from the button.
 */
const openDropdown = (event: MouseEvent): void => {
  // Always use the bounding rect of the whole split button for alignment
  let rect: DOMRect | undefined;
  if (splitButtonRef.value) {
    rect = splitButtonRef.value.getBoundingClientRect();
  } else if (event && event.currentTarget) {
    rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
  }
  if (rect) {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let left: number;
    let top: number = rect.bottom + 4;

    // Align dropdown to left or right of the WHOLE button
    if (props.dropdownAlign === "right") {
      left = rect.right;
    } else {
      left = rect.left;
    }

    // Adjust if dropdown would overflow viewport horizontally (min 20px margin)
    if (left < 20) {
      left = 20;
    }
    if (left > viewportWidth - 20) {
      left = viewportWidth - 20;
    }

    // Adjust if dropdown would overflow viewport vertically
    const estimatedDropdownHeight = 200; // Approximate max height
    if (top + estimatedDropdownHeight > viewportHeight) {
      top = rect.top - estimatedDropdownHeight - 4; // Show above button
      if (top < 20) {
        top = rect.bottom + 4; // Fallback to below
      }
    }

    dropdownPosition.value = { top, left, buttonWidth: rect.width };
  }

  isOpen.value = true;
};

/**
 * ### closeDropdown
 * **Description:** Closes the dropdown.
 */
const closeDropdown = (): void => {
  isOpen.value = false;
};

/**
 * ### handleItemClick
 * **Description:** Handles click on a dropdown item and emits the selection.
 * **Parameters:**
 * - `item` (any): The selected item data.
 */
const handleItemClick = (item: any): void => {
  emit("item-selected", item);
  closeDropdown();
};

/**
 * ### handleOutsideClick
 * **Description:** Closes dropdown when clicking outside of it.
 * **Parameters:**
 * - `event` (Event): The click event.
 */
const handleOutsideClick = (event: Event): void => {
  if (!event.target) return;

  const target = event.target as Element;

  // Don't close if clicking on the button
  const buttonElement = target.closest(
    `[data-dropdown-id="${dropdownId.value}"]`
  );
  if (buttonElement) return;

  // Don't close if clicking inside the dropdown
  const dropdownElement = target.closest(".dropdown-content") as HTMLElement;
  if (
    dropdownElement &&
    dropdownElement.dataset.dropdownId === dropdownId.value
  )
    return;

  closeDropdown();
};

// Lifecycle hooks
onMounted(() => {
  document.addEventListener("click", handleOutsideClick);
  window.addEventListener("scroll", closeDropdown);
});

onUnmounted(() => {
  document.removeEventListener("click", handleOutsideClick);
  window.removeEventListener("scroll", closeDropdown);
});
</script>

<template>
  <div class="relative inline-flex" ref="splitButtonRef">
    <!-- Split Button: Left (main) and Right (dropdown) -->
    <button
      type="button"
      :class="splitButtonLeftClasses"
      :disabled="disabled"
      :title="title"
      @click="handleMainClick"
      :data-dropdown-id="dropdownId"
    >
      <FontAwesomeIcon
        v-if="buttonIcon"
        :icon="buttonIcon"
        :class="iconSize"
        class="mr-1"
      />
      {{ buttonText }}
    </button>
    <!-- Separator -->
    <button
      type="button"
      :class="splitButtonRightClasses"
      :disabled="disabled"
      :aria-label="'Show dropdown'"
      @click="toggleDropdown"
      :data-dropdown-id="dropdownId"
      tabindex="-1"
    >
      <FontAwesomeIcon
        :icon="faChevronDown"
        :class="iconSize"
        class="transition-transform duration-200 ease-in-out"
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
            left: props.dropdownAlign === 'right' ? (dropdownPosition.left - (dropdownRef?.offsetWidth || 0)) + 'px' : dropdownPosition.left + 'px'
          }"
          ref="dropdownRef"
        >
          <div class="p-2 max-h-64 overflow-auto">
            <slot :close="closeDropdown" :handleItemClick="handleItemClick" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.split-button {
    border-left: thin solid var(--vt-c-accent);
}
</style>