import { ref, computed } from 'vue';
import api from '../services/api';
import { useNotifications } from './useNotifications';

// État global partagé entre toutes les instances
const installations = ref(new Map());
const modelDownloads = ref(new Map()); // Nouveau: suivi des téléchargements de modèles
const pollingInterval = ref(null);
const modelPollingInterval = ref(null); // Nouveau: polling séparé pour les modèles

export function useInstallProgress() {
  const { showNotification, success, error } = useNotifications();

  // Démarrer une installation
  const startInstallation = async (bundleId, bundleName, profiles) => {
    const installationId = `${bundleId}_${Date.now()}`;
    
    installations.value.set(installationId, {
      bundleId,
      bundleName,
      profiles,
      status: 'starting',
      progress: 0,
      currentStep: 'Initializing installation...',
      steps: [],
      errors: [],
      startTime: Date.now()
    });

    try {
      // Démarrer l'installation pour chaque profil
      for (const profile of profiles) {
        await api.post('/bundles/install', {
          bundle_id: bundleId,
          profile: profile
        });
      }

      // Commencer le polling pour suivre la progression
      startPolling(installationId);
      
      return installationId;
    } catch (err) {
      installations.value.get(installationId).status = 'error';
      installations.value.get(installationId).errors.push(err.response?.data?.detail || err.message);
      throw err;
    }
  };

  // Démarrer le polling pour une installation
  const startPolling = (installationId) => {
    if (pollingInterval.value) return;

    pollingInterval.value = setInterval(async () => {
      try {
        await updateInstallationProgress(installationId);
      } catch (err) {
        console.error('Error polling installation progress:', err);
      }
    }, 1000); // Vérifier toutes les secondes
  };

  // Mettre à jour la progression d'une installation
  const updateInstallationProgress = async (installationId) => {
    const installation = installations.value.get(installationId);
    if (!installation || installation.status === 'completed' || installation.status === 'error') {
      return;
    }

    try {
      // Vérifier l'état des téléchargements en cours
      const downloadsResponse = await api.get('/models/downloads');
      const downloads = downloadsResponse.data || {};

      // Vérifier si le bundle est installé
      const installedResponse = await api.get('/bundles/installed/');
      const installedBundles = installedResponse.data || [];
      
      const isInstalled = installedBundles.some(b => 
        b.id === installation.bundleId && 
        installation.profiles.includes(b.profile)
      );

      // Calculer la progression basée sur les téléchargements
      const downloadKeys = Object.keys(downloads);
      const activeDownloads = downloadKeys.filter(key => 
        downloads[key].status === 'downloading'
      );

      if (activeDownloads.length > 0) {
        // Calcul de la progression moyenne des téléchargements
        const totalProgress = activeDownloads.reduce((sum, key) => 
          sum + (downloads[key].progress || 0), 0
        );
        const avgProgress = Math.floor(totalProgress / activeDownloads.length);
        
        installation.status = 'downloading';
        installation.progress = Math.min(avgProgress, 95); // Max 95% pendant le téléchargement
        installation.currentStep = `Downloading models... (${activeDownloads.length} active)`;
      } else if (isInstalled) {
        // Installation terminée
        installation.status = 'completed';
        installation.progress = 100;
        installation.currentStep = 'Installation completed successfully';
        
        // Arrêter le polling
        stopPolling();
        
        // Notification de succès
        success(`Bundle "${installation.bundleName}" installed successfully`);
        
        // Nettoyer après 5 secondes
        setTimeout(() => {
          removeInstallation(installationId);
        }, 5000);
      } else {
        // En cours d'installation
        installation.status = 'installing';
        installation.progress = Math.min(installation.progress + 1, 90);
        installation.currentStep = 'Installing models and workflows...';
      }

    } catch (err) {
      installation.status = 'error';
      installation.errors.push(err.response?.data?.detail || err.message);
      error(`Installation failed for bundle "${installation.bundleName}": ${err.message}`);
      stopPolling();
    }
  };

  // Arrêter le polling
  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
      pollingInterval.value = null;
    }
  };

  // Ajouter support pour les téléchargements de modèles individuels
  const startModelDownload = async (modelId, modelName) => {
    const downloadId = `${modelId}_${Date.now()}`;
    
    modelDownloads.value.set(downloadId, {
      modelId,
      modelName,
      status: 'downloading',
      progress: 0,
      currentStep: 'Starting download...',
      startTime: Date.now(),
      errors: []
    });

    // Démarrer le polling pour les modèles si pas déjà actif
    if (!modelPollingInterval.value) {
      startModelPolling();
    }

    return downloadId;
  };

  // Nouveau: polling spécifique pour les téléchargements de modèles
  const startModelPolling = () => {
    if (modelPollingInterval.value) return;

    modelPollingInterval.value = setInterval(async () => {
      try {
        await updateModelDownloadProgress();
      } catch (err) {
        console.error('Error polling model download progress:', err);
      }
    }, 2000);
  };

  // Nouveau: mettre à jour la progression des téléchargements de modèles
  const updateModelDownloadProgress = async () => {
    if (modelDownloads.value.size === 0) {
      stopModelPolling();
      return;
    }

    try {
      const response = await api.get('/models/downloads');
      const downloads = response.data || {};
      
      // Vérifier chaque téléchargement de modèle
      for (const [downloadId, download] of modelDownloads.value.entries()) {
        const modelProgress = downloads[download.modelId];
        
        if (modelProgress) {
          // Téléchargement en cours
          download.progress = modelProgress.progress || 0;
          download.currentStep = `Downloading... ${download.progress}%`;
          download.status = 'downloading';
        } else {
          // Téléchargement terminé ou arrêté
          download.progress = 100;
          download.status = 'completed';
          download.currentStep = 'Download completed!';
          
          showNotification(`Download completed: ${download.modelName}`, 'success');
          
          // Supprimer après 3 secondes
          setTimeout(() => {
            modelDownloads.value.delete(downloadId);
          }, 3000);
        }
      }
    } catch (error) {
      console.error('Error updating model download progress:', error);
    }
  };

  // Nouveau: arrêter le polling des modèles
  const stopModelPolling = () => {
    if (modelPollingInterval.value) {
      clearInterval(modelPollingInterval.value);
      modelPollingInterval.value = null;
    }
  };

  // Supprimer une installation
  const removeInstallation = (installationId) => {
    installations.value.delete(installationId);
    
    // Si plus d'installations, arrêter le polling
    if (installations.value.size === 0) {
      stopPolling();
    }
  };

  // Nouveau: supprimer un téléchargement de modèle
  const removeModelDownload = (downloadId) => {
    modelDownloads.value.delete(downloadId);
    
    if (modelDownloads.value.size === 0) {
      stopModelPolling();
    }
  };

  // Annuler une installation
  const cancelInstallation = (installationId) => {
    const installation = installations.value.get(installationId);
    if (installation) {
      installation.status = 'cancelled';
      installation.currentStep = 'Installation cancelled';
      
      setTimeout(() => {
        removeInstallation(installationId);
      }, 2000);
    }
  };

  // Nouveau: annuler un téléchargement de modèle
  const cancelModelDownload = async (downloadId) => {
    const download = modelDownloads.value.get(downloadId);
    if (download) {
      try {
        // Tenter d'arrêter le téléchargement côté serveur
        await api.post('/models/stop_download', { modelId: download.modelId });
        
        download.status = 'cancelled';
        download.currentStep = 'Download cancelled';
        
        setTimeout(() => {
          removeModelDownload(downloadId);
        }, 2000);
      } catch (error) {
        console.error('Error cancelling download:', error);
        showNotification('Failed to cancel download', 'error');
      }
    }
  };

  // Nouveau: restaurer les téléchargements actifs au démarrage
  const restoreActiveDownloads = async () => {
    try {
      const response = await api.get('/models/downloads');
      const downloads = response.data || {};
      
      // Pour chaque téléchargement actif, créer un indicateur de progression
      for (const [modelId, downloadInfo] of Object.entries(downloads)) {
        if (downloadInfo.status === 'downloading' && downloadInfo.progress < 100) {
          // Créer un ID unique pour ce téléchargement
          const downloadId = `${modelId}_restored_${Date.now()}`;
          
          // Essayer de récupérer le nom du modèle depuis l'API des modèles
          let modelName = modelId;
          try {
            const modelsResponse = await api.get('/models/');
            const allModels = [];
            for (const [group, entries] of Object.entries(modelsResponse.data.groups || {})) {
              allModels.push(...entries.map(m => ({ ...m, group })));
            }
            const model = allModels.find(m => (m.dest || m.git) === modelId);
            if (model) {
              modelName = model.dest?.split('/').pop() || model.git || modelId;
            }
          } catch (err) {
            console.warn('Could not fetch model name for', modelId);
          }
          
          // Ajouter le téléchargement à la liste
          modelDownloads.value.set(downloadId, {
            modelId,
            modelName,
            status: 'downloading',
            progress: downloadInfo.progress || 0,
            currentStep: `Downloading... ${downloadInfo.progress || 0}%`,
            startTime: Date.now() - 30000, // Estimation: démarré il y a 30s
            errors: []
          });
        }
      }
      
      // Démarrer le polling si des téléchargements ont été restaurés
      if (modelDownloads.value.size > 0) {
        startModelPolling();
      }
      
    } catch (error) {
      console.error('Error restoring active downloads:', error);
    }
  };

  // Getters computed mis à jour
  const activeInstallations = computed(() => {
    const bundleInstallations = Array.from(installations.value.values()).filter(
      installation => installation.status !== 'completed' && installation.status !== 'cancelled'
    );
    
    const modelDownloadsList = Array.from(modelDownloads.value.values()).map(download => ({
      bundleId: download.modelId,
      bundleName: download.modelName,
      profiles: ['download'],
      status: download.status,
      progress: download.progress,
      currentStep: download.currentStep,
      startTime: download.startTime,
      errors: download.errors
    }));
    
    return [...bundleInstallations, ...modelDownloadsList];
  });

  const hasActiveInstallations = computed(() => {
    return activeInstallations.value.length > 0;
  });

  return {
    installations: computed(() => installations.value),
    modelDownloads: computed(() => modelDownloads.value),
    activeInstallations,
    hasActiveInstallations,
    startInstallation,
    cancelInstallation,
    removeInstallation,
    startModelDownload,
    cancelModelDownload,
    removeModelDownload,
    restoreActiveDownloads
  };
}
