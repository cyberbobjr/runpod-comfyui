<!-- filepath: f:\runpod-comfyui\front\src\components\ChangePasswordComponent.vue -->
<template>
  <div class="space-y-6 p-4 bg-background">
    <div class="card">
      <div class="flex items-center gap-3 mb-6">
        <FontAwesomeIcon icon="key" class="text-primary text-2xl" />
        <h1 class="text-2xl font-bold text-heading">Change Password</h1>
      </div>

      <div v-if="message" :class="messageClass" class="p-4 rounded-lg mb-6 flex items-center gap-2">
        <FontAwesomeIcon :icon="messageIcon" />
        <span>{{ message }}</span>
      </div>

      <form @submit.prevent="changePassword" class="space-y-6">
        <!-- Current Username -->
        <div>
          <label class="form-label">
            <FontAwesomeIcon icon="user" class="mr-2" />
            Current Username
          </label>
          <input
            v-model="form.oldUsername"
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
              v-model="form.oldPassword"
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
              <FontAwesomeIcon :icon="showCurrentPassword ? 'eye-slash' : 'eye'" />
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
            v-model="form.newUsername"
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
              v-model="form.newPassword"
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
              <FontAwesomeIcon :icon="showNewPassword ? 'eye-slash' : 'eye'" />
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
              <FontAwesomeIcon :icon="showConfirmPassword ? 'eye-slash' : 'eye'" />
            </button>
          </div>
          <p v-if="confirmPassword && !passwordsMatch" class="text-sm text-red-400 mt-1">
            Passwords do not match
          </p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4">
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <FontAwesomeIcon v-if="loading" icon="spinner" class="animate-spin" />
            <FontAwesomeIcon v-else icon="save" />
            {{ loading ? 'Changing...' : 'Change Password' }}
          </button>
          
          <button
            type="button"
            @click="resetForm"
            class="btn btn-default flex items-center gap-2"
          >
            <FontAwesomeIcon icon="undo" />
            Reset
          </button>
        </div>
      </form>

      <!-- Help Text -->
      <div class="mt-8 p-4 bg-background-mute rounded-lg">
        <h3 class="font-semibold text-text-light mb-2 flex items-center gap-2">
          <FontAwesomeIcon icon="info-circle" class="text-secondary" />
          Security Tips
        </h3>
        <ul class="text-sm text-text-muted space-y-1">
          <li>• Use a strong, unique password</li>
          <li>• Include a mix of letters, numbers, and symbols</li>
          <li>• Avoid using personal information</li>
          <li>• Your password is encrypted and cannot be recovered</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'ChangePasswordComponent',
  data() {
    return {
      form: {
        oldUsername: '',
        oldPassword: '',
        newUsername: '',
        newPassword: ''
      },
      confirmPassword: '',
      loading: false,
      message: '',
      messageType: 'info',
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false
    }
  },
  computed: {
    passwordsMatch() {
      return this.form.newPassword === this.confirmPassword
    },
    isFormValid() {
      return this.form.oldUsername.trim() &&
             this.form.oldPassword &&
             this.form.newUsername.trim() &&
             this.form.newPassword.length >= 4 &&
             this.passwordsMatch
    },
    messageClass() {
      const baseClass = 'border-l-4'
      switch (this.messageType) {
        case 'success':
          return `${baseClass} border-green-500 bg-green-900/20 text-green-300`
        case 'error':
          return `${baseClass} border-red-500 bg-red-900/20 text-red-300`
        case 'warning':
          return `${baseClass} border-yellow-500 bg-yellow-900/20 text-yellow-300`
        default:
          return `${baseClass} border-secondary bg-blue-900/20 text-secondary`
      }
    },
    messageIcon() {
      switch (this.messageType) {
        case 'success':
          return 'check-circle'
        case 'error':
          return 'exclamation-circle'
        case 'warning':
          return 'exclamation-triangle'
        default:
          return 'info-circle'
      }
    }
  },
  methods: {
    async changePassword() {
      if (!this.isFormValid) return

      this.loading = true
      this.message = ''

      try {
        await api.post('/models/change_user', {
          old_username: this.form.oldUsername,
          old_password: this.form.oldPassword,
          new_username: this.form.newUsername,
          new_password: this.form.newPassword
        })

        this.showMessage('Password changed successfully! Please log in again with your new credentials.', 'success')
        
        // Clear form after success
        this.resetForm()
        
        // Redirect to login after a delay
        setTimeout(() => {
          localStorage.removeItem('auth_token')
          this.$router.push({ name: 'login' })
        }, 2000)

      } catch (error) {
        console.error('Error changing password:', error)
        
        if (error.response?.status === 401) {
          this.showMessage('Invalid current username or password.', 'error')
        } else if (error.response?.status === 409) {
          this.showMessage('Username already exists. Please choose a different username.', 'error')
        } else {
          this.showMessage('Failed to change password. Please try again.', 'error')
        }
      } finally {
        this.loading = false
      }
    },
    
    resetForm() {
      this.form = {
        oldUsername: '',
        oldPassword: '',
        newUsername: '',
        newPassword: ''
      }
      this.confirmPassword = ''
      this.message = ''
      this.showCurrentPassword = false
      this.showNewPassword = false
      this.showConfirmPassword = false
    },
    
    showMessage(text, type = 'info') {
      this.message = text
      this.messageType = type
    }
  }
}
</script>