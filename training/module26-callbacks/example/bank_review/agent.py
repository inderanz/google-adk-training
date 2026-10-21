"""Attach local lifecycle callbacks to one agent, not to every agent globally."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from . import controls


def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    agent = Agent(
        name="controlled_review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Explain the CASE-001 checklist using read_checklist. Pass a requested "
            "max_items exactly; do not silently repair an invalid limit. Report "
            "tool errors truthfully. You cannot approve credit. Data is synthetic."
        ),
        tools=[controls.read_checklist],
        before_agent_callback=controls.before_agent,
        after_agent_callback=controls.after_agent,
        before_model_callback=controls.before_model,
        after_model_callback=controls.after_model,
        before_tool_callback=controls.before_tool,
        after_tool_callback=controls.after_tool,
    )
    return App(name="bank_review", root_agent=agent)


# One package can expose either the isolated lesson or the integrated exercise.
# The environment is configured by the operator, never by a user prompt.
if os.environ.get("BANKING_CAPSTONE") == "true":
    from .capstone import build_capstone
    app = build_capstone()
else:
    app = build_app()
root_agent = app.root_agent
