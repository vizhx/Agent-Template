# Backend for Agentic Chat Application

This is the backend service for an agentic chat application, built with Django. It provides real-time streaming responses from LLM providers, tool execution capabilities, and user approval workflows.

## Features

- Real-time streaming via Server-Sent Events (SSE)
- Tool execution with approval workflow
- Async/await support throughout
- Pluggable LLM provider architecture
- Extensible tool system
- Global content management
- Task-based conversation management

## Technology Stack

- **Django**: 5.2.7
- **Python**: 3.12+
- **uv**: Package manager
- **SQLite/PostgreSQL**: Database
- **Django Channels**: Async support
- **Daphne**: ASGI server
- **Redis**: Channel layer backend
- **Anthropic SDK**: LLM integration

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [repository-url]
    cd backend
    ```

2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the `backend/` directory based on `.env.example` and fill in your details, especially `SECRET_KEY` and `ANTHROPIC_API_KEY`.

    ```
    # .env
    SECRET_KEY='your-secret-key'
    DEBUG=True
    ALLOWED_HOSTS='*'
    ANTHROPIC_API_KEY='your-anthropic-api-key'
    ```

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Start the development server:**
    ```bash
    daphne -b 0.0.0.0 -p 8000 core.asgi:application
    ```
    Alternatively, for basic Django development (without Channels):
    ```bash
    python manage.py runserver
    ```

## Project Structure

```
backend/
├── manage.py
├── pyproject.toml
├── uv.lock
├── db.sqlite3
├── scenic_places.txt
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── README.md
│
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── chat/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── controller.py
    ├── task.py
    ├── content_manager.py
    ├── message_parser.py
    ├── llm/
    │   ├── provider.py
    │   └── anthropic.py
    ├── tools/
    │   ├── base.py
    │   └── all_tools.py
    └── migrations/
```

## API Endpoints

(To be documented as they are implemented)

## Development Guide

(To be documented as development progresses)
