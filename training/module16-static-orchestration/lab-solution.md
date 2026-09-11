---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 16 Solution: Building a Hybrid News Aggregator

## Goal

This file contains the complete code for the `agent.py` script using the ADK 2.0 Hybrid Graph pattern (Sequential + Parallel).

### `news_aggregator/agent.py`

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# 1. Define Specialist Nodes
tech_researcher = Agent(
    name="tech_researcher",
    model="gemini-3.5-flash",
    instruction="Find 3 exciting headlines about AI and Robotics. Be concise.",
    output_key="tech_news"
)

market_researcher = Agent(
    name="market_researcher",
    model="gemini-3.5-flash",
    instruction="Find 3 key headlines about Stock Market trends. Be concise.",
    output_key="market_news"
)

summarizer = Agent(
    name="summarizer",
    model="gemini-3.5-flash",
    instruction="""
    You are a news editor. Create a brief newsletter using the data provided:
    TECH: {tech_news}
    MARKET: {market_news}
    
    Synthesize the information into a single, cohesive daily briefing.
    """
)

# 2. Define the Synchronization Point
syncer = JoinNode(name="news_sync")

# 3. Assemble the Workflow
# Parallel Fan-out + Sequential Fan-in
root_agent = Workflow(
    name="NewsSystem",
    edges=[
        # Both start at the same time and connect to the same JoinNode
        ("START", tech_researcher, syncer),
        ("START", market_researcher, syncer),
        
        # Once both are done, the syncer triggers the summarizer
        (syncer, summarizer)
    ]
)
```

### Self-Reflection Answers

1.  **What happens if one of the parallel researchers fails?**
    *   **Answer:** By default, the `JoinNode` waits for ALL incoming edges. If one fails, the `JoinNode` will not fire its outgoing edge, potentially stalling the workflow. In production, you would add retry logic or error handling to ensure the graph can still converge.

2.  **Can I add a third researcher (e.g., 'sports_researcher')?**
    *   **Answer:** Yes! You just define the agent and add a third edge: `("START", sports_researcher, syncer)`. The syncer will automatically wait for all three.

3.  **Why use `output_key` if data flows automatically?**
    *   **Answer:** While ADK 2.0 passes the output of one node to the next, a `JoinNode` receives multiple outputs. Using `output_key` saves individual results into the global session state, making it much easier for the `summarizer` to access specific variables like `{tech_news}` via string interpolation.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module16-static-orchestration-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

