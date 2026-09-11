---
sidebar_position: 20.1
title: "Module 20 Enterprise Playbook: Cyclic Workflows for Iteration and Self-Correction"
---

# Module 20 Enterprise Playbook: Cyclic Workflows for Iteration and Self-Correction

This module introduces one of the most practical enterprise patterns in ADK: iterative refinement. In earlier modules, the workflow was generally described as a set of linear, branching, or specialist-based steps. Module 20 adds the behavior that many real-world systems need: a loop that reviews, corrects, and improves the output until a quality or completion condition is met.

For a forward-deployed engineer, this is a key pattern because a lot of business work is not one-pass. It is iterative, review-heavy, and usually benefits from quality control loops.

## The forward-deployed engineer lens

Enterprise teams often describe problems like:

- “We need the answer reviewed before sending it to the customer.”
- “The draft should be refined until it meets our quality criteria.”
- “This task needs a critic and a refiner to improve output quality.”
- “We want the system to self-correct, but still stop safely after a bounded number of passes.”

This is exactly the kind of situation where cyclic workflows become useful.

## Business translation

The core idea is simple: a workflow can run a review step, inspect the result, and then decide whether to revise it or stop.

Examples:

- draft generation → critic → edit loop
- incident summary → validation step → rewrite if needed
- proposal response → compliance check → revise and re-run
- research summary → quality review → improve clarity and completeness

This is not “the model keeps looping until it feels good.” It is a disciplined operational pattern designed around explicit exit conditions and safety limits.

## Core ADK concept

ADK 2.0 uses dynamic workflows and `@node` functions to implement cyclic behavior. A node can call other nodes repeatedly using Python control flow, such as `for` or `while` loops.

This is valuable because it enables:

- iterative refinement loops
- review and critique logic
- bounded retry or optimization cycles
- explicit stop conditions
- better observability over intermediate output quality

## Enterprise pattern

### Pattern 1: Critic-refiner loop
The first node reviews the current output and identifies gaps or issues. The second node uses that feedback to revise the work.

This is a common workflow for:

- writing and editing
- policy checks
- analysis quality improvements
- summarization refinement

### Pattern 2: Rework until acceptance
The loop continues until the work meets a business rule, quality threshold, or explicit “APPROVED” condition.

This pattern is useful when a result is not acceptable until it passes a defined bar.

### Pattern 3: Bounded self-correction
The system should always limit the number of iterations to protect cost, latency, and reliability. This is an essential production rule.

## Why this matters in production

A lot of AI systems fail not because the first pass is wrong, but because there is no control over iteration. Without a clear quality gate and loop limit, the system can spin, waste cost, or produce increasingly noisy results.

A strong enterprise workflow treats self-correction as a controlled operating pattern rather than an unbounded hallucination loop.

## Best practices for real customer work

### 1. Define a clear exit condition
Stop only when the result is accepted, not merely because the loop has run a few times.

### 2. Add a maximum iteration cap
Use a fixed limit such as 3–5 iterations to ensure cost and latency stay under control.

### 3. Keep review criteria explicit
The critic should follow a clear rubric, not vague “is this good?” logic.

### 4. Keep the loop narrow and purposeful
Do not build a large, open-ended self-correction loop if the real business task is simple and one pass is enough.

### 5. Log intermediate output
This is essential for debugging, evaluation, and quality tracking.

## Common enterprise anti-patterns

### Anti-pattern 1: infinite or unbounded iteration
Without a hard stop, the workflow becomes expensive and unpredictable.

### Anti-pattern 2: vague quality criteria
If the critic cannot articulate the condition, the system will not reliably know when to stop.

### Anti-pattern 3: using the loop to hide weak prompts
A loop should improve quality, not compensate for poor structure or unclear task definition.

### Anti-pattern 4: ignoring observability
You need to see what changed between iterations to evaluate whether the loop actually improves the output.

## Cyclic workflows as an operational pattern

This module is best understood as a production reliability pattern. It turns an AI process into a reviewable, inspectable loop that improves output under guardrails.

This is a very practical pattern for customer delivery, especially in content generation, analysis, and decision-support workflows that benefit from refinement.

## Related modules

- [Module 16 Enterprise Playbook](../module16-static-orchestration/enterprise-playbook.md)
- [Module 17 Enterprise Playbook](../module17-structured-routing/enterprise-playbook.md)
- [Module 18 Enterprise Playbook](../module18-dynamic-orchestration/enterprise-playbook.md)
- [Module 24 Evaluation](../module24-evaluation/README.md)
- [Module 25 Observability](../module25-observability/README.md)

## Recommended next move in the learning path

After mastering iterative loops, the next step is to move into collaborative teams and higher-level coordination patterns, where multiple specialized agents work together across a longer process and shared context.

## Final enterprise takeaway

Module 20 shows that AI workflows are not only about one-time generation. They are often about controlled improvement over time.

The strongest enterprise systems use loops with clear termination criteria, structured review, and operational guardrails. That is how iterative systems become trustworthy rather than noisy.

## Official ADK / Google references

- ADK documentation home: https://google.github.io/adk-docs/
- ADK workflows and orchestration docs: https://google.github.io/adk-docs/workflows/
- ADK agent and runtime docs: https://google.github.io/adk-docs/agents/
- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Vertex AI generative AI docs: https://cloud.google.com/vertex-ai/generative-ai/docs

These are the official sources to validate workflow behavior, orchestration patterns, and future changes to iterative execution design.

---

## Related roadmap

- [Enterprise ADK Playbook Index](../enterprise-adk-roadmap.md)
- [Module 20 README](./README.md)
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

