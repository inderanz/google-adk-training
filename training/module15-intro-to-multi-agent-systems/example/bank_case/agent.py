"""Two advisory roles; the coordinator calls a specialist and resumes."""
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


def build_agent(model=None):
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    selected_model = model or os.environ["GEMINI_MODEL"]
    document_adviser = Agent(
        name="document_adviser",
        model=selected_model,
        description="Explains the fictional commercial-review document checklist.",
        instruction=(
            "The training checklist requires financial statements and an ownership "
            "register. Explain why each is useful. You have no case lookup tool, "
            "so never claim that a document was received or that credit was approved."
        ),
    )
    return Agent(
        name="case_coordinator",
        model=selected_model,
        instruction=(
            "Help a bank analyst prepare CASE-001 for Acme Robotics (fictional). "
            "Consult document_adviser for checklist questions, then explain the "
            "next step. For actual status, say an authorized case lookup is needed. "
            "No agent here can approve credit or move funds."
        ),
        tools=[AgentTool(agent=document_adviser)],
    )
