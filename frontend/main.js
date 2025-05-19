import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ModelManager from './ModelManager.vue'
import FileManager from './FileManager.vue'

const routes = [
    { path: '/', component: ModelManager },
    { path: '/files', component: FileManager }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

createApp(App).use(router).mount('#app')