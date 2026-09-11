---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 3 Solution: Build and Run the "Echo" Agent

## Goal

### Overview

Build your first AI agent with the Google Agent Development Kit (ADK). In this lab, you'll create a "Parrot" agent. Its only purpose is to take any text you provide and repeat it back to you exactly, without answering questions or adding any commentary.

### Expected Behavior
*   **User:** "What time is it?" -> **Agent:** "What time is it?"
*   **User:** "Help me with my homework." -> **Agent:** "Help me with my homework."

### Prerequisites

*   You have successfully completed the setup in Module 2.
*   Your virtual environment is active.
*   You have authenticated with the gcloud CLI.
*   A Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey) or a configured Google Cloud project.

### Core Concepts

*   **Agent:** An AI assistant powered by a Large Language Model (LLM). It's a blueprint defining the agent's purpose (instructions), its model (e.g., Gemini), and its capabilities.
*   **`adk` CLI:** A command-line tool for creating and managing ADK projects.
*   **Dev UI:** An interactive web interface for testing and debugging your agents.

### Step 1: Create the Agent Project

We will use the `adk` command-line tool to create the file structure for our new agent.

1.  **Navigate to your training directory:**
    ```shell
    cd /path/to/your/adk-training
    ```

2.  **Create the agent project:**
    Run the following command to create a new agent named `echo_agent`. This defaults to the Python-based approach.
    ```shell
    uv run adk create echo_agent
    ```
    This command creates a new directory named `echo_agent/` with an `agent.py` file and a `.env` file inside.

### Step 2: Configure the Agent

Now, let's tell the agent how to behave and provide it with the necessary credentials.

1.  **Set up your API key:**
    Open the `.env` file. This file stores secret information like API keys.

    *   **For Google AI Studio API Key:**
        You can get a free API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
        ```
        GOOGLE_API_KEY=<your-google-gemini-api-key>
        ```
    *   **For Google Cloud Agent Platform:**
        ```
        GOOGLE_GENAI_USE_VERTEXAI=1
        GOOGLE_CLOUD_PROJECT=<your_gcp_project>
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

2.  **Define the agent's behavior (Python method):**
    Open `agent.py` and replace its contents with this:

    ```python
    from google.adk import Agent

    # IMPORTANT: The ADK requires this main agent variable
    # to be named exactly `root_agent`.
    root_agent = Agent(
        name="echo_agent",
        model="gemini-3.5-flash",
        description="A parrot agent that only repeats user input.",
        instruction="You are a parrot. Your ONLY job is to repeat the user's input back to them exactly as they wrote it. DO NOT answer questions. DO NOT provide help. DO NOT add extra words. If the user asks a question, repeat the question back to them."
    )
    ```

### Alternative: Defining the Agent in YAML

Instead of Python, you can define your agent in a YAML file. This is simpler for basic agents but less flexible.

1.  **Create the agent with the `--type=config` flag:**
    ```shell
    uv run adk create --type=config echo_agent
    ```
    This creates a `root_agent.yaml` file instead of `agent.py`.

2.  **Define the agent's behavior in `root_agent.yaml`:**
    Open `root_agent.yaml` and replace its contents with this:

    ```yaml
    # The first line is an optional schema definition that provides
    # auto-completion and validation in compatible code editors.
    # yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
    name: echo_agent
    model: gemini-3.5-flash
    description: An agent that repeats the user's input.
    instruction: You are an echo agent. Your only job is to repeat the user's input back to them exactly as they wrote it. Do not add any extra words or explanations.
    ```
    > **Note:** If both `agent.py` and `root_agent.yaml` exist, the ADK will use `agent.py` -- the generated `__init__.py` hard-imports it, regardless of a sibling YAML file. Avoid keeping both in the same directory.

### Step 3: Run the Agent

1.  **Start the ADK web server:**
    From the parent `adk-training` directory, run:
    ```shell
    uv run adk web
    ```
    You should see output indicating a server has started on `http://127.0.0.1:8080`.

2.  **Interact with your agent:**
    *   Open the URL in your web browser.
    *   In the chat interface, type "Hello, world!".
    *   The agent should respond with the exact same message: "Hello, world!".

### Understanding What's Happening

To understand how ADK processes every turn, imagine a **Restaurant** where each component has a clear job:

| ADK Component | Real-World Analogy | What It Does |
|:---|:---|:---|
| **You (User)** | 👤 **The Diner** | You type and send your message (your "order"). |
| **Runner** | 🤵 **The Waiter** | Takes your order, finds your table's running notepad (**Session**), and coordinates everything. |
| **App** | 📋 **The Floor Manager** | Knows the staff directory and introduces the right specialist (**Agent**) to the waiter. |
| **ADK Framework** | 🗂️ **The Order Ticket** | Bundles your message with the agent's recipe rules (**Instructions**) and previous chat memory (**Session History**). |
| **Gemini LLM** | 👨‍🍳 **The Master Chef (The Brain)** | Reads the complete ticket, follows the instructions ("repeat exactly"), and crafts the response. |
| **Runner** | 🍽️ **Serving the Food** | Notes down the response in your table's running history and delivers the reply back to your screen. |

#### Step-by-Step Flow:
1.  **Runner (The Waiter)** receives your message and retrieves (or creates) your **Session** (your personal conversation notepad).
2.  **App (The Manager)** directs the runner to the active **Agent** assigned to this task.
3.  **ADK (The Ticket Clipper)** packages your input together with the agent's instructions and recent conversation history.
4.  **Gemini LLM (The Chef)** generates the intelligent response.
5.  **Runner (The Waiter)** records the reply into the session state for future context and presents it to you.

**Use the Trace tab** in the Dev UI to see this exact flow visually with timings and payloads!

### Key Takeaways

✅ **`uv run adk create`** is the starting point for all agents.
✅ Agent behavior is defined by its **`instruction`**.
✅ **`.env`** keeps your API keys safe and out of code.
✅ You can define agents in **Python** (flexible) or **YAML** (simple).
✅ **`uv run adk web`** is your primary tool for testing and debugging.

### Common Issues & Solutions

*   **Problem**: "Agent not found" or errors on startup.
    *   **Solution**: Make sure you are running `uv run adk web` from the *parent directory* of `echo_agent`.
*   **Problem**: "Authentication error".
    *   **Solution**: Double-check that your `.env` file is correctly configured with your API key or GCP project.
*   **Problem**: If using `agent.py`, "root_agent not found".
    *   **Solution**: Ensure your agent variable is named **exactly** `root_agent`.

### Lab Summary

Fantastic! You have successfully built and interacted with your first AI agent. You have learned the core development loop: Create, Configure, and Run.

In the next modules, you will learn how to give your agents more sophisticated instructions and powerful new capabilities.

### Self-Reflection Answers
- **Advantages of Python over YAML:** Python allows you to add dynamic logic, load complex tools, use advanced environment variable integration, and define custom agents by inheriting from `BaseAgent`. YAML is excellent for rapid prototyping and strictly instruction-based agents without complex orchestration.
- **Importance of `.env` files:** It protects sensitive credentials (API keys) from being accidentally committed to version control systems like GitHub. It also makes it easier to swap credentials across different environments (dev, staging, production) without changing the source code.
- **Using the "Trace" tab:** The Trace tab shows a hierarchical, span-based view of the agent invocation (e.g. `invoke_agent`, `call_llm`, and — when tools are involved — `execute_tool` spans), each with timing/latency information. You can drill into any span to see its inputs and outputs, such as the exact prompt sent to the LLM or a tool's arguments and return value. This is invaluable for debugging more complex agents: it lets you see exactly how long each step took, in what order steps executed, and where in the pipeline a model might be behaving unexpectedly or a tool call might be failing.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module03-first-agent-echo-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

