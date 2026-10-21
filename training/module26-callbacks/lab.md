---
sidebar_position: 2
title: "Guided Banking Lab"
---

# Lab 26: Callbacks: Agent Lifecycle and Banking Tool Controls

**What you are practising:** Agent callbacks and lifecycle control in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Start with the customer, not an import statement

### Read this as a bank employee's task

The analyst asks the assistant for checklist items. The bank wants invalid requests rejected before a lookup, and wants developers to understand exactly when they can observe or replace an operation.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Check the requested item limit before looking up the checklist. Keep the same checks when another part of the application calls the lookup directly. Show us which operation ran and which was skipped.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A case ID and the requested maximum number of checklist items. |
| What should the employee receive? | A valid lookup result or a clear input error; the human still owns the credit decision. |
| What should happen when it cannot be completed? | An invalid request must not execute the tool body. A response change must preserve unrelated response fields. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Callback | A function that ADK calls at a defined point while running an agent. |
| Lifecycle | The stages an operation passes through, from starting to completing or failing. |
| Replacement | A hook result that ADK uses instead of the operation or result at that particular boundary. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Write the desired outcome in one sentence, then identify inputs, operations, outputs and failure outcomes. Separate a verified source value from something a model inferred. The following specification makes the fictional exercise executable; a customer’s data owner and policy owner must supply real requirements.

| Requirement | Code decision | Acceptance check |
|---|---|---|
| Bound requested work | Validate max_items as an integer from 1 to 5 | Booleans, strings and out-of-range values are rejected. |
| Validate at the durable boundary | Repeat the validation inside the callable tool | Direct Python calls cannot bypass the input contract. |
| Understand interception | Demonstrate None versus replacement return values | A blocked tool is not executed; the model can explain the error. |
| Preserve response structure | Copy only changed text parts and retain other fields | A later text part is changed without losing an accompanying function call. |

## Set up the reference and your practice copy

From the repository root:

```bash
cd training/module26-callbacks/example
uv sync --locked --python 3.14
uv run python -m unittest discover -s tests -v
```

The first command selects this example. `uv sync` creates its isolated environment from the dependency lock. The tests require no cloud credentials and use deterministic transport fixtures. They are the software-contract checkpoint, not completion of the real-service lab. Work in a copy when deliberately breaking behavior.

Complete [Google Cloud setup](../module23-artifacts/google-cloud-lab-guide.md#configure-a-real-service-run) before the live steps. It explains project selection, service identity, managed resource names, regions and configuration. Do not replace Google service calls with mock implementations and label the result a deployed test.

## Build the mental model

| English requirement | Coding step | How to check understanding |
|---|---|---|
| Bound requested work | Validate max_items as an integer from 1 to 5 | Booleans, strings and out-of-range values are rejected. |
| Validate at the durable boundary | Repeat the validation inside the callable tool | Direct Python calls cannot bypass the input contract. |
| Understand interception | Demonstrate None versus replacement return values | A blocked tool is not executed; the model can explain the error. |
| Preserve response structure | Copy only changed text parts and retain other fields | A later text part is changed without losing an accompanying function call. |

Use the existing runner and dependency setup. Rebuild the lesson functions in a practice copy one at a time: first define the input/output contract, then add validation, then connect the native ADK API, then exercise a failure path. Predict the trace before opening the complete solution.

## Files and responsibilities

| File | Responsibility |
|---|---|
| bank_review/controls.py | Lesson implementation, explained below |
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

**Derivation:** “Reject before lookup” motivates before_tool. “Still reject direct calls” requires validation inside the tool too. “Preserve function calls while changing text” requires copying the response parts selectively rather than rebuilding a text-only response.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Observe a valid lookup, invalid limit and before-model replacement. For each, predict which body and after hook execute. Run the empty-dictionary test to distinguish None from a valid empty tool replacement.

**Transfer to a changed customer requirement:** Compose a plugin and agent callback that both return replacements. Record which one wins, which hooks are skipped and whether any safety check can be bypassed by that ordering.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read and implement the code in small pieces

The blocks below follow the runnable files. Class-method excerpts belong inside their named class; the complete solution shows their indentation and constructor together. Read the explanation, predict the behavior, then run the relevant test.

### bank_review/controls.py

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### validate_request

Return None for valid inputs and an error dictionary otherwise. This contract is used by both the callback and tool. Exact type checks reject booleans and strings before numerical comparisons can accept or crash on them.

```python
def validate_request(case_id, max_items) -> dict | None:
    """Reject booleans as integers and unsupported scope before any lookup."""
    # Validate at the reusable business boundary because direct calls can bypass agent callbacks.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if type(max_items) is not int or not 1 <= max_items <= 5:
        return {"status": "invalid_limit", "allowed_range": "1..5"}
    return None
```

#### read_checklist

Call validation inside the tool, then return only the bounded synthetic checklist. This makes direct calls obey the same input contract. The slice demonstrates a work bound, although this fixture has only one missing item.

```python
def read_checklist(case_id: str, max_items: int = 5) -> dict:
    """The tool validates even when called without the ADK callback."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    problem = validate_request(case_id, max_items)
    if problem is not None:
        return problem
    return {"status": "ok", "case_id": case_id,
            "missing_documents": ["ownership_register"][:max_items],
            "source": "training-fixture:checklist-v1"}
```

#### before_agent

Initialize the temporary checks list for this invocation. Returning None tells ADK to execute the agent. It does not initialize a durable user preference or authorize a case.

```python
def before_agent(callback_context: CallbackContext) -> types.Content | None:
    # Initialize invocation-scoped diagnostic state before this agent starts its work.
    callback_context.state["temp:checks"] = []
    return None
```

#### before_model

Read current-turn user_content through the public context property and join its text parts. Only the exact laboratory marker returns a replacement LlmResponse. Other requests proceed to Gemini and are evaluated normally.

```python
def before_model(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    # This is an explicit lab input contract, not semantic intent detection.
    # This exact lab command illustrates provider-call replacement, not general natural-language policy detection.
    content = callback_context.user_content
    text = " ".join(part.text or "" for part in (content.parts or [])) if content else ""
    if text.strip() == "LAB:REQUEST_CREDIT_APPROVAL":
        return LlmResponse(content=types.Content(role="model", parts=[
            types.Part.from_text(text="A human analyst must make the credit decision.")
        ]))
    return None
```

#### before_tool

Only intercept read_checklist. Validate arguments, copy and update the temporary diagnostic list, and return the validation result. A dictionary skips this execution; None lets the tool run. The callback argument is named args, unlike the plugin’s tool_args.

```python
def before_tool(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None:
    if tool.name != "read_checklist":
        return None
    problem = validate_request(args.get("case_id"), args.get("max_items", 5))
    checks = list(tool_context.state.get("temp:checks", []))
    checks.append("blocked" if problem is not None else "validated")
    tool_context.state["temp:checks"] = checks
    return problem
```

#### after_tool

Add human decision ownership only to a successful checklist result. Dictionary unpacking creates a new result; failure dictionaries remain failures. This post-execution hook cannot undo a backend write.

```python
def after_tool(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None:
    # Add human ownership only to successful lookup results without rewriting failure outcomes.
    if tool.name == "read_checklist" and tool_response.get("status") == "ok":
        return {**tool_response, "decision_owner": "human_analyst"}
    return None
```

#### after_model

Walk every content part, copy changed text parts, and preserve untouched parts. model_copy retains the surrounding LlmResponse fields. Returning None when unchanged avoids constructing an unnecessary replacement. This exact marker transformation is not a security claim.

```python
def after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    # Demonstrate response copying without deleting other text or function calls.
    # Modify only the intended text parts so other response fields and function calls survive.
    content = llm_response.content
    if content is None or not content.parts:
        return None
    changed = False
    parts = []
    for part in content.parts:
        if part.text and "LAB_INTERNAL_MARKER" in part.text:
            parts.append(part.model_copy(update={"text": part.text.replace("LAB_INTERNAL_MARKER", "[removed]")}))
            changed = True
        else:
            parts.append(part)
    if not changed:
        return None
    return llm_response.model_copy(update={"content": content.model_copy(update={"parts": parts})})
```

#### after_agent

Record which invocation completed. The state update can yield a final event without text, which is why consumers inspect event content rather than blindly indexing the last event.

```python
def after_agent(callback_context: CallbackContext) -> types.Content | None:
    # Tracked state assignment can emit a state-only event after the text response.
    callback_context.state["last_review_invocation"] = callback_context.invocation_id
    return None
```

### bank_review/agent.py

```python
import os
from google.adk.agents import Agent
from google.adk.apps import App
from . import controls
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### build_app

Register each named function on its corresponding Agent hook. This wiring is local to this agent. The App itself has no safety plugin; to combine Modules 25.5 and 26, attach the native plugin explicitly and test the combined ordering.

```python
def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    agent = Agent(
        name="controlled_review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Explain the CASE-001 checklist using read_checklist. Pass a requested "
            "max_items exactly; do not silently repair an invalid limit. Report "
            "tool errors truthfully. You cannot approve credit. Data is synthetic."
        ),
        tools=[controls.read_checklist],
        before_agent_callback=controls.before_agent,
        after_agent_callback=controls.after_agent,
        before_model_callback=controls.before_model,
        after_model_callback=controls.after_model,
        before_tool_callback=controls.before_tool,
        after_tool_callback=controls.after_tool,
    )
    return App(name="bank_review", root_agent=agent)
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

```bash
uv run --env-file .env python run.py "Read CASE-001 with max_items=1."
```

| Experiment | Evidence to inspect |
|---|---|
| Ask for max_items=1 | Observe validated tool execution and added human decision ownership. |
| Ask for max_items=99 | Observe the error replacement and model explanation; the tool body must not run. |
| Send LAB:REQUEST_CREDIT_APPROVAL | Observe the fixed reply without a model request. |
| Inspect the multipart unit test | Explain why rebuilding Content from only the first text part would destroy information. |

Use synthetic inputs. Live model calls, storage, inspection and telemetry can incur charges. Record the observed results rather than copying the expected outcome into a test report.

## Verify the hosted application

Deploy through the [native Agent Runtime path](../module23-artifacts/google-cloud-lab-guide.md#deploy-the-reviewed-package-to-agent-runtime), then run:

```bash
uv run --env-file .env python check_deployed.py \
  --resource projects/PROJECT/locations/REGION/reasoningEngines/RUNTIME_ID
```

Open `deployment-results.json`. Check the selected resource, each test session, tool calls/results and final explanation. Complete the module-specific service evidence in the enterprise playbook. A passing HTTP response alone is insufficient. The supplied checker uses non-streaming `/run`; it does not validate token streaming.

## Advanced customer variation

Combine the Module 25.5 plugin with these callbacks in a practice copy. Prove the order for allowed input, denied tool arguments and unavailable inspection. If adding response caching, list every context and policy dependency before choosing a key.

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
