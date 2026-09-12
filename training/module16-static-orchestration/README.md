---
sidebar_position: 16
title: "Module 16: Static Orchestration - Linear and Parallel Edges"
---

# Module 16: Static Orchestration - Linear and Parallel Edges

## Theory

In ADK 2.0, orchestration is no longer about choosing between a "Sequential" or a "Parallel" agent. Instead, you design the **geometry of your graph** using **Edges**.

A `Workflow` is a deterministic engine that executes nodes based on these connections. By arranging your edges, you can create linear pipelines, concurrent branches, or a mix of both.

### 1. Sequential Flow (Linear Edges)

When you define edges in a chain, the ADK executes them one after another. Each node waits for the previous one to finish and receives its output as input.

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
from google.adk import Workflow

# A -> B -> C
my_pipeline = Workflow(
    name="SequentialSystem",
    edges=[
        ("START", researcher),
        (researcher, writer),
        (writer, editor)
    ]
)
```

### 2. Parallel Flow (Fan-Out)

When multiple edges originate from the same source (like `"START"` or a specific node), the ADK triggers all target nodes **simultaneously**.

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
# A and B start at the same time
parallel_run = Workflow(
    name="ParallelSystem",
    edges=[
        ("START", task_a),
        ("START", task_b)
    ]
)
```

### 3. Synchronization (The `JoinNode`)

When you have parallel branches, you often need to "wait" for all of them to finish before moving to a final step. This is called **Fan-In**, and it is handled by the **`JoinNode`**.

The `JoinNode` acts as a barrier: it will not fire its outgoing edge until **every incoming edge** has completed.

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
from google.adk.workflow import JoinNode

syncer = JoinNode(name="sync_point")

# Fan-out to A and B, then converge at 'syncer' to run C
complex_graph = Workflow(
    name="HybridSystem",
    edges=[
        ("START", task_a, syncer),
        ("START", task_b, syncer),
        (syncer, final_task)
    ]
)
```

### Why use Static Orchestration?

1.  **Performance:** Parallel execution reduces total latency to the duration of the slowest branch.
2.  **Predictability:** The path is fixed and code-defined; there is no "hallucination" risk in the routing.
3.  **Transparency:** The Dev UI Graph View gives you a 1:1 visual map of your business process.

### Key Takeaways
- **Edges define the flow:** Chain them for sequential, branch them for parallel.
- **`JoinNode`** is the mandatory synchronization point for parallel branches.
- **Data Flow:** ADK 2.0 handles passing results between nodes automatically, ensuring a seamless pipeline.

## Enterprise Lens: Process design is part of the AI architecture

This module is not just about graph topology. It is about modeling real business operations as a reliable workflow.

The practical design question is: do we need a linear process, a parallel fan-out, or a synchronized workflow that merges results before making a decision?

Read the companion guide here:

- [Module 16 Enterprise Playbook](./enterprise-playbook.md)
- [Enterprise ADK Playbook Index](../enterprise-adk-roadmap.md)

This keeps static orchestration linked to the wider ADK architecture story: specialization, tools, memory, routing, and governance working together as one system.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module16-static-orchestration-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

