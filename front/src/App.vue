<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import type { RouteLocationNormalizedLoaded, Router } from "vue-router";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import {
  faDownload,
  faBoxesStacked,
  faFolder,
  faFileCode,
  faGear,
  faBars,
} from "@fortawesome/free-solid-svg-icons";
import NotificationContainer from "./components/NotificationContainer.vue";
import DialogContainer from "./components/common/DialogContainer.vue";
import InstallProgressIndicator from "./components/InstallProgressIndicator.vue";
import FooterComponent from "./components/common/FooterComponent.vue";
import { useAuthStore } from "./stores/auth";
import { TOKENSTORAGEKEY } from "./services/types/api.types";

/**
 * App.vue - Main Application Component (TypeScript)
 *
 * **Description:** Root component that handles authentication, navigation, and global UI elements.
 * **Features:**
 * - Authentication state management
 * - Route-based navigation tabs
 * - Global notification and dialog containers
 * - Install progress indicator
 * - Responsive layout with header and footer
 *
 * @author Converted to TypeScript
 * @version 2.0.0
 */

const route: RouteLocationNormalizedLoaded = useRoute();
const router: Router = useRouter();
const authStore = useAuthStore();

/**
 * State for sidebar collapse
 *
 * **Description:** Reactive reference that controls sidebar visibility.
 * **Returns:** Boolean indicating if sidebar is collapsed
 */
const isSidebarCollapsed = ref<boolean>(false);

/**
 * Toggle sidebar collapse state
 *
 * **Description:** Toggles the sidebar between collapsed and expanded states.
 * **Parameters:** None
 * **Returns:** void
 */
const toggleSidebar = (): void => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};
/**
 * Check if the user is authenticated
 *
 * **Description:** Computed property that checks authentication status based on stored token.
 * **Returns:** Boolean indicating if user is authenticated
 */
const isAuthenticated = computed((): boolean => {
  return !!localStorage.getItem(TOKENSTORAGEKEY);
});

/**
 * Check if current route requires authentication and show header
 *
 * **Description:** Computed property that determines if the header should be displayed.
 * **Returns:** Boolean indicating if header should be shown
 */
const showHeader = computed((): boolean => {
  return isAuthenticated.value && !!route.meta.requiresAuth;
});

/**
 * Logout function
 *
 * **Description:** Handles user logout by clearing auth state and redirecting to login.
 * **Parameters:** None
 * **Returns:** void
 */
const handleLogout = (): void => {
  authStore.logout();
  // Navigate to login page
  router.push({ name: "login" });
};

/**
 * Get current active tab based on route
 *
 * **Description:** Computed property that returns the current active tab name.
 * **Returns:** String representing the active tab name
 */
const activeTab = computed((): string => {
  return (route.name as string) || "install";
});

/**
 * Handle tab navigation
 *
 * **Description:** Navigates to the specified route when tab is changed.
 * **Parameters:**
 * - `name` (string): Route name to navigate to
 * **Returns:** void
 */
const handleTabChange = (name: string): void => {
  router.push({ name });
};

// Tabs definition
const tabs = [
  {
    name: "install",
    label: "Install",
    icon: faDownload,
  },
  {
    name: "manage-bundles",
    label: "Manage bundles",
    icon: faBoxesStacked,
  },
  {
    name: "file-explorer",
    label: "File Explorer",
    icon: faFolder,
  },
  {
    name: "json-editor",
    label: "JSON Editor",
    icon: faFileCode,
  },
  {
    name: "settings",
    label: "Settings",
    icon: faGear,
  },
];

// Load persistent notifications on app startup
onMounted(() => {
  // Les notifications persistantes sont maintenant chargées automatiquement
  // lors de la première utilisation du composable useNotifications
});
</script>

<template>
  <div class="app-container">
    <!-- Header bar that appears only when logged in -->
    <header
      v-if="showHeader"
      class="bg-background-soft text-text-light flex justify-between items-center py-4 shadow-md border-b border-border"
    >
      <div class="flex items-center">
        <!-- Sidebar toggle button -->
        <button
          @click="toggleSidebar"
          class="btn bg-background-mute hover:bg-background text-text-light p-2 rounded transition-colors mr-4 ml-4"
        >
          <FontAwesomeIcon :icon="faBars" class="text-lg" />
        </button>
        <h1 class="text-2xl font-semibold">ComfyUI Model Manager</h1>
      </div>
      <button
        @click="handleLogout"
        class="btn bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors mr-4"
      >
        Logout
      </button>
    </header>

    <!-- Main content area with sidebar -->
    <div v-if="showHeader" class="flex flex-1 overflow-hidden">
      <!-- Vertical Sidebar -->
      <nav
        :class="[
          'bg-background-soft border-r border-border transition-all duration-300 ease-in-out overflow-hidden',
          isSidebarCollapsed ? 'w-16' : 'w-64'
        ]"
      >
        <!-- Global Install Progress Indicator -->
        <div class="px-2 py-2">
          <InstallProgressIndicator />
        </div>

        <!-- Navigation Items -->
        <div class="flex flex-col py-2">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            @click="handleTabChange(tab.name)"
            :class="[
              'flex items-center px-4 py-3 transition-all duration-200 ease-in-out focus:outline-none group relative',
              activeTab === tab.name
                ? 'text-primary bg-background-mute border-r-2 border-primary'
                : 'text-text-light-muted hover:bg-background-mute hover:text-text-light',
            ]"
            :title="isSidebarCollapsed ? tab.label : ''"
          >
            <div class="flex items-center min-w-0 w-full">
              <FontAwesomeIcon
                :icon="tab.icon"
                class="text-lg flex-shrink-0"
                :class="{ 'text-primary': activeTab === tab.name }"
              />
              <span
                :class="[
                  'ml-3 text-sm font-medium transition-all duration-300 ease-in-out whitespace-nowrap',
                  isSidebarCollapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100 w-auto'
                ]"
              >
                {{ tab.label }}
              </span>
            </div>
            
            <!-- Tooltip for collapsed state -->
            <div
              v-if="isSidebarCollapsed"
              class="absolute left-full ml-2 px-2 py-1 bg-background-soft text-text-light text-sm rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 whitespace-nowrap"
            >
              {{ tab.label }}
            </div>
          </button>
        </div>
      </nav>

      <!-- Main content area -->
      <main class="flex-1 overflow-auto bg-background">
        <div class="view-container">
          <RouterView />
        </div>
      </main>
    </div>

    <!-- For non-authenticated users, show full width content -->
    <div v-else class="view-container flex-1 overflow-auto bg-background w-full">
      <RouterView />
    </div>

    <!-- Footer - only show when logged in -->
    <FooterComponent
      v-if="showHeader"
      :show-build="false"
      :show-build-date="false"
    />

    <!-- Notification and Dialog containers -->
    <NotificationContainer />
    <DialogContainer />
  </div>
</template>

<style>
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  background-color: #0f2537; /* Direct color instead of Tailwind class for reliability */
  color: #ffffff;
}

body {
  font-family: sans-serif;
}

#app {
  width: 100vw;
  min-height: 100vh;
  height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: none;
  padding: 0;
  margin: 0;
  overflow-x: hidden;
}

.app-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 0;
  height: 100%;
  max-width: 100%;
  /* Adding max-width and centering for large screens */
  margin: 0 auto;
}


.view-container {
  flex: 1 1 auto;
  width: 100%;
  min-height: 0;
  padding: 1rem;
}

/* Smooth scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a2332;
}

::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}
</style>
