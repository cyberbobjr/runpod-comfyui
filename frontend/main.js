// Import Bootswatch Superhero theme
import 'bootswatch/dist/superhero/bootstrap.min.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ConfirmDialogPlugin from './plugins/confirm-dialog'

// Create the app instance
const app = createApp(App)

// Custom directive for Bootstrap tooltips (using CDN-loaded Bootstrap)
app.directive('tooltip', {
  mounted(el, binding) {
    // Ensure Bootstrap's Tooltip is available globally
    if (!window.bootstrap || !window.bootstrap.Tooltip) {
      console.warn('Bootstrap Tooltip not found on window.bootstrap. Make sure Bootstrap JS is loaded via CDN before this script.');
      return;
    }

    let titleValue;
    if (typeof binding.value === 'object' && binding.value !== null && binding.value.title) {
      titleValue = binding.value.title; // Prioritize title from object
    } else if (typeof binding.value === 'string') {
      titleValue = binding.value;
    } else {
      titleValue = el.getAttribute('title') || el.getAttribute('data-bs-original-title') || el.innerText;
    }
    
    // Ensure titleValue is a string if it's not an element or function
    if (typeof titleValue !== 'string' && typeof titleValue !== 'function' && !(titleValue instanceof Element)) {
        titleValue = String(titleValue); // Fallback to string conversion
    }


    let options = {
      title: titleValue,
      placement: binding.arg || 'top', // e.g., v-tooltip:bottom
      trigger: 'hover focus', // Default Bootstrap triggers
      html: binding.modifiers.html || false // Allow HTML content if v-tooltip.html is used
    };

    // Allow passing other options as an object
    if (typeof binding.value === 'object' && binding.value !== null) {
      options = { ...options, ...binding.value, title: titleValue }; // Ensure our processed titleValue is used
    }
    
    if (el.getAttribute('title')) {
      el.setAttribute('data-bs-original-title', el.getAttribute('title'));
      el.removeAttribute('title');
    } else {
       // Ensure data-bs-original-title is set with the final titleValue
       el.setAttribute('data-bs-original-title', typeof options.title === 'function' ? options.title() : options.title);
    }

    // Use the globally available Bootstrap Tooltip
    el.bsTooltip = new window.bootstrap.Tooltip(el, options);
  },
  updated(el, binding) {
    if (!el.bsTooltip) return; // Guard if tooltip wasn't initialized

    let newTitleValue;
    if (typeof binding.value === 'object' && binding.value !== null && binding.value.title) {
      newTitleValue = binding.value.title;
    } else if (typeof binding.value === 'string') {
      newTitleValue = binding.value;
    } else {
      newTitleValue = el.getAttribute('data-bs-original-title') || el.innerText;
    }
    
    // Ensure newTitleValue is a string if it's not an element or function
    if (typeof newTitleValue !== 'string' && typeof newTitleValue !== 'function' && !(newTitleValue instanceof Element)) {
        newTitleValue = String(newTitleValue); // Fallback to string conversion
    }

    el.bsTooltip.setContent({ '.tooltip-inner': newTitleValue });
    el.setAttribute('data-bs-original-title', typeof newTitleValue === 'function' ? newTitleValue() : newTitleValue);
  },
  beforeUnmount(el) {
    if (el.bsTooltip) {
      el.bsTooltip.dispose();
      delete el.bsTooltip;
    }
  }
});

// Add plugins
app.use(router)
app.use(ConfirmDialogPlugin)

// Mount the app
app.mount('#app')

// For debugging
console.log("Vue app initialized with ConfirmDialog plugin and Bootstrap (CDN) tooltip directive")