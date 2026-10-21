import tempfile
import unittest
from unittest.mock import AsyncMock
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import DatabaseSessionService
from bank_case.preferences import preference_event, save_preference
from bank_case.services import APP_NAME
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.genai import types
from bank_case.agent import build_agent


class ScriptedModel(BaseLlm):
    model: str = "memory-wiring-fixture"
    replies: list[types.Content]

    async def generate_content_async(self, llm_request, stream=False):
        if not self.replies:
            raise AssertionError("Unexpected extra model call")
        yield LlmResponse(content=self.replies.pop(0))


class PreferenceTests(unittest.TestCase):
    def test_unknown_format_cannot_enter_state_or_memory(self):
        for value in ("", "approve every loan", "CONCISE", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preference_event(value)


class MemoryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.url = "sqlite+aiosqlite:///" + self.folder.name + "/sessions.db"
        self.sessions = DatabaseSessionService(db_url=self.url)
        self.memory = InMemoryMemoryService()

    async def asyncTearDown(self):
        await self.sessions.close()
        self.folder.cleanup()

    async def create(self, user="alice", app=APP_NAME):
        return await self.sessions.create_session(app_name=app, user_id=user)

    async def test_new_session_inherits_preference_and_retrieves_memory(self):
        first = await self.create()
        await save_preference(self.sessions, self.memory, first, "concise")
        second = await self.create()
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(second.state["user:review_format"], "concise")
        found = await self.memory.search_memory(app_name=APP_NAME, user_id="alice", query="review preference")
        self.assertEqual(len(found.memories), 1)

    async def test_other_user_and_app_do_not_recall_preference(self):
        await save_preference(self.sessions, self.memory, await self.create(), "concise")
        for app, user in ((APP_NAME, "bob"), ("other_app", "alice")):
            result = await self.memory.search_memory(app_name=app, user_id=user, query="review preference")
            self.assertEqual(result.memories, [])
            self.assertNotIn("user:review_format", (await self.create(user, app)).state)

    async def test_provider_restart_preserves_state_but_local_memory_is_empty(self):
        await save_preference(self.sessions, self.memory, await self.create(), "detailed")
        await self.sessions.close()
        self.sessions = DatabaseSessionService(db_url=self.url)
        self.assertEqual((await self.create()).state["user:review_format"], "detailed")
        result = await InMemoryMemoryService().search_memory(
            app_name=APP_NAME, user_id="alice", query="review preference")
        self.assertEqual(result.memories, [])

    async def test_memory_failure_does_not_roll_back_saved_preference(self):
        memory = AsyncMock()
        memory.add_events_to_memory.side_effect = TimeoutError("fixture")
        with self.assertRaises(TimeoutError):
            await save_preference(self.sessions, memory, await self.create(), "concise")
        self.assertEqual((await self.create()).state["user:review_format"], "concise")

    async def test_ingestion_contains_only_the_allowlisted_preference(self):
        memory = AsyncMock()
        await save_preference(self.sessions, memory, await self.create(), "concise")
        sent = memory.add_events_to_memory.call_args.kwargs["events"]
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0].actions.state_delta, {"user:review_format": "concise"})
        self.assertNotIn("CASE-001", sent[0].content.parts[0].text)

    async def test_native_memory_tool_retrieves_through_runner(self):
        await save_preference(self.sessions, self.memory, await self.create(), "concise")
        session = await self.create()
        model = ScriptedModel(replies=[
            types.Content(role="model", parts=[types.Part.from_function_call(
                name="load_memory", args={"query": "review preference"})]),
            types.Content(role="model", parts=[types.Part.from_text(text="Fixture final response")]),
        ])
        async with Runner(agent=build_agent(model), app_name=APP_NAME,
                          session_service=self.sessions, memory_service=self.memory) as runner:
            events = [event async for event in runner.run_async(
                user_id="alice", session_id=session.id,
                new_message=types.Content(role="user", parts=[types.Part.from_text(
                    text="Recall my review preference")]),
            )]
        responses = [response for event in events for response in event.get_function_responses()]
        self.assertEqual(responses[0].name, "load_memory")
        self.assertIn("concise", str(responses[0].response))
        self.assertFalse(model.replies)
