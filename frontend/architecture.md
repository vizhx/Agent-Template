# Frontend Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Architecture](#core-architecture)
5. [Component Details](#component-details)
6. [State Management](#state-management)
7. [Services Layer](#services-layer)
8. [Type System](#type-system)
9. [Utilities](#utilities)
10. [Styling](#styling)
11. [Data Flow](#data-flow)
12. [Configuration](#configuration)
13. [Development Guide](#development-guide)

---

## Overview

This is a React-based frontend application for an agentic chat platform that provides a real-time streaming interface for interacting with AI agents. The application features a split-pane layout with task management on the left and content preview on the right.

**Key Features:**
- Real-time streaming via Server-Sent Events (SSE)
- Task-based conversation management
- Tool execution visualization with approval workflow
- Content preview with side-by-side comparison
- Persistent state with localStorage
- Type-safe TypeScript implementation
- Responsive UI with Tailwind CSS

---

## Technology Stack

### Core Framework
- **React**: 19.1.0 - UI library
- **TypeScript**: 5.8.3 - Type safety
- **Vite**: 7.0.0 - Build tool and dev server

### State Management
- **Zustand**: 5.0.6 - Lightweight state management
- **localStorage**: Browser persistence

### HTTP & Real-time Communication
- **Axios**: 1.10.0 - HTTP client
- **EventSource**: Native SSE support
- **Server-Sent Events (SSE)**: Unidirectional streaming

### Routing & Navigation
- **React Router DOM**: 7.6.3 - Client-side routing

### Styling
- **Tailwind CSS**: 4.1.11 - Utility-first CSS
- **@tailwindcss/vite**: 4.1.11 - Vite integration
- **Custom CSS**: Tool call animations

### Development Tools
- **ESLint**: 9.29.0 - Code linting
- **TypeScript ESLint**: 8.34.1 - TypeScript linting
- **Vite Plugin React**: 4.5.2 - React fast refresh

### Additional Libraries
- **uuid**: 11.1.0 - Unique ID generation
- **react-diff-viewer-continued**: 4.0.6 - Diff visualization (available but not currently used)

---

## Project Structure

```
frontend/
├── index.html                         # HTML entry point
├── package.json                       # Dependencies & scripts
├── package-lock.json                  # Locked dependencies
├── vite.config.ts                     # Vite configuration
├── tsconfig.json                      # TypeScript root config
├── tsconfig.app.json                  # App TypeScript config
├── tsconfig.node.json                 # Node TypeScript config
├── tailwind.config.js                 # Tailwind CSS config
├── eslint.config.js                   # ESLint configuration
├── .env                               # Environment variables (gitignored)
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore patterns
├── README.md                          # Project documentation
│
├── public/                            # Static assets
│   └── vite.svg                       # Vite logo
│
└── src/                               # Source code
    ├── main.tsx                       # Application entry point
    ├── App.tsx                        # Root component
    ├── index.css                      # Global styles
    ├── vite-env.d.ts                  # Vite type definitions
    │
    ├── assets/                        # Static assets
    │   └── react.svg                  # React logo
    │
    ├── components/                    # React components
    │   ├── MainLayout.tsx             # Main layout container
    │   ├── SidePanel.tsx              # Left panel with chat
    │   ├── Stage.tsx                  # Right panel with content
    │   ├── TaskMessageList.tsx        # Message list container
    │   ├── MessageGroup.tsx           # Grouped messages by sender
    │   ├── TaskMessageItem.tsx        # Individual message renderer
    │   ├── TaskInputArea.tsx          # Message input component
    │   └── ContentEditor.tsx          # Content preview modal
    │
    ├── services/                      # API & service layer
    │   ├── api.ts                     # Axios instance & interceptors
    │   ├── taskService.ts             # Task API operations
    │   ├── sseService.ts              # SSE connection manager
    │   └── contentService.ts          # Content streaming service
    │
    ├── store/                         # State management
    │   ├── taskStore.ts               # Task state (Zustand)
    │   └── contentStore.ts            # Content state (Zustand)
    │
    ├── types/                         # TypeScript definitions
    │   └── index.ts                   # All type definitions
    │
    ├── utils/                         # Utility functions
    │   ├── message-parser.ts          # Parse streaming messages
    │   └── message-transformer.ts     # Transform backend messages
    │
    └── styles/                        # Additional styles
        └── tool-call-animations.css   # Tool call animations
```

---

## Core Architecture

### Architectural Pattern: Component-Service-Store

The frontend uses a clean three-layer architecture separating UI, business logic, and state management.

```
┌─────────────────────────────────────────────────────────────┐
│                    Components Layer                          │
│  • MainLayout (container)                                    │
│  • SidePanel (task chat)                                     │
│  • Stage (content preview)                                   │
│  • Message components                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Uses
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Store Layer (Zustand)                     │
│  • taskStore - Task & message state                          │
│  • contentStore - Content preview state                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ Calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
│  • taskService - Task CRUD operations                        │
│  • sseService - SSE connection management                    │
│  • contentService - Content streaming                        │
│  • api - HTTP client configuration                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/SSE
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Django)                          │
│  • REST API endpoints                                        │
│  • SSE streaming                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Clear boundaries between UI, state, and services
2. **Type Safety**: Comprehensive TypeScript types throughout
3. **Real-time Updates**: SSE for streaming responses
4. **Optimistic UI**: Immediate feedback with backend sync
5. **Persistent State**: localStorage for task continuity
6. **Component Composition**: Reusable, focused components

---

## Component Details

### 1. MainLayout (`components/MainLayout.tsx`)

**Purpose**: Root layout component that organizes the application into two main sections.

**Structure**:
```tsx
<div className="flex h-screen">
  <SidePanel />  {/* Left: Task chat */}
  <Stage />      {/* Right: Content preview */}
</div>
```

**Responsibilities**:
- Layout container for the entire application
- Manages flex layout for side-by-side panels
- No state management (pure layout)

---

### 2. SidePanel (`components/SidePanel.tsx`)

**Purpose**: Left panel containing task management and chat interface.

**Key Features**:
- Task creation and deletion
- Message list display
- Input area for new messages
- Sync with backend button
- Tool approval interface

**State Dependencies**:
```tsx
const {
  currentTask,
  isLoading,
  pendingToolApproval,
  createTask,
  deleteTask,
  syncWithBackend,
  approveToolCall
} = useTaskStore();
```

**UI Sections**:
1. **Header**: Task title with action buttons (new, delete, sync)
2. **Message List**: Scrollable message history
3. **Input Area**: Message composition and send

**Actions**:
- `handleCreateNewTask()`: Prompts for task name and creates new task
- `handleDeleteTask()`: Confirms and deletes current task
- `syncWithBackend()`: Manually syncs with backend

---

### 3. Stage (`components/Stage.tsx`)

**Purpose**: Right panel displaying content with preview capabilities.

**Key Features**:
- Display current content
- Side-by-side preview mode
- Automatic content updates via SSE

**State Dependencies**:
```tsx
const {
  currentContent,
  isPreviewOpen,
  oldHtmlContent,
  newHtmlContent,
  subscribe,
  unsubscribe
} = useContentStore();
```

**Display Modes**:

1. **Normal Mode**: Single content view
   - Shows current content as HTML
   - Full-width display

2. **Preview Mode**: Side-by-side comparison
   - Left: Current content
   - Right: Proposed changes
   - Triggered by tool preview events

**Lifecycle**:
```tsx
useEffect(() => {
  subscribe('global');  // Subscribe to content updates
  return () => unsubscribe();  // Cleanup on unmount
}, []);
```

---

### 4. TaskMessageList (`components/TaskMessageList.tsx`)

**Purpose**: Container for displaying grouped messages with auto-scroll.

**Props**:
```tsx
interface TaskMessageListProps {
  messages: Message[];
  onToolApproval?: (toolCallId: string, approved: boolean) => void;
  pendingToolApproval?: {
    toolCallId: string;
    toolName: string;
    input: Record<string, unknown>;
  } | null;
}
```

**Key Features**:
- Groups consecutive messages by sender
- Auto-scrolls to latest message
- Displays tool approval UI when needed
- Empty state handling

**Message Grouping Logic**:
```tsx
// Groups consecutive messages from same sender
messages.forEach((message) => {
  const lastGroup = groupedMessages[groupedMessages.length - 1];
  if (lastGroup && lastGroup.sender === message.sender) {
    lastGroup.messages.push(message);
  } else {
    groupedMessages.push({ sender: message.sender, messages: [message] });
  }
});
```

**Tool Approval UI**:
- Displayed at the end of message list
- Shows tool name and approval buttons
- Calls `onToolApproval` with approval decision

---

### 5. MessageGroup (`components/MessageGroup.tsx`)

**Purpose**: Renders a group of consecutive messages from the same sender.

**Props**:
```tsx
interface MessageGroupProps {
  messages: Message[];
  sender: 'user' | 'agent';
  onToolApproval?: (toolCallId: string, approved: boolean) => void;
  pendingToolApproval?: { ... } | null;
}
```

**Visual Design**:
- Avatar icon (👤 for user, 🤖 for agent)
- Sender name and timestamp
- Background color based on sender
- Token count display (if available)

**Layout**:
```
┌─────────────────────────────────────┐
│ 👤 You              10:30 AM        │
│                                     │
│ Message 1 content...                │
│ Message 2 content...                │
│                                     │
│                      150 tokens →   │
└─────────────────────────────────────┘
```

---

### 6. TaskMessageItem (`components/TaskMessageItem.tsx`)

**Purpose**: Renders individual message content with support for parsed content blocks.

**Props**:
```tsx
interface TaskMessageItemProps {
  message: Message;
  showHeader?: boolean;
  onToolApproval?: (toolCallId: string, approved: boolean) => void;
  pendingToolApproval?: { ... } | null;
}
```

**Content Rendering**:

1. **Text Content**: Plain text with whitespace preservation
2. **Tool Use**: Inline tool call badges
3. **Tool Result**: Result indicators

**Parsed Content Types**:
```tsx
// Text block
<span className="text-gray-700 whitespace-pre-wrap">
  {textContent}
</span>

// Tool call badge
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded">
  🔧 {toolName}
</span>

// Tool result badge
<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded">
  ✓ Result
</span>
```

**Streaming Indicator**:
- Shows animated dots when message is streaming
- Three pulsing dots with staggered animation

---

### 7. TaskInputArea (`components/TaskInputArea.tsx`)

**Purpose**: Message input component with auto-resize and keyboard shortcuts.

**Props**:
```tsx
interface TaskInputAreaProps {
  isLoading: boolean;
}
```

**Key Features**:
- Auto-resizing textarea (max 200px height)
- Enter to send, Shift+Enter for new line
- Loading state with spinner
- Disabled when loading

**State Management**:
```tsx
const [message, setMessage] = useState('');
const { sendMessage } = useTaskStore();
```

**Keyboard Handling**:
```tsx
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit(e);
  }
};
```

**Auto-resize Logic**:
```tsx
useEffect(() => {
  if (textareaRef.current) {
    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  }
}, [message]);
```

---

### 8. ContentEditor (`components/ContentEditor.tsx`)

**Purpose**: Modal component for side-by-side content preview (currently unused in favor of Stage preview).

**State Dependencies**:
```tsx
const {
  isPreviewOpen,
  oldHtmlContent,
  newHtmlContent,
  closePreview
} = useContentStore();
```

**Features**:
- Full-screen modal overlay
- Side-by-side content comparison
- Close button
- Renders HTML content safely

**Note**: This component is available but the preview functionality is currently handled by the Stage component instead.

---

## State Management

### 1. Task Store (`store/taskStore.ts`)

**Purpose**: Manages task state, messages, and SSE connections using Zustand.

**State Interface**:
```tsx
interface TaskState {
  currentTask: Task | null;
  isLoading: boolean;
  error: string | null;
  pendingToolApproval: {
    toolCallId: string;
    toolName: string;
    input: Record<string, unknown>;
  } | null;
  currentAgentMessageId: string | null;
  
  // Actions
  createTask: (title: string) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  syncWithBackend: () => Promise<void>;
  loadTasks: () => Promise<Task[]>;
  approveToolCall: (toolCallId: string, approved: boolean) => Promise<void>;
}
```

**Key Actions**:

#### `createTask(title: string)`
Creates a new task and establishes SSE connection.
```tsx
- Calls taskService.createTask()
- Updates currentTask state
- Saves to localStorage
- Establishes SSE connection via sseManager
```

#### `sendMessage(content: string)`
Sends a message and prepares for streaming response.
```tsx
- Creates user message locally
- Adds to currentTask.messages
- Creates placeholder agent message
- Calls taskService.sendMessageToTask()
- Response arrives via SSE connection
```

#### `approveToolCall(toolCallId: string, approved: boolean)`
Approves or rejects a tool execution.
```tsx
- Validates pendingToolApproval
- Calls taskService.approveToolCall()
- Clears pendingToolApproval
- Response arrives via SSE
```

#### `syncWithBackend()`
Synchronizes state with backend.
```tsx
- Checks localStorage for task ID
- Fetches task from backend
- Transforms backend messages to frontend format
- Establishes SSE connection
- Falls back to creating new task if none found
```

**Event Handling**:

The store subscribes to SSE events and handles them via `handleTaskEvent()`:

```tsx
type TaskEvent =
  | 'user_message'           // User message echo
  | 'assistant_chunk'        // Streaming response chunk
  | 'assistant_complete'     // Response complete
  | 'tool_approval_request'  // Tool needs approval
  | 'tool_executed'          // Tool was executed
  | 'error';                 // Error occurred
```

**Event Processing**:

1. **assistant_chunk**: Updates current agent message with new content
2. **tool_approval_request**: Sets pendingToolApproval state
3. **tool_executed**: Creates new agent message for next response
4. **error**: Sets error state and stops loading

**Persistence**:
```tsx
// Auto-save to localStorage on state changes
useTaskStore.subscribe((state) => {
  if (state.currentTask) {
    localStorage.setItem('currentTask', JSON.stringify(state.currentTask));
  }
});
```

**Initialization**:
```tsx
export const initializeTaskStore = async () => {
  const { syncWithBackend } = useTaskStore.getState();
  await syncWithBackend();
};
```

---

### 2. Content Store (`store/contentStore.ts`)

**Purpose**: Manages content preview state and SSE subscription.

**State Interface**:
```tsx
interface ContentState {
  currentContent: string;
  isPreviewOpen: boolean;
  oldHtmlContent: string;
  newHtmlContent: string;
  cleanup: (() => void) | null;
  
  closePreview: () => void;
  subscribe: (taskId: string) => void;
  unsubscribe: () => void;
}
```

**Key Actions**:

#### `subscribe(taskId: string)`
Subscribes to content update events.
```tsx
- Unsubscribes from previous subscription
- Calls contentService.subscribeToContentUpdates()
- Stores cleanup function
```

#### `closePreview()`
Closes the preview mode.
```tsx
- Sets isPreviewOpen to false
- Clears preview content
```

#### `unsubscribe()`
Cleans up SSE subscription.
```tsx
- Calls cleanup function
- Clears cleanup reference
```

**Event Types**:
```tsx
type ContentEvent =
  | 'initial_content'    // Initial content on connect
  | 'content_preview'    // Show preview comparison
  | 'content_updated'    // Content was updated
  | 'error';             // Error occurred
```

**Event Handling**:
```tsx
subscribeToContentUpdates((event) => {
  if (event.type === 'initial_content') {
    set({ currentContent: event.content });
  } else if (event.type === 'content_preview') {
    set({
      isPreviewOpen: true,
      oldHtmlContent: event.old_content,
      newHtmlContent: event.new_content
    });
  } else if (event.type === 'content_updated') {
    set({
      currentContent: event.content,
      isPreviewOpen: false
    });
  }
});
```

---

## Services Layer

### 1. API Service (`services/api.ts`)

**Purpose**: Configures Axios instance with interceptors for authentication and error handling.

**Configuration**:
```tsx
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Request Interceptor**:
```tsx
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Response Interceptor**:
```tsx
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Handle unauthorized access
    }
    return Promise.reject(error);
  }
);
```

**Exports**:
- `api`: Configured Axios instance
- `baseURL`: Backend URL for SSE connections

---

### 2. Task Service (`services/taskService.ts`)

**Purpose**: Provides API methods for task operations.

**Methods**:

#### `createTask(title: string): Promise<Task>`
Creates a new task.
```tsx
POST /api/tasks/
Body: { title, userId: 'user-1' }
Returns: Task object
```

#### `getTask(taskId: string): Promise<Task>`
Retrieves a task by ID.
```tsx
GET /api/tasks/{taskId}
Returns: Task object with messages
```

#### `getUserTasks(userId: string): Promise<Task[]>`
Gets all tasks for a user.
```tsx
GET /api/users/{userId}/tasks/
Returns: Array of Task objects
```

#### `sendMessageToTask(content: string, taskId: string): Promise<void>`
Sends a message to a task.
```tsx
POST /api/tasks/{taskId}/messages/
Body: {