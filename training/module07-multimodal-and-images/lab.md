---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 7: Building a Visual Product Catalog Analyzer

## Goal

In this lab, you will build a multimodal agent that can analyze a product image and generate a marketing description. This will teach you how to handle image inputs and perform programmatic execution with a vision-capable agent.

### The Architecture

You will use the **App and Runner** pattern you learned in Module 6 to build a Python script that:
1.  Loads local image files as `types.Part` objects.
2.  Constructs a multimodal prompt containing both text and image data.
3.  Executes the agent using `run_async`.

### Step 1: Create and Prepare the Project

> **Note:** unlike other modules, `visual_catalog` must live directly inside this module's own folder (`module07-multimodal-and-images/`) rather than in your shared `adk-training` project -- see point 3 below for why. If this is the first agent you're creating from inside this folder, set up a local environment here first: `uv init --python 3.10 && uv add "google-adk>=2.1.0" python-dotenv`.

1.  **Create the agent project:**
    ```shell
    uv run adk create visual_catalog
    ```
2.  **Navigate into the new directory:**
    ```shell
    cd visual_catalog
    ```
3.  **Sample images:** two sample product photos, `headphones.jpg` and `laptop.jpg`, are already provided in this module's folder (`module07-multimodal-and-images/`), one level up from `visual_catalog/`. That's why you must create `visual_catalog` directly inside this module's folder (as done in step 1 above) — the script below loads them with a relative `../` path. Feel free to swap in your own images later, as long as the filenames match.
4.  **Set up your `.env` file.**
    Vision models require a Vertex AI configuration. Ensure your `.env` file looks like this:
    ```text
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_PROJECT="your-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```

### Step 2: Implement the Multimodal Script

**Exercise:** Create a file named `main.py` in your `visual_catalog` directory. Your task is to complete the core logic inside the `analyze_product` method by filling in the `# TODO` sections.

> **Note on Sessions:** When using `run_async` programmatically, you must explicitly create a session in the runner's session service before sending a message, just as you did with `curl` in Module 5.

Below is the same logic written in a teaching-friendly way. Instead of reading it as isolated lines, think of it as a small delivery pipeline:

1. Build the agent (the model with a job description)
2. Create a runner and session (the traffic system and conversation memory)
3. Turn the image into bytes inside a `types.Part`
4. Send a multimodal message containing both text and image
5. Read the final response from the model and print it

This is the main mental model you will reuse in real ADK projects: one object holds the model, another object manages the runtime, and the message carries the business data.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
# ------------------------------------------------------------
# 1) Import the libraries we need
# ------------------------------------------------------------
import asyncio                      # Lets us run async code (important for ADK run_async)
import logging                      # Helps us control noisy logs from Google libraries
import os                           # Lets us work with file paths and check whether files exist

from google.adk import Agent        # The AI brain / instruction set for the app
from google.adk.apps import App     # The app container that holds the root agent
from google.adk.runners import InMemoryRunner  # Runs the app in memory and manages session state
from google.genai import types      # Used to create Parts, Content, and Blob payloads for multimodal input
from dotenv import load_dotenv       # Loads environment variables from .env

# ------------------------------------------------------------
# 2) Keep the logs clean
# ------------------------------------------------------------
# This is optional, but very helpful when learning.
# Without this, ADK may print a lot of internal HTTP/debug logs that are not relevant to the app logic.
logging.getLogger("google.adk").setLevel(logging.WARNING)

# ------------------------------------------------------------
# 3) Helper function: convert a local image file into ADK format
# ------------------------------------------------------------
# Think of this as a "translator".
# The model does not understand a raw JPG file on disk directly.
# We must read the file bytes and package them into something the model can consume.
# `types.Part` is the message container for model input.
def load_image_from_file(path: str) -> types.Part:
    """Read an image file from disk and convert it into a `types.Part` for Gemini/ADK."""

    # Open the file in binary mode because images are not plain text.
    # 'rb' = read-binary
    with open(path, 'rb') as f:
        image_bytes = f.read()

    # Choose the MIME type based on the file extension.
    # This tells the model what kind of image it is receiving.
    # Think of MIME type as the file's label, like "this is a JPEG image".
    mime_type = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'

    # Build the payload structure expected by the Google GenAI SDK.
    # `types.Blob` holds the raw bytes and the file type.
    # `types.Part` wraps that blob so it can be placed inside a message.
    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

# ------------------------------------------------------------
# 4) Application class: organize the logic into a reusable object
# ------------------------------------------------------------
# This class is like a small business "workflow" object:
# - agent = the intelligence
# - app = the runtime container
# - runner = the execution engine that actually sends the task to the model
class VisualCatalogApp:
    def __init__(self):
        # A. Define the AI "brain"
        # --------------------------------------------------------
        # Here we define the model and the task instructions.
        # This is a classic ADK pattern:
        #   Agent(model=..., name=..., instruction=...)
        # The model is the actual LLM.
        # The instruction is the job description.
        self.agent = Agent(
            model='gemini-3.5-flash',
            name='catalog_writer',
            instruction="You are a professional product catalog writer. Analyze the image and write a compelling description."
        )

        # B. Build the app container
        # --------------------------------------------------------
        # `App` is the wrapper that holds the root agent.
        # In a real application, this is the place where the app is assembled.
        # It is the "container" in which the agent lives.
        self.app = App(name="visual_catalog", root_agent=self.agent)

        # C. Create the runner that executes the app
        # --------------------------------------------------------
        # `InMemoryRunner` is a lightweight runner for in-process execution.
        # It gives us an easy way to send messages and receive events.
        # For a learning example, this is much simpler than setting up a full web server.
        self.runner = InMemoryRunner(app=self.app)

    # ------------------------------------------------------------
    # 5) Main business method: analyze one product image
    # ------------------------------------------------------------
    # This is the key method that does the actual work.
    # It follows the same basic pattern you will use in most ADK apps:
    # 1) create / find a session
    # 2) load the input data
    # 3) produce a multimodal message
    # 4) run the agent
    # 5) read the final response
    async def analyze_product(self, product_id: str, image_path: str):
        # Print a clear heading so we know what is being processed.
        print(f"\n--- Analyzing Product: {product_id} ---")

        # Every conversation in ADK is associated with a user and session.
        # This is like a conversation thread or a ticket folder.
        # We give it a human-friendly user id and a unique session id.
        user_id = "catalog_admin"
        session_id = f"sess_{product_id}"

        # --------------------------------------------------------
        # Step 1: Create the session explicitly
        # --------------------------------------------------------
        # Very important! When using `run_async` programmatically,
        # you must create a session before sending a new message.
        # The session stores conversation state, memory, and context.
        # Without this, the runner has no place to keep the conversation.
        #
        # Analogy:
        # A session is like opening a customer support ticket before you send a message.
        # The ticket keeps all the details together so the support agent can see the full context.
        self.runner.session_service.create_session(
            app_name=self.app.name,
            user_id=user_id,
            session_id=session_id,
        )

        # --------------------------------------------------------
        # Step 2: Load the image
        # --------------------------------------------------------
        # We call our helper function to convert the image file into a `types.Part`.
        # This is how we package the raw image for the model.
        image_part = load_image_from_file(image_path)

        # --------------------------------------------------------
        # Step 3: Build the multimodal message
        # --------------------------------------------------------
        # A message in ADK is a `types.Content` object.
        # It has a role and a list of parts.
        # In this case, the message contains:
        # - a text instruction from the user
        # - an image part with the product photo
        #
        # This is the core multimodal pattern: combine different input types in one message.
        msg = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze this image for product {product_id}."),
                image_part
            ]
        )

        # --------------------------------------------------------
        # Step 4: Send the message to the agent via the runner
        # --------------------------------------------------------
        # `runner.run_async(...)` is the entry point that sends the message into the app.
        # It does the orchestration: session lookup, root agent invocation, model execution,
        # and event streaming back to us.
        #
        # We iterate through the returned event stream and wait for the final answer.
        print("📸 Sending image to Gemini...")
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg
        ):
            # `is_final_response()` tells us when the model has produced the final answer.
            # This is important because the model may emit intermediate streaming events first.
            if event.is_final_response():
                # In many ADK tasks, the response is in event.content.parts[0].text.
                # We print it for the user.
                print(f"✅ Description:\n{event.content.parts[0].text}\n")

# ------------------------------------------------------------
# 6) Entry point: run the workflow for multiple products
# ------------------------------------------------------------
# This function is the coordinator for the whole application.
# It loads environment variables, creates the app object, and loops through a list of product images.
async def main():
    # Load environment variables from .env so settings like GOOGLE_CLOUD_PROJECT and
    # GOOGLE_CLOUD_LOCATION are available to the Google SDK.
    load_dotenv()

    # Create one application object.
    # This object holds the agent and runner so we can reuse the workflow.
    catalog = VisualCatalogApp()

    # A list of product image pairs: (product_id, relative_path)
    # This is a simple data structure that lets us process multiple products in one loop.
    # In real work, this could come from a database, CSV, or API response.
    products = [
        ('HEADPHONES-01', '../headphones.jpg'),
        ('LAPTOP-02', '../laptop.jpg'),
    ]

    # Loop through each product.
    # For each one:
    # - check whether the file exists
    # - if yes, call analyze_product
    # - pause briefly to avoid hammering the model too quickly
    for product_id, path in products:
        if os.path.exists(path):
            await catalog.analyze_product(product_id, path)
            await asyncio.sleep(1)
        else:
            print(f"⚠️ Image not found: {path}")

# ------------------------------------------------------------
# 7) Standard Python execution pattern
# ------------------------------------------------------------
# `if __name__ == '__main__':` means:
# "Only run this block when the script is executed directly as a file."
# This is standard Python best practice and prevents code from running when imported as a module.
if __name__ == '__main__':
    # `asyncio.run(main())` starts the async event loop and runs the main coroutine.
    # This is the bridge between Python's async engine and the code we wrote.
    asyncio.run(main())
```

### Mental model: how the pieces fit together

Think of this like a small product studio workflow:

- `Agent` = the creative team member with a role and instructions
- `App` = the manager that organizes the team
- `InMemoryRunner` = the delivery system that sends tasks into the workflow
- `Session` = the project folder that keeps the conversation context together
- `types.Content` = the work packet containing both the human request and the image file
- `types.Part` = the individual item inside that packet, like one text block or one image block

The pattern is reusable in real code:

- You define the AI behavior once
- You create a runtime container once
- You create a session for each conversation or workflow instance
- You package inputs into structured messages
- You stream final events and act on the result

This is the real-world template for building AI workflows in Python and ADK: define the model, package the input, run the job, and process the output.

> The key idea is not to memorize every class name. The key idea is to understand the pattern: agent + message + session + runner = a working AI workflow.

---

### Quick takeaway for your org

When you build real AI features later, reuse this pattern:

- Keep the AI instructions clear and specific
- Keep the input payload structured and explicit
- Use sessions for continuity and multi-turn interactions
- Process streamed events until the final response appears
- Keep the app logic simple and reusable as a service or workflow method

This is the same reasoning you will use for real-world systems such as document analysis, product recommendation, OCR, call summarization, and customer support copilots.



> **Cleanup:** Unlike other modules, this lab's project was created directly inside `module07-multimodal-and-images/` (the actual course repo folder) rather than in your separate `adk-training` scratch directory. Once you're done, delete `visual_catalog/`, `.venv/`, `pyproject.toml`, and `uv.lock` from inside this module's folder so they don't accidentally get committed to the repo.

### Lab Summary
You have successfully built a multimodal agent! You have learned:
*   How to package image bytes into a `types.Part` object.
*   The importance of explicitly creating a **Session** when using `run_async` programmatically.
*   How to construct a structured `types.Content` object for complex inputs.

This completes **Part 1: Foundations**. You now know how to build, configure, run, and feed multimodal input to an agent. In Part 2, you'll start extending your agent's capabilities with tools.

### Self-Reflection Questions
- Why did we have to call `create_session` manually this time, whereas in Module 6's `run_debug` we didn't?
- How does the `InMemoryRunner` simplify the setup of the `SessionService` compared to a base `Runner`?
- If you wanted to analyze a PDF document instead of an image, which `mime_type` would you use in the `types.Blob`?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDctbXVsdGltb2RhbC1hbmQtaW1hZ2VzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module07-multimodal-and-images/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module07-multimodal-and-images-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

