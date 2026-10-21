"""Local teaching CLI; DEMO_USER_ID is synthetic and is not authentication."""

import argparse
import asyncio

from google.adk import Runner
from google.genai import types

from bank_review.agent import root_agent
from bank_review.sessions import (
    APP_NAME, DEMO_USER_ID, build_session_service, close_session_service,
)


async def run(prompt: str, session_id: str | None) -> None:
    service = build_session_service()
    try:
        if session_id:
            session = await service.get_session(
                app_name=APP_NAME, user_id=DEMO_USER_ID, session_id=session_id
            )
            if session is None:
                raise ValueError("Session not found; refusing to create a replacement.")
        else:
            session = await service.create_session(app_name=APP_NAME, user_id=DEMO_USER_ID)
        print(f"Session ID: {session.id}")
        async with Runner(
            agent=root_agent, app_name=APP_NAME, session_service=service
        ) as runner:
            message = types.Content(role="user", parts=[types.Part(text=prompt)])
            async for event in runner.run_async(
                user_id=DEMO_USER_ID, session_id=session.id, new_message=message
            ):
                if event.is_final_response() and event.content:
                    for part in event.content.parts or []:
                        if part.text:
                            print(part.text)
    finally:
        await close_session_service(service)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--session-id")
    args = parser.parse_args()
    asyncio.run(run(args.prompt, args.session_id))
