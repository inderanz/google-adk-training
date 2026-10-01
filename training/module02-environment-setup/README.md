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
1.  **Get an API Key:** Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a new key.
2.  **Set an Environment Variable:** Provide this key through an environment variable named `GOOGLE_API_KEY`. The cleanest way is saving it inside a `.env` file in your project root:
    ```bash
    # Create or update your .env file
    echo 'GOOGLE_API_KEY="AIzaSyYourActualKeyHere"' > .env
    ```
    The ADK and `python-dotenv` automatically load variables from `.env` when your agents run, keeping your credentials secure and out of version control (`.gitignore`).

#### Option B: Google Cloud Authentication (Enterprise)

For production, use **Application Default Credentials (ADC)** via the **Google Cloud CLI (gcloud)**.

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

The ADK automatically detects these credentials. Setting the quota project ensures Vertex AI knows which Google Cloud project to bill and check quotas against, preventing `429 Quota Exceeded` warnings.

### UV-Native Setup & Verification Checklist

Before you write or run agent code, always confirm that the environment is healthy.

#### 1. Create a project with the correct Python version

```bash
mkdir adk-training
cd adk-training
uv init --python 3.10
```

#### 2. Install the core ADK dependencies

```bash
uv add "google-adk>=2.1.0" python-dotenv
```

#### 3. Verify the package import works inside the project environment

```bash
uv run python -c "import google.adk; print(google.adk.__version__)"
```

Expected result: a version string prints successfully without import errors (e.g., `2.9.2`).

---

### 🎓 Deep Dive: Deconstructing Verification Commands & How to Troubleshoot Without Memorizing Syntax

When you are new to Python or modern tooling, strings like `-c` or double underscores (`__version__`) can feel unfamiliar. Here is the mental model of how this works and how you can discover what you need even when you don't know the exact syntax.

#### 1. Deconstructing the Verification Command

Let's break down: `uv run python -c "import google.adk; print(google.adk.__version__)"`

*   **`uv run`**:
    Tells `uv`: *"Execute the following command inside my project's virtual environment (`.venv`), where all my project dependencies are isolated."* Without `uv run`, running `python` might invoke your operating system's default global Python, which will fail to find `google.adk`.
*   **`python -c "..."`**:
    The `-c` flag stands for **command** (inline code execution). Instead of creating a temporary `.py` script on disk, Python executes whatever code string is placed between the quotes directly.
*   **`import google.adk; print(google.adk.__version__)`**:
    *   `import google.adk` loads the installed package into memory.
    *   `;` separates two Python statements on a single line.
    *   `google.adk.__version__` accesses a special package-level attribute. In Python conventions, attributes surrounded by double underscores are called **dunder** attributes (*double underscore*). Most well-behaved Python packages expose their installed version string via `__version__`.

---

#### 2. Four Ways to Troubleshoot & Inspect (From Basic to Advanced)

What if you don't know the syntax, forget the `__version__` name, or run into an error? Use these four techniques:

##### Technique A: Use `uv` Directly (Zero Python Syntax Needed)
You don't actually need to write Python code just to check what is installed in your project:
```bash
# View a graphical dependency tree with exact versions installed
uv tree

# Or filter installed packages directly
uv pip list | grep google-adk
```

##### Technique B: The Interactive Python REPL (The Beginner's Sandbox)
Instead of juggling bash quotes and one-liner semicolons with `-c`, open an interactive Python session inside your project:
```bash
uv run python
```
You will enter Python's interactive prompt (`>>>`). Now you can experiment line by line:
```python
>>> import google.adk
>>> google.adk.__version__
'2.9.2'
>>> exit()
```
*Advantage:* If `import google.adk` fails, the error appears immediately with a clear traceback pointing to the problem.

##### Technique C: Python's Built-in Inspection Tools (`dir()` and `help()`)
What if a package doesn't provide `__version__`, or you don't know what functions/classes exist inside `google.adk`? Inside the interactive REPL (`uv run python`):
What if a package doesn't provide `__version__`, or you don't know what functions/classes exist inside `google.adk` or `google.adk.tools`? Inside the interactive REPL (`uv run python`):

1.  **`dir(google.adk)`** — *"Show me everything inside this object"*:
    ```python
    >>> import google.adk
    >>> dir(google.adk)
    ```
    This prints a full list of all exposed modules, classes (like `Agent`, `Runner`), and attributes.

2.  **`help(google.adk)`** — *"Show me the built-in documentation"*:
    ```python
    >>> help(google.adk)
    ```
    (Press `q` to exit the help viewer).

3.  **Why `dir()` is Safer than `help()` for Submodules (e.g., `google.adk.tools`):**
    If you run `help(google.adk.tools)`, you might encounter an error like:
    ```text
    No module named 'mcp'
    ```
    *Why?* Python's `help()` recursively crawls and imports *all* submodules inside the package to generate docs. ADK includes tools for MCP (Model Context Protocol), but `mcp` is an optional extra (`google-adk[mcp]`). When `help()` tries to inspect an uninstalled optional submodule, it errors out.
    *The Solution:* Use **`dir()`** instead! `dir()` inspects attributes already loaded into memory without trying to recursively import optional dependencies:
    ```python
    >>> import google.adk.tools
    >>> dir(google.adk.tools)
    ```

4.  **Filtering Out Private Names to See Public Tools Clearly:**
    In Python, attributes starting with `_` (like `__builtins__` or `_gemini_schema_util`) are private internal plumbing. Use a list comprehension to filter them out and see only public tools:
    ```python
    >>> import google.adk.tools as tools
    >>> [name for name in dir(tools) if not name.startswith("_")]
    ```
    Or inspect the package's official public export manifest:
    ```python
    >>> tools.__all__
    ```

5.  **Understanding Python Import Scoping (Avoiding `NameError`):**
    If you import a specific tool like this:
    ```python
    >>> from google.adk.tools import google_search
    ```
    Python brings *only* `google_search` into your active namespace. The name `tools` was never imported!
    * If you type `help(tools)`, Python throws: `NameError: name 'tools' is not defined`.
    * To check help on what you actually imported, use: `help(google_search)`.
    * If you want to refer to `tools`, import it explicitly: `from google.adk import tools`, then `help(tools)` or `dir(tools)`.

##### Technique D: Standard Metadata Inspection (`importlib.metadata`)
In modern Python (Python 3.8+), Python includes a standard library module named `importlib.metadata` that can inspect any package's distribution metadata directly by its PyPI distribution name:
```bash
uv run python -c "import importlib.metadata; print(importlib.metadata.version('google-adk'))"
```

---

#### 3. Diagnostic Cheat Sheet for Common Beginner Errors

| Symptom / Error | Diagnosis Command | What It Tells You |
| :--- | :--- | :--- |
| **`ModuleNotFoundError: No module named 'google'`** | `uv pip list` | Package was not installed into `.venv`, or you forgot `uv run`. |
| **"Am I using the right Python interpreter?"** | `uv run which python` | Confirms path points to `.venv/bin/python`, not `/usr/bin/python3`. |
| **"What version of packages do I have?"** | `uv tree` | Shows a full dependency tree and installed versions. |
| **"Does my code syntax actually work?"** | `uv run python` | Interactive REPL (`>>>`) lets you test code line by line. |
| **`NameError: name 'tools' is not defined`** | `from google.adk import tools` | You imported a function (`from ... import google_search`), but did not import `tools`. |
| **`help(...) -> No module named 'mcp'`** | `dir(google.adk.tools)` | `help()` tried to load an optional extra. Use `dir()` instead or install `uv add "google-adk[mcp]"`. |

---

### 🎓 5. Python Software Architecture Hierarchy: How Libraries, Classes, Objects & Attributes Hang Together

When building enterprise agents, understanding how Python software architecture is organized helps you read codebase definitions, debug imports, and communicate effectively with engineering teams.

Python architecture follows a **5-Level Hierarchy** from the highest container level down to the smallest data element:

```text
LEVEL 1: LIBRARY / PACKAGE          (The Whole Mall / District)
  └── LEVEL 2: BASE CLASS           (The General Building Blueprint)
       └── LEVEL 3: SUBCLASS        (The Specialized Store Blueprint)
            └── LEVEL 4: OBJECT / INSTANCE  (The Actual Physical Store on Ground)
                 └── LEVEL 5: ATTRIBUTES, METHODS & PROPERTIES (Inside the Store)
```

#### Real-World Analogy: Indian Railways (IRCTC)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INDIAN RAILWAYS ANALOGY                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Level 1: Library/Package ──> `irctc` (The whole organization / codebase)  │
│  Level 2: Base Class ──────> `Train` (General blueprint for any train)      │
│  Level 3: Subclass ────────> `VandeBharatTrain` (Specialized fast train)    │
│  Level 4: Object/Instance ─> `train_20839` (The real train on Platform 1)   │
│                                                                             │
│  Level 5 (Inside `train_20839`):                                            │
│    • Data Attribute ───────> `train_20839.train_number` (holds 20839)       │
│    • Method ───────────────> `train_20839.start_engine()` (action!)        │
│    • Property ─────────────> `train_20839.is_running_late` (computed status)│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### How They Hang Together in `google.adk` and `google.genai`

```mermaid
flowchart TD
    L1["<b>Level 1: Library / Package</b><br/><code>google.adk</code> & <code>google.genai</code>"]

    L1 --> L2["<b>Level 2: Base Class</b><br/><code>BaseAgent</code> (Parent Class)"]

    L2 -->|Inherits from| L3["<b>Level 3: Subclass</b><br/><code>Agent</code> (Specialized Class in ADK)"]

    L3 -->|Instantiated via ()| L4["<b>Level 4: Object / Instance</b><br/><code>root_agent = Agent(name='calculator_agent')</code>"]

    L4 --> L5A["<b>Data Attribute</b><br/><code>root_agent.name</code><br/><i>(Stored Noun: 'calculator_agent')</i>"]
    L4 --> L5B["<b>Method</b><br/><code>root_agent.run_async(...)</code><br/><i>(Action Verb with ())</i>"]
    L4 --> L5C["<b>Property</b><br/><code>tool_context.user_id</code><br/><i>(Smart Computed Noun)</i>"]
```

#### Detailed Level-by-Level Breakdown with Real Code

##### Level 1: Library / Package / Module (The Container)
* **What it is:** A collection of Python files and folders installed on your computer (`pip install google-adk` / `uv add google-adk`).
* **Real Example:** `google.adk` and `google.genai`.
* **How you use it:** You import tools, modules, and classes from it.
  ```python
  import google.genai  # Importing the google.genai package
  from google.adk import Agent  # Importing the Agent class from google.adk
  from google.adk.tools import ToolContext  # Importing ToolContext class
  ```

##### Level 2: Base Class (The Parent Blueprint)
* **What it is:** A foundational blueprint that defines general rules shared by all agents or models. You rarely use it directly; it exists to be inherited.
* **Real Example:** `BaseAgent` in ADK, or `BaseModel` in Pydantic.
* **How it looks in source code:**
  ```python
  class BaseAgent:
      """The parent template for ALL agents in Google ADK."""

      ...
  ```

##### Level 3: Subclass (The Specialized Blueprint)
* **What it is:** A class that **inherits** (copies) all features from a Base Class and adds specialized superpowers (like LLM function calling or tool management).
* **Real Example:** `Agent` is a **subclass** of `BaseAgent`. `MathResult` is a **subclass** of Pydantic `BaseModel`.
* **How you write it:**
  ```python
  from pydantic import BaseModel


  # MathResult is a SUBCLASS of BaseModel!
  class MathResult(BaseModel):
      status: str
      result: float
  ```

##### Level 4: Instance / Object (The Real Living Thing in Memory)
* **What it is:** When you take a Class (Blueprint) and call it with parentheses `()`, Python allocates memory and builds a **real, living object**.
* **Real Example:** Your `root_agent` or a `types.Content` instance.
* **Code:**
  ```python
  # root_agent is an OBJECT (Instance of the Agent subclass):
  root_agent = Agent(
      name="calculator_agent",
      model="gemini-2.5-flash",
      tools=[add, subtract],
  )
  ```

##### Level 5: Inside the Object (Attributes, Methods & Properties)
Once you have a live Object (`root_agent` or `tool_context`), you interact with its internal members using the dot (`.`) notation:

1. **Data Attribute (Stored Noun):** Stored information inside the object read without `()`.
   ```python
   print(root_agent.name)  # Output: 'calculator_agent'
   print(tool_context.state)  # Output: {'user_name': 'Alice'}
   ```
2. **Method (Action Verb):** Functions inside the object that execute code when you call them with `()`.
   ```python
   # Calls Gemini, runs tools, and streams events:
   async for event in runner.run_async(...):
       ...

   # Saves a PDF file to disk:
   tool_context.save_artifact(pdf_artifact)
   ```
3. **Property (Smart Computed Noun):** A method disguised as data (using `@property`). You read it without `()`, but it runs internal checks behind the scenes.
   ```python
   # Reads verified user ID computed from session security context:
   active_user = tool_context.user_id
   ```

#### Complete Vocabulary Cheat Sheet for Teaching

| Term | What is it? | Real Code Example |
| :--- | :--- | :--- |
| **Library / Package** | Installed folder of Python modules | `google.adk`, `google.genai` |
| **Base Class** | Master parent blueprint | `BaseAgent`, Pydantic `BaseModel` |
| **Subclass** | Specialized child blueprint | `Agent` (child of `BaseAgent`), `MathResult` (child of `BaseModel`) |
| **Object / Instance** | Real created entity in memory | `root_agent = Agent(...)` |
| **Data Attribute** | Stored variable inside object | `root_agent.name` |
| **Method** | Action function executed with `()` | `tool_context.save_artifact(pdf)` |
| **Property** | Computed variable read without `()` | `tool_context.user_id` |

---

#### 4. Verify the exact optional feature you need is installed

Some ADK features are packaged as optional extras, not part of the base install. For example, LiteLLM support is not included in the base package.

```bash
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

If this fails with an error like:

```text
ImportError: LiteLLM support requires: pip install google-adk[extensions]
```

then install the extra in the same `uv` project:

```bash
uv add "google-adk[extensions]"
```

Then verify again:

```bash
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

> Use `uv add` when you want the dependency recorded in your `pyproject.toml`.
> Use `uv pip install` only when you are already inside the project virtual environment and want to install a package without changing the project manifest.

#### 5. Common optional extras used in this course

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

```bash
cd /path/to/your/adk/project
uv add "google-adk[extensions]"
uv run python -c "from google.adk.models.lite_llm import LiteLlm; print('LiteLLM OK')"
```

This is the correct approach because the project dependency is added to `pyproject.toml` and the environment is managed in a reproducible way.

#### 5. 🛑 `ModuleNotFoundError: No module named 'opentelemetry.exporter'`
This occurs when a feature needs the GCP/OpenTelemetry extra but it has not been installed.

**The UV-native fix:**

```bash
uv add "google-adk[gcp]"
```

#### 6. 🛑 `ImportError: cannot import name 'McpToolset'` or similar MCP import errors
These usually mean the MCP extra has not been installed in the current project environment.

**The UV-native fix:**

```bash
uv add "google-adk[mcp]"
```

#### 7. 🛑 `No module named 'mcp'` when running `help(google.adk.tools)`
Python's interactive `help()` function attempts to recursively import and inspect every submodule inside `google.adk.tools`, including optional MCP integrations. If `google-adk[mcp]` is not installed, `help()` throws this error.

**The Fix:**
* Use **`dir(google.adk.tools)`** instead of `help()`. `dir()` safely inspects objects already loaded in memory without triggering recursive imports of optional dependencies.
* Or, if you plan to use MCP tools in your project, install the extra:
  ```bash
  uv add "google-adk[mcp]"
  ```

#### 8. 🛑 `NameError: name 'tools' is not defined`
This happens in Python when you import a specific function or class from a submodule (e.g., `from google.adk.tools import google_search`), and then try to call `help(tools)`. Importing a member does not put the parent module name (`tools`) into your session's namespace.

**The Fix:**
* Call `help()` on the specific item you imported:
  ```python
  help(google_search)
  ```
* Or, if you want to inspect the entire tools module, import it explicitly:
  ```python
  from google.adk import tools
  dir(tools)
  ```

### Best Practice: Prefer `uv add` Over Bare `pip`

In this course, we use `uv` as the standard environment manager. When adding dependencies:

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

