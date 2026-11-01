---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 39 Solution: Fixing a "Hallucinating" Agent with Plugins

## Goal

This solution demonstrates how to use the `ReflectAndRetryToolPlugin` to automatically recover from tool usage errors (like incorrect tool names) without modifying the agent's prompt code.

## Steering Prompt Template

Use this prompt to guide an AI coding assistant (such as Google Antigravity or Gemini Code Assist) or validate your self-healing implementation against Google Principal FDE standards:

```markdown
Act as a Google Principal Forward-Deployed Engineer (FDE). I need to harden an ADK 2.0 application against tool hallucinations, invalid arguments, and runtime exceptions using the built-in `ReflectAndRetryToolPlugin`.

Requirements:
1. Agent Definition:
   - Configure a `FunctionTool` wrapping a function `secret_calculator(a: int, b: int) -> int`.
   - The agent's prompt is purposefully confused (instructed to call `super_calc`), simulating prompt drift or hallucination.
2. Self-Healing App Architecture:
   - Import `ReflectAndRetryToolPlugin` from `google.adk.plugins`.
   - Instantiate `retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)`.
   - Register the plugin globally on the `App` instance (`App(name="retry_app", root_agent=root_agent, plugins=[retry_plugin])`).
3. Verification & Execution:
   - Run programmatically via `InMemoryRunner(app=app)`.
   - Verify that upon invoking `What is 5 + 5?`, the plugin intercepts the initial `super_calc` failure, passes tool feedback back to the LLM, and successfully returns `10` from `secret_calculator` without crashing.
```

### `retry_agent/agent.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin  # 1. Import
from google.genai import types
from dotenv import load_dotenv
import asyncio

load_dotenv()


# The actual tool
def secret_calculator(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


# The agent with MISLEADING instructions
#
# NOTE on the wording: this needs to be forceful enough that the agent
# actually *attempts* the nonexistent `super_calc` call on its first try —
# a milder "you MUST use `super_calc`" gets ignored in practice, since
# modern models tend to just call whatever tool is actually declared,
# regardless of what the prompt claims its name is. But the no-deviation
# rule is explicitly scoped to "the first attempt only", so that once the
# tool-not-found error comes back, the agent is free to adapt instead of
# stubbornly retrying the same broken name forever (an unscoped "never
# deviate, under any circumstances" causes the agent to keep hammering
# `super_calc` even after ReflectAndRetryToolPlugin reports that
# `secret_calculator` is available).
root_agent = Agent(
    name="confused_agent",
    model="gemini-3.5-flash",
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
    tools=[FunctionTool(secret_calculator)],
)


async def main():
    # 2. Configure the Plugin
    # We give the agent 3 chances to realize its mistake and try the correct tool name.
    retry_plugin = ReflectAndRetryToolPlugin(max_retries=3)

    # 3. Register the Plugin on the App
    app = App(name="retry_app", root_agent=root_agent, plugins=[retry_plugin])

    runner = InMemoryRunner(app=app)

    # /run_async requires a session that already exists.
    await runner.session_service.create_session(
        app_name=app.name, user_id="test", session_id="1"
    )

    print("User: What is 5 + 5?")
    # Running programmatically
    async for event in runner.run_async(
        user_id="test",
        session_id="1",
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text="What is 5 + 5?")]
        ),
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Part 2 Solution: `enterprise_agent.py` (Catching Soft API Errors)

This solution implements a production-grade custom plugin that subclasses `ReflectAndRetryToolPlugin` to intercept dictionary-based "soft errors" returned by enterprise REST APIs and microservices.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Production Solution: Custom ReflectAndRetry plugin for enterprise soft-error recovery."""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.plugins.reflect_retry_tool_plugin import TrackingScope
from google.genai import types

load_dotenv()


def currency_converter(amount: float, target_currency: str) -> dict:
    """Converts USD amount to target currency.

    Demonstrates a realistic enterprise API behavior: returning HTTP 200 with
    a structured error payload when input formatting is invalid.
    """
    # Strict validation rule: currency must be 3 uppercase letters (e.g., 'EUR')
    if target_currency != target_currency.upper() or len(target_currency) != 3:
        return {
            "status": "error",
            "error_code": "INVALID_CURRENCY_FORMAT",
            "message": (
                f"Currency code '{target_currency}' is invalid. "
                "Must be a 3-letter uppercase ISO code (e.g., 'EUR', 'GBP', 'JPY')."
            ),
        }

    conversion_rates = {
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 155.0,
        "CAD": 1.38,
        "AUD": 1.52,
    }
    rate = conversion_rates.get(target_currency, 1.0)
    converted_amount = round(amount * rate, 2)
    return {
        "status": "success",
        "amount": converted_amount,
        "currency": target_currency,
        "exchange_rate": rate,
    }


class EnterpriseSoftErrorPlugin(ReflectAndRetryToolPlugin):
    """Subclass of ReflectAndRetryToolPlugin that detects non-exception soft errors.

    By default, ADK only retries when an actual Exception is raised. Overriding
    extract_error_from_result allows intercepting dictionary error contracts.
    """

    async def extract_error_from_result(self, *, tool, tool_args, tool_context, result):
        # Inspect return payload for enterprise error patterns
        if isinstance(result, dict) and result.get("status") == "error":
            error_message = result.get("message", "Unknown downstream API error")
            print(f"[Plugin Intercept] Detected soft API error: {error_message}")
            return error_message

        # Returning None indicates the tool succeeded; no reflection triggered
        return None


# Agent definition
forex_agent = Agent(
    name="forex_assistant",
    model="gemini-3.5-flash",
    instruction=(
        "You are a professional foreign exchange assistant. "
        "Use the `currency_converter` tool to fulfill customer currency exchange requests. "
        "If a tool call returns an error, read the feedback and correct your arguments."
    ),
    tools=[FunctionTool(currency_converter)],
)


async def main():
    # 1. Instantiate the custom plugin with bounded retries and invocation scope
    soft_error_plugin = EnterpriseSoftErrorPlugin(
        max_retries=3,
        throw_exception_if_retry_exceeded=True,
        tracking_scope=TrackingScope.INVOCATION,
    )

    # 2. Register globally on the App
    app = App(
        name="forex_enterprise_app", root_agent=forex_agent, plugins=[soft_error_plugin]
    )

    # 3. Execute via Runner
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name=app.name, user_id="trader_42", session_id="session_001"
    )

    # Intentionally provide lowercase 'eur' in the user prompt to trigger formatting repair
    user_prompt = "Can you convert 250 USD into eur?"
    print(f"User: {user_prompt}\n")

    async for event in runner.run_async(
        user_id="trader_42",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=user_prompt)]
        ),
    ):
        if event.is_final_response():
            print(f"\nFinal Agent Response: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step-by-Step Execution Trajectory

When `enterprise_agent.py` runs, the execution traces through this self-healing trajectory:

1. **Turn 1 (Initial Call):**
   * Gemini interprets *"convert 250 USD into eur"* and calls `currency_converter(amount=250.0, target_currency="eur")`.
   * The Python function executes without crashing, returning `{"status": "error", "message": "Currency code 'eur' is invalid. Must be a 3-letter uppercase ISO code..."}`.
2. **Turn 2 (Plugin Interception & Reflection):**
   * `EnterpriseSoftErrorPlugin.extract_error_from_result` intercepts the dictionary, extracts the error string, and injects a reflection prompt into the conversation state:
     `[Plugin Intercept] Detected soft API error: Currency code 'eur' is invalid. Must be a 3-letter uppercase ISO code...`
3. **Turn 3 (Autonomous Self-Correction):**
   * Gemini reviews the error, recognizes that `"eur"` must be uppercase `"EUR"`, and calls `currency_converter(amount=250.0, target_currency="EUR")`.
   * The function returns `{"status": "success", "amount": 230.0, "currency": "EUR", "exchange_rate": 0.92}`.
4. **Turn 4 (Final Synthesis):**
   * The agent synthesizes the successful output: *"250 USD is equivalent to 230.00 EUR at an exchange rate of 0.92."*

---

### Self-Reflection & Engineering Review Answers

1. **Why is it better to handle this with a Plugin rather than just fixing the prompt?**
   * **Answer:** System prompts cannot foresee every dynamic runtime failure (e.g., transient network drops, third-party API schema migrations, or nondeterministic LLM argument typos). The Plugin provides an infrastructure-level safety net across all tools globally, decoupling business tools from defensive retry spaghetti code.
2. **What would happen if we set `max_retries=0`?**
   * **Answer:** Retries are disabled. The initial tool exception or soft error immediately halts execution or propagates unhandled to the user without giving Gemini a reflection turn.
3. **What is the difference between `TrackingScope.INVOCATION` and `TrackingScope.GLOBAL`?**
   * **Answer:**
     * `TrackingScope.INVOCATION` (default): Resets the failure counter on each conversation turn. Ideal for transient model mistakes (e.g., trying a wrong tool name once per question).
     * `TrackingScope.GLOBAL`: Persists the failure count across all turns of a user session. Ideal when calling external APIs with strict quota caps (e.g., if an enterprise billing API fails 3 times across the entire user session, permanently disable that tool to prevent exhausting corporate quotas).
4. **Why must writes and state mutations be protected with idempotency keys?**
   * **Answer:** Retrying a read operation (`get_account_balance`) is safe because reads are idempotent. Retrying a state mutation (`transfer_funds` or `submit_order`) after a network timeout can result in duplicate debits if the server actually processed the first request. Stateful mutations must never rely solely on blind retries; they require an `idempotency_key: UUIDv4` enforced by the backend database.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module39-plugins-lab-solution -->
---

## Official References

- Google ADK Plugins Guide: https://adk.dev/plugins/
- Google ADK Reflect and Retry Plugin: https://adk.dev/integrations/reflect-and-retry/
- Google ADK BigQuery Analytics: https://adk.dev/integrations/bigquery-agent-analytics/
- Google ADK Model Armor Guardrails: https://adk.dev/integrations/model-armor/
- Google GenAI Python SDK: https://googleapis.github.io/python-genai/


