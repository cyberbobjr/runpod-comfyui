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
          </div>          <button
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
            {{ baseDirLoading ? "Updating..." : "Update Base Directory" }}</button>
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
                <FontAwesomeIcon :icon="showCivitaiToken ? 'eye-slash' : 'eye'" />
              </button>
            </div>
            <p class="text-sm text-text-muted mt-1">
              Required for downloading models from CivitAI
            </p>
          </div>

          <div class="flex gap-4">            <button
              type="submit"
              :disabled="tokensLoading"
              class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <FontAwesomeIcon v-if="tokensLoading" icon="spinner" class="animate-spin" />
              <FontAwesomeIcon v-else icon="save" />
              {{ tokensLoading ? 'Updating...' : 'Update Tokens' }}
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
            </button>            <button
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
          </h3>          <ul class="text-sm text-text-muted space-y-1">
            <li>• Use a strong, unique password</li>
            <li>• Include a mix of letters, numbers, and symbols</li>
            <li>• Avoid using personal information</li>
            <li>• Your password is encrypted and cannot be recovered</li>
            <li>• BASE_DIR changes are saved to a user-specific config file</li>
            <li>• API tokens are stored securely and used for downloading models</li>
            <li>• HuggingFace tokens allow access to gated models and private repositories</li>
            <li>• CivitAI tokens are required for downloading some models from CivitAI</li>
          </ul>
        </div>
      </AccordionComponent>
    </div>
  </div>
</template>

<script>
import api from "../services/api.js";
import AccordionComponent from "./common/AccordionComponent.vue";

export default {
  name: "SettingsComponent",
  components: {
    AccordionComponent,
  },
  data() {
    return {      // Base Directory form
      baseDirForm: {
        base_dir: "",
      },
      baseDirSource: "",
      baseDirLoading: false,

      // API Tokens form
      tokensForm: {
        hf_token: "",
        civitai_token: "",
      },
      tokensLoading: false,
      showHfToken: false,
      showCivitaiToken: false,

      // Password form
      passwordForm: {
        oldUsername: "",
        oldPassword: "",
        newUsername: "",
        newPassword: "",
      },
      confirmPassword: "",
      passwordLoading: false,

      // UI state
      message: "",
      messageType: "info",
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
    };
  },
  computed: {
    passwordsMatch() {
      return this.passwordForm.newPassword === this.confirmPassword;
    },
    isPasswordFormValid() {
      return (
        this.passwordForm.oldUsername.trim() &&
        this.passwordForm.oldPassword &&
        this.passwordForm.newUsername.trim() &&
        this.passwordForm.newPassword.length >= 4 &&
        this.passwordsMatch
      );
    },
    messageClass() {
      const baseClass = "border-l-4";
      switch (this.messageType) {
        case "success":
          return `${baseClass} border-green-500 bg-green-900/20 text-green-300`;
        case "error":
          return `${baseClass} border-red-500 bg-red-900/20 text-red-300`;
        case "warning":
          return `${baseClass} border-yellow-500 bg-yellow-900/20 text-yellow-300`;
        default:
          return `${baseClass} border-secondary bg-blue-900/20 text-secondary`;
      }
    },
    messageIcon() {
      switch (this.messageType) {
        case "success":
          return "check-circle";
        case "error":
          return "exclamation-circle";
        case "warning":
          return "exclamation-triangle";
        default:
          return "info-circle";
      }
    },
  },
  async mounted() {
    await this.loadConfig();
  },
  methods: {    async loadConfig() {
      try {
        // Load base directory config
        const configResponse = await api.get("/jsonmodels/config");
        this.baseDirForm.base_dir = configResponse.data.BASE_DIR;
        this.baseDirSource = configResponse.data.source;

        // Load API tokens
        const tokensResponse = await api.get("/models/tokens");
        this.tokensForm.hf_token = tokensResponse.data.hf_token || "";
        this.tokensForm.civitai_token = tokensResponse.data.civitai_token || "";
      } catch (error) {
        console.error("Error loading config:", error);
        this.showMessage("Failed to load configuration.", "error");
      }
    },

    async updateBaseDir() {
      if (!this.baseDirForm.base_dir.trim()) return;

      this.baseDirLoading = true;
      this.message = "";

      try {
        await api.post("/jsonmodels/config", {
          base_dir: this.baseDirForm.base_dir,
        });

        this.showMessage("Base directory updated successfully!", "success");

        // Reload config to get updated source
        await this.loadConfig();
      } catch (error) {
        console.error("Error updating base directory:", error);
        this.showMessage(
          "Failed to update base directory. Please try again.",
          "error"
        );      } finally {
        this.baseDirLoading = false;
      }
    },

    async updateTokens() {
      this.tokensLoading = true;
      this.message = "";

      try {
        await api.post("/models/tokens", {
          hf_token: this.tokensForm.hf_token || null,
          civitai_token: this.tokensForm.civitai_token || null,
        });

        this.showMessage("API tokens updated successfully!", "success");
      } catch (error) {
        console.error("Error updating tokens:", error);
        this.showMessage("Failed to update API tokens. Please try again.", "error");
      } finally {
        this.tokensLoading = false;
      }
    },

    resetTokensForm() {
      this.tokensForm = {
        hf_token: "",
        civitai_token: "",
      };
      this.showHfToken = false;
      this.showCivitaiToken = false;
    },

    async changePassword() {
      if (!this.isPasswordFormValid) return;

      this.passwordLoading = true;
      this.message = "";

      try {
        await api.post("/models/change_user", {
          old_username: this.passwordForm.oldUsername,
          old_password: this.passwordForm.oldPassword,
          new_username: this.passwordForm.newUsername,
          new_password: this.passwordForm.newPassword,
        });

        this.showMessage(
          "Password changed successfully! Please log in again with your new credentials.",
          "success"
        );

        // Clear form after success
        this.resetPasswordForm();

        // Redirect to login after a delay
        setTimeout(() => {
          localStorage.removeItem("auth_token");
          this.$router.push({ name: "login" });
        }, 2000);
      } catch (error) {
        console.error("Error changing password:", error);

        if (error.response?.status === 401) {
          this.showMessage("Invalid current username or password.", "error");
        } else if (error.response?.status === 409) {
          this.showMessage(
            "Username already exists. Please choose a different username.",
            "error"
          );
        } else {
          this.showMessage(
            "Failed to change password. Please try again.",
            "error"
          );
        }
      } finally {
        this.passwordLoading = false;
      }
    },

    resetPasswordForm() {
      this.passwordForm = {
        oldUsername: "",
        oldPassword: "",
        newUsername: "",
        newPassword: "",
      };
      this.confirmPassword = "";
      this.showCurrentPassword = false;
      this.showNewPassword = false;
      this.showConfirmPassword = false;
    },

    showMessage(text, type = "info") {
      this.message = text;
      this.messageType = type;
    },
  },
};
</script>
