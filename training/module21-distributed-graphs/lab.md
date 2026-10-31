---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 21: Distributed Graphs: A2A Service Boundaries

**What you are practising:** Remote agents and the A2A protocol in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

A separate document-operations team runs the checklist service. That team needs to update its service independently. The review assistant should call the service instead of keeping a copy of the team’s implementation.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Let our assistant ask the document team for the checklist result. If their service cannot be reached, tell the analyst that the check could not be completed.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A small request for the remote checklist capability. |
| What should the employee receive? | A response from the separate service that the local application can inspect. |
| What should happen when it cannot be completed? | A timeout or an unreachable service must not be reported as a completed check. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| A2A | Agent-to-Agent: a protocol for applications to communicate with agent services. |
| Agent card | A description of a service’s capabilities and connection details; it is not an access credential. |
| Remote | Running in another process or service, reached across a network. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


A loopback-only A2A server exposes a deterministic checklist workflow. A RemoteA2aAgent client discovers its card and submits a synthetic request.

Module 20 bounded local iterative work. This module introduces a remote ownership boundary. Module 21.5 asks you to justify the simplest architecture for the complete case.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Separate deployable ownership | Server and client are separate processes | The client depends on the endpoint contract, not a Python function import. |
| Advertise capabilities | ADK to_a2a creates the agent-card surface | The client resolves the fixed card URL. |
| Minimize transmitted data | Fresh local session containing only the synthetic snapshot | No existing banking conversation is attached. |
| Bound network work | Remote timeout and outer invocation deadline | Unavailable service does not become a successful check. |
| Make production identity explicit | Authenticated service endpoint and verified caller context | The loopback demo is not presented as production authentication. |

## Set up the supplied example

<Setup/>

From the repository root:

```bash
cd training/module21-distributed-graphs/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

`uv sync` creates an isolated `.venv` for this example. The lockfile fixes the resolved packages. Run commands from `example/` so Python can import the local `bank_case` package. The tests use synthetic data; they do not require Gemini credentials or a banking system.

Start the local server in terminal A:

```bash
uv run uvicorn bank_case.server:app --host 127.0.0.1 --port 8001
```

In terminal B, change to the same example directory, inspect discovery, then call it:

```bash
curl --fail http://127.0.0.1:8001/.well-known/agent-card.json
uv run python run.py
uv run python check_transport.py
```

The response identifies CASE-001 and the synthetic checklist status, with no credit approval. The separate transport check asserts this deterministic response through a real A2A round trip. The trace printer can show the same text in more than one protocol event; it is displaying events, not deduplicating a chat transcript. Stop terminal A with Ctrl+C. The server binds only to loopback and has no production authentication.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Declares Python support and the pinned ADK dependency; uv.lock records the resolution. |
| `.env.example` | Lists configuration for optional live services, not credentials to commit. |
| `bank_case/agent.py` | Defines the lesson operations and native ADK composition; construction is separate from execution. |
| `bank_case/contracts.py` | Validates the synthetic case boundary and defines SAMPLE. |
| `bank_case/server.py` | Exposes the separate checklist workflow through the native A2A adapter. |
| `runtime.py` | Creates a local app/session, consumes ADK events and prints observable output. |
| `run.py` | Parses the CLI request/options and starts the selected example. |
| `check_transport.py` | Asserts the deterministic response through a running loopback A2A server. |


The complete source is in this module’s `example/` directory. Work in a copy when experimenting. The [solution](./lab-solution.md) reproduces the implementation so you can compare each step.

## Develop the solution before opening the complete code

Work in a practice copy of `example/` so the reference remains available. Use the existing dependency and runner setup; rebuild the lesson functions in `bank_case/agent.py` one checkpoint at a time. Predict each result before running it. You do not need to build a second agent framework or recreate the cloud SDK.

| Checkpoint | What you write or decide | Evidence before continuing |
| --- | --- | --- |
| Specify the remote contract | List the allowed case fields and deterministic response. | You can reject an extra or malformed field before execution. |
| Build the server application | Compose review_checklist as a Workflow and expose it with to_a2a. | Importing the application works without a model or banking API. |
| Build the fixed proxy | Use a developer-controlled loopback card URL and explicit timeout. | No user or model can substitute an arbitrary destination. |
| Exercise the boundary | Run server, client and check_transport.py in separate terminals as documented. | A real protocol response is observed, and stopping the server produces visible failure. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Identify the reason for distribution

The team needs separate ownership and release cadence. If those needs do not exist, a local function or agent is simpler. A2A adds network, versioning, identity and failure responsibilities; it is not a prerequisite for multi-agent systems.

### Step 2: Read the server workflow

`review_checklist` receives a validated CaseRequest and returns only the case ID, checklist flag and fixture source. `Event.message` produces user-visible content; `Event.output` is the structured workflow value. The server uses ordinary ADK nodes, not a hand-written JSON-RPC implementation.

### Step 3: Expose with to_a2a

`to_a2a(specialist, host="127.0.0.1", port=8001)` builds an ASGI application. Uvicorn serves it. The host and port describe the local endpoint. Both binding and advertised address must match; 0.0.0.0 is a listening wildcard, not a client destination.

### Step 4: Read the client configuration

The card URL is a developer-controlled literal. `timeout=10` bounds HTTP operations and the outer runtime bounds the invocation. The proxy is constructed without contacting the server; discovery happens during execution. No API key is embedded.

### Step 5: Run server and client in separate terminals

Start Uvicorn first, fetch the agent card, then run the client. A correct test must observe an actual response, not merely that the proxy object constructed. Stop the server with Ctrl+C when finished.

### Step 6: Inspect the failure case

Stop the server and rerun the client. It must fail visibly rather than report an all-clear checklist. The default adapter’s in-memory sessions/tasks are a development convenience; they do not prove durable remote task recovery.

### Step 7: Design the production trust boundary

Choose an authenticated Google Cloud endpoint, service-to-service credentials, a case authorization contract, a durable task/session strategy and an allowlisted destination. Validate every returned business field before using it in Module 17’s router.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** Independent ownership motivates a service interface. Reusing a Python function would not meet independent release requirements. Use the official adapter instead of hand-writing an A2A transport; keep business authorization in the remote capability.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Run the server and client in separate terminals. Save the agent card and returned events. Stop the server and retry: distinguish discovery failure from a failure after work starts.

**Transfer to a changed customer requirement:** Produce a correlation table from one actual request and design a response-loss scenario. Specify which operations are safe to retry and which require reconciliation.

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
"""A fixed, developer-controlled endpoint; never accept a URL from the model."""

from google.adk.a2a.agent import RemoteA2aAgent
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `build_agent`

```python
def build_agent():
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    return RemoteA2aAgent(
        name="remote_checklist_client",
        agent_card="http://127.0.0.1:8001/.well-known/agent-card.json",
        description="Read-only synthetic checklist specialist on this machine.",
        timeout=10,
        use_legacy=False,
    )
```

Construct a remote proxy with a developer-owned discovery URL. The description explains the narrow service. The HTTP timeout and current ADK protocol-path option are explicit. Proxy construction is configuration; network discovery and invocation occur when Runner executes it. The server implementation lives in a different module/process.

### Explain the important expressions

| Expression | Meaning |
|---|---|
| `app = to_a2a(...)` | Build an ASGI app from a native ADK agent/workflow |
| `uvicorn bank_case.server:app` | Import the module and serve its `app` object |
| `RemoteA2aAgent(...)` | Build a client-side proxy, not a local copy of the specialist |
| `agent_card="http://127.0.0.1:8001/..."` | Fixed discovery URL for this local lab |
| `timeout=10` | HTTP timeout; does not roll back work already started remotely |
| `use_legacy=False` | Select the current ADK protocol implementation path |

### The remote server is a separate implementation

```python
"""Local A2A specialist. No authentication: bind only to loopback."""

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.events import Event
from google.adk.workflow import Workflow
from .contracts import CaseRequest


def review_checklist(node_input: CaseRequest) -> Event:
    # The remote service validates its own input; a network caller is not automatically trusted.
    result = {
        "case_id": node_input.case_id,
        "documents_complete": node_input.documents_complete,
        "source": "training-fixture:checklist-v1",
    }
    return Event(
        output=result,
        message=(
            f"{node_input.case_id}: checklist complete={node_input.documents_complete}. "
            "Synthetic evidence only; no credit approval."
        ),
    )


specialist = Workflow(
    name="remote_checklist",
    input_schema=CaseRequest,
    edges=[("START", review_checklist)],
    timeout=20,
)
app = to_a2a(specialist, host="127.0.0.1", port=8001)
```

The client never imports this function. Uvicorn imports `app`; requests cross A2A before the server workflow validates its input. `to_a2a` is the native protocol adapter. Its default development stores and unauthenticated loopback binding are not a production deployment design.

## Understand the small runner

For a line-by-line explanation of the CLI, async execution, Content messages and events, use [Follow Python from the command to the first event](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#follow-python-from-the-command-to-the-first-event).

`runtime.py` is visible teaching code, not an orchestration framework. `App(name="bank_case", root_agent=agent)` names the application; `InMemoryRunner` supplies development session storage. The synthetic `analyst-demo` value is an identity fixture, not authentication. Production must derive identity from a verified caller.

The helper creates a session, serializes the supplied payload as JSON in a `types.Content` user message, and iterates `runner.run_async(...)`. `async for` consumes events as ADK produces them. `RunConfig(max_llm_calls=12)` bounds model calls; it is separate from the 60-second invocation deadline. A workflow may also have its own shorter timeout.

`Event.output` carries software-facing graph data. Content/message fields carry text a UI can show. The helper prints both when present. An intermediate specialist or node can emit content too, so a production UI must define which results are drafts, internal work or the user-visible final result. Do not treat every text event as the completed banking answer.

The `async with` block closes runner resources. This local helper creates a new in-memory session for each run and does not claim restart persistence. Module 13.5 and Module 22 teach persistent providers.

## Run changed requests and predict the result

Start the server and run `uv run python check_transport.py` using the commands above. Then stop the server and run the client again. Record the discovery/invocation failure separately from an invalid request. A constructed proxy or a fetched card alone is not a passed business response.

### Advanced customer variation

Write a versioned remote-response contract, destination allowlist and timeout/reconciliation policy. Explain how verified user identity reaches the remote case authorization layer without entering a model-visible prompt.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Inspect the card before running the client | Check the advertised endpoint and capabilities against the local server. |
| Stop the server before a call | The call fails; no successful evidence result is fabricated. |
| Send an unknown case or string boolean | The strict server-side schema must reject the request. |
| Plan a side-effecting remote task | Explain why retries require idempotency and why an HTTP timeout leaves outcome uncertainty. |

### Local evidence

4 offline contract tests and 1 real loopback A2A transport test passed. The client received the deterministic checklist response through the local Uvicorn server. No model call or cloud deployment was involved; production authentication and remote recovery remain untested.

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

- [Expose an ADK agent through A2A](https://adk.dev/a2a/quickstart-exposing/)
- [Consume a remote agent](https://adk.dev/a2a/quickstart-consuming/)
- [Cloud Run service authentication](https://docs.cloud.google.com/run/docs/authenticating/service-to-service)
- [Official A2A SDK](https://github.com/a2aproject/a2a-python)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
