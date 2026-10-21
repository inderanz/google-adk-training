import unittest
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from bank_case.agent import build_agent
from runtime import run_once


class ScriptedModel(BaseLlm):
    """Transport fixture: proves orchestration, never Gemini response quality."""
    model: str = "scripted-test-model"
    replies: list[types.Content]

    async def generate_content_async(self, llm_request, stream=False):
        if not self.replies:
            raise AssertionError("Unexpected extra model call")
        yield LlmResponse(content=self.replies.pop(0))


def text_reply(text):
    return types.Content(role="model", parts=[types.Part.from_text(text=text)])


def call(name):
    return types.Content(role="model", parts=[types.Part.from_function_call(
        name=name, args={"request": "Explain the checklist for CASE-001"})])


class TeamTests(unittest.IsolatedAsyncioTestCase):
    async def test_specialist_result_returns_to_coordinator(self):
        model = ScriptedModel(replies=[call("document_adviser"),
                                      text_reply("Fixture specialist result"),
                                      text_reply("Fixture coordinator result")])
        events = await run_once(build_agent(model), "Prepare the case")
        calls = [call.name for event in events for call in event.get_function_calls()]
        self.assertIn("document_adviser", calls)
        self.assertEqual(events[-1].author, "case_coordinator")
        self.assertFalse(model.replies)

    def test_coordinator_has_no_payment_or_approval_tool(self):
        agent = build_agent(ScriptedModel(replies=[]))
        self.assertEqual([tool.name for tool in agent.tools], ["document_adviser"])
