# Stores Documentation

Ce dossier contient tous les stores Pinia utilisés dans l'application ComfyUI. Les stores gèrent l'état global de l'application et fournissent des actions pour manipuler les données.

# Stores Documentation

Ce dossier contient tous les stores Pinia utilisés dans l'application ComfyUI. Les stores gèrent l'état global de l'application et fournissent des actions pour manipuler les données.

## Structure des Stores

### 📊 Models Store (`models.js`)
**Description:** Gère les modèles AI disponibles et installés.
**Responsabilités:**
- Chargement et gestion des modèles AI
- Opérations de téléchargement et installation
- Sélection et filtrage des modèles
- Gestion du statut de téléchargement

**Principales actions:**
- `fetchModels()` - Charge les modèles depuis l'API
- `downloadModel(model)` - Télécharge un modèle spécifique
- `toggleModelSelection(model)` - Sélectionner/désélectionner un modèle
- `searchModels(query)` - Rechercher des modèles

### 📦 Bundles Store (`bundles.js`)
**Description:** Gère les bundles disponibles et installés.
**Responsabilités:**
- Gestion des bundles disponibles
- Installation et désinstallation des bundles
- Gestion des mises à jour
- Sélection et filtrage des bundles

**Principales actions:**
- `fetchBundles()` - Charge les bundles disponibles
- `fetchInstalledBundles()` - Charge les bundles installés
- `installBundle(bundle)` - Installe un bundle
- `uninstallBundle(bundle)` - Désinstalle un bundle
- `updateBundle(bundle)` - Met à jour un bundle

### 🔄 Workflows Store (`workflows.js`)
**Description:** Gère les workflows ComfyUI.
**Responsabilités:**
- Gestion des workflows disponibles
- Chargement et sauvegarde des workflows
- Exécution et historique
- Workflows favoris et récents

**Principales actions:**
- `fetchWorkflows()` - Charge les workflows
- `loadWorkflow(workflow)` - Charge un workflow spécifique
- `saveWorkflow(workflowData, name)` - Sauvegarde un workflow
- `executeWorkflow(workflow, inputs)` - Exécute un workflow
- `toggleFavorite(workflowId)` - Marquer comme favori

### 🔐 Auth Store (`auth.js`)
**Description:** Gère l'authentification et les sessions utilisateur.
**Responsabilités:**
- Connexion/déconnexion des utilisateurs
- Gestion des tokens d'authentification
- Vérification des permissions
- Gestion du profil utilisateur

**Principales actions:**
- `login(username, password)` - Connecte un utilisateur
- `logout()` - Déconnecte l'utilisateur actuel
- `verifyToken()` - Vérifie la validité du token
- `register(userData)` - Enregistre un nouvel utilisateur
- `updateProfile(profileData)` - Met à jour le profil

### 🎨 UI Store (`ui.js`)
**Description:** Gère l'état de l'interface utilisateur et les préférences.
**Responsabilités:**
- État de la navigation (sidebar, menu mobile)
- Thème et préférences utilisateur
- Notifications et messages
- Modales et dialogues
- États de chargement

**Principales actions:**
- `toggleSidebar()` - Basculer la sidebar
- `setDarkMode(enabled)` - Changer le thème
- `addNotification(notification)` - Ajouter une notification
- `openModal(modalName, data)` - Ouvrir une modale
- `setGlobalLoading(loading, message)` - Gérer le chargement global

### 🔢 Counter Store (`counter.js`)
**Description:** Store d'exemple pour démonstration.
**Note:** Ce store peut être supprimé en production.

## Utilisation des Stores

### Installation et Configuration

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { initializeStores } from './stores'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')

// Initialiser les stores après le montage
initializeStores()
```

### Utilisation dans les Composants

```javascript
// Dans un composant Vue
<script setup>
import { useModelsStore, useBundlesStore, useWorkflowsStore, useAuthStore, useUIStore } from '@/stores'

const modelsStore = useModelsStore()
const bundlesStore = useBundlesStore()
const workflowsStore = useWorkflowsStore()
const authStore = useAuthStore()
const uiStore = useUIStore()

// Utilisation des états réactifs
const { models, loading: modelsLoading } = modelsStore
const { bundles, installedBundles } = bundlesStore
const { workflows, currentWorkflow } = workflowsStore
const { user, isAuthenticated } = authStore
const { darkMode, notifications } = uiStore

// Utilisation des actions
const loadData = async () => {
  try {
    uiStore.setGlobalLoading(true, 'Loading data...')
    await Promise.all([
      modelsStore.fetchModels(),
      bundlesStore.fetchBundles(),
      workflowsStore.fetchWorkflows()
    ])
    uiStore.addSuccessNotification('Data loaded successfully')
  } catch (error) {
    uiStore.addErrorNotification('Failed to load data')
  } finally {
    uiStore.setGlobalLoading(false)
  }
}
</script>
```

### Computed Properties Utiles

```javascript
// Exemples d'utilisation des computed properties
const { modelsByType, availableModelTypes } = modelsStore
const { bundlesByCategory, updatableBundles } = bundlesStore
const { workflowsByCategory, favoriteWorkflows } = workflowsStore
const { isAdmin, userDisplayName } = authStore
const { unreadNotificationsCount, themeClasses } = uiStore
```

## Patterns et Bonnes Pratiques

### 1. Gestion d'Erreur
```javascript
// Toujours encapsuler les appels API avec try/catch
async function performAction() {
  try {
    uiStore.setGlobalLoading(true)
    await someApiCall()
    uiStore.addSuccessNotification('Action completed')
  } catch (error) {
    uiStore.handleApiError(error)
  } finally {
    uiStore.setGlobalLoading(false)
  }
}
```

### 2. États de Chargement
```javascript
// Utiliser les états de chargement appropriés
const isLoading = computed(() => 
  modelsStore.loading || 
  bundlesStore.loading || 
  workflowsStore.loading ||
  uiStore.globalLoading
)
```

### 3. Notifications
```javascript
// Utiliser les helpers de notification
uiStore.addSuccessNotification('Operation successful')
uiStore.addErrorNotification('Something went wrong', { persistent: true })
uiStore.addWarningNotification('Be careful with this action')
uiStore.addInfoNotification('New feature available')
```

### 4. Authentification
```javascript
// Vérifier l'authentification dans les composants
watchEffect(() => {
  if (!authStore.isAuthenticated && !authStore.authLoading) {
    // Rediriger vers la page de connexion
    router.push('/login')
  }
})
```

## API Endpoints Attendus

### Models Store
- `GET /api/models` - Liste des modèles
- `POST /api/models/download` - Télécharger un modèle
- `POST /api/models/download/{id}/cancel` - Annuler un téléchargement
- `DELETE /api/models/{id}` - Supprimer un modèle

### Bundles Store
- `GET /api/bundles` - Liste des bundles
- `GET /api/bundles/installed` - Bundles installés
- `POST /api/bundles/install` - Installer un bundle
- `POST /api/bundles/install/{id}/cancel` - Annuler une installation
- `DELETE /api/bundles/uninstall/{id}` - Désinstaller un bundle
- `POST /api/bundles/update/{id}` - Mettre à jour un bundle

### Workflows Store
- `GET /api/workflows` - Liste des workflows
- `GET /api/workflows/{id}` - Détails d'un workflow
- `POST /api/workflows/save` - Sauvegarder un workflow
- `PUT /api/workflows/{id}` - Mettre à jour un workflow
- `DELETE /api/workflows/{id}` - Supprimer un workflow
- `POST /api/workflows/{id}/duplicate` - Dupliquer un workflow
- `POST /api/workflows/execute` - Exécuter un workflow
- `POST /api/workflows/execute/{id}/cancel` - Annuler une exécution
- `PUT /api/workflows/{id}/favorite` - Marquer comme favori

### Auth Store
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/verify` - Vérifier le token
- `POST /api/auth/register` - Inscription
- `POST /api/auth/change-password` - Changer le mot de passe
- `PUT /api/auth/profile` - Mettre à jour le profil
- `POST /api/auth/refresh` - Rafraîchir le token

## Tests

Les stores incluent des tests unitaires complets. Pour exécuter les tests :

```bash
npm run test
# ou
npm run test:unit stores/
```

### Structure des Tests
- Tests des états initiaux
- Tests des actions asynchrones
- Tests des computed properties
- Tests de gestion d'erreur
- Mocks des appels API

## Persistence

### LocalStorage
- `auth_token` - Token d'authentification
- `darkMode` - Préférence de thème
- `language` - Langue sélectionnée
- `compactMode` - Mode compact de l'interface

### Considérations de Performance
- Les stores utilisent des `ref()` pour les données primitives
- Les listes utilisent des `ref([])` pour la réactivité
- Les computed properties sont mis en cache automatiquement
- Les appels API sont débounced quand nécessaire

## Migration et Compatibilité

Si vous migrez depuis Vuex ou un autre gestionnaire d'état :

1. Remplacer les mutations par des actions directes
2. Utiliser `ref()` et `computed()` au lieu de `state` et `getters`
3. Les actions sont maintenant des fonctions normales (pas de context)
4. Pas besoin de modules, chaque store est autonome

## Debugging

Pour débugger les stores en développement :

```javascript
// Accéder aux stores dans la console
window.stores = {
  data: useDataStore(),
  auth: useAuthStore(),
  ui: useUIStore()
}
```

Les stores sont compatibles avec Vue DevTools pour un debugging avancé.
