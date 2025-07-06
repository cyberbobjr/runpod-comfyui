/**
 * Workflows Store Types
 * 
 * Type definitions for the workflows store, including all workflow-related
 * interfaces and types used throughout the application.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

/**
 * Workflow store state interface
 */
export interface WorkflowsStoreState {
  workflows: string[];
  currentWorkflow: string | null;
  selectedWorkflow: string | null;
  loading: boolean;
  error: string | null;
}