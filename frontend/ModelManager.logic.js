import {
    apiFetch, groupedModels
} from './App.logic.js';

import { ref, computed } from 'vue';
import { useConfirm } from './plugins/confirm-dialog';

// Dialog handlers
const { confirm, alert } = useConfirm();

// Bundle management
export const bundles = ref({});
export const workflows = ref([]);
export const currentBundle = ref({
    name: '',
    bundle: {
        description: '',
        workflows: [], // Changed from workflow: '' to workflows: []
        models: [],
        hardware_profiles: {
            'high-end': {
                description: 'For powerful GPUs (24GB+ VRAM)',
                model_filters: {
                    include_tags: [],
                    exclude_tags: ['fp8', 'gguf']
                }
            },
            'mid-tier': {
                description: 'For mid-range GPUs (12-16GB VRAM)',
                model_filters: {
                    include_tags: ['fp8'],
                    exclude_tags: ['gguf']
                }
            },
            'low-end': {
                description: 'For GPUs with limited VRAM (<12GB)',
                model_filters: {
                    include_tags: ['gguf'],
                    exclude_tags: []
                }
            }
        },
        workflow_params: {}
    }
});

// Load bundles
export const loadBundles = async () => {
    try {
        const response = await apiFetch('/jsonmodels/bundles');
        if (response.ok) {
            bundles.value = await response.json();
        }
    } catch (error) {
        console.error('Failed to load bundles:', error);
    }
};

// Load workflows
export const loadWorkflows = async () => {
    try {
        const response = await apiFetch('/jsonmodels/workflows');
        if (response.ok) {
            workflows.value = await response.json();
        } else {
            workflows.value = [];
        }
    } catch (error) {
        console.error('Failed to load workflows:', error);
        workflows.value = [];
    }
};

// Save bundle
export const saveBundle = async () => {
    try {
        if (!currentBundle.value.name) {
            await alert({
                title: 'Validation Error',
                message: 'Bundle name is required',
                confirmLabel: 'OK',
                hideCancel: true
            });
            return;
        }
        
        if (currentBundle.value.bundle.workflows.length === 0) {
            await alert({
                title: 'Validation Error',
                message: 'At least one workflow file is required',
                confirmLabel: 'OK',
                hideCancel: true
            });
            return;
        }
        
        if (currentBundle.value.bundle.models.length === 0) {
            await alert({
                title: 'Validation Error',
                message: 'At least one model group is required',
                confirmLabel: 'OK',
                hideCancel: true
            });
            return;
        }
        
        const method = bundles.value[currentBundle.value.name] ? 'PUT' : 'POST';
        const response = await apiFetch('/jsonmodels/bundle', {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentBundle.value)
        });
        
        if (response.ok) {
            const data = await response.json();
            await alert({
                title: 'Success',
                message: data.message,
                confirmLabel: 'OK',
                hideCancel: true
            });
            await loadBundles();
            resetBundleForm();
        }
    } catch (error) {
        console.error('Failed to save bundle:', error);
        await alert({
            title: 'Error',
            message: 'Failed to save bundle',
            confirmLabel: 'OK',
            hideCancel: true
        });
    }
};

// Delete bundle
export const deleteBundle = async (name) => {
    const confirmed = await confirm({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete bundle "${name}"?`,
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel'
    });
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await apiFetch('/jsonmodels/bundle', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bundle_name: name })
        });
        
        if (response.ok) {
            const data = await response.json();
            await alert({
                title: 'Success',
                message: data.message,
                confirmLabel: 'OK',
                hideCancel: true
            });
            await loadBundles();
        }
    } catch (error) {
        console.error('Failed to delete bundle:', error);
        await alert({
            title: 'Error',
            message: 'Failed to delete bundle',
            confirmLabel: 'OK',
            hideCancel: true
        });
    }
};

// Edit bundle
export const editBundle = (name) => {
    const bundle = bundles.value[name];
    if (bundle) {
        // Handle backward compatibility for workflows
        let workflowsArray = [];
        if (bundle.workflows) {
            workflowsArray = Array.isArray(bundle.workflows) ? bundle.workflows : [bundle.workflows];
        } else if (bundle.workflow) {
            workflowsArray = [bundle.workflow];
        }
        
        currentBundle.value = {
            name,
            bundle: {
                description: bundle.description || '',
                workflows: workflowsArray,
                models: [...(bundle.models || [])],
                hardware_profiles: JSON.parse(JSON.stringify(bundle.hardware_profiles || {})),
                workflow_params: bundle.workflow_params ? JSON.parse(JSON.stringify(bundle.workflow_params)) : undefined
            }
        };
    }
};

// Reset bundle form
export const resetBundleForm = () => {
    currentBundle.value = {
        name: '',
        bundle: {
            description: '',
            workflows: [], // Changed from workflow: '' to workflows: []
            models: [],
            hardware_profiles: {
                'high-end': {
                    description: 'For powerful GPUs (24GB+ VRAM)',
                    model_filters: {
                        include_tags: [],
                        exclude_tags: ['fp8', 'gguf']
                    }
                },
                'mid-tier': {
                    description: 'For mid-range GPUs (12-16GB VRAM)',
                    model_filters: {
                        include_tags: ['fp8'],
                        exclude_tags: ['gguf']
                    }
                },
                'low-end': {
                    description: 'For GPUs with limited VRAM (<12GB)',
                    model_filters: {
                        include_tags: ['gguf'],
                        exclude_tags: []
                    }
                }
            },
            workflow_params: {}
        }
    };
};

// Upload workflow file
export const uploadWorkflow = async (file) => {
    try {
        const formData = new FormData();
        formData.append('workflow_file', file);
        
        const response = await apiFetch('/jsonmodels/workflow', {
            method: 'POST',
            body: formData
            // Note: No need to set Content-Type for FormData, browser will set it automatically
        });
        
        if (response.ok) {
            const data = await response.json();
            await alert({
                title: 'Success',
                message: data.message,
                confirmLabel: 'OK',
                hideCancel: true
            });
            await loadWorkflows();
        }
    } catch (error) {
        console.error('Failed to upload workflow:', error);
        await alert({
            title: 'Error',
            message: 'Failed to upload workflow',
            confirmLabel: 'OK',
            hideCancel: true
        });
    }
};

// Delete workflow file
export const deleteWorkflow = async (filename) => {
    const confirmed = await confirm({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete workflow "${filename}"?`,
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel'
    });
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await apiFetch(`/jsonmodels/workflow/${filename}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            const data = await response.json();
            await alert({
                title: 'Success',
                message: data.message,
                confirmLabel: 'OK',
                hideCancel: true
            });
            await loadWorkflows();
        }
    } catch (error) {
        console.error('Failed to delete workflow:', error);
        await alert({
            title: 'Error',
            message: 'Failed to delete workflow',
            confirmLabel: 'OK',
            hideCancel: true
        });
    }
};

// Add hardware profile
export const addHardwareProfile = async () => {
    // Create a custom input dialog
    const name = prompt('Enter hardware profile name:');
    if (name && !currentBundle.value.bundle.hardware_profiles[name]) {
        currentBundle.value.bundle.hardware_profiles[name] = {
            description: '',
            model_filters: {
                include_tags: [],
                exclude_tags: []
            }
        };
    }
};

// Remove hardware profile
export const removeHardwareProfile = async (name) => {
    const confirmed = await confirm({
        title: 'Confirm Removal',
        message: `Remove hardware profile "${name}"?`,
        confirmLabel: 'Remove',
        cancelLabel: 'Cancel'
    });
    
    if (confirmed) {
        delete currentBundle.value.bundle.hardware_profiles[name];
    }
};

// Export only the bundle management related functions
export { groupedModels, confirm, alert };
