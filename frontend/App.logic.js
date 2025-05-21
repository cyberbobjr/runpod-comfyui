import { ref, onMounted, computed, watch } from 'vue'
import { useConfirm } from './plugins/confirm-dialog'; // Import useConfirm

const models = ref([])
const hf_token = ref('')
const civitai_token = ref('')
const token = ref(localStorage.getItem('token') || '')
const login_user = ref('')
const login_pass = ref('')
const login_error = ref('')
const totalSize = ref(null)

// Initialize confirm and alert from useConfirm
const { confirm, alert } = useConfirm();

// Remplace la fonction apiUrl pour ne pas forcer le port 8081 et utiliser le même host/port que le frontend
function apiUrl(path) {
    const host = window.location.hostname
    const protocol = window.location.protocol
    const port = window.location.port
    let base = `${protocol}//${host}:${port}`
    if (path.startsWith('/')) {
        return `${base}/api${path}`
    }
    return `${base}/api/${path}`
}

function apiFetch(url, opts = {}) {
    opts.headers = opts.headers || {}
    if (token.value) opts.headers['Authorization'] = 'Bearer ' + token.value
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
    const res = await apiFetch('/models/') // <-- Ajoute le slash final
    if (handle401(res)) return
    models.value = await res.json()
}

async function fetchTokens() {
    if (!token.value) return
    const res = await apiFetch('/models/tokens')
    if (handle401(res)) return
    const data = await res.json()
    hf_token.value = data.hf_token || ''
    civitai_token.value = data.civitai_token || ''
}

async function fetchTotalSize() {
    if (!token.value) return
    const res = await apiFetch('/models/total_size')
    if (handle401(res)) return
    const data = await res.json()
    totalSize.value = data.total_size
}

async function saveTokens() {
    const res = await apiFetch('/models/tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hf_token: hf_token.value, civitai_token: civitai_token.value })
    })
    if (handle401(res)) return
    await alert({ title: 'Success', message: 'Tokens saved' }); // Replaced window.alert
}

async function download(model) {
    const res = await apiFetch('/models/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(model.entry)
    })
    if (handle401(res)) return
    pollProgress(model)
}

async function stopDownload(model) {
    const res = await apiFetch('/models/stop_download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(model.entry)
    })
    if (handle401(res)) return
    fetchModels()
}

async function del(model) {
    const res = await apiFetch('/models/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(model.entry)
    })
    if (handle401(res)) return
    fetchModels()
}

function pollProgress(model) {
    const interval = setInterval(async () => {
        const res = await apiFetch('/models/progress', {
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
    const res = await apiFetch('/auth/login', {
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
        fetchTotalSize()
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

async function confirmDownload(model) {
    const msg = missingTokenMsg(model)
    if (msg) {
        await alert({ title: 'Token Required', message: msg.trim() }); // Replaced window.alert
        return
    }
    const confirmed = await confirm({ // Replaced window.confirm
        title: 'Confirm Download',
        message: 'Do you really want to download this model?'
    });
    if (confirmed) {
        download(model)
    }
}

async function confirmDelete(model) {
    const confirmed = await confirm({ // Replaced window.confirm
        title: 'Confirm Delete',
        message: 'Do you really want to delete this model?'
    });
    if (confirmed) {
        del(model)
    }
}

const selected = ref({})

function modelKey(model) {
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

async function confirmDeleteSelected() {
    if (selectedToDelete.value.length === 0) return
    const confirmed = await confirm({ // Replaced window.confirm
        title: 'Confirm Delete Selected',
        message: `Do you really want to delete ${selectedToDelete.value.length} model(s)?`
    });
    if (confirmed) {
        for (const m of selectedToDelete.value) {
            del(m)
            selected.value[modelKey(m)] = false
        }
    }
}

async function confirmDownloadSelected() {
    if (selectedToDownload.value.length === 0) return
    let missing = []
    for (const m of selectedToDownload.value) {
        const msg = missingTokenMsg(m)
        if (msg) missing.push(`- ${m.entry.dest ? m.entry.dest.split('/').pop() : m.entry.git} :\n${msg.trim()}`)
    }
    if (missing.length) {
        await alert({ // Replaced window.alert
            title: 'Download Warning',
            message: 'Some models cannot be downloaded:\n\n' + missing.join('\n\n')
        });
        return
    }
    const confirmed = await confirm({ // Replaced window.confirm
        title: 'Confirm Download Selected',
        message: `Do you really want to download ${selectedToDownload.value.length} model(s)?`
    });
    if (confirmed) {
        for (const m of selectedToDownload.value) {
            download(m)
            selected.value[modelKey(m)] = false
        }
    }
}

const groupedModels = computed(() => {
    const groups = {}
    for (const model of models.value) {
        const group = model.group || 'Other'
        if (!groups[group]) groups[group] = []
        groups[group].push(model)
    }
    return groups
})

function formatSize(size) {
    if (typeof size !== 'number') return size
    if (size >= 1e9) return (size / 1e9).toFixed(2) + ' GB'
    if (size >= 1e6) return (size / 1e6).toFixed(2) + ' MB'
    if (size >= 1e3) return (size / 1e3).toFixed(2) + ' KB'
    return size + ' B'
}

function isNSFW(model) {
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
    const res = await apiFetch('/models/change_user', {
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

const activeDownloads = computed(() =>
    models.value.filter(m => m.status === 'downloading')
)

let downloadsInterval = null

function startDownloadsPolling() {
    if (downloadsInterval) return
    downloadsInterval = setInterval(async () => {
        if (activeDownloads.value.length === 0) {
            stopDownloadsPolling()
            return
        }
        await fetchModels()
    }, 5000)
}

function stopDownloadsPolling() {
    if (downloadsInterval) {
        clearInterval(downloadsInterval)
        downloadsInterval = null
    }
}

function useDownloadsPolling() {
    watch(
        activeDownloads,
        (newVal) => {
            if (newVal.length > 0) {
                startDownloadsPolling()
            } else {
                stopDownloadsPolling()
            }
        },
        { immediate: true }
    )
}

function useAppLogic() {
    onMounted(() => {
        console.log('App.logic.js onMounted called') // Debug: vérifier si onMounted est appelé
        fetchModels()
        fetchTokens()
        fetchTotalSize()
    })
}

// Met à jour la taille totale à chaque changement de modèles (ex: après download/delete)
watch(models, () => {
    fetchTotalSize()
})

export {
    models, hf_token, civitai_token, token,
    login_user, login_pass, login_error,
    apiUrl, apiFetch, handle401, fetchModels, fetchTokens, saveTokens,
    download, stopDownload, del, pollProgress, doLogin, logout,
    missingTokenMsg, confirmDownload, confirmDelete,
    selected, modelKey, allChecked, toggleAll,
    selectedToDelete, selectedToDownload,
    confirmDeleteSelected, confirmDownloadSelected,
    groupedModels, formatSize, isNSFW,
    old_username, old_password, new_username, new_password,
    change_user_msg, change_user_ok, changeUser,
    activeDownloads, useDownloadsPolling,
    useAppLogic,
    totalSize, // <-- Ajout export
}
