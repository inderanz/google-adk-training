---
sidebar_position: 2
title: "Module 2: Setting Up Your Development Environment (ADK 2.0)"
---

# Module 2: Setting Up Your Development Environment

## Theory

### The Importance of a Clean Environment

Before diving into building agents, it's crucial to set up a proper development environment. A well-structured environment ensures that your project's dependencies are isolated, preventing conflicts with other Python projects on your system. It makes your project self-contained and easily reproducible by others.

### Python 3.10+ and ADK 2.0 Requirements

The ADK uses modern Python features like advanced type hints and improved asynchronous handling. 

*   **Python Requirement:** Strictly **3.10 or higher**.
*   **ADK Requirement:** This course is built for **google.adk >= 2.1.0**, which introduces the **Workflow Graph Runtime**. Older versions (1.x) are not compatible with the advanced orchestration patterns taught in this course.

### Enter `uv`: The Modern Standard

Enterprise agent development has moved to **`uv`**.

`uv` is an extremely fast Python package and project manager written in Rust. It replaces `pip`, `venv`, and other tools with a single, unified interface that is orders of magnitude faster.

**Key Benefits of `uv`:**

*   **Speed:** It resolves dependencies and installs packages in a fraction of the time.
*   **Deterministic Builds:** It automatically manages a `uv.lock` file ensuring that every developer gets the *exact* same package versions.
*   **Python Version Management:** `uv` can automatically download and use the correct Python version if you specify it during initialization (e.g., `uv init --python 3.10`).

### Development Workflow Options: Choose Your Path

You can complete this training course using any of the following approaches depending on your preference:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CHOOSE YOUR WORKFLOW                            │
├─────────────────────────┬───────────────────────┬──────────────────────┤
│ Path 1: Codespaces      │ Path 2: DevContainer  │ Path 3: Local `uv`   │
│ (1-Click in Browser)    │ (VS Code + Docker)    │ (Terminal / Host OS) │
│ ⭐ Recommended for 100% │ ⭐ Best if you use    │ ⭐ Best for standard │
│ zero local installation │ Docker locally        │ local development    │
└─────────────────────────┴───────────────────────┴──────────────────────┘
```

---

#### 🌟 Path 1: GitHub Codespaces (1-Click Browser Environment)

If you don't want to install Docker, Python, or tools on your computer, you can run the entire course directly in your browser:

1. Open the GitHub repository in your browser: [`https://github.com/inderanz/google-adk-training`](https://github.com/inderanz/google-adk-training).
2. Click the green **`<> Code`** button near the top right.
3. Switch to the **Codespaces** tab.
4. Click **"Create codespace on main"** (or your active branch).
5. A full VS Code interface will launch in your browser. It automatically detects the `.devcontainer` configuration, installs Python 3.11, `uv`, and `gcloud`, and gives you a ready-to-use terminal.

---

#### 🐳 Path 2: VS Code Dev Containers (Local Docker)

A **DevContainer** (Development Container) packages an entire development environment inside a Docker container. It guarantees that Python 3.11, `uv`, `google-cloud-cli`, and all VS Code extensions are configured identically, avoiding "works on my machine" issues.

**How to start it step-by-step:**
1. **Prerequisites:**
   * Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/).
   * Install [VS Code](https://code.visualstudio.com/).
   * Install the official **Dev Containers** extension in VS Code (search for `ms-vscode-remote.remote-containers` in the Extensions tab).
2. **Open the Project:**
   * Clone the repository and open the folder in VS Code:
     ```bash
     git clone https://github.com/inderanz/google-adk-training.git
     cd google-adk-training
     code .
     ```
3. **Reopen in Container:**
   * VS Code will show a popup in the bottom right corner: *"Folder contains a Dev Container configuration file. Reopen in Container?"* → Click **"Reopen in Container"**.
   * *(Alternative)*: Press `F1` (or `Cmd+Shift+P` / `Ctrl+Shift+P`), type **`Dev Containers: Reopen in Container`**, and press `Enter`.
4. **Ready!** VS Code builds the container in the background (1–2 minutes the first time). Once finished, the bottom-left corner of VS Code will show `Dev Container: ADK 2.0 Training Environment`. Any terminal you open (`Ctrl+` `\``) is already inside Linux with Python 3.11, `uv`, and the Google Cloud CLI ready to use.

---

#### 💻 Path 3: Standard Local Setup (`uv` CLI on Host OS)

If you prefer to work directly on your host operating system (macOS, Linux, or Windows):
1. Install `uv` using the official installer:
   * **macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * **Windows (PowerShell):** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Verify installation: `uv --version`
3. Initialize your project with Python 3.10+: `uv init adk-training --python 3.10`



### Authentication: Connecting to Google Services

To use the ADK, your agent needs to communicate with Google's services. There are two primary ways to authenticate.

#### Option A: API Key (Recommended for Beginners)

The quickest way to get started is by using an API key from **Google AI Studio**.

1.  **Get an API Key:** Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Set an Environment Variable:** Provide this key through an environment variable named `GOOGLE_API_KEY`, typically stored in a `.env` file.

#### Option B: Google Cloud Authentication (Enterprise)

For production, use **Application Default Credentials (ADC)** via the **Google Cloud CLI (gcloud)**.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

The ADK automatically detects these credentials.

### UV-Native Setup & Verification Checklist

Before you write or run agent code, always confirm that the environment is healthy.

#### 1. Create a project with the correct Python version

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
mkdir adk-training
cd adk-training
uv init --python 3.10
```

#### 2. Install the core ADK dependencies

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk>=2.1.0" python-dotenv
```

#### 3. Verify the package import works inside the project environment

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python -c "import google.adk; print(google.adk.__version__)"
```

Expected result: a version string prints successfully without import errors.

#### 4. Verify the exact optional feature you need is installed

Some ADK features are packaged as optional extras, not part of the base install. For example, LiteLLM support is not included in the base package.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

If this fails with an error like:

```text
ImportError: LiteLLM support requires: pip install google-adk[extensions]
```

then install the extra in the same `uv` project:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk[extensions]"
```

Then verify again:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

> Use `uv add` when you want the dependency recorded in your `pyproject.toml`.
> Use `uv pip install` only when you are already inside the project virtual environment and want to install a package without changing the project manifest.

#### 5. Common optional extras used in this course

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk[extensions]"    # LiteLLM / local model adapters
uv add "google-adk[gcp]"           # GCP / OpenTelemetry extras
uv add "google-adk[mcp]"           # MCP support
uv add "google-adk[a2a]"           # A2A / distributed agent features
```

If you are unsure which extra is missing, read the import error message carefully. The ADK often tells you exactly which extra to install.

### Troubleshooting Common Errors

#### 1. 🛑 `404: Model 'gemini-3.5-flash' not found`
This error usually occurs when the model has not yet been deployed to your specific Google Cloud location.

**The Fix:**
Change your `GOOGLE_CLOUD_LOCATION` (or `LOCATION` in `.env`) to one of the following high-availability regions:
*   `us-central1`
*   `us-east4`
*   `europe-west9`

#### 2. 🛑 `PermissionDenied: 403`
Your user or service account does not have the "Agent Platform User" role.
**The Fix:** Go to IAM in the Cloud Console and grant your account the `roles/aiplatform.user` role.

#### 3. 🛑 `ModuleNotFoundError: No module named 'google'`
This happens if you are not running the command inside the virtual environment.
**The Fix:** Always prefix your commands with `uv run` (e.g., `uv run adk web .`).

#### 4. 🛑 `ImportError: LiteLLM support requires: pip install google-adk[extensions]`
This is the classic case of a missing optional ADK extra.

**The UV-native fix:**

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
cd /path/to/your/adk/project
uv add "google-adk[extensions]"
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

This is the correct approach because the project dependency is added to `pyproject.toml` and the environment is managed in a reproducible way.

#### 5. 🛑 `ModuleNotFoundError: No module named 'opentelemetry.exporter'`
This occurs when a feature needs the GCP/OpenTelemetry extra but it has not been installed.

**The UV-native fix:**

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk[gcp]"
```

#### 6. 🛑 `ImportError: cannot import name 'McpToolset'` or similar MCP import errors
These usually mean the MCP extra has not been installed in the current project environment.

**The UV-native fix:**

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk[mcp]"
```

### Best Practice: Prefer `uv add` Over Bare `pip`

In this course, we use `uv` as the standard environment manager. When adding dependencies:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv add "google-adk>=2.1.0"
uv add "google-adk[extensions]"
```

Avoid bare `pip install ...` commands unless you are deliberately working outside a project-managed environment. Using `pip` directly can install into the wrong interpreter and create confusing import issues.

### Key Takeaways
- **Python 3.10+** and **google.adk >= 2.1.0** are strictly required.
- **`uv`** is the recommended tool for managing Python projects and environments.
- Use a **`.env`** file to manage your API key or project settings securely.
- Missing ADK features usually mean a missing optional extra, and the fix is almost always `uv add "google-adk[<extra>]"`.
- Always validate imports with `uv run python -c "..."` before debugging application logic.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module02-environment-setup-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

