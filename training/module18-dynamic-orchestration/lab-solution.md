---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 18 solution: Dynamic Orchestration: Scheduling the Checks a Case Needs

A dynamic ADK node performs the required checklist check and conditionally runs one exposure check, returning their explicit results.

The employee needs this result: A list containing the required checklist result and, when applicable, the exposure-check result. A check that was skipped must not be described as completed. A failed required check must remain visible.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“Always” places checklist outside the if. “Only above the threshold” puts exposure inside it. “A bounded list of checks” means the callables are developer-defined; no model-generated import or function name is accepted.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Before implementing resumability, write an interruption matrix: before child, after child, before external commit, after commit with lost response. Give each external write a destination-enforced idempotency key; do not claim resume verification from the ordinary lab run.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Checklist always runs | Unconditional awaited child call | Every result contains documents. |
| Extra check only when required | Python if around ctx.run_node | The exact threshold runs one check; one cent above runs two. |
| Bound the work | Finite allowlisted children and workflow timeout | There is no model-generated function name or unbounded task list. |
| Keep execution visible to ADK | Use ctx.run_node for child work | Child outputs appear in the event stream. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Expression | Meaning |
|---|---|
| `@node(...)` | Decorate a function with ADK node configuration |
| `async def ...` | Define a coroutine that can await asynchronous work |
| `ctx: Context` | Request the current workflow execution context |
| `await ctx.run_node(checklist_check, node_input=payload)` | Execute a known child through ADK and receive its output |
| `results.append(...)` | Add one completed result to this invocation’s list |
| `edges=[("START", collect_required_checks)]` | Start the dynamic scheduler; internal child choices are in Python |

## `pyproject.toml`

```toml
[project]
name = "banking-module-18"
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

### `checklist_check`

The child receives the dumped dictionary, so `node_input["documents_complete"]` reads a required key. Its fresh result names the check and copies the boolean. A missing key raises rather than silently becoming false, but the parent normally supplies this key from the validated contract.

### `exposure_check`

The parent calls this child only after the high-amount condition passes. Therefore the fixture returns requires_specialist=true without repeating the comparison. The unused payload keeps the same child-call interface. A real exposure service would replace this fixture calculation and return its own authoritative evidence.

### `collect_required_checks`

The decorator supplies the resume setting required for dynamic child calls. The local list starts empty for every invocation. `await` completes the checklist child before append stores its result. The if statement determines whether the exposure child is called at all. The final Event returns the case and completed check list; it does not claim persistence of the local list across a process restart.

### `build_agent`

There is only one declared entry edge because collect_required_checks owns the internal conditional sequence. `CaseRequest` still validates the entry data. Dynamic children remain ADK node executions because the parent uses ctx.run_node; calling arbitrary Python directly would not create that same node boundary.

### Expected reasoning for the prediction exercise

No. Shared mutable state could retain another request’s results. This function intentionally constructs a fresh per-invocation list.

## Trace the implementation

### Identify what varies

The number of checks varies, but the permitted checks do not. Write the allowlist—checklist and exposure—before designing a planner. The supplied amount controls selection; a user cannot submit a function name or import path.

### Read the child functions

Each returns a small dictionary. `checklist_check` reads the supplied boolean. `exposure_check` returns a fixture signal because its caller already applied the threshold. Its result is not a balance lookup or an independent credit assessment.

### Decorate the orchestrator

`@node(rerun_on_resume=True)` applies ADK execution behavior to the function immediately below it. The `ctx` parameter receives ADK Context. The `node_input` parameter receives the typed predecessor output. Do not confuse this workflow context with a tool’s injected ToolContext.

### Build a fresh result list

`results = []` creates a per-call list. `model_dump()` produces a payload for children. `results.append(await ctx.run_node(...))` waits for the child result and then adds it. A module-level mutable list would mix evidence between requests.

### Use Python control flow for selection

The `if` surrounds the exposure child call, so the child is not scheduled for amounts at or below the threshold. The two calls are sequential in this example. Writing async code does not make this loop automatically parallel.

### Return both software output and a message

The returned Event contains the case ID and the list of checks. It also tells the learner that no credit decision occurred. The outer Workflow has one entry edge because the dynamic function owns internal scheduling.

### Inspect the actual child work

Run the two threshold scenarios in the tests and compare check names. Add an optional read-only check in a practice copy, then justify the exact condition, output contract and maximum number of calls.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Use exactly the threshold amount | Only the checklist child runs. |
| Increase by one cent | Both checklist and exposure children run. |
| Use an invalid case ID | Validation stops the request before any child is scheduled. |
| Replace a child with a controlled failure in a copy | A success result must not silently omit the failed required check. |

### Local evidence

3 offline tests passed, including real ADK dynamic scheduling on both sides of the threshold. External retries and durable human approval are design extensions, not implemented by this fixture.

Tests of strict schemas, routing, joins, budgets and service scope are software contract tests. Scripted model replies are transport fixtures; they cannot demonstrate whether Gemini understands a bank request or produces a faithful explanation.

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [Dynamic workflows](https://adk.dev/graphs/dynamic/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Resume agents](https://adk.dev/runtime/resume/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

