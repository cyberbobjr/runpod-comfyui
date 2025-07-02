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
 * Workflow interface
 */
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  category?: string;
  author?: string;
  version?: string;
  tags?: string[];
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  metadata?: WorkflowMetadata;
  created_at?: string;
  updated_at?: string;
  [key: string]: any;
}

/**
 * Workflow node interface
 */
export interface WorkflowNode {
  id: string;
  type: string;
  title?: string;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  properties?: Record<string, any>;
  position?: {
    x: number;
    y: number;
  };
  size?: {
    width: number;
    height: number;
  };
}

/**
 * Workflow connection interface
 */
export interface WorkflowConnection {
  id: string;
  source: {
    nodeId: string;
    slot: number | string;
  };
  target: {
    nodeId: string;
    slot: number | string;
  };
  type?: string;
}

/**
 * Workflow metadata interface
 */
export interface WorkflowMetadata {
  title?: string;
  description?: string;
  author?: string;
  version?: string;
  license?: string;
  dependencies?: string[];
  requirements?: {
    models?: string[];
    nodes?: string[];
    extensions?: string[];
  };
  thumbnail?: string;
  examples?: string[];
}

/**
 * Workflow execution interface
 */
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: string;
  endTime?: string;
  progress?: number;
  results?: any;
  error?: string;
  logs?: ExecutionLog[];
}

/**
 * Execution log interface
 */
export interface ExecutionLog {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  nodeId?: string;
  data?: any;
}

/**
 * Workflow template interface
 */
export interface WorkflowTemplate {
  id: string;
  name: string;
  description?: string;
  category: string;
  workflow: Partial<Workflow>;
  parameters?: WorkflowParameter[];
  preview?: string;
}

/**
 * Workflow parameter interface
 */
export interface WorkflowParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'file';
  label?: string;
  description?: string;
  defaultValue?: any;
  options?: string[];
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

/**
 * Workflow filter options
 */
export interface WorkflowFilterOptions {
  category?: string;
  tags?: string[];
  author?: string;
  search?: string;
  sortBy?: 'name' | 'date' | 'category' | 'author';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Workflow store state interface
 */
export interface WorkflowsStoreState {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  selectedWorkflow: Workflow | null;
  loading: boolean;
  error: string | null;
  executionHistory: WorkflowExecution[];
  executionStatus: Record<string, WorkflowExecution>;
  workflowCategories: string[];
  recentWorkflows: Workflow[];
}

/**
 * Workflow import/export options
 */
export interface WorkflowImportOptions {
  overwrite?: boolean;
  validateNodes?: boolean;
  updateReferences?: boolean;
}

export interface WorkflowExportOptions {
  includeMetadata?: boolean;
  format?: 'json' | 'yaml';
  compress?: boolean;
}

/**
 * Workflow operation result
 */
export interface WorkflowOperationResult {
  success: boolean;
  message?: string;
  error?: string;
  workflowId?: string;
  data?: any;
}
