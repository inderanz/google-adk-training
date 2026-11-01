---
sidebar_position: 3
title: "Complete Banking Lab Solution"
---

# Lab 23 solution: Artifacts: Reproducible Banking Review Packs

A source artifact, Markdown report and manifest identifying exact versions; managed Sessions and Cloud Storage on the real-service path.

The runnable source below is reproduced from `example/`. Read the [guided lab](./lab.md) for function-by-function explanations. The [cloud guide](../module23-artifacts/google-cloud-lab-guide.md) explains the actual service and deployment paths.

The employee needs this result: A saved checklist, report and small linking record identifying their versions. Missing or invalid source content must not produce a successful report. Failed saves may need later cleanup.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“The exact input reviewed” requires an explicit version. “Which report used it” requires a manifest. “Survive restart” selects GcsArtifactService. “Still retrieve earlier evidence” means never silently substitute latest during replay.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Choose recovery for a report saved before a failed manifest save: permit an orphan and reconcile it, or coordinate a committed business record. Explain why neither a digest nor three successful writes creates a transaction.

## Expected execution

| Stage | Input/action | Expected interpretation |
|---|---|---|
| save_checklist | Synthetic checklist has ownership_register=false | Storage returns source version 0 in a fresh scope. |
| create_review_pack(0) | Load and validate the exact saved bytes | Missing ownership_register is derived in Python. |
| Save report | Markdown names the input version | Storage returns a report version. |
| Save manifest | Link source digest and both versions | Return prepared_for_human_review, never approved. |

## What the checks establish

The tests exercise Python contracts and native ADK wiring with scripted transport fixtures. The eval directory supplies live model acceptance cases; the deployed checker calls a real hosted resource when configured. No live score or deployed pass is asserted without a recorded run.

## `bank_review/tools.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Create an evidence pack with exact input versions, using native ADK artifacts."""
import hashlib
import json

from google.adk.tools import ToolContext
from google.genai import types

SOURCE_NAME = "CASE-001-checklist.json"
REPORT_NAME = "CASE-001-review.md"
MANIFEST_NAME = "CASE-001-manifest.json"


def json_part(value: dict) -> types.Part:
    """Use UTF-8 bytes and an explicit media type for a portable JSON artifact."""
    # Artifacts store typed bytes, so serialize the dictionary and declare how those bytes are interpreted.
    data = json.dumps(value, sort_keys=True, indent=2).encode("utf-8")
    return types.Part.from_bytes(data=data, mime_type="application/json")


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
    if (case.get("case_id") != "CASE-001" or not isinstance(documents, dict)
            or set(documents) != required
            or any(type(value) is not bool for value in documents.values())):
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
        artifact=types.Part.from_bytes(data=report.encode("utf-8"), mime_type="text/markdown"),
    )
    manifest = {
        "case_id": "CASE-001",
        "source": {"filename": SOURCE_NAME, "version": source_version,
                   "sha256": hashlib.sha256(raw).hexdigest()},
        "report": {"filename": REPORT_NAME, "version": report_version},
        "status": "prepared_for_human_review",
    }
    # Save the manifest last. These saves are not one atomic transaction.
    manifest_version = await tool_context.save_artifact(
        filename=MANIFEST_NAME, artifact=json_part(manifest)
    )
    return {**manifest, "manifest_version": manifest_version}
```

## `bank_review/agent.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""The agent chooses tools; each tool enforces its own data contract."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .tools import create_review_pack, save_checklist


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


app = build_app()
root_agent = app.root_agent
```

## `verify_pack.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Read an actual deployed pack back from GCS using its exact saved scope/versions."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
from google.adk.artifacts import GcsArtifactService


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
    outcome = next(value for value in outputs if value.get("status") == "prepared_for_human_review")
    # A new client/process reads the data; nothing relies on the earlier Runner.
    service = GcsArtifactService(bucket_name=os.environ["ARTIFACT_BUCKET"])
    scope = {"app_name": "bank_review", "user_id": case["user_id"], "session_id": case["session_id"]}
    manifest_part = await service.load_artifact(
        **scope, filename="CASE-001-manifest.json", version=outcome["manifest_version"])
    if not manifest_part or not manifest_part.inline_data:
        raise AssertionError("Saved manifest could not be read back")
    manifest = json.loads(manifest_part.inline_data.data)
    source = await service.load_artifact(**scope, **{
        key: manifest["source"][key] for key in ("filename", "version")})
    saved_report = await service.load_artifact(**scope, **manifest["report"])
    if not source or not source.inline_data or not saved_report or not saved_report.inline_data:
        raise AssertionError("An exact referenced artifact version is missing")
    digest = hashlib.sha256(source.inline_data.data).hexdigest()
    if digest != manifest["source"]["sha256"]:
        raise AssertionError("Source digest does not match the manifest")
    if manifest["report"] != outcome["report"]:
        raise AssertionError("Returned report and saved manifest disagree")
    if b"ownership_register" not in saved_report.inline_data.data:
        raise AssertionError("Fixture report does not contain the expected missing item")
    return {"status": "verified_from_gcs", "source": manifest["source"], "report": manifest["report"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", nargs="?", default="deployment-results.json")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(verify(args.report)), indent=2))
```

## `bank_review/__init__.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Fictional bank review application; see agent.py for the ADK entry point."""

from . import agent
```

## `bank_review/requirements.txt`

```dotenv
google-adk[gcp,a2a]==2.11.0
google-cloud-modelarmor==0.7.1
google-cloud-aiplatform[agent_engines]==1.165.1
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
"""Run locally against real Gemini, managed Sessions and GCS services.

The agent executes in this Python process. check_deployed.py instead invokes
an agent already hosted on Agent Runtime. Both use synthetic bank records.
"""
import argparse
import asyncio
import json
import logging
import os
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.artifacts import GcsArtifactService
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types
from bank_review.agent import app


async def run(prompt: str, session_id: str | None):
    sessions = VertexAiSessionService(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["AGENT_RUNTIME_LOCATION"],
        agent_engine_id=os.environ["AGENT_ENGINE_ID"],
    )
    artifacts = GcsArtifactService(bucket_name=os.environ["ARTIFACT_BUCKET"])
    user_id = "training-analyst"  # Synthetic scope identifier, not authentication.
    if session_id is None:
        session = await sessions.create_session(app_name=app.name, user_id=user_id)
        session_id = session.id
    print(json.dumps({"session_id": session_id, "user_id": user_id}))
    async with Runner(app=app, session_service=sessions, artifact_service=artifacts) as runner:
        async with asyncio.timeout(90):
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                run_config=RunConfig(max_llm_calls=8, streaming_mode=StreamingMode.NONE),
            ):
                # This diagnostic output is for synthetic lab data only.
                print(event.model_dump_json(exclude_none=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", default="Prepare CASE-001 for human review.")
    parser.add_argument("--session-id", help="Reuse a managed session created by this lab user")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run(args.prompt, args.session_id))
```

## `check_deployed.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Call the native ADK HTTP surface of an already deployed Agent Runtime.

Supply a full resource name, not an arbitrary host. ADC signs HTTPS requests.
The report contains synthetic event data and is saved locally for review.
"""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import re
import uuid
import google.auth
from google.auth.transport.requests import AuthorizedSession


def check(events: list, expected: dict) -> None:
    responses = [part["functionResponse"] for event in events
                 for part in (event.get("content") or {}).get("parts", [])
                 if "functionResponse" in part]
    # ADK HTTP serialization can use Python field names instead of JSON aliases.
    responses += [part["function_response"] for event in events
                  for part in (event.get("content") or {}).get("parts", [])
                  if "function_response" in part]
    if expected.get("tool"):
        candidates = [item["response"] for item in responses if item.get("name") == expected["tool"]]
        if not any(item.get("status") == expected["status"] for item in candidates):
            raise AssertionError(f"Missing expected tool outcome: {expected}")
    final_text = "\n".join(part.get("text", "") for event in events
                           for part in (event.get("content") or {}).get("parts", []))
    if expected.get("contains") and expected["contains"] not in final_text:
        raise AssertionError("Expected control response was absent")
    if not final_text:
        raise AssertionError("No text response; inspect the deployment events")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", required=True, help="projects/P/locations/L/reasoningEngines/ID")
    parser.add_argument("--output", default="deployment-results.json")
    args = parser.parse_args()
    match = re.fullmatch(r"projects/([a-zA-Z0-9-]+)/locations/([a-z0-9-]+)/reasoningEngines/([a-zA-Z0-9-]+)", args.resource)
    if match is None:
        raise SystemExit("Expected a complete Agent Runtime resource name")
    region = match.group(2)
    base = f"https://{region}-aiplatform.googleapis.com/reasoningEngines/v1/{args.resource}/api"
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    report = {"resource": args.resource, "started_at": datetime.now(timezone.utc).isoformat(),
              "adk_version": version("google-adk"), "cases": [], "passed": False}
    try:
        with AuthorizedSession(credentials) as client:
            for case in json.loads(Path("deployed-cases.json").read_text()):
                user = "training-" + uuid.uuid4().hex
                response = client.post(f"{base}/apps/bank_review/users/{user}/sessions", json={}, timeout=30)
                response.raise_for_status()
                session_id = response.json()["id"]
                response = client.post(f"{base}/run", json={
                    "app_name": "bank_review", "user_id": user, "session_id": session_id,
                    "new_message": {"role": "user", "parts": [{"text": case["prompt"]}]},
                }, timeout=120)
                response.raise_for_status()
                events = response.json()
                report["cases"].append({"id": case["id"], "user_id": user, "session_id": session_id, "events": events})
                check(events, case["expected"])
        report["passed"] = True
    finally:
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(f"Deployed checks passed; inspect {args.output} and the matching cloud telemetry.")


if __name__ == "__main__":
    main()
```

## `pyproject.toml`

```toml
[project]
name = "banking-module23"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["google-adk[gcp,a2a]==2.11.0", "google-cloud-modelarmor==0.7.1", "google-cloud-aiplatform[agent_engines]==1.165.1"]

[project.optional-dependencies]
eval = ["google-adk[eval]==2.11.0"]

[tool.uv]
package = false
```

## `.env.example`

```dotenv
# Values below name resources; do not put credentials in this file.
GOOGLE_GENAI_USE_ENTERPRISE=true
ADK_MAX_LLM_CALLS=8
ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT
GOOGLE_CLOUD_PROJECT=YOUR_DEVELOPMENT_PROJECT
# Gemini model location can differ from the managed-service regions.
GOOGLE_CLOUD_LOCATION=global
GEMINI_MODEL=gemini-3.5-flash
AGENT_RUNTIME_LOCATION=us-central1
AGENT_ENGINE_ID=YOUR_EXISTING_RUNTIME_ID
ARTIFACT_BUCKET=YOUR_DEDICATED_LAB_BUCKET
# Required only for Module 25.5; must name an existing configured template.
MODEL_ARMOR_TEMPLATE=projects/YOUR_DEVELOPMENT_PROJECT/locations/us-central1/templates/YOUR_TEMPLATE
```

## `deployed-cases.json`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```json
[
  {
    "id": "pack",
    "prompt": "Prepare CASE-001 review pack. Save the checklist then use its returned version.",
    "expected": {
      "tool": "create_review_pack",
      "status": "prepared_for_human_review"
    }
  }
]
```

## `eval/cases.evalset.json`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```json
{
  "eval_set_id": "banking_23",
  "name": "Bank review acceptance",
  "eval_cases": [
    {
      "eval_id": "pack",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Prepare CASE-001 review pack. Save the checklist then use its returned version."
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
  ]
}
```

## `eval/eval_config.json`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```json
{
  "criteria": {
    "rubric_based_final_response_quality_v1": {
      "threshold": 1,
      "judge_model_options": {
        "judge_model": "gemini-3.5-flash",
        "num_samples": 3
      },
      "rubrics": [
        {
          "rubric_id": "customer_contract",
          "rubric_content": {
            "text_property": "Use the actual tool results for filenames and versions. State preparation for human review, not credit approval. Never invent completed artifacts after a failed operation."
          }
        }
      ]
    }
  }
}
```

## Review questions and expected reasoning

| Question | Expected reasoning |
|---|---|
| Preserve the reviewed input — where is this implemented? | Save a named JSON artifact and retain the returned integer version. Demonstrate: An older version remains readable after a later save. |
| Link report to evidence — where is this implemented? | Load the requested source version and record a SHA-256 digest. Demonstrate: The manifest names that input version and the report version. |
| Handle missing/invalid input — where is this implemented? | Return explicit failure before writing the report. Demonstrate: Missing evidence does not produce a success-shaped report. |
| Persist across processes — where is this implemented? | Use GcsArtifactService and managed Sessions. Demonstrate: A new client can retrieve the saved version in the same scope. |

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

