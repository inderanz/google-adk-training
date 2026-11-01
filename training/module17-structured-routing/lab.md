---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 17: Structured Routing: Turning Bank Rules into Edges

**What you are practising:** Structured routing and explicit control signals in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

The bank analyst has the document status and requested amount. The next task is to identify what should happen next. In this fictional exercise, missing documents must be dealt with before the amount-based review rule is considered.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> If documents are missing, tell me to collect them first. Otherwise, tell me whether the case needs specialist review or standard review. Do not describe either route as loan approval.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A validated case snapshot: the case ID, document status and requested amount. |
| What should the employee receive? | Exactly one next step: collect documents, specialist review or standard review. |
| What should happen when it cannot be completed? | Malformed input is rejected. An unexpected routing label goes to manual checking. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Route | The next operation selected by the application. |
| Precedence | Which rule is checked first when more than one could apply. |
| Structured output | Data in named fields, so code does not have to guess its meaning from a sentence. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Exactly one route handler produces a next-step instruction from a validated synthetic snapshot.

Module 16 collected evidence. This module chooses a step from fixed rules. Module 18 will schedule a varying set of checks without hiding business logic inside a prompt.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Missing documents take precedence | First branch in choose_route | A high amount with missing documents still goes to document collection. |
| Define the threshold precisely | Integer cents and > 20_000_000 | The exact threshold stays in standard review; one cent above goes to specialist review. |
| Handle unexpected routing values | Explicit __DEFAULT__ edge | Unsupported routes lead to manual triage. |
| Reject malformed input before routing | Workflow input_schema | Unknown cases, booleans as money and extra approval fields are rejected. |

## Set up the supplied example

<Setup/>

From the repository root:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
cd training/module17-structured-routing/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

`uv sync` creates an isolated `.venv` for this example. The lockfile fixes the resolved packages. Run commands from `example/` so Python can import the local `bank_case` package. The tests use synthetic data; they do not require Gemini credentials or a banking system.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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
| Write four example cases | Specify incomplete/low, incomplete/high, complete/exact threshold and complete/above. | You can predict all four destinations before coding. |
| Implement the ordered rule | Write if/elif/else and return an Event with payload and route. | The first condition enforces missing-document precedence. |
| Write handlers and the mapping | Give each handler a next-step result and map matching labels. | Every rule label has a destination and the default is explicit. |
| Run the boundary commands | Use the new CLI flags below rather than editing the fixture. | Observed outputs match your four predictions. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Write a decision table

Use the four rows above. Work out the result for an incomplete high-value case before coding. This catches the common mistake of checking the amount first and allowing missing evidence to bypass collection.

### Step 2: Validate the boundary

Read `CaseRequest` from Module 16 again. The test passes invalid values directly to Pydantic to demonstrate rejection. The fixture CLI supplies a dictionary; a production endpoint must obtain the actual status and amount from trusted services.

### Step 3: Implement choose_route

`if`, `elif` and `else` form one ordered decision chain. Only one assignment to `route` happens. `node_input.model_dump()` converts the validated model into a JSON-compatible dictionary. `Event(..., route=route)` tells ADK which edge to take.

### Step 4: Keep handlers narrow

Each handler reads the case ID and returns a `next_step` plus a human-readable message. There is no queue API here: “specialist_review” is a proposed next step in the demo. In production, a queue write needs its own authorized, idempotent service operation.

### Step 5: Connect the route map

The route dictionary contains function objects as values. Quoted route strings are business labels; unquoted names such as `request_documents` refer to Python functions. The special default key provides a fall-through destination for an unmatched routing label.

### Step 6: Exercise boundaries through ADK

The tests invoke the real graph for incomplete/low, incomplete/high, complete/exact threshold and complete/one-cent-above cases. Inspect the final `next_step`. Test the helper and runtime wiring: checking only the Python comparison would miss a misspelled edge label.

### Step 7: Add a policy safely

For practice, add a training rule requiring manual triage above a second threshold. Update the requirement table, route function, mapping, diagram explanation and boundary tests together. Explain its precedence relative to missing documents.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** Translate “missing documents first” into the first if. Translate “above” into >, including a boundary case at equality. The fallback represents an unrecognized control label, not permission to guess the bank policy.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Before execution, fill four rows: incomplete/high; complete/high; complete/equal; complete/low. Predict label and handler. Then intentionally misspell one emitted label and inspect the default outcome.

**Transfer to a changed customer requirement:** Add a policy version and effective date to an authoritative input contract. Show how a change from above to at-least affects both the condition and its boundary test.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read the implementation in small pieces

### Validate the case snapshot

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

`SAMPLE` is a synthetic input, not a case lookup. In a customer solution, an authenticated adapter obtains these fields from the system of record. The strict schema protects shape; authorization and factual correctness require that adapter.

### Imports and definitions

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
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `choose_route`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def choose_route(node_input: CaseRequest) -> Event:
    # Missing evidence takes priority over amount, so the order of these conditions is business logic.
    if not node_input.documents_complete:
        route = "documents"
    elif node_input.requested_cents > 20_000_000:
        route = "specialist"
    else:
        route = "standard"
    return Event(output=node_input.model_dump(), route=route)
```

Python evaluates the conditions from top to bottom. When documents are missing, the first assignment wins and neither later branch runs. Otherwise it compares cents and selects specialist or standard. `model_dump()` produces the plain dictionary that the handler will receive. `route=route` means the left name is the Event field and the right name is this function's local variable.

### Read `request_documents`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def request_documents(node_input: dict) -> Event:
    # Return the selected next step as data; this function does not send a real document request.
    return Event(
        output={"case_id": node_input["case_id"], "next_step": "collect_documents"},
        message="Collect the missing checklist evidence before review.",
    )
```

This handler receives a plain dictionary, so it uses square-bracket key lookup rather than model attribute access. It returns the canonical case ID and the action label collect_documents. The message explains that label to the analyst. It does not contact the borrower or write a request into a case system.

### Read `specialist_review`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def specialist_review(node_input: dict) -> Event:
    # Routing identifies the review owner; it does not approve the requested credit.
    return Event(
        output={"case_id": node_input["case_id"], "next_step": "specialist_review"},
        message="Send the complete evidence pack to a specialist analyst.",
    )
```

The router has already applied the rule. This handler only packages the next-step label specialist_review and a readable explanation. There is no hidden second model decision or approval operation here. A real queue submission would require a separate service call and an idempotency contract.

### Read `standard_review`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def standard_review(node_input: dict) -> Event:
    # The remaining valid cases enter standard review; they still require a human decision.
    return Event(
        output={"case_id": node_input["case_id"], "next_step": "standard_review"},
        message="Send the complete evidence pack to a standard analyst queue.",
    )
```

The normal handler returns standard_review, which still means an analyst queue, not automatic approval. Keeping the label machine-readable lets a UI or later operation interpret it without parsing prose. The current example returns data only.

### Read `unsupported_route`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def unsupported_route(node_input: dict) -> Event:
    # Unexpected control labels need an explicit manual outcome instead of an invented default approval.
    return Event(
        output={"case_id": node_input["case_id"], "next_step": "manual_triage"},
        message="An unsupported route requires manual triage.",
    )
```

This handler preserves the case identifier but chooses manual_triage. It is deliberately distinguishable from the standard path. The default mapping invokes it for an unmatched routing signal; an invalid input schema fails earlier and does not reach this handler.

### Read `build_agent`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return Workflow(
        name="case_router",
        input_schema=CaseRequest,
        timeout=30,
        edges=[
            ("START", choose_route),
            (
                choose_route,
                {
                    "documents": request_documents,
                    "specialist": specialist_review,
                    "standard": standard_review,
                    "__DEFAULT__": unsupported_route,
                },
            ),
        ],
    )
```

The first edge runs choose_route. The next edge contains a dictionary mapping emitted labels to function objects. Quoted strings are route keys; unquoted handler names reference code. __DEFAULT__ is the fallback key. No outgoing edges are needed for the handlers because their results terminate their branches.

### Explain the important expressions

| Expression | Meaning |
|---|---|
| `if not node_input.documents_complete` | The first condition is true when the validated boolean is false |
| `elif ... > ...` | Test this condition only if the previous condition was false |
| `model_dump()` | Convert a Pydantic model into plain data for downstream nodes |
| `Event(output=..., route=...)` | Carry data separately from the routing decision |
| `(choose_route, {...})` | Map the emitting node’s route labels to destinations |
| `"__DEFAULT__": unsupported_route` | Handle an unmatched label; malformed input still fails validation earlier |


## Understand the small runner

For a line-by-line explanation of the CLI, async execution, Content messages and events, use [Follow Python from the command to the first event](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#follow-python-from-the-command-to-the-first-event).

`runtime.py` is visible teaching code, not an orchestration framework. `App(name="bank_case", root_agent=agent)` names the application; `InMemoryRunner` supplies development session storage. The synthetic `analyst-demo` value is an identity fixture, not authentication. Production must derive identity from a verified caller.

The helper creates a session, serializes the supplied payload as JSON in a `types.Content` user message, and iterates `runner.run_async(...)`. `async for` consumes events as ADK produces them. `RunConfig(max_llm_calls=12)` bounds model calls; it is separate from the 60-second invocation deadline. A workflow may also have its own shorter timeout.

`Event.output` carries software-facing graph data. Content/message fields carry text a UI can show. The helper prints both when present. An intermediate specialist or node can emit content too, so a production UI must define which results are drafts, internal work or the user-visible final result. Do not treat every text event as the completed banking answer.

The `async with` block closes runner resources. This local helper creates a new in-memory session for each run and does not claim restart persistence. Module 13.5 and Module 22 teach persistent providers.

## Run changed requests and predict the result

From this module's `example/` directory, these commands change the synthetic input without editing source:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python run.py --requested-cents 20000000 --documents-complete
uv run python run.py --requested-cents 20000001 --documents-complete
uv run python run.py --requested-cents 25000000
```

`argparse` reads command-line options. `type=int` converts the amount text into an integer; Pydantic still enforces the business range. `action="store_true"` makes `--documents-complete` set the flag to true; omitting it leaves false. `SAMPLE | {...}` creates a new dictionary with overridden fields and leaves the original fixture unchanged.

The next steps are standard_review, specialist_review and collect_documents respectively. The third demonstrates that missing documents outrank the amount condition.

### Advanced customer variation

Add a policy-version field and propose migration behavior for sessions started under an older rule set. Explain how the audit record identifies the actual applied rule.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

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

