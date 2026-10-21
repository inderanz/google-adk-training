"""Evaluate grounded explanation separately from exact tool contracts."""
import os
from google.adk.agents import Agent
from google.adk.apps import App


def read_case(case_id: str) -> dict:
    """Read a synthetic record; unsupported identifiers never return CASE-001."""
    # Reject unsupported identifiers before returning facts, preventing accidental substitution of another case.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    return {
        "status": "ok", "case_id": case_id,
        "missing_documents": ["ownership_register"],
        "source": "training-fixture:checklist-v1",
        "decision_owner": "human_analyst",
    }


def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    agent = Agent(
        name="review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Help prepare commercial reviews using read_case. Ask for the case ID "
            "if absent. For a supplied case ID, look it up before making factual "
            "claims. Report missing documents, source and human decision ownership. "
            "On not_found, say the case was not found; never substitute another case. "
            "You cannot approve credit or modify records. Tool data is synthetic."
        ),
        tools=[read_case],
    )
    return App(name="bank_review", root_agent=agent)


app = build_app()
root_agent = app.root_agent
