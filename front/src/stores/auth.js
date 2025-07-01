import { defineStore } from 'pinia'
import api from '../services/api' // Assuming you have an api.js file for API requests

/**
 * Store Pinia for managing authentication and user state
 * Handles user login, logout, and session management
 */
export const useAuthStore = defineStore('auth', {
  // === STATE ===
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    token: localStorage.getItem('auth_token') || null,
    sessionExpiry: null,
    permissions: []
  }),

  // === GETTERS ===
  getters: {
    /**
     * Check if user has admin privileges
     * @returns {Boolean} True if user is admin
     */
    isAdmin: (state) => {
      return state.user && state.user.role === 'admin'
    },

    /**
     * Get user's display name
     * @returns {String} User's display name or email
     */
    userDisplayName: (state) => {
      if (!state.user) return ''
      return state.user.displayName || state.user.username || state.user.email || ''
    },

    /**
     * Check if authentication is required
     * @returns {Boolean} True if auth is required but user is not authenticated
     */
    authRequired: (state) => {
      return !state.isAuthenticated && state.token === null
    },

    /**
     * Check if user has specific permission
     * @returns {Function} Function that takes permission and returns boolean
     */
    hasPermission: (state) => (permission) => {
      return state.permissions.includes(permission) || state.user?.role === 'admin'
    },

    /**
     * Check if session is expired
     * @returns {Boolean} True if session is expired
     */
    isSessionExpired: (state) => {
      if (!state.sessionExpiry) return false
      return new Date() > new Date(state.sessionExpiry)
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Login user with credentials
     * @param {String} username - Username or email
     * @param {String} password - User password
     * @returns {Promise} Promise that resolves on successful login
     */
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('/auth/login', {
          username: username,
          password: password
        });

        // Stocker le token
        localStorage.setItem('auth_token', response.data.token);

        // Store token and user data
        this.token = response.data.token
        this.isAuthenticated = true

        return true;
      } catch (error) {
        this.error = error.message
        console.error('Login error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Logout current user
     * @returns {Promise} Promise that resolves when logout is complete
     */
    async logout() {
      this.loading = true

      try {
        if (this.token) {
          await api.post('/auth/logout')
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // Clear all auth data regardless of API call success
        this.token = null
        this.isAuthenticated = false
        this.error = null
        this.loading = false

        // Remove token from localStorage
        localStorage.removeItem('auth_token')
      }
    },

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise} Promise that resolves on successful registration
     */
    async register(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(userData)
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || 'Registration failed')
        }

        const data = await response.json()

        // Auto-login after successful registration
        if (data.token) {
          this.token = data.token
          this.user = data.user
          this.isAuthenticated = true
          this.permissions = data.permissions || []
          this.sessionExpiry = data.expiresAt
          localStorage.setItem('auth_token', data.token)
        }

        return data
      } catch (error) {
        this.error = error.message
        console.error('Registration error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Change user password
     * @param {String} currentPassword - Current password
     * @param {String} newPassword - New password
     * @returns {Promise} Promise that resolves when password is changed
     */
    async changePassword(currentPassword, newPassword) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/auth/change-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
          },
          body: JSON.stringify({ currentPassword, newPassword })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || 'Password change failed')
        }

        return await response.json()
      } catch (error) {
        this.error = error.message
        console.error('Password change error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update user profile
     * @param {Object} profileData - Updated profile data
     * @returns {Promise} Promise that resolves when profile is updated
     */
    async updateProfile(profileData) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/auth/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`
          },
          body: JSON.stringify(profileData)
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || 'Profile update failed')
        }

        const data = await response.json()
        this.user = { ...this.user, ...data.user }

        return data
      } catch (error) {
        this.error = error.message
        console.error('Profile update error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear auth error
     */
    clearError() {
      this.error = null
    },

    /**
     * Get authorization header for API requests
     * @returns {Object} Authorization header object
     */
    getAuthHeader() {
      if (!this.token) return {}
      return {
        'Authorization': `Bearer ${this.token}`
      }
    },

    /**
     * Check if user can perform action
     * @param {String} action - Action to check
     * @returns {Boolean} True if user can perform action
     */
    canPerform(action) {
      if (!this.isAuthenticated) return false
      if (this.isAdmin) return true
      return this.permissions.includes(action)
    },

    /**
     * Set user permissions
     * @param {Array} permissions - Array of permission strings
     */
    setPermissions(permissions) {
      this.permissions = permissions
    },

    /**
     * Update user data
     * @param {Object} userData - Updated user data
     */
    updateUser(userData) {
      this.user = { ...this.user, ...userData }
    }
  }
})
