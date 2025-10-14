from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from google.genai import types

async def coding_after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    """Save generated code to artifacts after model response."""
    if llm_response.content and llm_response.content.parts:
        # Get the code from the response - check if it's text
        for part in llm_response.content.parts:
            code_text = None
            if part.text:
                code_text = part.text

            if part.function_call:
                code_text = llm_response.content.parts[0].function_call.args['code']

            if code_text:
                # Create an artifact Part with proper MIME type
                code_artifact = types.Part.from_bytes(
                    data=code_text.encode('utf-8'),
                    mime_type="text/x-python"
                )

                # Save to artifact with a descriptive filename
                version = await callback_context.save_artifact(
                    filename="generated_code.py",
                    artifact=code_artifact
                )
                print(f"✓ Code saved to artifact 'generated_code.py' (version {version})")

                # Replace the response with a simple message

    new_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text="Code is in your artifacts now")]
        )
    )
    return new_response

code_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="coding_agent",
    instruction="You are a coding agent, create a python script. If it needs some parameters create command line parameters for the script. IMPORTANT: Only generate the code. Do not attempt to run, execute, or test the code. Just provide the code and stop.",
    after_model_callback=coding_after_model_callback,
)

root_agent = LlmAgent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    instruction="You are a helpfull assistant",
    sub_agents=[code_agent],
)
