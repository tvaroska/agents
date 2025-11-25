# Stock News Research Agent - Project Status

## Current Project Status

**Project Name**: Stock News Research Agent
**Framework**: Google Agent Development Kit (ADK)
**Status**: ✅ Functional MVP Complete
**Last Updated**: 2025-10-23

### What's Been Built

This is a **Stock News Research Agent** that automatically searches Google for recent stock news and generates comprehensive research reports saved as markdown artifacts.

#### Core Implementation

1. **Main Agent** (`research/agent.py`)
   - Uses Gemini 2.5 Flash model
   - Integrated with Google Search built-in tool
   - Configured as professional stock market research analyst
   - Generates structured markdown reports with:
     - Executive Summary
     - Key Developments
     - Detailed Article Summaries with Sources
     - Market Sentiment Analysis
     - Key Themes and Trends
     - Conclusions

2. **Example Script** (`example.py`)
   - Demonstrates programmatic agent usage
   - Shows async execution pattern
   - Includes session management
   - Error handling examples

3. **Documentation**
   - `README.md` - Comprehensive user guide with installation, usage, and troubleshooting
   - `QUICKSTART.md` - 5-minute quick start guide
   - `CLAUDE.md` - This file (ADK reference + project status)

#### Project Structure

```
news/
├── research/
│   ├── __init__.py           # Package exports
│   └── agent.py              # Main agent definition (stock_research_agent)
├── example.py                # Programmatic usage example
├── pyproject.toml            # Project dependencies (google-adk>=1.16.0)
├── .env.example              # Environment template (Vertex AI config)
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
└── CLAUDE.md                 # This file
```

### Configuration

**Environment Setup** (`.env.example`):
```bash
GOOGLE_CLOUD_PROJECT=btvaroska
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

**Dependencies**:
- `google-adk>=1.16.0` (managed via pyproject.toml/uv)

### How to Use

**Web UI** (Recommended):
```bash
adk web
```

**Terminal**:
```bash
adk run
```

**Programmatically**:
```bash
python example.py
```

**Example Queries**:
- "Research news for AAPL"
- "Find recent articles about GOOGL stock"
- "What's the latest news on NVDA?"

### Key Features Implemented

- ✅ Google Search integration via ADK built-in tool
- ✅ Automated multi-query research (24-hour news focus)
- ✅ Structured markdown report generation
- ✅ Professional analyst persona
- ✅ Source attribution and links
- ✅ Sentiment analysis
- ✅ Theme identification
- ✅ Artifact storage support
- ✅ Async execution support
- ✅ Error handling
- ✅ Comprehensive documentation

### Architecture Decisions

1. **Single Built-in Tool**: Uses only `google_search` built-in tool (ADK constraint: one built-in tool per agent)
2. **Model Choice**: Gemini 2.5 Flash for speed and built-in tool support
3. **Report Format**: Markdown for readability and artifact compatibility
4. **Time Window**: 24-hour news focus for relevance

### Git Status

Recent commits:
- `fd5a768` - wpi coding
- `e6e4e01` - feat: runner for agents
- `410c379` - ADK state
- `51fd853` - adk + ag ui

### Future Enhancement Ideas

Potential additions (not implemented yet):
- [ ] Multi-agent system with separate sentiment analyzer
- [ ] Historical price data integration
- [ ] Technical analysis component
- [ ] Industry comparison agent
- [ ] Email/Slack report delivery
- [ ] Scheduled automated research
- [ ] Custom report templates
- [ ] Multiple time window options
- [ ] Portfolio tracking
- [ ] Alert system for specific events

### Important Notes

- **Not Financial Advice**: This tool is for research purposes only
- **Built-in Tool Limitation**: Cannot combine google_search with custom tools
- **Search Quality**: Results depend on publicly available Google Search data
- **Rate Limits**: Subject to Google AI API rate limits

---

# Google Agent Development Kit (ADK) - Reference Documentation

## Framework Overview

This project uses Google's Agent Development Kit (ADK), an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with strong integration to Google Cloud services and Gemini models.

## What is ADK?

The Agent Development Kit (ADK) is a flexible and modular framework developed by Google that emphasizes:
- **Code-first development** - Define agent logic, workflows, and state management directly in Python
- **Fine-grained control** - Complete control over agent behavior, orchestration, and tool usage
- **Google Cloud integration** - Native support for Gemini models and Google Cloud services
- **Production-ready** - Built for deployment to local environments, Cloud Run, and Vertex AI Agent Engine

## Core Concepts

### 1. Agents

Agents are self-contained execution units designed to act autonomously to achieve specific goals. ADK provides three main types:

#### LLM Agents (`LlmAgent`, `Agent`)
- Use Large Language Models as their core engine
- Ideal for flexible, language-centric tasks
- Non-deterministic behavior
- Key parameters: `name`, `description`, `model`, `instruction`, `tools`

```python
from google.adk import Agent

agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    description="A helpful assistant",
    instruction="You are a helpful assistant that...",
    tools=[tool1, tool2]
)
```

#### Workflow Agents
Control execution flow in predefined, deterministic patterns:

- **SequentialAgent** - Executes sub-agents one after another
- **ParallelAgent** - Executes sub-agents concurrently
- **LoopAgent** - Repeatedly runs agents for a specified number of iterations

```python
from google.adk import SequentialAgent

workflow = SequentialAgent(
    name="pipeline",
    sub_agents=[agent1, agent2, agent3]
)
```

#### Custom Agents
- Extend `BaseAgent` directly for unique operational logic
- Provides ultimate flexibility for specialized integrations

### 2. Tools

Tools extend agent capabilities beyond conversation, allowing interaction with external APIs, searches, code execution, etc.

#### Tool Types:

**Function Tools**
```python
def get_weather(location: str) -> dict:
    """Get current weather for a location.

    Args:
        location: The city name or zip code

    Returns:
        Dictionary with temperature, conditions, etc.
    """
    return {"temperature": 72, "conditions": "sunny"}
```

**Built-in Tools**
- Google Search
- Code Execution
- Vertex AI Search

**Third-Party Tools**
- LangChain tools (via `LangchainTool`)
- CrewAI tools (via `CrewaiTool`)

**Google Cloud Tools**
- API Hub Tools (`ApiHubToolset`)
- Application Integration Tools
- Database Tools (MCP Toolbox)

**OpenAPI Integration**
```python
from google.adk import OpenAPIToolset

api_tools = OpenAPIToolset(
    name="my_api",
    spec_url="https://api.example.com/openapi.json"
)
```

**Model Context Protocol (MCP) Tools**
```python
from google.adk import MCPToolset

mcp_tools = MCPToolset(
    name="mcp_server",
    server_url="http://localhost:3000"
)
```

### 3. Session, State, and Memory

#### Session
Represents a single interaction between user and agent:
- Contains chronological sequence of Events
- Has unique `id`, `appName`, `userId`
- Managed by `SessionService`

#### State (`session.state`)
Dictionary for storing dynamic details during conversation:
- **Session-specific**: No prefix
- **User-specific**: `user:` prefix
- **App-wide**: `app:` prefix
- **Temporary**: `temp:` prefix (not persisted)

```python
# Access state in tool
def my_tool(tool_context: ToolContext) -> dict:
    user_name = tool_context.state.get('user:name')
    tool_context.state['result'] = "success"
    return {"status": "ok"}
```

#### Memory
Long-term knowledge store across sessions:
- `MemoryService` interface for managing knowledge
- `InMemoryMemoryService` for testing
- `VertexAiRagMemoryService` for production (Vertex AI RAG)

### 4. Multi-Agent Systems

Build complex applications with multiple specialized agents:

#### Common Patterns:

**Coordinator/Dispatcher Pattern**
```python
coordinator = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    sub_agents=[specialist1, specialist2, specialist3]
)
```

**Sequential Pipeline Pattern**
```python
pipeline = SequentialAgent(
    name="data_pipeline",
    sub_agents=[fetch_agent, transform_agent, save_agent]
)
```

**Parallel Fan-Out/Gather Pattern**
```python
parallel_search = ParallelAgent(
    name="multi_search",
    sub_agents=[web_search, db_search, doc_search]
)
```

**Iterative Refinement Pattern**
```python
refiner = LoopAgent(
    name="refiner",
    sub_agents=[generator, critic],
    max_iterations=3
)
```

### 5. Callbacks

Custom code that runs at specific points in agent execution:

```python
def before_tool_callback(ctx: CallbackContext, tool_name: str, args: dict):
    """Log tool usage"""
    print(f"Calling tool: {tool_name} with args: {args}")

agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    callbacks={
        'before_tool': before_tool_callback,
        'after_tool': after_tool_callback,
        'before_model': before_model_callback,
        'after_model': after_model_callback
    }
)
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install ADK
pip install google-adk
```

## Configuration

### Google AI Studio (for development)
```bash
# .env file
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### Vertex AI (for production)
```bash
# .env file
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

## Running Agents Locally

```bash
# Interactive Dev UI in browser
adk web

# Terminal interaction
adk run

# Local FastAPI server
adk api_server
```

## Project Structure

```
project/
├── .env                    # Environment configuration
├── agent.py               # Main agent definition
├── __init__.py
├── tools/                 # Custom tools
│   ├── __init__.py
│   └── custom_tools.py
└── workflows/             # Workflow agents
    ├── __init__.py
    └── pipelines.py
```

## Deployment Options

1. **Local Development** - Use `adk web` or `adk run`
2. **Cloud Run** - Deploy as containerized service
3. **Vertex AI Agent Engine** - Scalable managed deployment
4. **GKE** - Kubernetes deployment

## Evaluation

ADK includes built-in evaluation tools:

```python
# Create evaluation dataset
test_cases = [
    {
        "input": "What's the weather?",
        "expected_tools": ["get_weather"],
        "expected_response_contains": ["temperature"]
    }
]

# Run evaluation locally
results = evaluate_agent(agent, test_cases)
```

## Key Features

- **Rich Tool Ecosystem** - Built-in, custom, third-party, Google Cloud, OpenAPI, MCP tools
- **Flexible Orchestration** - Workflow agents + LLM-driven routing
- **Streaming Support** - Real-time text and audio (Gemini Live API)
- **State Management** - Session state, long-term memory, artifacts
- **Authentication** - Built-in support for API keys, OAuth 2.0, service accounts
- **Callbacks** - Hooks for logging, validation, guardrails, caching
- **Model Support** - Optimized for Gemini, extensible to other LLMs
- **Interoperability** - Integrate LangChain and CrewAI tools

## Best Practices

### Tool Design
1. Use descriptive function names (verb-noun pattern)
2. Return dictionaries with clear keys
3. Write detailed docstrings (LLM uses these!)
4. Keep tools focused on single tasks
5. Use JSON-serializable types

### State Management
1. Use appropriate state scopes (session, user, app, temp)
2. Update state via Events for proper persistence
3. Use `output_key` for automatic state updates from agent responses

### Multi-Agent Systems
1. Give agents distinct, clear descriptions
2. Use workflow agents for predictable flows
3. Use LLM-driven delegation for dynamic routing
4. Share data via session state or explicit tool calls

### Security
1. Never hardcode credentials
2. Use environment variables or secret managers
3. Implement proper authentication for tools
4. Use callbacks for guardrails and validation

## Resources

- **Documentation**: https://github.com/google/adk-docs
- **GitHub**: https://github.com/google/genai-adk (check for correct repo)
- **Gemini Models**: https://ai.google.dev/
- **Vertex AI**: https://cloud.google.com/vertex-ai

## Common Commands

```bash
# Install ADK
pip install google-adk

# Run agent in Dev UI
adk web

# Run agent in terminal
adk run

# Start API server
adk api_server

# Set SSL cert for streaming (wss://)
export SSL_CERT_FILE=$(python -m certifi)
```

## Example Agent

```python
from google.adk import Agent
from typing import Dict

def get_current_time() -> Dict[str, str]:
    """Get the current time.

    Returns:
        Dictionary with current time information
    """
    from datetime import datetime
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d")
    }

my_agent = Agent(
    name="time_agent",
    model="gemini-2.0-flash",
    description="An agent that can tell you the current time",
    instruction="You are a helpful assistant that provides time information.",
    tools=[get_current_time]
)
```

---

*This document is based on the official Google ADK documentation and provides a quick reference for Python development with ADK.*
