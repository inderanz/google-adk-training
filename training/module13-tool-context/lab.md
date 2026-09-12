---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 13: Building a Secure Agent with HITL and Actions

## Goal

In this lab, you will build a **Secure Finance Agent**. You will learn how to implement **Human-in-the-Loop (HITL)** for sensitive transactions and how to use **`tool_context.actions`** to dynamically escalate a conversation to a supervisor node.

### Step 1: Prepare the Project

<Setup/>

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
uv run adk create secure_finance
cd secure_finance
```

### Step 2: Implement the Secure Tools

**Exercise:** Create `tools/finance.py`. You will implement a tool that handles investments.

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
# In tools/finance.py
from google.adk.tools import ToolContext

def execute_investment(amount: float, tool_context: ToolContext) -> str:
    """
    Executes a long-term investment.
    Use this tool only when the user explicitly asks to 'invest' or 'buy'.
    """
    # 1. Check for escalation: Any amount > 10,000 needs a human supervisor
    if amount > 10000:
        # TODO: Set tool_context.actions.transfer_to_agent to "supervisor"
        # Hint: This will dynamically route the user to a different node.
        pass
        return f"Amount ${amount} requires supervisor approval. Escalating..."

    # 2. Regular investment logic
    return f"Success! ${amount} has been invested in your portfolio."
```

### Step 3: Configure the Agent with HITL

**Exercise:** Open `agent.py`. You need to wrap your tool in a `FunctionTool` to enable the confirmation pop-up.

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
# In agent.py
from google.adk import Agent, Workflow
from google.adk.tools import FunctionTool
from .tools.finance import execute_investment

# --- 1. Define the Supervisor Node ---
supervisor = Agent(
    name="supervisor",
    model="gemini-3.5-flash",
    instruction="You are a senior supervisor. Review the large investment request and provide a final verdict."
)

# --- 2. Wrap the Tool for Safety ---
# TODO: Create a FunctionTool named 'secure_investment_tool'
# Enable require_confirmation=True
secure_investment_tool = ...

# --- 3. Define the Main Agent ---
finance_agent = Agent(
    name="finance_agent",
    model="gemini-3.5-flash",
    instruction="Help users with their investments. Use 'execute_investment' for trades.",
    tools=[secure_investment_tool],
    sub_agents=[supervisor] # Required for discovery during transfer
)

# --- 4. Build the Workflow Graph ---
root_agent = Workflow(
    name="SecureSystem",
    edges=[("START", finance_agent)]
)
```

### Step 4: Test the Secure Workflow

1.  **Start the Dev UI:** `uv run adk web .`
2.  **Test HITL:** 
    - Ask: "Invest $500 for me."
    - **Observe:** A confirmation box should appear. The code only runs if you click "Approve."
3.  **Test Dynamic Transfer:**
    - Ask: "Invest $50,000 for me."
    - **Observe:** Since `require_confirmation=True` wraps the tool unconditionally, you will see the *same* confirmation pop-up as above first — click "Approve" to let the tool actually run. Only then does the escalation logic inside `execute_investment` fire. In the Trace, you will see the `active_agent` change from `finance_agent` to `supervisor`.

### Lab Summary

You have built a production-ready secure agent! You learned:
*   How to **pause execution** for human approval using `require_confirmation`.
*   How to **reroute the conversation** dynamically using `tool_context.actions.transfer_to_agent`.
*   How to combine manual safety (HITL) with automated business rules (Escalation).

### Self-Reflection Questions
- Why is it important to use `require_confirmation` for sensitive actions rather than just relying on the LLM's instructions?
- In the dynamic transfer example, why did we need to add the `supervisor` agent to the `sub_agents` list of the `finance_agent`?
- How does `tool_context.actions` allow you to implement business rules that the LLM cannot override?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTMtdG9vbC1jb250ZXh0L2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module13-tool-context/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module13-tool-context-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

