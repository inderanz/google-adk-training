"""Validated facts select one explicit route; no LLM chooses bank policy."""
from google.adk.events import Event
from google.adk.workflow import Workflow
from .contracts import CaseRequest


def choose_route(node_input: CaseRequest) -> Event:
    # Missing evidence takes priority over amount, so the order of these conditions is business logic.
    if not node_input.documents_complete:
        route = "documents"
    elif node_input.requested_cents > 20_000_000:
        route = "specialist"
    else:
        route = "standard"
    return Event(output=node_input.model_dump(), route=route)


def request_documents(node_input: dict) -> Event:
    # Return the selected next step as data; this function does not send a real document request.
    return Event(output={"case_id": node_input["case_id"], "next_step": "collect_documents"},
                 message="Collect the missing checklist evidence before review.")


def specialist_review(node_input: dict) -> Event:
    # Routing identifies the review owner; it does not approve the requested credit.
    return Event(output={"case_id": node_input["case_id"], "next_step": "specialist_review"},
                 message="Send the complete evidence pack to a specialist analyst.")


def standard_review(node_input: dict) -> Event:
    # The remaining valid cases enter standard review; they still require a human decision.
    return Event(output={"case_id": node_input["case_id"], "next_step": "standard_review"},
                 message="Send the complete evidence pack to a standard analyst queue.")


def unsupported_route(node_input: dict) -> Event:
    # Unexpected control labels need an explicit manual outcome instead of an invented default approval.
    return Event(output={"case_id": node_input["case_id"], "next_step": "manual_triage"},
                 message="An unsupported route requires manual triage.")


def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return Workflow(
        name="case_router", input_schema=CaseRequest, timeout=30,
        edges=[
            ("START", choose_route),
            (choose_route, {
                "documents": request_documents,
                "specialist": specialist_review,
                "standard": standard_review,
                "__DEFAULT__": unsupported_route,
            }),
        ],
    )
