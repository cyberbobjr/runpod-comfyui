<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

/**
 * FormDropdownComponent
 * -----------------------------------------------------------------------------
 * A simple, form-style dropdown for use in forms (e.g., workflow selection).
 *
 * ## Props
 * - label (string, required): The label or button text to display.
 * - icon (object, optional): FontAwesome icon object for the button (e.g. faPlusCircle).
 * - items (Array<any>, required): The list of items to display in the dropdown.
 * - itemKey (string|function, default: 'id'): The property or function to use as unique key for each item.
 * - itemLabel (string|function, default: 'label'): The property or function to use as label for each item.
 * - placeholder (string, optional): Text to show when no items are available.
 * - disabled (boolean, default: false): Whether the dropdown is disabled.
 * - widthClass (string, default: 'w-full'): Tailwind width class for the dropdown panel.
 *
 * ## Emits
 * - select: Emitted when an item is selected (payload: item).
 *
 * ## Slots
 * - default (scoped): Custom content for each item. Props: { item, select }
 * - empty: Custom content when no items are available.
 *
 * ## Example Usage
 * <FormDropdownComponent
 *   label="Add Workflows"
 *   :icon="faPlusCircle"
 *   :items="availableWorkflows"
 *   item-key="name"
 *   item-label="name"
 *   placeholder="All workflows are already selected"
 *   @select="addWorkflowToSelection"
 * />
 */

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, default: null },
  items: { type: Array, required: true },
  itemKey: { type: [String, Function], default: "id" },
  itemLabel: { type: [String, Function], default: "label" },
  placeholder: { type: String, default: "No items available" },
  disabled: { type: Boolean, default: false },
  widthClass: { type: String, default: "w-full" },
});

const emit = defineEmits(["select"]);

const isOpen = ref(false);
const dropdownRef = ref(null);
const buttonRef = ref(null);

/**
 * getItemKey
 * Description: Returns the unique key for an item. If the item is a primitive, returns the item itself.
 * Parameters:
 * - item (any): The item from the items array.
 * Returns: The key (string|number|any).
 */
function getItemKey(item) {
  if (item !== Object(item)) return item; // primitive (string, number, etc.)
  if (typeof props.itemKey === "function") return props.itemKey(item);
  return item[props.itemKey];
}
/**
 * getItemLabel
 * Description: Returns the label for an item. If the item is a primitive, returns the item itself.
 * Parameters:
 * - item (any): The item from the items array.
 * Returns: The label (string|number|any).
 */
function getItemLabel(item) {
  if (item !== Object(item)) return item; // primitive (string, number, etc.)
  if (typeof props.itemLabel === "function") return props.itemLabel(item);
  return item[props.itemLabel];
}

function toggleDropdown() {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
  if (isOpen.value) nextTick(() => {
    // Focus first item for accessibility if needed
  });
}
function closeDropdown() {
  isOpen.value = false;
}
function handleSelect(item) {
  emit("select", item);
  closeDropdown();
}

function handleClickOutside(event) {
  if (
    dropdownRef.value &&
    !dropdownRef.value.contains(event.target) &&
    buttonRef.value &&
    !buttonRef.value.contains(event.target)
  ) {
    closeDropdown();
  }
}
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
