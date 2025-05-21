<template>
  <div class="container-fluid d-flex flex-column" style="height: 100vh;">
    <div v-if="!token" class="row justify-content-center flex-grow-1">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="card-title mb-4 text-center">Login</h2>
            <form @submit.prevent="doLogin">
              <div class="mb-3">
                <input
                  v-model="login_user"
                  placeholder="Username"
                  class="form-control"
                  autocomplete="username"
                />
              </div>
              <div class="mb-3">
                <input
                  v-model="login_pass"
                  placeholder="Password"
                  type="password"
                  class="form-control"
                  autocomplete="current-password"
                />
              </div>
              <button type="submit" class="btn btn-primary w-100 mb-2">
                Sign in
              </button>
            </form>
            <div v-if="login_error" class="alert alert-danger py-2 px-3 mt-2">
              {{ login_error }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="d-flex flex-column flex-grow-1">
      <div class="d-flex justify-content-between align-items-center mb-3 bg-primary p-3 rounded">
        <h1 class="mb-0">
          ComfyUI Model Manager
          <span
            v-if="totalSize !== null"
            class="fs-6 text-muted"
            style="margin-left:1em;"
          >
            (Total size: {{ formatSize(totalSize) }})
          </span>
        </h1>
        <button class="btn btn-outline-secondary" @click="logout">
          Logout
        </button>
      </div>
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <router-link
            to="/models"
            class="nav-link"
            :class="{ active: $route.path === '/models' }"
            ><i class="fas fa-download me-1"></i>Install Models</router-link
          >
        </li>
        <li class="nav-item">
          <router-link
            to="/install-bundles"
            class="nav-link"
            :class="{ active: $route.path === '/install-bundles' }"
            ><i class="fas fa-cubes me-1"></i>Install Bundles</router-link
          >
        </li>
        <li class="nav-item">
          <router-link
            to="/bundles"
            class="nav-link"
            :class="{ active: $route.path === '/bundles' }"
            >Bundle Management</router-link
          >
        </li>
        <li class="nav-item">
          <router-link
            to="/files"
            class="nav-link"
            :class="{ active: $route.path === '/files' }"
            >File explorer</router-link
          >
        </li>
        <li class="nav-item">
          <router-link
            to="/jsoneditor"
            class="nav-link"
            :class="{ active: $route.path === '/jsoneditor' }"
            >JSON Editor</router-link
          >
        </li>
        <li class="nav-item">
          <router-link
            to="/settings"
            class="nav-link"
            :class="{ active: $route.path === '/settings' }"
            >Settings</router-link
          >
        </li>
      </ul>
      <div class="flex-grow-1" style="overflow-y: auto;">
        <router-view />
      </div>
    </div>
  </div>
  <!-- Make sure this is at the end of your template -->
  <GlobalConfirmDialog />
</template>

<script setup>
import {
  token,
  login_user,
  login_pass,
  login_error,
  doLogin,
  logout,
  totalSize,
  formatSize,
} from "./App.logic.js";
</script>

<style>
/* Ajout d'un style pour le conteneur principal afin d'éviter le débordement */
.container-fluid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}
</style>
