"""Record bounded metadata; standard runtime spans come from ADK itself."""
import logging
from google.adk.plugins import BasePlugin
from google.cloud.logging.handlers import StructuredLogHandler
from opentelemetry import trace

logger = logging.getLogger("bank_review.operations")


def configure_logging() -> None:
    """Write Cloud Logging structured JSON to stdout; the runtime collects it."""
    # Install one structured handler per logger so repeated setup does not duplicate operational records.
    if not any(isinstance(handler, StructuredLogHandler) for handler in logger.handlers):
        logger.addHandler(StructuredLogHandler())
    logger.setLevel(logging.INFO)
    logger.propagate = False


class ReviewTelemetry(BasePlugin):
    """No shared request counters and no prompt, result or exception text capture."""

    def __init__(self):
        super().__init__(name="review_telemetry")

    def record(self, tool_context, tool, outcome: str) -> None:
        # Allowlist diagnostic metadata; copying tool arguments or raw results would disclose banking content.
        fields = {
            "event": "bank_tool_outcome",
            "invocation_id": tool_context.invocation_id,
            "agent": tool_context.agent_name,
            "tool": tool.name,
            "outcome": outcome,
        }
        span = trace.get_current_span().get_span_context()
        if span.is_valid:
            fields["trace_id"] = format(span.trace_id, "032x")
        logger.info("bank_tool_outcome", extra={"json_fields": fields})

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        # A returned result is available here; returning None preserves it for subsequent processing.
        outcome = "ok" if result.get("status") == "ok" else "business_failure"
        self.record(tool_context, tool, outcome)
        return None  # Observe without replacing the tool result.

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        # Recovery returns an explicit unavailable result, which must never be interpreted as retrieved evidence.
        self.record(tool_context, tool, "exception")
        # This is an intentional recovery contract, not a successful lookup.
        return {"status": "unavailable", "retryable": True}
