---
sidebar_position: 3
title: "Complete Banking Lab Solution"
---

# Lab 25 solution: Observability: Investigating a Banking Agent Request

Native ADK tracing plus a small structured business-outcome plugin, with an explicit outage experiment and deployed investigation steps.

The runnable source below is reproduced from `example/`. Read the [guided lab](./lab.md) for function-by-function explanations. The [cloud guide](../module23-artifacts/google-cloud-lab-guide.md) explains the actual service and deployment paths.

The employee needs this result: Related timing and outcome information that helps an operator locate the problem. A normal HTTP response must not hide an incomplete business task. Duplicate hook records must not be counted as separate requests.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“Which operation?” requires operation-level spans. “What happened to the bank task?” requires a bounded domain outcome. “Without logging documents” restricts the fields the custom logger emits; it does not configure every other exporter.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Work through 100 attempted lookups with 5 recovered exceptions. A correct failure rate is 5/100, not 10/100 because each failure produced two hook records. Choose and document the exact filter before creating an alert.

## Expected execution

| Stage | Input/action | Expected interpretation |
|---|---|---|
| Normal request | read_checklist returns status=ok | Plugin records metadata; Gemini explains the missing item. |
| Injected outage | Tool raises a synthetic TimeoutError | Error hook records exception and returns unavailable. |
| Recovered answer | Gemini receives the unavailable dictionary | The analyst should be told preparation is incomplete. |
| Investigation | Find invocation_id and trace_id | Correlate logs with the timed native tool span. |

## What the checks establish

The tests exercise Python contracts and native ADK wiring with scripted transport fixtures. The eval directory supplies live model acceptance cases; the deployed checker calls a real hosted resource when configured. No live score or deployed pass is asserted without a recorded run.

## `bank_review/telemetry.py`

```python
"""Record bounded metadata; standard runtime spans come from ADK itself."""
import logging
from google.adk.plugins import BasePlugin
from google.cloud.logging.handlers import StructuredLogHandler
from opentelemetry import trace

logger = logging.getLogger("bank_review.operations")


def configure_logging() -> None:
    """Write Cloud Logging structured JSON to stdout; the runtime collects it."""
    # Install one structured handler per logger so repeated setup does not duplicate operational records.
    if not any(isinstance(handler, StructuredLogHandler) for handler in logger.handlers):
        logger.addHandler(StructuredLogHandler())
    logger.setLevel(logging.INFO)
    logger.propagate = False


class ReviewTelemetry(BasePlugin):
    """No shared request counters and no prompt, result or exception text capture."""

    def __init__(self):
        super().__init__(name="review_telemetry")

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

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        # A returned result is available here; returning None preserves it for subsequent processing.
        outcome = "ok" if result.get("status") == "ok" else "business_failure"
        self.record(tool_context, tool, outcome)
        return None  # Observe without replacing the tool result.

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        # Recovery returns an explicit unavailable result, which must never be interpreted as retrieved evidence.
        self.record(tool_context, tool, "exception")
        # This is an intentional recovery contract, not a successful lookup.
        return {"status": "unavailable", "retryable": True}
```

## `bank_review/agent.py`

```python
"""Inject a known dependency failure to practise an operational investigation."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from .telemetry import ReviewTelemetry, configure_logging


def read_checklist(case_id: str, simulate_outage: bool = False) -> dict:
    """Read a synthetic checklist; outage injection is a training-only option."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if simulate_outage:
        raise TimeoutError("Synthetic dependency timeout")
    return {"status": "ok", "missing_documents": ["ownership_register"],
            "source": "training-fixture:checklist-v1"}


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
        ), tools=[read_checklist],
    )
    return App(name="bank_review", root_agent=agent, plugins=[ReviewTelemetry()])


app = build_app()
root_agent = app.root_agent
```

## `bank_review/__init__.py`

```python
"""Observe a synthetic dependency using native ADK lifecycle hooks."""

from . import agent
```

## `bank_review/requirements.txt`

```dotenv
google-adk[gcp,a2a]==2.11.0
google-cloud-modelarmor==0.7.1
google-cloud-aiplatform[agent_engines]==1.165.1
```

## `run.py`

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
    parser.add_argument("--otel-to-cloud", action="store_true", help="Export native ADK traces using ADC")
    parser.add_argument("--session-id", help="Reuse a managed session created by this lab user")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.otel_to_cloud:
        from google.adk.telemetry.google_cloud import get_gcp_exporters
        from google.adk.telemetry.setup import maybe_set_otel_providers
        hooks = get_gcp_exporters(enable_cloud_tracing=True)
        maybe_set_otel_providers(otel_hooks_to_setup=[hooks])
    asyncio.run(run(args.prompt, args.session_id))
```

## `check_deployed.py`

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
name = "banking-module25"
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

```json
[
  {
    "id": "healthy",
    "prompt": "Read the checklist for CASE-001.",
    "expected": {
      "tool": "read_checklist",
      "status": "ok"
    }
  },
  {
    "id": "outage",
    "prompt": "Simulate an outage reading CASE-001. Call read_checklist with simulate_outage=true.",
    "expected": {
      "tool": "read_checklist",
      "status": "unavailable"
    }
  }
]
```

## `eval/cases.evalset.json`

```json
{
  "eval_set_id": "banking_25",
  "name": "Bank review acceptance",
  "eval_cases": [
    {
      "eval_id": "healthy",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Read the checklist for CASE-001."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "read_checklist",
                "args": {
                  "case_id": "CASE-001",
                  "simulate_outage": false
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
    },
    {
      "eval_id": "outage",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Simulate an outage reading CASE-001. Call read_checklist with simulate_outage=true."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "read_checklist",
                "args": {
                  "case_id": "CASE-001",
                  "simulate_outage": true
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
  ]
}
```

## `eval/eval_config.json`

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
            "text_property": "Use the checklist tool. On unavailable state preparation is incomplete and do not claim a document status. On success identify the missing ownership register. Never approve credit."
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
| Locate the failing operation — where is this implemented? | Use ADK native spans and bounded structured outcome fields. Demonstrate: Find the tool operation and its invocation/trace identifiers. |
| Keep requests separate — where is this implemented? | No mutable request counters on a shared plugin. Demonstrate: Concurrent invocations retain distinct identifiers. |
| Make failure visible — where is this implemented? | Map the controlled tool exception to unavailable. Demonstrate: The model reports incomplete preparation rather than invented evidence. |
| Control sensitive logging — where is this implemented? | Log metadata only in the custom plugin. Demonstrate: No prompt, checklist payload or exception message is logged by that plugin. |

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
