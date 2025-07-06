---
applyTo: '**/*vue'
---
# Instructions for Code generation
The library used for styling is Tailwind CSS.
When you create a new component, always create the associated test file in the `__tests__` directory.

# styling
the style is global and defined in "/front/src/assets/main.css" don't create new style files or classes if the style exists in the global style file.

# Common Components
Always use common components available in the project instead of creating new ones. The common components are located in the `/front/src/components/common` directory.
These components are designed to be reusable and maintain consistency across the application.

* AccordionComponent.vue
* ButtonDropdownComponent.vue
* CommonCard.vue
* CommonModale.vue
* DialogContainer.vue
* DropdownComponent.vue
* FormDropdownComponent.vue
* TooltipComponent.vue

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
