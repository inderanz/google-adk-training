---
sidebar_position: 2
title: "Challenge Lab"
---

import { ChainSetup } from '../_chain-setup-snippet.mdx';

# Lab 6.5: Programmatic Types & Advanced Content Modeling

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Goal

In this lab, you will step into the shoes of a **Forward-Deployed Engineer (FDE)** building a programmatic intake pipeline for an enterprise customer support system.

Instead of passing unformatted raw strings, you will construct strongly typed **`google.genai.types.Content`** objects containing multiple **`types.Part`** instances. You will send these payloads to an agent via `runner.run_async()`, stream the response in real-time, and extract the generated output using defensive ADK 2.0 accessors.

---

### Step 1: Project Setup

<ChainSetup module={4} project="support_analyzer" />

1.  **Navigate to your existing `support_analyzer` directory:**
    ```shell
    cd /path/to/your/adk-training/support_analyzer
    ```

2.  **Create your ticket processor script:**
    In the same directory alongside `agent.py`, create a new Python file named `ticket_processor.py`.

---

### Python Skeleton (`ticket_processor.py`)

Complete the `ticket_processor.py` script by following the numbered `TODO` comments.

```python
import asyncio
import logging
from dotenv import load_dotenv

# --- Step 1: Import ADK and Google GenAI Types ---
# TODO: Import App from google.adk.apps
# TODO: Import InMemoryRunner from google.adk.runners
# TODO: Import types from google.genai
# TODO: Import root_agent from agent.py
from ... import ...

# Suppress verbose debug logs from network clients
logging.getLogger("google.adk").setLevel(logging.WARNING)

load_dotenv()

# --- Step 2: Infrastructure Initialization ---
# TODO: Create an App instance named "ticket_processing_app" wrapping root_agent
app = ...

# TODO: Create an InMemoryRunner bound to the app
runner = ...


def build_ticket_payload(ticket_id: str, priority: str, user_description: str) -> types.Content:
    """
    Constructs a strongly-typed multi-part Content object for an enterprise ticket.
    """
    # --- Step 3: Construct Individual Parts ---
    # TODO: Create part_header using types.Part.from_text containing metadata:
    #       "[TICKET_METADATA] ID: {ticket_id} | Priority: {priority}"
    part_header = ...

    # TODO: Create part_body using types.Part.from_text containing the user description:
    #       "[USER_DESCRIPTION] " + user_description
    part_body = ...

    # --- Step 4: Assemble Content Object ---
    # TODO: Return a types.Content instance with role="user" and parts=[part_header, part_body]
    return types.Content(
        ...
    )


async def main() -> None:
    user_id = "fde_operator_01"

    # --- Step 5: Explicit Session Creation ---
    # In production streaming pipelines, initialize the session explicitly before turns.
    # TODO: Call runner.session_service.create_session with app.name and user_id
    session = await runner.session_service.create_session(
        ...
    )
    print(f"Initialized active session: {session.id} for operator: {user_id}\n")

    # --- Step 6: Build the Typed Payload ---
    ticket_payload = build_ticket_payload(
        ticket_id="INC-9941",
        priority="HIGH",
        user_description="Our database replica is out of sync and billing jobs are failing.",
    )

    print("Agent Response Stream: ", end="", flush=True)

    # --- Step 7: Stream with run_async ---
    # TODO: Use 'async for' to iterate over runner.run_async()
    #       Pass user_id, session.id, and new_message=ticket_payload
    async for event in runner.run_async(
        ...
    ):
        # --- Step 8: Safe Defensive Inspection ---
        # TODO: Check if event.content and event.content.parts exist
        # TODO: Loop over event.content.parts and print part.text if present
        # Hint: Remember to use flush=True for streaming terminal output
        if event.content and event.content.parts:
            for part in event.content.parts:
                ...

        # TODO: Check if event is the terminal response using event.is_final_response()
        if event.is_final_response():
            print("\n\n[Turn Complete: Final response verified]")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step 3: Run the Script

Execute the script from your terminal using `uv`:

```shell
uv run python ticket_processor.py
```

---

### Step 4: Verify Your Output

If your typed payload and event streaming logic are correctly implemented, you will observe:
1. The session is initialized with a unique session ID.
2. The agent's response streams token-by-token directly to your console.
3. The completion banner `[Turn Complete: Final response verified]` prints once generation ends.

---

### Self-Reflection Questions

1. **Architecture:** Why is passing a `types.Content` object with two separate `types.Part` elements superior to concatenating the metadata and description into a single plain string?
2. **Defensive Programming:** Why must you verify `if event.content and event.content.parts:` before accessing `part.text`?
3. **Enterprise Readiness:** In a production microservice with automated tests, what advantage does static typing (`types.Content`) give you over unstructured dictionaries?

---

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here is a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDZfNS1wcm9ncmFtbWF0aWMtZXhlY3V0aW9uL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module06_5-programmatic-execution/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module06_5-programmatic-types-lab -->
