import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: { name: 'install', query: { tab: 'bundles' } }
    },
    {
      // New unified install page with tabs
      path: '/install',
      name: 'install',
      component: () => import('../views/InstallPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      // Redirect old bundle route to new install page
      path: '/download-bundles',
      redirect: { name: 'install', query: { tab: 'bundles' } }
    },
    {
      // Redirect old models route to new install page
      path: '/download-models',
      redirect: { name: 'install', query: { tab: 'models' } }
    },
    {
      path: '/manage-bundles',
      name: 'manage-bundles',
      component: () => import('../components/BundleManagerComponent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/file-explorer',
      name: 'file-explorer',
      component: () => import('../components/FileManagerComponent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/json-editor',
      name: 'json-editor',
      component: () => import('../components/JsonEditorComponent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../components/SettingsComponent.vue'),
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
    next({ name: 'install', query: { tab: 'bundles' } }); // Rediriger vers la page d'accueil
  } 
  else {
    next(); // Continuer normalement
  }
});

export default router
