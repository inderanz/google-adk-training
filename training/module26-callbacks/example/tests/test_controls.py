import unittest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from google.adk.tools import FunctionTool
from bank_review.agent import build_app
from bank_review import controls
from support import ScriptedModel, call, text, invoke, results


class CallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_invalid_tool_arguments_short_circuit_execution(self):
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001", max_items=99), text("Invalid")])
        app = build_app(model)
        def forbidden_body(case_id: str, max_items: int = 5) -> dict:
            raise AssertionError("The invalid tool call must be short-circuited")
        forbidden_body.__name__ = "read_checklist"
        app.root_agent.tools = [FunctionTool(func=forbidden_body)]
        events, session, _ = await invoke(app)
        self.assertEqual(results(events)[0]["status"], "invalid_limit")
        self.assertIn("last_review_invocation", session.state)

    async def test_before_model_can_answer_without_model(self):
        model = ScriptedModel(replies=[])
        app = build_app(model)
        def after_model_must_not_run(callback_context, llm_response):
            raise AssertionError("A before-model replacement bypasses after-model in this runtime")
        app.root_agent.after_model_callback = after_model_must_not_run
        events, _, _ = await invoke(app, "LAB:REQUEST_CREDIT_APPROVAL")
        messages = [event.content.parts[0].text for event in events if event.content and event.content.parts]
        self.assertTrue(any("human analyst" in value for value in messages))

    async def test_valid_tool_result_is_augmented(self):
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001", max_items=1), text("Ready")])
        events, _, _ = await invoke(build_app(model))
        self.assertEqual(results(events)[0]["decision_owner"], "human_analyst")

    def test_multipart_edit_preserves_calls_and_metadata(self):
        call_part = types.Part.from_function_call(name="read_checklist", args={"case_id": "CASE-001"})
        original = LlmResponse(content=types.Content(role="model", parts=[
            types.Part.from_text(text="First"), types.Part.from_text(text="LAB_INTERNAL_MARKER"), call_part]),
            partial=False, model_version="fixture")
        edited = controls.after_model(None, original)
        self.assertEqual(edited.content.parts[1].text, "[removed]")
        self.assertEqual(edited.content.parts[2], call_part)
        self.assertEqual(edited.model_version, "fixture")
        self.assertEqual(original.content.parts[1].text, "LAB_INTERNAL_MARKER")

    def test_direct_tool_still_validates(self):
        for invalid in [True, 0, 6, "3", None]:
            self.assertEqual(controls.read_checklist("CASE-001", invalid)["status"], "invalid_limit")


class CallbackListTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_dictionary_stops_tool_callback_list_and_body(self):
        # Pin a subtle ADK 2.10 contract: {} is a replacement, not None.
        executed = []
        def first(tool, args, tool_context):
            executed.append("first")
            return {}
        def second(tool, args, tool_context):
            raise AssertionError("A non-None replacement must stop this list")
        def body(case_id: str, max_items: int = 5) -> dict:
            raise AssertionError("The tool must not run after replacement")
        body.__name__ = "read_checklist"
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001"), text("done")])
        app = build_app(model)
        app.root_agent.tools = [FunctionTool(func=body)]
        app.root_agent.before_tool_callback = [first, second]
        events, _, _ = await invoke(app)
        self.assertEqual(executed, ["first"])
        self.assertEqual(results(events), [{}])
