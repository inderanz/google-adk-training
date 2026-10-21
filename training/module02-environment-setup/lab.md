---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 2: Environment Setup Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Prerequisites
Before you begin, ensure you have the following tools ready:
*   **Code Editor (IDE):** You need a good environment to write your code. We recommend:
    *   [VS Code](https://code.visualstudio.com/) (Local)
    *   [Project IDX](https://idx.dev/) (Cloud-based)
    *   [Google Cloud Shell Editor](https://shell.cloud.google.com/) (Cloud-based)
*   **Environment Choice (Pick one - see README for full step-by-step guides):**
    *   **Option A — GitHub Codespaces (1-Click in Browser):** Open repo on GitHub → Click **`<> Code`** → **Codespaces** → **"Create codespace"**. Ready in under 1 minute without installing anything locally!
    *   **Option B — VS Code Dev Containers (Local Docker):** Open the repo in VS Code with Docker Desktop running and click **"Reopen in Container"**.
    *   **Option C — Standard Local Setup (`uv` on Host OS):** Install `uv` via terminal:
        *   macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
        *   Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Goal
Your task is to prepare your environment for enterprise agent development using modern tools. Try to complete the steps below using your existing knowledge. If you get stuck, the `lab-solution.md` file provides a detailed, step-by-step walkthrough.

## Lab Tasks

### Step 0: Ensure Python 3.10+ (Crucial)
Before you start, you must ensure you are using a modern version of Python. The ADK **requires Python 3.10 or higher**. Using older versions (like 3.9) will result in numerous warnings and potential crashes.

Fortunately, `uv` makes this easy. Even if your system doesn't have Python 3.10, you can tell `uv` to install and use it for your project. (If you are using Codespaces or DevContainer, Python 3.11 is already the active default).

### Step 1: Create the Project Structure with `uv`
1.  Use `uv` to initialize a new Python project named `adk-training`. Use the `--python 3.10` flag to guarantee you meet the ADK's requirements:
    ```bash
    uv init adk-training --python 3.10
    ```
    *(Note: Run this in your terminal — whether on your local host or inside the DevContainer/Codespaces terminal)*.
2.  Navigate into the `adk-training` directory.
3.  Use `uv add` to install the modern ADK and dotenv:
    ```bash
    uv add "google-adk>=2.1.0" python-dotenv
    ```
    Notice how `uv` automatically creates a virtual environment (`.venv`) and locks the dependencies in `uv.lock`.

### Step 2: Configure Authentication

Create a file named `.env` in your `adk-training` directory. This file will securely store your authentication credentials. Choose **one** of the two options below.

**Option A: Use a Google AI Studio API Key (Recommended for Beginners)**
1.  Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Add the following line to your `.env` file:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY"
    ```

**Option B: Use Agent Platform (Advanced)**
1.  Authenticate with the gcloud CLI: `gcloud auth application-default login`
2.  Add the following lines to your `.env` file, replacing the placeholder values with your Google Cloud project details:
    ```
    GOOGLE_GENAI_USE_VERTEXAI="1"
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_QUOTA_PROJECT="your-gcp-project-id"
    GOOGLE_CLOUD_LOCATION="global"
    ```

> **💡 Real-World Tip for ADC Quota Warnings:** When authenticating via end-user credentials (`gcloud auth application-default login`), Google Cloud requires `GOOGLE_CLOUD_QUOTA_PROJECT` to know which project's quota to bill against. If omitted, Google Cloud emits an advisory warning.

> **Note on `adk create` and `.env` variables:** Later modules use `uv run adk create <name>` to scaffold a project. That command is an **interactive wizard** — it will prompt you for choices like the model, backend, GCP project, and region, so don't be surprised when it asks questions instead of just running silently. Also, the `.env` file it auto-generates may show `GOOGLE_GENAI_USE_ENTERPRISE=1` instead of the `GOOGLE_GENAI_USE_VERTEXAI=1` used in this lab's examples. Both variables are real and fully supported — they are functionally equivalent ways of telling the ADK to use Vertex AI/Agent Platform. If you see `GOOGLE_GENAI_USE_ENTERPRISE=1` in a generated `.env` file, that's fine; there's no need to "fix" it to match the `GOOGLE_GENAI_USE_VERTEXAI=1` shown elsewhere in the docs.

### Step 3: Verification Script

Create a file named `verify_setup.py` and add the following content:

```python
# verify_setup.py - Environment verification script for Google ADK 2.0

# asyncio provides support for asynchronous programming, allowing non-blocking I/O operations (like calling LLM APIs).
import asyncio
# os provides access to operating system dependent functionality and environment variables.
import os
# warnings enables managing runtime warning messages emitted by Python or third-party libraries.
import warnings
# load_dotenv reads key-value pairs from a local .env file and sets them as environment variables (e.g., API keys).
from dotenv import load_dotenv
# Agent is the core building block representing an intelligent worker configured with instructions, a model, and tools.
from google.adk import Agent
# App encapsulates agents, configurations, and workflows into a deployable application unit.
from google.adk.apps import App
# InMemoryRunner executes agent apps locally in-memory for testing, debugging, and development.
from google.adk.runners import InMemoryRunner

# Pedagogical Note for Learners:
# Automatic Function Calling (AFC) advisory: Under-the-hood, the google-genai SDK emits an advisory warning
# when generate_content is called with default AFC settings in a single-turn verification script.
# In production CLI/verification utilities, we silence non-actionable upstream SDK warnings.
warnings.filterwarnings(
    "ignore",
    message="Direct use of automatic function calling.*",
    category=UserWarning,
)

# Define the asynchronous entry point for our verification logic
async def main():
    # Load environment variables from .env file so the Google SDK can discover GOOGLE_API_KEY or GCP settings
    load_dotenv()


    # Pedagogical Note for Enterprise Authentication (ADC):
    # When using Application Default Credentials (ADC) with gcloud, Google Cloud requires a quota project
    # so Vertex AI knows which billing account/quota to charge. If GOOGLE_CLOUD_PROJECT is set but
    # GOOGLE_CLOUD_QUOTA_PROJECT is not, we automatically align them to avoid 429 quota warnings.
    if os.getenv("GOOGLE_CLOUD_PROJECT") and not os.getenv("GOOGLE_CLOUD_QUOTA_PROJECT"):
        os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = os.environ["GOOGLE_CLOUD_PROJECT"]

    # Print status message indicating start of verification checks
    print("🔍 Testing ADK 2.0 Environment...")

    # Wrap initialization and execution in a try-block to catch and report runtime or configuration errors
    try:
        # Step 1: Define an agent with a name, the target Gemini model, and a system instruction
        agent = Agent(
            # Unique identifier for the agent within the application
            name="verify_agent",
            # The foundation model to use for inference (Gemini 2.5/3.5 Flash)
            model="gemini-3.5-flash",
            # System prompt directing the agent's behavior and required response
            instruction="Respond with: 'ADK 2.0 is Ready!'"
            instruction="Respond with: 'ADK 2.0 is Ready!'",
        )

        # Step 2: Package the agent into an App instance as the root agent
        app = App(name="verify_app", root_agent=agent)

        # Step 3: Instantiate an in-memory runner to orchestrate and execute turns with the app
        runner = InMemoryRunner(app=app)

        # Step 4: Run a single turn using run_debug, sending a test prompt with a session user identifier
        print("🚀 Connecting to LLM...")
        events = await runner.run_debug("Hello!", user_id="test_user")


        # Flag to track whether the expected final response event was received from the agent
        ready = False
        # Iterate over all execution events generated during the run turn
        for event in events:
            # Check if this event contains the agent's completed final response (as opposed to intermediate events)
            if event.is_final_response():
                # Extract and print the generated text content from the first part of the response payload
                print(f"✅ Agent Response: {event.content.parts[0].text}")
                # Set the flag to True indicating successful interaction with the model
                ready = True


        # Check completion flag and output final verification status
        if ready:
            # Confirms all credentials, ADK packages, and LLM connectivity are functioning properly
            print("\n🎉 SETUP COMPLETE! You are running ADK 2.0.")
        else:
            # Reached if events finished without emitting a final response
            print("\n❌ Failed to get a final response from the agent.")

    # Catch missing or incompatible package errors (e.g. outdated google-adk version)
    except ImportError as e:
        print(f"❌ Version Error: {e}")
        print("Ensure you installed google-adk>=2.1.0")
    # Catch any other runtime exceptions (e.g., missing API key, network failure, model 404)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# Standard Python boilerplate to run the main async function when executed directly from the terminal
if __name__ == "__main__":
    # Start the asyncio event loop and run main() to completion
    asyncio.run(main())
```

### Step 4: Run the Verification

Execute the script using `uv run`. This command ensures that your script runs within the virtual environment that `uv` created, without you needing to manually activate it!

```bash
uv run python verify_setup.py
```

### 💡 Troubleshooting: Model Not Found (404)

If you see an error like `Publisher Model ... gemini-3.5-flash was not found`, it usually means the specific model is not yet available in your chosen Google Cloud region (e.g., `us-central1`).

**The Fix:**
1.  Open your `.env` file.
2.  Change `GOOGLE_CLOUD_LOCATION` to a different supported region, such as `us-east4`, `us-west1`, or `europe-west9`.
3.  Run the verification script again.
4.  If switching regions doesn't resolve it, the model may simply not be enabled/allowlisted for your specific GCP project at all. Check the Vertex AI Model Garden in your project, or contact your project admin to confirm access.

> **Note:** You might see a `UserWarning` regarding an `[EXPERIMENTAL]` feature (like `PLUGGABLE_AUTH`). You can safely ignore this; it is just the ADK informing you of its internal development state and does not affect your lab.

## Self-Reflection Questions
*   Why is `uv` considered a major upgrade over traditional tools like `pip` and `venv`?
*   What is the purpose of the `uv.lock` file generated in your project directory?
*   What are the security implications of storing API keys in a `.env` file versus hardcoding them in your script?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDItZW52aXJvbm1lbnQtc2V0dXAvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module02-environment-setup/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module02-environment-setup-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

