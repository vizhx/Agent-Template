# Backend Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Architecture](#core-architecture)
5. [Component Details](#component-details)
6. [Database Models](#database-models)
7. [API Endpoints](#api-endpoints)
8. [Data Flow](#data-flow)
9. [Configuration](#configuration)
10. [Security & Performance](#security--performance)
11. [Development Guide](#development-guide)

---

## Overview

This is a Django-based backend implementation for an agentic chat application that provides real-time streaming responses from LLM providers (currently Anthropic Claude) with tool execution capabilities and user approval workflows.

**Key Features:**
- Real-time streaming via Server-Sent Events (SSE)
- Tool execution with approval workflow
- Async/await support throughout
- Pluggable LLM provider architecture
- Extensible tool system
- Global content management
- Task-based conversation management

---

## Technology Stack

### Core Framework
- **Django**: 5.2.7 - Web framework
- **Python**: 3.12+ - Programming language
- **uv**: Package manager (faster than pip)

### Database
- **SQLite**: Default database (development)
- **PostgreSQL**: Supported for production
- **Django ORM**: Database abstraction layer

### Real-time Communication
- **Server-Sent Events (SSE)**: Unidirectional streaming
- **Django Channels**: Async support
- **Daphne**: ASGI server
- **Redis**: Channel layer backend

### LLM Integration
- **Anthropic SDK**: 0.71.0+ - Claude API client
- **Model**: claude-sonnet-4-20250514

### Additional Libraries
- **djangorestframework**: 3.16.1+ - REST API framework
- **django-cors-headers**: 4.9.0+ - CORS handling
- **python-dotenv**: 1.1.1+ - Environment variables
- **channels-redis**: 4.3.0+ - Redis integration
- **psycopg2-binary**: 2.9.11+ - PostgreSQL adapter

---

## Project Structure

```
backend/
├── manage.py                          # Django CLI entry point
├── main.py                            # Alternative entry point (unused)
├── pyproject.toml                     # Project metadata & dependencies
├── uv.lock                            # Locked dependency versions
├── db.sqlite3                         # SQLite database file
├── scenic_places.txt                  # Demo content file
├── .env                               # Environment variables (gitignored)
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore patterns
├── .python-version                    # Python version (3.12)
├── README.md                          # Project documentation
│
├── core/                              # Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Configuration & settings
│   ├── urls.py                        # Root URL routing
│   ├── asgi.py                        # ASGI application
│   └── wsgi.py                        # WSGI application
│
└── chat/                              # Main Django app
    ├── __init__.py
    ├── apps.py                        # App configuration
    ├── admin.py                       # Django admin setup
    ├── models.py                      # Database models
    ├── views.py                       # API view handlers
    ├── urls.py                        # App URL patterns
    ├── controller.py                  # Task lifecycle controller
    ├── task.py                        # Task execution engine
    ├── content_manager.py             # Content state manager
    ├── message_parser.py              # Message parsing logic
    ├── tests.py                       # Test suite
    │
    ├── migrations/                    # Database migrations
    │   ├── __init__.py
    │   └── 0001_initial.py
    │
    ├── llm/                           # LLM provider layer
    │   ├── __init__.py
    │   ├── provider.py                # Base provider interface
    │   ├── anthropic.py               # Anthropic implementation
    │   └── prompts/
    │       └── __init__.py            # System prompt builder
    │
    ├── tools/                         # Tool system
    │   ├── __init__.py
    │   ├── base.py                    # Tool base & registry
    │   └── all_tools.py               # Tool implementations
    │
    ├── context/                       # Context management (future)
    │   └── __init__.py
    │
    └── utils/                         # Utilities (future)
        └── __init__.py
```

---

## Core Architecture

### Architectural Pattern: Simplified Two-Layer

The backend uses a streamlined two-layer architecture with only Controller and Task as orchestration layers, eliminating unnecessary complexity.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TS)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/SSE
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Views Layer (Django)                       │
│  • REST API endpoints                                        │
│  • SSE streaming handlers                                    │
│  • Request validation                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Delegates
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Controller (Singleton)                     │
│  • Task lifecycle management                                 │
│  • Active task caching                                       │
│  • Message/tool coordination                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ Manages
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Task Instances                             │
│  • Conversation history                                      │
│  • LLM streaming                                             │
│  • Tool execution                                            │
│  • Event broadcasting                                        │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ LLM  │ │ Tools  │ │Database│ │Content │ │  Event   │
│Provider│ │Registry│ │ Models │ │Manager │ │  Queues  │
└──────┘ └────────┘ └────────┘ └────────┘ └──────────┘
```

### Key Design Principles

1. **Simplicity**: Only two orchestration layers (Controller + Task)
2. **Async-First**: Async/await throughout for better concurrency
3. **Event-Driven**: Pub/sub pattern for real-time updates
4. **Pluggable**: Extensible LLM providers and tools
5. **Stateful**: In-memory task caching with DB persistence

---

## Component Details

### 1. Controller (`chat/controller.py`)

**Purpose**: Manages task lifecycle and coordinates between frontend and Task instances.

**Responsibilities:**
- Create new tasks
- Retrieve and cache active tasks
- Coordinate message processing
- Handle tool approval workflow
- Manage task deletion

**Key Attributes:**
```python
class Controller:
    active_tasks: Dict[str, Task]  # In-memory task cache
```

**Key Methods:**

#### `create_task(user_id: str, title: str) -> Dict[str, Any]`
Creates a new task and stores it in active tasks cache.
- Creates Task model in database
- Initializes Task instance
- Caches in `active_tasks`
- Returns task dictionary

#### `async get_task(task_id: str) -> Task`
Retrieves task from cache or loads from database.
- Checks `active_tasks` cache first
- If not found, loads from database
- Restores conversation history
- Caches for future use

#### `async process_message_async(task_id: str, message: str)`
Triggers background message processing.
- Retrieves task instance
- Calls `task.process_user_message()`
- Runs asynchronously (non-blocking)

#### `async approve_tool_async(task_id: str, tool_call_id: str, approved: bool)`
Handles tool approval/rejection.
- Retrieves task instance
- Calls `task.handle_tool_approval()`
- Runs asynchronously (non-blocking)

#### `async get_tasks_for_user(user_id: str) -> list`
Fetches all tasks for a user.
- Queries database by user_id
- Returns list of task dictionaries
- Ordered by creation date (newest first)

#### `async delete_task(task_id: str) -> bool`
Deletes a task.
- Removes from `active_tasks` cache
- Deletes from database (cascade)
- Returns success status

**Singleton Pattern:**
```python
# Global controller instance
controller = Controller()
```

---

### 2. Task (`chat/task.py`)

**Purpose**: Core task execution engine managing conversation flow, LLM interaction, and tool execution.

**Responsibilities:**
- Manage conversation history
- Stream LLM responses
- Parse assistant messages
- Execute tools with approval
- Broadcast events to subscribers
- Persist interactions to database

**Key Attributes:**
```python
class Task:
    id: str                                    # Task UUID
    user_id: str                               # User identifier
    title: str                                 # Task title
    interaction_record_id: str                 # DB record ID
    llm_provider: AnthropicProvider            # LLM instance
    pending_tool_request: Dict[str, Any]       # Awaiting approval
    conversation_history: List[LLMMessage]     # Full history
    tool_registry: ToolRegistry                # Available tools
    event_subscribers: List[asyncio.Queue]     # SSE subscribers
```

**Key Methods:**

#### `@classmethod create(user_id: str, title: str) -> Task`
Factory method to create new task.
- Creates TaskModel in database
- Creates empty InteractionRecord
- Returns Task instance

#### `@classmethod async from_model(task_model: TaskModel) -> Task`
Reconstructs task from database.
- Loads InteractionRecord
- Rebuilds conversation_history
- Returns Task instance

#### `async process_user_message(content: str)`
Processes user message and starts agent loop.
- Adds message to conversation_history
- Saves to InteractionRecord
- Broadcasts user_message event
- Calls `start_agent_loop()`

#### `async start_agent_loop()`
Main agent loop that continues until completion or approval request.
- Loops until stopped
- Calls `stream_llm_response()`
- Handles tool execution
- Stops on approval request or completion

#### `async stream_llm_response() -> AsyncGenerator`
Streams LLM response with tool handling.
- Accumulates content chunks
- Parses into structured blocks
- Detects tool calls
- Handles approval workflow
- Executes auto-approved tools
- Yields events to subscribers

#### `async handle_tool_approval(tool_call_id: str, approved: bool)`
Handles tool approval/rejection from frontend.
- Validates pending tool request
- Executes if approved
- Adds rejection message if rejected
- Continues agent loop

#### `async execute_tool(tool_call: Dict) -> str`
Executes a tool call.
- Retrieves tool from registry
- Calls tool.execute()
- Returns result string
- Handles errors gracefully

#### `async subscribe() -> asyncio.Queue`
Subscribes to task events.
- Creates new asyncio.Queue
- Adds to event_subscribers
- Returns queue for receiving events

#### `async unsubscribe(queue: asyncio.Queue)`
Unsubscribes from task events.
- Removes queue from subscribers
- Called on SSE disconnect

#### `async _broadcast_event(event: Dict)`
Broadcasts event to all subscribers.
- Iterates through event_subscribers
- Puts event in each queue
- Non-blocking operation

#### `async _save_interaction(data: Dict)`
Appends interaction to InteractionRecord.
- Creates record if doesn't exist
- Appends to interactions array
- Updates timestamp
- Saves to database

**Event Types:**
- `user_message` - User sent message
- `assistant_chunk` - Streaming response chunk
- `tool_approval_request` - Tool needs approval
- `tool_executed` - Tool was executed
- `assistant_complete` - Response complete
- `error` - Error occurred

---

### 3. LLM Provider System (`chat/llm/`)

#### Base Provider (`provider.py`)

**Data Classes:**
```python
@dataclass
class LLMMessage:
    role: str      # 'user', 'assistant', 'system'
    content: str

@dataclass
class LLMResponseChunk:
    content: str
    is_complete: bool = False
    tool_calls: Optional[List[Dict]] = None
```

**Abstract Base Class:**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_streaming_response(
        messages: List[LLMMessage],
        system_prompt: Optional[str],
        tools: Optional[List[Dict]],
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[LLMResponseChunk, None]
    
    @abstractmethod
    def format_messages(messages: List[LLMMessage]) -> List[Dict]
    
    def handle_error(error: Exception) -> None
```

#### Anthropic Provider (`anthropic.py`)

**Implementation:**
```python
class AnthropicProvider(LLMProvider):
    def __init__(api_key: str, model: str)
    async def generate_streaming_response(...)
    def format_messages(messages: List[LLMMessage])
```

**Features:**
- Streaming via `AsyncAnthropic`
- Handles `content_block_delta` events
- Processes text deltas
- Detects message completion
- Formats messages for Claude API

**Message Formatting:**
- Filters out system messages (handled separately)
- Only includes 'user' and 'assistant' roles
- Converts to Claude's expected format

#### System Prompts (`prompts/__init__.py`)

**Function:**
```python
def get_system_prompt(base_prompt: Optional[str] = None) -> str
```

**Features:**
- Builds system prompt with tool descriptions
- Fetches tools from ToolRegistry
- Formats tool usage guidelines
- Includes XML-style formatting rules
- Auto-generates tool documentation

**Default Base Prompt:**
```
"You are a helpful AI assistant, who is tasked with helping 
the user with the creation of a document"
```

---

### 4. Tool System (`chat/tools/`)

#### Base Tool (`base.py`)

**Abstract Base Class:**
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]
    needs_approval: bool
    show_preview: Optional[Callable]
    
    def requires_approval() -> bool
    async def preview(args: Dict, task_id: str)
    @abstractmethod
    async def execute(args: Dict, task_id: str) -> str
    def to_anthropic_tool() -> Dict
```

**Tool Registry:**
```python
class ToolRegistry:
    _instance: Optional['ToolRegistry']  # Singleton
    tools: Dict[str, BaseTool]
    
    def register_tool(tool: BaseTool)
    def get_tool(name: str) -> Optional[BaseTool]
    def get_all_tools() -> Dict[str, BaseTool]
    def has_tool(name: str) -> bool
    def remove_tool(name: str) -> bool
    def clear_tools()
    def get_anthropic_tools() -> list
```

#### Tool Implementations (`all_tools.py`)

**1. EditContentTool**
```python
class EditContentTool(BaseTool):
    name = "edit_content"
    needs_approval = True
    show_preview = _show_preview
    
    async def _show_preview(args, task_id)
    async def execute(args, task_id) -> str
```
- Edits global content
- Requires user approval
- Shows preview via SSE
- Updates ContentManager

**2. GetCurrentContentTool**
```python
class GetCurrentContentTool(BaseTool):
    name = "get_current_content"
    needs_approval = False
    
    async def execute(args, task_id) -> str
```
- Returns current content
- No approval needed
- Read-only operation

**3. CompleteTaskTool**
```python
class CompleteTaskTool(BaseTool):
    name = "complete_task"
    needs_approval = False
    
    async def execute(args, task_id) -> str
```
- Marks task complete
- Stops agent loop
- Returns final result

---

### 5. Content Manager (`chat/content_manager.py`)

**Purpose**: Manages global content state and broadcasts updates via SSE.

**Key Features:**
- Task-independent (shared across all tasks)
- File system persistence
- SSE broadcasting
- Preview support

**Attributes:**
```python
class ContentManager:
    current_content: str
    subscribers: Set[asyncio.Queue]
    content_file_path: str  # scenic_places.txt
```

**Key Methods:**

#### `_load_initial_content() -> str`
Loads content from scenic_places.txt on startup.

#### `get_content() -> str`
Returns current content string.

#### `update_content(new_content: str)`
Updates content after approval.
- Updates in-memory content
- Writes to file system
- Broadcasts content_updated event

#### `async subscribe() -> asyncio.Queue`
Subscribes to content updates.
- Creates new queue
- Sends initial_content event
- Returns queue

#### `async unsubscribe(queue: asyncio.Queue)`
Unsubscribes from content updates.

#### `async broadcast_content_preview(old: str, new: str)`
Broadcasts preview with old/new content.

#### `async _broadcast_update(update: Dict)`
Broadcasts update to all subscribers.

**Event Types:**
- `initial_content` - Initial content on subscribe
- `content_preview` - Preview before approval
- `content_updated` - Content was updated

**Singleton Pattern:**
```python
content_manager = ContentManager()
```

---

### 6. Message Parser (`chat/message_parser.py`)

**Purpose**: LLM-agnostic parser for assistant messages that extracts structured content blocks.

**Features:**
- Parses XML-style tool tags
- Extracts text and tool calls
- Handles partial messages during streaming
- Supports nested parameters

**Supported Tools:**
```python
TOOL_USE_NAMES = [
    "calculator", "current_time", "web_search", "thinking",
    "complete_task", "edit_content", "get_current_content"
]

TOOL_PARAM_NAMES = [
    "expression", "format", "query", "content",
    "summary", "newContent"
]
```

**Parser Class:**
```python
class MessageParser:
    tool_use_open_tags: Dict[str, str]
    tool_param_open_tags: Dict[str, str]
    
    def parse(assistant_message: str) -> List[Dict]
```

**Output Format:**
```python
[
    {
        "type": "text",
        "content": "Here's the result...",
        "partial": False
    },
    {
        "type": "tool_use",
        "name": "edit_content",
        "params": {"newContent": "..."},
        "partial": False
    }
]
```

**Parsing States:**
1. Parsing text content
2. Detected tool opening tag
3. Parsing tool parameters
4. Detected parameter closing tag
5. Detected tool closing tag
6. Finalize blocks

**Global Function:**
```python
def parse_assistant_message(message: str) -> List[Dict]
```

---

## Database Models

### 1. Task Model (`chat/models.py`)

**Purpose**: Represents a conversation task/session.

**Schema:**
```python
class Task(models.Model):
    id = UUIDField(primary_key=True, default=uuid4)
    user_id = CharField(max_length=255, db_index=True)
    title = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['user_id', '-created_at'])
        ]
```

**Relationships:**
- One-to-many with InteractionRecord

**Indexes:**
- Primary: `id` (UUID)
- Composite: `user_id` + `created_at` (descending)

### 2. InteractionRecord Model

**Purpose**: Stores complete interaction data as JSON for a task.

**Schema:**
```python
class InteractionRecord(models.Model):
    id = UUIDField(primary_key=True, default=uuid4)
    task = ForeignKey(Task, on_delete=CASCADE, related_name='interactions')
    ts = BigIntegerField()  # Timestamp in milliseconds
    data = JSONField()      # Complete interaction data
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['ts']
        indexes = [
            Index(fields=['task', 'ts'])
        ]
```

