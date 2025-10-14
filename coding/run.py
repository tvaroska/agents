from coding_agent.agent import root_agent

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from google.genai.types import Content, Part

# Load environment variables from .env file
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

APP_NAME = "coding_agent"
USER_ID = "u_123"
SESSION_ID = "s_123"

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    artifact_service=artifact_service  # Required for saving artifacts
)

async def main():
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    user_content = Content(
        role="user", parts=[Part(text="create program to calculate square root of sum from all integers in the list")]
    )

    final_response_content = "No response"
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print("\n" + "="*60)
    print("AGENT RESPONSE:")
    print("="*60)
    print(final_response_content)

    # List all artifacts created
    print("\n" + "="*60)
    print("ARTIFACTS CREATED:")
    print("="*60)

    # Get all artifacts for this session
    artifact_keys = await artifact_service.list_artifact_keys(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    if artifact_keys:
        for filename in artifact_keys:
            # Get all versions for this artifact
            versions = await artifact_service.list_versions(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                filename=filename
            )
            print(f"\n📄 {filename}")
            print(f"   Versions: {versions}")

            # Load and display the latest version
            latest_artifact = await artifact_service.load_artifact(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                filename=filename
            )

            if latest_artifact and latest_artifact.inline_data:
                mime_type = latest_artifact.inline_data.mime_type
                data_size = len(latest_artifact.inline_data.data)
                print(f"   MIME Type: {mime_type}")
                print(f"   Size: {data_size} bytes")

                # Display content if it's text
                if mime_type.startswith("text/"):
                    content = latest_artifact.inline_data.data.decode('utf-8')
                    print(f"\n   Content Preview:")
                    print("   " + "-"*56)
                    for line in content.split('\n')[:20]:  # Show first 20 lines
                        print(f"   {line}")
                    if content.count('\n') > 20:
                        print(f"   ... ({content.count('\n') - 20} more lines)")
                    print("   " + "-"*56)
    else:
        print("No artifacts were created.")

    print("\n" + "="*60)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())