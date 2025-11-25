import sys

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor

from coding.agent import coding_agent

def run(code: str, args: str) -> str:
    """
        Run python code in safe environment

        Input:
            code: python script
            args: command line parameters

        Output:
            str -> stdout
    """
    return '10'



root_agent = LlmAgent(
    model = 'gemini-2.5-flash',
    name = 'main',
    instruction='You are manager of SWE team. USe coder agent to create code and execute it. Rely only on subagent and tools, don`t guess results',
    sub_agents=[coding_agent],
    tools = [run]
)