"""Small callback contracts; these are not a general content-safety system."""
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types


def validate_request(case_id, max_items) -> dict | None:
    """Reject booleans as integers and unsupported scope before any lookup."""
    # Validate at the reusable business boundary because direct calls can bypass agent callbacks.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if type(max_items) is not int or not 1 <= max_items <= 5:
        return {"status": "invalid_limit", "allowed_range": "1..5"}
    return None


def read_checklist(case_id: str, max_items: int = 5) -> dict:
    """The tool validates even when called without the ADK callback."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    problem = validate_request(case_id, max_items)
    if problem is not None:
        return problem
    return {"status": "ok", "case_id": case_id,
            "missing_documents": ["ownership_register"][:max_items],
            "source": "training-fixture:checklist-v1"}


def before_agent(callback_context: CallbackContext) -> types.Content | None:
    # Initialize invocation-scoped diagnostic state before this agent starts its work.
    callback_context.state["temp:checks"] = []
    return None


def before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    # This is an explicit lab input contract, not semantic intent detection.
    # This exact lab command illustrates provider-call replacement, not general natural-language policy detection.
    content = callback_context.user_content
    text = " ".join(part.text or "" for part in (content.parts or [])) if content else ""
    if text.strip() == "LAB:REQUEST_CREDIT_APPROVAL":
        return LlmResponse(content=types.Content(role="model", parts=[
            types.Part.from_text(text="A human analyst must make the credit decision.")
        ]))
    return None


def before_tool(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None:
    # Reuse the tool’s validator to reject invalid work before executing the resolved tool body.
    if tool.name != "read_checklist":
        return None
    problem = validate_request(args.get("case_id"), args.get("max_items", 5))
    checks = list(tool_context.state.get("temp:checks", []))
    checks.append("blocked" if problem is not None else "validated")
    tool_context.state["temp:checks"] = checks
    return problem  # A dictionary replaces this tool execution; None allows it.


def after_tool(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None:
    # Add human ownership only to successful lookup results without rewriting failure outcomes.
    if tool.name == "read_checklist" and tool_response.get("status") == "ok":
        return {**tool_response, "decision_owner": "human_analyst"}
    return None


def after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    # Demonstrate response copying without deleting other text or function calls.
    # Modify only the intended text parts so other response fields and function calls survive.
    content = llm_response.content
    if content is None or not content.parts:
        return None
    changed = False
    parts = []
    for part in content.parts:
        if part.text and "LAB_INTERNAL_MARKER" in part.text:
            parts.append(part.model_copy(update={"text": part.text.replace("LAB_INTERNAL_MARKER", "[removed]")}))
            changed = True
        else:
            parts.append(part)
    if not changed:
        return None
    return llm_response.model_copy(update={"content": content.model_copy(update={"parts": parts})})


def after_agent(callback_context: CallbackContext) -> types.Content | None:
    # Tracked state assignment can emit a state-only event after the text response.
    callback_context.state["last_review_invocation"] = callback_context.invocation_id
    return None
