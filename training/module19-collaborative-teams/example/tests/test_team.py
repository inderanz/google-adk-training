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
    async def test_two_specialist_calls_return_to_coordinator(self):
        reply = '{"summary":"Fixture advisory note","limitation":"No live case access"}'
        model = ScriptedModel(replies=[call("document_adviser"), text_reply(reply),
                                      call("review_adviser"), text_reply(reply),
                                      text_reply("Fixture combined response")])
        events = await run_once(build_agent(model), "Prepare the full case explanation")
        calls = [call.name for event in events for call in event.get_function_calls()]
        self.assertEqual(calls, ["document_adviser", "review_adviser"])
        self.assertEqual(events[-1].author, "case_coordinator")
        self.assertFalse(model.replies)

    async def test_single_turn_delegation_returns_to_coordinator(self):
        from bank_case.agent import build_delegation_team
        model = ScriptedModel(replies=[call("checklist_specialist"),
                                      text_reply("Fixture specialist result"),
                                      text_reply("Fixture coordinator result")])
        events = await run_once(build_delegation_team(model), "Explain the checklist")
        calls = [call.name for event in events for call in event.get_function_calls()]
        self.assertIn("checklist_specialist", calls)
        self.assertEqual(events[-1].author, "delegation_coordinator")
        self.assertFalse(model.replies)

    async def test_chat_transfer_leaves_specialist_as_responding_agent(self):
        from bank_case.agent import build_delegation_team
        transfer = types.Content(role="model", parts=[types.Part.from_function_call(
            name="transfer_to_agent", args={"agent_name": "checklist_specialist"})])
        model = ScriptedModel(replies=[transfer, text_reply("Fixture specialist answer")])
        events = await run_once(build_delegation_team(model, mode="chat"), "Explain the checklist")
        self.assertEqual(events[-1].author, "checklist_specialist")
        self.assertFalse(model.replies)
