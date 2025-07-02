<template>
  <div class="space-y-6 p-4 bg-background">
    <div class="card">
      <div class="flex items-center gap-3 mb-6">
        <FontAwesomeIcon icon="cog" class="text-primary text-2xl" />
        <h1 class="text-2xl font-bold text-heading">Settings</h1>
      </div>

      <div
        v-if="message"
        :class="messageClass"
        class="p-4 rounded-lg mb-6 flex items-center gap-2"
      >
        <FontAwesomeIcon :icon="messageIcon" />
        <span>{{ message }}</span>
      </div>
      <!-- Base Directory Configuration Accordion -->
      <AccordionComponent
        title="Base Directory Configuration"
        icon="folder"
        :default-open="true"
        class="mb-4"
      >
        <form @submit.prevent="updateBaseDir" class="space-y-4">
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="folder-open" class="mr-2" />
              BASE_DIR
            </label>
            <input
              v-model="baseDirForm.base_dir"
              type="text"
              class="form-input"
              placeholder="Enter base directory path"
              required
            />
            <p class="text-sm text-text-muted mt-1">
              Current source: {{ baseDirSource }}
            </p>
          </div>
          <button
            type="submit"
            :disabled="baseDirLoading"
            class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <FontAwesomeIcon
              v-if="baseDirLoading"
              icon="spinner"
              class="animate-spin"
            />
            <FontAwesomeIcon v-else icon="save" />
            {{ baseDirLoading ? "Updating..." : "Update Base Directory" }}
          </button>
        </form>
      </AccordionComponent>

      <!-- API Tokens Configuration Accordion -->
      <AccordionComponent
        title="API Tokens Configuration"
        icon="key"
        :default-open="false"
        class="mb-4"
      >
        <form @submit.prevent="updateTokens" class="space-y-4">
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="cloud" class="mr-2" />
              HuggingFace Token
            </label>
            <div class="relative">
              <input
                v-model="tokensForm.hf_token"
                :type="showHfToken ? 'text' : 'password'"
                class="form-input pr-12"
                placeholder="Enter your HuggingFace token (optional)"
              />
              <button
                type="button"
                @click="showHfToken = !showHfToken"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-light"
              >
                <FontAwesomeIcon :icon="showHfToken ? 'eye-slash' : 'eye'" />
              </button>
            </div>
            <p class="text-sm text-text-muted mt-1">
              Required for downloading models from HuggingFace
            </p>
          </div>

          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="download" class="mr-2" />
              CivitAI Token
            </label>
            <div class="relative">
              <input
                v-model="tokensForm.civitai_token"
                :type="showCivitaiToken ? 'text' : 'password'"
                class="form-input pr-12"
                placeholder="Enter your CivitAI token (optional)"
              />
              <button
                type="button"
                @click="showCivitaiToken = !showCivitaiToken"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-light"
              >
                <FontAwesomeIcon
                  :icon="showCivitaiToken ? 'eye-slash' : 'eye'"
                />
              </button>
            </div>
            <p class="text-sm text-text-muted mt-1">
              Required for downloading models from CivitAI
            </p>
          </div>

          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="tokensLoading"
              class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <FontAwesomeIcon
                v-if="tokensLoading"
                icon="spinner"
                class="animate-spin"
              />
              <FontAwesomeIcon v-else icon="save" />
              {{ tokensLoading ? "Updating..." : "Update Tokens" }}
            </button>

            <button
              type="button"
              @click="resetTokensForm"
              class="btn btn-primary flex items-center gap-2"
            >
              <FontAwesomeIcon icon="undo" />
              Reset
            </button>
          </div>
        </form>
      </AccordionComponent>

      <!-- Password Change Accordion -->
      <AccordionComponent
        title="Change Password"
        icon="key"
        :default-open="false"
        class="mb-4"
      >
        <form @submit.prevent="changePassword" class="space-y-6">
          <!-- Current Username -->
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="user" class="mr-2" />
              Current Username
            </label>
            <input
              v-model="passwordForm.oldUsername"
              type="text"
              class="form-input"
              required
              autocomplete="username"
            />
          </div>

          <!-- Current Password -->
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="lock" class="mr-2" />
              Current Password
            </label>
            <div class="relative">
              <input
                v-model="passwordForm.oldPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                class="form-input pr-12"
                required
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showCurrentPassword = !showCurrentPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-light"
              >
                <FontAwesomeIcon
                  :icon="showCurrentPassword ? 'eye-slash' : 'eye'"
                />
              </button>
            </div>
          </div>

          <!-- New Username -->
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="user-edit" class="mr-2" />
              New Username
            </label>
            <input
              v-model="passwordForm.newUsername"
              type="text"
              class="form-input"
              required
              autocomplete="username"
            />
          </div>

          <!-- New Password -->
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="key" class="mr-2" />
              New Password
            </label>
            <div class="relative">
              <input
                v-model="passwordForm.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                class="form-input pr-12"
                required
                autocomplete="new-password"
                minlength="4"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-light"
              >
                <FontAwesomeIcon
                  :icon="showNewPassword ? 'eye-slash' : 'eye'"
                />
              </button>
            </div>
            <p class="text-sm text-text-muted mt-1">Minimum 4 characters</p>
          </div>

          <!-- Confirm New Password -->
          <div>
            <label class="form-label">
              <FontAwesomeIcon icon="shield-alt" class="mr-2" />
              Confirm New Password
            </label>
            <div class="relative">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                class="form-input pr-12"
                required
                minlength="4"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-light"
              >
                <FontAwesomeIcon
                  :icon="showConfirmPassword ? 'eye-slash' : 'eye'"
                />
              </button>
            </div>
            <p
              v-if="confirmPassword && !passwordsMatch"
              class="text-sm text-red-400 mt-1"
            >
              Passwords do not match
            </p>
          </div>

          <!-- Submit Button -->
          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="passwordLoading || !isPasswordFormValid"
              class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <FontAwesomeIcon
                v-if="passwordLoading"
                icon="spinner"
                class="animate-spin"
              />
              <FontAwesomeIcon v-else icon="save" />
              {{ passwordLoading ? "Changing..." : "Change Password" }}
            </button>
            <button
              type="button"
              @click="resetPasswordForm"
              class="btn btn-primary flex items-center gap-2"
            >
              <FontAwesomeIcon icon="undo" />
              Reset
            </button>
          </div>
        </form>
        <!-- Help Text -->
        <div class="mt-8 p-4 bg-background-mute rounded-lg">
          <h3
            class="font-semibold text-text-light mb-2 flex items-center gap-2"
          >
            <FontAwesomeIcon icon="info-circle" class="text-secondary" />
            Security Tips
          </h3>
          <ul class="text-sm text-text-muted space-y-1">
            <li>• Use a strong, unique password</li>
            <li>• Include a mix of letters, numbers, and symbols</li>
            <li>• Avoid using personal information</li>
            <li>• Your password is encrypted and cannot be recovered</li>
            <li>• BASE_DIR changes are saved to a user-specific config file</li>
            <li>
              • API tokens are stored securely and used for downloading models
            </li>
            <li>
              • HuggingFace tokens allow access to gated models and private
              repositories
            </li>
            <li>
              • CivitAI tokens are required for downloading some models from
              CivitAI
            </li>
          </ul>
        </div>
      </AccordionComponent>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from "../services/api.js";
import AccordionComponent from "./common/AccordionComponent.vue";

// === ROUTER ===
const router = useRouter();

/**
 * SettingsComponent
 * -----------------------------------------------------------------------------
 * A comprehensive settings management component for application configuration.
 * Handles base directory settings, API tokens, and user authentication credentials.
 *
 * ## Features & Behavior
 * - Base directory configuration with source tracking
 * - API token management for Hugging Face and CivitAI
 * - User authentication (username/password) management
 * - Real-time form validation and error handling
 * - Secure password input with visibility toggles
 * - Responsive accordion layout for organized settings
 * - Success/error messaging with visual feedback
 * - Auto-loading of current configuration on mount
 *
 * ## State Management
 * - Local reactive state for form data and UI state
 * - Computed properties for validation and styling
 * - RESTful API integration for persistence
 * - Loading states for async operations
 *
 * ## Methods
 * ### loadConfig
 * **Description:** Loads current configuration from the API.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### updateBaseDir
 * **Description:** Updates the base directory configuration.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### updateTokens
 * **Description:** Updates API tokens for external services.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### updateCredentials
 * **Description:** Updates user authentication credentials.
 * **Parameters:** None
 * **Returns:** Promise<void>
 *
 * ### showMessage
 * **Description:** Displays a status message to the user.
 * **Parameters:**
 * - `message` (string): The message to display.
 * - `type` (MessageType): The type of message (success, error, warning, info).
 * **Returns:** void
 *
 * ### togglePasswordVisibility
 * **Description:** Toggles password field visibility for different inputs.
 * **Parameters:**
 * - `field` (string): The password field to toggle.
 * **Returns:** void
 */

/**
 * Message type enum
 */
type MessageType = 'success' | 'error' | 'warning' | 'info';

/**
 * Base directory form interface
 */
interface BaseDirForm {
  base_dir: string;
}

/**
 * API tokens form interface
 */
interface TokensForm {
  hf_token: string;
  civitai_token: string;
}

/**
 * Password form interface
 */
interface PasswordForm {
  oldUsername: string;
  oldPassword: string;
  newUsername: string;
  newPassword: string;
}

/**
 * Configuration response interface
 */
interface ConfigResponse {
  BASE_DIR: string;
  source: string;
}

/**
 * Tokens response interface
 */
interface TokensResponse {
  hf_token: string;
  civitai_token: string;
}

// --- Reactive State ---
// Base Directory form
const baseDirForm = ref<BaseDirForm>({
  base_dir: "",
});
const baseDirSource = ref<string>("");
const baseDirLoading = ref<boolean>(false);

// API Tokens form
const tokensForm = ref<TokensForm>({
  hf_token: "",
  civitai_token: "",
});
const tokensLoading = ref<boolean>(false);
const showHfToken = ref<boolean>(false);
const showCivitaiToken = ref<boolean>(false);

// Password form
const passwordForm = ref<PasswordForm>({
  oldUsername: "",
  oldPassword: "",
  newUsername: "",
  newPassword: "",
});
const confirmPassword = ref<string>("");
const passwordLoading = ref<boolean>(false);

// UI state
const message = ref<string>("");
const messageType = ref<MessageType>("info");
const showCurrentPassword = ref<boolean>(false);
const showNewPassword = ref<boolean>(false);
const showConfirmPassword = ref<boolean>(false);

// --- Computed Properties ---
const passwordsMatch = computed((): boolean =>
  passwordForm.value.newPassword === confirmPassword.value
);

const isPasswordFormValid = computed((): boolean =>
  !!passwordForm.value.oldUsername.trim() &&
  !!passwordForm.value.oldPassword &&
  !!passwordForm.value.newUsername.trim() &&
  passwordForm.value.newPassword.length >= 4 &&
  !!passwordsMatch.value
);

const messageClass = computed((): string => {
  const baseClass = "border-l-4";
  switch (messageType.value) {
    case "success":
      return `${baseClass} border-green-500 bg-green-900/20 text-green-300`;
    case "error":
      return `${baseClass} border-red-500 bg-red-900/20 text-red-300`;
    case "warning":
      return `${baseClass} border-yellow-500 bg-yellow-900/20 text-yellow-300`;
    default:
      return `${baseClass} border-secondary bg-blue-900/20 text-secondary`;
  }
});

const messageIcon = computed((): string => {
  switch (messageType.value) {
    case "success":
      return "check-circle";
    case "error":
      return "exclamation-circle";
    case "warning":
      return "exclamation-triangle";
    default:
      return "info-circle";
  }
});

// === METHODS ===

/**
 * Load configuration from API
 */
const loadConfig = async (): Promise<void> => {
  try {
    // Load base directory config
    const configResponse = await api.get("/jsonmodels/config");
    baseDirForm.value.base_dir = configResponse.data.BASE_DIR;
    baseDirSource.value = configResponse.data.source;

    // Load API tokens
    const tokensResponse = await api.get("/models/tokens");
    tokensForm.value.hf_token = tokensResponse.data.hf_token || "";
    tokensForm.value.civitai_token = tokensResponse.data.civitai_token || "";
  } catch (error: any) {
    console.error("Error loading config:", error);
    showMessage("Failed to load configuration.", "error");
  }
};

/**
 * Update base directory configuration
 */
const updateBaseDir = async (): Promise<void> => {
  if (!baseDirForm.value.base_dir.trim()) return;

  baseDirLoading.value = true;
  message.value = "";

  try {
    await api.post("/jsonmodels/config", {
      base_dir: baseDirForm.value.base_dir,
    });

    showMessage("Base directory updated successfully!", "success");

    // Reload config to get updated source
    await loadConfig();
  } catch (error: any) {
    console.error("Error updating base directory:", error);
    showMessage(
      "Failed to update base directory. Please try again.",
      "error"
    );
  } finally {
    baseDirLoading.value = false;
  }
};

/**
 * Update API tokens
 */
const updateTokens = async (): Promise<void> => {
  tokensLoading.value = true;
  message.value = "";

  try {
    await api.post("/models/tokens", {
      hf_token: tokensForm.value.hf_token || null,
      civitai_token: tokensForm.value.civitai_token || null,
    });

    showMessage("API tokens updated successfully!", "success");
  } catch (error: any) {
    console.error("Error updating tokens:", error);
    showMessage("Failed to update API tokens. Please try again.", "error");
  } finally {
    tokensLoading.value = false;
  }
};

/**
 * Reset tokens form
 */
const resetTokensForm = (): void => {
  tokensForm.value = {
    hf_token: "",
    civitai_token: "",
  };
  showHfToken.value = false;
  showCivitaiToken.value = false;
};

/**
 * Change user password
 */
const changePassword = async (): Promise<void> => {
  if (!isPasswordFormValid.value) return;

  passwordLoading.value = true;
  message.value = "";

  try {
    await api.post("/models/change_user", {
      old_username: passwordForm.value.oldUsername,
      old_password: passwordForm.value.oldPassword,
      new_username: passwordForm.value.newUsername,
      new_password: passwordForm.value.newPassword,
    });

    showMessage(
      "Password changed successfully! Please log in again with your new credentials.",
      "success"
    );

    // Clear form after success
    resetPasswordForm();

    // Redirect to login after a delay
    setTimeout(() => {
      localStorage.removeItem("auth_token");
      router.push({ name: "login" });
    }, 2000);
  } catch (error: any) {
    console.error("Error changing password:", error);

    if (error.response?.status === 401) {
      showMessage("Invalid current username or password.", "error");
    } else if (error.response?.status === 409) {
      showMessage(
        "Username already exists. Please choose a different username.",
        "error"
      );
    } else {
      showMessage(
        "Failed to change password. Please try again.",
        "error"
      );
    }
  } finally {
    passwordLoading.value = false;
  }
};

/**
 * Reset password form
 */
const resetPasswordForm = (): void => {
  passwordForm.value = {
    oldUsername: "",
    oldPassword: "",
    newUsername: "",
    newPassword: "",
  };
  confirmPassword.value = "";
  showCurrentPassword.value = false;
  showNewPassword.value = false;
  showConfirmPassword.value = false;
};

/**
 * Show message to user
 */
const showMessage = (text: string, type: MessageType = "info"): void => {
  message.value = text;
  messageType.value = type;
};

// === LIFECYCLE ===

onMounted(() => {
  loadConfig();
});
</script>
