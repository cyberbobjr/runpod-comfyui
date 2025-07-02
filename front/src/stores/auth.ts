/**
 * Authentication Store
 * 
 * Pinia store for managing user authentication, session management,
 * and authorization with TypeScript support.
 * 
 * @author TypeScript Migration
 * @version 1.0.0
 */

import { defineStore } from 'pinia'
import api from '../services/api'

/**
 * User role types
 */
export type UserRole = 'admin' | 'user' | 'guest'

/**
 * User permission types
 */
export type Permission = 
  | 'read_models' 
  | 'write_models' 
  | 'delete_models' 
  | 'admin_access'
  | 'user_management'

/**
 * User interface
 */
export interface User {
  id: string | number
  username: string
  email?: string
  displayName?: string
  role: UserRole
  avatar?: string
  createdAt?: string
  lastLogin?: string
}

/**
 * Authentication response interface
 */
export interface AuthResponse {
  token: string
  user: User
  permissions?: Permission[]
  expiresAt?: string
}

/**
 * Registration data interface
 */
export interface RegistrationData {
  username: string
  email: string
  password: string
  displayName?: string
}

/**
 * Profile update data interface
 */
export interface ProfileUpdateData {
  displayName?: string
  email?: string
  avatar?: string
}

/**
 * Auth store state interface
 */
export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  token: string | null
  sessionExpiry: string | null
  permissions: Permission[]
}

/**
 * Auth store getters interface
 */
export interface AuthGetters {
  isAdmin: boolean
  userDisplayName: string
  authRequired: boolean
  hasPermission: (permission: Permission) => boolean
  isSessionExpired: boolean
}

/**
 * Authentication Store
 * Handles user login, logout, registration, and session management
 */
export const useAuthStore = defineStore('auth', {
  // === STATE ===
  state: (): AuthState => ({
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
     * @returns True if user is admin
     */
    isAdmin: (state): boolean => {
      return state.user?.role === 'admin' || false
    },

    /**
     * Get user's display name
     * @returns User's display name or username
     */
    userDisplayName: (state): string => {
      if (!state.user) return ''
      return state.user.displayName || state.user.username || state.user.email || ''
    },

    /**
     * Check if authentication is required
     * @returns True if auth is required but user is not authenticated
     */
    authRequired: (state): boolean => {
      return !state.isAuthenticated && state.token === null
    },

    /**
     * Check if user has specific permission
     * @returns Function that takes permission and returns boolean
     */
    hasPermission: (state) => (permission: Permission): boolean => {
      return state.permissions.includes(permission) || state.user?.role === 'admin'
    },

    /**
     * Check if session is expired
     * @returns True if session is expired
     */
    isSessionExpired: (state): boolean => {
      if (!state.sessionExpiry) return false
      return new Date() > new Date(state.sessionExpiry)
    }
  },

  // === ACTIONS ===
  actions: {
    /**
     * Login user with credentials
     * @param username - Username or email
     * @param password - User password
     * @returns Promise that resolves on successful login
     */
    async login(username: string, password: string): Promise<boolean> {
      this.loading = true
      this.error = null

      try {
        const response = await api.post<AuthResponse>('/auth/login', {
          username,
          password
        })

        // Store token and user data
        this.token = response.data.token
        this.user = response.data.user
        this.isAuthenticated = true
        this.permissions = response.data.permissions || []
        this.sessionExpiry = response.data.expiresAt || null

        // Store token in localStorage
        localStorage.setItem('auth_token', response.data.token)

        return true
      } catch (error: any) {
        this.error = error.message || 'Login failed'
        console.error('Login error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Logout user and clear session
     * @param redirect - Whether to redirect after logout
     */
    async logout(redirect: boolean = true): Promise<void> {
      this.loading = true

      try {
        // Call logout endpoint if token exists
        if (this.token) {
          await api.post('/auth/logout')
        }
      } catch (error) {
        console.error('Logout error:', error)
        // Continue with local logout even if API call fails
      } finally {
        // Clear local state regardless of API response
        this.user = null
        this.isAuthenticated = false
        this.token = null
        this.permissions = []
        this.sessionExpiry = null
        this.error = null
        this.loading = false

        // Clear token from localStorage
        localStorage.removeItem('auth_token')

        if (redirect) {
          // Redirect handled by router guard
          window.location.href = '/login'
        }
      }
    },

    /**
     * Check authentication status and validate token
     * @returns Promise that resolves to authentication status
     */
    async checkAuth(): Promise<boolean> {
      if (!this.token) {
        this.isAuthenticated = false
        return false
      }

      this.loading = true

      try {
        const response = await api.get<{ user: User; permissions: Permission[] }>('/auth/me')
        
        this.user = response.data.user
        this.permissions = response.data.permissions || []
        this.isAuthenticated = true

        return true
      } catch (error) {
        console.error('Auth check failed:', error)
        // Clear invalid token
        await this.logout(false)
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * Register new user
     * @param userData - Registration data
     * @returns Promise that resolves with user data
     */
    async register(userData: RegistrationData): Promise<AuthResponse> {
      this.loading = true
      this.error = null

      try {
        const response = await api.post<AuthResponse>('/auth/register', userData)

        // Auto-login after successful registration
        if (response.data.token) {
          this.token = response.data.token
          this.user = response.data.user
          this.isAuthenticated = true
          this.permissions = response.data.permissions || []
          this.sessionExpiry = response.data.expiresAt || null
          localStorage.setItem('auth_token', response.data.token)
        }

        return response.data
      } catch (error: any) {
        this.error = error.message || 'Registration failed'
        console.error('Registration error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Change user password
     * @param currentPassword - Current password
     * @param newPassword - New password
     * @returns Promise that resolves when password is changed
     */
    async changePassword(currentPassword: string, newPassword: string): Promise<void> {
      this.loading = true
      this.error = null

      try {
        await api.post('/auth/change-password', {
          currentPassword,
          newPassword
        })
      } catch (error: any) {
        this.error = error.message || 'Password change failed'
        console.error('Password change error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update user profile
     * @param profileData - Updated profile data
     * @returns Promise that resolves when profile is updated
     */
    async updateProfile(profileData: ProfileUpdateData): Promise<User> {
      this.loading = true
      this.error = null

      try {
        const response = await api.put<{ user: User }>('/auth/profile', profileData)
        
        this.user = { ...this.user!, ...response.data.user }

        return response.data.user
      } catch (error: any) {
        this.error = error.message || 'Profile update failed'
        console.error('Profile update error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear auth error
     */
    clearError(): void {
      this.error = null
    },

    /**
     * Get authorization header for API requests
     * @returns Authorization header object
     */
    getAuthHeader(): Record<string, string> {
      if (!this.token) return {}
      return {
        'Authorization': `Bearer ${this.token}`
      }
    },

    /**
     * Check if user can perform action
     * @param action - Action to check
     * @returns True if user can perform action
     */
    canPerform(action: Permission): boolean {
      if (!this.isAuthenticated) return false
      if (this.isAdmin) return true
      return this.permissions.includes(action)
    },

    /**
     * Set user permissions
     * @param permissions - Array of permission strings
     */
    setPermissions(permissions: Permission[]): void {
      this.permissions = permissions
    },

    /**
     * Update user data
     * @param userData - Updated user data
     */
    updateUser(userData: Partial<User>): void {
      if (this.user) {
        this.user = { ...this.user, ...userData }
      }
    }
  }
})
