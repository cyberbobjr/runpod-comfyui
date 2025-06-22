import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: { name: 'download-bundles' }
    },
    {
      // Tab routes
      path: '/download-bundles',
      name: 'download-bundles',
      component: () => import('../components/DownloadBundlesComponent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/download-models',
      name: 'download-models',
      component: () => import('../components/DownloadModelsComponent.vue'),
      props: { feature: 'Download Models' },
      meta: { requiresAuth: true }
    },
    {
      path: '/manage-bundles',
      name: 'manage-bundles',
      component: () => import('../components/BundleManagerComponent.vue'),
      props: { feature: 'Manage Bundles' },
      meta: { requiresAuth: true }
    },
    {
      path: '/file-explorer',
      name: 'file-explorer',
      component: () => import('../components/FileManagerComponent.vue'),
      props: { feature: 'File Explorer' },
      meta: { requiresAuth: true }
    },
    {
      path: '/json-editor',
      name: 'json-editor',
      component: () => import('../components/JsonEditorComponent.vue'),
      props: { feature: 'JSON Editor' },
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../components/SettingsComponent.vue'),
      props: { feature: 'Settings' },
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: { guest: true }
    }
  ],
})

// Navigation guard pour protéger les routes
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token');
  
  // Si la route nécessite une authentification et que l'utilisateur n'est pas connecté
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } 
  // Si la route est pour les invités et que l'utilisateur est connecté (ex: page de login)
  else if (to.matched.some(record => record.meta.guest) && isAuthenticated) {
    next('/download-bundles'); // Rediriger vers la page d'accueil
  } 
  else {
    next(); // Continuer normalement
  }
});

export default router
