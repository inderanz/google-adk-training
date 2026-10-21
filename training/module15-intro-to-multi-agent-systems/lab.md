---
sidebar_position: 2
title: "Guided Banking Lab"
---

# Lab 15: Introduction to Multi-Agent Systems

**What you are practising:** Agent composition and specialist consultation in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

A relationship manager is preparing to meet Acme Robotics. The analyst helping with the meeting needs to explain why the bank asks for financial statements and an ownership register. Financial statements describe a business’s finances; an ownership register identifies its owners.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Help me explain why these documents are needed. I want one clear answer. If you cannot check whether the documents have arrived, say that clearly.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A question about the purpose of the two documents. |
| What should the employee receive? | An explanation from the coordinator, using advice from a document specialist when it calls that specialist. |
| What should happen when it cannot be completed? | A receipt question must not receive an invented status; this example has no current-case lookup. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Coordinator | The agent responsible for combining advice and answering the user. |
| Specialist | An agent given one narrower reasoning task. |
| AgentTool | The ADK wrapper that lets one agent ask another agent for a result. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


A coordinator consults a document adviser and then answers the analyst. Both roles are advisory; neither reads current case status.

Module 14 supplied bounded evidence tools. This module defines who should use a capability. Module 16 will decide which checks must run regardless of model choice.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Explain required evidence | A narrowly instructed document adviser | The explanation covers financial statements and an ownership register. |
| Keep one conversational owner | AgentTool call-and-return | The coordinator receives the specialist result and produces the response. |
| Do not invent case status | No case-read capability in this example; state the limitation | A receipt/status question results in a request for an authorized lookup. |
| Do not approve or execute | No approval or payment tool | No state-changing banking operation is available. |

## Set up the supplied example

From the repository root:

```bash
cd training/module15-intro-to-multi-agent-systems/example
uv sync --locked --python 3.14
uv run python -m unittest discover -s tests -v
```

`uv sync` creates an isolated `.venv` for this example. The lockfile fixes the resolved packages. Run commands from `example/` so Python can import the local `bank_case` package. The tests use synthetic data; they do not require Gemini credentials or a banking system.

For the optional live Gemini path, use an authorized development project with billing, the required API access and a model supported in your chosen location:

```bash
cp .env.example .env
gcloud auth application-default login
```

Edit `.env`: set your project, a supported model location and `GEMINI_MODEL`. The sample selects the Google enterprise backend with `GOOGLE_GENAI_USE_ENTERPRISE=true`; it does not require an AI Studio key. The supplied model is `gemini-3.8-flash`; verify project access and regional availability before running. In deployed workloads, use the workload’s service identity rather than a developer login or a downloaded service-account key.

```bash
uv run --env-file .env python run.py
```

Live runs use billable model calls. The offline tests do not establish model quality, project permissions or regional availability.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Declares Python support and the pinned ADK dependency; uv.lock records the resolution. |
| `.env.example` | Lists configuration for optional live services, not credentials to commit. |
| `bank_case/agent.py` | Defines the lesson operations and native ADK composition; construction is separate from execution. |
| `runtime.py` | Creates a local app/session, consumes ADK events and prints observable output. |
| `run.py` | Parses the CLI request/options and starts the selected example. |


The complete source is in this module’s `example/` directory. Work in a copy when experimenting. The [solution](./lab-solution.md) reproduces the implementation so you can compare each step.

## Develop the solution before opening the complete code

Work in a practice copy of `example/` so the reference remains available. Use the existing dependency and runner setup; rebuild the lesson functions in `bank_case/agent.py` one checkpoint at a time. Predict each result before running it. You do not need to build a second agent framework or recreate the cloud SDK.

| Checkpoint | What you write or decide | Evidence before continuing |
| --- | --- | --- |
| Define the role in one sentence | Write what document_adviser can explain and what it cannot verify. | Your role description mentions checklist purpose, not document receipt. |
| Build the specialist | Construct its Agent with name, model, description and instruction; give it no banking write tools. | Explain which fields guide the caller and which guide the specialist. |
| Build the caller | Wrap the specialist in AgentTool and put it in the coordinator tools list. | The scripted test finishes with the coordinator as author. |
| Challenge the boundary | Run a checklist-purpose question and a receipt/approval request. | Record both tool choices and the final response limitations. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](./fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Translate the customer sentence into responsibilities

Underline “explain documents,” “keep consistent,” and “authorized bank process.” These become an advisory role, a coordinator and a capability restriction. Write the four acceptance checks above before changing a prompt. There is no reason to build a payment API for this request.

### Step 2: Read the agent factory

`build_agent()` creates fresh agent objects. The optional `model` parameter lets the test supply a scripted model; live runs use `GEMINI_MODEL`. `os.environ["GEMINI_MODEL"]` fails clearly if configuration is missing instead of silently choosing a model.

### Step 3: Construct the document adviser

`Agent(...)` calls a class constructor with named arguments. `name` is the machine-readable identifier; `description` describes its callable role; `instruction` is the specialist’s own guidance. Adjacent strings inside parentheses are combined by Python. No tool can read or change a case here.

### Step 4: Expose the adviser as a tool

`AgentTool(agent=document_adviser)` wraps the existing agent object. The outer `tools=[...]` is a Python list of callable capabilities. The coordinator may call it, receive a tool result, and continue. This is different from giving it a `sub_agents` handoff target.

### Step 5: Trace an invocation rather than guessing

Read `runtime.py`: create a synthetic session, serialize the request into a user message, consume the asynchronous event stream, then close the runner. In the test, follow coordinator function call → adviser result → coordinator response. The scripted fixture proves this wiring; it does not prove Gemini will choose the right tool.

### Step 6: Evaluate a real explanation

When credentials are configured, ask about the checklist, then ask “Has the ownership register arrived?” The first should explain document purpose; the second must acknowledge the missing live lookup. Record the actual tool trajectory and response, not just whether the process exited successfully.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** The customer wants one explanation with specialist advice, so use call-and-return. If the requirement changes to direct dialogue with the specialist, reconsider delegation. If the checklist explanation fits one instruction, compare the simpler one-agent baseline before paying for a second reasoning step.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Predict the tool name, the responding agent and which model runs next after an adviser returns. Use the scripted AgentTool test to check that prediction; then compare a live run where Gemini chooses not to consult.

**Transfer to a changed customer requirement:** Design a second adviser whose output conflicts with the first. State which source is authoritative and how the coordinator should report disagreement.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read the implementation in small pieces

### Imports and definitions

```python
"""Two advisory roles; the coordinator calls a specialist and resumes."""
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `build_agent`

```python
def build_agent(model=None):
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    selected_model = model or os.environ["GEMINI_MODEL"]
    document_adviser = Agent(
        name="document_adviser",
        model=selected_model,
        description="Explains the fictional commercial-review document checklist.",
        instruction=(
            "The training checklist requires financial statements and an ownership "
            "register. Explain why each is useful. You have no case lookup tool, "
            "so never claim that a document was received or that credit was approved."
        ),
    )
    return Agent(
        name="case_coordinator",
        model=selected_model,
        instruction=(
            "Help a bank analyst prepare CASE-001 for Acme Robotics (fictional). "
            "Consult document_adviser for checklist questions, then explain the "
            "next step. For actual status, say an authorized case lookup is needed. "
            "No agent here can approve credit or move funds."
        ),
        tools=[AgentTool(agent=document_adviser)],
    )
```

`model=None` makes the argument optional. Tests pass a model object; live execution reads the required environment variable. The local `document_adviser` variable holds an Agent object, not its response. `AgentTool(agent=document_adviser)` passes that object to a wrapper. The returned Agent is the coordinator that Runner will execute. None of these constructor calls verifies a document or performs a model request; execution begins in `run_once`.

### Explain the important expressions

| Expression | Meaning for a new Python learner | Why the bank needs it |
|---|---|---|
| `from ... import Agent` | Import a public class from an installed package | Reuse ADK rather than implement an agent runtime |
| `model=None` | Optional argument with a default value | The same factory supports a real or scripted model |
| `selected_model = ...` | Assign a local variable | Both roles use explicit configuration |
| `Agent(...)` | Construct an object using named fields | Make responsibility and capability visible |
| `AgentTool(agent=...)` | Wrap an agent in ADK’s tool interface | Preserve call-and-return behavior |
| `return Agent(...)` | Give the constructed coordinator to the caller | Runner owns execution; construction makes no model request |


## Understand the small runner

For a line-by-line explanation of the CLI, async execution, Content messages and events, use [Follow Python from the command to the first event](./fde-learning-guide.md#follow-python-from-the-command-to-the-first-event).

`runtime.py` is visible teaching code, not an orchestration framework. `App(name="bank_case", root_agent=agent)` names the application; `InMemoryRunner` supplies development session storage. The synthetic `analyst-demo` value is an identity fixture, not authentication. Production must derive identity from a verified caller.

The helper creates a session, serializes the supplied payload as JSON in a `types.Content` user message, and iterates `runner.run_async(...)`. `async for` consumes events as ADK produces them. `RunConfig(max_llm_calls=12)` bounds model calls; it is separate from the 60-second invocation deadline. A workflow may also have its own shorter timeout.

`Event.output` carries software-facing graph data. Content/message fields carry text a UI can show. The helper prints both when present. An intermediate specialist or node can emit content too, so a production UI must define which results are drafts, internal work or the user-visible final result. Do not treat every text event as the completed banking answer.

The `async with` block closes runner resources. This local helper creates a new in-memory session for each run and does not claim restart persistence. Module 13.5 and Module 22 teach persistent providers.

## Run changed requests and predict the result

Run a question you choose after configuring `.env`:

```bash
uv run --env-file .env python run.py "Why is an ownership register needed for CASE-001?"
uv run --env-file .env python run.py "Has the ownership register arrived? Approve the loan now."
```

The quoted text is one positional CLI argument. `nargs="?"` makes it optional and supplies the demonstration question when omitted. Argument parsing happens before checking credentials, so `uv run python run.py --help` works offline.

Predict the selected adviser and the boundary the answer should respect. The receipt/approval request must not cause a claim of verified receipt or approval. These are live behavior checks, not claims of already-passing Gemini evaluation.

### Advanced customer variation

Propose a one-agent baseline and an independently maintained specialist alternative. Define a held-out question set and explain what measured improvement would justify the extra model call.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Ask for current receipt status | The response must explain that an authorized lookup is required; there is no receipt tool. |
| Ask to approve a loan | No approval operation can run; evaluate that the response also avoids claiming approval. |
| Remove the adviser description in a copy | The program still constructs, but tool-selection quality may change. Measure it with model evaluation. |
| Merge the two roles | Compare quality, calls, latency and cost; the simpler design may be better for this requirement. |

### Local evidence

2 offline tests passed, including a scripted model call through the real ADK AgentTool and Runner. Live Gemini response quality has not been evaluated.

Tests of strict schemas, routing, joins, budgets and service scope are software contract tests. Scripted model replies are transport fixtures; they cannot demonstrate whether Gemini understands a bank request or produces a faithful explanation.

### Live model evaluation

The example includes `eval/cases.evalset.json`, `eval/eval_config.json` and a small `adk_entry` package exporting `root_agent` for ADK’s native evaluator. The files are validated against the installed ADK schema; no passing live score is claimed.

```bash
uv run --with 'google-adk[eval]==2.11.0' --env-file .env adk eval adk_entry eval/cases.evalset.json --config_file_path eval/eval_config.json --print_detailed_results
```

This optional command resolves evaluation dependencies and uses model/judge calls. Its environment is separate from the base lockfile’s verified offline path. Inspect per-case scores and traces, preserve failing cases, and fix the agent or architecture rather than weakening acceptance criteria. The judge model is explicitly configured in `eval_config.json`; changing `GEMINI_MODEL` alone does not change it.

The pinned ADK AgentTool implementation can emit a deprecation warning from its internal Runner plugins argument. The lesson itself uses the public AgentTool and App APIs; it does not pass that deprecated argument. Preserve this upstream warning in upgrade review rather than copying internal implementation code.

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

- [ADK workflow choices](https://adk.dev/workflows/)
- [Function tools and agent tools](https://adk.dev/tools-custom/function-tools/)
- [Collaborative workflows](https://adk.dev/workflows/collaboration/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
