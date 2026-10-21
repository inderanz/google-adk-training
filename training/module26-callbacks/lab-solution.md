---
sidebar_position: 3
title: "Complete Banking Lab Solution"
---

# Lab 26 solution: Callbacks: Agent Lifecycle and Banking Tool Controls

Six explained agent callbacks, real ADK short-circuit tests, validated tool inputs and multipart-preserving response modification.

The runnable source below is reproduced from `example/`. Read the [guided lab](./lab.md) for function-by-function explanations. The [cloud guide](../module23-artifacts/google-cloud-lab-guide.md) explains the actual service and deployment paths.

The employee needs this result: A valid lookup result or a clear input error; the human still owns the credit decision. An invalid request must not execute the tool body. A response change must preserve unrelated response fields.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

“Reject before lookup” motivates before_tool. “Still reject direct calls” requires validation inside the tool too. “Preserve function calls while changing text” requires copying the response parts selectively rather than rebuilding a text-only response.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Compose a plugin and agent callback that both return replacements. Record which one wins, which hooks are skipped and whether any safety check can be bypassed by that ordering.

## Expected execution

| Stage | Input/action | Expected interpretation |
|---|---|---|
| Request max_items=99 | Model proposes the requested arguments | before_tool returns invalid_limit; lookup is skipped. |
| Model receives error | Conversation can continue | It should explain the invalid input rather than claim success. |
| Exact laboratory command | before_model returns a fixed LlmResponse | The scripted model has no replies and must not be called. |
| Multipart output edit | Second text part contains the marker | Only affected text changes; function calls and response metadata survive. |

## What the checks establish

The tests exercise Python contracts and native ADK wiring with scripted transport fixtures. The eval directory supplies live model acceptance cases; the deployed checker calls a real hosted resource when configured. No live score or deployed pass is asserted without a recorded run.

## `bank_review/controls.py`

```python
"""Small callback contracts; these are not a general content-safety system."""
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types


def validate_request(case_id, max_items) -> dict | None:
    """Reject booleans as integers and unsupported scope before any lookup."""
    # Validate at the reusable business boundary because direct calls can bypass agent callbacks.
    if case_id != "CASE-001":
        return {"status": "not_found"}
    if type(max_items) is not int or not 1 <= max_items <= 5:
        return {"status": "invalid_limit", "allowed_range": "1..5"}
    return None


def read_checklist(case_id: str, max_items: int = 5) -> dict:
    """The tool validates even when called without the ADK callback."""
    # Return a bounded synthetic lookup; real case access requires an authorized repository.
    problem = validate_request(case_id, max_items)
    if problem is not None:
        return problem
    return {"status": "ok", "case_id": case_id,
            "missing_documents": ["ownership_register"][:max_items],
            "source": "training-fixture:checklist-v1"}


def before_agent(callback_context: CallbackContext) -> types.Content | None:
    # Initialize invocation-scoped diagnostic state before this agent starts its work.
    callback_context.state["temp:checks"] = []
    return None


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


def before_tool(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None:
    # Reuse the tool’s validator to reject invalid work before executing the resolved tool body.
    if tool.name != "read_checklist":
        return None
    problem = validate_request(args.get("case_id"), args.get("max_items", 5))
    checks = list(tool_context.state.get("temp:checks", []))
    checks.append("blocked" if problem is not None else "validated")
    tool_context.state["temp:checks"] = checks
    return problem  # A dictionary replaces this tool execution; None allows it.


def after_tool(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None:
    # Add human ownership only to successful lookup results without rewriting failure outcomes.
    if tool.name == "read_checklist" and tool_response.get("status") == "ok":
        return {**tool_response, "decision_owner": "human_analyst"}
    return None


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


def after_agent(callback_context: CallbackContext) -> types.Content | None:
    # Tracked state assignment can emit a state-only event after the text response.
    callback_context.state["last_review_invocation"] = callback_context.invocation_id
    return None
```

## `bank_review/agent.py`

```python
"""Attach local lifecycle callbacks to one agent, not to every agent globally."""
import os
from google.adk.agents import Agent
from google.adk.apps import App
from . import controls


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


# One package can expose either the isolated lesson or the integrated exercise.
# The environment is configured by the operator, never by a user prompt.
if os.environ.get("BANKING_CAPSTONE") == "true":
    from .capstone import build_capstone
    app = build_capstone()
else:
    app = build_app()
root_agent = app.root_agent
```

## `bank_review/__init__.py`

```python
"""Agent-specific controls, with authoritative validation inside the tool."""

from . import agent
```

## `bank_review/requirements.txt`

```dotenv
google-adk[gcp,a2a]==2.11.0
google-cloud-modelarmor==0.7.1
google-cloud-firestore==2.33.0
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
    parser.add_argument("--session-id", help="Reuse a managed session created by this lab user")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
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
name = "banking-module26"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["google-adk[gcp,a2a]==2.11.0", "google-cloud-modelarmor==0.7.1", "google-cloud-aiplatform[agent_engines]==1.165.1", "google-cloud-firestore==2.33.0"]

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

# Enable only for the integrated exercise and its ADK deployment/evaluation.
BANKING_CAPSTONE=false
FIRESTORE_DATABASE=(default)
```

## `deployed-cases.json`

```json
[
  {
    "id": "valid",
    "prompt": "Read CASE-001 with max_items=1.",
    "expected": {
      "tool": "read_checklist",
      "status": "ok"
    }
  },
  {
    "id": "invalid",
    "prompt": "Read CASE-001 with max_items=99. Pass the value exactly.",
    "expected": {
      "tool": "read_checklist",
      "status": "invalid_limit"
    }
  },
  {
    "id": "short_circuit",
    "prompt": "LAB:REQUEST_CREDIT_APPROVAL",
    "expected": {
      "contains": "A human analyst must make the credit decision."
    }
  }
]
```

## `eval/cases.evalset.json`

```json
{
  "eval_set_id": "banking_26",
  "name": "Bank review acceptance",
  "eval_cases": [
    {
      "eval_id": "valid",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Read CASE-001 with max_items=1."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "read_checklist",
                "args": {
                  "case_id": "CASE-001",
                  "max_items": 1
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
      "eval_id": "invalid",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Read CASE-001 with max_items=99. Pass the value exactly."
              }
            ]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "read_checklist",
                "args": {
                  "case_id": "CASE-001",
                  "max_items": 99
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
      "eval_id": "short_circuit",
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "LAB:REQUEST_CREDIT_APPROVAL"
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
            "text_property": "Report validation failures without silently changing max_items. For valid lookup use the supplied evidence and human decision ownership. Do not claim credit approval."
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
| Bound requested work — where is this implemented? | Validate max_items as an integer from 1 to 5. Demonstrate: Booleans, strings and out-of-range values are rejected. |
| Validate at the durable boundary — where is this implemented? | Repeat the validation inside the callable tool. Demonstrate: Direct Python calls cannot bypass the input contract. |
| Understand interception — where is this implemented? | Demonstrate None versus replacement return values. Demonstrate: A blocked tool is not executed; the model can explain the error. |
| Preserve response structure — where is this implemented? | Copy only changed text parts and retain other fields. Demonstrate: A later text part is changed without losing an accompanying function call. |

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
