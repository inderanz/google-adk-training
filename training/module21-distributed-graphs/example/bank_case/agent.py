"""A fixed, developer-controlled endpoint; never accept a URL from the model."""
from google.adk.a2a.agent import RemoteA2aAgent


def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return RemoteA2aAgent(
        name="remote_checklist_client",
        agent_card="http://127.0.0.1:8001/.well-known/agent-card.json",
        description="Read-only synthetic checklist specialist on this machine.",
        timeout=10,
        use_legacy=False,
    )
