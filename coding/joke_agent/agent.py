from typing import Optional

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content

from .prompt import ORCHESTRATOR_PROMPT

class Joke(BaseModel):
    """A model for a joke with setup and punchline."""
    setup: str = Field(description="The question or setup of the joke.")
    punchline: str = Field(description="The answer or punchline to the joke.")
    category: Optional[str] = Field(None, description="The category or topic of the joke.")
    rating: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="An optional rating for the joke, from 1 to 10."
    )

generator = LlmAgent(
    model="gemini-2.5-flash",
    name="generator",
    instruction="Invent new joke from user instruction.", # Update output key and present joke to the user as well.",
    output_schema=Joke,
    output_key='joke'
)

def add_to_list(callback_context: CallbackContext) -> Optional[Content]:

    if 'joke' in callback_context.state or callback_context.state['joke'] == "":
        if 'jokes' in callback_context.state or len(callback_context.state['jokes']) == 0:
            jokes = callback_context.state['jokes']
            jokes.append(callback_context.state['joke'])
            callback_context.state['jokes'] = jokes
        else:
            callback_context.state['jokes'] = [callback_context.state['joke']]
    else:
        callback_context.state['joke'] = ""
        callback_context.state['jokes'] = []
    return None

root_agent = LlmAgent(
    model = "gemini-2.5-flash",
    name = "joker",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[generator],
    after_agent_callback=add_to_list
)