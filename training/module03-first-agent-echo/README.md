---
sidebar_position: 3
title: "Module 3: Your First Agent: The \"Echo\" Agent"
---

# Module 3: Your First Agent: The "Echo" Agent

## Theory

### The Core of an ADK Agent

At its heart, an ADK Agent is a blueprint that tells a Large Language Model (LLM) how to behave. This blueprint consists of a few key pieces of information:

*   **`name`:** A unique identifier for your agent.
*   **`model`:** The specific LLM that will act as the agent's "brain" (e.g., `gemini-3.5-flash`).
*   **`instruction`:** The most critical part. This is the detailed prompt that defines the agent's persona, goals, and constraints. Crafting a clear and effective instruction is the key to building a successful agent.
*   **`description`:** A short, human-readable summary of the agent's purpose.

### Two Ways to Define an Agent

The ADK provides two primary methods for creating this blueprint, catering to different needs and complexity levels.

#### 1. Configuration-Based (YAML)

The simplest way to define an agent is with a **YAML** configuration file (e.g., `root_agent.yaml`). This "configuration-over-code" approach is excellent for rapid prototyping and for agents that don't require complex logic.

**Advantages:**
*   **Simple & Fast:** Define an agent in just a few lines.
*   **Clear:** The agent's purpose and instructions are easy to read and understand.
*   **Accessible:** Non-programmers can easily create and modify agents.

A typical YAML configuration looks like this:

```yaml
name: echo_agent
model: gemini-3.5-flash
description: An agent that repeats the user's input.
instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it.
```

#### 2. Programmatic (Python)

For more advanced scenarios, you can define your agent directly in a Python script (e.g., `agent.py`) using the **`Agent`** class. This is the modern standard in ADK 2.0.

**Advantages:**
*   **Flexibility:** Allows for dynamic configuration and logic.
*   **Advanced Features:** Required for implementing features like tools, workflows, and plugins.
*   **Integration:** Easily integrates with other Python code and systems.

The same agent defined in Python would look like this:

```python
from google.adk import Agent

root_agent = Agent(
    name="echo_agent",
    model="gemini-3.5-flash",
    description="An agent that repeats the user's input.",
    instruction="You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it.",
)
```
**Important:** When defining an agent in Python, the ADK requires that the main agent variable be named exactly `root_agent`.

### The ADK 2.0 Runtime: App and Runner

In ADK 2.0, defining an agent is only the first step. Writing an agent blueprint doesn't make it do anything by itself—just like writing a function definition doesn't execute it until you call it.

To bring an agent to life, the ADK architecture cleanly separates **what the agent is** from **how the agent executes** using two core runtime abstractions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                               RUNNER                                   │
│  (The Execution Engine / Runtime Environment)                          │
│  - Session & State Management     - LLM Network Connectivity           │
│  - Event Streaming & Lifecycle    - Step Orchestration                 │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                              APP                               │   │
│   │  (The Deployable Boundary / Application Package)               │   │
│   │  - App Name: "customer_support_app"                            │   │
│   │  - Global Plugins (Tracing, Telemetry, Logging)                │   │
│   │                                                                │   │
│   │   ┌────────────────────────────────────────────────────────┐   │   │
│   │   │                      ROOT AGENT                        │   │   │
│   │   │  (The Brain / Logic Blueprint)                         │   │   │
│   │   │  - Name: "echo_agent"                                  │   │   │
│   │   │  - Model: "gemini-3.5-flash"                           │   │   │
│   │   │  - Instruction: "You are an echo agent..."             │   │   │
│   │   └────────────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

#### 🧠 Cloud & Kubernetes Analogy: Building a Solid Mental Model

If you have experience with Cloud architecture, Docker, or Kubernetes (GKE), this hierarchy maps 1:1 to patterns you already know:

| ADK 2.0 Concept | Cloud / Container Analogy | Kubernetes (GKE) Analogy | Role in Real-World Systems |
| :--- | :--- | :--- | :--- |
| **`Agent`** | **Application Code / Binary** | **Container Image** (`image: echo:v1`) | The core workload logic, model selection, instructions, and tools. |
| **`App`** | **Container / Dockerfile** | **Pod Spec / Deployment** | The deployable packaging unit. Sets boundaries, configuration, and injects sidecars/plugins (like OpenTelemetry tracing). |
| **`Runner`** | **Container Engine (Docker/containerd)** | **Kubelet / Kubernetes Node / Cloud Run** | The active runtime engine. Manages lifecycle, allocates memory/sessions, feeds inputs, and drives turns to completion. |

---

#### 1. What is an `App`? (The Package)
An **`App`** encapsulates your agent into a cohesive, deployable application unit.
*   **Wraps the `root_agent`**: Every app has one entry point—its `root_agent` (which can later branch out into multi-agent teams or workflows).
*   **App Boundaries**: Defines application-wide metadata like the `name`.
*   **Global Services & Plugins**: If you want enterprise OpenTelemetry logging, safety guardrails, or metrics collected across every turn, you attach them at the **App** level, keeping your agent logic clean.

#### 2. What is a `Runner`? (The Engine)
A **`Runner`** is the execution engine that actually runs the `App`. It does not contain prompt instructions; instead, it provides the runtime infrastructure:
*   **Manages Sessions**: Remembers conversation history across multiple turns (via `InMemorySessionService`, `FirestoreSessionService`, etc.).
*   **Dispatches Turns**: Calls Gemini/Vertex AI, manages streaming responses, and triggers tool execution.
*   **Emits Events**: Yields granular event streams (`Event.is_final_response()`, tool call events, etc.).
*   **Provides Debug & Production Modes**:
    *   `InMemoryRunner`: Fast, local in-memory execution for unit tests and local CLI debugging (`run_debug()`).
    *   `ServerRunner` / Vertex Agent Engine: Scalable production runners serving webhooks, REST APIs, or Cloud Run containers.

---

#### 💻 How They Work Together in Code

Here is how `Agent`, `App`, and `Runner` interact programmatically:

```python
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

# 1. THE BRAIN: Define the agent blueprint
root_agent = Agent(
    name="echo_agent",
    model="gemini-3.5-flash",
    instruction="Repeat the user message verbatim.",
)

# 2. THE PACKAGE: Wrap agent into an application with global settings
app = App(name="echo_app", root_agent=root_agent)

# 3. THE RUNTIME: Instantiate an execution engine to drive the app
runner = InMemoryRunner(app=app)

# 4. EXECUTE: Run a turn through the engine
# (Behind the scenes, runner connects to Gemini, tracks history, and yields events)
```

> **CLI Magic:** When you run `uv run adk web .` or `uv run adk run .`, the ADK CLI automatically detects your `root_agent`, wraps it in an `App`, and spins up an `InMemoryRunner` with a web server for you behind the scenes!

### Scaffolding Your Project with `uv run adk create`
...
The ADK command-line tool helps you quickly set up the necessary file structure for a new agent.

Running `uv run adk create <agent_name>` initiates a wizard that lets you choose your preferred method (Config-based or Programmatic). It then creates a directory containing:

*   **`root_agent.yaml`** (for config-based) or **`agent.py`** (for programmatic).
*   **`.env`:** A file for storing environment variables, such as your API keys. This keeps your secrets separate from your agent's code and configuration.

In the upcoming lab, you will use these concepts to create, configure, and run your first agent using both methods.

### Key Takeaways
- An ADK agent is defined by its `name`, `model`, `instruction`, and `description`.
- The `instruction` is the most critical part, defining the agent's persona, goals, and rules.
- Agents can be defined simply with YAML (`root_agent.yaml`) or programmatically with Python (`agent.py`).
- The `uv run adk create` command scaffolds the necessary project structure for a new agent.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module03-first-agent-echo-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

