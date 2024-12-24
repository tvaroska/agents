from typing import Annotated, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    input: str
    messages: Annotated[list[AnyMessage], add_messages]

prompt = ChatPromptTemplate(
    messages = [
        ("system", "You are very unhelpfull assistant. Refuse to answer any question in rude tone"),
        ("user", "{question}")
    ]
)

llm = ChatVertexAI(model='gemini-1.5-flash-002')

def convert(state: State):
    messages = prompt.invoke({'question': state['input']})
    return {
        'messages': messages.messages
    }

def chat(state: State):
    messages = [llm.invoke(state['messages'])]
    return {
        'messages': messages
    }
    
def human(state: State):
    if len(state['messages']) > 3:
        return Command(
            # control flow
            goto=END
        )
    else:
        return {
            'messages': HumanMessage(state['input'])
        }


builder = StateGraph(state_schema=State)

builder.set_entry_point("convert")
builder.add_node("convert", convert)
builder.add_node("llm", chat)
builder.add_node("human", human)

builder.add_edge("convert", "llm")
builder.add_edge("llm", "human")
builder.add_edge("human", "llm")

graph = builder.compile()
