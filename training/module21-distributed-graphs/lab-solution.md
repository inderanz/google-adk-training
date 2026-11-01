---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 21 solution: Distributed Graphs: A2A Service Boundaries

A loopback-only A2A server exposes a deterministic checklist workflow. A RemoteA2aAgent client discovers its card and submits a synthetic request.

The employee needs this result: A response from the separate service that the local application can inspect. A timeout or an unreachable service must not be reported as a completed check.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

Independent ownership motivates a service interface. Reusing a Python function would not meet independent release requirements. Use the official adapter instead of hand-writing an A2A transport; keep business authorization in the remote capability.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Produce a correlation table from one actual request and design a response-loss scenario. Specify which operations are safe to retry and which require reconciliation.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Separate deployable ownership | Server and client are separate processes | The client depends on the endpoint contract, not a Python function import. |
| Advertise capabilities | ADK to_a2a creates the agent-card surface | The client resolves the fixed card URL. |
| Minimize transmitted data | Fresh local session containing only the synthetic snapshot | No existing banking conversation is attached. |
| Bound network work | Remote timeout and outer invocation deadline | Unavailable service does not become a successful check. |
| Make production identity explicit | Authenticated service endpoint and verified caller context | The loopback demo is not presented as production authentication. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Expression | Meaning |
|---|---|
| `app = to_a2a(...)` | Build an ASGI app from a native ADK agent/workflow |
| `uvicorn bank_case.server:app` | Import the module and serve its `app` object |
| `RemoteA2aAgent(...)` | Build a client-side proxy, not a local copy of the specialist |
| `agent_card="http://127.0.0.1:8001/..."` | Fixed discovery URL for this local lab |
| `timeout=10` | HTTP timeout; does not roll back work already started remotely |
| `use_legacy=False` | Select the current ADK protocol implementation path |

## `pyproject.toml`

```toml
[project]
name = "banking-module-21"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["google-adk[a2a]==2.11.0"]

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
"""A fixed, developer-controlled endpoint; never accept a URL from the model."""
from google.adk.a2a.agent import RemoteA2aAgent


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

## `bank_case/server.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Local A2A specialist. No authentication: bind only to loopback."""
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.events import Event
from google.adk.workflow import Workflow
from .contracts import CaseRequest


def review_checklist(node_input: CaseRequest) -> Event:
    # The remote service validates its own input; a network caller is not automatically trusted.
    result = {"case_id": node_input.case_id,
              "documents_complete": node_input.documents_complete,
              "source": "training-fixture:checklist-v1"}
    return Event(output=result, message=(
        f"{node_input.case_id}: checklist complete={node_input.documents_complete}. "
        "Synthetic evidence only; no credit approval."
    ))


specialist = Workflow(name="remote_checklist", input_schema=CaseRequest,
                      edges=[("START", review_checklist)], timeout=20)
app = to_a2a(specialist, host="127.0.0.1", port=8001)
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
import asyncio
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import display, run_once

if __name__ == "__main__":
    display(asyncio.run(run_once(build_agent(), SAMPLE)))
```

## `check_transport.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Run with the loopback server active; makes no model or cloud API calls."""
import unittest
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import run_once


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_a2a_round_trip(self):
        events = await run_once(build_agent(), SAMPLE)
        text = "\n".join(
            part.text for event in events if event.content
            for part in event.content.parts or [] if part.text
        )
        # This asserts a deterministic server response, not LLM phrasing.
        self.assertIn("CASE-001: checklist complete=False", text)
        self.assertIn("Synthetic evidence only; no credit approval.", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Explain the implementation to a reviewer

### `build_agent`

Construct a remote proxy with a developer-owned discovery URL. The description explains the narrow service. The HTTP timeout and current ADK protocol-path option are explicit. Proxy construction is configuration; network discovery and invocation occur when Runner executes it. The server implementation lives in a different module/process.

### Expected reasoning for the prediction exercise

No. Discovery and authorization are different operations. The production service must verify the caller and case entitlement before returning business facts.

## Trace the implementation

### Identify the reason for distribution

The team needs separate ownership and release cadence. If those needs do not exist, a local function or agent is simpler. A2A adds network, versioning, identity and failure responsibilities; it is not a prerequisite for multi-agent systems.

### Read the server workflow

`review_checklist` receives a validated CaseRequest and returns only the case ID, checklist flag and fixture source. `Event.message` produces user-visible content; `Event.output` is the structured workflow value. The server uses ordinary ADK nodes, not a hand-written JSON-RPC implementation.

### Expose with to_a2a

`to_a2a(specialist, host="127.0.0.1", port=8001)` builds an ASGI application. Uvicorn serves it. The host and port describe the local endpoint. Both binding and advertised address must match; 0.0.0.0 is a listening wildcard, not a client destination.

### Read the client configuration

The card URL is a developer-controlled literal. `timeout=10` bounds HTTP operations and the outer runtime bounds the invocation. The proxy is constructed without contacting the server; discovery happens during execution. No API key is embedded.

### Run server and client in separate terminals

Start Uvicorn first, fetch the agent card, then run the client. A correct test must observe an actual response, not merely that the proxy object constructed. Stop the server with Ctrl+C when finished.

### Inspect the failure case

Stop the server and rerun the client. It must fail visibly rather than report an all-clear checklist. The default adapter’s in-memory sessions/tasks are a development convenience; they do not prove durable remote task recovery.

### Design the production trust boundary

Choose an authenticated Google Cloud endpoint, service-to-service credentials, a case authorization contract, a durable task/session strategy and an allowlisted destination. Validate every returned business field before using it in Module 17’s router.

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

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [Expose an ADK agent through A2A](https://adk.dev/a2a/quickstart-exposing/)
- [Consume a remote agent](https://adk.dev/a2a/quickstart-consuming/)
- [Cloud Run service authentication](https://docs.cloud.google.com/run/docs/authenticating/service-to-service)
- [Official A2A SDK](https://github.com/a2aproject/a2a-python)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

