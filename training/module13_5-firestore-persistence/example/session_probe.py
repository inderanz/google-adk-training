"""Prove ADK persistence in separate processes without Gemini or Firestore."""

import argparse
import asyncio
import json
from uuid import uuid4

from google.adk.events import Event, EventActions
from google.genai import types

from bank_review.sessions import (
    APP_NAME, DEMO_USER_ID, build_session_service, close_session_service,
)


async def run(action: str, session_id: str | None) -> None:
    service = build_session_service()
    try:
        if action == "write":
            session = await service.create_session(
                app_name=APP_NAME, user_id=DEMO_USER_ID,
                state={"last_case_id": "CASE-001"},
            )
            # One invocation can produce several distinct events.
            invocation_id = str(uuid4())
            for step in ("opened", "paused"):
                event = Event(
                    author="checkpoint_demo",
                    invocation_id=invocation_id,
                    content=types.Content(
                        role="model", parts=[types.Part(text=f"Review {step}.")]
                    ),
                    actions=EventActions(state_delta={"review_step": step}),
                )
                await service.append_event(session=session, event=event)
        else:
            if not session_id:
                raise ValueError("read requires --session-id from the write output.")
            session = await service.get_session(
                app_name=APP_NAME, user_id=DEMO_USER_ID, session_id=session_id
            )
            if session is None:
                raise ValueError("Session not found; check identity, backend and ID.")
        print(json.dumps({
            "session_id": session.id,
            "state": session.state,
            "events": [
                {"id": event.id, "invocation_id": event.invocation_id}
                for event in session.events
            ],
        }, indent=2))
    finally:
        await close_session_service(service)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("write", "read"))
    parser.add_argument("--session-id")
    args = parser.parse_args()
    asyncio.run(run(args.action, args.session_id))
