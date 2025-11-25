from typing import NoReturn
import logging

from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

from a2a.types import AgentSkill, AgentCard, AgentCapabilities, Role, TextPart, TaskState, UnsupportedOperationError
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message
from a2a.utils.errors import ServerError

from google.genai.types import Content, Part

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

qna_agent = LlmAgent(
    # The LLM model to use
    model="gemini-2.5-flash",
    # Internal name for the agent (used in logging and sessions)
    name="qa_assistant",
    # Human-readable description
    description="I answer questions using web search.",
    # The system instruction that guides the agent's behavior
    # This is crucial for getting good results
    instruction="""You are a helpful Q&A assistant.
        When asked a question:
        1. Use Google Search to find current, accurate information
        2. Synthesize the search results into a clear answer
        3. Cite your sources when possible
        4. If you can't find a good answer, say so honestly

        Always aim for accuracy over speculation.""",
    # Tools available to the agent
    # The agent will automatically use these when needed
    tools=[google_search_tool.google_search],
)

# root_agent = qna_agent

# Define a skill - a specific capability your agent offers
# Agents can have multiple skills for different tasks
qna_agent_skill = AgentSkill(
    # Unique identifier for this skill
    id="web_qa",
    # Human-friendly name
    name="web_qa",
    # Detailed description helps clients understand when to use this skill
    description="Answer questions using current web search results",
    # Tags for categorization and discovery
    # These help in agent marketplaces or registries
    tags=["question-answering", "search", "research"],
    # Examples show clients what kinds of requests work well
    # This is especially helpful for LLM-based clients
    examples=[
        "What is the current weather in Tokyo?",
        "Who won the latest Nobel Prize in Physics?",
        "What are the symptoms of the flu?",
        "How do I make sourdough bread?",
    ],
    # Optional: specify input/output modes
    # Default is text, but could include images, files, etc.
    input_modes=["text/plain"],
    output_modes=["text/plain"],
)

# Use the helper function to create a complete Agent Card
qna_agent_card = AgentCard(
    capabilities=AgentCapabilities(),
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    description='I answer questions using web search.',
    name='qa_assistant',
    skills = [qna_agent_skill],
    url='http://localhost:8001',
    version='0.0.1'
)

class QnAAgentExecutor(AgentExecutor):
    """Agent Executor that bridges A2A protocol with our ADK agent.

    The executor handles:
    1. Protocol translation (A2A messages to/from agent format)
    2. Task lifecycle management (submitted -> working -> completed)
    3. Session management for multi-turn conversations
    4. Error handling and recovery
    """

    def __init__(self) -> None:
        """Initialize with lazy loading pattern."""
        self.agent = None
        self.runner = None

    def _init_agent(self) -> None:
        """Lazy initialization of agent resources."""
        if self.agent is None:
            # Create the actual agent
            self.agent = qna_agent

            # The Runner orchestrates the agent execution
            # It manages the LLM calls, tool execution, and state
            self.runner = Runner(
                app_name=self.agent.name,
                agent=self.agent,
                # In-memory services for simplicity
                # In production, you might use persistent storage
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Process a user query and return the answer.

        This method is called by the A2A protocol handler when:
        1. A new message arrives (message/send)
        2. A streaming request is made (message/stream)
        """
        # Initialize agent
        if self.agent is None:
            self._init_agent()

        # Extract the user's question from the protocol message
        query = context.get_user_input()

        # Create a TaskUpdater for managing task state
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        # Update task status through its lifecycle
        # submitted -> working -> completed/failed
        if not context.current_task:
            # New task - mark as submitted
            await updater.submit()

        # Mark task as working (processing)
        await updater.start_work()

        logging.info("Running search")

        try:
            # Get or create a session for this conversation
            session = await self._get_or_create_session(context.context_id)

            # Prepare the user message in ADK format
            content = Content(role=Role.user, parts=[Part(text=query)])

            # Run the agent asynchronously
            # This may involve multiple LLM calls and tool uses
            async for event in self.runner.run_async(
                session_id=session.id,
                user_id="user",  # In production, use actual user ID
                new_message=content,
            ):
                # The agent may produce multiple events
                # We're interested in the final response
                if event.is_final_response():
                    # Extract the answer text from the response
                    answer = self._extract_answer(event)

                    # Add the answer as an artifact
                    # Artifacts are the "outputs" or "results" of a task
                    # They're separate from status messages
                    await updater.add_artifact(
                        [TextPart(text=answer)],
                        name="answer",  # Name helps clients identify artifacts
                    )

                    await updater.add_artifact(
                        [TextPart(text=answer)],
                        name='code'
                    )

                    # Mark task as completed successfully
                    await updater.complete()
                    break

                    # For intermediate events, we could send status updates
                    # This is useful for long-running tasks
                    # Example:
                    # await updater.update_status(
                    #     TaskState.working,
                    #     message=new_agent_text_message("Searching the web...")
                    # )

        except Exception as e:
            # Errors should never pass silently (Zen of Python)
            # Always inform the client when something goes wrong
            await updater.update_status(
                TaskState.failed, message=new_agent_text_message(f"Error: {e!s}")
            )
            # Re-raise for proper error handling up the stack
            raise

    async def _get_or_create_session(self, context_id: str):
        """Get existing session or create new one."""
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id="user",
            session_id=context_id,
        )

        if not session:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id="user",
                session_id=context_id,
            )

        return session

    def _extract_answer(self, event) -> str:
        """Extract text answer from agent response."""
        parts = event.content.parts
        text_parts = [part.text for part in parts if part.text]

        # Join all text parts with space
        return " ".join(text_parts) if text_parts else "No answer found."

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> NoReturn:
        """Handle task cancellation requests.

        For long-running agents, this would:
        1. Stop any ongoing processing
        2. Clean up resources
        3. Update task state to 'cancelled'
        """
        # Inform client that cancellation isn't supported
        raise ServerError(error=UnsupportedOperationError())
    
