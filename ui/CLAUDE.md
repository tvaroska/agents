# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack application demonstrating CopilotKit with Google ADK (Agent Development Kit) integration. The project consists of:
- **Backend**: FastAPI server running a Google ADK agent (Python 3.13+)
- **Frontend**: Next.js 15 application with CopilotKit integration (React 19, TypeScript)

The app demonstrates AI agent capabilities including shared state management, generative UI, and frontend/backend tool integration using a "proverbs" demo agent.

## Development Commands

### Backend (from `/backend` directory)

Start the backend server:
```bash
cd backend
uv run python -m proverbs.ui
# or
uvicorn proverbs.ui:app --reload
```

Default port: 8000

**Environment requirements:**
- Set `GOOGLE_API_KEY` environment variable (required for ADK agent)
- Uses Python virtual environment in `.venv`
- Dependencies managed with `uv` and defined in `pyproject.toml`

### Frontend (from `/frontend` directory)

Development server:
```bash
cd frontend
npm run dev
```

Build:
```bash
npm run build --turbopack
```

Lint:
```bash
npm run lint
```

Production server:
```bash
npm run start
```

Default port: 3000

**Environment requirements:**
- `.env.local` must define `NEXT_PUBLIC_AGENT_URL` (default: http://localhost:8000)

## Architecture

### Backend: ADK Agent (`/backend/proverbs`)

**Agent structure:**
- `agent.py`: Core LlmAgent definition using Google ADK
  - Agent name: "ProverbsAgent"
  - Model: "gemini-2.5-flash"
  - Tools: `set_proverbs`, `get_weather`
  - State management via callbacks: `on_before_agent`, `before_model_modifier`, `simple_after_model_modifier`

- `ui.py`: FastAPI application wrapper
  - Wraps the agent with `ADKAgent` middleware from `ag-ui-adk`
  - Exposes agent via HTTP endpoint at `/`

**Key patterns:**
- State is managed through `ProverbsState` Pydantic model
- Agent uses callback hooks to inject state into system prompts
- `before_model_modifier`: Injects current proverbs state into system instruction
- `simple_after_model_modifier`: Stops consecutive tool calling after text response
- `set_proverbs` tool requires the COMPLETE list of proverbs (not incremental changes)

### Frontend: Next.js + CopilotKit (`/frontend`)

**Structure:**
- `app/page.tsx`: Main UI component with CopilotKit hooks
  - `useCoAgent`: Manages shared state with backend agent
  - `useCopilotAction`: Defines both frontend tools (`set_theme`) and generative UI renderers (`get_weather`)

- `app/api/copilotkit/route.ts`: CopilotKit runtime endpoint
  - Connects to backend ADK agent via `HttpAgent` from `@ag-ui/client`
  - Agent name must match between frontend (`useCoAgent`) and runtime config

**Key patterns:**
- Shared state syncs automatically between agent and UI via `useCoAgent`
- Generative UI: Backend tools can trigger frontend component rendering
- Frontend tools: Direct UI manipulation from chat (e.g., `set_theme`)
- The `available: "disabled"` parameter in generative UI actions prevents direct frontend invocation

### Communication Flow

1. User interacts with CopilotSidebar in Next.js app
2. Request goes to `/api/copilotkit` endpoint
3. CopilotRuntime forwards to backend ADK agent via HttpAgent
4. ADK agent processes with tools and state management
5. Response returns with state updates and optional generative UI
6. Frontend re-renders based on shared state changes

## Important Notes

- Both backend and frontend must be running for full functionality
- Backend agent state is stored in-memory (resets on server restart)
- The proverbs agent expects the FULL proverbs list in `set_proverbs` calls, not deltas
- Generative UI rendering happens client-side but is triggered by backend tool calls
