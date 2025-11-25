import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from search.agent import qna_agent, qna_agent_card, QnAAgentExecutor

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from vertexai.preview.reasoning_engines.templates.a2a import create_agent_card
from a2a.types import AgentSkill, AgentCard, AgentCapabilities

request_handler = DefaultRequestHandler(
        agent_executor=QnAAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

server = A2AStarletteApplication(
    agent_card=qna_agent_card,
    http_handler=request_handler,
)

# a2a_app = to_a2a(qna_agent, port=8001, agent_card=qna_agent_card)
# uvicorn.run(a2a_app, host='0.0.0.0', port=8001)

uvicorn.run(server.build(), host='0.0.0.0', port=8001)