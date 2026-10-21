"""Run one synthetic request through the real ADK runtime."""
import asyncio
import json

from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types


async def run_once(agent, payload):
    # This identity is a fixture, never an authentication implementation.
    async with InMemoryRunner(app=App(name="bank_case", root_agent=agent)) as runner:
        session = await runner.session_service.create_session(
            app_name="bank_case", user_id="analyst-demo"
        )
        message = types.Content(
            role="user", parts=[types.Part.from_text(text=json.dumps(payload))]
        )
        events = []
        # The deadline bounds the invocation; it cannot undo external writes.
        async with asyncio.timeout(60):
            async for event in runner.run_async(
                user_id="analyst-demo", session_id=session.id,
                new_message=message, run_config=RunConfig(max_llm_calls=12),
            ):
                events.append(event)
        return events


def display(events):
    for event in events:
        if event.output is not None:
            print(json.dumps({"author": event.author, "output": event.output}))
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"{event.author}: {part.text}")
