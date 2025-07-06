/**
 * ComfyUI Store - Pinia Store
 *
 * Store for managing ComfyUI workflow generation and execution.
 * Handles communication with the backend API and manages state
 * for the ComfyUI interface.
 *
 * @author ComfyUI Integration
 * @version 1.0.0
 */

import { defineStore } from "pinia";
import type {
  ComfyUIStoreState,
  GenerationParams,
  ComfyWorkflow,
  ComfyExecutionResult,
  ComfyStatusResponse,
  ComfyGenerationResponse,
  ComfyGenerateAndExecuteResponse,
  ComfyModelsResponse,
  ModelRegistry,
  SamplerOption,
  ModelOption
} from "./types/comfyui.types";

const { default: api } = await import("@/services/api");

export const useComfyUIStore = defineStore("comfyui", {
  // === STATE ===
  state: (): ComfyUIStoreState => ({
    // Models
    models: {},
    
    // Current generation
    currentParams: null,
    currentWorkflow: null,
    
    // Execution status
    isGenerating: false,
    currentPromptId: null,
    
    // Results
    previewImage: null,
    finalImages: [],
    
    // UI state
    loading: false,
    error: null,
    
    // Server status
    serverStatus: null,
    isServerAvailable: false,
  }),

  // === GETTERS ===
  getters: {
    /**
     * Get available models as options for form dropdown
     */
    modelOptions(): ModelOption[] {
      return Object.entries(this.models).map(([key, model]) => ({
        value: key,
        label: key.toUpperCase(),
        type: model.model_type
      }));
    },

    /**
     * Get available samplers as options for form dropdown
     */
    samplerOptions(): SamplerOption[] {
      return [
        { value: "euler", label: "Euler" },
        { value: "euler_ancestral", label: "Euler Ancestral" },
        { value: "dpm_2", label: "DPM 2" },
        { value: "dpm_2_ancestral", label: "DPM 2 Ancestral" },
        { value: "lms", label: "LMS" },
        { value: "dpm_fast", label: "DPM Fast" },
        { value: "dpm_adaptive", label: "DPM Adaptive" },
        { value: "dpmpp_2s_ancestral", label: "DPM++ 2S Ancestral" },
        { value: "dpmpp_sde", label: "DPM++ SDE" },
        { value: "dpmpp_2m", label: "DPM++ 2M" },
      ];
    },

    /**
     * Check if generation is possible
     */
    canGenerate(): boolean {
      return this.isServerAvailable && !this.isGenerating && this.currentParams !== null;
    },

    /**
     * Get current generation progress
     */
    generationProgress(): string {
      if (!this.isGenerating) return "Ready";
      if (this.previewImage) return "Generating...";
      return "Initializing...";
    },
  },

  // === ACTIONS ===
  actions: {
    /**
     * Initialize the ComfyUI store
     * **Description:** Loads models and checks server status
     */
    async initialize() {
      this.loading = true;
      this.error = null;
      
      try {
        await Promise.all([
          this.loadModels(),
          this.checkServerStatus()
        ]);
      } catch (error) {
        console.error("Error initializing ComfyUI store:", error);
        this.error = error instanceof Error ? error.message : "Failed to initialize ComfyUI";
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load available models from the API
     * **Description:** Fetches the model registry from the backend
     */
    async loadModels() {
      try {
        const response = await api.get<ComfyModelsResponse>("/comfy/models");
        this.models = response.data.models;
      } catch (error) {
        console.error("Error loading models:", error);
        throw new Error("Failed to load models");
      }
    },

    /**
     * Check ComfyUI server status
     * **Description:** Verifies that the ComfyUI server is available
     */
    async checkServerStatus() {
      try {
        const response = await api.get<ComfyStatusResponse>("/comfy/status");
        this.serverStatus = response.data;
        this.isServerAvailable = response.data.status === "available";
      } catch (error) {
        console.error("Error checking server status:", error);
        this.serverStatus = null;
        this.isServerAvailable = false;
      }
    },

    /**
     * Generate workflow from parameters
     * **Description:** Creates a ComfyUI workflow from generation parameters
     * **Parameters:**
     * - params (GenerationParams): The generation parameters
     * **Returns:** Generated workflow object
     */
    async generateWorkflow(params: GenerationParams): Promise<ComfyWorkflow> {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post<ComfyGenerationResponse>("/comfy/workflow/generate", params);
        this.currentWorkflow = response.data.workflow;
        this.currentParams = params;
        return response.data.workflow;
      } catch (error) {
        console.error("Error generating workflow:", error);
        this.error = error instanceof Error ? error.message : "Failed to generate workflow";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Execute a workflow
     * **Description:** Sends a workflow to ComfyUI for execution
     * **Parameters:**
     * - workflow (ComfyWorkflow): The workflow to execute
     * **Returns:** Execution result
     */
    async executeWorkflow(workflow: ComfyWorkflow): Promise<ComfyExecutionResult> {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.post<ComfyExecutionResult>("/comfy/workflow/execute", workflow);
        this.finalImages = response.data.images;
        return response.data;
      } catch (error) {
        console.error("Error executing workflow:", error);
        this.error = error instanceof Error ? error.message : "Failed to execute workflow";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Generate and execute workflow in one call
     * **Description:** Convenience method that generates and executes a workflow
     * **Parameters:**
     * - params (GenerationParams): The generation parameters
     * **Returns:** Execution result or prompt ID for async execution
     */
    async generateAndExecute(params: GenerationParams): Promise<ComfyGenerateAndExecuteResponse> {
      this.isGenerating = true;
      this.error = null;
      this.previewImage = null;
      this.finalImages = [];
      
      try {
        const response = await api.post<ComfyGenerateAndExecuteResponse>("/comfy/generate-and-execute", params);
        
        this.currentParams = params;
        this.currentPromptId = response.data.prompt_id;
        
        if (response.data.workflow) {
          this.currentWorkflow = response.data.workflow;
        }
        
        if (response.data.images) {
          this.finalImages = response.data.images;
          this.isGenerating = false;
        }
        
        return response.data;
      } catch (error) {
        console.error("Error in generate and execute:", error);
        this.error = error instanceof Error ? error.message : "Failed to generate and execute";
        this.isGenerating = false;
        throw error;
      }
    },

    /**
     * Get result by prompt ID
     * **Description:** Retrieves the result of a specific prompt execution
     * **Parameters:**
     * - promptId (string): The prompt ID to get results for
     * **Returns:** Execution result
     */
    async getResultByPromptId(promptId: string): Promise<ComfyExecutionResult> {
      try {
        const response = await api.get<ComfyExecutionResult>(`/comfy/result/${promptId}`);
        
        if (response.data.images) {
          this.finalImages = response.data.images;
        }
        
        return response.data;
      } catch (error) {
        console.error("Error getting result:", error);
        throw error;
      }
    },

    /**
     * Set preview image
     * **Description:** Updates the preview image during generation
     * **Parameters:**
     * - imageUrl (string): The preview image URL
     */
    setPreviewImage(imageUrl: string) {
      this.previewImage = imageUrl;
    },

    /**
     * Set final images
     * **Description:** Updates the final generated images
     * **Parameters:**
     * - images (string[]): Array of final image URLs
     */
    setFinalImages(images: string[]) {
      this.finalImages = images;
      this.isGenerating = false;
    },

    /**
     * Reset generation state
     * **Description:** Clears the current generation state
     */
    resetGeneration() {
      this.currentParams = null;
      this.currentWorkflow = null;
      this.currentPromptId = null;
      this.previewImage = null;
      this.finalImages = [];
      this.isGenerating = false;
      this.error = null;
    },

    /**
     * Set error state
     * **Description:** Sets an error message
     * **Parameters:**
     * - error (string): The error message
     */
    setError(error: string) {
      this.error = error;
      this.isGenerating = false;
    },

    /**
     * Clear error state
     * **Description:** Clears the current error
     */
    clearError() {
      this.error = null;
    },

    /**
     * Get default generation parameters
     * **Description:** Returns a default set of generation parameters
     * **Returns:** Default GenerationParams object
     */
    getDefaultParams(): GenerationParams {
      const firstModel = Object.keys(this.models)[0];
      return {
        model_key: firstModel || "flux-dev",
        prompt: "",
        negative_prompt: "",
        sampler: "euler",
        steps: 30,
        cfg: 7.5,
        width: 1024,
        height: 1024,
        seed: null,
        loras: [],
        controlnet_image: null,
        controlnet_preprocessor: null,
        controlnet_model: null,
        init_image: null,
        inpaint_mask: null,
        outpaint_padding: null,
        enable_tea_cache: true,
        enable_clear_cache: true,
        add_details: false,
        wait: false,
      };
    },
  },
});
