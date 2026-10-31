---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 16: Static Orchestration: Collecting Independent Evidence

**What you are practising:** Static workflows, fan-out and joins in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

Before reviewing a case, a bank analyst needs two pieces of information: whether the documents are complete and whether the requested amount requires specialist review under the fictional exercise rule. Neither check needs the other’s answer.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Do both checks every time. Show me the combined result only after both finish. Make sure both results belong to the same case.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A case ID, a document-complete flag and the requested amount in the exercise’s integer units. |
| What should the employee receive? | One result containing both completed checks, with their source labels. |
| What should happen when it cannot be completed? | A failed check or mismatched case ID must not become a complete-looking result. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Orchestration | The code that decides which operations run and in what order. |
| Fan-out | Starting separate pieces of work from the same input. |
| Join | Waiting for the required results and collecting them for the next operation. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


An ADK Workflow schedules two checks, joins their named results, and produces a synthetic evidence pack.

Module 15 separated roles. This module makes required collection explicit. Module 17 will use the collected facts to select the next review step.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Run both checks for every request | Static fan-out from START | The completed pack contains both results. |
| Combine only matching cases | Compare case IDs at the join consumer | Mismatched evidence raises an error. |
| Use exact money and explicit booleans | Strict Pydantic contract; integer cents | Strings, floats and boolean amounts are rejected. |
| Do not turn collection into approval | Result describes evidence and required review | The output makes no credit decision. |

## Set up the supplied example

<Setup/>

From the repository root:

```bash
cd training/module16-static-orchestration/example
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
| Describe each output | Write the keys for document and exposure evidence before coding. | Both identify the same case and include their fixture source. |
| Implement one check at a time | Write each function and predict its result for SAMPLE. | The amount comparison uses cents and a strict greater-than rule. |
| Draw and construct the join | Connect fan-out, JoinNode and combine with the same function objects. | The CLI trace contains both named outputs before the pack. |
| Break consistency intentionally | Use the supplied mismatched-ID test and explain its failure. | No successful pack is returned for mixed case IDs. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Write the dependency sentence

Say it out loud: both checks need the snapshot; the pack needs both checks. Draw that sentence before naming an ADK class. If one check needed the other’s result, it would not belong in this fan-out.

### Step 2: Read the input contract

`CaseRequest(BaseModel)` defines a validated object. `Literal["CASE-001"]` restricts this fixture to one case. `strict=True` rejects convenient but dangerous coercions such as `"yes"` to a boolean. `extra="forbid"` rejects unexpected fields. `Field(ge=1, le=...)` bounds the amount. These validations enforce shape, not caller authorization.

### Step 3: Implement the two pure checks

Each function accepts `node_input` and returns a new dictionary. Attribute access such as `node_input.case_id` reads a validated model field. The threshold is a fictional review-routing rule. The source strings identify local fixtures, not verified external records.

### Step 4: Wire the fan-out and join

An outer list holds graph edges. `("START", (document_check, exposure_check))` has a tuple of destinations and starts both branches. `((document_check, exposure_check), joined)` feeds their outputs into the same named join. Passing a function object without parentheses registers work; writing `document_check(...)` would execute it immediately.

### Step 5: Combine deliberately

Look up each result by its node name rather than assuming which branch finished first. Compare IDs. Raise `ValueError` on mismatch so there is no apparently complete evidence pack. Return `Event(output=..., message=...)`: the output feeds software; the message is visible to a person.

### Step 6: Run and inspect intermediate outputs

The CLI prints each nonempty node output, including the join map. Find both keys before looking at the final pack. Change the amount to exactly 20,000,000 cents and then 20,000,001; only the latter requires the fictional specialist review.

### Step 7: Plan the real adapters

Replace the fixture document function with the authorized Firestore-backed service from Module 13.5. Read exposure from the bank’s ledger API, not from a user claim. Keep the same return contract and add versions/timestamps. Async network functions should await the official client; do not put blocking requests inside an async function and assume it is concurrent.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** “Both” creates two required operations. “Independent” permits fan-out. “Only after” creates a join. “Same case” creates the comparison in combine. Those four phrases explain the graph and the guard before any SDK import is chosen.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Run each pure check on SAMPLE, write the expected join map, then run the full workflow. In a practice copy make one check raise TimeoutError: explain why there must be no complete pack.

**Transfer to a changed customer requirement:** Compare graph output passing with template SequentialAgent/ParallelAgent composition. Templates are appropriate for fixed agent arrangements; the graph makes these function-node inputs and named joins explicit.

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
"""An explicit fan-out and join over a synthetic case snapshot."""

from google.adk.events import Event
from google.adk.workflow import JoinNode, Workflow
from .contracts import CaseRequest
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `document_check`

```python
def document_check(node_input: CaseRequest) -> dict:
    # The checklist is required evidence, so copy its value and case identity into a separate result.
    return {
        "case_id": node_input.case_id,
        "documents_complete": node_input.documents_complete,
        "source": "training-fixture:document-checklist-v1",
    }
```

`node_input` is already a CaseRequest because the workflow validates it at entry. Attribute access reads the case ID and boolean from that model. The returned dictionary copies those selected fields and adds a fixture source identifier. It has no Firestore client and performs no network read.

### Read `exposure_check`

```python
def exposure_check(node_input: CaseRequest) -> dict:
    # A teaching threshold, not a bank policy or an approval limit.
    # The customer rule uses a strict threshold; equality must not enter specialist review.
    return {
        "case_id": node_input.case_id,
        "specialist_review": node_input.requested_cents > 20_000_000,
        "source": "training-fixture:review-threshold-v1",
    }
```

The expression after `specialist_review` evaluates to a Python boolean. Numeric underscores only improve readability: 20_000_000 means twenty million cents. The operator is `>`, so equality does not request specialist review. This is routing against a fictional threshold, not calculation of a borrower's actual credit exposure.

### Read `combine`

```python
def combine(node_input: dict) -> Event:
    # JoinNode keys are the predecessor node names, not completion order.
    # Both branches must refer to the same case before their evidence can form one pack.
    documents = node_input["document_check"]
    exposure = node_input["exposure_check"]
    if documents["case_id"] != exposure["case_id"]:
        raise ValueError("Cannot combine evidence from different cases")
    result = {"case_id": documents["case_id"], "evidence": [documents, exposure]}
    return Event(
        output=result, message="Evidence collected; analyst review is required."
    )
```

The predecessor names are keys in JoinNode's output map. Read each required entry, then compare their case IDs before constructing the pack. `raise ValueError` stops the success path for mixed cases. The evidence list keeps both original result mappings. `Event.output` makes that pack available to software; `message` gives a person an explanation.

### Read `build_agent`

```python
def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    joined = JoinNode(name="evidence_join")
    return Workflow(
        name="evidence_pipeline",
        input_schema=CaseRequest,
        timeout=30,
        edges=[
            ("START", (document_check, exposure_check)),
            ((document_check, exposure_check), joined),
            (joined, combine),
        ],
    )
```

Construct one JoinNode and reuse that same object as destination and source. The first edge fans out to two function objects. The second feeds the two predecessors into the join. The third waits for the join output before combine runs. `input_schema` supplies validation and typed input; `timeout` bounds workflow time. Construction itself executes neither check.

### Explain the important expressions

| Code | How to read it |
|---|---|
| `def ... (node_input: CaseRequest) -> dict` | A function taking one typed input and returning a mapping |
| `requested_cents > 20_000_000` | A strict greater-than comparison; underscores improve numeric readability |
| `JoinNode(name="evidence_join")` | Construct one synchronization node and reuse that object in edges |
| `node_input["document_check"]` | Read a required result by its stable predecessor name |
| `raise ValueError(...)` | Stop producing a successful pack when evidence is inconsistent |
| `timeout=30` | Bound workflow elapsed time; it is not a rollback mechanism |


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

The exposure result changes from false to true across the first two commands. The third command returns an incomplete document result. Both branches still run each time.

### Advanced customer variation

Design a partial-result policy and a consistency rule for two real services. Decide whether the pack can be displayed, routed or only marked incomplete when one source is unavailable.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

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

- [Graph routes and joins](https://adk.dev/graphs/routes/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Supported workflow choices](https://adk.dev/workflows/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
