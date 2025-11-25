import sys
import uvicorn

import vertexai
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.genai import types

from coding.agent import coding_agent
from coding.server import a2a_agent

# Run locally
# try:
#     port = int(sys.argv[1])
# except:
#     port = 8090

# a2a_app = to_a2a(coding_agent, port=port)

# uvicorn.run(a2a_app, host='localhost', port=port)

# Deploy to Agent Engine
LOCATION = 'us-central1'
BUCKET_URI = f"gs://btvaroska_tmp"
client = vertexai.Client(
    project = 'conten001',
    location = LOCATION,
    http_options=types.HttpOptions(
        api_version="v1beta1", base_url=f"https://{LOCATION}-aiplatform.googleapis.com/"
    ),
)

remote_a2a_agent = client.agent_engines.create(
    # The actual agent to deploy
    agent=a2a_agent,
    config={
        # Display name shown in the console
        "display_name": a2a_agent.agent_card.name,
        # Description for documentation
        "description": a2a_agent.agent_card.description,
        # Python dependencies needed in Agent Engine
        "requirements": [
            "google-cloud-aiplatform[agent_engines,adk]>=1.112.0",
            "a2a-sdk >= 0.3.4",
        ],
        # Http options
        "http_options": {
            "base_url": f"https://{LOCATION}-aiplatform.googleapis.com",
            "api_version": "v1beta1",
        },
        # Staging bucket
        "staging_bucket": BUCKET_URI,
    },
)
