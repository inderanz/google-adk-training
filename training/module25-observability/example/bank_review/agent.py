"""Inject a known dependency failure to practise an operational investigation."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .telemetry import ReviewTelemetry, configure_logging


def read_checklist(case_id: str, simulate_outage: bool = False) -> dict:
    """Read a synthetic checklist; outage injection is a training-only option."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if simulate_outage:
        raise TimeoutError("Synthetic dependency timeout")
    return {"status": "ok", "missing_documents": ["ownership_register"],
            "source": "training-fixture:checklist-v1"}


def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    configure_logging()
    agent = Agent(
        name="observed_review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Read CASE-001's checklist with read_checklist. Set simulate_outage=True "
            "only when asked to simulate an outage. On unavailable, explain that "
            "preparation is incomplete; do not invent document status or retry in "
            "a loop. A human owns the credit decision. Data is synthetic."
        ), tools=[read_checklist],
    )
    return App(name="bank_review", root_agent=agent, plugins=[ReviewTelemetry()])


app = build_app()
root_agent = app.root_agent
