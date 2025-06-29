# Common Components Documentation

This document provides a comprehensive overview of all reusable components available in `/front/src/components/common/`. These components should be used instead of creating custom components from scratch.

## AccordionComponent

A collapsible accordion component with customizable sizes and icons.

### Props
- `title` (String, required): The title displayed in the accordion header
- `icon` (String, optional): FontAwesome icon name to display next to the title
- `defaultOpen` (Boolean, default: false): Whether the accordion is open by default
- `size` (String, default: 'm'): Size variant ('xs', 'm', 'l')
  - `xs`: Compact size with smaller padding (p-2) and text - ideal for nested content
  - `m`: Default size with standard padding (p-4) and text - ideal for main sections  
  - `l`: Large size with bigger padding (p-6) and text - ideal for prominent sections

### Slots
- `default`: Content displayed when the accordion is expanded

### Usage Example
```vue
<AccordionComponent 
  title="Hardware Profiles" 
  icon="server" 
  size="xs"
  :default-open="true"
>
  <p>Accordion content goes here</p>
</AccordionComponent>
```

---

## CommonCard

A simple card container component for grouping content with consistent styling.

### Props
None

### Slots
- `default`: Content to display inside the card

### Usage Example
```vue
<CommonCard>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</CommonCard>
```

---

## CommonEmptyState

A component for displaying empty states when there is no data to show.

### Props
None

### Slots
- `icon` (optional): Custom icon to display
- `title` (optional): Title text (default: "No Data")
- `description` (optional): Description text (default: "There is nothing to display here.")
- `action` (optional): Action button or element

### Usage Example
```vue
<CommonEmptyState>
  <template #icon>
    <FontAwesomeIcon :icon="faBoxOpen" class="text-4xl text-gray-500 mb-4" />
  </template>
  <template #title>No Bundles Found</template>
  <template #description>Upload a bundle file to get started.</template>
  <template #action>
    <button class="btn btn-primary">Upload Bundle</button>
  </template>
</CommonEmptyState>
```

---

## CommonModal

A modal dialog component with header, content, and footer sections.

### Props
- `show` (Boolean, required): Controls the visibility of the modal

### Emits
- `close`: Emitted when the modal requests to be closed

### Slots
- `title`: Modal title text (default: "Modal Title")
- `close-icon` (optional): Custom close icon
- `default`: Main modal content
- `footer` (optional): Footer content (default: Close button)

### Usage Example
```vue
<CommonModal :show="showModal" @close="showModal = false">
  <template #title>Bundle Details</template>
  <div>
    <p>Modal content goes here</p>
  </div>
  <template #footer>
    <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
    <button class="btn btn-primary" @click="save">Save</button>
  </template>
</CommonModal>
```

---

## DropdownComponent

A reusable dropdown component with customizable sizes, positioning, and variants.

### Props
- `buttonText` (String, required): Text to display on the dropdown button
- `buttonIcon` (Object, optional): FontAwesome icon to display on the button
- `size` (String, default: 'm'): Size of the dropdown ('xs', 'm', 'l')
  - `xs`: text-xs px-2 py-1
  - `m`: text-sm px-3 py-2
  - `l`: text-base px-4 py-3
- `variant` (String, default: 'primary'): Button variant ('primary', 'secondary', 'danger', etc.)
- `disabled` (Boolean, default: false): Whether the dropdown is disabled
- `title` (String, optional): Tooltip text for the button
- `dropdownWidth` (Number, default: 200): Width of the dropdown in pixels
- `align` (String, default: 'left'): Alignment of dropdown ('left', 'right')

### Emits
- `item-selected`: Emitted when a dropdown item is selected, passes the selected item

### Slots
- `default`: Dropdown content with scoped slot props:
  - `close`: Function to close the dropdown
  - `handleItemClick`: Function to handle item clicks and emit selection

### Features
- Intelligent positioning (handles viewport overflow)
- Teleported to body for proper z-index layering
- Auto-closes on outside click and scroll
- Responsive positioning (above/below based on viewport space)

### Usage Example
```vue
<DropdownComponent
  button-text="Install"
  :button-icon="faDownload"
  size="xs"
  variant="primary"
  title="Install bundle profiles"
  :dropdown-width="250"
  align="left"
  @item-selected="handleSelection"
>
  <template #default="{ handleItemClick }">
    <div class="text-sm font-medium text-text-light mb-2">
      Select an option:
    </div>
    <div
      v-for="option in options"
      :key="option.id"
      class="p-2 hover:bg-background-soft rounded cursor-pointer"
      @click="handleItemClick(option)"
    >
      {{ option.name }}
    </div>
  </template>
</DropdownComponent>
```

---

## FooterComponent

Application footer component showing version information and build details.

### Props
- Likely has props for version info, build date, etc. (implementation details in component)

### Features
- Displays app name and version
- Shows build date and build number
- Version details modal
- Responsive layout

### Usage Example
```vue
<FooterComponent />
```

---

## TooltipComponent

A tooltip component that shows additional information on hover.

### Props
- `text` (String, required): The tooltip text to display
- `position` (String, default: 'top'): Position of the tooltip ('top', 'bottom', 'left', 'right')
- `delay` (Number, default: 500): Delay in milliseconds before showing the tooltip

### Slots
- `default`: The element that triggers the tooltip

### Features
- Teleported to body for proper positioning
- Smart positioning based on viewport bounds
- Smooth fade transition
- Configurable delay
- Arrow pointing to trigger element

### Usage Example
```vue
<TooltipComponent text="This is a helpful tooltip" position="top" :delay="300">
  <button class="btn btn-primary">Hover me</button>
</TooltipComponent>
```

---

## Design System Integration

All components follow the project's design system:

### CSS Classes Used
- **Colors**: `text-text-light`, `text-text-muted`, `bg-background`, `bg-background-soft`, `bg-background-mute`
- **Borders**: `border-border`, `rounded-lg`
- **Buttons**: `btn`, `btn-primary`, `btn-secondary`, `btn-danger`, `btn-danger-outline`
- **Cards**: `card`
- **Form inputs**: `form-input`

### Icons
- All components use FontAwesome icons
- Import icons from `@fortawesome/free-solid-svg-icons`
- Use `FontAwesomeIcon` component from `@fortawesome/vue-fontawesome`

### Responsive Design
- Components use Tailwind CSS responsive utilities
- Modals and dropdowns handle viewport overflow intelligently
- Mobile-friendly sizing and spacing

## Best Practices

1. **Always use these common components** instead of creating custom ones
2. **Follow the size system**: Use 'xs', 'm', 'l' sizes consistently across components
3. **Use appropriate variants**: Choose the right button/component variant for the context
4. **Leverage slots**: Use named slots for maximum flexibility
5. **Handle events properly**: Listen to component events and handle them appropriately
6. **Maintain accessibility**: Components include ARIA attributes and keyboard support where applicable
7. **Test responsiveness**: Ensure components work well on different screen sizes

## Component Combinations

Components can be combined effectively:

```vue
<CommonCard>
  <AccordionComponent title="Advanced Options" size="m">
    <DropdownComponent 
      button-text="Select Action" 
      size="xs"
      @item-selected="handleAction"
    >
      <template #default="{ handleItemClick }">
        <!-- Dropdown content -->
      </template>
    </DropdownComponent>
  </AccordionComponent>
</CommonCard>
```

This design system ensures consistency, reusability, and maintainability across the entire application.
