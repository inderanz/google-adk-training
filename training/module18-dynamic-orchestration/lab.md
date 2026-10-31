---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 18: Dynamic Orchestration: Scheduling the Checks a Case Needs

**What you are practising:** Dynamic workflows and child-node execution in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

Some cases need an additional specialist check and others do not. The analyst wants the checklist checked for every case, with the extra check performed only when the exercise’s amount rule requires it.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Always check the documents. Add the specialist check only for cases above the agreed threshold. Tell me which checks actually ran.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | The same validated case information used by the earlier routing exercise. |
| What should the employee receive? | A list containing the required checklist result and, when applicable, the exposure-check result. |
| What should happen when it cannot be completed? | A check that was skipped must not be described as completed. A failed required check must remain visible. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Dynamic workflow | A workflow whose selected work can change according to input values while it runs. |
| Child node | A smaller operation scheduled by another operation through ADK. |
| Await | Pause this function until the requested asynchronous operation returns, allowing other scheduled work to run meanwhile. This does not automatically run all surrounding operations in parallel. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


A dynamic ADK node performs the required checklist check and conditionally runs one exposure check, returning their explicit results.

Module 17 selected a single destination. This module schedules a variable set of known checks. Module 19 will let a conversational coordinator consult advisory specialists.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Checklist always runs | Unconditional awaited child call | Every result contains documents. |
| Extra check only when required | Python if around ctx.run_node | The exact threshold runs one check; one cent above runs two. |
| Bound the work | Finite allowlisted children and workflow timeout | There is no model-generated function name or unbounded task list. |
| Keep execution visible to ADK | Use ctx.run_node for child work | Child outputs appear in the event stream. |

## Set up the supplied example

<Setup/>

From the repository root:

```bash
cd training/module18-dynamic-orchestration/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

`uv sync` creates an isolated `.venv` for this example. The lockfile fixes the resolved packages. Run commands from `example/` so Python can import the local `bank_case` package. The tests use synthetic data; they do not require Gemini credentials or a banking system.

```bash
uv run python run.py
```

This default run uses deterministic function nodes and the actual ADK runtime. Read the printed intermediate outputs as well as the final result. It does not contact a model or a cloud database.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Declares Python support and the pinned ADK dependency; uv.lock records the resolution. |
| `.env.example` | Lists configuration for optional live services, not credentials to commit. |
| `bank_case/agent.py` | Defines the lesson operations and native ADK composition; construction is separate from execution. |
| `bank_case/contracts.py` | Validates the synthetic case boundary and defines SAMPLE. |
| `runtime.py` | Creates a local app/session, consumes ADK events and prints observable output. |
| `run.py` | Parses the CLI request/options and starts the selected example. |


The complete source is in this module’s `example/` directory. Work in a copy when experimenting. The [solution](./lab-solution.md) reproduces the implementation so you can compare each step.

## Develop the solution before opening the complete code

Work in a practice copy of `example/` so the reference remains available. Use the existing dependency and runner setup; rebuild the lesson functions in `bank_case/agent.py` one checkpoint at a time. Predict each result before running it. You do not need to build a second agent framework or recreate the cloud SDK.

| Checkpoint | What you write or decide | Evidence before continuing |
| --- | --- | --- |
| Define the finite child set | List checklist and exposure; specify each result mapping. | No dynamic import or model-provided operation name is needed. |
| Implement the unconditional call | Create results and await the checklist child. | Every successful output contains documents. |
| Add the conditional call | Place the exposure call inside the amount if statement. | It does not run at the exact threshold. |
| Return and observe | Return case ID plus the collected results, then run both amount scenarios. | The actual child outputs explain the different result lengths. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Identify what varies

The number of checks varies, but the permitted checks do not. Write the allowlist—checklist and exposure—before designing a planner. The supplied amount controls selection; a user cannot submit a function name or import path.

### Step 2: Read the child functions

Each returns a small dictionary. `checklist_check` reads the supplied boolean. `exposure_check` returns a fixture signal because its caller already applied the threshold. Its result is not a balance lookup or an independent credit assessment.

### Step 3: Decorate the orchestrator

`@node(rerun_on_resume=True)` applies ADK execution behavior to the function immediately below it. The `ctx` parameter receives ADK Context. The `node_input` parameter receives the typed predecessor output. Do not confuse this workflow context with a tool’s injected ToolContext.

### Step 4: Build a fresh result list

`results = []` creates a per-call list. `model_dump()` produces a payload for children. `results.append(await ctx.run_node(...))` waits for the child result and then adds it. A module-level mutable list would mix evidence between requests.

### Step 5: Use Python control flow for selection

The `if` surrounds the exposure child call, so the child is not scheduled for amounts at or below the threshold. The two calls are sequential in this example. Writing async code does not make this loop automatically parallel.

### Step 6: Return both software output and a message

The returned Event contains the case ID and the list of checks. It also tells the learner that no credit decision occurred. The outer Workflow has one entry edge because the dynamic function owns internal scheduling.

### Step 7: Inspect the actual child work

Run the two threshold scenarios in the tests and compare check names. Add an optional read-only check in a practice copy, then justify the exact condition, output contract and maximum number of calls.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** “Always” places checklist outside the if. “Only above the threshold” puts exposure inside it. “A bounded list of checks” means the callables are developer-defined; no model-generated import or function name is accepted.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Compare child event outputs at 20,000,000 and 20,000,001 cents. Then add a print before the awaited child in a disposable resume experiment: treat re-entry as possible until actual event evidence establishes the path.

**Transfer to a changed customer requirement:** Before implementing resumability, write an interruption matrix: before child, after child, before external commit, after commit with lost response. Give each external write a destination-enforced idempotency key; do not claim resume verification from the ordinary lab run.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read the implementation in small pieces

### Validate the case snapshot

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

`SAMPLE` is a synthetic input, not a case lookup. In a customer solution, an authenticated adapter obtains these fields from the system of record. The strict schema protects shape; authorization and factual correctness require that adapter.

### Imports and definitions

```python
"""Schedule only the read-only checks required by this case."""

from google.adk.agents.context import Context
from google.adk.events import Event
from google.adk.workflow import Workflow, node
from .contracts import CaseRequest
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `checklist_check`

```python
def checklist_check(node_input: dict) -> dict:
    # Return only this check’s result so the orchestrator can name and combine completed work.
    return {"check": "documents", "complete": node_input["documents_complete"]}
```

The child receives the dumped dictionary, so `node_input["documents_complete"]` reads a required key. Its fresh result names the check and copies the boolean. A missing key raises rather than silently becoming false, but the parent normally supplies this key from the validated contract.

### Read `exposure_check`

```python
def exposure_check(node_input: dict) -> dict:
    # The parent schedules this child only after the amount rule requires specialist review.
    return {"check": "exposure", "requires_specialist": True}
```

The parent calls this child only after the high-amount condition passes. Therefore the fixture returns requires_specialist=true without repeating the comparison. The unused payload keeps the same child-call interface. A real exposure service would replace this fixture calculation and return its own authoritative evidence.

### Read `collect_required_checks`

```python
@node(rerun_on_resume=True)
async def collect_required_checks(ctx: Context, node_input: CaseRequest) -> Event:
    # Construct a fresh list per call; never retain another case's evidence.
    results = []
    payload = node_input.model_dump()
    results.append(await ctx.run_node(checklist_check, node_input=payload))
    if node_input.requested_cents > 20_000_000:
        results.append(await ctx.run_node(exposure_check, node_input=payload))
    return Event(
        output={"case_id": node_input.case_id, "checks": results},
        message="Required checks collected; no credit decision has been made.",
    )
```

The decorator supplies the resume setting required for dynamic child calls. The local list starts empty for every invocation. `await` completes the checklist child before append stores its result. The if statement determines whether the exposure child is called at all. The final Event returns the case and completed check list; it does not claim persistence of the local list across a process restart.

### Read `build_agent`

```python
def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return Workflow(
        name="dynamic_checks",
        input_schema=CaseRequest,
        timeout=30,
        edges=[("START", collect_required_checks)],
    )
```

There is only one declared entry edge because collect_required_checks owns the internal conditional sequence. `CaseRequest` still validates the entry data. Dynamic children remain ADK node executions because the parent uses ctx.run_node; calling arbitrary Python directly would not create that same node boundary.

### Explain the important expressions

| Expression | Meaning |
|---|---|
| `@node(...)` | Decorate a function with ADK node configuration |
| `async def ...` | Define a coroutine that can await asynchronous work |
| `ctx: Context` | Request the current workflow execution context |
| `await ctx.run_node(checklist_check, node_input=payload)` | Execute a known child through ADK and receive its output |
| `results.append(...)` | Add one completed result to this invocation’s list |
| `edges=[("START", collect_required_checks)]` | Start the dynamic scheduler; internal child choices are in Python |


## Understand the small runner

For a line-by-line explanation of the CLI, async execution, Content messages and events, use [Follow Python from the command to the first event](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#follow-python-from-the-command-to-the-first-event).

`runtime.py` is visible teaching code, not an orchestration framework. `App(name="bank_case", root_agent=agent)` names the application; `InMemoryRunner` supplies development session storage. The synthetic `analyst-demo` value is an identity fixture, not authentication. Production must derive identity from a verified caller.

The helper creates a session, serializes the supplied payload as JSON in a `types.Content` user message, and iterates `runner.run_async(...)`. `async for` consumes events as ADK produces them. `RunConfig(max_llm_calls=12)` bounds model calls; it is separate from the 60-second invocation deadline. A workflow may also have its own shorter timeout.

`Event.output` carries software-facing graph data. Content/message fields carry text a UI can show. The helper prints both when present. An intermediate specialist or node can emit content too, so a production UI must define which results are drafts, internal work or the user-visible final result. Do not treat every text event as the completed banking answer.

The `async with` block closes runner resources. This local helper creates a new in-memory session for each run and does not claim restart persistence. Module 13.5 and Module 22 teach persistent providers.

## Run changed requests and predict the result

From this module's `example/` directory, these commands change the synthetic input without editing source:

```bash
uv run python run.py --requested-cents 20000000 --documents-complete
uv run python run.py --requested-cents 20000001 --documents-complete
uv run python run.py --requested-cents 25000000
```

`argparse` reads command-line options. `type=int` converts the amount text into an integer; Pydantic still enforces the business range. `action="store_true"` makes `--documents-complete` set the flag to true; omitting it leaves false. `SAMPLE | {...}` creates a new dictionary with overridden fields and leaves the original fixture unchanged.

The first command schedules only documents; the second and third also schedule exposure. The third retains complete=false in the document result.

### Advanced customer variation

Extend the requirement to a bounded list of subsidiaries. Define authorization per subsidiary, maximum item count, concurrency budget and whether one failed child invalidates the whole pack.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

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

## Troubleshooting by symptom

| Symptom | Check |
| --- | --- |
| ModuleNotFoundError for bank_case | Run from this module’s example directory after uv sync. |
| ValidationError | Inspect the rejected field and type; do not disable validation to make the sample pass. |
| Missing GEMINI_MODEL | Use --env-file .env for live runs and set the required variable. |
| Authentication, model-access or region error | Verify the development identity, project permissions and endpoint support; a local unit test cannot prove them. |
| A timeout or missing required output | Inspect the failed operation. Do not substitute an approval or an empty success result. |
| Experimental/deprecation warning inside a dependency | Record the emitting package and version. Do not assume your example uses the deprecated API or hide the warning. |

## Transfer exercise

A second bank asks for the same capability with different document types, review thresholds and case identifiers. Before editing code, rewrite the requirement table and name the authoritative sources. Change the contract and rule tests together, then explain which orchestration pattern remains useful and which assumptions must change.

Hand over your decision table, readable diagram, working example, negative-test evidence and live-validation plan. A learner has understood the pattern when they can explain a failure path without copying the solution.

## Official sources

- [Dynamic workflows](https://adk.dev/graphs/dynamic/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Resume agents](https://adk.dev/runtime/resume/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
