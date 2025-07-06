/**
 * Vue Router Configuration - TypeScript Version
 *
 * Comprehensive router configuration with TypeScript support for the ComfyUI application.
 *
 * Features:
 * - Type-safe route definitions with meta properties
 * - Authentication guards with typed navigation
 * - Automatic redirects for legacy routes
 * - Guest and authenticated route protection
 * - Query parameter handling for tab navigation
 *
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { TOKENSTORAGEKEY } from "@/services/types/api.types";
import { createRouter, createWebHistory } from "vue-router";
import type {
  Router,
  RouteRecordRaw,
  NavigationGuardNext,
  RouteLocationNormalized,
} from "vue-router";

/**
 * Route meta interface for type safety
 */
interface RouteMeta {
  requiresAuth?: boolean;
  guest?: boolean;
  title?: string;
  description?: string;
}

/**
 * Extended route record with typed meta
 */
interface TypedRouteRecord extends Omit<RouteRecordRaw, "meta"> {
  meta?: RouteMeta;
}

/**
 * Authentication token management
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKENSTORAGEKEY);
};

/**
 * Check if user is authenticated
 */
const isUserAuthenticated = (): boolean => {
  return !!getAuthToken();
};

/**
 * Route definitions with TypeScript support
 */
const routes: TypedRouteRecord[] = [
  {
    path: "/",
    redirect: { name: "install", query: { tab: "bundles" } },
    meta: {
      title: "Home",
      description: "Default redirect to install page",
    },
  },
  {
    // New unified install page with tabs
    path: "/install",
    name: "install",
    component: () => import("../views/Install.vue"),
    meta: {
      requiresAuth: true,
      title: "Install",
      description: "Install models and bundles",
    },
  },
  {
    // Redirect old bundle route to new install page
    path: "/download-bundles",
    redirect: { name: "install", query: { tab: "bundles" } },
    meta: {
      title: "Download Bundles (Legacy)",
      description: "Legacy route redirect to install page",
    },
  },
  {
    // Redirect old models route to new install page
    path: "/download-models",
    redirect: { name: "install", query: { tab: "models" } },
    meta: {
      title: "Download Models (Legacy)",
      description: "Legacy route redirect to install page",
    },
  },
  {
    path: "/manage-bundles",
    name: "manage-bundles",
    component: () => import("../views/BundleManager.vue"),
    meta: {
      requiresAuth: true,
      title: "Manage Bundles",
      description: "Manage installed bundles and configurations",
    },
  },
  {
    path: "/file-explorer",
    name: "file-explorer",
    component: () => import("../views/FileManager.vue"),
    meta: {
      requiresAuth: true,
      title: "File Explorer",
      description: "Browse and manage application files",
    },
  },
  {
    path: "/json-editor",
    name: "json-editor",
    component: () => import("../views/JsonEditor.vue"),
    meta: {
      requiresAuth: true,
      title: "JSON Editor",
      description: "Edit JSON configuration files",
    },
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("../views/Settings.vue"),
    meta: {
      requiresAuth: true,
      title: "Settings",
      description: "Application settings and preferences",
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/Login.vue"),
    meta: {
      guest: true,
      title: "Login",
      description: "User authentication",
    },
  },
  {
    path: "/comfyui",
    name: "comfyui",
    component: () => import("../views/ComfyUIView.vue"),
    meta: {
      requiresAuth: true,
      title: "ComfyUI Generator",
      description: "Generate images using ComfyUI workflows",
    },
  },
  {
    // Catch-all route for 404 errors
    path: "/:pathMatch(.*)*",
    name: "not-found",
    redirect: { name: "install", query: { tab: "bundles" } },
    meta: {
      title: "Page Not Found",
      description: "Redirect to install page for unknown routes",
    },
  },
];

/**
 * Create Vue Router instance with TypeScript configuration
 */
const router: Router = createRouter({
  history: createWebHistory((import.meta as any).env.BASE_URL),
  routes: routes as RouteRecordRaw[],
  // Scroll behavior for better UX
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  },
});

/**
 * Navigation guard to protect routes based on authentication
 * @param to - Target route location
 * @param from - Source route location
 * @param next - Navigation guard next function
 */
router.beforeEach(
  (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ): void => {
    const isAuthenticated: boolean = isUserAuthenticated();

    // Check if route requires authentication
    const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth);
    const isGuestRoute = to.matched.some((record) => record.meta?.guest);

    if (requiresAuth && !isAuthenticated) {
      // Route requires authentication but user is not authenticated
      console.log("🔒 Access denied: Authentication required");
      next({
        name: "login",
        query: { redirect: to.fullPath },
      });
    } else if (isGuestRoute && isAuthenticated) {
      // Route is for guests but user is authenticated (e.g., login page)
      console.log("🔄 Redirecting authenticated user from guest route");
      next({
        name: "install",
        query: { tab: "bundles" },
      });
    } else {
      // Allow navigation
      next();
    }
  }
);

/**
 * After navigation hook for logging and analytics
 */
router.afterEach(
  (to: RouteLocationNormalized, from: RouteLocationNormalized): void => {
    // Update document title if route has meta title
    if (to.meta?.title) {
      document.title = `ComfyUI Manager - ${to.meta.title}`;
    }

    // Log navigation for debugging (in development)
    if ((import.meta as any).env.MODE === "development") {
      console.log(
        `🧭 Navigation: ${String(from.name) || from.path} → ${
          String(to.name) || to.path
        }`
      );
    }
  }
);

/**
 * Router error handler
 */
router.onError((error: Error): void => {
  console.error("🚨 Router error:", error);

  // In production, you might want to send this to an error tracking service
  if ((import.meta as any).env.MODE === "production") {
    // Example: Sentry.captureException(error);
  }
});

/**
 * Utility functions for programmatic navigation
 */
export const navigateToInstall = async (
  tab: string = "bundles"
): Promise<void> => {
  try {
    await router.push({ name: "install", query: { tab } });
  } catch (error: any) {
    if (error.name !== "NavigationDuplicated") {
      console.error("Navigation error:", error);
    }
  }
};

export const navigateToLogin = async (redirectPath?: string): Promise<void> => {
  try {
    const query = redirectPath ? { redirect: redirectPath } : {};
    await router.push({ name: "login", query });
  } catch (error: any) {
    if (error.name !== "NavigationDuplicated") {
      console.error("Navigation error:", error);
    }
  }
};

export const navigateToSettings = async (): Promise<void> => {
  try {
    await router.push({ name: "settings" });
  } catch (error: any) {
    if (error.name !== "NavigationDuplicated") {
      console.error("Navigation error:", error);
    }
  }
};

/**
 * Type-safe route name checking
 */
export const isCurrentRoute = (routeName: string): boolean => {
  return router.currentRoute.value.name === routeName;
};

/**
 * Get current route meta information
 */
export const getCurrentRouteMeta = (): RouteMeta | undefined => {
  return router.currentRoute.value.meta as RouteMeta;
};

// Export router as default
export default router;

// Export types for use in other files
export type { RouteMeta, TypedRouteRecord };
