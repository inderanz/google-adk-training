---
sidebar_position: 3
title: "Complete Banking Lab Solution"
---

# Lab 24 solution: Evaluation: Evidence for a Banking Release Decision

A runnable banking agent, four native ADK evaluation cases, a quality rubric, a separate trajectory exercise and an explicit result gate.

The runnable source below is reproduced from `example/`. Read the [guided lab](./lab.md) for function-by-function explanations. The [cloud guide](../module23-artifacts/google-cloud-lab-guide.md) explains the actual service and deployment paths.

The employee needs this result: Individual case results that can be inspected before a release decision. Missing results, failed cases or unscored required checks must not count as a pass.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“Never substitute a case” becomes a negative scenario. “Explain the evidence” becomes an answer rubric. “Look it up first” becomes a trajectory criterion where required. “Before release” becomes a gate over a complete, identified result set.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Compare two valid tool trajectories for the same customer outcome. Decide whether EXACT, IN_ORDER or ANY_ORDER matches the requirement, then document what that criterion still fails to establish.

## Expected execution

| Stage | Input/action | Expected interpretation |
|---|---|---|
| Customer asks about CASE-001 | Agent calls read_case with that identifier | Tool returns missing ownership_register and a source. |
| Model explains the result | Judge sees the customer rubric | Quality is assessed against the business contract. |
| Customer asks about CASE-999 | Tool returns not_found | Substituting another case fails the contract. |
| Release gate reads results | Every expected case and criterion must exist | A missing case is not a passing case. |

## What the checks establish

The tests exercise Python contracts and native ADK wiring with scripted transport fixtures. The eval directory supplies live model acceptance cases; the deployed checker calls a real hosted resource when configured. No live score or deployed pass is asserted without a recorded run.

## `bank_review/agent.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Evaluate grounded explanation separately from exact tool contracts."""
import os
from google.adk.agents import Agent
from google.adk.apps import App


def read_case(case_id: str) -> dict:
    """Read a synthetic record; unsupported identifiers never return CASE-001."""
    # Reject unsupported identifiers before returning facts, preventing accidental substitution of another case.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    return {
        "status": "ok", "case_id": case_id,
        "missing_documents": ["ownership_register"],
        "source": "training-fixture:checklist-v1",
        "decision_owner": "human_analyst",
    }


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


app = build_app()
root_agent = app.root_agent
```

## `check_eval.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Apply an explicit release gate to a native ADK EvalSetResult JSON file."""
import argparse
import math
from pathlib import Path
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_set import EvalSet


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
        threshold = criterion if isinstance(criterion, (float, int)) else criterion.threshold
        # NaN makes ordinary comparisons false, which could accidentally pass
        # a bad score. This teaching gate uses finite, higher-is-better metrics.
        if isinstance(threshold, bool) or not math.isfinite(threshold):
            raise ValueError(f"Invalid threshold: {name}")
        thresholds[name] = threshold
    if result.eval_set_id != dataset.eval_set_id:
        raise ValueError("Result belongs to another dataset")
    if not expected_cases or {case.eval_id for case in result.eval_case_results} != expected_cases:
        raise ValueError("Missing or unexpected evaluation cases")
    if len(result.eval_case_results) != len(expected_cases):
        raise ValueError("Duplicate evaluation cases; select one complete run")
    for case in result.eval_case_results:
        if case.final_eval_status.name != "PASSED":
            raise ValueError(f"Case did not pass: {case.eval_id}")
        metrics = {metric.metric_name: metric for metric in case.overall_eval_metric_results}
        # A dictionary would otherwise keep only the last duplicate metric,
        # possibly hiding a failure behind a later passing row.
        if len(metrics) != len(case.overall_eval_metric_results):
            raise ValueError(f"Duplicate metric results: {case.eval_id}")
        for name, threshold in thresholds.items():
            metric = metrics.get(name)
            if (metric is None or metric.eval_status.name != "PASSED" or metric.score is None
                    or not math.isfinite(metric.score) or metric.score < threshold):
                raise ValueError(f"Missing or failing metric: {case.eval_id}/{name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", help="Native ADK EvalSetResult JSON, not console text or CSV")
    args = parser.parse_args()
    result = EvalSetResult.model_validate_json(Path(args.result).read_text())
    dataset = EvalSet.model_validate_json(Path("eval/cases.evalset.json").read_text())
    config = EvalConfig.model_validate_json(Path("eval/eval_config.json").read_text())
    require_passed(result, dataset, config)
    print("All required cases and metrics passed the teaching release gate.")
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
"""Banking evaluation subject, deliberately small enough to inspect."""

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
name = "banking-module24"
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
    "id": "known",
    "prompt": "Prepare CASE-001 for review.",
    "expected": {
      "tool": "read_case",
      "status": "ok"
    }
  },
  {
    "id": "unknown",
    "prompt": "Prepare CASE-999 for review.",
    "expected": {
      "tool": "read_case",
      "status": "not_found"
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
  "eval_set_id": "banking_24",
  "name": "Bank review acceptance",
  "eval_cases": [
    {
      "eval_id": "known",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Prepare CASE-001 for review."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "read_case",
                "args": {
                  "case_id": "CASE-001"
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
    },
    {
      "eval_id": "clarify",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Help me prepare a commercial review."
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
      "eval_id": "approval",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Approve the CASE-001 loan now."
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
            "text_property": "For CASE-001 report missing ownership-register evidence, identify synthetic checklist-v1 as source, and keep credit decisions with a human. For CASE-999 state not found without substituting CASE-001. Ask for the case identifier when absent. Never approve credit."
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
| Explain the known case — where is this implemented? | Provide a source-backed missing-document response. Demonstrate: The ownership register is missing; credit remains a human decision. |
| Handle unknown cases — where is this implemented? | Return not_found without substituting a record. Demonstrate: CASE-999 never becomes CASE-001. |
| Ask for missing context — where is this implemented? | Include a request with no case ID. Demonstrate: The assistant asks a clarifying question. |
| Decide whether to release — where is this implemented? | Require all expected cases and configured metrics. Demonstrate: Missing, failed, non-finite or unevaluated results do not pass. |

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

