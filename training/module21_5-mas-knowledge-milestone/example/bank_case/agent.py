"""An executable architecture decision: fixed checks, explicit route, no LLM."""
from google.adk.events import Event
from google.adk.workflow import JoinNode, Workflow
from .contracts import CaseRequest


def documents(node_input: CaseRequest) -> dict:
    # Preserve case identity so the downstream join can reject mixed records.
    return {"complete": node_input.documents_complete, "case_id": node_input.case_id}


def exposure(node_input: CaseRequest) -> dict:
    # Compute the fictional review requirement in exact code rather than asking a model to guess it.
    return {"specialist": node_input.requested_cents > 20_000_000,
            "case_id": node_input.case_id}


def decide(node_input: dict) -> Event:
    # Read both named results and apply the agreed precedence before rendering an explanation.
    docs = node_input["documents"]
    amount = node_input["exposure"]
    if docs["case_id"] != amount["case_id"]:
        raise ValueError("Case evidence mismatch")
    if not docs["complete"]:
        destination = "collect_documents"
    elif amount["specialist"]:
        destination = "specialist_review"
    else:
        destination = "standard_review"
    return Event(output={"case_id": docs["case_id"], "next_step": destination},
                 route=destination)


def explain(node_input: dict) -> Event:
    # Expose the selected next step without changing the rule or claiming a credit decision.
    return Event(output=node_input,
                 message=f"Next step: {node_input['next_step']}. No credit approval issued.")


def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    joined = JoinNode(name="evidence_join")
    return Workflow(
        name="review_milestone", input_schema=CaseRequest, timeout=30,
        edges=[("START", (documents, exposure)),
               ((documents, exposure), joined), (joined, decide),
               (decide, {"collect_documents": explain, "specialist_review": explain,
                         "standard_review": explain})],
    )
