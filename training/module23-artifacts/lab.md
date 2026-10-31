---
sidebar_position: 2
title: "Guided Banking Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 23: Artifacts: Reproducible Banking Review Packs

**What you are practising:** Artifacts, versions and storage providers in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Start with the customer, not an import statement

### Read this as a bank employee's task

An analyst reviews a checklist and a generated report today. Tomorrow the checklist may change. The bank needs to retrieve the exact input and report used for today’s review.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Save the checklist used for each report. Keep a way to find the exact saved version later, even after the case changes.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A checklist snapshot and the explicit saved source version used to prepare the report. |
| What should the employee receive? | A saved checklist, report and small linking record identifying their versions. |
| What should happen when it cannot be completed? | Missing or invalid source content must not produce a successful report. Failed saves may need later cleanup. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Artifact | A file-like item saved through ADK, such as a JSON checklist or Markdown report. |
| Manifest | A small record listing which saved input and output belong together. |
| Digest | A value calculated from bytes to detect a change; it does not prove who supplied them. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Write the desired outcome in one sentence, then identify inputs, operations, outputs and failure outcomes. Separate a verified source value from something a model inferred. The following specification makes the fictional exercise executable; a customer’s data owner and policy owner must supply real requirements.

| Requirement | Code decision | Acceptance check |
|---|---|---|
| Preserve the reviewed input | Save a named JSON artifact and retain the returned integer version | An older version remains readable after a later save. |
| Link report to evidence | Load the requested source version and record a SHA-256 digest | The manifest names that input version and the report version. |
| Handle missing/invalid input | Return explicit failure before writing the report | Missing evidence does not produce a success-shaped report. |
| Persist across processes | Use GcsArtifactService and managed Sessions | A new client can retrieve the saved version in the same scope. |

## Set up the reference and your practice copy

<Setup/>

From the repository root:

```bash
cd training/module23-artifacts/example
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

The first command selects this example. `uv sync` creates its isolated environment from the dependency lock. The tests require no cloud credentials and use deterministic transport fixtures. They are the software-contract checkpoint, not completion of the real-service lab. Work in a copy when deliberately breaking behavior.

Complete [Google Cloud setup](../module23-artifacts/google-cloud-lab-guide.md#configure-a-real-service-run) before the live steps. It explains project selection, service identity, managed resource names, regions and configuration. Do not replace Google service calls with mock implementations and label the result a deployed test.

## Build the mental model

| English requirement | Coding step | How to check understanding |
|---|---|---|
| Preserve the reviewed input | Save a named JSON artifact and retain the returned integer version | An older version remains readable after a later save. |
| Link report to evidence | Load the requested source version and record a SHA-256 digest | The manifest names that input version and the report version. |
| Handle missing/invalid input | Return explicit failure before writing the report | Missing evidence does not produce a success-shaped report. |
| Persist across processes | Use GcsArtifactService and managed Sessions | A new client can retrieve the saved version in the same scope. |

Use the existing runner and dependency setup. Rebuild the lesson functions in a practice copy one at a time: first define the input/output contract, then add validation, then connect the native ADK API, then exercise a failure path. Predict the trace before opening the complete solution.

## Files and responsibilities

| File | Responsibility |
|---|---|
| bank_review/tools.py | Lesson implementation, explained below |
| bank_review/agent.py | Lesson implementation, explained below |
| verify_pack.py | Lesson implementation, explained below |
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

**Derivation:** “The exact input reviewed” requires an explicit version. “Which report used it” requires a manifest. “Survive restart” selects GcsArtifactService. “Still retrieve earlier evidence” means never silently substitute latest during replay.

Do these checkpoints in a practice copy. Keep the reference available, but predict the data and execution before reading its answer.

| Checkpoint | What you produce | Evidence to retain |
|---|---|---|
| 1. Customer contract | One normal request and one failure request in English | Expected business outcome for each |
| 2. Data contract | A concrete input and output for the lesson operation | Explain every field's source and consumer |
| 3. Small implementation | The first relevant function below, with comments explaining the requirement | Run its contract check before adding orchestration |
| 4. Native ADK wiring | The supplied factory, context or provider configuration | Identify who calls your function and who reads its return |
| 5. Execution | Predict, then run the supplied scenario | Actual event/tool result compared with the prediction |
| 6. Failure | Change one condition without changing the acceptance rule | A failure result and explanation of the responsible boundary |

**Module-specific observation:** Save once, retain version 0, save changed bytes again, then load both explicit versions. Inspect the artifact delta in the saved events and compare it with the complete loaded Part.

**Transfer to a changed customer requirement:** Choose recovery for a report saved before a failed manifest save: permit an orphan and reconcile it, or coordinate a committed business record. Explain why neither a digest nor three successful writes creates a transaction.

The complete lab command below runs the software checks. Read the test names and retain the case relevant to your checkpoint. These tests establish code contracts; real Gemini evaluation and cloud evidence remain separate completion requirements.

## Read and implement the code in small pieces

The blocks below follow the runnable files. Class-method excerpts belong inside their named class; the complete solution shows their indentation and constructor together. Read the explanation, predict the behavior, then run the relevant test.

### bank_review/tools.py

```python
import hashlib
import json
from google.adk.tools import ToolContext
from google.genai import types
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### json_part

`json.dumps` serializes a dictionary; sorting keys gives stable ordering for these values. Encoding produces UTF-8 bytes. The explicit JSON MIME type lets the reader reject a different kind of artifact. The digest later covers these exact bytes, not a reserialized approximation.

```python
def json_part(value: dict) -> types.Part:
    """Use UTF-8 bytes and an explicit media type for a portable JSON artifact."""
    # Artifacts store typed bytes, so serialize the dictionary and declare how those bytes are interpreted.
    data = json.dumps(value, sort_keys=True, indent=2).encode("utf-8")
    return types.Part.from_bytes(data=data, mime_type="application/json")
```

#### save_checklist

The function accepts only injected ToolContext, so the model cannot choose another user or session namespace. Its dictionary is explicitly a fictional source snapshot. `await` waits for the native save. The returned version is passed onwards, including when it is zero; do not test it with `if version:`.

```python
async def save_checklist(tool_context: ToolContext) -> dict:
    """Save the supplied fictional checklist; this does not read a bank system."""
    # Retain the version returned by ADK rather than predicting a version that another writer could change.
    checklist = {
        "case_id": "CASE-001",
        "source": "training-fixture:checklist-v1",
        "documents": {"financial_statements": True, "ownership_register": False},
    }
    version = await tool_context.save_artifact(
        filename=SOURCE_NAME, artifact=json_part(checklist)
    )
    return {"status": "saved", "filename": SOURCE_NAME, "version": version}
```

#### create_review_pack

Read the guard clauses before the happy path. `type(value) is int` rejects Python booleans, which otherwise behave like integers. `load_artifact(..., version=...)` pins the evidence. Check MIME type and byte bound before parsing, then require the expected document keys and Boolean values. This avoids treating an empty checklist as complete. The comprehension derives the missing-document names. Each await saves one artifact; the final manifest links those saves. Errors from storage propagate instead of being mislabeled as successful completion.

```python
async def create_review_pack(source_version: int, tool_context: ToolContext) -> dict:
    """Build a report from one exact version; never silently switch to latest."""
    # Validate and load the requested evidence before any report save; never substitute the latest version.
    if type(source_version) is not int or source_version < 0:
        return {"status": "invalid_version"}
    source = await tool_context.load_artifact(SOURCE_NAME, version=source_version)
    if source is None:
        return {"status": "source_missing", "version": source_version}
    if not source.inline_data or source.inline_data.mime_type != "application/json":
        return {"status": "invalid_source"}
    raw = source.inline_data.data
    if not raw or len(raw) > 16_384:
        return {"status": "invalid_source"}
    try:
        case = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return {"status": "invalid_source"}
    required = {"financial_statements", "ownership_register"}
    if not isinstance(case, dict):
        return {"status": "invalid_source"}
    documents = case.get("documents")
    if (
        case.get("case_id") != "CASE-001"
        or not isinstance(documents, dict)
        or set(documents) != required
        or any(type(value) is not bool for value in documents.values())
    ):
        return {"status": "invalid_source"}
    missing = sorted(name for name, received in documents.items() if not received)
    report = (
        "# CASE-001 review preparation\n\n"
        f"Checklist artifact: {SOURCE_NAME}, version {source_version}.\n\n"
        f"Missing documents: {', '.join(missing) if missing else 'none'}.\n\n"
        "Synthetic evidence only. A human analyst owns the credit decision.\n"
    )
    report_version = await tool_context.save_artifact(
        filename=REPORT_NAME,
        artifact=types.Part.from_bytes(
            data=report.encode("utf-8"), mime_type="text/markdown"
        ),
    )
    manifest = {
        "case_id": "CASE-001",
        "source": {
            "filename": SOURCE_NAME,
            "version": source_version,
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "report": {"filename": REPORT_NAME, "version": report_version},
        "status": "prepared_for_human_review",
    }
    # Save the manifest last. These saves are not one atomic transaction.
    manifest_version = await tool_context.save_artifact(
        filename=MANIFEST_NAME, artifact=json_part(manifest)
    )
    return {**manifest, "manifest_version": manifest_version}
```

### bank_review/agent.py

```python
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .tools import create_review_pack, save_checklist
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### build_app

The factory constructs an Agent and App; it does not run Gemini. Tool functions are passed as callable objects, without parentheses. ADK turns their signatures into tool schemas and injects ToolContext at execution. The exported app is also what deployment loads.

```python
def build_app(model=None) -> App:
    # Attach the configured root agent to an App; provider services are supplied by Runner.
    agent = Agent(
        name="review_pack_assistant",
        model=model or os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        instruction=(
            "Prepare a fictional CASE-001 review pack. Call save_checklist, then "
            "pass its returned version to create_review_pack. Never invent a version. "
            "Report the filenames and versions returned by the tools. If a tool fails, "
            "report incomplete preparation. No real evidence lookup or approval occurs."
        ),
        tools=[save_checklist, create_review_pack],
    )
    return App(name="bank_review", root_agent=agent)
```

### verify_pack.py

```python
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
from google.adk.artifacts import GcsArtifactService
```

Imports make the documented Python, Google and ADK names available. Relative imports beginning with `.` load another file in this package.

#### verify

Read the deployed checker report and find the actual create_review_pack result. Use its test user/session scope with a new GcsArtifactService client. Load the saved manifest version, then the exact source/report references recorded there. Recompute the digest from retrieved bytes and compare it; also check the returned report reference and the fixture content. This proves readback from the configured bucket when run against real GCS, not merely that an earlier save returned an integer.

```python
async def verify(report_path: str) -> dict:
    # Read the exact referenced objects using a fresh provider, then compare bytes and scope.
    report = json.loads(Path(report_path).read_text())
    case = next(case for case in report["cases"] if case["id"] == "pack")
    outputs = []
    for event in case["events"]:
        for part in (event.get("content") or {}).get("parts", []):
            response = part.get("function_response") or part.get("functionResponse")
            if response and response["name"] == "create_review_pack":
                outputs.append(response["response"])
    outcome = next(
        value for value in outputs if value.get("status") == "prepared_for_human_review"
    )
    # A new client/process reads the data; nothing relies on the earlier Runner.
    service = GcsArtifactService(bucket_name=os.environ["ARTIFACT_BUCKET"])
    scope = {
        "app_name": "bank_review",
        "user_id": case["user_id"],
        "session_id": case["session_id"],
    }
    manifest_part = await service.load_artifact(
        **scope, filename="CASE-001-manifest.json", version=outcome["manifest_version"]
    )
    if not manifest_part or not manifest_part.inline_data:
        raise AssertionError("Saved manifest could not be read back")
    manifest = json.loads(manifest_part.inline_data.data)
    source = await service.load_artifact(
        **scope, **{key: manifest["source"][key] for key in ("filename", "version")}
    )
    saved_report = await service.load_artifact(**scope, **manifest["report"])
    if (
        not source
        or not source.inline_data
        or not saved_report
        or not saved_report.inline_data
    ):
        raise AssertionError("An exact referenced artifact version is missing")
    digest = hashlib.sha256(source.inline_data.data).hexdigest()
    if digest != manifest["source"]["sha256"]:
        raise AssertionError("Source digest does not match the manifest")
    if manifest["report"] != outcome["report"]:
        raise AssertionError("Returned report and saved manifest disagree")
    if b"ownership_register" not in saved_report.inline_data.data:
        raise AssertionError(
            "Fixture report does not contain the expected missing item"
        )
    return {
        "status": "verified_from_gcs",
        "source": manifest["source"],
        "report": manifest["report"],
    }
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
uv run --env-file .env python run.py "Prepare CASE-001 review pack. Save the checklist then use its returned version."
```

| Experiment | Evidence to inspect |
|---|---|
| Prepare a fresh pack | Inspect function responses and record the returned source/report/manifest versions. |
| Request source version 999 before saving it | Expect source_missing and no new report. |
| Save the same source name again | Expect a new version; retrieve both versions explicitly. |
| Load with another test user/session | Expect no access through that namespace; separately test real API authorization. |

Use synthetic inputs. Live model calls, storage, inspection and telemetry can incur charges. Record the observed results rather than copying the expected outcome into a test report.

## Verify the hosted application

Deploy through the [native Agent Runtime path](../module23-artifacts/google-cloud-lab-guide.md#deploy-the-reviewed-package-to-agent-runtime), then run:

```bash
uv run --env-file .env python check_deployed.py \
  --resource projects/PROJECT/locations/REGION/reasoningEngines/RUNTIME_ID
```

Open `deployment-results.json`. Check the selected resource, each test session, tool calls/results and final explanation. Complete the module-specific service evidence in the enterprise playbook. A passing HTTP response alone is insufficient. The supplied checker uses non-streaming `/run`; it does not validate token streaming.

## Advanced customer variation

Replace the source fixture with the authorized Module 13.5 repository adapter. Preserve its case version and observation timestamp, specify idempotency for retries, and describe how partially saved packs are reconciled.

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
