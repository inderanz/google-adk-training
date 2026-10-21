"""Local A2A specialist. No authentication: bind only to loopback."""
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.events import Event
from google.adk.workflow import Workflow
from .contracts import CaseRequest


def review_checklist(node_input: CaseRequest) -> Event:
    # The remote service validates its own input; a network caller is not automatically trusted.
    result = {"case_id": node_input.case_id,
              "documents_complete": node_input.documents_complete,
              "source": "training-fixture:checklist-v1"}
    return Event(output=result, message=(
        f"{node_input.case_id}: checklist complete={node_input.documents_complete}. "
        "Synthetic evidence only; no credit approval."
    ))


specialist = Workflow(name="remote_checklist", input_schema=CaseRequest,
                      edges=[("START", review_checklist)], timeout=20)
app = to_a2a(specialist, host="127.0.0.1", port=8001)
