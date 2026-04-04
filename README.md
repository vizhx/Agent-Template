# Agent Playground 🤖

Welcome to the **Agent Playground**, a project designed to explore and experiment with LLM-based autonomous agents. 

> [!IMPORTANT]
> This is a **playground and experimental template**. It is built for development iterations and is **not intended for production deployment** as-is.

## 🚀 Overview
This repository provides a full-stack environment for building agents that can:
- **Stream responses**: Real-time Server-Sent Events (SSE) for incremental token output.
- **Call Tools**: Interleaved execution of text and function calls.
- **Support Interruption**: Stop long-running agents mid-generation.
- **Maintain Context**: Persistent storage for conversations and task states.

## 🏗️ Project Structure
The project is split into two main components:

- **`/backend`**: A Python (Django/Daphne) server.
  - **LLM Providers**: Gemini (Google) and Anthropic.
  - **Multi-turn conversation management**: State is persisted across turns.
  - **Extensible Tool Registry**: Easily add new capabilities to your agents.
- **`/frontend`**: A modern React application (Vite + TypeScript).
  - **Zustand**: Lightweight state management for tasks and UI state.
  - **Tailwind CSS**: Modern UI with a unified design system.
  - **Lucide Icons**: Crisp iconography for tools and actions.

## 🛠️ Getting Started

### Prerequisites
- Python 3.12+ (managed via `uv` recommended)
- Node.js 20+
- LLM API Keys (Gemini or Anthropic)

### Backend Setup
1. Navigate to `/backend`.
2. Install dependencies (using [uv](https://github.com/astral-sh/uv)):
   ```bash
   uv sync
   ```
3. Set up your environment variables in `.env` (use `.env.example` as a template):
   - `GOOGLE_API_KEY`
   - `ANTHROPIC_API_KEY`
4. Run migrations:
   ```bash
   uv run python manage.py migrate
   ```
5. Start the server:
   ```bash
   uv run daphne core.asgi:application
   ```

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## ⚖️ License
This project is provided "as-is" for educational and experimentation purposes.
