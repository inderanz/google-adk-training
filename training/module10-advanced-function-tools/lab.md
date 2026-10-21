---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 10: Building an Enterprise "Stateful Banking" Agent Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Goal

In this lab, you will build an enterprise-grade banking agent (`banking_agent`) that uses **`ToolContext`** to persist customer preferences, enforce zero-trust identity verification, and accumulate multi-turn loan application drafts across conversation turns.

---

### Step 1: Create the Project Structure

<Setup/>

1. **Create the agent project:**
   ```bash
   uv run adk create banking_agent
   cd banking_agent
   ```

2. **Set up authentication:**
   Create a `.env` file in your `banking_agent` directory and add your `GOOGLE_API_KEY`:
   ```bash
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Create the tools package:**
   Organize your tool code cleanly inside a `tools/` module:
   ```bash
   mkdir tools
   touch tools/__init__.py
   touch tools/banking.py
   ```

---

### Step 2: Implement Stateful Tools (`tools/banking.py`)

Open `tools/banking.py` and implement the stateful tools using `ToolContext`. Pay close attention to docstrings and parameter signatures.

> [!CRITICAL]
> **Docstring Rule:** Do NOT list `tool_context` in your function docstrings! ADK strips `tool_context` from the Gemini schema automatically, so mentioning it in docstrings will confuse the model.

#### Part A: Customer Profile & Preference Hydration
Implement tools that store customer preferences and fetch profile data using `tool_context.state` and `tool_context.user_id`:

```python
# In tools/banking.py
from google.adk.tools import ToolContext


def set_customer_preference(
    preferred_language: str, preferred_branch: str, tool_context: ToolContext
) -> dict:
    """Updates the customer's communication language and primary branch preference.

    Args:
        preferred_language: Requested language (e.g., 'Hindi', 'English',
          'Tamil').
        preferred_branch: City or branch code (e.g., 'Connaught Place Delhi',
          'MG Road Bengaluru').
    """
    # TODO: Write 'preferred_language' and 'preferred_branch' into tool_context.state
    # Return: {"status": "success", "message": "Preferences saved successfully."}
    pass


def get_customer_profile(tool_context: ToolContext) -> dict:
    """Retrieves the active customer's profile, preference settings, and verified identity."""
    # TODO: Read verified user ID from tool_context.user_id (Zero-Trust Security)
    # TODO: Read 'preferred_language' and 'preferred_branch' from tool_context.state
    # Return a structured dictionary with user_id, preferred_language, and preferred_branch.
    pass
```

#### Part B: Enterprise Multi-Turn Loan Application Draft Accumulator
In real-world enterprise banking, collecting 10+ loan fields in a single turn is overwhelming. Implement a multi-turn draft accumulator that updates `tool_context.state`:

```python
def update_loan_draft(
    field_name: str, field_value: str, tool_context: ToolContext
) -> dict:
    """Updates a specific field in the customer's active loan application draft.

    Args:
        field_name: The draft field to update ('applicant_name',
          'annual_income', 'loan_amount', 'tenure_months').
        field_value: The value provided by the customer for the field.
    """
    # TODO: Retrieve the existing dictionary 'loan_draft' from tool_context.state (or {} if missing)
    # TODO: Update draft[field_name] = field_value
    # TODO: Save updated dictionary back into tool_context.state["loan_draft"]
    # TODO: Check which required fields ('applicant_name', 'annual_income', 'loan_amount', 'tenure_months') are missing
    # Return status: 'in_progress' or 'ready_for_submission', captured_fields, and missing_fields.
    pass


def submit_loan_application(tool_context: ToolContext) -> dict:
    """Submits the accumulated loan application draft for processing and calculates EMI."""
    # TODO: Retrieve 'loan_draft' from tool_context.state
    # TODO: Verify all 4 required fields exist. If missing, return status: 'error' with list of missing fields.
    # TODO: Calculate approximate monthly EMI deterministically:
    #       P = float(loan_amount), N = int(tenure_months), R = 10.5 / 12 / 100 (10.5% annual interest)
    #       EMI = (P * R * (1 + R)**N) / ((1 + R)**N - 1)
    # Return status: 'submitted', application_id, total_loan, tenure_months, and calculated_emi.
    pass
```

---

### Step 3: Configure the Agent Node (`agent.py`)

Create `agent.py` and register all 4 stateful tools using the ADK 2.0 **`Agent`** class:

```python
# In agent.py
from google.adk import Agent
from .tools.banking import (
    set_customer_preference,
    get_customer_profile,
    update_loan_draft,
    submit_loan_application,
)

root_agent = Agent(
    name="banking_agent",
    model="gemini-2.5-flash",
    description="An enterprise banking assistant for preferences and multi-turn loan applications.",
    instruction="""
You are a helpful, professional enterprise banking assistant.
Use 'set_customer_preference' when the user specifies language or branch preferences.
Use 'get_customer_profile' when the user asks about their account or stored preferences.
Use 'update_loan_draft' as the user provides loan application details turn-by-turn.
Use 'submit_loan_application' ONLY when the customer asks to submit or finalize their loan application.
State all responses clearly and politely.
""",
    # TODO: Register all 4 imported stateful tool functions in this list:
    tools=[
        # add your functions here
    ],
)
```

---

### Step 4: Test and Verify the Agent

#### 1. Interactive Terminal Mode
Start the agent using the ADK CLI:

```bash
uv run adk run .
```

Test across multi-turn user dialogues:

1. **Preference Hydration Test:**
   ```text
   User: Set my preferred branch to MG Road Bengaluru and language to Hindi.
   User: What is my stored customer profile?
   ```
   *(Verify it reads `tool_context.user_id` and retrieves preferences saved in state!)*

2. **Multi-Turn Loan Accumulation Test:**
   ```text
   User: I want to apply for a loan. My name is Rajesh Kumar and annual income is 1200000.
   User: I need a loan amount of 500000 for 36 months.
   User: Please submit my loan application.
   ```
   *(Verify the draft accumulates turn-by-turn and `submit_loan_application` calculates EMI deterministically!)*

#### 2. Visual Trace & State Inspection (Web UI)
Launch the Web UI:

```bash
uv run adk web .
```

Open `http://localhost:8000` in your browser. Send a multi-turn loan prompt, click the **State** tab in the top navigation, and inspect `tool_context.state` live as keys (`loan_draft`, `preferred_branch`) update!

---

### Having Trouble?

If you get stuck, you can find the complete, production-ready code in the `lab-solution.md` file.

### Lab Summary

You have successfully built an enterprise stateful banking agent! You learned:
* How ADK injects **`ToolContext`** at runtime while stripping it from Gemini's JSON schema.
* How to use **`tool_context.state`** for multi-turn draft accumulators and preference caching.
* How to enforce **Zero-Trust Security** using `tool_context.user_id`.
* How to visually debug state mutations using `uv run adk web`.

### Self-Reflection Questions
1. Why is `tool_context.user_id` safer than accepting `user_id: str` as an argument from Gemini?
2. What happens to `tool_context.state` when the user opens a new chat session?
3. Why must objects stored in `tool_context.state` be JSON-serializable?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTAtYWR2YW5jZWQtZnVuY3Rpb24tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module10-advanced-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module10-advanced-function-tools-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
