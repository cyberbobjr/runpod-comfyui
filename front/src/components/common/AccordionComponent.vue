<template>
  <div class="border border-border rounded-lg overflow-hidden">
    <!-- Accordion Header -->
    <div 
      class="flex justify-between items-center cursor-pointer p-4 bg-background-mute hover:bg-background-soft transition-colors"
      :class="{ 'border-b border-border': isOpen }"
      @click="toggleAccordion"
    >
      <div class="flex items-center gap-3">
        <FontAwesomeIcon 
          v-if="icon" 
          :icon="icon" 
          class="text-secondary text-xl" 
        />
        <h2 class="text-xl font-semibold text-text-light">{{ title }}</h2>
      </div>
      <FontAwesomeIcon 
        icon="chevron-down" 
        class="text-text-muted transform transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
      />
    </div>
    
    <!-- Accordion Content -->
    <div 
      v-if="isOpen"
      class="p-4 bg-background"
    >
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AccordionComponent',
  props: {
    /**
     * The title displayed in the accordion header
     */
    title: {
      type: String,
      required: true
    },
    /**
     * FontAwesome icon name to display next to the title (optional)
     */
    icon: {
      type: String,
      default: null
    },
    /**
     * Whether the accordion is open by default
     */
    defaultOpen: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isOpen: this.defaultOpen
    }
  },
  methods: {
    /**
     * Toggles the accordion open/closed state
     */
    toggleAccordion() {
      this.isOpen = !this.isOpen
      this.$emit('toggle', this.isOpen)
    },
    
    /**
     * Opens the accordion
     */
    open() {
      this.isOpen = true
      this.$emit('toggle', this.isOpen)
    },
    
    /**
     * Closes the accordion
     */
    close() {
      this.isOpen = false
      this.$emit('toggle', this.isOpen)
    }
  },
  emits: ['toggle']
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
