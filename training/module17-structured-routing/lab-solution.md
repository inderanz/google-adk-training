---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 17 solution: Structured Routing: Turning Bank Rules into Edges

Exactly one route handler produces a next-step instruction from a validated synthetic snapshot.

The employee needs this result: Exactly one next step: collect documents, specialist review or standard review. Malformed input is rejected. An unexpected routing label goes to manual checking.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

Translate “missing documents first” into the first if. Translate “above” into >, including a boundary case at equality. The fallback represents an unrecognized control label, not permission to guess the bank policy.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Add a policy version and effective date to an authoritative input contract. Show how a change from above to at-least affects both the condition and its boundary test.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Missing documents take precedence | First branch in choose_route | A high amount with missing documents still goes to document collection. |
| Define the threshold precisely | Integer cents and > 20_000_000 | The exact threshold stays in standard review; one cent above goes to specialist review. |
| Handle unexpected routing values | Explicit __DEFAULT__ edge | Unsupported routes lead to manual triage. |
| Reject malformed input before routing | Workflow input_schema | Unknown cases, booleans as money and extra approval fields are rejected. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Expression | Meaning |
|---|---|
| `if not node_input.documents_complete` | The first condition is true when the validated boolean is false |
| `elif ... > ...` | Test this condition only if the previous condition was false |
| `model_dump()` | Convert a Pydantic model into plain data for downstream nodes |
| `Event(output=..., route=...)` | Carry data separately from the routing decision |
| `(choose_route, {...})` | Map the emitting node’s route labels to destinations |
| `"__DEFAULT__": unsupported_route` | Handle an unmatched label; malformed input still fails validation earlier |

## `pyproject.toml`

```toml
[project]
name = "banking-module-17"
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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
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
```

## `bank_case/contracts.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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

### `choose_route`

Python evaluates the conditions from top to bottom. When documents are missing, the first assignment wins and neither later branch runs. Otherwise it compares cents and selects specialist or standard. `model_dump()` produces the plain dictionary that the handler will receive. `route=route` means the left name is the Event field and the right name is this function's local variable.

### `request_documents`

This handler receives a plain dictionary, so it uses square-bracket key lookup rather than model attribute access. It returns the canonical case ID and the action label collect_documents. The message explains that label to the analyst. It does not contact the borrower or write a request into a case system.

### `specialist_review`

The router has already applied the rule. This handler only packages the next-step label specialist_review and a readable explanation. There is no hidden second model decision or approval operation here. A real queue submission would require a separate service call and an idempotency contract.

### `standard_review`

The normal handler returns standard_review, which still means an analyst queue, not automatic approval. Keeping the label machine-readable lets a UI or later operation interpret it without parsing prose. The current example returns data only.

### `unsupported_route`

This handler preserves the case identifier but chooses manual_triage. It is deliberately distinguishable from the standard path. The default mapping invokes it for an unmatched routing signal; an invalid input schema fails earlier and does not reach this handler.

### `build_agent`

The first edge runs choose_route. The next edge contains a dictionary mapping emitted labels to function objects. Quoted strings are route keys; unquoted handler names reference code. __DEFAULT__ is the fallback key. No outgoing edges are needed for the handlers because their results terminate their branches.

### Expected reasoning for the prediction exercise

No named route matches; the __DEFAULT__ mapping selects manual triage. That result is deliberately different from a successful standard route.

## Trace the implementation

### Write a decision table

Use the four rows above. Work out the result for an incomplete high-value case before coding. This catches the common mistake of checking the amount first and allowing missing evidence to bypass collection.

### Validate the boundary

Read `CaseRequest` from Module 16 again. The test passes invalid values directly to Pydantic to demonstrate rejection. The fixture CLI supplies a dictionary; a production endpoint must obtain the actual status and amount from trusted services.

### Implement choose_route

`if`, `elif` and `else` form one ordered decision chain. Only one assignment to `route` happens. `node_input.model_dump()` converts the validated model into a JSON-compatible dictionary. `Event(..., route=route)` tells ADK which edge to take.

### Keep handlers narrow

Each handler reads the case ID and returns a `next_step` plus a human-readable message. There is no queue API here: “specialist_review” is a proposed next step in the demo. In production, a queue write needs its own authorized, idempotent service operation.

### Connect the route map

The route dictionary contains function objects as values. Quoted route strings are business labels; unquoted names such as `request_documents` refer to Python functions. The special default key provides a fall-through destination for an unmatched routing label.

### Exercise boundaries through ADK

The tests invoke the real graph for incomplete/low, incomplete/high, complete/exact threshold and complete/one-cent-above cases. Inspect the final `next_step`. Test the helper and runtime wiring: checking only the Python comparison would miss a misspelled edge label.

### Add a policy safely

For practice, add a training rule requiring manual triage above a second threshold. Update the requirement table, route function, mapping, diagram explanation and boundary tests together. Explain its precedence relative to missing documents.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Incomplete checklist and maximum allowed amount | Document collection wins because its rule comes first. |
| Complete checklist at and one cent above the threshold | The two requests select different analyst queues. |
| Change one emitted label in a copy | The default handler sends it to manual triage; it must not look like normal review. |
| Put an approval field in the request | The input schema rejects the extra field. |

### Local evidence

3 offline tests passed, including a real ADK run for all four decision-table scenarios and strict input checks. No live queue or credit-decision service is connected.

Tests of strict schemas, routing, joins, budgets and service scope are software contract tests. Scripted model replies are transport fixtures; they cannot demonstrate whether Gemini understands a bank request or produces a faithful explanation.

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [ADK graph routing](https://adk.dev/graphs/routes/)
- [Structured graph data](https://adk.dev/graphs/data-handling/)
- [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

