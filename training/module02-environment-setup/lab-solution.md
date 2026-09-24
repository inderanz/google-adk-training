---
sidebar_position: 3
id: lab-solution
title: "Lab Solution"
---

# Lab Solution: Environment Setup

This guide walks you through verifying and troubleshooting your environment setup.

## Step 1: Verify Prerequisites

First, ensure you have the right tools installed.

### IDE (Code Editor)
Make sure you have an IDE installed and open.
*   **VS Code:** Recommended for local development.
*   **Project IDX:** Excellent cloud-based alternative.
*   **Cloud Shell Editor:** Built into Google Cloud.

### Check uv
```bash
uv --version
```
**Requirement:** You must see the `uv` version printed. If not, follow the installation instructions in the lab challenge. `uv` handles Python installation automatically, so you no longer need to worry about checking your Python version manually! *(Note: If you are using the DevContainer / GitHub Codespaces environment, `uv` and Python 3.11 are already pre-installed and available).*


## Step 2: Create the Project Structure

Using `uv` makes project initialization incredibly fast and simple.

1.  **Initialize Project with Python 3.10+:**
    ```bash
    uv init adk-training --python 3.10
    ```
    This creates the directory, sets up a `pyproject.toml` file, and prepares the structure. **Crucially, the `--python 3.10` flag tells `uv` to use Python 3.10. If you don't have it installed on your machine, `uv` will download it for you automatically!**

2.  **Navigate into the directory:**
    ```bash
    cd adk-training
    ```

## Step 3: Install Packages

Use `uv` to add your dependencies. We explicitly require version 2.1.0 or higher for the Graph Runtime.

```bash
uv add "google-adk>=2.1.0" python-dotenv
```

## Step 4: Configure Authentication

Create a file named `.env` in the `adk-training` folder.

**Option A: Google AI Studio (API Key)**
```text
GOOGLE_API_KEY="AIzaSy..."
```

**Option B: Agent Platform (Service Account/ADC)**
```text
GOOGLE_GENAI_USE_VERTEXAI="1"
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_QUOTA_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
```
*Note: If using Agent Platform, ensure you have run `gcloud auth application-default login`.*

> **💡 Real-World Tip for ADC Quota Warnings:** When using `gcloud auth application-default login`, Google Cloud issues an advisory warning if `GOOGLE_CLOUD_QUOTA_PROJECT` is not defined:
> *"Your application has authenticated using end user credentials... without a quota project. You might receive a 'quota exceeded' or 'API not enabled' error."*
> Setting `GOOGLE_CLOUD_QUOTA_PROJECT` to your GCP Project ID tells Vertex AI exactly which project to charge for API quotas.

> **Note on `adk create` and `.env` variables:** Later modules use `uv run adk create <name>` to scaffold a project. That command is an **interactive wizard** — it will prompt you for choices like the model, backend, GCP project, and region, so don't be surprised when it asks questions instead of just running silently. Also, the `.env` file it auto-generates may show `GOOGLE_GENAI_USE_ENTERPRISE=1` instead of the `GOOGLE_GENAI_USE_VERTEXAI=1` used above. Both variables are real and fully supported — they are functionally equivalent ways of telling the ADK to use Vertex AI/Agent Platform. If you see `GOOGLE_GENAI_USE_ENTERPRISE=1` in a generated `.env` file, that's fine; there's no need to "fix" it to match the `GOOGLE_GENAI_USE_VERTEXAI=1` shown elsewhere in the docs.

## Step 5: Run Verification

Create `verify_setup.py` (using the modern `Agent` and `App` patterns) and run it using `uv run`. `uv run` ensures the script is executed using the exact Python version (3.10) and dependencies stored in your virtual environment.

```bash
uv run python verify_setup.py
```

**Expected Output:**
`🔍 Testing ADK 2.0 Environment...`
`🚀 Connecting to LLM...`
`✅ Agent Response: ADK 2.0 is Ready!`
`🎉 SETUP COMPLETE! You are running ADK 2.0.`

### 💡 Troubleshooting: Model Not Found (404)

If you see a `404 NOT_FOUND` error for `gemini-3.5-flash`, it is likely a region availability issue.

**The Fix:**
1.  Open your `.env` file.
2.  Update `GOOGLE_CLOUD_LOCATION` to a region where the model is available (e.g., `us-east4`, `us-west1`, or `europe-west9`).
3.  Run the verification script again.
4.  If switching regions doesn't resolve it, the model may simply not be enabled/allowlisted for your specific GCP project at all. Check the Vertex AI Model Garden in your project, or contact your project admin to confirm access.

---

## Self-Reflection Answers

*   **Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?**
    `uv` is written in Rust, making it extremely fast. It unifies project management, virtual environments, and dependency locking into a single tool, eliminating the need to juggle `pip`, `venv`, and `requirements.txt` manually. It even handles downloading the correct Python version for you.
*   **What is the purpose of the `uv.lock` file generated in your project directory?**
    The `uv.lock` file records the exact version of every dependency (and sub-dependency) installed. If you share your project, `uv sync` reads this file to recreate an identical environment, preventing "it works on my machine" bugs.
*   **What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?**
    Hardcoding keys makes them visible to anyone viewing your source code, and they will likely be committed to version control (like GitHub) by accident. A `.env` file is meant to be ignored by git (`.gitignore`), keeping your secrets local and safe.

---

## 🚀 Forward Deployed Engineer (FDE) Playbook: Supercharging Coding Agents with MCP & ADK Ground Truth

When consulting with enterprise customers or configuring AI coding agents (such as Google Antigravity, Claude Code, Cursor, or Codex) to build production-grade ADK applications, standard out-of-the-box LLMs often struggle because their training data predates recent breaking changes (such as ADK 2.0 object models and ADK 2.9 features).

As an FDE or Technical Consultant, you can equip any modern coding agent with **live, verified ground truth** by setting up Model Context Protocol (MCP) servers and runtime inspection.

### 1. The Architectural Blueprint: The 3-Tier Ground Truth Model

To prevent hallucinations and guarantee accurate, enterprise-grade ADK code:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Upstream MCP Documentation (adk-docs / llms.txt)    │  <- Official design patterns & latest features
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Local Runtime Reflection (.venv / help / dir)        │  <- Exact installed type signatures & parameters
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Empirical Simulation (Execution & Verification)      │  <- Zero runtime crashes verified locally
└─────────────────────────────────────────────────────────────┘
```

---

### 2. MCP Server Configuration Guide for Any Coding Agent

Modern coding agents support the **Model Context Protocol (MCP)**. You can provide live documentation feeds to Antigravity, Claude Code, or Cursor using standard configuration files.

#### A. Antigravity Configuration (`~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "adk-docs": {
      "command": "npx",
      "args": ["-y", "@google/adk-docs-mcp"],
      "env": {
        "DOCS_SOURCE_URL": "https://adk.dev/llms.txt"
      }
    },
    "gemini-api-docs": {
      "command": "npx",
      "args": ["-y", "@google/gemini-docs-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
    }
  }
}
```

#### B. Claude Code / Claude Desktop Configuration (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "adk-docs": {
      "command": "npx",
      "args": ["-y", "@google/adk-docs-mcp"],
      "env": {
        "DOCS_SOURCE_URL": "https://adk.dev/llms.txt"
      }
    }
  }
}
```

---

### 3. FDE Inspection Runbook: Troubleshooting Syntax & Verifying Code Without Memorizing APIs

When onboarding a customer team or troubleshooting in a live workshop, use these four progressive diagnostic steps:

#### Step 1: Zero-Syntax Verification with `uv`
Check installed versions and complete dependency trees without writing any Python:
```bash
# Display full graphical dependency tree with exact resolved versions
uv tree

# Query installed ADK package directly
uv pip list | grep google-adk
```

#### Step 2: Single-Line Dynamic Version Check
Confirm the installed version in `.venv` rather than host Python:
```bash
uv run python -c "import google.adk; print(google.adk.__version__)"
```
*(Alternative using standard library metadata)*:
```bash
uv run python -c "import importlib.metadata; print(importlib.metadata.version('google-adk'))"
```

#### Step 3: Interactive Sandbox Inspection (`dir()` and `help()`)
Teach customer developers how to discover exact classes, methods, and parameters live in the terminal:
```bash
uv run python
```
```python
>>> import google.adk
>>> # 1. See every exposed symbol:
>>> dir(google.adk)
>>> # 2. View full interactive documentation and signatures:
>>> help(google.adk)
>>> # 3. Inspect a specific component (e.g., Agent or Runner):
>>> from google.adk import Agent
>>> help(Agent)
>>> exit()
```

#### Step 4: Golden Rules for ADK 2.0 (To inject into Agent Instructions / `GEMINI.md` / `CLAUDE.md`)
Always provide these rules to any agent pair-programming on ADK code:
* **`LlmResponse`**: Never use `.candidates`. Use `.content` directly.
* **`LlmRequest`**: Access prompt history via `.contents`.
* **Events**: Use modern event methods (e.g. `event.is_final_response()`).
* **Environment Execution**: Always run commands via `uv run` to ensure isolation inside `.venv`.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module02-environment-setup-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

