---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 25: Observability: Investigating a Banking Agent Request

**What you are practising:** Observability, execution traces and App plugins in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

Read the [ADK lifecycle primer](../module25-observability/lifecycle-primer.md) before implementing the hooks below. It introduces registration, runtime arguments, App scope and replacement behavior.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Start with the customer, not an import statement

### Read this as a bank employee's task

An analyst reports that the assistant sometimes takes too long or cannot finish a checklist lookup. The support team needs to find which operation was slow or failed.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Help us find the failed operation and understand what the analyst was told. Do not routinely copy company records into our diagnostic logs.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A request identifier and observations recorded while the request runs. |
| What should the employee receive? | Related timing and outcome information that helps an operator locate the problem. |
| What should happen when it cannot be completed? | A normal HTTP response must not hide an incomplete business task. Duplicate hook records must not be counted as separate requests. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Observability | Recorded information that helps people understand what a running application did. |
| Span | A timed operation, such as one tool execution. |
| Trace | Related spans that show the work performed for a request. |
| Log | A recorded observation, such as a lookup returning unavailable. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Write the desired outcome in one sentence, then identify inputs, operations, outputs and failure outcomes. Separate a verified source value from something a model inferred. The following specification makes the fictional exercise executable; a customer’s data owner and policy owner must supply real requirements.

| Requirement | Code decision | Acceptance check |
|---|---|---|
| Locate the failing operation | Use ADK native spans and bounded structured outcome fields | Find the tool operation and its invocation/trace identifiers. |
| Keep requests separate | No mutable request counters on a shared plugin | Concurrent invocations retain distinct identifiers. |
| Make failure visible | Map the controlled tool exception to unavailable | The model reports incomplete preparation rather than invented evidence. |
| Control sensitive logging | Log metadata only in the custom plugin | No prompt, checklist payload or exception message is logged by that plugin. |

## Set up the reference and your practice copy

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
cd training/module25-observability/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

The first command selects this example. `uv sync` creates its isolated environment from the dependency lock. The tests require no cloud credentials and use deterministic transport fixtures. They are the software-contract checkpoint, not completion of the real-service lab. Work in a copy when deliberately breaking behavior.

Complete [Google Cloud setup](../module23-artifacts/google-cloud-lab-guide.md#configure-a-real-service-run) before the live steps. It explains project selection, service identity, managed resource names, regions and configuration. Do not replace Google service calls with mock implementations and label the result a deployed test.

## Build the mental model

| English requirement | Coding step | How to check understanding |
|---|---|---|
| Locate the failing operation | Use ADK native spans and bounded structured outcome fields | Find the tool operation and its invocation/trace identifiers. |
| Keep requests separate | No mutable request counters on a shared plugin | Concurrent invocations retain distinct identifiers. |
| Make failure visible | Map the controlled tool exception to unavailable | The model reports incomplete preparation rather than invented evidence. |
| Control sensitive logging | Log metadata only in the custom plugin | No prompt, checklist payload or exception message is logged by that plugin. |

Use the existing runner and dependency setup. Rebuild the lesson functions in a practice copy one at a time: first define the input/output contract, then add validation, then connect the native ADK API, then exercise a failure path. Predict the trace before opening the complete solution.

## Files and responsibilities

| File | Responsibility |
|---|---|
| bank_review/telemetry.py | Lesson implementation, explained below |
| bank_review/agent.py | Lesson implementation, explained below |
| run.py | Execute locally against real Google model and persistence services |
| check_deployed.py / deployed-cases.json | Invoke an existing hosted agent and inspect its outcomes |
| eval/ | Native ADK model-evaluation cases and criteria |
| tests/ | Deterministic contract tests using real ADK wiring |
| pyproject.toml / uv.lock | Declared dependencies and resolved versions |
| .env.example | Resource/model settings; no credential material |

## Read Python before reading framework behavior

Imports make names available; importing Agent does not invoke Gemini. A function definition creates a callable; its body runs only when called. `name=value` passes a named argument. A dictionary maps keys to values, and a list keeps an ordered collection. `return` exits the function with a value. A type annotation explains an expected type; an explicit guard or schema performs runtime validation.

`async def` defines a coroutine. `await` waits for an asynchronous operation while allowing the event loop to do other work. It does not make an ordinary blocking SDK call asynchronous. `asyncio.run` starts the CLI event loop once. `async with Runner(...)` ensures runtime resources are closed when execution finishes or raises an error.

`None` means no replacement at the callback boundaries used here; an empty dictionary is still a dictionary. Zero is a valid artifact version. Test these values according to their contract rather than relying on truthiness. The solution includes every helper so learners can follow the request all the way to the returned event.

## Build this capability in observable increments

**Derivation:** “Which operation?” requires operation-level spans. “What happened to the bank task?” requires a bounded domain outcome. “Without logging documents” restricts the fields the custom logger emits; it does not configure every other exporter.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Run normal and injected-outage requests. For each, record invocation ID, trace ID if present, tool span duration, domain outcome and final response. Explain why HTTP success can coexist with incomplete preparation.

**Transfer to a changed customer requirement:** Work through 100 attempted lookups with 5 recovered exceptions. A correct failure rate is 5/100, not 10/100 because each failure produced two hook records. Choose and document the exact filter before creating an alert.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read and implement the code in small pieces

The blocks below follow the runnable files. Class-method excerpts belong inside their named class; the complete solution shows their indentation and constructor together. Read the explanation, predict the behavior, then run the relevant test.

### bank_review/telemetry.py

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
import logging
from google.adk.plugins import BasePlugin
from google.cloud.logging.handlers import StructuredLogHandler
from opentelemetry import trace
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### configure_logging

The handler formats structured JSON without a per-message network API call. The isinstance check prevents adding the same handler repeatedly when factories are called in tests. propagate=False avoids also emitting the same record through the root logger.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def configure_logging() -> None:
    """Write Cloud Logging structured JSON to stdout; the runtime collects it."""
    # Install one structured handler per logger so repeated setup does not duplicate operational records.
    if not any(
        isinstance(handler, StructuredLogHandler) for handler in logger.handlers
    ):
        logger.addHandler(StructuredLogHandler())
    logger.setLevel(logging.INFO)
    logger.propagate = False
```

#### ReviewTelemetry

Inheriting BasePlugin supplies native lifecycle integration. The constructor gives the plugin a stable name. App registration gives it application scope; it is not a fleet-wide service and does not automatically apply to another deployment.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
class ReviewTelemetry(BasePlugin):
    def __init__(self):
        super().__init__(name="review_telemetry")
```

#### ReviewTelemetry.record

Build a small dictionary with allowed metadata fields. The current OpenTelemetry span supplies a trace ID only when valid. `extra={json_fields: ...}` is the Google logging handler contract. This function never serializes tool_args, result or the exception object.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def record(self, tool_context, tool, outcome: str) -> None:
    # Allowlist diagnostic metadata; copying tool arguments or raw results would disclose banking content.
    fields = {
        "event": "bank_tool_outcome",
        "invocation_id": tool_context.invocation_id,
        "agent": tool_context.agent_name,
        "tool": tool.name,
        "outcome": outcome,
    }
    span = trace.get_current_span().get_span_context()
    if span.is_valid:
        fields["trace_id"] = format(span.trace_id, "032x")
    logger.info("bank_tool_outcome", extra={"json_fields": fields})
```

#### ReviewTelemetry.after_tool_callback

Plugin parameter names are tool_args and result; these differ from agent callback names in Module 26. The hook logs the status category and returns None so ADK keeps the original result.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
    # A returned result is available here; returning None preserves it for subsequent processing.
    outcome = "ok" if result.get("status") == "ok" else "business_failure"
    self.record(tool_context, tool, outcome)
    return None  # Observe without replacing the tool result.
```

#### ReviewTelemetry.on_tool_error_callback

Record an exception category and return an explicit unavailable outcome. Returning a dictionary changes execution by recovering this error. There is no automatic retry and no false success. In a real adapter, decide which exception classes are actually recoverable.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
    # Recovery returns an explicit unavailable result, which must never be interpreted as retrieved evidence.
    self.record(tool_context, tool, "exception")
    # This is an intentional recovery contract, not a successful lookup.
    return {"status": "unavailable", "retryable": True}
```

### bank_review/agent.py

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .telemetry import ReviewTelemetry, configure_logging
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### read_checklist

simulate_outage is a visible training switch. It must not become a customer-controlled production fault switch. The normal path returns a synthetic checklist with a source; the failing path raises an exception so the real ADK error hook runs.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def read_checklist(case_id: str, simulate_outage: bool = False) -> dict:
    """Read a synthetic checklist; outage injection is a training-only option."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if simulate_outage:
        raise TimeoutError("Synthetic dependency timeout")
    return {
        "status": "ok",
        "missing_documents": ["ownership_register"],
        "source": "training-fixture:checklist-v1",
    }
```

#### build_app

Configure the structured logger once, construct the agent and register the plugin on App. Standard tracing is configured at the execution/deployment boundary, separately from the business-outcome plugin.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    configure_logging()
    agent = Agent(
        name="observed_review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Read CASE-001's checklist with read_checklist. Set simulate_outage=True "
            "only when asked to simulate an outage. On unavailable, explain that "
            "preparation is incomplete; do not invent document status or retry in "
            "a loop. A human owns the credit decision. Data is synthetic."
        ),
        tools=[read_checklist],
    )
    return App(name="bank_review", root_agent=agent, plugins=[ReviewTelemetry()])
```

## Trace the runner into actual Google services

Read `run.py` alongside the [Google Cloud lab guide](../module23-artifacts/google-cloud-lab-guide.md). The CLI uses real Gemini, managed Sessions and a GCS artifact provider; only the banking records are synthetic.

| Expression | What happens | What it does not prove |
|---|---|---|
| `argparse.ArgumentParser` | Defines accepted CLI inputs | It does not validate bank authorization |
| `VertexAiSessionService(...)` | Selects managed conversation persistence | The locally executing agent has not been deployed |
| `GcsArtifactService(...)` | Selects the native Cloud Storage adapter | A bucket name alone does not grant permission |
| `create_session(...)` | Creates a session under this app/user scope | The synthetic user_id is not an authenticated end user |
| `types.Content(...parts=...)` | Packages the user message for ADK | Text claiming a bank fact is not a verified record |
| `Runner(app=..., ...)` | Combines application and service providers | Construction does not execute a request |
| `runner.run_async(...)` | Executes the invocation and yields events | Not every event is a final response |
| `RunConfig(max_llm_calls=8)` | Limits model-call count | It is not a precise currency budget |
| `asyncio.timeout(90)` | Bounds the local invocation wait | It cannot roll back completed external writes |
| `model_dump_json(...)` | Prints diagnostic event data | Full-event output is appropriate only for this synthetic lab |

`--session-id` reuses a managed session created by the same lab user. Without it, the CLI creates a new conversation. Save the printed identifier when testing continuity. The managed-service region and Gemini model location are separate settings.

`check_deployed.py` makes authenticated HTTPS calls to the hosted Agent Runtime ADK surface. It creates fresh test sessions, invokes `/run`, verifies the expected control/tool outcomes and saves returned events. It checks service behavior; natural-language quality still requires the evaluation rubric and review.

## Run the real-service scenario

After editing `.env` using the cloud guide:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python run.py "Read the checklist for CASE-001."
```

| Experiment | Evidence to inspect |
|---|---|
| Read CASE-001 normally | Find an ok outcome and the native tool span. |
| Ask to simulate an outage | Find an exception observation and an unavailable tool result. |
| Run two requests concurrently | Correlate each invocation separately; no shared request counter is used. |
| Inspect exported telemetry | Check actual payload capture, access and retention rather than assuming the custom plugin controls all logging. |

Use synthetic inputs. Live model calls, storage, inspection and telemetry can incur charges. Record the observed results rather than copying the expected outcome into a test report.

## Investigate the controlled incident

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python run.py --otel-to-cloud "Simulate an outage reading CASE-001."
```

Find the exception observation, the unavailable tool response and the final explanation. The structured log includes invocation_id and, when an active span exists, trace_id. Locally the structured log is printed; in the hosted runtime stdout is collected by Cloud Logging. Native trace export requires Cloud Trace permissions.

After the deployed check, use Logs Explorer with the selected project and a filter such as `jsonPayload.event="bank_tool_outcome"`. Add the recorded invocation_id to narrow it. Follow the recorded trace ID in Trace Explorer. If the event is not present, verify deployed identity, export settings and the runtime's log resource rather than assuming a successful model reply proves telemetry works.

Define the availability metric only after identifying whether one recovered error creates multiple hook observations. Choose one outcome/filter and document what a counted event means. This is a deliberate lesson about measurement, not a prebuilt production alert.

## Verify the hosted application

Deploy through the [native Agent Runtime path](../module23-artifacts/google-cloud-lab-guide.md#deploy-the-reviewed-package-to-agent-runtime), then run:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python check_deployed.py \
  --resource projects/PROJECT/locations/REGION/reasoningEngines/RUNTIME_ID
```

Open `deployment-results.json`. Check the selected resource, each test session, tool calls/results and final explanation. Complete the module-specific service evidence in the enterprise playbook. A passing HTTP response alone is insufficient. The supplied checker uses non-streaming `/run`; it does not validate token streaming.

## Advanced customer variation

Define a logs-based metric and an alert for sustained unavailable outcomes. Document the denominator and avoid double-counting recovered tool events. Reproduce a slow dependency and identify its span.

Before changing the code, write the new requirement, changed boundary, failure scenario and evidence needed to accept the change.

## Explain the result without reading the solution

- Which input is trusted, and which is supplied by the model?
- Which native Google or ADK component performs the operation?
- What changes when the happy path fails?
- What did the local tests establish, and what requires a real cloud run?
- What additional customer information is needed before production integration?

[Compare with the complete solution](./lab-solution.md).

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->

## Continue with the integrated customer exercise

The [integrated banking lab](../module26-callbacks/integrated-lab.md) connects the authorized Firestore read, deterministic next step, versioned artifacts, Gemini explanation, evaluation, logging and Model Armor in one App. Complete its live and deployed checkpoints after the isolated lesson. Its scope excludes an unimplemented ledger adapter and credit approval.
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

