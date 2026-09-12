---
sidebar_position: 12
title: "Module 12: Built-in Tools and Grounding"
---

# Module 12: Built-in Tools and Grounding

## Theory

### Why Built-in Tools Matter

Traditional AI models have a knowledge cutoff date—they don't know about recent events, current news, or real-time information. Built-in tools solve this by allowing models to **ground** their responses in current web data. This process of retrieving external information to enhance the LLM's generation is the foundation of **Retrieval Augmented Generation (RAG)** systems.

**Key Advantages**:
*   **Current Information:** Access to up-to-date web content.
*   **No Local Execution:** Tools run inside the model's environment (managed by Google), requiring no local code execution or infrastructure from you.
*   **Automatic Integration:** The LLM seamlessly incorporates the search results into its final response, often providing citations.
*   **Production Ready:** These tools are used by real-world, enterprise applications for grounding.

**Important:** Built-in tools are a feature of Gemini 2.0 and newer models and will raise errors with older versions.

### `google_search`: Web Grounding

The `google_search` tool is a built-in capability that allows a Gemini 2.0+ model to search the web to find information. When you add this tool to your agent, the model can autonomously decide to use it when a user's query requires current information.

In the modern ADK, using web grounding by itself is incredibly simple — just import it and add it to `tools`:

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
from google.adk.tools import google_search

agent = Agent(
    name="grounded_agent",
    model="gemini-3.5-flash",
    instruction="Search the web to answer the user's question.",
    tools=[google_search],
)
```

As Module 9 covered, `google_search` **cannot** be listed alongside your own custom function tools in that same `tools` list — that's a restriction from the Gemini API itself (not the ADK), and it constructs fine in Python but fails the moment the model actually runs: `400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools.`

### Combining Grounding with Custom Logic

So how do you use `google_search` *and* your own custom processing together? Since they can't share one agent, the answer is **sequential composition**: run a search-only agent, then feed its output into a second agent that has your custom tools.

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
from google.adk.tools import google_search

def my_custom_tool(item_id: str) -> dict:
    """Looks up internal warehouse data."""
    return {"status": "success", "stock": 42}

# Agent 1: only the built-in tool
research_agent = Agent(
    name="research_agent",
    model="gemini-3.5-flash",
    instruction="Search the web to answer the user's question.",
    tools=[google_search],
)

# Agent 2: only your custom tool(s)
warehouse_agent = Agent(
    name="warehouse_agent",
    model="gemini-3.5-flash",
    instruction="Use my_custom_tool to check warehouse stock for the item you're given.",
    tools=[my_custom_tool],
)
```

You then call `research_agent` first, take its final text output, and pass it as input to `warehouse_agent` — two separate `Runner`/`run_async` calls in your own Python code, not a single agent juggling both tool types. This is exactly the workaround Module 9 introduced; the lab below builds it hands-on.

### Looking Ahead: Managed Agents (Preview)

ADK 2.4.0 introduces `ManagedAgent`, a way to plug Google's own first-party, server-hosted agents (like the Antigravity agent) directly into your ADK flow — no sandbox to provision, no client-side tool declarations, just an `agent_id` and a `GEMINI_API_KEY`. It implements the same `BaseAgent` contract you've been using, so it drops into a workflow like any other agent. The trade-off: you get powerful built-in capabilities (web search, server-side code execution) but lose the fine-grained control you have with `LlmAgent`. It's still Preview, so treat it as a preview of where ADK is headed rather than a pattern to build on yet. As of v2.6.0, `ManagedAgent` also accepts an `instruction` parameter (forwarded as `system_instruction`), so you're not limited to the backend's default behavior.

### `google_maps_grounding`: Location-Based Queries

The `google_maps_grounding` tool enables agents to answer location-based queries, such as finding nearby places, getting directions, or understanding geographic context. This tool is currently only available when using the **Vertex AI API**.

### Key Takeaways
- Built-in tools like `google_search` allow agents to access real-time information from the web, overcoming the LLM's knowledge cutoff.
- These tools run within the model's environment, making them easy to set up and scale.
- A built-in tool like `google_search` **cannot** share an agent's `tools` list with custom function tools — that's a Gemini API restriction, confirmed by a real `400 INVALID_ARGUMENT` at runtime, not just an ADK convention.
- To combine grounding with custom logic, use **sequential composition**: a search-only agent's output feeds into a second agent that has your custom tools, called one after another in your own code.

## Enterprise Lens: Grounding as a trust and relevance layer

This module matters because enterprise AI becomes far more valuable when it can answer with current, relevant facts instead of relying on stale model knowledge alone.

The real question is not only “can the agent search?” but “can the agent produce a grounded answer that helps a user make a better decision?”

Read the companion guide here:

- [Module 12 Enterprise Playbook](./enterprise-playbook.md)
- [Enterprise ADK Playbook Index](../enterprise-adk-roadmap.md)

This keeps the grounding lesson connected to the bigger ADK story: combine fresh facts, structured business tools, and careful reasoning into a system that is more reliable and more usable in real customer environments.

## Official ADK / Google references

Use the official Google and ADK documentation as the current source of truth for grounding, search, and tool behavior:

- ADK docs home: https://google.github.io/adk-docs/
- ADK tools documentation: https://google.github.io/adk-docs/tools/
- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Google Search grounding docs: https://ai.google.dev/gemini-api/docs/google-search
- Vertex AI docs: https://cloud.google.com/vertex-ai/generative-ai/docs

These references should be reviewed whenever the course is updated for new grounding capabilities, search behavior, or model/tool constraints.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module12-built-in-tools-grounding-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

