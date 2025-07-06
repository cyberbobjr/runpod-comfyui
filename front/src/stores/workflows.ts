/**
 * Workflows Store - TypeScript Version (Simplified)
 *
 * Pinia store for managing workflows.
 * This is a simplified version to resolve import errors.
 *
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { defineStore } from "pinia";
import type { WorkflowsStoreState } from "./types/workflows.types";
const { default: api } = await import("@/services/api");

export const useWorkflowsStore = defineStore("workflows", {
  // === STATE ===
  state: (): WorkflowsStoreState => ({
    workflows: [],
    currentWorkflow: null,
    selectedWorkflow: null,
    loading: false,
    error: null,
  }),

  // === GETTERS ===
  getters: {},

  // === ACTIONS ===
  actions: {
    /**
     * Fetch workflows
     *
     * **Description:** Loads workflows from the server (placeholder implementation).
     * **Parameters:** None
     * **Returns:** Promise that resolves when workflows are loaded
     */
    async fetchWorkflows(): Promise<void> {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get<string[]>("/workflows/");
        this.workflows = response.data || [];
      } catch (error: any) {
        this.error = error.message;
        console.error("Error fetching workflows:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Upload workflow
     *
     * **Description:** Uploads a workflow file to the server.
     * **Parameters:**
     * - `file` (File): The workflow file to upload
     * **Returns:** Promise that resolves when the workflow is uploaded
     */
    async uploadWorkflow(file: File): Promise<void> {
      this.loading = true;
      this.error = null;

      try {
        const formData = new FormData();
        formData.append("workflow_file", file);

        // Dynamic import to avoid circular dependency

        await api.post("/workflows/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        // Reload workflows after successful upload
        await this.fetchWorkflows();
      } catch (error: any) {
        this.error = error.message;
        console.error("Error uploading workflow:", error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Clear workflows
     *
     * **Description:** Clears all workflows data.
     * **Parameters:** None
     * **Returns:** void
     */
    clearWorkflows(): void {
      this.workflows = [];
      this.currentWorkflow = null;
      this.selectedWorkflow = null;
      this.error = null;
    },
  },
});
