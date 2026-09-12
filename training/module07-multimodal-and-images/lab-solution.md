---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 7 Solution: Building a Visual Product Catalog Analyzer

## Goal

This file contains the complete code for the `main.py` script in the Visual Product Catalog Analyzer lab, demonstrating how to explicitly manage sessions when using `run_async` for multimodal input.

### `visual_catalog/main.py`

This is the working solution pattern used in the lab. It is intentionally written in a simple, readable style so students can understand not only what each line does, but also why the code is structured this way.

Think of it like a small production pipeline:

1. prepare the agent
2. create a runtime and conversation session
3. package the image and text as a message
4. send it to the model
5. read the final answer and print it

That is the same pattern you will reuse in real AI projects later.

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
```python
# ------------------------------------------------------------
# 1) Import the libraries we need
# ------------------------------------------------------------
import asyncio                      # Required to run async code with `await` and `asyncio.run()`
import logging                      # Helps us control noisy logs from Google / ADK internals
import os                           # Lets us check file paths and whether files exist on disk

from google.adk import Agent        # ADK agent class: the model + instructions + role
from google.adk.apps import App     # App wrapper that holds the root agent
from google.adk.runners import InMemoryRunner  # In-memory execution engine for local testing
from google.genai import types      # Provides `Part`, `Content`, and `Blob` for multimodal input
from dotenv import load_dotenv       # Reads values from a local `.env` file

# ------------------------------------------------------------
# 2) Reduce unnecessary noise from external libraries
# ------------------------------------------------------------
# This is optional, but very valuable when learning.
# ADK may print lots of HTTP/debug logs that are not important for the business logic.
logging.getLogger("google.adk").setLevel(logging.WARNING)

# ------------------------------------------------------------
# 3) Helper function: convert a local image into AI-readable content
# ------------------------------------------------------------
# This is one of the most important ideas in multimodal AI:
# the model does not read a JPG file directly from your computer.
# We must read the bytes and place them into a container ADK knows how to send.
#
# Analogy:
# If a human receives a file, they need to know what it is and what format it is in.
# The same is true for the LLM: we tell it "this is an image" and send the raw bytes.
def load_image_from_file(path: str) -> types.Part:
    """Read an image file from disk and return a `types.Part` for the model."""

    # Open the file in binary mode because images are not text files.
    with open(path, 'rb') as f:
        image_bytes = f.read()

    # Decide the media type based on the file extension.
    # JPG/JPEG => image/jpeg
    # PNG => image/png
    mime_type = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'

    # Wrap the raw bytes in the structure expected by Google GenAI.
    # `Blob` contains the binary data and its mime type.
    # `Part` is the message chunk that can be placed inside a multimodal payload.
    return types.Part(
        inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
    )

# ------------------------------------------------------------
# 4) The application class: organize the workflow cleanly
# ------------------------------------------------------------
# This class keeps the logic reusable.
# A real app usually wraps AI behavior in a class so you can call it again and again.
class VisualCatalogApp:
    def __init__(self):
        # A. Define the intelligence for this app
        # ----------------------------------------------------------------
        # The `Agent` is the model plus instructions.
        # Think of this as the job description given to the LLM.
        self.agent = Agent(
            model='gemini-3.5-flash',
            name='catalog_writer',
            instruction="""
                You are an expert product catalog writer.
                Your task is to analyze the provided image and generate a compelling,
                professional description for a web catalog.
                Highlight the main features, materials, and potential use cases.
            """.strip()
        )

        # B. Build the app container
        # ----------------------------------------------------------------
        # `App` is the wrapper that holds the root agent.
        # In a real system, this is the overall AI application structure.
        self.app = App(name="visual_catalog", root_agent=self.agent)

        # C. Create the runner used to execute the app
        # ----------------------------------------------------------------
        # `InMemoryRunner` is a lightweight local runner for learning and testing.
        # It is useful because it handles the internal session and event flow for us.
        self.runner = InMemoryRunner(app=self.app)

    # ------------------------------------------------------------
    # 5) The actual business method: analyze one product image
    # ------------------------------------------------------------
    # This is the core workflow you will reuse in many AI apps.
    async def analyze_product(self, product_id: str, image_path: str):
        # Print a readable heading so we know which product is being processed.
        print(f"\n--- Analyzing Product: {product_id} ---")

        # A session keeps the conversation state together.
        # In ADK, a session is like a conversation thread or a project folder.
        user_id = "catalog_admin"
        session_id = f"sess_{product_id}"

        # --------------------------------------------------------
        # Step 1: Create the session explicitly
        # --------------------------------------------------------
        # This is required when using `run_async` programmatically.
        # Without a valid session, the runner does not know where to store the conversation context.
        #
        # Analogy:
        # If you open a support ticket before sending a request, the agent can keep context.
        # Without the ticket, the agent has no place to store the conversation history.
        await self.runner.session_service.create_session(
            app_name=self.app.name,
            user_id=user_id,
            session_id=session_id,
        )

        # --------------------------------------------------------
        # Step 2: Convert the image into an ADK input object
        # --------------------------------------------------------
        # Here we call the helper to turn the JPG/PNG file into a `types.Part` payload.
        image_part = load_image_from_file(image_path)

        # --------------------------------------------------------
        # Step 3: Build a multimodal message
        # --------------------------------------------------------
        # A message in ADK is a `types.Content` object.
        # It contains a list of `parts`, and each part can be text, image, or other structured input.
        #
        # This is the real multimodal pattern:
        # - text explains the task
        # - image contains the actual visual data
        msg = types.Content(
            role="user",
            parts=[
                types.Part(text=f"Analyze product ID '{product_id}' and write a catalog description."),
                image_part,
            ],
        )

        # --------------------------------------------------------
        # Step 4: Send the message to the model through the runner
        # --------------------------------------------------------
        # `run_async()` is the ADK entry point for programmatic execution.
        # It returns a stream of events while the model thinks and responds.
        print("📸 Sending image to Gemini...")
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg,
        ):
            # We only care about the final answer.
            # There may be intermediate events before the model is done.
            if event.is_final_response():
                description = event.content.parts[0].text
                print(f"✅ Description Generated:\n{description}\n")

# ------------------------------------------------------------
# 6) Entry point for running the workflow
# ------------------------------------------------------------
# This function is like the orchestrator for the whole app.
# It loads environment config, creates the app object, and loops through products.
async def main():
    # Load environment settings from .env, such as project and location values.
    load_dotenv()

    # Create one app object that can be reused.
    catalog = VisualCatalogApp()

    # List of product IDs and their image paths.
    # In real work, these could come from a database, spreadsheet, or external API.
    products = [
        ('HEADPHONES-01', '../headphones.jpg'),
        ('LAPTOP-02', '../laptop.jpg'),
    ]

    # Loop through each item.
    for product_id, path in products:
        if os.path.exists(path):
            await catalog.analyze_product(product_id, path)
            await asyncio.sleep(1)  # Simple delay to avoid sending too many requests too quickly
        else:
            print(f"⚠️ Warning: Image not found at {path}")

# ------------------------------------------------------------
# 7) Standard Python execution pattern
# ------------------------------------------------------------
# This guard ensures the code only runs when executed directly as a file.
if __name__ == '__main__':
    asyncio.run(main())
```

### Why this logic is written this way

This is not random code. It follows a reusable mental model for modern AI app development:

- `Agent` = the model with instructions and role
- `App` = the application wrapper around the agent
- `InMemoryRunner` = the execution engine that drives the app
- `Session` = the conversation context, stored for the user
- `Content` = the complete message payload
- `Part` = one item inside that message, such as text or image data

If you understand this pattern, you can reuse it for many practical tasks:

- analyze customer documents
- compare product photos
- summarize contracts
- build a visual QA bot
- route user uploads to the right AI workflow

This is the same structure used in many real-world agent systems: structured input, context, runner, and final response handling.

### Key learning point for students

The biggest habit to learn is this:

- do not send raw files directly to the model
- package the data into `types.Part` / `types.Content`
- create or reuse a session for state
- stream events until final response

That is the core pattern behind real AI app engineering.

> The important idea is not memorizing syntax. It is understanding the flow: define the agent, give it context, package the input, execute, and read the final result.

---

### Self-Reflection Answers

1. Why did we have to call `create_session` manually this time, whereas in Module 6's `run_debug` we didn't?
   - `run_debug` is a higher-level helper that handles some setup for us.
   - `run_async` is the lower-level programmatic pattern, so we must create the session explicitly.

2. How does the `InMemoryRunner` simplify the setup compared to a base `Runner`?
   - It gives us a default in-memory session service, making local testing simpler.
   - This reduces boilerplate and makes the learning flow easier.

3. If you wanted to analyze a PDF document instead of an image, which `mime_type` would you use?
   - You would use `application/pdf`.
   - The message structure is the same; only the MIME type changes.

> This version is intentionally kept simple and correct. It follows the repo's working ADK pattern and remains safe to use as a lab solution.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module07-multimodal-and-images-lab-solution -->

> **Cleanup:** Unlike other modules, this project lives directly inside `module07-multimodal-and-images/` (the actual course repo folder) rather than in a separate `adk-training` scratch directory. Once you're done, delete `visual_catalog/`, `.venv/`, `pyproject.toml`, and `uv.lock` from inside this module's folder so they don't accidentally get committed to the repo.

### Self-Reflection Answers

1.  **Why did we have to call `create_session` manually this time, whereas in Module 6's `run_debug` we didn't?**
    *   **Answer:** `run_debug` is a high-level helper method that automatically handles session creation. `run_async` is the production standard; it requires explicit session management, giving developers more control.

2.  **How does the `InMemoryRunner` simplify the setup compared to a base `Runner`?**
    *   **Answer:** The `InMemoryRunner` comes pre-bundled with an `InMemorySessionService` configured, so you don't have to manage the service object manually.

3.  **If you wanted to analyze a PDF document instead of an image, which `mime_type` would you use?**
    *   **Answer:** You would use `application/pdf`. The `Part` and `Blob` structure remains the same for all media types.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module07-multimodal-and-images-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

