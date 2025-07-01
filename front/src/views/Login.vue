<template>
  <div class="min-h-screen flex justify-center items-center bg-background px-4">
    <div class="card w-full max-w-md">
      <h2 class="text-2xl font-bold text-primary mb-6">Login</h2>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="formValue.username"
            type="text"
            class="form-input"
            placeholder="Enter your username"
            :class="{ 'border-red-500': errors.username }"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-500">
            {{ errors.username }}
          </p>
        </div>

        <div>
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="formValue.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            placeholder="Enter your password"
            :class="{ 'border-red-500': errors.password }"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-500">
            {{ errors.password }}
          </p>
        </div>

        <div class="flex items-center space-x-4">
          <button
            type="submit"
            class="btn btn-primary flex-1"
            :disabled="loading"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Loading...
            </span>
            <span v-else>Login</span>
          </button>
          <button type="button" class="btn btn-default" @click="resetForm">
            Reset
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useNotifications } from "../composables/useNotifications";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const loading = ref(false);
const showPassword = ref(false);
const { success, error } = useNotifications();
const authStore = useAuthStore();
const formValue = reactive({
  username: "",
  password: "",
});

const errors = reactive({
  username: "",
  password: "",
});

const validateForm = () => {
  let isValid = true;

  // Reset errors
  errors.username = "";
  errors.password = "";

  // Validate username
  if (!formValue.username.trim()) {
    errors.username = "Please enter your username";
    isValid = false;
  }

  // Validate password
  if (!formValue.password) {
    errors.password = "Please enter your password";
    isValid = false;
  }

  return isValid;
};

const handleLogin = async () => {
  if (!validateForm()) return;

  loading.value = true;

  try {
    await authStore.login(formValue.username, formValue.password);
    // Show success message with elegant notification
    success("Login successful!");

    router.push(route.query.redirect || "/");
  } catch (err) {
    if (err.response) {
      error(err.response.data.message || "Authentication failed");
    } else {
      error("Network error. Please try again later.");
    }
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  formValue.username = "";
  formValue.password = "";
  errors.username = "";
  errors.password = "";
};
</script>
