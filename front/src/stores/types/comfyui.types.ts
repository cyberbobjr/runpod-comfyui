/**
 * ComfyUI Store Types
 * 
 * Type definitions for the ComfyUI store, including all workflow-related
 * interfaces and types used throughout the application.
 * 
 * @author ComfyUI Integration
 * @version 1.0.0
 */

/**
 * LoRA configuration interface
 */
export interface LoRA {
  name: string;
  strength: number;
}

/**
 * Generation parameters interface matching the backend GenerationParams model
 */
export interface GenerationParams {
  // Basic generation parameters
  model_key: string;
  prompt: string;
  negative_prompt?: string;
  sampler?: string;
  steps?: number;
  cfg?: number;
  width?: number;
  height?: number;
  seed?: number | null;
  
  // LoRA parameters
  loras?: LoRA[];
  
  // ControlNet parameters
  controlnet_image?: string | null;
  controlnet_preprocessor?: string | null;
  controlnet_model?: string | null;
  
  // Image-to-image parameters
  init_image?: string | null;
  
  // Inpainting parameters
  inpaint_mask?: string | null;
  
  // Outpainting parameters
  outpaint_padding?: number | null;
  
  // Optimization parameters
  enable_tea_cache?: boolean;
  enable_clear_cache?: boolean;
  
  // Detail enhancement parameters
  add_details?: boolean;
  
  // Execution control
  wait?: boolean;
}

/**
 * Model registry entry interface
 */
export interface ModelRegistryEntry {
  model_type: string;
  filename: string;
}

/**
 * Model registry interface
 */
export interface ModelRegistry {
  [key: string]: ModelRegistryEntry;
}

/**
 * ComfyUI workflow interface
 */
export interface ComfyWorkflow {
  [key: string]: any;
}

/**
 * ComfyUI execution result interface
 */
export interface ComfyExecutionResult {
  prompt_id: string;
  workflow?: ComfyWorkflow;
  images: string[];
  result: any;
  status?: string;
}

/**
 * ComfyUI status response interface
 */
export interface ComfyStatusResponse {
  status: string;
  base_url: string;
  system_stats: any;
}

/**
 * ComfyUI generation response interface
 */
export interface ComfyGenerationResponse {
  workflow: ComfyWorkflow;
}

/**
 * ComfyUI generate and execute response interface
 */
export interface ComfyGenerateAndExecuteResponse {
  status?: string;
  prompt_id: string;
  workflow?: ComfyWorkflow;
  images?: string[];
  result?: any;
}

/**
 * ComfyUI models response interface
 */
export interface ComfyModelsResponse {
  models: ModelRegistry;
}

/**
 * ComfyUI store state interface
 */
export interface ComfyUIStoreState {
  // Models
  models: ModelRegistry;
  
  // Current generation
  currentParams: GenerationParams | null;
  currentWorkflow: ComfyWorkflow | null;
  
  // Execution status
  isGenerating: boolean;
  currentPromptId: string | null;
  
  // Results
  previewImage: string | null;
  finalImages: string[];
  
  // UI state
  loading: boolean;
  error: string | null;
  
  // Server status
  serverStatus: ComfyStatusResponse | null;
  isServerAvailable: boolean;
}

/**
 * Sampler options for the generation form
 */
export interface SamplerOption {
  value: string;
  label: string;
}

/**
 * Model option for the generation form
 */
export interface ModelOption {
  value: string;
  label: string;
  type: string;
}

/**
 * Form validation errors interface
 */
export interface FormErrors {
  [key: string]: string[];
}

/**
 * Generation form state interface
 */
export interface GenerationFormState {
  params: GenerationParams;
  errors: FormErrors;
  isValid: boolean;
  isSubmitting: boolean;
}
