<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, withDefaults } from "vue";
import type { Ref } from "vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";

/**
 * FormDropdownComponent
 * -----------------------------------------------------------------------------
 * A simple, form-style dropdown for use in forms (e.g., workflow selection).
 * Designed to integrate seamlessly with form layouts and styling.
 *
 * ## Props
 * - `label` (string, required): The label or button text to display.
 * - `icon` (IconDefinition, optional): FontAwesome icon object for the button (e.g. faPlusCircle).
 * - `items` (Array<any>, required): The list of items to display in the dropdown.
 * - `itemKey` (string|function, default: 'id'): The property or function to use as unique key for each item.
 * - `itemLabel` (string|function, default: 'label'): The property or function to use as label for each item.
 * - `placeholder` (string, default: 'No items available'): Text to show when no items are available.
 * - `disabled` (boolean, default: false): Whether the dropdown is disabled.
 * - `widthClass` (string, default: 'w-full'): Tailwind width class for the dropdown panel.
 *
 * ## Features & Behavior
 * - Form-integrated styling that matches other form inputs
 * - Auto-closes on outside click
 * - Supports both primitive and object items
 * - Flexible key/label extraction via properties or functions
 * - Customizable item rendering via slots
 * - Disabled state support
 * - Smooth open/close animations
 * - Keyboard accessibility ready
 * - Scrollable item list for large datasets
 *
 * ## Emits
 * - `select`: Emitted when an item is selected (payload: item).
 *
 * ## Slots
 * - `default` (scoped): Custom content for each item. Props: { item, select }
 * - `empty`: Custom content when no items are available.
 *
 * ## Methods
 * ### getItemKey
 * **Description:** Returns the unique key for an item. If the item is a primitive, returns the item itself.
 * **Parameters:**
 * - `item` (any): The item from the items array.
 * **Returns:** The key (string|number|any).
 *
 * ### getItemLabel
 * **Description:** Returns the label for an item. If the item is a primitive, returns the item itself.
 * **Parameters:**
 * - `item` (any): The item from the items array.
 * **Returns:** The label (string|number|any).
 *
 * ### toggleDropdown
 * **Description:** Toggles the dropdown open/closed state.
 * **Parameters:** None
 * **Returns:** void
 *
 * ### closeDropdown
 * **Description:** Closes the dropdown.
 * **Parameters:** None
 * **Returns:** void
 *
 * ### handleSelect
 * **Description:** Handles item selection and emits the select event.
 * **Parameters:**
 * - `item` (any): The selected item.
 * **Returns:** void
 *
 * ### handleClickOutside
 * **Description:** Closes dropdown when clicking outside of it.
 * **Parameters:**
 * - `event` (Event): The click event.
 * **Returns:** void
 *
 * ## Example Usage
 * ```vue
 * <FormDropdownComponent
 *   label="Add Workflows"
 *   :icon="faPlusCircle"
 *   :items="availableWorkflows"
 *   item-key="name"
 *   item-label="name"
 *   placeholder="All workflows are already selected"
 *   @select="addWorkflowToSelection"
 * />
 * ```
 */

/**
 * Key/Label extractor function type
 */
type KeyLabelExtractor = ((item: any) => string | number) | string;

/**
 * Component props interface
 */
interface Props {
  /** The label or button text to display */
  label: string;
  /** FontAwesome icon object for the button */
  icon?: IconDefinition;
  /** The list of items to display in the dropdown */
  items: any[];
  /** The property or function to use as unique key for each item */
  itemKey?: KeyLabelExtractor;
  /** The property or function to use as label for each item */
  itemLabel?: KeyLabelExtractor;
  /** Text to show when no items are available */
  placeholder?: string;
  /** Whether the dropdown is disabled */
  disabled?: boolean;
  /** Tailwind width class for the dropdown panel */
  widthClass?: string;
}

/**
 * Component emits interface
 */
interface Emits {
  /** Emitted when an item is selected */
  select: [item: any];
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  itemKey: "id",
  itemLabel: "label",
  placeholder: "No items available",
  disabled: false,
  widthClass: "w-full",
});

// Define emits
const emit = defineEmits<Emits>();

// Reactive state
const isOpen = ref<boolean>(false);
const dropdownRef = ref<HTMLElement>();
const buttonRef = ref<HTMLElement>();

/**
 * ### getItemKey
 * **Description:** Returns the unique key for an item. If the item is a primitive, returns the item itself.
 * **Parameters:**
 * - `item` (any): The item from the items array.
 */
function getItemKey(item: any): string | number | any {
  if (item !== Object(item)) return item; // primitive (string, number, etc.)
  if (typeof props.itemKey === "function") return props.itemKey(item);
  return item[props.itemKey as string];
}

/**
 * ### getItemLabel
 * **Description:** Returns the label for an item. If the item is a primitive, returns the item itself.
 * **Parameters:**
 * - `item` (any): The item from the items array.
 */
function getItemLabel(item: any): string | number | any {
  if (item !== Object(item)) return item; // primitive (string, number, etc.)
  if (typeof props.itemLabel === "function") return props.itemLabel(item);
  return item[props.itemLabel as string];
}

/**
 * ### toggleDropdown
 * **Description:** Toggles the dropdown open/closed state.
 */
function toggleDropdown(): void {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
  if (isOpen.value) nextTick(() => {
    // Focus first item for accessibility if needed
  });
}

/**
 * ### closeDropdown
 * **Description:** Closes the dropdown.
 */
function closeDropdown(): void {
  isOpen.value = false;
}

/**
 * ### handleSelect
 * **Description:** Handles item selection and emits the select event.
 * **Parameters:**
 * - `item` (any): The selected item.
 */
function handleSelect(item: any): void {
  emit("select", item);
  closeDropdown();
}

/**
 * ### handleClickOutside
 * **Description:** Closes dropdown when clicking outside of it.
 * **Parameters:**
 * - `event` (Event): The click event.
 */
function handleClickOutside(event: Event): void {
  const target = event.target as Element;
  if (
    dropdownRef.value &&
    !dropdownRef.value.contains(target) &&
    buttonRef.value &&
    !buttonRef.value.contains(target)
  ) {
    closeDropdown();
  }
}

// Lifecycle hooks
onMounted(() => {
  document.addEventListener("mousedown", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("mousedown", handleClickOutside);
});
</script>

<template>
  <div class="relative">
    <button
      ref="buttonRef"
      type="button"
      class="form-input w-full text-left flex items-center justify-between cursor-pointer"
      :disabled="disabled"
      @click="toggleDropdown"
    >
      <span class="flex items-center">
        <FontAwesomeIcon v-if="icon" :icon="icon" class="mr-2" />
        {{ label }}
      </span>
      <FontAwesomeIcon
        :icon="isOpen ? 'chevron-up' : 'chevron-down'"
        :class="[
          'transition-transform duration-200',
          isOpen ? 'rotate-180' : 'rotate-0',
        ]"
      />
    </button>
    <Transition
      name="dropdown-fade-updown"
      enter-active-class="transition duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-out"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-show="isOpen"
        ref="dropdownRef"
        class="absolute z-10 mt-1 bg-background-soft border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto"
        :class="widthClass"
      >
        <div v-if="items.length > 0" class="p-2">
          <slot
            v-for="item in items"
            :key="getItemKey(item)"
            name="default"
            :item="item"
            :select="() => handleSelect(item)"
          >
            <div
              class="flex items-center px-3 py-2 hover:bg-background-mute cursor-pointer rounded"
              @click="handleSelect(item)"
            >
              <FontAwesomeIcon icon="file-code" class="mr-2 text-blue-600" />
              <span>{{ getItemLabel(item) }}</span>
            </div>
          </slot>
        </div>
        <div v-else class="p-4 text-text-muted text-center">
          <slot name="empty">
            <FontAwesomeIcon icon="info-circle" class="mr-1" />{{ placeholder }}
          </slot>
        </div>
      </div>
    </Transition>
  </div>
</template>
