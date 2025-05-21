import { ref, h, watch } from 'vue';

// Create a singleton instance for the dialog service
const singleton = {
  isVisible: ref(false),
  resolvePromise: ref(null),
  options: ref({
    title: 'Confirmation',
    message: 'Are you sure?',
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
    hideCancel: false,
    isPrompt: false, // New: indicates if it's a prompt
    promptInitialValue: '', // New: initial value for prompt input
    promptPlaceholder: '', // New: placeholder for prompt input
  }),
  // Store the current prompt input value separately, as options might be reset
  // This will be updated by the ConfirmDialog component via an event or direct binding if possible
  // For simplicity with GlobalConfirmDialog, we'll have ConfirmDialog manage its internal state
  // and pass the value back on confirm.
};

// Composant de dialogue simple
const ConfirmDialog = {
  name: 'ConfirmDialog',
  props: {
    modelValue: Boolean,
    title: String,
    message: String,
    confirmLabel: {
      type: String,
      default: 'Confirm'
    },
    cancelLabel: {
      type: String,
      default: 'Cancel'
    },
    hideCancel: {
      type: Boolean,
      default: false
    },
    isPrompt: { // New prop
      type: Boolean,
      default: false
    },
    promptInitialValue: { // New prop
      type: String,
      default: ''
    },
    promptPlaceholder: { // New prop
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'confirm', 'cancel'],
  setup(props, { emit }) {
    const internalPromptValue = ref('');

    watch(() => props.modelValue, (newValue) => {
      if (newValue && props.isPrompt) {
        internalPromptValue.value = props.promptInitialValue;
      }
    }, { immediate: true });
    
    watch(() => props.promptInitialValue, (newValue) => {
        if (props.isPrompt) {
            internalPromptValue.value = newValue;
        }
    });

    const handleConfirm = () => {
      emit('update:modelValue', false);
      if (props.isPrompt) {
        emit('confirm', internalPromptValue.value);
      } else {
        emit('confirm');
      }
    };

    const handleCancel = () => {
      emit('update:modelValue', false);
      emit('cancel');
    };

    // Focus input when dialog becomes visible and is a prompt
    const promptInputRef = ref(null);
    watch(() => [props.modelValue, props.isPrompt], ([newModelValue, newIsPrompt]) => {
      if (newModelValue && newIsPrompt) {
        setTimeout(() => { // Ensure element is in DOM
          promptInputRef.value?.focus();
        }, 0);
      }
    });

    return { handleConfirm, handleCancel, internalPromptValue, promptInputRef };
  },
  template: `
    <div v-if="modelValue" class="modal-overlay" @click.self="handleCancel">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" @click="handleCancel" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>{{ message }}</p>
          <input 
            v-if="isPrompt" 
            ref="promptInputRef"
            type="text" 
            class="form-control mt-2" 
            v-model="internalPromptValue" 
            :placeholder="promptPlaceholder"
            @keyup.enter="handleConfirm"
          />
        </div>
        <div class="modal-footer">
          <button v-if="!hideCancel" type="button" class="btn btn-secondary" @click="handleCancel">
            {{ cancelLabel }}
          </button>
          <button type="button" class="btn btn-primary" @click="handleConfirm">
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  `
};

// Service de dialogue
export function useConfirm() {
  const reveal = (dialogOptions) => {
    console.log("Dialog reveal called with options:", dialogOptions);
    return new Promise((resolve) => {
      singleton.options.value = {
        // Reset to defaults first, then apply new options
        title: 'Confirmation',
        message: 'Are you sure?',
        confirmLabel: 'Confirm',
        cancelLabel: 'Cancel',
        hideCancel: false,
        isPrompt: false,
        promptInitialValue: '',
        promptPlaceholder: '',
        ...dialogOptions // Apply incoming options
      };
      
      singleton.isVisible.value = true;
      singleton.resolvePromise.value = resolve;
      console.log("Dialog should now be visible", singleton.isVisible.value, "Prompt mode:", singleton.options.value.isPrompt);
    });
  };

  const confirm = (dialogOptions = {}) => {
    console.log("Confirm dialog requested with options:", dialogOptions);
    return reveal({
      ...dialogOptions,
      isPrompt: false, // Ensure isPrompt is false for confirm
      hideCancel: false
    });
  };

  const alert = (dialogOptions = {}) => {
    console.log("Alert dialog requested with options:", dialogOptions);
    return reveal({
      ...dialogOptions,
      isPrompt: false, // Ensure isPrompt is false for alert
      hideCancel: true
    });
  };

  const prompt = (dialogOptions = {}) => { // New prompt function
    console.log("Prompt dialog requested with options:", dialogOptions);
    return reveal({
      ...dialogOptions,
      isPrompt: true,
      hideCancel: false, // Usually prompts have a cancel
      confirmLabel: dialogOptions.confirmLabel || 'OK',
      cancelLabel: dialogOptions.cancelLabel || 'Cancel',
    });
  };

  // handleConfirm and handleCancel in GlobalConfirmDialog will now receive inputValue if it's a prompt
  // So, these specific handlers in useConfirm are mostly for the GlobalConfirmDialog's setup
  // The actual promise resolution happens within GlobalConfirmDialog's handlers.

  return {
    isVisible: singleton.isVisible, // For GlobalConfirmDialog to watch
    options: singleton.options,     // For GlobalConfirmDialog to pass as props
    confirm, // Exported for direct use
    alert,   // Exported for direct use
    prompt,  // Exported for direct use
    // reveal is internal, handleConfirm/handleCancel are now primarily managed by GlobalConfirmDialog's setup
  };
}

// Composant global qui gère le dialogue
const GlobalConfirmDialog = {
  setup() {
    const handleConfirm = (promptInputValue) => {
      console.log("GlobalConfirmDialog: handleConfirm called. Prompt mode:", singleton.options.value.isPrompt, "Input:", promptInputValue);
      if (singleton.resolvePromise.value) {
        if (singleton.options.value.isPrompt) {
          singleton.resolvePromise.value(promptInputValue); // Resolve with input value for prompts
        } else {
          singleton.resolvePromise.value(true); // Resolve with true for confirms
        }
        singleton.resolvePromise.value = null;
      }
      singleton.isVisible.value = false;
    };

    const handleCancel = () => {
      console.log("GlobalConfirmDialog: handleCancel called. Prompt mode:", singleton.options.value.isPrompt);
      if (singleton.resolvePromise.value) {
        if (singleton.options.value.isPrompt) {
          singleton.resolvePromise.value(null); // Resolve with null for canceled prompts
        } else {
          singleton.resolvePromise.value(false); // Resolve with false for canceled confirms
        }
        singleton.resolvePromise.value = null;
      }
      singleton.isVisible.value = false;
    };
    
    return {
      isVisible: singleton.isVisible,
      options: singleton.options,
      handleConfirm,
      handleCancel
    };
  },
  render() {
    console.log("GlobalConfirmDialog rendering, isVisible:", this.isVisible, "options:", this.options);
    if (!this.isVisible) {
      return null; 
    }
    return h(ConfirmDialog, {
      modelValue: this.isVisible,
      // 'onUpdate:modelValue': (value) => this.isVisible = value, // isVisible is directly from singleton
      title: this.options.title,
      message: this.options.message,
      confirmLabel: this.options.confirmLabel,
      cancelLabel: this.options.cancelLabel,
      hideCancel: this.options.hideCancel,
      isPrompt: this.options.isPrompt, // Pass new props
      promptInitialValue: this.options.promptInitialValue,
      promptPlaceholder: this.options.promptPlaceholder,
      onConfirm: this.handleConfirm, // Will receive input value if prompt
      onCancel: this.handleCancel
    });
  }
};

// Plugin Vue
export const ConfirmDialogPlugin = {
  install: (app) => {
    app.component('GlobalConfirmDialog', GlobalConfirmDialog);
    
    const dialogService = useConfirm();

    app.config.globalProperties.$confirm = (message, title = 'Confirmation', options = {}) => {
      return dialogService.confirm({ title, message, ...options });
    };
    
    app.config.globalProperties.$alert = (message, title = 'Alert', options = {}) => {
      return dialogService.alert({ title, message, ...options });
    };

    app.config.globalProperties.$prompt = (message, title = 'Prompt', options = {}) => { // New global prompt
      return dialogService.prompt({ title, message, ...options });
    };
  }
};

// Export du plugin par défaut
export default {
  install(app) {
    // Register the plugin which in turn registers GlobalConfirmDialog
    // and global properties.
    app.use(ConfirmDialogPlugin);
    // ConfirmDialog is used internally by GlobalConfirmDialog,
    // no need to register it globally unless used directly elsewhere.
    // app.component('ConfirmDialog', ConfirmDialog); 
  }
};

// CSS pour le dialogue (sera injecté dans le composant)
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.75); /* Adjusted for semi-transparency */
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }
    .modal-content {
      background-color: #2b3e50;
      color: #fff;
      border-radius: 6px;
      max-width: 500px;
      width: 100%;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
    }
    .modal-header {
      padding: 1rem;
      border-bottom: 1px solid #4e5d6c;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-body {
      padding: 1.5rem;
    }
    .modal-footer {
      padding: 1rem;
      border-top: 1px solid #4e5d6c;
      display: flex;
      justify-content: flex-end;
      gap: 0.5rem;
    }
    .btn-close {
      filter: invert(1) grayscale(100%) brightness(200%);
    }
  `;
  document.head.appendChild(style);
}
