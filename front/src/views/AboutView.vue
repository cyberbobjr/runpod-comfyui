<!--
 * AboutView - TypeScript Vue Component
 * 
 * Simple about page displaying application information.
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
-->
<script setup lang="ts">
import { computed } from 'vue';
import type { PageMeta } from './types/views.types';

// Page meta information
const pageMeta = computed<PageMeta>(() => ({
  title: 'About',
  description: 'Information about ComfyUI Manager',
  keywords: ['about', 'comfyui', 'manager', 'information']
}));

// Set document title
document.title = `ComfyUI Manager - ${pageMeta.value.title}`;
</script>

<template>
  <div class="about min-h-screen bg-background flex items-center justify-center p-6">
    <div class="card max-w-2xl w-full">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-primary mb-6">About ComfyUI Manager</h1>
        <div class="space-y-4 text-text-light">
          <p class="text-lg">
            ComfyUI Manager is a comprehensive tool for managing models, bundles, and configurations 
            for ComfyUI installations.
          </p>
          <p>
            This application provides an intuitive interface for downloading, installing, and managing 
            various AI models and workflow bundles, making it easier to work with ComfyUI.
          </p>
          <div class="mt-8 pt-6 border-t border-border">
            <p class="text-sm text-text-muted">
              Built with Vue 3, TypeScript, and Tailwind CSS
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Component-specific styles */
.about {
  background: linear-gradient(135deg, rgba(var(--background-rgb), 0.95) 0%, rgba(var(--background-soft-rgb), 0.98) 100%);
}

@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
  }
}
</style>
