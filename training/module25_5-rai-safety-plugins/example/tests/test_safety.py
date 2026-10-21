import unittest
from unittest.mock import AsyncMock, patch
from google.cloud import modelarmor_v1 as armor
from google.genai import types
from bank_review.agent import build_app
from bank_review.safety import ModelArmorInspector, verdict, REMOVED, UNAVAILABLE
from support import ScriptedModel, call, text, invoke, results


class FixtureInspector:
    """Deterministic inspection fixture; never presented as a Model Armor score."""
    def __init__(self, decisions):
        self.decisions = list(decisions)

    async def inspect(self, text, response=False):
        decision = self.decisions.pop(0)
        if isinstance(decision, Exception):
            raise decision
        return decision

    async def close(self):
        pass


class SafetyTests(unittest.IsolatedAsyncioTestCase):
    async def test_official_client_receives_bounded_typed_request(self):
        inspector = ModelArmorInspector()
        inspector.client = AsyncMock()
        inspector.client.sanitize_user_prompt.return_value = armor.SanitizeUserPromptResponse(
            sanitization_result=armor.SanitizationResult(invocation_result=armor.InvocationResult.SUCCESS,
                filter_match_state=armor.FilterMatchState.NO_MATCH_FOUND))
        with patch.dict("os.environ", {"MODEL_ARMOR_TEMPLATE": "projects/lab/locations/us-central1/templates/test"}):
            self.assertEqual(await inspector.inspect("synthetic input"), "allow")
        kwargs = inspector.client.sanitize_user_prompt.call_args.kwargs
        self.assertEqual(kwargs["request"].user_prompt_data.text, "synthetic input")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertIsNone(kwargs["retry"])

    async def test_allowed_call_reaches_tool_and_model(self):
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001"), text("Fixture answer")])
        app = build_app(model, FixtureInspector(["allow"] * 4))
        events, _, _ = await invoke(app)
        self.assertEqual(results(events)[0]["status"], "ok")

    async def test_blocked_user_text_not_saved_or_sent_to_model(self):
        app = build_app(ScriptedModel(replies=[]), FixtureInspector(["block"]))
        events, saved, _ = await invoke(app, "SYNTHETIC_BLOCKED_INPUT")
        self.assertEqual(events[-1].content.parts[0].text, REMOVED)
        self.assertNotIn("SYNTHETIC_BLOCKED_INPUT", saved.model_dump_json())

    async def test_inspection_exception_withholds_input(self):
        app = build_app(ScriptedModel(replies=[]), FixtureInspector([TimeoutError("fixture")]))
        events, saved, _ = await invoke(app, "SYNTHETIC_INPUT")
        self.assertEqual(events[-1].content.parts[0].text, UNAVAILABLE)
        self.assertNotIn("SYNTHETIC_INPUT", saved.model_dump_json())

    async def test_later_model_part_is_inspected_before_persistence(self):
        response = types.Content(role="model", parts=[types.Part.from_text(text="Fine"), types.Part.from_text(text="SYNTHETIC_BLOCKED_OUTPUT")])
        app = build_app(ScriptedModel(replies=[response]), FixtureInspector(["allow", "block"]))
        events, saved, _ = await invoke(app)
        self.assertEqual(events[-1].content.parts[0].text, REMOVED)
        self.assertNotIn("SYNTHETIC_BLOCKED_OUTPUT", saved.model_dump_json())

    async def test_tool_output_withheld_before_returning_to_model(self):
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001"), text("Cannot complete")])
        app = build_app(model, FixtureInspector(["allow", "allow", "block", "allow"]))
        events, _, _ = await invoke(app)
        self.assertEqual(results(events)[0]["status"], "withheld")

    def test_service_result_requires_success_and_no_match(self):
        for status in armor.InvocationResult:
            for match in armor.FilterMatchState:
                result = armor.SanitizationResult(invocation_result=status, filter_match_state=match)
                expected = "allow" if status == armor.InvocationResult.SUCCESS and match == armor.FilterMatchState.NO_MATCH_FOUND else "block" if status == armor.InvocationResult.SUCCESS and match == armor.FilterMatchState.MATCH_FOUND else "unavailable"
                self.assertEqual(verdict(result), expected)
