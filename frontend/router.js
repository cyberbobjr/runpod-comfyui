import { createRouter, createWebHistory } from 'vue-router';
import ModelManager from './ModelManager.vue';
import BundlePage from './BundlePage.vue';
import BundleInstaller from './BundleInstaller.vue';
import FileExplorer from './FileManager.vue';
import JsonEditor from './JsonEditor.vue';
import Settings from './Settings.vue';

const routes = [
  {
    path: '/',
    redirect: '/models'
  },
  {
    path: '/models',
    component: ModelManager
  },
  {
    path: '/bundles',
    component: BundlePage
  },
  {
    path: '/install-bundles',
    component: BundleInstaller
  },
  {
    path: '/files',
    component: FileExplorer
  },
  {
    path: '/jsoneditor',
    component: JsonEditor
  },
  {
    path: '/settings',
    component: Settings
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
