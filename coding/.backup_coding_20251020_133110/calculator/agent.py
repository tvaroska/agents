from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.code_executors import BuiltInCodeExecutor

# TODO 1: Deploy to AgentEngine
# TODO 2: Test if we can do A2A (separate coder)


def add(a: float, b: float) -> float:
    """
    Calculate add of two numbers

    Args:
        a: int or float
        b: int or float

    Returns:
        int or float: a + b
    """
    return a + b

code = LlmAgent(
    name = 'coder',
    description = 'Coding agent to get results from description of the task and input parameters for the task',
    model = 'gemini-2.5-flash',
    instruction = 'You are a coding agent to resolve question. Create and run python code to get results for the request',
    code_executor=BuiltInCodeExecutor()
)

calculator = LlmAgent(
    name = 'calculator',
    description = 'Basic calculator agent',
    model = 'gemini-2.5-flash-lite',
    instruction = 'You are a calculator agent, answer any mathematical question and refuse to answer anything else. For mathematical question you can use code subagent to generate and execute python code',
    tools=[add, AgentTool(code)],
#    sub_agents=[code]
)

root_agent = calculator