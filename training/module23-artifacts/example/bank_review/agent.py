"""The agent chooses tools; each tool enforces its own data contract."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .tools import create_review_pack, save_checklist


def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    agent = Agent(
        name="review_pack_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Prepare a fictional CASE-001 review pack. Call save_checklist, then "
            "pass its returned version to create_review_pack. Never invent a version. "
            "Report the filenames and versions returned by the tools. If a tool fails, "
            "report incomplete preparation. No real evidence lookup or approval occurs."
        ),
        tools=[save_checklist, create_review_pack],
    )
    return App(name="bank_review", root_agent=agent)


app = build_app()
root_agent = app.root_agent
