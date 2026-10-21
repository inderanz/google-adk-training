"""Run locally against real Gemini, managed Sessions and GCS services.

The agent executes in this Python process. check_deployed.py instead invokes
an agent already hosted on Agent Runtime. Both use synthetic bank records.
"""
import argparse
import asyncio
import json
import logging
import os
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.artifacts import GcsArtifactService
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types
from bank_review.agent import app


async def run(prompt: str, session_id: str | None):
    sessions = VertexAiSessionService(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["AGENT_RUNTIME_LOCATION"],
        agent_engine_id=os.environ["AGENT_ENGINE_ID"],
    )
    artifacts = GcsArtifactService(bucket_name=os.environ["ARTIFACT_BUCKET"])
    user_id = "training-analyst"  # Synthetic scope identifier, not authentication.
    if session_id is None:
        session = await sessions.create_session(app_name=app.name, user_id=user_id)
        session_id = session.id
    print(json.dumps({"session_id": session_id, "user_id": user_id}))
    async with Runner(app=app, session_service=sessions, artifact_service=artifacts) as runner:
        async with asyncio.timeout(90):
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                run_config=RunConfig(max_llm_calls=8, streaming_mode=StreamingMode.NONE),
            ):
                # This diagnostic output is for synthetic lab data only.
                print(event.model_dump_json(exclude_none=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="Prepare CASE-001 for human review.")
    parser.add_argument("--otel-to-cloud", action="store_true", help="Export native ADK traces using ADC")
    parser.add_argument("--session-id", help="Reuse a managed session created by this lab user")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.otel_to_cloud:
        from google.adk.telemetry.google_cloud import get_gcp_exporters
        from google.adk.telemetry.setup import maybe_set_otel_providers
        hooks = get_gcp_exporters(enable_cloud_tracing=True)
        maybe_set_otel_providers(otel_hooks_to_setup=[hooks])
    asyncio.run(run(args.prompt, args.session_id))
