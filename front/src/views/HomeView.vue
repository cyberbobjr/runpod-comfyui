<!--
 * HomeView - TypeScript Vue Component
 * 
 * Main home page component with welcome message and navigation guidance.
 * 
 * Features:
 * - Welcome message with application overview
 * - Navigation guidance for new users
 * - Responsive design with proper styling
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
-->
<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faBoxOpen, faCubes, faRocket } from '@fortawesome/free-solid-svg-icons';
import type { PageMeta } from './types/views.types';

// Router for navigation
const router = useRouter();

// Page meta information
const pageMeta = computed<PageMeta>(() => ({
  title: 'Home',
  description: 'ComfyUI Manager - Your central hub for managing AI models and workflows',
  keywords: ['comfyui', 'manager', 'home', 'models', 'bundles']
}));

// Navigation functions
const navigateToInstall = async (tab: 'bundles' | 'models'): Promise<void> => {
  try {
    await router.push({ name: 'install', query: { tab } });
  } catch (error: any) {
    console.error('Navigation error:', error);
  }
};

// Set document title on mount
onMounted(() => {
  document.title = `ComfyUI Manager - ${pageMeta.value.title}`;
});
</script>

<template>
  <main class="w-full min-h-screen bg-background flex flex-col">
    <!-- Hero Section -->
    <div class="flex-1 flex flex-col items-center justify-center p-6">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Main Title -->
        <div class="mb-8">
          <h1 class="text-4xl md:text-5xl font-bold text-primary mb-4">
            Welcome to ComfyUI Manager
          </h1>
          <p class="text-xl text-text-muted max-w-2xl mx-auto">
            Your central hub for managing AI models, workflow bundles, and ComfyUI configurations with ease.
          </p>
        </div>

        <!-- Quick Actions -->
        <div class="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto mb-8">
          <!-- Install Bundles Card -->
          <div 
            class="card cursor-pointer hover:bg-background-soft transition-colors duration-200 group"
            @click="navigateToInstall('bundles')"
          >
            <div class="text-center p-4">
              <FontAwesomeIcon 
                :icon="faBoxOpen" 
                class="text-3xl text-primary mb-3 group-hover:scale-110 transition-transform duration-200" 
              />
              <h3 class="text-lg font-semibold text-text-light mb-2">Install Bundles</h3>
              <p class="text-text-muted text-sm">
                Download and install workflow bundles with all required models and configurations.
              </p>
            </div>
          </div>

          <!-- Install Models Card -->
          <div 
            class="card cursor-pointer hover:bg-background-soft transition-colors duration-200 group"
            @click="navigateToInstall('models')"
          >
            <div class="text-center p-4">
              <FontAwesomeIcon 
                :icon="faCubes" 
                class="text-3xl text-primary mb-3 group-hover:scale-110 transition-transform duration-200" 
              />
              <h3 class="text-lg font-semibold text-text-light mb-2">Install Models</h3>
              <p class="text-text-muted text-sm">
                Browse and install individual AI models for your ComfyUI workflows.
              </p>
            </div>
          </div>
        </div>

        <!-- Get Started Button -->
        <div class="mt-8">
          <button 
            @click="navigateToInstall('bundles')"
            class="btn btn-primary px-8 py-3 text-lg inline-flex items-center space-x-2"
          >
            <FontAwesomeIcon :icon="faRocket" />
            <span>Get Started</span>
          </button>
        </div>

        <!-- Additional Info -->
        <div class="mt-12 text-center">
          <p class="text-text-muted text-sm">
            Select a tab from the navigation bar above or click on the cards to explore the features.
          </p>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* Component-specific styles */
.btn-lg {
  @apply px-8 py-3 text-lg;
}

/* Hover effects for cards */
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Smooth transitions */
.card {
  transition: all 0.2s ease-in-out;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
