from pydantic import BaseModel

from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from coding.prompt import CODING_PROMPT

class CoderOutput(BaseModel):
    code: str
    description: str

async def coding_after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    """Save generated code to artifacts after model response."""
    if llm_response.content and llm_response.content.parts:
        # Get the code from the response - check if it's text
        for part in llm_response.content.parts:
            data = None
            code = None
            if part.text:
                data = part.text
                code = CoderOutput.model_validate_json(data).code

            if part.function_call:
                code = part.function_call.args['code']

            if code:
                # Create an artifact Part with proper MIME type
                code_artifact = types.Part.from_bytes(
                    data=code.encode('utf-8'),
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
            parts=[types.Part(text=code)]
        )
    )
    return new_response


coding_agent = LlmAgent(
    model = 'gemini-2.5-pro',
    name = 'coder',
    description='Coding agent',
    instruction=CODING_PROMPT,
    output_schema=CoderOutput,
    after_model_callback=coding_after_model_callback
)

root_agent = coding_agent