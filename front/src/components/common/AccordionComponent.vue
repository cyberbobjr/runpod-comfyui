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

<script>
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
 * **Slots:**
 * - `default`: Content displayed when the accordion is expanded
 * 
 * **Features:**
 * - Smooth expand/collapse animation with chevron rotation
 * - Hover effects on header for better UX
 * - Border and rounded corners for clean appearance
 * - Responsive sizing system
 * - Icon support with FontAwesome integration
 * - Click-to-toggle functionality
 * 
 * **Methods:**
 * - `toggleAccordion()`: Toggles the open/closed state of the accordion
 * 
 * **Usage Example:**
 * ```vue
 * <AccordionComponent 
 *   title="Hardware Profiles" 
 *   icon="server" 
 *   size="xs"
 *   :default-open="true"
 * >
 *   <div class="space-y-2">
 *     <p>Accordion content goes here</p>
 *     <div class="grid grid-cols-2 gap-4">
 *       <!-- Additional content -->
 *     </div>
 *   </div>
 * </AccordionComponent>
 * ```
 */
export default {
  name: "AccordionComponent",
  props: {
    /**
     * The title displayed in the accordion header
     */
    title: {
      type: String,
      required: true,
    },
    /**
     * FontAwesome icon name to display next to the title (optional)
     */
    icon: {
      type: String,
      default: null,
    },
    /**
     * Whether the accordion is open by default
     */
    defaultOpen: {
      type: Boolean,
      default: false,
    },
    /**
     * Size of the accordion (xs, m, l)
     * - xs: Compact size with smaller padding and text (ideal for nested content)
     * - m: Default size with standard padding and text (ideal for main sections)
     * - l: Large size with bigger padding and text (ideal for prominent sections)
     */
    size: {
      type: String,
      default: "m",
      validator(value) {
        return ["xs", "m", "l"].includes(value);
      },
    },
  },
  data() {
    return {
      isOpen: this.defaultOpen,
    };
  },
  computed: {
    /**
     * CSS classes for the accordion header based on size
     */
    headerClasses() {
      const sizeClasses = {
        xs: "p-2",
        m: "p-4",
        l: "p-6",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
    /**
     * CSS classes for the accordion content based on size
     */
    contentClasses() {
      const sizeClasses = {
        xs: "p-2",
        m: "p-4",
        l: "p-6",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
    /**
     * CSS classes for the title based on size
     */
    titleClasses() {
      const sizeClasses = {
        xs: "text-sm font-medium",
        m: "text-xl font-semibold",
        l: "text-2xl font-bold",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
    /**
     * CSS classes for the icon based on size
     */
    iconClasses() {
      const sizeClasses = {
        xs: "text-sm",
        m: "text-xl",
        l: "text-2xl",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
    /**
     * CSS classes for the chevron icon based on size
     */
    chevronClasses() {
      const sizeClasses = {
        xs: "text-sm",
        m: "text-base",
        l: "text-lg",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
    /**
     * Gap classes for the header items based on size
     */
    gapClasses() {
      const sizeClasses = {
        xs: "gap-2",
        m: "gap-3",
        l: "gap-4",
      };
      return sizeClasses[this.size] || sizeClasses.m;
    },
  },
  methods: {
    /**
     * ### toggleAccordion
     * **Description:** Toggles the accordion open/closed state and emits toggle event.
     * **Parameters:** None
     * **Returns:** None
     * **Emits:** toggle event with current open state (Boolean)
     */
    toggleAccordion() {
      this.isOpen = !this.isOpen;
      this.$emit("toggle", this.isOpen);
    },

    /**
     * ### open
     * **Description:** Opens the accordion programmatically and emits toggle event.
     * **Parameters:** None
     * **Returns:** None
     * **Emits:** toggle event with true value
     */
    open() {
      this.isOpen = true;
      this.$emit("toggle", this.isOpen);
    },

    /**
     * ### close
     * **Description:** Closes the accordion programmatically and emits toggle event.
     * **Parameters:** None
     * **Returns:** None
     * **Emits:** toggle event with false value
     */
    close() {
      this.isOpen = false;
      this.$emit("toggle", this.isOpen);
    },
  },
  emits: ["toggle"],
};
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
