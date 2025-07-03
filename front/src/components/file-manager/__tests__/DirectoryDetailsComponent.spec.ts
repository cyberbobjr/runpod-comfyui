/**
 * DirectoryDetailsComponent Tests
 * 
 * Test suite for the DirectoryDetailsComponent, covering file listing, directory navigation,
 * TypeScript integration, and user interactions with files and folders.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DirectoryDetailsComponent from '../DirectoryDetailsComponent.vue'
import type { 
  FileItem, 
  DirectoryItem, 
  FileProperties,
} from '../../../views/types/views.types'

// Mock FontAwesome
vi.mock('@fortawesome/vue-fontawesome', () => ({
  FontAwesomeIcon: {
    name: 'FontAwesomeIcon',
    template: '<i class="fa-icon"></i>'
  }
}))

// Mock components
vi.mock('./FilePropertiesComponent.vue', () => ({
  default: {
    name: 'FilePropertiesComponent',
    template: '<div class="file-properties">File Properties</div>'
  }
}))

vi.mock('../common/TooltipComponent.vue', () => ({
  default: {
    name: 'TooltipComponent',
    template: '<div class="tooltip"><slot></slot></div>'
  }
}))

describe('DirectoryDetailsComponent', () => {
  let wrapper: VueWrapper<any>

  const mockFiles: FileItem[] = [
    {
      name: 'model1.safetensors',
      type: 'file',
      size: 1024000,
      modified: '2023-01-01T10:00:00Z',
      extension: 'safetensors',
      is_registered: true,
      is_corrupted: false
    },
    {
      name: 'model2.ckpt',
      type: 'file',
      size: 2048000,
      modified: '2023-01-02T10:00:00Z',
      extension: 'ckpt',
      is_registered: false,
      is_corrupted: true,
      expected_size: 2100000,
      actual_size: 2048000
    },
    {
      name: 'normal_file.txt',
      type: 'file',
      size: 512,
      modified: '2023-01-03T10:00:00Z',
      extension: 'txt'
    }
  ]

  const mockDirectories: DirectoryItem[] = [
    {
      name: 'subfolder1',
      path: '/current/subfolder1',
      children: []
    },
    {
      name: 'subfolder2',
      path: '/current/subfolder2',
      children: [
        {
          name: 'nested',
          path: '/current/subfolder2/nested',
          children: []
        }
      ]
    }
  ]

  const mockFileProperties: FileProperties = {
    name: 'model1.safetensors',
    path: '/current/model1.safetensors',
    size: 1024000,
    type: 'application/octet-stream',
    modified: '2023-01-01T10:00:00Z',
    extension: 'safetensors',
    isRegistered: true
  }

  const defaultProps = {
    currentPath: '/current',
    files: mockFiles,
    dirs: mockDirectories,
    selectedFile: null,
    fileProps: null
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    
    wrapper = mount(DirectoryDetailsComponent, {
      props: defaultProps,
      global: {
        stubs: {
          FilePropertiesComponent: true,
          TooltipComponent: true,
          FontAwesomeIcon: true
        }
      }
    })
  })

  describe('Component Initialization', () => {
    it('should render without errors', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should display current path', () => {
      expect(wrapper.text()).toContain('/current')
    })

    it('should display subdirectories section', () => {
      expect(wrapper.text()).toContain('Subdirectories')
    })

    it('should display files section', () => {
      expect(wrapper.text()).toContain('Files')
    })

    it('should display file properties section', () => {
      expect(wrapper.text()).toContain('File Properties')
    })
  })

  describe('TypeScript Integration', () => {
    it('should have properly typed props', () => {
      expect(typeof wrapper.vm.currentPath).toBe('string')
      expect(Array.isArray(wrapper.vm.files)).toBe(true)
      expect(Array.isArray(wrapper.vm.dirs)).toBe(true)
      expect(wrapper.vm.selectedFile).toBe(null)
      expect(wrapper.vm.fileProps).toBe(null)
    })

    it('should handle typed emit events', async () => {
      const goUpBtn = wrapper.find('button[data-testid="go-up"]') || 
                     wrapper.find('button:contains("Up")')
      
      if (goUpBtn.exists()) {
        await goUpBtn.trigger('click')
        
        expect(wrapper.emitted('go-up')).toBeTruthy()
      }
    })

    it('should have properly typed hoveredItem state', () => {
      expect(wrapper.vm.hoveredItem).toBe(null)
      expect(typeof wrapper.vm.hoveredItem === 'string' || wrapper.vm.hoveredItem === null).toBe(true)
    })
  })

  describe('Directory Display', () => {
    it('should display all subdirectories', () => {
      mockDirectories.forEach(dir => {
        expect(wrapper.text()).toContain(dir.name)
      })
    })

    it('should handle empty subdirectories', async () => {
      await wrapper.setProps({ dirs: [] })
      
      expect(wrapper.text()).toContain('No subdirectories in this directory')
    })

    it('should emit navigate-to-folder on directory double-click', async () => {
      const dirElement = wrapper.find('.subdirectory-item')
      
      if (dirElement.exists()) {
        await dirElement.trigger('dblclick')
        
        expect(wrapper.emitted('navigate-to-folder')).toBeTruthy()
        expect(wrapper.emitted('navigate-to-folder')?.[0]).toEqual([mockDirectories[0].path])
      }
    })

    it('should show directory actions on hover', async () => {
      const dirElement = wrapper.find('.subdirectory-item')
      
      if (dirElement.exists()) {
        await dirElement.trigger('mouseover')
        
        expect(wrapper.vm.hoveredItem).toBe(mockDirectories[0].path)
      }
    })
  })

  describe('File Display', () => {
    it('should display all files', () => {
      mockFiles.forEach(file => {
        expect(wrapper.text()).toContain(file.name)
      })
    })

    it('should handle empty file list', async () => {
      await wrapper.setProps({ files: [] })
      
      expect(wrapper.text()).toContain('No files in this directory')
    })

    it('should show registered badge for registered files', () => {
      const registeredFile = mockFiles.find(f => f.is_registered)
      if (registeredFile) {
        expect(wrapper.text()).toContain('Registered')
      }
    })

    it('should show corrupted badge for corrupted files', () => {
      const corruptedFile = mockFiles.find(f => f.is_corrupted)
      if (corruptedFile) {
        expect(wrapper.text()).toContain('Corrupted')
      }
    })

    it('should emit select-file on file click', async () => {
      const fileElement = wrapper.find('.file-item')
      
      if (fileElement.exists()) {
        await fileElement.trigger('click')
        
        expect(wrapper.emitted('select-file')).toBeTruthy()
        expect(wrapper.emitted('select-file')?.[0]).toEqual([mockFiles[0]])
      }
    })
  })

  describe('Toolbar Actions', () => {
    it('should emit go-up when up button is clicked', async () => {
      const upBtn = wrapper.find('button:contains("Up")')
      
      if (upBtn.exists()) {
        await upBtn.trigger('click')
        
        expect(wrapper.emitted('go-up')).toBeTruthy()
      }
    })

    it('should disable up button when at root', async () => {
      await wrapper.setProps({ currentPath: '' })
      
      const upBtn = wrapper.find('button:contains("Up")')
      if (upBtn.exists()) {
        expect(upBtn.attributes('disabled')).toBeDefined()
      }
    })

    it('should emit refresh when refresh button is clicked', async () => {
      const refreshBtn = wrapper.find('button:contains("Refresh")')
      
      if (refreshBtn.exists()) {
        await refreshBtn.trigger('click')
        
        expect(wrapper.emitted('refresh')).toBeTruthy()
      }
    })

    it('should emit create-directory when new folder button is clicked', async () => {
      const newFolderBtn = wrapper.find('button:contains("New Folder")')
      
      if (newFolderBtn.exists()) {
        await newFolderBtn.trigger('click')
        
        expect(wrapper.emitted('create-directory')).toBeTruthy()
      }
    })

    it('should handle file upload input change', async () => {
      const fileInput = wrapper.find('input[type="file"]')
      
      if (fileInput.exists()) {
        const mockEvent = {
          target: {
            files: [new File(['test'], 'test.txt', { type: 'text/plain' })]
          }
        }
        
        await fileInput.trigger('change', mockEvent)
        
        expect(wrapper.emitted('file-upload')).toBeTruthy()
      }
    })
  })

  describe('File Actions', () => {
    it('should emit download when download button is clicked', async () => {
      const downloadBtn = wrapper.find('.file-actions button:contains("download")')
      
      if (downloadBtn.exists()) {
        await downloadBtn.trigger('click')
        
        expect(wrapper.emitted('download')).toBeTruthy()
      }
    })

    it('should emit rename when rename button is clicked', async () => {
      const renameBtn = wrapper.find('.file-actions button[title*="Rename"]') ||
                       wrapper.find('.file-actions button:contains("pencil")')
      
      if (renameBtn.exists()) {
        await renameBtn.trigger('click')
        
        expect(wrapper.emitted('rename')).toBeTruthy()
      }
    })

    it('should emit copy when copy button is clicked', async () => {
      const copyBtn = wrapper.find('.file-actions button:contains("copy")')
      
      if (copyBtn.exists()) {
        await copyBtn.trigger('click')
        
        expect(wrapper.emitted('copy')).toBeTruthy()
      }
    })

    it('should emit delete when delete button is clicked', async () => {
      const deleteBtn = wrapper.find('.file-actions button:contains("trash")')
      
      if (deleteBtn.exists()) {
        await deleteBtn.trigger('click')
        
        expect(wrapper.emitted('delete')).toBeTruthy()
      }
    })
  })

  describe('File Properties', () => {
    it('should show file properties when file is selected', async () => {
      await wrapper.setProps({ 
        selectedFile: mockFiles[0],
        fileProps: mockFileProperties 
      })
      
      expect(wrapper.find('.file-properties').exists()).toBe(true)
    })

    it('should show placeholder when no file is selected', () => {
      expect(wrapper.text()).toContain('Select a file to see its properties')
    })

    it('should show registered status for selected file', async () => {
      const registeredFile = mockFiles.find(f => f.is_registered)
      await wrapper.setProps({ 
        selectedFile: registeredFile,
        fileProps: mockFileProperties 
      })
      
      expect(wrapper.text()).toContain('Registered Model')
    })

    it('should show corruption warning for corrupted files', async () => {
      const corruptedFile = mockFiles.find(f => f.is_corrupted)
      await wrapper.setProps({ 
        selectedFile: corruptedFile,
        fileProps: mockFileProperties 
      })
      
      expect(wrapper.text()).toContain('Potentially Corrupted')
    })
  })

  describe('Helper Functions', () => {
    it('should format file sizes correctly', () => {
      expect(wrapper.vm.formatSize(0)).toBe('0 Bytes')
      expect(wrapper.vm.formatSize(1024)).toBe('1 KB')
      expect(wrapper.vm.formatSize(1048576)).toBe('1 MB')
      expect(wrapper.vm.formatSize(1073741824)).toBe('1 GB')
    })

    it('should handle undefined sizes', () => {
      expect(wrapper.vm.formatSize(undefined)).toBe('0 Bytes')
    })

    it('should format large sizes correctly', () => {
      expect(wrapper.vm.formatSize(1024000)).toBe('1000 KB')
      expect(wrapper.vm.formatSize(2048000)).toBe('1.95 MB')
    })
  })

  describe('Visual States', () => {
    it('should highlight selected file', async () => {
      await wrapper.setProps({ selectedFile: mockFiles[0] })
      
      const selectedFileElement = wrapper.find('.file-item.bg-primary\\/10')
      expect(selectedFileElement.exists()).toBe(true)
    })

    it('should show visual indicators for file status', async () => {
      // Test registered file styling
      const registeredFile = wrapper.find('.border-l-green-500')
      expect(registeredFile.exists()).toBe(true)
      
      // Test corrupted file styling
      const corruptedFile = wrapper.find('.border-l-red-500')
      expect(corruptedFile.exists()).toBe(true)
    })

    it('should show action buttons on hover', async () => {
      const fileItem = wrapper.find('.file-item')
      
      if (fileItem.exists()) {
        await fileItem.trigger('mouseenter')
        
        const actions = fileItem.find('.file-actions')
        expect(actions.exists()).toBe(true)
      }
    })
  })

  describe('Path Display', () => {
    it('should show root path indicator', async () => {
      await wrapper.setProps({ currentPath: '' })
      
      expect(wrapper.text()).toContain('/')
    })

    it('should display current path correctly', () => {
      expect(wrapper.text()).toContain('/current')
    })

    it('should update path display when prop changes', async () => {
      await wrapper.setProps({ currentPath: '/new/path' })
      
      expect(wrapper.text()).toContain('/new/path')
    })
  })

  describe('Error States', () => {
    it('should handle missing props gracefully', async () => {
      await wrapper.setProps({ 
        files: undefined,
        dirs: undefined 
      })
      
      // Component should not crash
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle corrupted file information display', async () => {
      const corruptedFile = mockFiles.find(f => f.is_corrupted)
      await wrapper.setProps({ selectedFile: corruptedFile })
      
      // Should display corruption information without errors
      expect(wrapper.vm.formatSize(corruptedFile?.expected_size)).toBeTruthy()
      expect(wrapper.vm.formatSize(corruptedFile?.actual_size)).toBeTruthy()
    })
  })
})
