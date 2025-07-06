# Frontend Documentation

## Architecture Overview

The frontend is built using Vue.js 3 with TypeScript, providing a modern and responsive user interface for ComfyUI workflow management and image generation. The architecture follows Vue.js best practices with Composition API, Pinia for state management, and a component-based structure.

## Core Components

### State Management (Pinia)

#### ComfyUI Store
**Location:** `front/src/stores/comfyui.ts`

**Purpose:** Central state management for ComfyUI workflow generation and model management

**Key State:**
- `models` - Available models registry
- `generationParams` - Current generation parameters
- `generationResults` - Generated images and metadata
- `isGenerating` - Generation status flag
- `websocketConnection` - WebSocket connection state

**Methods:**
- `fetchModels()` - Loads available models from API
- `generateWorkflow()` - Generates and executes workflow
- `updateGenerationParams()` - Updates generation parameters
- `connectWebSocket()` - Establishes WebSocket connection for real-time updates

#### Additional Stores
- `front/src/stores/auth.ts` - Authentication state management
- `front/src/stores/bundles.ts` - Bundle management state
- `front/src/stores/models.ts` - Model management state
- `front/src/stores/ui.ts` - UI state management
- `front/src/stores/workflows.ts` - Workflow management state

### API Service

#### ApiConfig Class
**Location:** `front/src/services/api.ts`

**Architecture:** Class-based API service with dependency injection support

**Purpose:** Encapsulates API configuration and provides testable service

**Features:**
- Token management with localStorage
- Request/response interceptors
- Error handling with automatic redirects
- File download functionality
- TypeScript support with interfaces

**Key Methods:**
- `getAuthToken()` - Retrieves authentication token
- `setAuthToken(token)` - Sets authentication token
- `getApiInstance()` - Returns configured Axios instance
- `setRouter(router)` - Configures router for redirections
- `downloadFile(path, filename)` - Downloads files with progress tracking

### Views and Pages

#### ComfyUI Generation View
**Location:** `front/src/views/ComfyUIView.vue`

**Purpose:** Main interface for AI image generation using ComfyUI workflows

**Features:**
- **Collapsible Parameter Form:** Intuitive form for generation parameters
- **Model Selection:** Dropdown with available models (Flux, SDXL, HiDream)
- **Advanced Options:** LoRA integration, optimization settings, detail enhancement
- **Real-time Preview:** WebSocket-based live generation updates
- **Results Management:** Image preview, download, and history

**Key Components:**
- Model selector with filtering
- Parameter input forms with validation
- Progress indicators and status displays
- Image gallery with download functionality

#### Additional Views
- `front/src/views/AboutView.vue` - About page
- `front/src/views/BundleManager.vue` - Bundle management interface
- `front/src/views/FileManager.vue` - File management interface
- `front/src/views/Install.vue` - Installation management
- `front/src/views/JsonEditor.vue` - JSON model editing
- `front/src/views/Login.vue` - Authentication interface
- `front/src/views/Settings.vue` - Application settings

### Reusable Components

#### ModelSelectorModal
**Location:** `front/src/components/common/ModelSelectorModal.vue`

**Purpose:** Reusable modal component for model selection with filtering

**Features:**
- Tag-based filtering and grouping
- Search functionality
- Multi-select capabilities
- Responsive design

**Props:**
- `visible` - Modal visibility state
- `selectedModels` - Currently selected models
- `modelGroups` - Available model groups

**Events:**
- `close` - Modal close event
- `apply` - Selection apply event

#### InstallProgressIndicator
**Location:** `front/src/components/common/InstallProgressIndicator.vue`

**Purpose:** Visual progress indicator for installations and downloads

**Features:**
- Multiple progress states (idle, in-progress, completed, error)
- Animated progress bars
- Status text and icons
- Configurable appearance

**Props:**
- `progress` - Progress percentage (0-100)
- `status` - Current status ('idle', 'downloading', 'completed', 'error')
- `message` - Status message

#### Type Definitions

#### ComfyUI Types
**Location:** `front/src/stores/types/comfyui.types.ts`

**Purpose:** TypeScript definitions for ComfyUI-related data structures

#### Additional Type Files
- `front/src/stores/types/bundles.types.ts` - Bundle management types
- `front/src/stores/types/models.types.ts` - Model management types
- `front/src/stores/types/ui.types.ts` - UI state types
- `front/src/stores/types/workflows.types.ts` - Workflow types
- `front/src/types/stores.d.ts` - General store type definitions

## Advanced Features

### WebSocket Integration
**Implementation:** Integrated into ComfyUI store

**Purpose:** Real-time updates during image generation

**Features:**
- Live progress updates
- Generation status notifications
- Error handling and reconnection
- Automatic connection management

**Usage:**
```typescript
// Store automatically manages WebSocket connection
const comfyStore = useComfyUIStore();
await comfyStore.connectWebSocket();
```

### Responsive Design
**Implementation:** Tailwind CSS with responsive utilities

**Features:**
- Mobile-first approach
- Adaptive layouts for different screen sizes
- Touch-friendly interfaces
- Optimized for tablets and desktop

### Real-time Generation Preview
**Implementation:** WebSocket-based live updates

**Features:**
- Live generation progress
- Intermediate result previews
- Status updates and notifications
- Error handling and recovery

## Testing

### Test Structure
**Location:** `front/src/`

**Test Files:**
- `stores/comfyui.test.ts` - Store unit tests
- `services/__tests__/api.test.ts` - API service tests
- `components/examples/__tests__/` - Component tests

### Testing Strategy
- **Unit Tests:** Store methods, utility functions, composables
- **Component Tests:** Vue components with Vue Testing Library
- **Integration Tests:** API service integration
- **E2E Tests:** User workflows and interactions

### Running Tests
```bash
# Run all tests
npm run test

# Run specific test file
npm run test stores/comfyui.test.ts

# Run with coverage
npm run test:coverage
```

## UI/UX Guidelines

### Design System
- **Color Palette:** Consistent color scheme using Tailwind CSS
- **Typography:** Hierarchical text styling with proper contrast
- **Spacing:** Consistent spacing using Tailwind spacing scale
- **Components:** Reusable component library with consistent styling

### User Experience
- **Loading States:** Clear loading indicators for all async operations
- **Error Handling:** User-friendly error messages and recovery options
- **Progressive Disclosure:** Collapsible sections for advanced options
- **Accessibility:** ARIA labels, keyboard navigation, screen reader support

### Performance
- **Lazy Loading:** Components and routes loaded on demand
- **Image Optimization:** Efficient image loading and caching
- **Bundle Splitting:** Code splitting for optimal loading
- **State Management:** Efficient state updates and reactivity

## Development Guidelines

### Component Development
1. Use Composition API for better TypeScript support
2. Implement proper prop validation
3. Use TypeScript interfaces for type safety
4. Follow Vue.js style guide conventions
5. Include comprehensive component documentation

### State Management
1. Use Pinia for global state management
2. Keep stores focused and single-purpose
3. Implement proper error handling in actions
4. Use computed properties for derived state
5. Maintain immutability in state updates

### API Integration
1. Use the `ApiConfig` class for consistent API calls
2. Implement proper error handling and user feedback
3. Use TypeScript interfaces for API responses
4. Handle loading states appropriately
5. Implement retry logic for failed requests

## Configuration

### Environment Variables
- `VITE_API_BASE_URL` - Backend API base URL
- `VITE_WS_BASE_URL` - WebSocket server URL
- `VITE_APP_TITLE` - Application title
- `VITE_DEBUG` - Debug mode flag

### Build Configuration
**Location:** `front/vite.config.js`

**Features:**
- TypeScript support
- Vue.js single-file components
- Tailwind CSS integration
- Development server configuration
- Build optimization

### Router Configuration
**Location:** `front/src/router/index.ts`

**Routes:**
- `/` - Home/Dashboard
- `/comfyui` - ComfyUI generation interface
- `/models` - Model management
- `/workflows` - Workflow management
- `/login` - Authentication

## Styling and Theming

### Tailwind CSS
**Configuration:** `front/tailwind.config.js`

**Features:**
- Custom color palette
- Responsive breakpoints
- Component utilities
- Dark mode support

### Component Styling
- **Scoped Styles:** Component-specific styling
- **Utility Classes:** Tailwind utility classes for rapid development
- **CSS Variables:** Custom properties for theming
- **Responsive Design:** Mobile-first responsive utilities

## Build and Deployment

### Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run in development mode with hot reload
npm run serve
```

### Production Build
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Storybook
```bash
# Run Storybook for component development
npm run storybook

# Build Storybook
npm run build-storybook
```

## Best Practices

### Code Quality
- Use ESLint and Prettier for code formatting
- Follow Vue.js and TypeScript best practices
- Write comprehensive tests for components and stores
- Use semantic HTML and proper accessibility attributes

### Performance Optimization
- Implement lazy loading for routes and components
- Use computed properties for expensive calculations
- Optimize images and assets
- Minimize bundle size with proper tree shaking

### Security
- Sanitize user inputs
- Implement proper authentication checks
- Use HTTPS for all API communications
- Validate data on both client and server

This documentation provides a comprehensive overview of the frontend architecture and implementation details for the ComfyUI Model Manager application.
