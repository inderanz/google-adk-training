"""A coordinator consults two local specialists using call-and-return."""
import os
from typing import Literal
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field


class AdvisoryNote(BaseModel):
    summary: str = Field(max_length=600)
    limitation: str = Field(max_length=300)


def build_agent(model=None):
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    selected_model = model or os.environ["GEMINI_MODEL"]
    documents = Agent(
        name="document_adviser", model=selected_model,
        description="Explains financial statements and ownership-register evidence.",
        instruction="Explain the two required documents; you cannot verify receipt.",
        output_schema=AdvisoryNote,
    )
    policy = Agent(
        name="review_adviser", model=selected_model,
        description="Explains that a human analyst owns the credit decision.",
        instruction=("Explain that analysts assess evidence and authorize decisions. "
                     "You have no policy retrieval tool; do not invent policy limits."),
        output_schema=AdvisoryNote,
    )
    return Agent(
        name="case_coordinator", model=selected_model,
        instruction=(
            "Prepare an advisory explanation for CASE-001 (fictional). For a full "
            "preparation request, consult both advisers and combine their notes, "
            "preserving their limitations. If either fails, report an incomplete "
            "explanation. Do not approve credit or claim current case status."
        ),
        tools=[AgentTool(agent=documents), AgentTool(agent=policy)],
    )


def build_delegation_team(model=None, mode: Literal["chat", "task", "single_turn"] = "single_turn"):
    # Mode chooses the interaction contract, not a banking permission.
    # Create a fresh child for this parent; mode controls delegation rather than business authorization.
    selected_model = model or os.environ["GEMINI_MODEL"]
    specialist = Agent(
        name="checklist_specialist", model=selected_model, mode=mode,
        description="Explains the financial-statements and ownership-register checklist.",
        instruction="Explain the two document types. Do not claim receipt or approval.",
    )
    return Agent(
        name="delegation_coordinator", model=selected_model,
        instruction="Delegate checklist questions to checklist_specialist.",
        sub_agents=[specialist],
    )
