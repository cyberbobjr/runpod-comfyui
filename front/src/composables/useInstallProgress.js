import { ref, computed } from 'vue';
import api from '../services/api';
import { useNotifications } from './useNotifications';

// État global partagé entre toutes les instances
const installations = ref(new Map());
const modelDownloads = ref(new Map()); // Nouveau: suivi des téléchargements de modèles
const rawDownloads = ref({}); // Nouveau: données brutes de l'API /downloads
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
      const downloadsResponse = await api.get('/downloads/');
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
    console.log(`Starting download tracking for ${modelId}`);
    
    // S'assurer que le polling est actif
    startGlobalDownloadPolling();
    
    return modelId; // Retourner l'ID du modèle
  };  // Nouveau: polling spécifique pour les téléchargements de modèles
  const startModelPolling = () => {
    if (modelPollingInterval.value) {
      console.log('Model polling already running, interval ID:', modelPollingInterval.value);
      return;
    }

    console.log('Starting model polling - setting up interval');
    modelPollingInterval.value = setInterval(async () => {
      try {
        await updateModelDownloadProgress();
      } catch (err) {
        console.error('Error polling model download progress:', err);
      }
    }, 2000); // Fréquence alignée avec l'ancien polling du DownloadModelsComponent
    
    console.log('Model polling started with interval ID:', modelPollingInterval.value);
  };
  // Nouveau: mettre à jour la progression des téléchargements de modèles
  const updateModelDownloadProgress = async () => {
    try {
      console.log('Polling /downloads...');
      const response = await api.get('/downloads');
      const downloads = response.data || {};
      
      console.log('Current downloads from API:', Object.keys(downloads).length, 'items');
      
      // Mettre à jour les données brutes pour que d'autres composants puissent les utiliser
      rawDownloads.value = downloads;
        // Pour chaque téléchargement détecté par l'API
      for (const [modelId, downloadInfo] of Object.entries(downloads)) {
        console.log(`Processing download ${modelId}:`, downloadInfo.status, downloadInfo.progress + '%');
        
        // Traiter les téléchargements en cours
        if (downloadInfo.status === 'downloading' || (downloadInfo.progress < 100 && downloadInfo.status !== 'stopped')) {
          // Vérifier si on a déjà une entrée pour ce modèle
          let found = false;
          for (const [downloadId, download] of modelDownloads.value.entries()) {
            if (download.modelId === modelId) {
              // Mettre à jour l'entrée existante
              download.progress = downloadInfo.progress || 0;
              download.currentStep = `Downloading... ${download.progress}%`;
              download.status = 'downloading';
              found = true;
              break;
            }
          }
          
          // Si pas trouvé, créer une nouvelle entrée
          if (!found) {
            const downloadId = `${modelId}_detected_${Date.now()}`;
            
            // Essayer de récupérer le nom du modèle
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
            
            modelDownloads.value.set(downloadId, {
              modelId,
              modelName,
              status: 'downloading',
              progress: downloadInfo.progress || 0,
              currentStep: `Downloading... ${downloadInfo.progress || 0}%`,
              startTime: Date.now(),
              errors: []            });
          }
        }
        // Traiter les téléchargements arrêtés par le backend
        else if (downloadInfo.status === 'stopped') {
          // Trouver l'entrée correspondante et la marquer comme cancelled
          for (const [downloadId, download] of modelDownloads.value.entries()) {
            if (download.modelId === modelId && download.status !== 'cancelled') {
              download.status = 'cancelled';
              download.currentStep = 'Download cancelled';
              download.progress = downloadInfo.progress || download.progress; // Garder le progress actuel
              
              console.log(`Download ${modelId} marked as cancelled due to backend status 'stopped'`);
              
              showNotification(`Download cancelled: ${download.modelName}`, 'info');
              
              // Supprimer après 3 secondes
              setTimeout(() => {
                modelDownloads.value.delete(downloadId);
              }, 3000);
              break;
            }
          }
        }
      }
        // Nettoyer les téléchargements terminés ou qui n'existent plus
      for (const [downloadId, download] of modelDownloads.value.entries()) {
        const apiDownload = downloads[download.modelId];
        
        if (!apiDownload) {
          // Le téléchargement a disparu de l'API
          // Vérifier si on l'a déjà marqué comme cancelled localement
          if (download.status === 'cancelled') {
            // Ne rien faire, il est déjà marqué comme cancelled
            console.log(`Download ${download.modelId} already marked as cancelled`);
          } else {
            // Si ce n'était pas cancelled, alors c'est vraiment terminé
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
      }
        // Arrêter le polling s'il n'y a plus rien à surveiller
      if (Object.keys(downloads).length === 0 && modelDownloads.value.size === 0) {
        console.log('No downloads detected, attempting to stop polling');
        stopModelPolling();
      } else {
        console.log('Continuing polling - downloads found:', Object.keys(downloads).length, 'managed:', modelDownloads.value.size);
      }
      
    } catch (error) {
      console.error('Error updating model download progress:', error);
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
        removeInstallation(installationId);      }, 2000);
    }
  };

  // Nouveau: annuler un téléchargement de modèle
  const cancelModelDownload = async (downloadId) => {
    // downloadId peut être soit l'ID généré, soit directement l'ID du modèle
    let download = modelDownloads.value.get(downloadId);
    let actualModelId = downloadId;
    
    if (download) {
      actualModelId = download.modelId;
    } else {
      // Si on ne trouve pas le download avec l'ID, c'est peut-être l'ID du modèle directement
      for (const [id, dl] of modelDownloads.value.entries()) {
        if (dl.modelId === downloadId) {
          download = dl;
          downloadId = id;
          actualModelId = dl.modelId;
          break;
        }
      }
    }
    
    if (download) {
      try {
        // Tenter d'arrêter le téléchargement côté serveur
        // Utiliser l'endpoint correct pour arrêter le téléchargement
        await api.post('/models/stop_download', { 
          model_id: actualModelId,
          dest: actualModelId,
          git: actualModelId
        });
        
        download.status = 'cancelled';
        download.currentStep = 'Download cancelled';
        
        showNotification(`Download cancelled: ${download.modelName}`, 'info');
        
        setTimeout(() => {
          removeModelDownload(downloadId);
        }, 2000);
      } catch (error) {
        console.error('Error cancelling download:', error);
        showNotification('Failed to cancel download', 'error');
        
        // En cas d'erreur de l'API, on marque quand même comme annulé localement
        download.status = 'cancelled';
        download.currentStep = 'Download cancelled (forced)';
        
        setTimeout(() => {
          removeModelDownload(downloadId);
        }, 2000);
      }
    } else {      console.warn('Download not found for cancellation:', downloadId);
    }
  };

  // Nouveau: restaurer les téléchargements actifs au démarrage
  const restoreActiveDownloads = async () => {
    try {
      const response = await api.get('/downloads');
      const downloads = response.data || {};
      
      // Pour chaque téléchargement actif, créer un indicateur de progression
      for (const [modelId, downloadInfo] of Object.entries(downloads)) {
        if (downloadInfo.status === 'downloading' && downloadInfo.progress < 100) {
          // Vérifier si ce téléchargement existe déjà pour éviter les doublons
          let alreadyExists = false;
          for (const [existingId, existingDownload] of modelDownloads.value.entries()) {
            if (existingDownload.modelId === modelId) {
              alreadyExists = true;
              break;
            }
          }
          
          if (alreadyExists) {
            console.log(`Download already exists for ${modelId}, skipping restore`);
            continue;
          }
          
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
            startTime: Date.now() - 30000, // Estimation: démarré il y a 30s            errors: []
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
    
    const modelDownloadsList = Array.from(modelDownloads.value.entries()).map(([downloadId, download]) => ({
      downloadId, // Ajouter l'ID réel du download
      bundleId: download.modelId,
      bundleName: download.modelName,
      profiles: ['download'],
      status: download.status,
      progress: download.progress,
      currentStep: download.currentStep,
      startTime: download.startTime,
      errors: download.errors    }));
    
    return [...bundleInstallations, ...modelDownloadsList];
  });

  const hasActiveInstallations = computed(() => {
    return activeInstallations.value.length > 0;
  });
  // Nouveau: fonction pour forcer une mise à jour des téléchargements
  const refreshDownloads = async () => {
    try {
      const response = await api.get('/downloads');
      rawDownloads.value = response.data || {};
      return rawDownloads.value;
    } catch (error) {
      console.error('Error refreshing downloads:', error);
      rawDownloads.value = {};
      return {};
    }
  };  // Nouveau: démarrer le polling même s'il n'y a pas de téléchargements gérés
  const startGlobalDownloadPolling = () => {
    if (!modelPollingInterval.value) {
      console.log('Starting global download polling from startGlobalDownloadPolling');
      startModelPolling();
    } else {
      console.log('Global download polling already active');
    }
  };

  // Nouveau: arrêter le polling seulement s'il n'y a vraiment aucun téléchargement
  const stopModelPolling = () => {
    // Vérifier s'il y a des téléchargements actifs dans rawDownloads
    const hasActiveDownloads = Object.values(rawDownloads.value).some(
      download => download.status === 'downloading' && download.progress < 100
    );
    
    // Ne stopper que s'il n'y a aucun téléchargement ET aucun download géré
    if (!hasActiveDownloads && modelDownloads.value.size === 0) {
      console.log('Stopping model polling - no active downloads');
      if (modelPollingInterval.value) {
        clearInterval(modelPollingInterval.value);
        modelPollingInterval.value = null;
      }
    } else {
      console.log('Keeping polling active - downloads found:', Object.keys(rawDownloads.value).length, 'managed:', modelDownloads.value.size);
    }
  };
  return {
    installations: computed(() => installations.value),
    modelDownloads: computed(() => modelDownloads.value),
    rawDownloads: computed(() => rawDownloads.value), // Nouveau: exposer les données brutes
    activeInstallations,
    hasActiveInstallations,
    startInstallation,
    cancelInstallation,
    removeInstallation,
    startModelDownload,
    cancelModelDownload,
    removeModelDownload,
    restoreActiveDownloads,
    refreshDownloads, // Nouveau: fonction pour rafraîchir les téléchargements
    startGlobalDownloadPolling // Nouveau: démarrer le polling global
  };
}
