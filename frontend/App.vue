<template>
  <div class="container py-4">
    <div v-if="!token" class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="card-title mb-4 text-center">Login</h2>
            <form @submit.prevent="doLogin">
              <div class="mb-3">
                <input v-model="login_user" placeholder="Username" class="form-control" autocomplete="username" />
              </div>
              <div class="mb-3">
                <input v-model="login_pass" placeholder="Password" type="password" class="form-control" autocomplete="current-password" />
              </div>
              <button type="submit" class="btn btn-primary w-100 mb-2">Sign in</button>
            </form>
            <div v-if="login_error" class="alert alert-danger py-2 px-3 mt-2">{{ login_error }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1 class="mb-0">ComfyUI Model Manager</h1>
        <button class="btn btn-outline-secondary" @click="logout">Logout</button>
      </div>
      <div class="accordion mb-4" id="settingsAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-tokens">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-tokens" aria-expanded="true" aria-controls="collapse-tokens">
              Configure tokens
            </button>
          </h2>
          <div id="collapse-tokens" class="accordion-collapse collapse show" aria-labelledby="heading-tokens" data-bs-parent="#settingsAccordion">
            <div class="accordion-body">
              <div class="row g-2 align-items-center">
                <div class="col-md-5">
                  <input v-model="hf_token" placeholder="HuggingFace Token" class="form-control" />
                </div>
                <div class="col-md-5">
                  <input v-model="civitai_token" placeholder="CivitAI Token" class="form-control" />
                </div>
                <div class="col-md-2">
                  <button @click="saveTokens" class="btn btn-success w-100">Save</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading-user">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-user" aria-expanded="false" aria-controls="collapse-user">
              Change username/password
            </button>
          </h2>
          <div id="collapse-user" class="accordion-collapse collapse" aria-labelledby="heading-user" data-bs-parent="#settingsAccordion">
            <div class="accordion-body">
              <form @submit.prevent="changeUser">
                <div class="row g-2 align-items-center mb-2">
                  <div class="col-md-3">
                    <input v-model="old_username" placeholder="Current username" class="form-control" autocomplete="username" />
                  </div>
                  <div class="col-md-3">
                    <input v-model="old_password" placeholder="Current password" type="password" class="form-control" autocomplete="current-password" />
                  </div>
                  <div class="col-md-3">
                    <input v-model="new_username" placeholder="New username" class="form-control" autocomplete="username" />
                  </div>
                  <div class="col-md-3">
                    <input v-model="new_password" placeholder="New password" type="password" class="form-control" autocomplete="new-password" />
                  </div>
                </div>
                <button class="btn btn-warning" type="submit">Change credentials</button>
                <span v-if="change_user_msg" :class="{'text-success': change_user_ok, 'text-danger': !change_user_ok}" style="margin-left:1em">{{ change_user_msg }}</span>
              </form>
            </div>
          </div>
        </div>
      </div>
      <div class="card shadow-sm">
        <div class="card-body">
          <h2 class="card-title h5 mb-3">Available models</h2>
          <div class="mb-3 d-flex gap-2">
            <button class="btn btn-danger btn-sm" :disabled="selectedToDelete.length === 0" @click="confirmDeleteSelected">
              Delete selected
            </button>
            <button class="btn btn-primary btn-sm" :disabled="selectedToDownload.length === 0" @click="confirmDownloadSelected">
              Download selected
            </button>
          </div>
          <div class="accordion" id="modelsAccordion">
            <div v-for="(groupModels, groupName, idx) in groupedModels" :key="groupName" class="accordion-item">
              <h2 class="accordion-header" :id="`heading-${idx}`">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                  :data-bs-target="`#collapse-${idx}`" aria-expanded="false" :aria-controls="`collapse-${idx}`">
                  {{ groupName }}
                </button>
              </h2>
              <div :id="`collapse-${idx}`" class="accordion-collapse collapse" :aria-labelledby="`heading-${idx}`"
                data-bs-parent="#modelsAccordion">
                <div class="accordion-body p-0">
                  <div class="table-responsive">
                    <table class="table table-bordered align-middle mb-0">
                      <thead class="table-light">
                        <tr>
                          <th style="width:32px">
                            <input type="checkbox"
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
                            <input type="checkbox"
                              v-model="selected[modelKey(model)]"
                              :disabled="model.status==='downloading'"
                            />
                          </td>
                          <td>
                            <span
                              v-if="isNSFW(model)"
                              class="badge bg-danger text-white"
                            >
                              {{ model.entry.dest ? model.entry.dest.split('/').pop() : model.entry.git }}
                            </span>
                            <span v-else>
                              {{ model.entry.dest ? model.entry.dest.split('/').pop() : model.entry.git }}
                            </span>
                          </td>
                          <td>{{ model.entry.type || groupName }}</td>
                          <td>
                            <span v-if="model.entry.size">{{ formatSize(model.entry.size) }}</span>
                            <span v-else class="text-muted">-</span>
                          </td>
                          <td>
                            <a
                              v-if="model.entry.src"
                              :href="model.entry.src"
                              target="_blank"
                              rel="noopener"
                              class="btn btn-link btn-sm p-0"
                            >Link</a>
                            <span v-else class="text-muted">-</span>
                          </td>
                          <td>
                            <span v-if="model.exists" class="badge bg-success">Yes</span>
                            <span v-else class="badge bg-danger">No</span>
                          </td>
                          <td style="min-width:120px">
                            <div v-if="model.status==='downloading'">
                              <span>{{ model.progress }}%</span>
                              <div class="progress" style="height: 8px;">
                                <div class="progress-bar" :style="{width: model.progress + '%'}"></div>
                              </div>
                            </div>
                            <span v-else>{{ model.status }}</span>
                          </td>
                          <td>
                            <button
                              v-if="!model.exists && model.status!=='downloading'"
                              @click="confirmDownload(model)"
                              class="btn btn-primary btn-sm"
                            >Download</button>
                            <button
                              v-if="model.exists"
                              @click="confirmDelete(model)"
                              class="btn btn-danger btn-sm ms-2"
                            >Delete</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="Object.keys(groupedModels).length === 0" class="text-center text-muted py-4">
              No models found.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const models = ref([])
const hf_token = ref('')
const civitai_token = ref('')
const token = ref(localStorage.getItem('token') || '')
const login_user = ref('')
const login_pass = ref('')
const login_error = ref('')

function apiUrl(path) {
  // Prefix all API routes with /api
  const { protocol, hostname } = window.location
  return `${protocol}//${hostname}:8000/api${path}`
}

function apiFetch(url, opts={}) {
  opts.headers = opts.headers || {}
  if (token.value) opts.headers['Authorization'] = 'Bearer ' + token.value
  // If url does not start with http, prefix it
  if (!/^https?:\/\//.test(url)) url = apiUrl(url)
  return fetch(url, opts)
}

function handle401(res) {
  if (res.status === 401) {
    logout()
    login_error.value = "Session expired. Please log in again."
    return true
  }
  return false
}

async function fetchModels() {
  if (!token.value) return
  const res = await apiFetch('/models')
  if (handle401(res)) return
  models.value = await res.json()
}

async function fetchTokens() {
  if (!token.value) return
  const res = await apiFetch('/tokens')
  if (handle401(res)) return
  const data = await res.json()
  hf_token.value = data.hf_token || ''
  civitai_token.value = data.civitai_token || ''
}

async function saveTokens() {
  const res = await apiFetch('/tokens', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hf_token: hf_token.value, civitai_token: civitai_token.value })
  })
  if (handle401(res)) return
  alert('Tokens saved')
}

async function download(model) {
  const res = await apiFetch('/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model.entry)
  })
  if (handle401(res)) return
  pollProgress(model)
}

async function del(model) {
  const res = await apiFetch('/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model.entry)
  })
  if (handle401(res)) return
  fetchModels()
}

function pollProgress(model) {
  const interval = setInterval(async () => {
    const res = await apiFetch('/progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(model.entry)
    })
    if (handle401(res)) {
      clearInterval(interval)
      return
    }
    const data = await res.json()
    model.progress = data.progress
    model.status = data.status
    if (data.status === 'done' || data.status === 'error') {
      clearInterval(interval)
      fetchModels()
    }
  }, 1000)
}

async function doLogin() {
  login_error.value = ''
  const res = await apiFetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: login_user.value, password: login_pass.value })
  })
  if (res.ok) {
    const data = await res.json()
    token.value = data.token
    localStorage.setItem('token', data.token)
    fetchModels()
    fetchTokens()
  } else {
    login_error.value = "Invalid credentials"
  }
}

function logout() {
  token.value = ''
  localStorage.removeItem('token')
  models.value = []
}

function missingTokenMsg(model) {
  const url = model.entry.url || ''
  let msg = ''
  if (url.includes('huggingface.co') && !hf_token.value) {
    msg += 'HuggingFace token is required for this download.\n'
  }
  if (url.includes('civitai.com') && !civitai_token.value) {
    msg += 'CivitAI token is required for this download.\n'
  }
  return msg
}

function confirmDownload(model) {
  const msg = missingTokenMsg(model)
  if (msg) {
    window.alert(msg.trim())
    return
  }
  if (window.confirm(`Do you really want to download this model?`)) {
    download(model)
  }
}

function confirmDelete(model) {
  if (window.confirm(`Do you really want to delete this model?`)) {
    del(model)
  }
}

const selected = ref({})

function modelKey(model) {
  // Use a unique key for each model
  return model.entry.dest || model.entry.git
}

function allChecked(groupModels) {
  return groupModels.length > 0 && groupModels.every(m => selected.value[modelKey(m)])
}

function toggleAll(groupModels, event) {
  const checked = event.target.checked
  for (const m of groupModels) {
    if (m.status !== 'downloading') {
      selected.value[modelKey(m)] = checked
    }
  }
}

const selectedToDelete = computed(() =>
  models.value.filter(m => selected.value[modelKey(m)] && m.exists)
)
const selectedToDownload = computed(() =>
  models.value.filter(m => selected.value[modelKey(m)] && !m.exists && m.status !== 'downloading')
)

function confirmDeleteSelected() {
  if (selectedToDelete.value.length === 0) return
  if (window.confirm(`Do you really want to delete ${selectedToDelete.value.length} model(s)?`)) {
    for (const m of selectedToDelete.value) {
      del(m)
      selected.value[modelKey(m)] = false
    }
  }
}

function confirmDownloadSelected() {
  if (selectedToDownload.value.length === 0) return
  // Check for each selected model
  let missing = []
  for (const m of selectedToDownload.value) {
    const msg = missingTokenMsg(m)
    if (msg) missing.push(`- ${m.entry.dest ? m.entry.dest.split('/').pop() : m.entry.git} :\n${msg.trim()}`)
  }
  if (missing.length) {
    window.alert('Some models cannot be downloaded:\n\n' + missing.join('\n\n'))
    return
  }
  if (window.confirm(`Do you really want to download ${selectedToDownload.value.length} model(s)?`)) {
    for (const m of selectedToDownload.value) {
      download(m)
      selected.value[modelKey(m)] = false
    }
  }
}

const groupedModels = computed(() => {
  // Group models by group/type
  const groups = {}
  for (const model of models.value) {
    const group = model.group || 'Other'
    if (!groups[group]) groups[group] = []
    groups[group].push(model)
  }
  return groups
})

function formatSize(size) {
  // size in bytes, returns a readable string
  if (typeof size !== 'number') return size
  if (size >= 1e9) return (size / 1e9).toFixed(2) + ' GB'
  if (size >= 1e6) return (size / 1e6).toFixed(2) + ' MB'
  if (size >= 1e3) return (size / 1e3).toFixed(2) + ' KB'
  return size + ' B'
}

function isNSFW(model) {
  // Check if the model has a 'nsfw' tag in entry.tags (array or string)
  const tags = model.entry.tags
  if (!tags) return false
  if (Array.isArray(tags)) return tags.map(t => t.toLowerCase()).includes('nsfw')
  if (typeof tags === 'string') return tags.toLowerCase().includes('nsfw')
  return false
}

const old_username = ref('')
const old_password = ref('')
const new_username = ref('')
const new_password = ref('')
const change_user_msg = ref('')
const change_user_ok = ref(false)

async function changeUser() {
  change_user_msg.value = ''
  change_user_ok.value = false
  const res = await apiFetch('/change_user', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      old_username: old_username.value,
      old_password: old_password.value,
      new_username: new_username.value,
      new_password: new_password.value
    })
  })
  if (handle401(res)) return
  if (res.ok) {
    change_user_msg.value = 'Credentials changed. Please log in again.'
    change_user_ok.value = true
    // Déconnecte l'utilisateur après changement
    setTimeout(() => {
      logout()
      old_username.value = ''
      old_password.value = ''
      new_username.value = ''
      new_password.value = ''
      change_user_msg.value = ''
    }, 1500)
  } else {
    const data = await res.json().catch(() => ({}))
    change_user_msg.value = data.detail || 'Error'
    change_user_ok.value = false
  }
}

onMounted(() => {
  fetchModels()
  fetchTokens()
})
</script>