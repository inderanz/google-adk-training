"""Offline contract tests: real ADK/SQLite; mocked Firestore network calls."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from google.adk import Agent, Runner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.models.llm_request import LlmRequest
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
from google.api_core.exceptions import Forbidden

from bank_review import repository, sessions, tools

EXAMPLE = Path(__file__).resolve().parents[1]


def record():
    return {
        "assigned_analyst_id": "analyst-demo",
        "borrower_name": "Acme (fictional)",
        "documents": {"financial_statements": False, "ownership_register": False},
        "version": 1,
        "private_note": "must not reach the model",
    }


class CaseValidationTests(unittest.TestCase):
    def test_only_approved_fields_are_returned(self):
        result = repository.summarize_case(record(), "CASE-001", "analyst-demo")
        self.assertEqual(result["status"], "ok")
        self.assertNotIn("private_note", result)
        self.assertNotIn("assigned_analyst_id", result)

    def test_missing_and_unauthorized_look_the_same(self):
        missing = repository.summarize_case(None, "CASE-001", "analyst-demo")
        denied = repository.summarize_case(record(), "CASE-001", "another-analyst")
        self.assertEqual(missing, denied)
        self.assertNotIn("borrower_name", denied)

    def test_bad_fields_are_rejected(self):
        for field, value in (("version", True), ("version", 0), ("borrower_name", ""),
                             ("borrower_name", "a" * 201), ("documents", None)):
            data = record()
            data[field] = value
            self.assertEqual(
                repository.summarize_case(data, "CASE-001", "analyst-demo")["status"],
                "invalid_record",
            )

    def test_checklist_requires_real_booleans(self):
        data = record()
        data["documents"]["financial_statements"] = "yes"
        self.assertEqual(
            repository.summarize_case(data, "CASE-001", "analyst-demo")["status"],
            "invalid_record",
        )


class TransactionTests(unittest.IsolatedAsyncioTestCase):
    async def apply(self, data, user="analyst-demo", version=1):
        self.transaction = MagicMock()
        self.reference = MagicMock()
        self.reference.get = AsyncMock(return_value=MagicMock(to_dict=lambda: data))
        return await repository.mark_in_transaction(
            self.transaction, self.reference, "CASE-001", user,
            "financial_statements", version,
        )

    async def test_success_updates_flag_version_and_timestamp(self):
        original = record()
        result = await self.apply(original)
        self.assertEqual(result["version"], 2)
        self.assertTrue(result["documents"]["financial_statements"])
        self.assertFalse(original["documents"]["financial_statements"])
        changes = self.transaction.update.call_args.args[1]
        self.assertEqual(changes["version"], 2)
        self.assertIs(changes["updated_at"], repository.firestore.SERVER_TIMESTAMP)
        self.reference.get.assert_awaited_once_with(
            transaction=self.transaction, timeout=10, retry=None
        )

    async def test_stale_version_does_not_write(self):
        result = await self.apply(record(), version=99)
        self.assertEqual(result["status"], "conflict")
        self.transaction.update.assert_not_called()

    async def test_repeat_is_noop_even_with_old_version(self):
        data = record()
        data["documents"]["financial_statements"] = True
        data["version"] = 2
        result = await self.apply(data, version=1)
        self.assertEqual(result["status"], "already_received")
        self.assertEqual(result["version"], 2)
        self.transaction.update.assert_not_called()

    async def test_unauthorized_update_does_not_write(self):
        result = await self.apply(record(), user="intruder")
        self.assertEqual(result["status"], "not_found")
        self.transaction.update.assert_not_called()

    async def test_missing_or_invalid_case_does_not_write(self):
        for data, status in ((None, "not_found"), ({**record(), "version": -1}, "invalid_record")):
            self.assertEqual((await self.apply(data))["status"], status)
            self.transaction.update.assert_not_called()

    async def test_wrapper_uses_google_transaction_decorator(self):
        commit = AsyncMock(return_value={"status": "ok"})
        with patch.object(repository, "get_client") as factory:
            with patch.object(repository.firestore, "async_transactional", return_value=commit) as decorate:
                result = await repository.mark_received("CASE-001", "analyst-demo", "financial_statements", 1)
                decorate.assert_called_once_with(repository.mark_in_transaction)
                factory.return_value.transaction.assert_called_once_with(max_attempts=3)
                commit.assert_awaited_once()
                self.assertEqual(result["status"], "ok")

    async def test_read_uses_fixed_collection_and_bounded_call(self):
        reference = MagicMock()
        reference.get = AsyncMock(return_value=MagicMock(to_dict=record))
        with patch.object(repository, "get_client") as factory:
            factory.return_value.collection.return_value.document.return_value = reference
            result = await repository.read_case("CASE-001", "analyst-demo")
            factory.return_value.collection.assert_called_once_with("review_cases")
            reference.get.assert_awaited_once_with(timeout=10, retry=None)
            self.assertEqual(result["status"], "ok")


class ToolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        service = InMemorySessionService()
        session = await service.create_session(app_name="test", user_id="analyst-demo")
        self.context = ToolContext(invocation_context=InvocationContext(
            invocation_id="turn-1", agent=Agent(name="test", model="unused"),
            session=session, session_service=service,
        ))

    async def test_bad_ids_never_read(self):
        for value in ("", "../CASE-001", "CASE-1", None):
            with patch.object(repository, "read_case", new_callable=AsyncMock) as read:
                result = await tools.get_review_case(value, self.context)
                self.assertEqual(result["status"], "invalid_input")
                read.assert_not_awaited()

    async def test_identity_comes_from_context_and_state_is_only_hint(self):
        result = repository.summarize_case(record(), "CASE-001", "analyst-demo")
        with patch.object(repository, "read_case", new_callable=AsyncMock, return_value=result) as read:
            await tools.get_review_case("CASE-001", self.context)
            read.assert_awaited_once_with("CASE-001", "analyst-demo")
        self.assertEqual(self.context.actions.state_delta, {"last_case_id": "CASE-001"})

    async def test_invalid_update_arguments_never_write(self):
        for name, version in (("arbitrary.field", 1), ("financial_statements", True),
                              ("financial_statements", -1), ("financial_statements", "1")):
            with patch.object(repository, "mark_received", new_callable=AsyncMock) as write:
                result = await tools.mark_document_received("CASE-001", name, version, self.context)
                self.assertEqual(result["status"], "invalid_input")
                write.assert_not_awaited()

    async def test_write_passes_trusted_identity(self):
        with patch.object(repository, "mark_received", new_callable=AsyncMock, return_value={"status": "ok"}) as write:
            await tools.mark_document_received("CASE-001", "financial_statements", 1, self.context)
            write.assert_awaited_once_with("CASE-001", "analyst-demo", "financial_statements", 1)

    async def test_failed_operations_do_not_update_hint(self):
        with patch.object(repository, "mark_received", new_callable=AsyncMock, return_value={"status": "conflict"}):
            await tools.mark_document_received("CASE-001", "financial_statements", 1, self.context)
        self.assertEqual(self.context.actions.state_delta, {})

    async def test_service_error_does_not_leak_details(self):
        with patch.object(repository, "read_case", new_callable=AsyncMock, side_effect=Forbidden("SECRET")):
            with self.assertLogs(tools.logger) as logs:
                result = await tools.get_review_case("CASE-001", self.context)
        self.assertEqual(result["status"], "unavailable")
        self.assertNotIn("SECRET", json.dumps(result) + str(logs.output))

    async def test_adk_schema_hides_context_and_identity(self):
        for function, expected in (
            (tools.get_review_case, {"case_id"}),
            (tools.mark_document_received, {"case_id", "document_name", "expected_version"}),
        ):
            request = LlmRequest()
            await FunctionTool(function).process_llm_request(
                tool_context=self.context, llm_request=request
            )
            declaration = request.config.tools[0].function_declarations[0]
            schema = declaration.parameters_json_schema
            fields = schema["properties"] if schema else declaration.parameters.properties
            self.assertEqual(set(fields), expected)


class SessionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.service = DatabaseSessionService(
            db_url=f"sqlite+aiosqlite:///{self.directory.name}/sessions.db"
        )

    async def asyncTearDown(self):
        await self.service.close()
        self.directory.cleanup()

    async def test_event_ids_are_distinct_within_one_invocation(self):
        session = await self.service.create_session(app_name="test", user_id="one")
        for value in ("opened", "paused"):
            await self.service.append_event(session, Event(
                author="test", invocation_id="same-turn",
                actions=EventActions(state_delta={"step": value}),
            ))
        restored = await self.service.get_session(app_name="test", user_id="one", session_id=session.id)
        self.assertEqual(restored.state["step"], "paused")
        self.assertEqual(len(restored.events), 2)
        self.assertNotEqual(restored.events[0].id, restored.events[1].id)
        self.assertEqual(restored.events[0].invocation_id, restored.events[1].invocation_id)

    async def test_other_user_cannot_load_session(self):
        session = await self.service.create_session(app_name="test", user_id="one")
        other = await self.service.get_session(app_name="test", user_id="two", session_id=session.id)
        self.assertIsNone(other)

    async def test_direct_dictionary_edit_is_not_persistence(self):
        session = await self.service.create_session(app_name="test", user_id="one")
        session.state["unsaved"] = True
        restored = await self.service.get_session(app_name="test", user_id="one", session_id=session.id)
        self.assertNotIn("unsaved", restored.state)

    async def test_state_scopes_are_not_all_session_local(self):
        one = await self.service.create_session(app_name="test", user_id="one")
        await self.service.append_event(one, Event(author="test", invocation_id="scope", actions=EventActions(
            state_delta={"local": 1, "user:preference": "brief", "app:policy": "v1", "temp:scratch": "discard"}
        )))
        two = await self.service.create_session(app_name="test", user_id="one")
        other = await self.service.create_session(app_name="test", user_id="two")
        self.assertEqual(two.state["user:preference"], "brief")
        self.assertNotIn("local", two.state)
        self.assertNotIn("user:preference", other.state)
        self.assertEqual(other.state["app:policy"], "v1")
        restored = await self.service.get_session(app_name="test", user_id="one", session_id=one.id)
        self.assertNotIn("temp:scratch", restored.state)

    async def test_runner_persists_tool_context_delta(self):
        class ScriptedModel(BaseLlm):
            async def generate_content_async(self, llm_request, stream=False):
                parts = llm_request.contents[-1].parts or []
                if any(part.function_response for part in parts):
                    output = types.Part(text="Scripted test response.")
                else:
                    output = types.Part(function_call=types.FunctionCall(
                        name="get_review_case", args={"case_id": "CASE-001"}
                    ))
                yield LlmResponse(content=types.Content(role="model", parts=[output]))

        agent = Agent(name="test", model=ScriptedModel(model="offline-script"),
                      tools=[FunctionTool(tools.get_review_case)])
        session = await self.service.create_session(app_name="test", user_id="analyst-demo")
        result = repository.summarize_case(record(), "CASE-001", "analyst-demo")
        with patch.object(repository, "read_case", new_callable=AsyncMock, return_value=result):
            async with Runner(agent=agent, app_name="test", session_service=self.service) as runner:
                async for _ in runner.run_async(
                    user_id="analyst-demo", session_id=session.id,
                    new_message=types.Content(role="user", parts=[types.Part(text="Read CASE-001")]),
                ):
                    pass
        restored = await self.service.get_session(
            app_name="test", user_id="analyst-demo", session_id=session.id
        )
        self.assertEqual(restored.state["last_case_id"], "CASE-001")
        self.assertGreaterEqual(len(restored.events), 3)


class ProcessAndConfigurationTests(unittest.TestCase):
    def test_real_process_restart_preserves_events_and_state(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, "SESSION_BACKEND": "sqlite",
                   "SESSION_DB_URL": f"sqlite+aiosqlite:///{directory}/sessions.db"}
            def command(*args):
                result = subprocess.run(
                    [sys.executable, "session_probe.py", *args],
                    cwd=EXAMPLE, env=env, check=True, capture_output=True, text=True,
                )
                return json.loads(result.stdout)
            first = command("write")
            second = command("read", "--session-id", first["session_id"])
            self.assertEqual(first, second)
            self.assertEqual(len(second["events"]), 2)

    def test_unknown_backend_fails_without_fallback(self):
        with patch.dict(os.environ, {"SESSION_BACKEND": "typo"}):
            with self.assertRaises(ValueError):
                sessions.build_session_service()

    def test_managed_service_uses_separate_session_location(self):
        with patch.dict(os.environ, {
            "SESSION_BACKEND": "managed", "GOOGLE_CLOUD_PROJECT": "demo",
            "GOOGLE_CLOUD_AGENT_ENGINE_LOCATION": "session-region",
            "GOOGLE_CLOUD_LOCATION": "model-region",
            "GOOGLE_CLOUD_AGENT_ENGINE_ID": "123",
        }):
            with patch("google.adk.sessions.VertexAiSessionService") as provider:
                sessions.build_session_service()
                provider.assert_called_once_with(
                    project="demo", location="session-region", agent_engine_id="123"
                )


if __name__ == "__main__":
    unittest.main()
