---
sidebar_position: 2
title: "Challenge Lab: Building an Enterprise Stateful Banking Agent"
---

import Setup from '../_setup-snippet.mdx';

# Lab 10: Building an Enterprise Stateful Banking Agent

**Learning Checkpoint:** Review the [Module 10 Concepts](./README.md) before starting. In this lab, you build an enterprise-grade stateful agent that uses **`ToolContext`** to persist customer preferences across conversation turns, enforce zero-trust identity verification, and accumulate multi-turn loan application drafts.

---

## 🎯 Lab Objectives

By completing this challenge lab, you will:
1. **Implement `ToolContext` Dependency Injection:** Author stateful custom functions where ADK injects runtime context automatically.
2. **Enforce Zero-Trust Security:** Read customer identity exclusively from `tool_context.user_id` without accepting user IDs as model-supplied arguments.
3. **Build Multi-Turn Draft Accumulators:** Accumulate progressive form data across multiple conversation turns using `tool_context.state`.
4. **Implement Deterministic Business Logic:** Calculate monthly loan EMI deterministically using standard financial formulas upon submission.
5. **Programmatically Verify Multi-Turn State:** Write an automated test harness using `InMemoryRunner` to verify that state persists across 3 consecutive turns.

---

## Step 1: Environment & Project Setup

<Setup/>

### 1. Initialize the Workspace
Create a clean directory for your stateful banking agent project:

```bash
mkdir -p banking_agent/tools
cd banking_agent
```

### 2. Configure Environment Variables
Create a `.env` file in `banking_agent/`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Initialize Package Files
Create the package files:

```bash
touch tools/__init__.py
touch tools/banking.py
touch agent.py
touch run_verification.py
```

---

## Step 2: Implement Stateful Tools (`tools/banking.py`)

Open `tools/banking.py`. Your challenge is to implement the 4 stateful tools using `ToolContext`.

> [!CRITICAL]
> **The Docstring Rule:**
> Do NOT document `tool_context` in your function docstrings or parameter lists! ADK automatically strips `tool_context` from the Gemini schema. Mentioning it in docstrings will confuse the model and cause parameter hallucinations.

```python
"""
tools/banking.py
Enterprise stateful tools for preference caching and multi-turn loan draft accumulation.
"""
from typing import Dict, Any, List
from google.adk.tools import ToolContext


def set_customer_preference(
    preferred_language: str,
    preferred_branch: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Updates the customer's communication language and primary branch preference.

    Args:
        preferred_language: Requested language (e.g., 'Hindi', 'English', 'Tamil').
        preferred_branch: City or branch code (e.g., 'Connaught Place Delhi', 'MG Road Bengaluru').

    Returns:
        A dictionary confirming the preferences saved.
    """
    # TODO: 1. Write 'preferred_language' into tool_context.state["preferred_language"]
    # TODO: 2. Write 'preferred_branch' into tool_context.state["preferred_branch"]
    # TODO: 3. Return {"status": "success", "message": "Preferences saved successfully."}
    pass


def get_customer_profile(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves the active customer's profile, preference settings, and verified identity.

    Returns:
        A dictionary containing user_id, preferred_language, and preferred_branch.
    """
    # TODO: 1. Extract verified identity from tool_context.user_id (Zero-Trust Security!)
    # TODO: 2. Read 'preferred_language' from tool_context.state with default 'English'
    # TODO: 3. Read 'preferred_branch' from tool_context.state with default 'Main Branch'
    # TODO: 4. Return structured dictionary with user_id, preferred_language, and preferred_branch
    pass


def update_loan_draft(
    field_name: str,
    field_value: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Updates a specific field in the customer's active loan application draft.

    Args:
        field_name: The draft property ('legal_name', 'annual_income', 'loan_amount', 'tenure_months').
        field_value: The value provided by the customer for this specific field.

    Returns:
        A dictionary indicating progress status, captured fields, and any missing required fields.
    """
    # Required loan fields
    required_fields = ["legal_name", "annual_income", "loan_amount", "tenure_months"]

    # TODO: 1. Retrieve the existing 'loan_draft' dict from tool_context.state (or {} if not yet initialized)
    # TODO: 2. Store field_value in draft[field_name]
    # TODO: 3. Save the updated dictionary back into tool_context.state["loan_draft"]
    # TODO: 4. Identify which required fields are still missing
    # TODO: 5. Return a dictionary with:
    #       - 'status': 'ready_for_submission' if len(missing) == 0 else 'in_progress'
    #       - 'captured_fields': list(draft.keys())
    #       - 'missing_fields': missing
    pass


def submit_loan_application(tool_context: ToolContext) -> Dict[str, Any]:
    """Submits the accumulated loan application draft for processing and calculates monthly EMI.

    Returns:
        A dictionary containing submission status, application_id, loan details, and calculated EMI.
    """
    # TODO: 1. Retrieve 'loan_draft' from tool_context.state
    # TODO: 2. Verify all 4 required fields exist ('legal_name', 'annual_income', 'loan_amount', 'tenure_months')
    #          If any required field is missing, return {"status": "error", "missing_fields": missing}
    # TODO: 3. Calculate monthly EMI deterministically:
    #          P = float(loan_amount)
    #          N = int(tenure_months)
    #          R = 10.5 / 12 / 100  (10.5% annual interest)
    #          EMI = round((P * R * (1 + R)**N) / ((1 + R)**N - 1), 2)
    # TODO: 4. Generate a synthetic application ID (e.g. 'APP-LON-9021')
    # TODO: 5. Clear or mark tool_context.state["loan_draft_submitted"] = True
    # TODO: 6. Return structured dictionary with:
    #          'status': 'submitted',
    #          'application_id': application_id,
    #          'applicant_name': draft['legal_name'],
    #          'loan_amount': P,
    #          'tenure_months': N,
    #          'monthly_emi': EMI
    pass
```

---

## Step 3: Configure the Agent Node (`agent.py`)

Open `agent.py`. Register your stateful tools using ADK 2.0's `Agent` class:

```python
"""
agent.py
Root agent definition binding stateful tools to Gemini 2.5 Flash.
"""
from google.adk import Agent
from tools.banking import (
    set_customer_preference,
    get_customer_profile,
    update_loan_draft,
    submit_loan_application,
)

# TODO: Define the root_agent:
# 1. name: "banking_agent"
# 2. model: "gemini-2.5-flash"
# 3. instruction:
#    - Direct the agent to use 'set_customer_preference' when preferences are mentioned.
#    - Direct the agent to use 'get_customer_profile' when asked about account settings.
#    - Direct the agent to use 'update_loan_draft' turn-by-turn as loan details arrive.
#    - Direct the agent to use 'submit_loan_application' ONLY when the user asks to submit or finalize.
# 4. tools: register all 4 functions in the tools list.

root_agent = Agent(
    name="banking_agent",
    model="gemini-2.5-flash",
    description="An enterprise stateful banking assistant.",
    instruction="""
# TODO: Complete steering prompt following the instructions above
""",
    tools=[
        # TODO: Add your 4 tool functions
    ],
)
```

---

## Step 4: Programmatic Multi-Turn Verification (`run_verification.py`)

In enterprise AI engineering, you must verify that state **persists across multiple consecutive turns** within the same session.

Open `run_verification.py` and implement the 3-turn test harness:

```python
"""
run_verification.py
Automated programmatic verification testing state persistence across 3 turns.
"""
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from google.genai import types
from agent import root_agent

load_dotenv()


async def send_turn(runner: InMemoryRunner, session_id: str, prompt: str):
    print(f"\n==================================================")
    print(f"USER: {prompt}")
    print(f"==================================================")

    async for event in runner.run_async(
        user_id="customer_rajesh_99",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.is_final_response():
            print(f"AGENT:\n{event.content.parts[0].text}\n")


async def main():
    print("Initializing ADK InMemoryRunner...")
    app = App(name="banking_app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    # 1. Create a dedicated session for customer 'customer_rajesh_99'
    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id="customer_rajesh_99",
        session_id="session_banking_01"
    )

    # Turn 1: Hydrate preferences and start loan draft
    await send_turn(
        runner,
        session.id,
        "Hello! Please set my preferred branch to MG Road Bengaluru and preferred language to Hindi. Also, my name is Rajesh Kumar and my annual income is 1200000."
    )

    # Turn 2: Provide remaining loan parameters (testing state accumulation)
    await send_turn(
        runner,
        session.id,
        "I need a personal loan of Rs. 500,000 for a tenure of 36 months."
    )

    # Turn 3: Submit application and verify profile (testing state retrieval)
    await send_turn(
        runner,
        session.id,
        "Please submit my loan application and confirm my customer profile settings."
    )


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 5: Execute & Validate

Run the programmatic verification script:

```bash
uv run python run_verification.py
```

### Expected Validation Criteria
1. **Turn 1:** The agent acknowledges that preferences (MG Road Bengaluru, Hindi) are saved and notes that initial applicant details (Rajesh Kumar, 1,200,000 income) were captured.
2. **Turn 2:** The agent recognizes that `loan_amount` (500,000) and `tenure_months` (36) were added to the existing draft, confirming all required fields are now present.
3. **Turn 3:** The agent executes `submit_loan_application`, calculates the approximate monthly EMI (approximately Rs. 16,252/month at 10.5% interest), and quotes the customer's stored preferences without asking for them again!

---

## Self-Reflection Questions

1. **Schema Stripping:** Why does ADK strip `tool_context: ToolContext` from the OpenAPI schema sent to Gemini? What happens if you mention `tool_context` in your docstring?
2. **Zero-Trust Identity:** Why is reading `tool_context.user_id` fundamentally safer than accepting `def fetch_balance(user_id: str)` as an LLM argument?
3. **State Scope:** What happens to `tool_context.state` when the user opens a new chat session? How does this differ from external database persistence (e.g. Firestore in Module 13.5)?

---

### 🕵️ Hidden Solution Hint 🕵️

Stuck or need to verify your implementation? Base64-decode the hint below:

`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTAtYWR2YW5jZWQtZnVuY3Rpb24tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module10-advanced-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

---

## Official References

- **Google ADK Custom Tools:** https://adk.dev/tools-custom/
- **Google ADK Session State:** https://adk.dev/sessions/
- **Google Gemini API Function Calling:** https://ai.google.dev/gemini-api/docs/function-calling
