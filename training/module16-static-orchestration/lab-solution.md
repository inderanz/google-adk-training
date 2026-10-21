---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 16 solution: Static Orchestration: Collecting Independent Evidence

An ADK Workflow schedules two checks, joins their named results, and produces a synthetic evidence pack.

The employee needs this result: One result containing both completed checks, with their source labels. A failed check or mismatched case ID must not become a complete-looking result.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“Both” creates two required operations. “Independent” permits fan-out. “Only after” creates a join. “Same case” creates the comparison in combine. Those four phrases explain the graph and the guard before any SDK import is chosen.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Compare graph output passing with template SequentialAgent/ParallelAgent composition. Templates are appropriate for fixed agent arrangements; the graph makes these function-node inputs and named joins explicit.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Run both checks for every request | Static fan-out from START | The completed pack contains both results. |
| Combine only matching cases | Compare case IDs at the join consumer | Mismatched evidence raises an error. |
| Use exact money and explicit booleans | Strict Pydantic contract; integer cents | Strings, floats and boolean amounts are rejected. |
| Do not turn collection into approval | Result describes evidence and required review | The output makes no credit decision. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Code | How to read it |
|---|---|
| `def ... (node_input: CaseRequest) -> dict` | A function taking one typed input and returning a mapping |
| `requested_cents > 20_000_000` | A strict greater-than comparison; underscores improve numeric readability |
| `JoinNode(name="evidence_join")` | Construct one synchronization node and reuse that object in edges |
| `node_input["document_check"]` | Read a required result by its stable predecessor name |
| `raise ValueError(...)` | Stop producing a successful pack when evidence is inconsistent |
| `timeout=30` | Bound workflow elapsed time; it is not a rollback mechanism |

## `pyproject.toml`

```toml
[project]
name = "banking-module-16"
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

### `document_check`

`node_input` is already a CaseRequest because the workflow validates it at entry. Attribute access reads the case ID and boolean from that model. The returned dictionary copies those selected fields and adds a fixture source identifier. It has no Firestore client and performs no network read.

### `exposure_check`

The expression after `specialist_review` evaluates to a Python boolean. Numeric underscores only improve readability: 20_000_000 means twenty million cents. The operator is `>`, so equality does not request specialist review. This is routing against a fictional threshold, not calculation of a borrower's actual credit exposure.

### `combine`

The predecessor names are keys in JoinNode's output map. Read each required entry, then compare their case IDs before constructing the pack. `raise ValueError` stops the success path for mixed cases. The evidence list keeps both original result mappings. `Event.output` makes that pack available to software; `message` gives a person an explanation.

### `build_agent`

Construct one JoinNode and reuse that same object as destination and source. The first edge fans out to two function objects. The second feeds the two predecessors into the join. The third waits for the join output before combine runs. `input_schema` supplies validation and typed input; `timeout` bounds workflow time. Construction itself executes neither check.

### Expected reasoning for the prediction exercise

No. It indexes the join map by predecessor names. Evidence consistency still needs explicit case/version checks.

## Trace the implementation

### Write the dependency sentence

Say it out loud: both checks need the snapshot; the pack needs both checks. Draw that sentence before naming an ADK class. If one check needed the other’s result, it would not belong in this fan-out.

### Read the input contract

`CaseRequest(BaseModel)` defines a validated object. `Literal["CASE-001"]` restricts this fixture to one case. `strict=True` rejects convenient but dangerous coercions such as `"yes"` to a boolean. `extra="forbid"` rejects unexpected fields. `Field(ge=1, le=...)` bounds the amount. These validations enforce shape, not caller authorization.

### Implement the two pure checks

Each function accepts `node_input` and returns a new dictionary. Attribute access such as `node_input.case_id` reads a validated model field. The threshold is a fictional review-routing rule. The source strings identify local fixtures, not verified external records.

### Wire the fan-out and join

An outer list holds graph edges. `("START", (document_check, exposure_check))` has a tuple of destinations and starts both branches. `((document_check, exposure_check), joined)` feeds their outputs into the same named join. Passing a function object without parentheses registers work; writing `document_check(...)` would execute it immediately.

### Combine deliberately

Look up each result by its node name rather than assuming which branch finished first. Compare IDs. Raise `ValueError` on mismatch so there is no apparently complete evidence pack. Return `Event(output=..., message=...)`: the output feeds software; the message is visible to a person.

### Run and inspect intermediate outputs

The CLI prints each nonempty node output, including the join map. Find both keys before looking at the final pack. Change the amount to exactly 20,000,000 cents and then 20,000,001; only the latter requires the fictional specialist review.

### Plan the real adapters

Replace the fixture document function with the authorized Firestore-backed service from Module 13.5. Read exposure from the bank’s ledger API, not from a user claim. Keep the same return contract and add versions/timestamps. Async network functions should await the official client; do not put blocking requests inside an async function and assume it is concurrent.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Set the amount to 20,000,000 cents | The exposure result is false at the boundary; it becomes true one cent above. |
| Set documents_complete to "false" | Validation rejects the string instead of interpreting it as a boolean. |
| Supply mismatched case IDs directly to combine | The contract test proves the pack is rejected. |
| Make one check fail in a copy | No successful combined pack should be produced; inspect how the failure is surfaced. |

### Local evidence

4 offline tests passed using the real ADK graph runtime, including both joined results, strict boundaries and mismatched-case rejection. The fixture does not call Firestore or a ledger.

Tests of strict schemas, routing, joins, budgets and service scope are software contract tests. Scripted model replies are transport fixtures; they cannot demonstrate whether Gemini understands a bank request or produces a faithful explanation.

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [Graph routes and joins](https://adk.dev/graphs/routes/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Supported workflow choices](https://adk.dev/workflows/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
