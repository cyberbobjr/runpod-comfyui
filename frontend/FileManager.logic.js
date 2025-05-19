import { ref } from 'vue'
import { apiFetch, handle401, token } from './App.logic.js'

const currentPath = ref('')
const dirs = ref([])
const files = ref([])
const selectedFile = ref(null)
const fileProps = ref(null)
const errorMsg = ref('')
const refreshKey = ref(0)

function joinPath(...parts) {
    return parts.filter(Boolean).join('/').replace(/\/+/g, '/')
}

async function fetchDirs() {
    errorMsg.value = ''
    const res = await apiFetch(`/file/list_dirs?path=${encodeURIComponent(currentPath.value)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to list directories'
        return
    }
    const data = await res.json()
    dirs.value = data.dirs
}

async function fetchFiles() {
    errorMsg.value = ''
    const res = await apiFetch(`/file/list_files?path=${encodeURIComponent(currentPath.value)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to list files'
        return
    }
    const data = await res.json()
    files.value = data.files
}

async function refresh() {
    await fetchDirs()
    await fetchFiles()
    fileProps.value = null
    selectedFile.value = null
    refreshKey.value++
}

async function goToDir(dir) {
    currentPath.value = joinPath(currentPath.value, dir)
    await refresh()
}

async function goUp() {
    if (!currentPath.value) return
    currentPath.value = currentPath.value.split('/').slice(0, -1).join('/')
    await refresh()
}

async function selectFile(file) {
    selectedFile.value = file
    await fetchFileProps(file)
}

async function fetchFileProps(file) {
    errorMsg.value = ''
    const path = joinPath(currentPath.value, file)
    const res = await apiFetch(`/file/properties?path=${encodeURIComponent(path)}`)
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to get file properties'
        fileProps.value = null
        return
    }
    fileProps.value = await res.json()
}

async function deleteFileOrDir(name) {
    errorMsg.value = ''
    const path = joinPath(currentPath.value, name)
    if (!window.confirm(`Delete "${name}"?`)) return
    const res = await apiFetch('/file/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
    })
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to delete'
        return
    }
    await refresh()
}

async function renameFileOrDir(oldName, newName) {
    errorMsg.value = ''
    const src = joinPath(currentPath.value, oldName)
    const dst = joinPath(currentPath.value, newName)
    const res = await apiFetch('/file/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ src, dst })
    })
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to rename'
        return
    }
    await refresh()
}

async function copyFile(srcName, dstName) {
    errorMsg.value = ''
    const src = joinPath(currentPath.value, srcName)
    const dst = joinPath(currentPath.value, dstName)
    const res = await apiFetch('/file/copy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ src, dst })
    })
    if (handle401(res)) return
    if (!res.ok) {
        errorMsg.value = 'Failed to copy'
        return
    }
    await refresh()
}

function formatDate(dateStr) {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleString()
}

function formatSize(size) {
    if (typeof size !== 'number') return size
    if (size >= 1e9) return (size / 1e9).toFixed(2) + ' GB'
    if (size >= 1e6) return (size / 1e6).toFixed(2) + ' MB'
    if (size >= 1e3) return (size / 1e3).toFixed(2) + ' KB'
    return size + ' B'
}

export {
    currentPath, dirs, files, selectedFile, fileProps, errorMsg, refreshKey,
    fetchDirs, fetchFiles, refresh, goToDir, goUp, selectFile,
    fetchFileProps, deleteFileOrDir, renameFileOrDir, copyFile,
    formatDate, formatSize
}
