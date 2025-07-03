/**
 * FileManager Component Tests
 * 
 * Test suite for the FileManager component, covering file management functionality,
 * TypeScript integration, upload/download operations, and user interactions.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FileManager from '../FileManager.vue'
import { useNotifications } from '../../composables/useNotifications'
import type { 
  FileItem, 
  DirectoryItem, 
  FileProperties, 
  UploadProgress 
} from '../types/views.types'

// Mock notifications
vi.mock('../../composables/useNotifications', () => ({
  useNotifications: vi.fn(() => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    confirm: vi.fn(),
    prompt: vi.fn()
  }))
}))

// Mock API
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    downloadFile: vi.fn()
  }
}))

// Mock components
vi.mock('../file-manager/FolderTreeComponent.vue', () => ({
  default: {
    name: 'FolderTreeComponent',
    template: '<div class="folder-tree">Folder Tree</div>',
    emits: ['select-folder']
  }
}))

vi.mock('../file-manager/DirectoryDetailsComponent.vue', () => ({
  default: {
    name: 'DirectoryDetailsComponent',
    template: '<div class="directory-details">Directory Details</div>',
    emits: [
      'go-up', 'refresh', 'file-upload', 'create-directory',
      'navigate-to-folder', 'select-file', 'rename', 'delete',
      'download', 'copy'
    ]
  }
}))

describe('FileManager', () => {
  let wrapper: VueWrapper<any>
  let notifications: ReturnType<typeof useNotifications>
  let mockApi: any

  const mockFiles: FileItem[] = [
    {
      name: 'test.txt',
      type: 'file',
      size: 1024,
      modified: '2023-01-01T10:00:00Z',
      extension: 'txt'
    },
    {
      name: 'image.jpg',
      type: 'file',
      size: 2048,
      modified: '2023-01-02T10:00:00Z',
      extension: 'jpg'
    }
  ]

  const mockDirectories: DirectoryItem[] = [
    {
      name: 'folder1',
      path: '/folder1',
      children: []
    },
    {
      name: 'folder2',
      path: '/folder2',
      children: [
        {
          name: 'subfolder1',
          path: '/folder2/subfolder1',
          children: []
        }
      ]
    }
  ]

  const mockFileProperties: FileProperties = {
    name: 'test.txt',
    path: '/test.txt',
    size: 1024,
    type: 'text/plain',
    modified: '2023-01-01T10:00:00Z',
    extension: 'txt',
    isRegistered: false
  }

  beforeEach(async () => {
    setActivePinia(createPinia())
    notifications = useNotifications()
    
    // Mock API responses
    mockApi = await import('../../services/api')
    vi.mocked(mockApi.default.get).mockImplementation((url: string) => {
      if (url.includes('/file/list_files')) {
        return Promise.resolve({ data: { files: mockFiles } })
      }
      if (url.includes('/file/list_dirs')) {
        return Promise.resolve({ data: mockDirectories })
      }
      if (url.includes('/file/list_all_dirs')) {
        return Promise.resolve({ data: mockDirectories })
      }
      if (url.includes('/file/properties')) {
        return Promise.resolve({ data: mockFileProperties })
      }
      return Promise.resolve({ data: [] })
    })

    vi.mocked(mockApi.default.post).mockResolvedValue({ data: { success: true } })
    vi.mocked(mockApi.default.downloadFile).mockResolvedValue(undefined)

    wrapper = mount(FileManager, {
      global: {
        stubs: {
          FolderTreeComponent: true,
          DirectoryDetailsComponent: true
        }
      }
    })

    // Wait for component initialization
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
  })

  describe('Component Initialization', () => {
    it('should render without errors', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should display file manager title', () => {
      expect(wrapper.text()).toContain('File Manager')
    })

    it('should initialize folder structure on mount', () => {
      expect(mockApi.default.get).toHaveBeenCalledWith('/file/list_all_dirs')
    })

    it('should fetch files and directories on mount', () => {
      expect(mockApi.default.get).toHaveBeenCalledWith(
        expect.stringContaining('/file/list_files')
      )
      expect(mockApi.default.get).toHaveBeenCalledWith(
        expect.stringContaining('/file/list_dirs')
      )
    })
  })

  describe('TypeScript Integration', () => {
    it('should have properly typed reactive state', () => {
      expect(typeof wrapper.vm.currentPath).toBe('string')
      expect(Array.isArray(wrapper.vm.dirs)).toBe(true)
      expect(Array.isArray(wrapper.vm.files)).toBe(true)
      expect(typeof wrapper.vm.treeReady).toBe('boolean')
      expect(typeof wrapper.vm.uploadProgress.isUploading).toBe('boolean')
    })

    it('should handle typed method parameters correctly', async () => {
      const testFile: FileItem = {
        name: 'test.txt',
        type: 'file',
        size: 1024
      }

      await wrapper.vm.selectFile(testFile)
      await wrapper.vm.navigateToFolder('/test/path')
      
      // No TypeScript errors should occur
      expect(true).toBe(true)
    })

    it('should properly type upload progress', () => {
      const progress = wrapper.vm.uploadProgress
      expect(typeof progress.isUploading).toBe('boolean')
      expect(typeof progress.percentage).toBe('number')
      expect(typeof progress.loaded).toBe('number')
      expect(typeof progress.total).toBe('number')
      expect(typeof progress.fileName).toBe('string')
    })
  })

  describe('Helper Functions', () => {
    it('should join paths correctly', () => {
      const result = wrapper.vm.joinPath('folder1', 'folder2', 'file.txt')
      expect(result).toBe('folder1/folder2/file.txt')
    })

    it('should handle empty path parts', () => {
      const result = wrapper.vm.joinPath('', 'folder1', '', 'file.txt')
      expect(result).toBe('folder1/file.txt')
    })

    it('should format bytes correctly', () => {
      expect(wrapper.vm.formatBytes(0)).toBe('0 Bytes')
      expect(wrapper.vm.formatBytes(1024)).toBe('1 KB')
      expect(wrapper.vm.formatBytes(1048576)).toBe('1 MB')
    })
  })

  describe('Navigation', () => {
    it('should navigate to folder', async () => {
      await wrapper.vm.navigateToFolder('/test/path')
      
      expect(wrapper.vm.currentPath).toBe('/test/path')
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.fileProps).toBe(null)
    })

    it('should handle go up navigation', async () => {
      wrapper.vm.currentPath = '/folder1/subfolder1'
      
      await wrapper.vm.handleGoUp()
      
      expect(wrapper.vm.currentPath).toBe('/folder1')
    })

    it('should handle go up from root', async () => {
      wrapper.vm.currentPath = ''
      
      await wrapper.vm.handleGoUp()
      
      expect(wrapper.vm.currentPath).toBe('')
    })
  })

  describe('File Operations', () => {
    it('should select file and fetch properties', async () => {
      const testFile: FileItem = {
        name: 'test.txt',
        type: 'file',
        size: 1024
      }

      await wrapper.vm.selectFile(testFile)

      expect(wrapper.vm.selectedFile).toEqual(testFile)
      expect(mockApi.default.get).toHaveBeenCalledWith(
        expect.stringContaining('/file/properties')
      )
    })

    it('should handle file download', async () => {
      const testFile: FileItem = {
        name: 'test.txt',
        type: 'file',
        size: 1024
      }

      await wrapper.vm.downloadFile(testFile)

      expect(mockApi.default.downloadFile).toHaveBeenCalledWith(
        'test.txt',
        'test.txt'
      )
    })

    it('should handle file download with selected file', async () => {
      wrapper.vm.selectedFile = {
        name: 'selected.txt',
        type: 'file',
        size: 512
      }

      await wrapper.vm.downloadFile()

      expect(mockApi.default.downloadFile).toHaveBeenCalledWith(
        'selected.txt',
        'selected.txt'
      )
    })

    it('should not download if no file specified or selected', async () => {
      wrapper.vm.selectedFile = null
      
      await wrapper.vm.downloadFile()

      expect(mockApi.default.downloadFile).not.toHaveBeenCalled()
    })
  })

  describe('File Upload', () => {
    it('should handle file upload with progress tracking', async () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
      const mockEvent = {
        target: {
          files: [mockFile],
          value: ''
        }
      } as any

      const uploadPromise = wrapper.vm.handleFileUpload(mockEvent)
      
      expect(wrapper.vm.uploadProgress.isUploading).toBe(true)
      expect(wrapper.vm.uploadProgress.fileName).toBe('test.txt')

      await uploadPromise

      expect(mockApi.default.post).toHaveBeenCalledWith(
        '/file/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      )
    })

    it('should reset upload progress after completion', async () => {
      const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' })
      const mockEvent = {
        target: {
          files: [mockFile],
          value: ''
        }
      } as any

      await wrapper.vm.handleFileUpload(mockEvent)

      // Wait for timeout to complete
      await new Promise(resolve => setTimeout(resolve, 1100))

      expect(wrapper.vm.uploadProgress.isUploading).toBe(false)
    })
  })

  describe('Directory Operations', () => {
    it('should create directory', async () => {
      vi.mocked(notifications.prompt).mockResolvedValue('New Folder')

      await wrapper.vm.promptCreateDirectory()

      expect(mockApi.default.post).toHaveBeenCalledWith('/file/create_dir', {
        path: 'New Folder'
      })
    })

    it('should not create directory if name is empty', async () => {
      vi.mocked(notifications.prompt).mockResolvedValue('')

      await wrapper.vm.promptCreateDirectory()

      expect(mockApi.default.post).not.toHaveBeenCalledWith('/file/create_dir', expect.anything())
    })

    it('should not create directory if user cancels', async () => {
      vi.mocked(notifications.prompt).mockResolvedValue(null)

      await wrapper.vm.promptCreateDirectory()

      expect(mockApi.default.post).not.toHaveBeenCalledWith('/file/create_dir', expect.anything())
    })
  })

  describe('File/Directory Manipulation', () => {
    it('should handle rename operation', async () => {
      const testFile: FileItem = {
        name: 'old-name.txt',
        type: 'file',
        size: 1024
      }

      vi.mocked(notifications.prompt).mockResolvedValue('new-name.txt')

      await wrapper.vm.promptRename(testFile)

      expect(mockApi.default.post).toHaveBeenCalledWith('/file/rename', {
        src: 'old-name.txt',
        dst: 'new-name.txt'
      })
    })

    it('should handle copy operation', async () => {
      const testFile: FileItem = {
        name: 'original.txt',
        type: 'file',
        size: 1024
      }

      vi.mocked(notifications.prompt).mockResolvedValue('copy.txt')

      await wrapper.vm.promptCopy(testFile)

      expect(mockApi.default.post).toHaveBeenCalledWith('/file/copy', {
        src: 'original.txt',
        dst: 'copy.txt'
      })
    })

    it('should handle delete operation with confirmation', async () => {
      const testFile: FileItem = {
        name: 'delete-me.txt',
        type: 'file',
        size: 1024
      }

      vi.mocked(notifications.confirm).mockResolvedValue(true)

      await wrapper.vm.handleDeleteFileOrDir(testFile)

      expect(notifications.confirm).toHaveBeenCalledWith(
        'Delete "delete-me.txt"?',
        'Confirm Deletion'
      )
      expect(mockApi.default.post).toHaveBeenCalledWith('/file/delete', {
        path: 'delete-me.txt'
      })
    })

    it('should not delete if user cancels confirmation', async () => {
      const testFile: FileItem = {
        name: 'keep-me.txt',
        type: 'file',
        size: 1024
      }

      vi.mocked(notifications.confirm).mockResolvedValue(false)

      await wrapper.vm.handleDeleteFileOrDir(testFile)

      expect(mockApi.default.post).not.toHaveBeenCalledWith('/file/delete', expect.anything())
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      vi.mocked(mockApi.default.get).mockRejectedValue(new Error('API Error'))

      await wrapper.vm.fetchFiles()

      expect(wrapper.vm.errorMsg).toBe('Failed to list files')
    })

    it('should handle upload errors', async () => {
      vi.mocked(mockApi.default.post).mockRejectedValue(new Error('Upload failed'))

      const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' })
      const mockEvent = {
        target: {
          files: [mockFile],
          value: ''
        }
      } as any

      await wrapper.vm.handleFileUpload(mockEvent)

      expect(notifications.error).toHaveBeenCalledWith(
        expect.stringContaining('Upload failed'),
        8000,
        true
      )
    })

    it('should handle download errors', async () => {
      vi.mocked(mockApi.default.downloadFile).mockRejectedValue(new Error('Download failed'))

      const testFile: FileItem = {
        name: 'test.txt',
        type: 'file',
        size: 1024
      }

      await wrapper.vm.downloadFile(testFile)

      expect(notifications.error).toHaveBeenCalledWith(
        'Download failed: Download failed'
      )
    })
  })

  describe('Refresh Operations', () => {
    it('should refresh all data', async () => {
      const result = await wrapper.vm.refresh()

      expect(result).toBe(true)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.fileProps).toBe(null)
    })

    it('should reload folder structure', async () => {
      await wrapper.vm.initFolderStructure()

      expect(wrapper.vm.treeReady).toBe(true)
      expect(mockApi.default.get).toHaveBeenCalledWith('/file/list_all_dirs')
    })
  })

  describe('Event Handling', () => {
    it('should handle models.json update events', async () => {
      wrapper.vm.selectedFile = {
        name: 'test.txt',
        type: 'file',
        size: 1024
      }

      await wrapper.vm.handleModelsJsonUpdate()

      expect(mockApi.default.get).toHaveBeenCalledWith(
        expect.stringContaining('/file/properties')
      )
    })
  })
})
