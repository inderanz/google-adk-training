---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 39: Fixing a "Hallucinating" Agent with Plugins

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.

## Goal

In this lab, you will work with an agent that has been given misleading instructions. It will try to call a tool by the wrong name. Your task is to use the `ReflectAndRetryToolPlugin` to allow the agent to self-correct and succeed *without* changing the misleading instruction.

### Step 1: Create the Project

1.  **Create a new agent project:**

    <Setup/>

    ```shell
    uv run adk create retry_agent
    ```
    This prompts for a model choice (any option is fine, you'll set the real model in `agent.py` below) and, if needed, a backend -- there's no separate "type" prompt, `agent.py`/Code is already the default.

2.  **Navigate to the directory:**
    ```shell
    cd retry_agent
    ```

### Step 2: The "Broken" Agent

**Exercise:** Open `agent.py` and replace its content with the code below.

This code defines a tool named `secret_calculator`. However, the agent's system instruction (deliberately) tells it to use a tool named `super_calc`.

**A note on the instruction wording:** it's forceful enough to guarantee the agent actually *attempts* the nonexistent `super_calc` call on its first try (a milder "you MUST use `super_calc`" gets ignored in practice — modern models tend to just call whatever tool is actually declared, regardless of what the prompt claims its name is), while explicitly scoping that no-deviation rule to "the first attempt only" — so that once the tool-not-found error comes back, the agent is free to adapt instead of stubbornly retrying the same broken name forever. Both halves matter: this is the wording that reliably reproduces both the failure (Step 3) and the plugin-assisted recovery (Step 5).

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.genai import types
from dotenv import load_dotenv
import asyncio

load_dotenv()

# The actual tool
def secret_calculator(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

# The agent with MISLEADING instructions
root_agent = Agent(
    name="confused_agent",
    model="gemini-3.5-flash",
    # We lie to the agent about the tool name!
    instruction="""You are a helper that MUST call a function named exactly `super_calc`
        to add numbers. This is a strict, non-negotiable rule for your FIRST
        attempt only: you are FORBIDDEN from calling any function whose name
        is not literally `super_calc` on your first try, even if a
        differently-named function appears in your available tools. Always
        attempt `super_calc(a, b)` first, no matter what.

        However, if that first attempt fails or returns an error, the
        no-deviation rule above no longer applies: you are then expected to
        read the error message carefully and intelligently adapt, including
        calling a different, correctly-named tool if the error tells you
        one is available.""",
    tools=[FunctionTool(secret_calculator)]
)

async def main():
    # TODO: 1. Import ReflectAndRetryToolPlugin from google.adk.plugins
    
    # TODO: 2. Initialize the plugin here with max_retries=3
    
    # TODO: 3. Create an App instance, passing the root_agent and the plugins list
    app = App(
        name="retry_app",
        root_agent=root_agent,
        # Add your plugin here
    )

    runner = InMemoryRunner(app=app)

    # /run_async requires a session that already exists.
    await runner.session_service.create_session(app_name=app.name, user_id="test", session_id="1")

    print("User: What is 5 + 5?")
    # Running programmatically
    async for event in runner.run_async(
        user_id="test", 
        session_id="1", 
        new_message=types.Content(role="user", parts=[types.Part.from_text(text="What is 5 + 5?")])
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Observe the Failure

1.  **Run the agent:**
    ```shell
    python agent.py
    ```
2.  **Analyze the Output:**
    You should see a `ValueError: Tool 'super_calc' not found.` stack trace that crashes the script. This is because the agent tried to call `super_calc` (as instructed), but only `secret_calculator` is registered — ADK raises this when a model's function call doesn't match any registered tool.

### Step 4: Add the Safety Net

Now, let's fix this using the Plugin *instead* of fixing the prompt.

1.  **Import the Plugin:**
    Add `from google.adk.plugins import ReflectAndRetryToolPlugin` to your imports.

2.  **Initialize the Plugin:**
    Create an instance of `ReflectAndRetryToolPlugin` with `max_retries=3`.

3.  **Register the Plugin:**
    Update the `App` initialization to include your plugin instance in the `plugins` list.

### Step 5: Verify Success (Part 1)

1.  **Run the agent again:**
    ```shell
    python agent.py
    ```
2.  **Analyze the Output:**
    *   Notice the slight pause on the first turn: the model initially attempts `super_calc`.
    *   The ADK runtime catches the missing tool, intercepts it via `ReflectAndRetryToolPlugin`, and appends an observation informing the model: *"Error: Tool 'super_calc' not found. Available tools: 'secret_calculator'"*.
    *   The model reflects on the error, automatically switches to `secret_calculator(a=5, b=5)`, and prints:
        ```text
        User: What is 5 + 5?
        Agent: 5 + 5 is 10.
        ```
    *   **The system recovered autonomously without human intervention or prompt modifications!**

---

### Step 6: Advanced Challenge (Part 2) - Intercepting "Soft Errors" via `extract_error_from_result`

In real-world enterprise environments, external microservices and ERP APIs often **do not raise Python exceptions**. Instead, they return an HTTP 200 payload containing a structured error response, such as:
```python
{"status": "error", "error_code": "INVALID_FORMAT", "message": "Currency code must be 3-letter ISO uppercase (e.g., 'USD', 'EUR')."}
```
By default, `ReflectAndRetryToolPlugin` only triggers when a tool raises an unhandled `Exception`. It ignores successful tool return dictionaries, even if they indicate a failure.

**Your Task:**
Create an `enterprise_agent.py` that extends `ReflectAndRetryToolPlugin` to catch soft dictionary errors and steer the model to self-correct.

```python
# In enterprise_agent.py (Starter Skeleton)
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.genai import types

load_dotenv()

def currency_converter(amount: float, target_currency: str) -> dict:
    """Converts USD amount to target currency."""
    # Simulates an enterprise API returning a soft error on lowercase or invalid codes
    if target_currency != target_currency.upper() or len(target_currency) != 3:
        return {
            "status": "error",
            "message": f"Invalid currency '{target_currency}'. Currency must be a 3-letter uppercase ISO code (e.g. 'EUR', 'GBP', 'JPY')."
        }
    rates = {"EUR": 0.92, "GBP": 0.79, "JPY": 155.0}
    converted = amount * rates.get(target_currency, 1.0)
    return {"status": "success", "amount": converted, "currency": target_currency}

# TODO: Subclass ReflectAndRetryToolPlugin to detect soft errors
class EnterpriseSoftErrorPlugin(ReflectAndRetryToolPlugin):
    async def extract_error_from_result(
        self, *, tool, tool_args, tool_context, result
    ):
        """Inspects dictionary return values and extracts errors for LLM reflection."""
        # TODO: Check if result is a dict with status == "error"
        # TODO: Return the error message string if an error is found, otherwise return None
        pass

agent = Agent(
    name="forex_agent",
    model="gemini-3.5-flash",
    instruction="You are a foreign exchange assistant. Use currency_converter to convert amounts.",
    tools=[FunctionTool(currency_converter)]
)

async def main():
    # TODO: Instantiate EnterpriseSoftErrorPlugin with max_retries=3
    # TODO: Register on App(name="forex_app", root_agent=agent, plugins=[...])
    # TODO: Execute via InMemoryRunner with a query: "Convert $100 to eur"
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Self-Reflection & Engineering Review Questions
1. **Architectural Isolation:** Why is handling tool repair at the `App` plugin layer fundamentally cleaner than embedding retry loops inside individual tool functions?
2. **State & Cost Safety:** What happens if an API call is non-idempotent (e.g., `charge_credit_card`)? Why must `ReflectAndRetryToolPlugin` be restricted or paired with idempotency keys for state mutations?
3. **Tracking Scope:** What is the difference between `TrackingScope.INVOCATION` and `TrackingScope.GLOBAL`? In what scenarios would you choose `GLOBAL` tracking?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMzktcGx1Z2lucy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module39-plugins/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module39-plugins-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

