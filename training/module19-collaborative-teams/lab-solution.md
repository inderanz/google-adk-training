---
sidebar_position: 3
title: "Explained Lab Solution"
---

# Lab 19 solution: Collaborative Teams: Calls, Returns and Handoffs

A local coordinator has two AgentTools with structured advisory outputs. A separate factory demonstrates a single-turn delegation team.

The employee needs this result: A coordinator response that combines the consulted specialists’ advice and preserves their limitations. If a required consultation is missing, record that as a behaviour failure or choose a workflow that forces the consultation.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.

## Explain why this code exists

One combined explanation suggests a coordinator receiving notes. A sustained conversation with an expert suggests delegation. Mandatory evidence collection belongs in deterministic scheduling even if the final explanation uses advisers.

Read the comments as a requirement-to-code explanation. Then trace one input through the ADK object, returned value and consuming operation. Reproducing the output is the first checkpoint; explaining the changed-input experiment is the mastery checkpoint.

**Design review:** Supply a valid structured note with an unsupported assertion. Design a quality criterion that rejects it despite schema success.

## Why this implementation answers the customer

| Requirement | Implementation | Check |
| --- | --- | --- |
| Coordinator combines advisory results | Two AgentTool capabilities | Each consulted specialist returns to the coordinator. |
| Make limitations explicit | AdvisoryNote output_schema | Every specialist result has summary and limitation fields. |
| Do not imply required collection is guaranteed | Evaluate tool selection; use static workflow for mandatory checks | Missing consultations are visible as an evaluation failure. |
| Distinguish dialogue ownership | Separate single_turn sub-agent example | Learners can explain why this differs from tools=[...]. |

The files below match `example/`. They are complete teaching implementations with explicit fixture boundaries. Follow the [guided lab](./lab.md) for incremental construction and the [enterprise playbook](./enterprise-playbook.md) for the production extension.

| Expression | Meaning |
|---|---|
| `class AdvisoryNote(BaseModel)` | Define a typed return contract |
| `output_schema=AdvisoryNote` | Give ADK the schema class, not an already-created note |
| `tools=[AgentTool(...), AgentTool(...)]` | Supply callable specialist capabilities |
| `sub_agents=[specialist]` | Establish a delegation hierarchy instead |
| `mode="single_turn"` | Choose the local child’s interaction mode |
| `build_delegation_team()` | Build the alternative separately so the comparison is visible |

## `pyproject.toml`

```toml
[project]
name = "banking-module-19"
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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""A coordinator consults two local specialists using call-and-return."""
import os
from typing import Literal
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field


class AdvisoryNote(BaseModel):
    summary: str = Field(max_length=600)
    limitation: str = Field(max_length=300)


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

## `runtime.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Choose a real prompt; credentials are needed only after argument parsing."""
import argparse
import asyncio
import os
from bank_case.agent import build_agent, build_delegation_team
from runtime import display, run_once

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask about fictional bank review preparation")
    parser.add_argument("prompt", nargs="?", default="Explain how to prepare CASE-001 for review.")
    parser.add_argument("--mode", choices=["tools", "single_turn", "task", "chat"], default="tools")
    args = parser.parse_args()
    if not os.environ.get("GEMINI_MODEL"):
        raise SystemExit("Load .env using: uv run --env-file .env python run.py")
    agent = (build_agent() if args.mode == "tools" else build_delegation_team(mode=args.mode))
    display(asyncio.run(run_once(agent, args.prompt)))
```

## Explain the implementation to a reviewer

### `AdvisoryNote`

The class inherits Pydantic's validation behavior. Both annotated fields are required strings because no defaults are supplied. Field(max_length=...) bounds length; it does not require nonempty content, verify citations or make a statement true. Passing the class as output_schema describes the expected specialist result; it is not an example result instance.

### `build_agent`

`selected_model` is shared configuration, while `documents` and `policy` are different Agent objects with different instructions. The name policy is a Python variable for the review adviser, not a policy datastore. Each adviser emits AdvisoryNote-shaped output. Two explicit AgentTool wrappers expose the advisers to the coordinator. The prompt requests both consultations; only an execution trace/evaluation can establish that the model actually selected both.

### `build_delegation_team`

`Literal` documents the permitted mode strings, and Agent validates its own mode field. The CLI separately restricts the allowed option values. A fresh checklist_specialist is placed in sub_agents, establishing the hierarchy. In single_turn mode ADK exposes a named delegation capability; in chat mode a transfer changes the responding agent. The factory returns the coordinator without starting a conversation.

### Expected reasoning for the prediction exercise

No. The interface executed the calls the model selected. The agent failed the behavioral consultation requirement; use evaluation or change the architecture if the consultation must be guaranteed.

## Trace the implementation

### Choose who owns the final response

The customer asked for one coherent explanation. Keep the coordinator as the final conversational owner and make specialist work callable. If the customer instead wanted a sustained conversation with one expert, evaluate a handoff design.

### Define the advisory contract

`AdvisoryNote(BaseModel)` has two bounded strings. `summary` says what the specialist contributes. `limitation` says what it cannot establish. `Field(max_length=...)` bounds generated fields; it does not verify factual correctness.

### Construct specialists before the coordinator

Python variables `documents` and `policy` refer to Agent objects. They share the explicitly chosen model but have different instructions and descriptions. Passing the Pydantic class to `output_schema` tells ADK the required response structure.

### Wrap both roles in AgentTool

The tools list contains two wrappers. The coordinator can request either tool by its exposed name and receive the result. An instruction to consult both is still model behavior: inspect traces and evaluate omissions.

### Read the alternative delegation factory

`build_delegation_team()` creates a fresh specialist in `sub_agents`; its default mode is `single_turn`. The CLI selects this alternative with `--mode single_turn`, `--mode task` or `--mode chat`. With no mode option, it runs the explicit AgentTool example. Reusing one child instance under multiple parents can violate the agent-tree ownership rules; factories avoid that confusion.

### Trace two calls in the offline test

The scripted model returns a document tool call, a structured adviser reply, a review tool call, another reply and a coordinator response. ADK performs the actual nested calls. This proves call-and-return wiring, not natural-language reasoning quality.

### Evaluate the real coordinator

Use a full preparation request, a narrow checklist question and a request for actual approval. Check which capabilities it called, whether it preserved limitations and whether it invented status. If required coverage remains unreliable, change the architecture to a static collection workflow.

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

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --with 'google-adk[eval]==2.11.0' --env-file .env adk eval adk_entry eval/cases.evalset.json --config_file_path eval/eval_config.json --print_detailed_results
```

This optional command resolves evaluation dependencies and uses model/judge calls. Its environment is separate from the base lockfile’s verified offline path. Inspect per-case scores and traces, preserve failing cases, and fix the agent or architecture rather than weakening acceptance criteria. The judge model is explicitly configured in `eval_config.json`; changing `GEMINI_MODEL` alone does not change it.

The pinned ADK AgentTool implementation can emit a deprecation warning from its internal Runner plugins argument. The lesson itself uses the public AgentTool and App APIs; it does not pass that deprecated argument. Preserve this upstream warning in upgrade review rather than copying internal implementation code.

## Answers to the design questions

Why use the native ADK primitive? It already supplies the execution/service contract this lesson needs. Why keep fixture adapters small? They let you inspect orchestration before introducing credentials and external records. Why keep negative outcomes explicit? A bank must distinguish a completed preparation step from missing evidence, failed work or an unverified decision.

## Official sources

- [Collaborative workflows and modes](https://adk.dev/workflows/collaboration/)
- [Agent tools](https://adk.dev/tools-custom/function-tools/)
- [Remote A2A consumption](https://adk.dev/a2a/quickstart-consuming/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

