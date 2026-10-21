---
sidebar_position: 2
title: "Guided Banking Lab"
---

# Lab 19: Collaborative Teams: Calls, Returns and Handoffs

**What you are practising:** Collaboration, delegation and conversation ownership in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Begin with the customer

### Read this as a bank employee's task

An analyst needs a single explanation covering both document requirements and how the review process works. One specialist can explain documents; another can explain the review process. The analyst should not have to combine their replies manually.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Use the relevant specialists to help explain how to prepare this case. Give me one answer, and keep any statements about what the specialists cannot verify.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A question about preparing the fictional case. |
| What should the employee receive? | A coordinator response that combines the consulted specialists’ advice and preserves their limitations. |
| What should happen when it cannot be completed? | If a required consultation is missing, record that as a behaviour failure or choose a workflow that forces the consultation. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Call-and-return | Ask a specialist for a result, then continue answering as the caller. |
| Handoff | Let another agent become responsible for the conversation. |
| Output schema | The named fields an agent’s result is expected to contain; it does not prove the facts are correct. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


A local coordinator has two AgentTools with structured advisory outputs. A separate factory demonstrates a single-turn delegation team.

Modules 16–18 controlled required work in code. This module introduces flexible advisory consultation. Module 20 will bound attempts when a generated memo needs revision.

## The technical specification you will implement

| Requirement | Code decision | Acceptance check |
| --- | --- | --- |
| Coordinator combines advisory results | Two AgentTool capabilities | Each consulted specialist returns to the coordinator. |
| Make limitations explicit | AdvisoryNote output_schema | Every specialist result has summary and limitation fields. |
| Do not imply required collection is guaranteed | Evaluate tool selection; use static workflow for mandatory checks | Missing consultations are visible as an evaluation failure. |
| Distinguish dialogue ownership | Separate single_turn sub-agent example | Learners can explain why this differs from tools=[...]. |

## Set up the supplied example

From the repository root:

```bash
cd training/module19-collaborative-teams/example
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
| Define the return schema | Write summary and limitation fields before constructing either adviser. | Describe what shape validation proves and what it cannot prove. |
| Build one adviser, then the second | Give each a distinct role description and no live banking write capability. | A reader can identify which adviser answers each kind of question. |
| Compose explicit tools | Wrap both with AgentTool and instruct the coordinator to preserve limitations. | The scripted test demonstrates two returns to the coordinator. |
| Compare delegation modes | Run single_turn and chat through the CLI, then task through a continuing ADK Web session. | Identify the capability name and responding agent in each trace. |

For each checkpoint, state: **input → operation → output → failure**. First explain it in ordinary English, then point to the Python line that implements it. A successful process exit is not enough; inspect the returned data and the control path.

Use the [FDE discovery and integration guide](../module15-intro-to-multi-agent-systems/fde-learning-guide.md) to record customer-specific answers. The lab brief supplies fictional assumptions; an FDE obtains actual policy, data ownership and access requirements from the customer.

## Build the mental model before reading the solution

### Step 1: Choose who owns the final response

The customer asked for one coherent explanation. Keep the coordinator as the final conversational owner and make specialist work callable. If the customer instead wanted a sustained conversation with one expert, evaluate a handoff design.

### Step 2: Define the advisory contract

`AdvisoryNote(BaseModel)` has two bounded strings. `summary` says what the specialist contributes. `limitation` says what it cannot establish. `Field(max_length=...)` bounds generated fields; it does not verify factual correctness.

### Step 3: Construct specialists before the coordinator

Python variables `documents` and `policy` refer to Agent objects. They share the explicitly chosen model but have different instructions and descriptions. Passing the Pydantic class to `output_schema` tells ADK the required response structure.

### Step 4: Wrap both roles in AgentTool

The tools list contains two wrappers. The coordinator can request either tool by its exposed name and receive the result. An instruction to consult both is still model behavior: inspect traces and evaluate omissions.

### Step 5: Read the alternative delegation factory

`build_delegation_team()` creates a fresh specialist in `sub_agents`; its default mode is `single_turn`. The CLI selects this alternative with `--mode single_turn`, `--mode task` or `--mode chat`. With no mode option, it runs the explicit AgentTool example. Reusing one child instance under multiple parents can violate the agent-tree ownership rules; factories avoid that confusion.

### Step 6: Trace two calls in the offline test

The scripted model returns a document tool call, a structured adviser reply, a review tool call, another reply and a coordinator response. ADK performs the actual nested calls. This proves call-and-return wiring, not natural-language reasoning quality.

### Step 7: Evaluate the real coordinator

Use a full preparation request, a narrow checklist question and a request for actual approval. Check which capabilities it called, whether it preserved limitations and whether it invented status. If required coverage remains unreliable, change the architecture to a static collection workflow.

## Python reading guide

Read a file from its inputs toward its outputs. Imports make library names available. A `def` creates a function; its body runs when called. Type annotations describe expected values; Pydantic performs the runtime validation at the schema boundary. A dictionary maps keys to values, a list holds ordered items, and a tuple groups fixed items such as graph endpoints.

Named arguments such as `name="case_router"` identify constructor options. An unquoted function name is a callable object; adding `()` calls it. `return` ends the function and supplies its result. `raise` reports a failure instead of producing success. In asynchronous code, `await` waits without blocking the event loop on that operation; it does not automatically parallelize surrounding statements.

The examples use current built-in annotations such as `list[str]` and `dict`, Pydantic v2 `model_validate()`/`model_dump()`, `asyncio.run()` at the CLI boundary, and native ADK classes. No custom agent execution framework is required.

## Build this capability in observable increments

**Derivation:** One combined explanation suggests a coordinator receiving notes. A sustained conversation with an expert suggests delegation. Mandatory evidence collection belongs in deterministic scheduling even if the final explanation uses advisers.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Use one continuing ADK Web session: request document help, ask a follow-up, then ask for another specialist. Record the responding author at each turn for chat and task modes; compare with an AgentTool return.

**Transfer to a changed customer requirement:** Supply a valid structured note with an unsupported assertion. Design a quality criterion that rejects it despite schema success.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read the implementation in small pieces

### Imports and definitions

```python
"""A coordinator consults two local specialists using call-and-return."""
import os
from typing import Literal
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field
```

Imports name the public ADK and Python APIs used below. Importing a class does not run a model call. The factory separates object construction from execution so the same code can be exercised with a test fixture.

### Read `AdvisoryNote`

```python
class AdvisoryNote(BaseModel):
    summary: str = Field(max_length=600)
    limitation: str = Field(max_length=300)
```

The class inherits Pydantic's validation behavior. Both annotated fields are required strings because no defaults are supplied. Field(max_length=...) bounds length; it does not require nonempty content, verify citations or make a statement true. Passing the class as output_schema describes the expected specialist result; it is not an example result instance.

### Read `build_agent`

```python
def build_agent(model=None):
    # Construct the ADK composition now; Runner executes it only after receiving a request.
    selected_model = model or os.environ["GEMINI_MODEL"]
    documents = Agent(
        name="document_adviser", model=selected_model,
        description="Explains financial statements and ownership-register evidence.",
        instruction="Explain the two required documents; you cannot verify receipt.",
        output_schema=AdvisoryNote,
    )
    policy = Agent(
        name="review_adviser", model=selected_model,
        description="Explains that a human analyst owns the credit decision.",
        instruction=("Explain that analysts assess evidence and authorize decisions. "
                     "You have no policy retrieval tool; do not invent policy limits."),
        output_schema=AdvisoryNote,
    )
    return Agent(
        name="case_coordinator", model=selected_model,
        instruction=(
            "Prepare an advisory explanation for CASE-001 (fictional). For a full "
            "preparation request, consult both advisers and combine their notes, "
            "preserving their limitations. If either fails, report an incomplete "
            "explanation. Do not approve credit or claim current case status."
        ),
        tools=[AgentTool(agent=documents), AgentTool(agent=policy)],
    )
```

`selected_model` is shared configuration, while `documents` and `policy` are different Agent objects with different instructions. The name policy is a Python variable for the review adviser, not a policy datastore. Each adviser emits AdvisoryNote-shaped output. Two explicit AgentTool wrappers expose the advisers to the coordinator. The prompt requests both consultations; only an execution trace/evaluation can establish that the model actually selected both.

### Read `build_delegation_team`

```python
def build_delegation_team(model=None, mode: Literal["chat", "task", "single_turn"] = "single_turn"):
    # Mode chooses the interaction contract, not a banking permission.
    # Create a fresh child for this parent; mode controls delegation rather than business authorization.
    selected_model = model or os.environ["GEMINI_MODEL"]
    specialist = Agent(
        name="checklist_specialist", model=selected_model, mode=mode,
        description="Explains the financial-statements and ownership-register checklist.",
        instruction="Explain the two document types. Do not claim receipt or approval.",
    )
    return Agent(
        name="delegation_coordinator", model=selected_model,
        instruction="Delegate checklist questions to checklist_specialist.",
        sub_agents=[specialist],
    )
```

`Literal` documents the permitted mode strings, and Agent validates its own mode field. The CLI separately restricts the allowed option values. A fresh checklist_specialist is placed in sub_agents, establishing the hierarchy. In single_turn mode ADK exposes a named delegation capability; in chat mode a transfer changes the responding agent. The factory returns the coordinator without starting a conversation.

### Explain the important expressions

| Expression | Meaning |
|---|---|
| `class AdvisoryNote(BaseModel)` | Define a typed return contract |
| `output_schema=AdvisoryNote` | Give ADK the schema class, not an already-created note |
| `tools=[AgentTool(...), AgentTool(...)]` | Supply callable specialist capabilities |
| `sub_agents=[specialist]` | Establish a delegation hierarchy instead |
| `mode="single_turn"` | Choose the local child’s interaction mode |
| `build_delegation_team()` | Build the alternative separately so the comparison is visible |


## Understand the small runner

For a line-by-line explanation of the CLI, async execution, Content messages and events, use [Follow Python from the command to the first event](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#follow-python-from-the-command-to-the-first-event).

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

Compare two additional control modes:

```bash
uv run --env-file .env python run.py --mode single_turn "Explain the document checklist."
uv run --env-file .env python run.py --mode chat "Explain the document checklist."
```

With `tools` (the default), the CLI builds the two-adviser AgentTool example. Other modes build the one-specialist hierarchy. For `single_turn`, inspect the named specialist delegation and coordinator return. For `chat`, inspect transfer_to_agent and which agent responds. Model choice of whether to delegate still requires evaluation.

To explore `task` over several turns, use a continuing ADK Web session:

```bash
TEAM_MODE=task uv run --env-file .env adk web .
```

Select **adk_entry**, send a checklist question, and continue in the same session. The browser is a local development interface. The role here may not need clarification for a simple question; for an exercise, give it a narrowly defined task that genuinely requires a missing fact. Do not infer multi-turn behavior from rerunning the one-turn CLI, which creates a new session each time. Stop the local server when finished.

The supplied evaluation cases exercise the default two-adviser `tools` mode. Leave TEAM_MODE unset or set it to tools for that evaluation; define separate acceptance cases when evaluating chat or task behavior.

### Advanced customer variation

Replace optional consultation with compulsory collection in a design variant. Compare control guarantees, number of model calls, error handling and evidence completeness. Explain when each design is appropriate.

Before implementing the variation, record the new requirement, the code boundary that changes and the negative case that would expose an incorrect implementation.

## Verify the customer outcome

| Experiment | What to observe |
| --- | --- |
| Ask for a full preparation explanation | Evaluate that both advisers are consulted and limitations survive synthesis. |
| Ask only why ownership evidence is needed | Evaluate whether the selected consultation is appropriate; do not force an unrelated exact tool order. |
| Compare --mode single_turn and --mode chat | Inspect the selected delegation/transfer capability and the final responding agent. |
| Require a compulsory two-source evidence pack | Explain why Module 16 provides a stronger scheduling guarantee than this coordinator prompt. |

### Local evidence

3 offline tests passed, covering two explicit AgentTool calls, a single-turn delegation that returns to the coordinator, and a chat transfer whose specialist responds. All model replies are scripted fixtures. Live consultation quality remains unevaluated.

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

- [Collaborative workflows and modes](https://adk.dev/workflows/collaboration/)
- [Agent tools](https://adk.dev/tools-custom/function-tools/)
- [Remote A2A consumption](https://adk.dev/a2a/quickstart-consuming/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
