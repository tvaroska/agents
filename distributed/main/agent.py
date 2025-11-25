from google.adk.agents import LlmAgent

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

search_agent = RemoteA2aAgent(
    name="qa_assistant",
    description=(
        "A helpful assistant agent that can answer questions."
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name = "main",
    description="Helpfull assistant",
    instruction="You are helpfull assistant. Use qa_asistant to search for answers. If user does not specify use this defaults: country - Canada, year 2020",
    sub_agents=[search_agent]
)