<template>
  <div>
    <!-- API Tokens Card -->
    <div class="card shadow-sm mb-4">
      <div class="card-header">
        <h2 class="card-title h5 mb-0">API Tokens</h2>
      </div>
      <div class="card-body">
        <div class="row g-2 align-items-center">
          <div class="col-md-5">
            <label class="form-label">HuggingFace Token</label>
            <input
              v-model="hf_token"
              placeholder="Enter HuggingFace Token"
              class="form-control"
            />
          </div>
          <div class="col-md-5">
            <label class="form-label">CivitAI Token</label>
            <input
              v-model="civitai_token"
              placeholder="Enter CivitAI Token"
              class="form-control"
            />
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button @click="saveTokens" class="btn btn-success w-100">
              Save Tokens
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Account Card -->
    <div class="card shadow-sm mb-4">
      <div class="card-header">
        <h2 class="card-title h5 mb-0">Change Login Credentials</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="changeUser">
          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <h6 class="mb-3">Authentication</h6>
              <div class="mb-3">
                <label class="form-label">Current Username</label>
                <input
                  v-model="old_username"
                  class="form-control"
                  autocomplete="username"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Current Password</label>
                <input
                  v-model="old_password"
                  type="password"
                  class="form-control"
                  autocomplete="current-password"
                  required
                />
              </div>
            </div>
            <div class="col-md-6">
              <h6 class="mb-3">New Credentials</h6>
              <div class="mb-3">
                <label class="form-label">New Username</label>
                <input
                  v-model="new_username"
                  class="form-control"
                  autocomplete="username"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input
                  v-model="new_password"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  required
                />
              </div>
            </div>
          </div>
          <button class="btn btn-warning" type="submit">
            Update Credentials
          </button>
          <span
            v-if="change_user_msg"
            :class="{
              'text-success': change_user_ok,
              'text-danger': !change_user_ok,
            }"
            style="margin-left: 1em"
            >{{ change_user_msg }}</span
          >
        </form>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import {
  hf_token,
  civitai_token,
  saveTokens,
  old_username,
  old_password,
  new_username,
  new_password,
  change_user_msg,
  change_user_ok,
  changeUser,
} from "./App.logic.js";
</script>
