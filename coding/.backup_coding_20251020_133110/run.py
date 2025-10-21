import json
import importlib
import argparse

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from google.genai.types import Content, Part

# from opentelemetry import trace
# from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
# from opentelemetry.sdk.trace import export
# from opentelemetry.sdk.trace import TracerProvider

from phoenix.otel import register


# Load environment variables from .env file
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

APP_NAME = "coding_agent"
USER_ID = "u_123"


session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

def setup_cloud_trace():
    """Setup Cloud Trace for OpenTelemetry."""
    # provider = TracerProvider()
    # processor = export.BatchSpanProcessor(
    #     CloudTraceSpanExporter(project_id=os.getenv('GOOGLE_CLOUD_PROJECT'))
    # )
    # provider.add_span_processor(processor)
    # trace.set_tracer_provider(provider)

    tracer_provider = register(
        endpoint='https://app.phoenix.arize.com/s/boris3659',
        project_name="jokes",  # Project name for organizing traces
        auto_instrument=True,  # Auto-instrument your app based on installed OI dependencies
    )

def load_agent(agent_name: str):
    """Dynamically import and return the agent.

    If agent_name contains a dot, treats it as module.attribute.
    If agent_name is just a module name, tries ADK defaults:
    1. module.root_agent
    2. module.agent.root_agent
    """
    if '.' in agent_name:
        # Explicit module.attribute format
        module_path, attr_name = agent_name.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    else:
        # Module name only - try ADK defaults
        try:
            # Try module.root_agent first
            module = importlib.import_module(agent_name)
            return getattr(module, 'root_agent')
        except (ImportError, AttributeError):
            # Try module.agent.root_agent as fallback
            module = importlib.import_module(f"{agent_name}.agent")
            return getattr(module, 'root_agent')

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run ADK agent with JSON configuration')
    parser.add_argument('config_file', help='Path to JSON configuration file')
    parser.add_argument('--cloud_trace', action='store_true',
                        help='Enable Cloud Trace for OpenTelemetry')
    parser.add_argument('--output', '-o', help='Path to save evaluation results in EvalSet format')
    args = parser.parse_args()

    # Setup Cloud Trace if requested
    if args.cloud_trace:
        setup_cloud_trace()
        print("Cloud Trace enabled")

    # Load JSON definition file
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    # Extract agent name and conversations
    agent_name = config['agent']
    conversations = config['conversations']  # List[List[str]]

    # Use agent name as app_name (fallback to default if not provided)
    app_name = agent_name if agent_name else APP_NAME

    # Load the agent dynamically
    agent = load_agent(agent_name)

    # Create runner with the loaded agent
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
        artifact_service=artifact_service
    )

    # Initialize eval_cases list to store results
    eval_cases = []

    # Process each conversation
    for conv_idx, conversation in enumerate(conversations):
        SESSION_ID = f"s_{conv_idx}"

        session = await session_service.get_session(
            app_name=app_name, user_id=USER_ID, session_id=SESSION_ID
        )
        if session is None:
            session = await session_service.create_session(
                app_name=app_name, user_id=USER_ID, session_id=SESSION_ID
            )

        print(f"\n{'='*60}")
        print(f"CONVERSATION {conv_idx + 1}:")
        print(f"{'='*60}")

        # Store conversation turns for this eval case
        conversation_turns = []

        # Process each message in the conversation
        for msg_idx, message in enumerate(conversation):
            print(f"\n[Message {msg_idx + 1}]: {message}")

            user_content = Content(
                role="user", parts=[Part(text=message)]
            )

            final_response_content = "No response"
            async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response_content = event.content.parts[0].text

            print(f"\n[Agent Response]:")
            print(final_response_content)

            # Record this turn in EvalSet format
            conversation_turns.append({
                "user_content": {
                    "parts": [{"text": message}]
                },
                "final_response": {
                    "parts": [{"text": final_response_content}]
                }
            })

        # Add this conversation as an eval case
        eval_cases.append({
            "eval_id": f"eval_{conv_idx}",
            "conversation": conversation_turns,
            "session_input": {
                "app_name": app_name
            }
        })

    # List all artifacts created across all conversations
    print("\n" + "="*60)
    print("ARTIFACTS CREATED:")
    print("="*60)

    for conv_idx in range(len(conversations)):
        SESSION_ID = f"s_{conv_idx}"

        # Get all artifacts for this session
        artifact_keys = await artifact_service.list_artifact_keys(
            app_name=app_name,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

        if artifact_keys:
            print(f"\nConversation {conv_idx + 1}:")
            for filename in artifact_keys:
                # Get all versions for this artifact
                versions = await artifact_service.list_versions(
                    app_name=app_name,
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    filename=filename
                )
                print(f"\n  {filename}")
                print(f"     Versions: {versions}")

                # Load and display the latest version
                latest_artifact = await artifact_service.load_artifact(
                    app_name=app_name,
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    filename=filename
                )

                if latest_artifact and latest_artifact.inline_data:
                    mime_type = latest_artifact.inline_data.mime_type
                    data_size = len(latest_artifact.inline_data.data)
                    print(f"     MIME Type: {mime_type}")
                    print(f"     Size: {data_size} bytes")

                    # Display content if it's text
                    if mime_type.startswith("text/"):
                        content = latest_artifact.inline_data.data.decode('utf-8')
                        print(f"\n     Content Preview:")
                        print("     " + "-"*52)
                        for line in content.split('\n')[:20]:  # Show first 20 lines
                            print(f"     {line}")
                        if content.count('\n') > 20:
                            print(f"     ... ({content.count('\n') - 20} more lines)")
                        print("     " + "-"*52)

    print("\n" + "="*60)

    # Save evaluation results if output file specified
    if args.output:
        eval_set = {
            "eval_set_id": f"eval_set_{app_name}",
            "name": f"Evaluation results for {agent_name}",
            "eval_cases": eval_cases
        }

        with open(args.output, 'w') as f:
            json.dump(eval_set, f, indent=2)

        print(f"\nEvaluation results saved to: {args.output}")
        print(f"Total eval cases: {len(eval_cases)}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())