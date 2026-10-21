"""Scripted transport fixtures exercise real ADK wiring, not Gemini quality."""
from google.adk.artifacts import InMemoryArtifactService
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


class ScriptedModel(BaseLlm):
    model: str = "scripted-contract-test"
    replies: list[types.Content]

    async def generate_content_async(self, llm_request, stream=False):
        if not self.replies:
            raise AssertionError("Unexpected model call")
        yield LlmResponse(content=self.replies.pop(0))


def text(value):
    return types.Content(role="model", parts=[types.Part.from_text(text=value)])


def call(name, **args):
    return types.Content(role="model", parts=[types.Part.from_function_call(name=name, args=args)])


async def invoke(app, prompt="Prepare CASE-001", user="analyst-a", artifacts=None):
    store = artifacts or InMemoryArtifactService()
    async with Runner(app=app, session_service=InMemorySessionService(), artifact_service=store) as runner:
        session = await runner.session_service.create_session(app_name=app.name, user_id=user)
        events = [event async for event in runner.run_async(
            user_id=user, session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))]
        saved = await runner.session_service.get_session(app_name=app.name, user_id=user, session_id=session.id)
    return events, saved, store


def results(events):
    return [response.response for event in events for response in event.get_function_responses()]
