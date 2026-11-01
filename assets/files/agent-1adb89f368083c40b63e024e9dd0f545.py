"""An explicit fan-out and join over a synthetic case snapshot."""
from google.adk.events import Event
from google.adk.workflow import JoinNode, Workflow
from .contracts import CaseRequest


def document_check(node_input: CaseRequest) -> dict:
    # The checklist is required evidence, so copy its value and case identity into a separate result.
    return {
        "case_id": node_input.case_id,
        "documents_complete": node_input.documents_complete,
        "source": "training-fixture:document-checklist-v1",
    }


def exposure_check(node_input: CaseRequest) -> dict:
    # A teaching threshold, not a bank policy or an approval limit.
    # The customer rule uses a strict threshold; equality must not enter specialist review.
    return {
        "case_id": node_input.case_id,
        "specialist_review": node_input.requested_cents > 20_000_000,
        "source": "training-fixture:review-threshold-v1",
    }


def combine(node_input: dict) -> Event:
    # JoinNode keys are the predecessor node names, not completion order.
    # Both branches must refer to the same case before their evidence can form one pack.
    documents = node_input["document_check"]
    exposure = node_input["exposure_check"]
    if documents["case_id"] != exposure["case_id"]:
        raise ValueError("Cannot combine evidence from different cases")
    result = {"case_id": documents["case_id"], "evidence": [documents, exposure]}
    return Event(output=result, message="Evidence collected; analyst review is required.")


def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    joined = JoinNode(name="evidence_join")
    return Workflow(
        name="evidence_pipeline", input_schema=CaseRequest, timeout=30,
        edges=[
            ("START", (document_check, exposure_check)),
            ((document_check, exposure_check), joined),
            (joined, combine),
        ],
    )
