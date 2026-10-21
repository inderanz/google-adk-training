---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 15 solution: Introduction to Multi-Agent Systems

A coordinator consults a document adviser and then answers the analyst. Both roles are advisory; neither reads current case status.

The employee needs this result: An explanation from the coordinator, using advice from a document specialist when it calls that specialist. A receipt question must not receive an invented status; this example has no current-case lookup.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

The customer wants one explanation with specialist advice, so use call-and-return. If the requirement changes to direct dialogue with the specialist, reconsider delegation. If the checklist explanation fits one instruction, compare the simpler one-agent baseline before paying for a second reasoning step.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Design a second adviser whose output conflicts with the first. State which source is authoritative and how the coordinator should report disagreement.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Explain required evidence | A narrowly instructed document adviser | The explanation covers financial statements and an ownership register. |
| Keep one conversational owner | AgentTool call-and-return | The coordinator receives the specialist result and produces the response. |
| Do not invent case status | No case-read capability in this example; state the limitation | A receipt/status question results in a request for an authorized lookup. |
| Do not approve or execute | No approval or payment tool | No state-changing banking operation is available. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Expression | Meaning for a new Python learner | Why the bank needs it |
|---|---|---|
| `from ... import Agent` | Import a public class from an installed package | Reuse ADK rather than implement an agent runtime |
| `model=None` | Optional argument with a default value | The same factory supports a real or scripted model |
| `selected_model = ...` | Assign a local variable | Both roles use explicit configuration |
| `Agent(...)` | Construct an object using named fields | Make responsibility and capability visible |
| `AgentTool(agent=...)` | Wrap an agent in ADK’s tool interface | Preserve call-and-return behavior |
| `return Agent(...)` | Give the constructed coordinator to the caller | Runner owns execution; construction makes no model request |

## `pyproject.toml`

```toml
[project]
name = "banking-module-15"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["google-adk==2.11.0"]

[tool.uv]
package = false
```

## `.env.example`

```dotenv
GOOGLE_GENAI_USE_ENTERPRISE=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GEMINI_MODEL=gemini-3.8-flash
```

## `bank_case/agent.py`

```python
"""Two advisory roles; the coordinator calls a specialist and resumes."""
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


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

## `runtime.py`

```python
"""Run one synthetic request through the real ADK runtime."""
import asyncio
import json

from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types


async def run_once(agent, payload):
    # This identity is a fixture, never an authentication implementation.
    async with InMemoryRunner(app=App(name="bank_case", root_agent=agent)) as runner:
        session = await runner.session_service.create_session(
            app_name="bank_case", user_id="analyst-demo"
        )
        message = types.Content(
            role="user", parts=[types.Part.from_text(text=json.dumps(payload))]
        )
        events = []
        # The deadline bounds the invocation; it cannot undo external writes.
        async with asyncio.timeout(60):
            async for event in runner.run_async(
                user_id="analyst-demo", session_id=session.id,
                new_message=message, run_config=RunConfig(max_llm_calls=12),
            ):
                events.append(event)
        return events


def display(events):
    for event in events:
        if event.output is not None:
            print(json.dumps({"author": event.author, "output": event.output}))
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"{event.author}: {part.text}")
```

## `run.py`

```python
"""Choose a real prompt; credentials are needed only after argument parsing."""
import argparse
import asyncio
import os
from bank_case.agent import build_agent
from runtime import display, run_once

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask about fictional bank review preparation")
    parser.add_argument("prompt", nargs="?", default="Explain how to prepare CASE-001 for review.")
    args = parser.parse_args()
    if not os.environ.get("GEMINI_MODEL"):
        raise SystemExit("Load .env using: uv run --env-file .env python run.py")
    agent = build_agent()
    display(asyncio.run(run_once(agent, args.prompt)))
```

## Explain the implementation to a reviewer

### `build_agent`

`model=None` makes the argument optional. Tests pass a model object; live execution reads the required environment variable. The local `document_adviser` variable holds an Agent object, not its response. `AgentTool(agent=document_adviser)` passes that object to a wrapper. The returned Agent is the coordinator that Runner will execute. None of these constructor calls verifies a document or performs a model request; execution begins in `run_once`.

### Expected reasoning for the prediction exercise

No. A user statement and an explanatory role do not establish an authoritative case update. Add an authorized lookup capability only when that requirement is in scope.

## Trace the implementation

### Translate the customer sentence into responsibilities

Underline “explain documents,” “keep consistent,” and “authorized bank process.” These become an advisory role, a coordinator and a capability restriction. Write the four acceptance checks above before changing a prompt. There is no reason to build a payment API for this request.

### Read the agent factory

`build_agent()` creates fresh agent objects. The optional `model` parameter lets the test supply a scripted model; live runs use `GEMINI_MODEL`. `os.environ["GEMINI_MODEL"]` fails clearly if configuration is missing instead of silently choosing a model.

### Construct the document adviser

`Agent(...)` calls a class constructor with named arguments. `name` is the machine-readable identifier; `description` describes its callable role; `instruction` is the specialist’s own guidance. Adjacent strings inside parentheses are combined by Python. No tool can read or change a case here.

### Expose the adviser as a tool

`AgentTool(agent=document_adviser)` wraps the existing agent object. The outer `tools=[...]` is a Python list of callable capabilities. The coordinator may call it, receive a tool result, and continue. This is different from giving it a `sub_agents` handoff target.

### Trace an invocation rather than guessing

Read `runtime.py`: create a synthetic session, serialize the request into a user message, consume the asynchronous event stream, then close the runner. In the test, follow coordinator function call → adviser result → coordinator response. The scripted fixture proves this wiring; it does not prove Gemini will choose the right tool.

### Evaluate a real explanation

When credentials are configured, ask about the checklist, then ask “Has the ownership register arrived?” The first should explain document purpose; the second must acknowledge the missing live lookup. Record the actual tool trajectory and response, not just whether the process exited successfully.

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

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [ADK workflow choices](https://adk.dev/workflows/)
- [Function tools and agent tools](https://adk.dev/tools-custom/function-tools/)
- [Collaborative workflows](https://adk.dev/workflows/collaboration/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
