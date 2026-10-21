"""A one-turn CLI; new session each run, persistent preference state."""
import argparse
import asyncio
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.genai import types
from bank_case.agent import build_agent
from bank_case.preferences import save_preference
from bank_case.services import APP_NAME, DEMO_USER, memory_service, session_service


async def main(prompt, review_format):
    sessions = session_service()
    memory = memory_service()
    try:
        session = await sessions.create_session(app_name=APP_NAME, user_id=DEMO_USER)
        if review_format:
            await save_preference(sessions, memory, session, review_format)
        async with Runner(agent=build_agent(), app_name=APP_NAME,
                          session_service=sessions, memory_service=memory) as runner:
            async with asyncio.timeout(60):
                async for event in runner.run_async(
                    user_id=DEMO_USER, session_id=session.id,
                    new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                    run_config=RunConfig(max_llm_calls=4),
                ):
                    if event.is_final_response() and event.content:
                        print("".join(part.text or "" for part in event.content.parts or []))
    finally:
        await sessions.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--remember-format", choices=["concise", "detailed"])
    args = parser.parse_args()
    asyncio.run(main(args.prompt, args.remember_format))
