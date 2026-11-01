---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 24: Evaluation: Evidence for a Banking Release Decision

**What you are practising:** Agent evaluation and release evidence in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Start with the customer, not an import statement

### Read this as a bank employee's task

The bank is considering a pilot of the assistant. A successful answer to one question is not enough: the team needs to check known cases, missing cases, unclear requests and requests the assistant must not fulfil.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Show us how the assistant behaves on an agreed set of questions. When we change it, show which answers improved and which became worse.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | Example questions, expected tool activity where relevant, and written rules for judging answers. |
| What should the employee receive? | Individual case results that can be inspected before a release decision. |
| What should happen when it cannot be completed? | Missing results, failed cases or unscored required checks must not count as a pass. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Evaluation | Running scenarios and assessing whether the observed behaviour meets the agreed requirements. |
| Rubric | Written rules explaining what makes an answer acceptable or unacceptable. |
| Trajectory | The sequence of actions and tool calls observed while answering a request. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Write the desired outcome in one sentence, then identify inputs, operations, outputs and failure outcomes. Separate a verified source value from something a model inferred. The following specification makes the fictional exercise executable; a customer’s data owner and policy owner must supply real requirements.

| Requirement | Code decision | Acceptance check |
|---|---|---|
| Explain the known case | Provide a source-backed missing-document response | The ownership register is missing; credit remains a human decision. |
| Handle unknown cases | Return not_found without substituting a record | CASE-999 never becomes CASE-001. |
| Ask for missing context | Include a request with no case ID | The assistant asks a clarifying question. |
| Decide whether to release | Require all expected cases and configured metrics | Missing, failed, non-finite or unevaluated results do not pass. |

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
cd training/module24-evaluation/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

The first command selects this example. `uv sync` creates its isolated environment from the dependency lock. The tests require no cloud credentials and use deterministic transport fixtures. They are the software-contract checkpoint, not completion of the real-service lab. Work in a copy when deliberately breaking behavior.

Complete [Google Cloud setup](../module23-artifacts/google-cloud-lab-guide.md#configure-a-real-service-run) before the live steps. It explains project selection, service identity, managed resource names, regions and configuration. Do not replace Google service calls with mock implementations and label the result a deployed test.

## Build the mental model

| English requirement | Coding step | How to check understanding |
|---|---|---|
| Explain the known case | Provide a source-backed missing-document response | The ownership register is missing; credit remains a human decision. |
| Handle unknown cases | Return not_found without substituting a record | CASE-999 never becomes CASE-001. |
| Ask for missing context | Include a request with no case ID | The assistant asks a clarifying question. |
| Decide whether to release | Require all expected cases and configured metrics | Missing, failed, non-finite or unevaluated results do not pass. |

Use the existing runner and dependency setup. Rebuild the lesson functions in a practice copy one at a time: first define the input/output contract, then add validation, then connect the native ADK API, then exercise a failure path. Predict the trace before opening the complete solution.

## Files and responsibilities

| File | Responsibility |
|---|---|
| bank_review/agent.py | Lesson implementation, explained below |
| check_eval.py | Lesson implementation, explained below |
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

**Derivation:** “Never substitute a case” becomes a negative scenario. “Explain the evidence” becomes an answer rubric. “Look it up first” becomes a trajectory criterion where required. “Before release” becomes a gate over a complete, identified result set.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Open only the unknown case first. Label each nested field, predict the tool arguments and write one passing and one failing explanation. Run the evaluator; locate that eval_id and explain its metric result before running the gate.

**Transfer to a changed customer requirement:** Compare two valid tool trajectories for the same customer outcome. Decide whether EXACT, IN_ORDER or ANY_ORDER matches the requirement, then document what that criterion still fails to establish.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read and implement the code in small pieces

The blocks below follow the runnable files. Class-method excerpts belong inside their named class; the complete solution shows their indentation and constructor together. Read the explanation, predict the behavior, then run the relevant test.

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
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### read_case

The if statement rejects unknown identifiers before returning the fixture. The result contains both facts and provenance. A real adapter would additionally authorize the caller and retrieve the current bank record; changing the prompt cannot supply either guarantee.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def read_case(case_id: str) -> dict:
    """Read a synthetic record; unsupported identifiers never return CASE-001."""
    # Reject unsupported identifiers before returning facts, preventing accidental substitution of another case.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    return {
        "status": "ok",
        "case_id": case_id,
        "missing_documents": ["ownership_register"],
        "source": "training-fixture:checklist-v1",
        "decision_owner": "human_analyst",
    }
```

#### build_app

The instruction defines the desired behavior for known, unknown and missing identifiers. Its correctness is evaluated through actual model runs. Passing a scripted test only establishes that ADK can call the tool and receive the dictionary.

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
    agent = Agent(
        name="review_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Help prepare commercial reviews using read_case. Ask for the case ID "
            "if absent. For a supplied case ID, look it up before making factual "
            "claims. Report missing documents, source and human decision ownership. "
            "On not_found, say the case was not found; never substitute another case. "
            "You cannot approve credit or modify records. Tool data is synthetic."
        ),
        tools=[read_case],
    )
    return App(name="bank_review", root_agent=agent)
```

## Construct one evaluation case before writing the gate

The bank says: “An unknown case must not become another customer's case.” This produces the following native case, copied from the supplied dataset:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```json
{
  "eval_id": "unknown",
  "conversation": [
    {
      "user_content": {
        "role": "user",
        "parts": [
          {
            "text": "Prepare CASE-999 for review."
          }
        ]
      },
      "intermediate_data": {
        "tool_uses": [
          {
            "name": "read_case",
            "args": {
              "case_id": "CASE-999"
            }
          }
        ]
      }
    }
  ],
  "session_input": {
    "app_name": "bank_review",
    "user_id": "training-evaluator"
  }
}
```

| Field | Derivation and consumer |
|---|---|
| eval_id | Stable scenario identity used to find its result; not a banking case ID |
| conversation | Ordered turns in this scenario; add a second turn to test conversational continuity |
| user_content.role | This is a user message to the agent |
| parts[].text | The exact customer request the evaluator submits |
| intermediate_data.tool_uses | Expected capability and arguments for metrics that inspect trajectories |
| session_input | App/user scope for the evaluation session; the fixture identifier is not authentication |

First write two candidate answers on paper: “CASE-999 was not found” and “CASE-001 needs an ownership register.” Only the first satisfies the unknown-case requirement. Explain why fluent wording cannot rescue the second. Then inspect which configured metric checks that distinction.

Open eval_config.json. The rubric text is the scoring instruction; threshold is the acceptance bar; judge_model selects the evaluator model; num_samples controls repeated judging. None of these changes the agent's tool permissions. The separate trajectory_config.json selects EXACT for its narrow known-case exercise.

For an illustrative result, imagine known=1, unknown=0, clarify=1 and approval=1. An average of 0.75 hides the specific wrong-case failure. The supplied gate requires every configured case and metric to meet its threshold. This example explains interpretation; it is not a claimed live score.

### check_eval.py

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
import argparse
import math
from pathlib import Path
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_set import EvalSet
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### require_passed

First reject a dataset with duplicate case IDs and a configuration with no criteria. Then compare the dataset identity and exact case coverage. Inspect each case status and configured metric. Reject duplicate metric rows before turning them into a dictionary: otherwise a later passing row could hide an earlier failure. A missing score, non-finite score or threshold, or score below its required threshold rejects the result. The gate reads native result fields rather than scraping terminal output. It does not calculate judge scores itself.

This gate is written for the supplied metrics, where a higher score is better. A future latency or cost criterion may need a maximum rather than a minimum. Define that comparison explicitly before reusing this function. A passing result also needs trusted provenance: retain the dataset, configuration, code revision and model settings from the run. The gate cannot prove that an edited result file was produced by the stated model.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
def require_passed(result: EvalSetResult, dataset: EvalSet, config: EvalConfig) -> None:
    # A release gate needs complete case coverage and every required metric, not merely a zero process exit.
    expected_cases = {case.eval_id for case in dataset.eval_cases}
    # A set removes duplicates. Check the original length so two scenarios with
    # the same ID cannot silently become one required result.
    if len(expected_cases) != len(dataset.eval_cases):
        raise ValueError("Duplicate case IDs in the dataset")
    if not config.criteria:
        raise ValueError("No evaluation criteria configured")
    thresholds = {}
    for name, criterion in config.criteria.items():
        threshold = (
            criterion if isinstance(criterion, (float, int)) else criterion.threshold
        )
        # NaN makes ordinary comparisons false, which could accidentally pass
        # a bad score. This teaching gate uses finite, higher-is-better metrics.
        if isinstance(threshold, bool) or not math.isfinite(threshold):
            raise ValueError(f"Invalid threshold: {name}")
        thresholds[name] = threshold
    if result.eval_set_id != dataset.eval_set_id:
        raise ValueError("Result belongs to another dataset")
    if (
        not expected_cases
        or {case.eval_id for case in result.eval_case_results} != expected_cases
    ):
        raise ValueError("Missing or unexpected evaluation cases")
    if len(result.eval_case_results) != len(expected_cases):
        raise ValueError("Duplicate evaluation cases; select one complete run")
    for case in result.eval_case_results:
        if case.final_eval_status.name != "PASSED":
            raise ValueError(f"Case did not pass: {case.eval_id}")
        metrics = {
            metric.metric_name: metric for metric in case.overall_eval_metric_results
        }
        # A dictionary would otherwise keep only the last duplicate metric,
        # possibly hiding a failure behind a later passing row.
        if len(metrics) != len(case.overall_eval_metric_results):
            raise ValueError(f"Duplicate metric results: {case.eval_id}")
        for name, threshold in thresholds.items():
            metric = metrics.get(name)
            if (
                metric is None
                or metric.eval_status.name != "PASSED"
                or metric.score is None
                or not math.isfinite(metric.score)
                or metric.score < threshold
            ):
                raise ValueError(f"Missing or failing metric: {case.eval_id}/{name}")
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
uv run --env-file .env python run.py "Prepare CASE-001 for review."
```

| Experiment | Evidence to inspect |
|---|---|
| Run the four supplied cases | Inspect individual scores and actual tool arguments, not just an average. |
| Deliberately instruct the agent to invent missing status in a practice copy | The affected rubric should fail; keep the failing result for comparison. |
| Run the known-case trajectory exercise | Use the separate EXACT configuration for one deterministic lookup scenario. |
| Remove one case result from a copied result file | check_eval.py must reject incomplete coverage. |

Use synthetic inputs. Live model calls, storage, inspection and telemetry can incur charges. Record the observed results rather than copying the expected outcome into a test report.

## Evaluate, introduce a regression, then apply a result gate

Install the pinned native evaluator extras and run the four cases:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv sync --locked --extra eval
uv run --env-file .env adk eval bank_review eval/cases.evalset.json --config_file_path eval/eval_config.json --print_detailed_results
```

Read `eval/cases.evalset.json` first. Its four eval_id values cover known case, unknown case, missing identifier and an approval request. The configuration names a rubric, threshold, judge model and sample count. The dataset's expected tool calls are used only when a selected metric examines trajectories; a quality-only run does not silently enforce them.

Now evaluate only the known-case tool trajectory using the separate criterion:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env adk eval bank_review eval/cases.evalset.json:known --config_file_path eval/trajectory_config.json --print_detailed_results
```

An EXACT tool match is appropriate for this narrow exercise. Do not make every open-ended consultation require a recorded tool sequence. Also do not feed this one-case result into the full four-case quality gate: it should be rejected as incomplete.

The native local result manager stores EvalSetResult JSON under the application's `.adk/eval_history` directory. Inspect the emitted path/results; select the complete quality run you intend to gate, not an arbitrary newest file from another experiment:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python check_eval.py bank_review/.adk/eval_history/YOUR_RESULT_FILE.evalset_result.json
```

In a practice copy, add an instruction that contradicts the customer contract, rerun and retain the failing result. Restore/fix the instruction and compare case-level evidence. Never lower the criterion solely to make the broken candidate pass. The exit code of check_eval.py is a gate on the supplied result, not proof that the dataset covers every customer risk.

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

Add a multi-turn case where evidence becomes unavailable, maintain a held-out set, and compare repeated baseline/candidate runs. Explain how judge disagreement affects the release decision.

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

