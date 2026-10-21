---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 21.5 solution: MAS Knowledge Milestone: Defend a Banking Architecture

An executable minimum combines static evidence collection with deterministic routing. The learner designs optional advisory, revision and remote extensions using an architecture decision record.

The employee needs this result: A working preparation example plus an explanation of why each operation and service is needed. A missing source connection must remain an open task; adding more agents does not supply the missing data.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

Start with what the bank must guarantee. Add a model for language work, a service boundary for independent ownership and persistence for required continuity. Each addition needs a specific requirement and a failure contract.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Change the customer brief to require a sanctioned ledger amount. Identify the missing adapter and entitlement contract before changing the route; a new fixture field does not complete that integration.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Collect two required checks | Static fan-out plus join | Both named check outputs exist before routing. |
| Choose the next step by facts | Ordered route function | Incomplete evidence has precedence over amount. |
| Keep optional complexity justified | ADR compares alternatives | Each added agent/service answers a specific requirement. |
| Show verification limits | Separate local control tests and live evaluations | No claim of production readiness rests on a fixture run alone. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Function | Responsibility |
|---|---|
| `documents` | Produce the synthetic checklist result |
| `exposure` | Apply the fictional amount threshold |
| `decide` | Verify case alignment and select the ordered next step |
| `explain` | Render the result without changing its meaning |
| `build_agent` | Compose those responsibilities using native graph edges |

## `pyproject.toml`

```toml
[project]
name = "banking-module-21-5"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["google-adk==2.11.0"]

[tool.uv]
package = false
```

## `.env.example`

```dotenv
GOOGLE_GENAI_USE_ENTERPRISE=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GEMINI_MODEL=gemini-3.8-flash
```

## `bank_case/agent.py`

```python
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
```

## `bank_case/contracts.py`

```python
"""Small, strict boundary for fictional CASE-001; no credit decision."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    case_id: Literal["CASE-001"]
    # Integer cents avoid binary floating-point errors in money arithmetic.
    requested_cents: int = Field(ge=1, le=100_000_000)
    documents_complete: bool


SAMPLE = {
    "case_id": "CASE-001",
    "requested_cents": 25_000_000,
    "documents_complete": False,
}
```

## `runtime.py`

```python
"""Run one synthetic request through the real ADK runtime."""
import asyncio
import json

from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types


async def run_once(agent, payload):
    # This identity is a fixture, never an authentication implementation.
    async with InMemoryRunner(app=App(name="bank_case", root_agent=agent)) as runner:
        session = await runner.session_service.create_session(
            app_name="bank_case", user_id="analyst-demo"
        )
        message = types.Content(
            role="user", parts=[types.Part.from_text(text=json.dumps(payload))]
        )
        events = []
        # The deadline bounds the invocation; it cannot undo external writes.
        async with asyncio.timeout(60):
            async for event in runner.run_async(
                user_id="analyst-demo", session_id=session.id,
                new_message=message, run_config=RunConfig(max_llm_calls=12),
            ):
                events.append(event)
        return events


def display(events):
    for event in events:
        if event.output is not None:
            print(json.dumps({"author": event.author, "output": event.output}))
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"{event.author}: {part.text}")
```

## `run.py`

```python
"""Change the synthetic case inputs without editing the implementation."""
import argparse
import asyncio
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import display, run_once

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a fictional CASE-001 scenario")
    parser.add_argument("--requested-cents", type=int, default=SAMPLE["requested_cents"])
    parser.add_argument("--documents-complete", action="store_true")
    args = parser.parse_args()
    # Copy the fixture; do not mutate a shared dictionary between runs.
    payload = SAMPLE | {"requested_cents": args.requested_cents,
                        "documents_complete": args.documents_complete}
    agent = build_agent()
    display(asyncio.run(run_once(agent, payload)))
```

## Explain the implementation to a reviewer

### `documents`

Read the validated checklist flag and case ID and return a small mapping. The key is complete here because this module defines its own internal branch contract; it is not a live database column. No external fact is fetched.

### `exposure`

Compare the requested cents with the fictional threshold and return that boolean with the case ID. The separate branch allows the join and rule precedence to remain visible. It is a read-only fixture operation.

### `decide`

Read both named branch outputs, reject different case IDs, then apply missing-document precedence before amount. `destination` holds a machine-readable next step. The Event carries that value in output and uses the same string as its route, connecting the business result to explicit graph control.

### `explain`

Read the chosen next step and insert it into a Python f-string for display. The returned output is the same mapping, so rendering does not change the business result. There is no model interpretation between the rule and this baseline explanation.

### `build_agent`

Compose the previously learned fan-out and join, then call decide and route supported labels to explain. Multiple route keys can point to the same renderer while preserving explicit allowed control signals. The function constructs the graph; run.py supplies the case and starts execution.

### Expected reasoning for the prediction exercise

If the agreed requirement permits a deterministic explanation, the verified next step can still be shown. Define that fallback explicitly; never manufacture missing required evidence.

## Trace the implementation

### Restate the bank problem without SDK names

Describe who uses the system, what successful preparation looks like and what it must not claim. If your first sentence names Workflow or A2A, return to the business requirement.

### Build a traceability table

Assign each requirement an owner, input, output, failure outcome and check. For “both checks,” name the two outputs and what happens when one fails. For “understandable,” define evaluation examples with a bank analyst.

### Run the minimum architecture

The sample reuses the ideas from Modules 16 and 17 in one file. The two function outputs reach a JoinNode; decide applies the rules; explain emits the result. No extra framework is introduced.

### Read the composition carefully

The combiner verifies matching case IDs. The ordered conditions preserve document precedence. The route mapping sends all supported next-step labels to the same renderer. Routing remains explicit even though the final explanatory function is shared.

### Choose one justified extension

Add a model-generated explanation, a remote checklist service or a bounded memo revision in a practice branch. Write the requirement that needs it. Define the new input/output contract and explain its failure effect before implementation.

### Review like a bank FDE

Present the English requirement, your decision table, graph, synthetic demonstration, test evidence and untested production assumptions. Ask the reviewer to challenge the authorization boundary, unknown outcomes and source freshness.

### Complete the assessment

Use the rubric in this module’s playbook. A solution that claims a fixture flag is an authoritative bank record or that a model can approve credit without an authorized operation cannot pass, even if its graph executes.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Remove the model from an exact threshold calculation | The result remains correct and the design becomes easier to verify. |
| Make explanations optional | Required collection and routing must still complete without an LLM. |
| Move one check to a remote service on paper | Add identity, timeout, schema and reconciliation requirements. |
| Change the case state during collection | Explain how versions or a fresh read prevent a stale decision. |

### Local evidence

3 offline tests passed, including real ADK execution for the four routing scenarios. The milestone is an executable architecture baseline plus a design assessment, not a deployed banking system.

Tests of strict schemas, routing, joins, budgets and service scope are software contract tests. Scripted model replies are transport fixtures; they cannot demonstrate whether Gemini understands a bank request or produces a faithful explanation.

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [ADK workflow options](https://adk.dev/workflows/)
- [Graph routes](https://adk.dev/graphs/routes/)
- [ADK safety and security](https://adk.dev/safety/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
