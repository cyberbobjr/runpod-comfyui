// Import Bootswatch Superhero theme
import 'bootswatch/dist/superhero/bootstrap.min.css';

import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import ModelManager from './ModelManager.vue'
import FileManager from './FileManager.vue'
import JsonEditor from './JsonEditor.vue'
import { tooltip } from './directives/tooltip'

const routes = [
    { path: '/', redirect: '/models' },
    { path: '/models', component: ModelManager },
    { path: '/files', component: FileManager },
    { path: '/jsoneditor', component: JsonEditor }
]

const router = createRouter({
    history: createWebHashHistory(), // Changé de createWebHistory à createWebHashHistory
    routes
})

const app = createApp(App)

// Enregistrer la directive tooltip globalement
app.directive('tooltip', tooltip)

app.use(router).mount('#app')