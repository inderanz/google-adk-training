---
sidebar_position: 2
title: "Guided Banking Lab"
---

# Lab 21.5: MAS Knowledge Milestone: Defend a Banking Architecture

**What you are practising:** Choosing and composing ADK patterns in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

The bank now asks you to put the earlier ideas together and explain your design. The analyst still wants reliable preparation: collect the required facts, identify the next step and explain it clearly.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Show us the smallest application that completes the required checks and explains the next step. Tell us which parts are working examples and which still need a real bank-system connection.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A customer requirement list and the case information available from agreed sources. |
| What should the employee receive? | A working preparation example plus an explanation of why each operation and service is needed. |
| What should happen when it cannot be completed? | A missing source connection must remain an open task; adding more agents does not supply the missing data. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Architecture | How the application’s parts fit together and share responsibilities. |
| Data contract | The fields, types and meanings agreed between two operations. |
| Acceptance evidence | Observed results showing whether an agreed requirement was met. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


An executable minimum combines static evidence collection with deterministic routing. The learner designs optional advisory, revision and remote extensions using an architecture decision record.

Modules 15–21 introduced choices. This milestone combines and justifies them. Module 22 adds personalized continuity while keeping preferences separate from authoritative case facts.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Collect two required checks | Static fan-out plus join | Both named check outputs exist before routing. |
| Choose the next step by facts | Ordered route function | Incomplete evidence has precedence over amount. |
| Keep optional complexity justified | ADR compares alternatives | Each added agent/service answers a specific requirement. |
| Show verification limits | Separate local control tests and live evaluations | No claim of production readiness rests on a fixture run alone. |

## Set up the supplied example

From the repository root:

```bash
cd training/module21_5-mas-knowledge-milestone/example
uv sync --locked --python 3.14
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
| Write the architecture decision | Compare exact workflow, flexible team and remote service alternatives against the brief. | Every chosen boundary has a business reason. |
| Compose required work | Build document/exposure branches and a named join. | Both results precede routing in the trace. |
| Preserve the rule | Apply missing-document precedence and render the returned next step. | The four decision-table scenarios pass. |
| Specify one real integration | Choose checklist, profile or model explanation and name its authorized input/output contract. | You identify both reuse from earlier modules and genuinely missing bank fields. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Restate the bank problem without SDK names

Describe who uses the system, what successful preparation looks like and what it must not claim. If your first sentence names Workflow or A2A, return to the business requirement.

### Step 2: Build a traceability table

Assign each requirement an owner, input, output, failure outcome and check. For “both checks,” name the two outputs and what happens when one fails. For “understandable,” define evaluation examples with a bank analyst.

### Step 3: Run the minimum architecture

The sample reuses the ideas from Modules 16 and 17 in one file. The two function outputs reach a JoinNode; decide applies the rules; explain emits the result. No extra framework is introduced.

### Step 4: Read the composition carefully

The combiner verifies matching case IDs. The ordered conditions preserve document precedence. The route mapping sends all supported next-step labels to the same renderer. Routing remains explicit even though the final explanatory function is shared.

### Step 5: Choose one justified extension

Add a model-generated explanation, a remote checklist service or a bounded memo revision in a practice branch. Write the requirement that needs it. Define the new input/output contract and explain its failure effect before implementation.

### Step 6: Review like a bank FDE

Present the English requirement, your decision table, graph, synthetic demonstration, test evidence and untested production assumptions. Ask the reviewer to challenge the authorization boundary, unknown outcomes and source freshness.

### Step 7: Complete the assessment

Use the rubric in this module’s playbook. A solution that claims a fixture flag is an authoritative bank record or that a model can approve credit without an authorized operation cannot pass, even if its graph executes.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** Start with what the bank must guarantee. Add a model for language work, a service boundary for independent ownership and persistence for required continuity. Each addition needs a specific requirement and a failure contract.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Present one traceability row per requirement with the exact function, expected output and negative test. A requirement without an implementation or evidence is explicitly open.

**Transfer to a changed customer requirement:** Change the customer brief to require a sanctioned ledger amount. Identify the missing adapter and entitlement contract before changing the route; a new fixture field does not complete that integration.

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
"""An executable architecture decision: fixed checks, explicit route, no LLM."""
from google.adk.events import Event
from google.adk.workflow import JoinNode, Workflow
from .contracts import CaseRequest
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `documents`

```python
def documents(node_input: CaseRequest) -> dict:
    # Preserve case identity so the downstream join can reject mixed records.
    return {"complete": node_input.documents_complete, "case_id": node_input.case_id}
```

Read the validated checklist flag and case ID and return a small mapping. The key is complete here because this module defines its own internal branch contract; it is not a live database column. No external fact is fetched.

### Read `exposure`

```python
def exposure(node_input: CaseRequest) -> dict:
    # Compute the fictional review requirement in exact code rather than asking a model to guess it.
    return {"specialist": node_input.requested_cents > 20_000_000,
            "case_id": node_input.case_id}
```

Compare the requested cents with the fictional threshold and return that boolean with the case ID. The separate branch allows the join and rule precedence to remain visible. It is a read-only fixture operation.

### Read `decide`

```python
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
```

Read both named branch outputs, reject different case IDs, then apply missing-document precedence before amount. `destination` holds a machine-readable next step. The Event carries that value in output and uses the same string as its route, connecting the business result to explicit graph control.

### Read `explain`

```python
def explain(node_input: dict) -> Event:
    # Expose the selected next step without changing the rule or claiming a credit decision.
    return Event(output=node_input,
                 message=f"Next step: {node_input['next_step']}. No credit approval issued.")
```

Read the chosen next step and insert it into a Python f-string for display. The returned output is the same mapping, so rendering does not change the business result. There is no model interpretation between the rule and this baseline explanation.

### Read `build_agent`

```python
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

Compose the previously learned fan-out and join, then call decide and route supported labels to explain. Multiple route keys can point to the same renderer while preserving explicit allowed control signals. The function constructs the graph; run.py supplies the case and starts execution.

### Explain the important expressions

| Function | Responsibility |
|---|---|
| `documents` | Produce the synthetic checklist result |
| `exposure` | Apply the fictional amount threshold |
| `decide` | Verify case alignment and select the ordered next step |
| `explain` | Render the result without changing its meaning |
| `build_agent` | Compose those responsibilities using native graph edges |


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

Both evidence branches run, then the next steps are standard_review, specialist_review and collect_documents. Explain why the route differs even though the graph shape stays the same.

### Advanced customer variation

Present a change-impact review for a new policy version, new data owner and unavailable model. Show which contracts and tests change and which architecture boundaries stay stable.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

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

- [ADK workflow options](https://adk.dev/workflows/)
- [Graph routes](https://adk.dev/graphs/routes/)
- [ADK safety and security](https://adk.dev/safety/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->

## Continue with the integrated customer exercise

The [integrated banking lab](../module26-callbacks/integrated-lab.md) connects the authorized Firestore read, deterministic next step, versioned artifacts, Gemini explanation, evaluation, logging and Model Armor in one App. Complete its live and deployed checkpoints after the isolated lesson. Its scope excludes an unimplemented ledger adapter and credit approval.
