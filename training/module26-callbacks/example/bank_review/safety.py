"""ADK plugin hooks plus the official asynchronous Model Armor client.

Study the upstream google/adk-samples safety-plugins recipe for the hook pattern.
This implementation bounds inspection, handles unavailable verdicts, and accepts
only non-streaming text conversations. It does not implement bank authorization.
"""
import json
import os

from google.adk.agents.run_config import StreamingMode
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins import BasePlugin
from google.cloud import modelarmor_v1 as armor
from google.genai import types

REMOVED = "Content withheld by the configured inspection policy."
UNAVAILABLE = "Content inspection is unavailable. Please try again later."


def verdict(result) -> str:
    """An incomplete/unspecified service result never counts as a clean scan."""
    # Service success and a clean filter result are both required before the application permits content.
    if result.invocation_result != armor.InvocationResult.SUCCESS:
        return "unavailable"
    if result.filter_match_state == armor.FilterMatchState.NO_MATCH_FOUND:
        return "allow"
    if result.filter_match_state == armor.FilterMatchState.MATCH_FOUND:
        return "block"
    return "unavailable"


class ModelArmorInspector:
    """Reuse the Google client; credentials come from Application Default Credentials."""

    def __init__(self):
        self.client = None

    async def inspect(self, text: str, response: bool = False) -> str:
        # Use the template’s region and typed Google request; the timeout bounds this inspection attempt.
        if len(text.encode("utf-8")) > 16_384:
            return "block"  # Explicit lab bound, not the service's maximum.
        template = os.environ["MODEL_ARMOR_TEMPLATE"]
        # A template resource is projects/P/locations/L/templates/T.
        pieces = template.split("/")
        if len(pieces) != 6 or pieces[0] != "projects" or pieces[2] != "locations" or pieces[4] != "templates":
            raise ValueError("MODEL_ARMOR_TEMPLATE must be a full template resource name")
        location = pieces[3]
        if location == "global":
            raise ValueError("Model Armor requires a supported regional template")
        if self.client is None:
            self.client = armor.ModelArmorAsyncClient(client_options={
                "api_endpoint": f"modelarmor.{location}.rep.googleapis.com"
            })
        data = armor.DataItem(text=text)
        if response:
            result = await self.client.sanitize_model_response(
                request=armor.SanitizeModelResponseRequest(name=template, model_response_data=data),
                timeout=10, retry=None,
            )
        else:
            result = await self.client.sanitize_user_prompt(
                request=armor.SanitizeUserPromptRequest(name=template, user_prompt_data=data),
                timeout=10, retry=None,
            )
        return verdict(result.sanitization_result)

    async def close(self):
        # Release the owned asynchronous transport when the application runtime shuts down.
        if self.client is not None:
            await self.client.transport.close()


def message(role: str, text: str) -> types.Content:
    # Content holds the role and Parts; a Python string alone is not an ADK replacement message.
    return types.Content(role=role, parts=[types.Part.from_text(text=text)])


class BankingSafety(BasePlugin):
    """Inspects this App's user text, model text, tool arguments and tool results."""

    def __init__(self, inspector=None):
        super().__init__(name="banking_safety")
        self.inspector = inspector or ModelArmorInspector()

    async def check(self, text: str, response: bool = False) -> str:
        # Translate an inspection failure into unavailable so missing evidence of safety does not grant permission.
        try:
            result = await self.inspector.inspect(text, response=response)
        except Exception:
            # Service/configuration errors withhold content; never log the payload.
            return "unavailable"
        return result if result in {"allow", "block"} else "unavailable"

    async def on_user_message_callback(self, *, invocation_context, user_message):
        # Replace blocked input before persistence, and pass the decision to the subsequent run hook.
        parts = user_message.parts or []
        if not parts or any(part.text is None for part in parts):
            decision = "block"  # Binary and multimodal inputs are outside this lab.
        else:
            decision = await self.check("\n".join(part.text for part in parts))
        if decision == "allow":
            return None
        key = f"temp:armor_block:{invocation_context.invocation_id}"
        invocation_context.session.state[key] = decision
        # Replace the user message before ADK appends it to the session.
        return message("user", REMOVED)

    async def before_run_callback(self, *, invocation_context):
        # Consume only this invocation’s decision so a previous blocked request cannot stop an unrelated run.
        if invocation_context.run_config.streaming_mode != StreamingMode.NONE:
            raise ValueError("This safety lab requires StreamingMode.NONE")
        key = f"temp:armor_block:{invocation_context.invocation_id}"
        decision = invocation_context.session.state.pop(key, None)
        if decision is not None:
            return message("model", UNAVAILABLE if decision == "unavailable" else REMOVED)
        return None

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        # Inspect before executing the body; replacing its response prevents this proposed operation.
        decision = await self.check(json.dumps({"tool": tool.name, "args": tool_args}))
        if decision != "allow":
            return {"status": "withheld", "reason": decision}
        return None

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        # A returned result is available here; returning None preserves it for subsequent processing.
        decision = await self.check(json.dumps(result))
        if decision != "allow":
            return {"status": "withheld", "reason": decision}
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        # Inspect every supported text part before publishing this non-streaming model response.
        content = llm_response.content
        if content is None or not content.parts:
            return None
        if any(part.text is None and part.function_call is None for part in content.parts):
            return llm_response.model_copy(update={"content": message("model", REMOVED)})
        text = "\n".join(part.text for part in content.parts if part.text)
        if not text:
            return None  # Function-call arguments are checked in before_tool.
        decision = await self.check(text, response=True)
        if decision != "allow":
            replacement = message("model", UNAVAILABLE if decision == "unavailable" else REMOVED)
            # Deliberately drop the entire blocked response, including any calls.
            return llm_response.model_copy(update={"content": replacement})
        return None

    async def close(self):
        # Release the owned asynchronous transport when the application runtime shuts down.
        await self.inspector.close()
