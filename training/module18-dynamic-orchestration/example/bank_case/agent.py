"""Schedule only the read-only checks required by this case."""
from google.adk.agents.context import Context
from google.adk.events import Event
from google.adk.workflow import Workflow, node
from .contracts import CaseRequest


def checklist_check(node_input: dict) -> dict:
    # Return only this check’s result so the orchestrator can name and combine completed work.
    return {"check": "documents", "complete": node_input["documents_complete"]}


def exposure_check(node_input: dict) -> dict:
    # The parent schedules this child only after the amount rule requires specialist review.
    return {"check": "exposure", "requires_specialist": True}


@node(rerun_on_resume=True)
async def collect_required_checks(ctx: Context, node_input: CaseRequest) -> Event:
    # Construct a fresh list per call; never retain another case's evidence.
    # Always collect documents, then schedule only the allowlisted conditional work the amount requires.
    results = []
    payload = node_input.model_dump()
    results.append(await ctx.run_node(checklist_check, node_input=payload))
    if node_input.requested_cents > 20_000_000:
        results.append(await ctx.run_node(exposure_check, node_input=payload))
    return Event(
        output={"case_id": node_input.case_id, "checks": results},
        message="Required checks collected; no credit decision has been made.",
    )


def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return Workflow(
        name="dynamic_checks", input_schema=CaseRequest, timeout=30,
        edges=[("START", collect_required_checks)],
    )
