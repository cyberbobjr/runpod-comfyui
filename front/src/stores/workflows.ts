/**
 * Workflows Store - TypeScript Version (Simplified)
 * 
 * Pinia store for managing workflows.
 * This is a simplified version to resolve import errors.
 * 
 * @author Converted to TypeScript
 * @version 2.0.0
 */

import { defineStore } from 'pinia';
import type {
  Workflow,
  WorkflowsStoreState,
  WorkflowExecution,
  WorkflowFilterOptions
} from './types/workflows.types';

export const useWorkflowsStore = defineStore('workflows', {
  // === STATE ===
  state: (): WorkflowsStoreState => ({
    workflows: [],
    currentWorkflow: null,
    selectedWorkflow: null,
    loading: false,
    error: null,
    executionHistory: [],
    executionStatus: {},
    workflowCategories: [],
    recentWorkflows: []
  }),

  // === GETTERS ===
  getters: {
    /**
     * Get workflows grouped by category
     * 
     * **Description:** Groups workflows by their category for organized display.
     * **Returns:** Object with categories as keys and workflow arrays as values
     */
    workflowsByCategory(): Record<string, Workflow[]> {
      const grouped: Record<string, Workflow[]> = {};
      this.workflows.forEach((workflow: Workflow) => {
        const category = workflow.category || 'Uncategorized';
        if (!grouped[category]) {
          grouped[category] = [];
        }
        grouped[category].push(workflow);
      });
      return grouped;
    },

    /**
     * Get available workflow categories
     * 
     * **Description:** Returns a list of unique workflow categories.
     * **Returns:** Array of unique workflow categories
     */
    availableCategories(): string[] {
      const categories = new Set<string>();
      this.workflows.forEach((workflow: Workflow) => {
        categories.add(workflow.category || 'Uncategorized');
      });
      return [...categories];
    },

    /**
     * Get workflows count
     * 
     * **Description:** Returns the total number of workflows.
     * **Returns:** Total number of workflows
     */
    workflowsCount(): number {
      return this.workflows.length;
    }
  },

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
        // TODO: Implement actual API call
        // const response = await api.get('/workflows/');
        // this.workflows = response.data || [];
        this.workflows = [];
      } catch (error: any) {
        this.error = error.message;
        console.error('Error fetching workflows:', error);
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
      this.executionHistory = [];
      this.executionStatus = {};
      this.recentWorkflows = [];
      this.error = null;
    },

    /**
     * Set current workflow
     * 
     * **Description:** Sets the currently active workflow.
     * **Parameters:**
     * - `workflow` (Workflow | null): Workflow to set as current
     * **Returns:** void
     */
    setCurrentWorkflow(workflow: Workflow | null): void {
      this.currentWorkflow = workflow;
    },

    /**
     * Set selected workflow
     * 
     * **Description:** Sets the selected workflow for operations.
     * **Parameters:**
     * - `workflow` (Workflow | null): Workflow to set as selected
     * **Returns:** void
     */
    setSelectedWorkflow(workflow: Workflow | null): void {
      this.selectedWorkflow = workflow;
    }
  }
});
