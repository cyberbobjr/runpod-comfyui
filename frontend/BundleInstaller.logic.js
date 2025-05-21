import { ref, computed, onMounted, watch } from 'vue';
import { 
  apiFetch, formatSize, models as allModels,
  groupedModels
} from './App.logic.js';
import { useConfirm } from './plugins/confirm-dialog';

export function useBundleInstallerLogic() {
  // State
  const bundles = ref({});
  const installedBundles = ref([]);
  const selectedBundle = ref('');
  const selectedProfile = ref('');
  const isInstalling = ref(false);
  const isUninstalling = ref(false);
  const isUninstallingMap = ref({});
  const averageDownloadSpeed = ref(5 * 1024 * 1024); // 5MB/s default

  // Dialog handlers
  const { confirm, alert } = useConfirm();

  // Computed properties
  const selectedBundleDetails = computed(() => {
    if (!selectedBundle.value) return null;
    return bundles.value[selectedBundle.value];
  });

  const selectedBundleProfiles = computed(() => {
    if (!selectedBundleDetails.value) return {};
    return selectedBundleDetails.value.hardware_profiles || {};
  });

  const bundleKey = computed(() => {
    if (!selectedBundle.value || !selectedProfile.value) return '';
    return `${selectedBundle.value}:${selectedProfile.value}`;
  });

  const bundleModelsList = computed(() => {
    if (!selectedBundleDetails.value || !selectedProfile.value) return [];
    const result = [];
    const profileFilters = selectedBundleProfiles.value[selectedProfile.value]?.model_filters || {
      include_tags: [],
      exclude_tags: []
    };
    const matchesFilter = (model) => {
      const modelTags = model.entry.tags || [];
      const tagsArray = Array.isArray(modelTags) ? modelTags : [modelTags];
      if (profileFilters.exclude_tags.length > 0) {
        if (profileFilters.exclude_tags.some(tag => tagsArray.includes(tag))) {
          return false;
        }
      }
      if (profileFilters.include_tags.length > 0) {
        return profileFilters.include_tags.some(tag => tagsArray.includes(tag));
      }
      return true;
    };
    selectedBundleDetails.value.models.forEach(groupName => {
      const modelsInGroup = groupedModels.value[groupName] || [];
      modelsInGroup.forEach(model => {
        if (matchesFilter(model)) {
          result.push({
            path: model.entry.dest || model.entry.git,
            exists: model.exists,
            size: model.entry.size || 0,
            tags: model.entry.tags || []
          });
        }
      });
    });
    return result;
  });

  const totalDownloadSize = computed(() => {
    return bundleModelsList.value
      .filter(model => !model.exists)
      .reduce((total, model) => total + (model.size || 0), 0);
  });

  const estimatedDownloadTime = computed(() => {
    if (!totalDownloadSize.value || !averageDownloadSpeed.value) return null;
    const seconds = totalDownloadSize.value / averageDownloadSpeed.value;
    if (seconds < 60) return `${Math.round(seconds)} seconds`;
    if (seconds < 3600) return `${Math.round(seconds / 60)} minutes`;
    return `${Math.round(seconds / 3600 * 10) / 10} hours`;
  });

  const installedBundlesList = computed(() => {
    return installedBundles.value.map(key => {
      const [bundleName, profileName] = key.split(':');
      let completeStatus = false;
      if (bundles.value[bundleName]) {
        const bundle = bundles.value[bundleName];
        const profile = bundle.hardware_profiles[profileName];
        if (bundle && profile) {
          let allModelsInstalled = true;
          let hasModels = false;
          bundle.models.forEach(groupName => {
            const modelsInGroup = groupedModels.value[groupName] || [];
            modelsInGroup.forEach(model => {
              const modelTags = model.entry.tags || [];
              const tagsArray = Array.isArray(modelTags) ? modelTags : [modelTags];
              let matchesFilter = true;
              if (profile.model_filters.exclude_tags?.length > 0) {
                if (profile.model_filters.exclude_tags.some(tag => tagsArray.includes(tag))) {
                  matchesFilter = false;
                }
              }
              if (matchesFilter && profile.model_filters.include_tags?.length > 0) {
                matchesFilter = profile.model_filters.include_tags.some(tag => tagsArray.includes(tag));
              }
              if (matchesFilter) {
                hasModels = true;
                if (!model.exists) {
                  allModelsInstalled = false;
                }
              }
            });
          });
          completeStatus = hasModels && allModelsInstalled;
        }
      }
      return {
        key,
        bundleName,
        profileName,
        completeStatus
      };
    });
  });

  // Methods
  const loadBundles = async () => {
    try {
      const response = await apiFetch('/jsonmodels/bundles');
      if (response.ok) {
        bundles.value = await response.json();
      }
    } catch (error) {
      console.error('Failed to load bundles:', error);
    }
  };

  const loadInstalledBundles = async () => {
    try {
      const response = await apiFetch('/jsonmodels/installed-bundles');
      if (response.ok) {
        installedBundles.value = await response.json() || [];
      } else {
        installedBundles.value = [];
      }
    } catch (error) {
      console.error('Failed to load installed bundles:', error);
      installedBundles.value = [];
    }
  };

  const installBundle = async () => {
    if (!selectedBundle.value || !selectedProfile.value || isInstalling.value) return;
    try {
      isInstalling.value = true;
      const missingModels = bundleModelsList.value.filter(model => !model.exists);
      if (missingModels.length > 0) {
        const confirmed = await confirm({
          title: 'Confirm Download',
          message: `This will download ${missingModels.length} missing models (${formatSize(totalDownloadSize.value)}). Continue?`,
          confirmLabel: 'Download',
          cancelLabel: 'Cancel'
        });
        if (!confirmed) {
          isInstalling.value = false;
          return;
        }
      }
      // Appel API pour installer le bundle (côté serveur, installation réelle)
      const response = await apiFetch('/jsonmodels/install-bundle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }, // <-- Ajouté
        body: JSON.stringify({
          bundle: selectedBundle.value,
          profile: selectedProfile.value
        })
      });
      if (!response.ok) throw new Error('Failed to install bundle');
      await loadInstalledBundles();
    } catch (error) {
      console.error('Failed to install bundle:', error);
      await alert({
        title: 'Installation Error',
        message: 'Failed to install bundle. See console for details.',
        confirmLabel: 'OK',
        hideCancel: true
      });
    } finally {
      isInstalling.value = false;
    }
  };

  const uninstallBundle = () => {
    uninstallBundleByKey(bundleKey.value);
  };

  const uninstallBundleByKey = async (key) => {
    if (!key || isUninstallingMap.value[key]) return;
    const [bundleName, profileName] = key.split(':');
    const confirmed = await confirm({
      title: 'Confirm Uninstallation',
      message: `Are you sure you want to uninstall the bundle "${bundleName}" with profile "${profileName}"?`,
      confirmLabel: 'Uninstall',
      cancelLabel: 'Cancel'
    });
    if (!confirmed) return;
    try {
      isUninstallingMap.value[key] = true;
      // Appel API pour désinstaller le bundle (côté serveur, suppression réelle)
      const response = await apiFetch('/jsonmodels/uninstall-bundle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }, // <-- Ajouté
        body: JSON.stringify({
          bundle: bundleName,
          profile: profileName
        })
      });
      if (!response.ok) throw new Error('Failed to uninstall bundle');
      await loadInstalledBundles();
    } catch (error) {
      console.error('Failed to uninstall bundle:', error);
      await alert({
        title: 'Uninstallation Error',
        message: 'Failed to uninstall bundle. See console for details.',
        confirmLabel: 'OK',
        hideCancel: true
      });
    } finally {
      isUninstallingMap.value[key] = false;
    }
  };

  const bundleWorkflows = computed(() => {
    if (!selectedBundleDetails.value) return [];
    if (selectedBundleDetails.value.workflows) {
      return selectedBundleDetails.value.workflows;
    } else if (selectedBundleDetails.value.workflow) {
      return [selectedBundleDetails.value.workflow];
    }
    return [];
  });

  const getModelName = (path) => {
    if (!path) return 'Unknown';
    const parts = path.split('/');
    return parts[parts.length - 1];
  };

  const isNSFW = (model) => {
    const tags = model.tags;
    if (!tags) return false;
    if (Array.isArray(tags)) return tags.map(t => t.toLowerCase()).includes('nsfw');
    if (typeof tags === 'string') return tags.toLowerCase().includes('nsfw');
    return false;
  };

  const getBundleWorkflows = (bundleName) => {
    const bundle = bundles.value[bundleName];
    if (!bundle) return [];
    if (bundle.workflows) {
      return bundle.workflows;
    } else if (bundle.workflow) {
      return [bundle.workflow];
    }
    return [];
  };

  const bundleHasWorkflows = (bundleName) => {
    return getBundleWorkflows(bundleName).length > 0;
  };

  const downloadWorkflow = async (workflowName) => {
    if (!workflowName) return;
    try {
      const token = localStorage.getItem('token');
      const headers = {};
      if (token) {
        headers['Authorization'] = 'Bearer ' + token;
      }
      const response = await fetch(`/api/jsonmodels/workflow/${encodeURIComponent(workflowName)}?download=true`, {
        headers
      });
      if (!response.ok) throw new Error('Failed to fetch workflow');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = workflowName.endsWith('.json') ? workflowName : `${workflowName}.json`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 100);
    } catch (error) {
      console.error('Failed to download workflow:', error);
      alert('Failed to download workflow.');
    }
  };

  const downloadAllWorkflows = async (bundleName) => {
    const workflows = getBundleWorkflows(bundleName);
    if (workflows.length === 0) return;
    workflows.forEach(workflow => {
      setTimeout(() => downloadWorkflow(workflow), 250);
    });
  };

  watch([selectedBundle], () => {
    selectedProfile.value = '';
  });

  onMounted(async () => {
    await Promise.all([
      loadBundles(),
      loadInstalledBundles()
    ]);
  });

  return {
    bundles,
    installedBundles,
    selectedBundle,
    selectedProfile,
    isInstalling,
    isUninstalling,
    isUninstallingMap,
    averageDownloadSpeed,
    confirm,
    alert,
    selectedBundleDetails,
    selectedBundleProfiles,
    bundleKey,
    bundleModelsList,
    totalDownloadSize,
    estimatedDownloadTime,
    installedBundlesList,
    loadBundles,
    loadInstalledBundles,
    installBundle,
    uninstallBundle,
    uninstallBundleByKey,
    bundleWorkflows,
    getModelName,
    isNSFW,
    getBundleWorkflows,
    bundleHasWorkflows,
    downloadWorkflow,
    downloadAllWorkflows,
    formatSize
  };
}
