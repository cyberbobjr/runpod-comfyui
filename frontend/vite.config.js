import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  publicDir: 'public',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Ensure public directory files are copied to dist
    copyPublicDir: true,
    emptyOutDir: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      // Add this alias to use the Vue build with the template compiler
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  server: {
    proxy: {
      // Proxy /api to backend in dev mode
      '/api': {
        target: 'http://localhost:8082',
        changeOrigin: true,
        secure: false,
      }
    }
  }
}))