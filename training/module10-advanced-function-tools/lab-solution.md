---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 10 Solution: Building a "Memory" Agent with Stateful Tools

## Goal

This file contains the complete code for the `agent.py` and `tools/memory.py` files using ADK 2.0 standards for stateful tools.

### `memory_agent/tools/memory.py`

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
from google.adk.tools import ToolContext

def store_name(name: str, tool_context: ToolContext) -> str:
    """
    Saves the user's name to the session memory.
    Use this tool when the user tells you their name.
    """
    # Write to session state
    tool_context.state["user_name"] = name
    return f"Got it, {name}! I've saved your name."

def recall_name(tool_context: ToolContext) -> str:
    """
    Retrieves the user's name from the session memory.
    Use this tool if the user asks who they are or what their name is.
    """
    # Read from session state
    name = tool_context.state.get("user_name", "Stranger")
    return f"Your name is {name}."
```

### `memory_agent/agent.py`

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
from google.adk import Agent
from .tools.memory import store_name, recall_name

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    description="An agent node that remembers users.",
    instruction="""
    You are a friendly assistant. 
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.
    """,
    tools=[store_name, recall_name]
)
```

### Self-Reflection Answers

1.  **Why is it more reliable to store data in the session state rather than just relying on the LLM's chat history?**
    *   **Answer:** Chat history is "noisy" and has a limited context window. As a conversation gets longer, older messages (like an introduction) might be pushed out. Session state is **structured and persistent**; it acts as a reliable "database" for key facts that the agent can access deterministically.

2.  **What would happen if you used the same key (e.g., "user_name") for two different users?**
    *   **Answer:** Nothing bad! The ADK's `Runner` automatically isolates sessions based on the `user_id`. Each user has their own independent `state` dictionary, so Alice's "user_name" will never overwrite Bob's "user_name."

3.  **How could you extend this agent to remember other things?**
    *   **Answer:** You can create more tools that follow the same pattern (e.g., `store_preference(key, value)`, `recall_preference(key)`). Because `tool_context.state` is just a Python dictionary, you can store any JSON-serializable data there.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module10-advanced-function-tools-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

