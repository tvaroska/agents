# Kanban Board Implementation Plan

## Overview
Build a Kanban board application with 4 columns (New Tasks, In Process, Waiting for Feedback, Done) where tasks are managed by an ADK agent and the UI uses AG-UI protocol for communication.

## Architecture

### Backend: ADK Agent (`/backend/kanban`)

#### Data Model
```python
class TaskStatus(Enum):
    NEW = "new"
    IN_PROCESS = "in_process"
    WAITING_FEEDBACK = "waiting_feedback"
    DONE = "done"

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    assigned_agent: Optional[str]

class KanbanState(BaseModel):
    tasks: List[Task]
```

#### Agent Tools
1. **create_task(title: str, description: str)** → Creates new task in "New Tasks" column
2. **update_task(task_id: str, title: str, description: str)** → Updates task details
3. **move_task(task_id: str, new_status: TaskStatus)** → Moves task between columns
4. **delete_task(task_id: str)** → Removes task
5. **get_tasks(status: Optional[TaskStatus])** → Retrieves tasks (filtered or all)

#### Agent Implementation (`/backend/kanban/agent.py`)
- LlmAgent named "KanbanAgent"
- Model: "gemini-2.5-flash"
- State management via callbacks:
  - `on_before_agent`: Initialize empty task list if not exists
  - `before_model_modifier`: Inject current tasks into system prompt
  - `after_model_callback`: Control tool calling flow

#### FastAPI Wrapper (`/backend/kanban/ui.py`)
- Wrap agent with `ADKAgent` middleware
- Expose via `add_adk_fastapi_endpoint` at path "/"
- Run on port 8001 (to avoid conflict with proverbs agent)

### Frontend: Next.js Kanban UI (`/frontend`)

#### New Page: `/app/kanban/page.tsx`
```tsx
- Use `useCoAgent` hook to sync with KanbanAgent state
- Display 4 columns: New Tasks, In Process, Waiting for Feedback, Done
- Drag-and-drop functionality for moving tasks
- Click to edit task details
- Button to create new tasks
- Real-time state sync with backend agent
```

#### UI Components Structure
```
/app/kanban/
  page.tsx           // Main Kanban board page
  components/
    KanbanBoard.tsx  // Board container with 4 columns
    KanbanColumn.tsx // Single column component
    TaskCard.tsx     // Individual task card
```

#### CopilotKit Integration
- Update `/app/api/copilotkit/route.ts` to add KanbanAgent
- Add agent to runtime configuration:
  ```ts
  agents: {
    ProverbsAgent: ...,
    KanbanAgent: new HttpAgent({
      url: process.env.NEXT_PUBLIC_KANBAN_AGENT_URL || "http://localhost:8001"
    })
  }
  ```

#### Layout Options
**Option A**: New route with separate layout
- `/app/kanban/layout.tsx` with CopilotKit configured for KanbanAgent
- Keeps Kanban isolated from Proverbs demo

**Option B**: Shared layout with agent switcher
- Update root layout to support multiple agents
- Add navigation between Proverbs and Kanban demos

## Implementation Steps

### Phase 1: Backend Agent
1. Create `/backend/kanban/` directory
2. Implement data models in `agent.py`
3. Create agent tools (create_task, update_task, move_task, delete_task)
4. Implement LlmAgent with callbacks
5. Create FastAPI wrapper in `ui.py`
6. Test agent via direct HTTP calls

### Phase 2: Frontend UI
1. Create `/frontend/app/kanban/` directory structure
2. Build TaskCard component (display title, description, status)
3. Build KanbanColumn component (container for tasks)
4. Build KanbanBoard component (4 columns layout)
5. Implement main page.tsx with useCoAgent hook
6. Add basic styling with Tailwind CSS

### Phase 3: Integration
1. Update CopilotKit runtime to include KanbanAgent
2. Add `.env.local` variable for NEXT_PUBLIC_KANBAN_AGENT_URL
3. Connect frontend state to backend via useCoAgent
4. Test state synchronization

### Phase 4: Agent Interaction
1. Add CopilotSidebar to Kanban page
2. Configure agent instructions for natural language task management
3. Test commands like:
   - "Create a task to implement login feature"
   - "Move task X to in process"
   - "Show all tasks waiting for feedback"

### Phase 5: Enhanced Features
1. Drag-and-drop task movement between columns
2. Task editing via inline forms
3. Visual feedback for state updates
4. Task filtering and search
5. Generative UI for task creation confirmation

## File Structure

```
/backend/kanban/
  __init__.py
  agent.py          # ADK agent with tools and state management
  ui.py             # FastAPI wrapper

/frontend/app/kanban/
  page.tsx          # Main Kanban board page
  layout.tsx        # (Optional) Kanban-specific layout
  components/
    KanbanBoard.tsx
    KanbanColumn.tsx
    TaskCard.tsx

/frontend/.env.local
  NEXT_PUBLIC_KANBAN_AGENT_URL=http://localhost:8001
```

## Environment Setup

### Backend
```bash
cd backend
# Add to pyproject.toml if needed
uv run python -m kanban.ui  # Run on port 8001
```

### Frontend
```bash
cd frontend
# Update .env.local with NEXT_PUBLIC_KANBAN_AGENT_URL
npm run dev
```

## Testing Strategy

1. **Unit Tests**: Test individual agent tools
2. **Integration Tests**: Test AG-UI protocol communication
3. **E2E Tests**: Test full workflow from UI to agent
4. **Manual Testing**:
   - Create tasks via chat
   - Move tasks via drag-and-drop
   - Verify state persistence in agent
   - Test concurrent updates

## Key Considerations

1. **State Persistence**: Currently in-memory; could extend to database
2. **Task IDs**: Use UUID for unique identification
3. **Concurrent Updates**: Handle race conditions in state updates
4. **Error Handling**: Graceful failures when agent unavailable
5. **Loading States**: Show spinners during agent processing
6. **Optimistic Updates**: Update UI immediately, rollback on error
7. **Agent Instructions**: Clear prompts for task management operations

## Success Criteria

- [ ] Backend agent successfully manages task CRUD operations
- [ ] Frontend displays 4-column Kanban board
- [ ] State syncs bidirectionally between UI and agent
- [ ] Users can create/update/move/delete tasks via chat
- [ ] UI updates reflect agent state changes in real-time
- [ ] Drag-and-drop works for moving tasks between columns
- [ ] Application handles errors gracefully
