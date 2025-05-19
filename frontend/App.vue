<template>
  <div class="container py-4">
    <div v-if="!token" class="row justify-content-center">
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
    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-3">
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
      <div class="accordion mb-4" id="settingsAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-tokens">
            <button
              class="accordion-button"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#collapse-tokens"
              aria-expanded="true"
              aria-controls="collapse-tokens"
            >
              Configure tokens
            </button>
          </h2>
          <div
            id="collapse-tokens"
            class="accordion-collapse collapse show"
            aria-labelledby="heading-tokens"
            data-bs-parent="#settingsAccordion"
          >
            <div class="accordion-body">
              <div class="row g-2 align-items-center">
                <div class="col-md-5">
                  <input
                    v-model="hf_token"
                    placeholder="HuggingFace Token"
                    class="form-control"
                  />
                </div>
                <div class="col-md-5">
                  <input
                    v-model="civitai_token"
                    placeholder="CivitAI Token"
                    class="form-control"
                  />
                </div>
                <div class="col-md-2">
                  <button @click="saveTokens" class="btn btn-success w-100">
                    Save
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-user">
            <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#collapse-user"
              aria-expanded="false"
              aria-controls="collapse-user"
            >
              Change username/password
            </button>
          </h2>
          <div
            id="collapse-user"
            class="accordion-collapse collapse"
            aria-labelledby="heading-user"
            data-bs-parent="#settingsAccordion"
          >
            <div class="accordion-body">
              <form @submit.prevent="changeUser">
                <div class="row g-2 align-items-center mb-2">
                  <div class="col-md-3">
                    <input
                      v-model="old_username"
                      placeholder="Current username"
                      class="form-control"
                      autocomplete="username"
                    />
                  </div>
                  <div class="col-md-3">
                    <input
                      v-model="old_password"
                      placeholder="Current password"
                      type="password"
                      class="form-control"
                      autocomplete="current-password"
                    />
                  </div>
                  <div class="col-md-3">
                    <input
                      v-model="new_username"
                      placeholder="New username"
                      class="form-control"
                      autocomplete="username"
                    />
                  </div>
                  <div class="col-md-3">
                    <input
                      v-model="new_password"
                      placeholder="New password"
                      type="password"
                      class="form-control"
                      autocomplete="new-password"
                    />
                  </div>
                </div>
                <button class="btn btn-warning" type="submit">
                  Change credentials
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
        <!-- Nouvel accordéon pour les téléchargements en cours -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-downloads">
            <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#collapse-downloads"
              aria-expanded="false"
              aria-controls="collapse-downloads"
            >
              Active downloads
            </button>
          </h2>
          <div
            id="collapse-downloads"
            class="accordion-collapse collapse"
            aria-labelledby="heading-downloads"
            data-bs-parent="#settingsAccordion"
          >
            <div class="accordion-body">
              <div v-if="activeDownloads.length === 0" class="text-muted">
                No active downloads.
              </div>
              <div v-else>
                <ul class="list-group">
                  <li
                    v-for="model in activeDownloads"
                    :key="modelKey(model)"
                    class="list-group-item d-flex align-items-center justify-content-between"
                  >
                    <div>
                      <strong>{{
                        model.entry.dest
                          ? model.entry.dest.split("/").pop()
                          : model.entry.git
                      }}</strong>
                      <span
                        v-if="model.entry.tags && model.entry.tags.length"
                        class="ms-2"
                      >
                        <span
                          v-for="tag in Array.isArray(model.entry.tags)
                            ? model.entry.tags
                            : [model.entry.tags]"
                          :key="tag"
                          class="badge bg-secondary me-1"
                          style="font-size: 0.8em"
                          >{{ tag }}</span
                        >
                      </span>
                    </div>
                    <div style="min-width: 180px">
                      <span>{{ model.progress }}%</span>
                      <div class="progress" style="height: 8px">
                        <div
                          class="progress-bar"
                          :style="{ width: model.progress + '%' }"
                        ></div>
                      </div>
                    </div>
                    <button
                      class="btn btn-outline-danger btn-sm ms-3"
                      @click="stopDownload(model)"
                    >
                      Stop
                    </button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card shadow-sm">
        <div class="card-body">
          <h2 class="card-title h5 mb-3">Available models</h2>
          <div class="mb-3 d-flex gap-2">
            <button
              class="btn btn-danger btn-sm"
              :disabled="selectedToDelete.length === 0"
              @click="confirmDeleteSelected"
            >
              Delete selected
            </button>
            <button
              class="btn btn-primary btn-sm"
              :disabled="selectedToDownload.length === 0"
              @click="confirmDownloadSelected"
            >
              Download selected
            </button>
          </div>
          <div class="accordion" id="modelsAccordion">
            <div
              v-for="(groupModels, groupName, idx) in groupedModels"
              :key="groupName"
              class="accordion-item"
            >
              <h2 class="accordion-header" :id="`heading-${idx}`">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  :data-bs-target="`#collapse-${idx}`"
                  aria-expanded="false"
                  :aria-controls="`collapse-${idx}`"
                >
                  {{ groupName }}
                </button>
              </h2>
              <div
                :id="`collapse-${idx}`"
                class="accordion-collapse collapse"
                :aria-labelledby="`heading-${idx}`"
                data-bs-parent="#modelsAccordion"
              >
                <div class="accordion-body p-0">
                  <div class="table-responsive">
                    <table class="table table-bordered align-middle mb-0">
                      <thead class="table-light">
                        <tr>
                          <th style="width: 32px">
                            <input
                              type="checkbox"
                              :checked="allChecked(groupModels)"
                              @change="toggleAll(groupModels, $event)"
                            />
                          </th>
                          <th>Name</th>
                          <th>Type</th>
                          <th>Size</th>
                          <th>Source</th>
                          <th>Present</th>
                          <th>Progress</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="model in groupModels"
                          :key="model.entry.dest || model.entry.git"
                        >
                          <td>
                            <input
                              type="checkbox"
                              v-model="selected[modelKey(model)]"
                              :disabled="model.status === 'downloading'"
                            />
                          </td>
                          <td>
                            <span
                              v-if="isNSFW(model)"
                              class="badge bg-danger text-white"
                            >
                              {{
                                model.entry.dest
                                  ? model.entry.dest.split("/").pop()
                                  : model.entry.git
                              }}
                            </span>
                            <span v-else>
                              {{
                                model.entry.dest
                                  ? model.entry.dest.split("/").pop()
                                  : model.entry.git
                              }}
                            </span>
                            <!-- Affichage des tags sous forme de badges -->
                            <span
                              v-if="model.entry.tags && model.entry.tags.length"
                              class="ms-2"
                            >
                              <span
                                v-for="tag in Array.isArray(model.entry.tags)
                                  ? model.entry.tags
                                  : [model.entry.tags]"
                                :key="tag"
                                class="badge bg-secondary me-1"
                                style="font-size: 0.8em"
                                >{{ tag }}</span
                              >
                            </span>
                          </td>
                          <td>{{ model.entry.type || groupName }}</td>
                          <td>
                            <span v-if="model.entry.size">{{
                              formatSize(model.entry.size)
                            }}</span>
                            <span v-else class="text-muted">-</span>
                          </td>
                          <td>
                            <a
                              v-if="model.entry.src"
                              :href="model.entry.src"
                              target="_blank"
                              rel="noopener"
                              class="btn btn-link btn-sm p-0"
                              >Link</a
                            >
                            <span v-else class="text-muted">-</span>
                          </td>
                          <td>
                            <span v-if="model.exists" class="badge bg-success"
                              >Yes</span
                            >
                            <span v-else class="badge bg-danger">No</span>
                          </td>
                          <td style="min-width: 120px">
                            <div v-if="model.status === 'downloading'">
                              <span>{{ model.progress }}%</span>
                              <div class="progress" style="height: 8px">
                                <div
                                  class="progress-bar"
                                  :style="{ width: model.progress + '%' }"
                                ></div>
                              </div>
                            </div>
                            <span v-else>{{ model.status }}</span>
                          </td>
                          <td>
                            <button
                              v-if="
                                !model.exists && model.status !== 'downloading'
                              "
                              @click="confirmDownload(model)"
                              class="btn btn-primary btn-sm"
                            >
                              Download
                            </button>
                            <button
                              v-if="model.exists"
                              @click="confirmDelete(model)"
                              class="btn btn-danger btn-sm ms-2"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div
              v-if="Object.keys(groupedModels).length === 0"
              class="text-center text-muted py-4"
            >
              No models found.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  hf_token,
  civitai_token,
  token,
  login_user,
  login_pass,
  login_error,
  saveTokens,
  doLogin,
  logout,
  confirmDownload,
  confirmDelete,
  selected,
  modelKey,
  allChecked,
  toggleAll,
  selectedToDelete,
  selectedToDownload,
  confirmDeleteSelected,
  confirmDownloadSelected,
  groupedModels,
  formatSize,
  isNSFW,
  old_username,
  old_password,
  new_username,
  new_password,
  change_user_msg,
  change_user_ok,
  changeUser,
  activeDownloads,
  stopDownload,
  useDownloadsPolling,
  useAppLogic, // <-- Ajout import
  totalSize,
} from "./App.logic.js";

useAppLogic(); // <-- Ajouté ici
useDownloadsPolling();
</script>
