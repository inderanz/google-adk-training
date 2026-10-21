"""Check the registered third-party tool through a real ADK Runner."""
from datetime import UTC, datetime
import os
import unittest
from unittest.mock import patch

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.integrations.langchain import LangchainTool
from google.genai import types

from corporate_research import tools
with patch.dict(os.environ, {"GEMINI_MODEL": "configured-for-contract-test"}):
    from corporate_research.agent import root_agent


class ScriptedModel(BaseLlm):
    # The test controls model replies; ADK still executes the actual adapter.
    model: str = "scripted-model"
    company_id: str

    async def generate_content_async(self, llm_request, stream=False):
        has_response = any(part.function_response for content in llm_request.contents
                           for part in content.parts or [])
        if has_response:
            part = types.Part.from_text(text="Fixture explanation; not a quality score.")
        else:
            part = types.Part.from_function_call(name="get_company_profile",
                                                 args={"company_id": self.company_id})
        yield LlmResponse(content=types.Content(role="model", parts=[part]))


class AdaptedAgentTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, company_id):
        self.assertIsInstance(root_agent.tools[0], LangchainTool)
        sessions = InMemorySessionService()
        session = await sessions.create_session(app_name="corporate_research", user_id="test-analyst")
        # Patch only the model transport. The actual configured tool remains registered.
        with patch.object(root_agent, "model", ScriptedModel(company_id=company_id)):
            async with Runner(app_name="corporate_research", agent=root_agent,
                              session_service=sessions) as runner:
                events = [event async for event in runner.run_async(
                    user_id="test-analyst", session_id=session.id,
                    new_message=types.Content(role="user", parts=[types.Part.from_text(text="Company profile")]))]
        return [response.response for event in events for response in event.get_function_responses()]

    async def test_adapted_agent_returns_record_source_and_date(self):
        record = {"company_id": "ACME-001", "company_name": "Acme Robotics (fictional)",
                  "summary": "Fictional training company.", "source_uri": "training-fixture:ACME-001",
                  "reviewed_on": datetime.now(UTC).date().isoformat()}
        with patch.object(tools, "fetch_profile", return_value=record) as fetch:
            responses = await self.invoke("ACME-001")
        fetch.assert_called_once_with("ACME-001")
        self.assertEqual(responses[0]["status"], "ok")
        self.assertEqual(responses[0]["source_uri"], record["source_uri"])
        self.assertEqual(responses[0]["reviewed_on"], record["reviewed_on"])

    async def test_adapted_agent_rejects_invalid_id_before_query(self):
        with patch.object(tools, "fetch_profile") as fetch:
            responses = await self.invoke("invalid id")
        fetch.assert_not_called()
        self.assertEqual(responses[0]["status"], "invalid_input")
