---
sidebar_position: 5.1
title: "Module 05 Enterprise Playbook: Running Agents in the Real World"
---

# Module 05 Enterprise Playbook: Running Agents in the Real World

This playbook connects the ADK runtime concepts from Module 05 to real customer engineering work. The purpose is to help a forward-deployed engineer, solution architect, or AI coding agent translate ambiguous business requests into a robust ADK runtime design.

## Business translation

A vague customer request might sound like:

> "We want an AI assistant for our support team."

That is not yet an implementation spec. The real ask is usually something like:

- Who is using the agent?
- Is it internal or customer-facing?
- Should it be interactive, API-based, or both?
- Do we need chat state across multiple turns?
- Will this run locally, in staging, or in a production cloud deployment?
- Do we need log traces for debugging and compliance reviews?

This module matters because agent runtime selection is a real design decision. Your agent may need:

- local interactive debugging
- command-line testing for automation
- REST API integration for downstream systems
- a runtime that supports sessions and conversation continuity

## The core ADK concept

Module 05 introduces the practical ways to run an agent:

- `uv run adk web` for interactive local debugging
- `uv run adk run` for terminal-based interaction
- `uv run adk api_server` for exposing agent functionality over HTTP

These are not just convenience commands. They represent three different engineering modes:

1. Developer mode
2. Test mode
3. Service mode

This separation is extremely important in enterprise engineering. A customer solution cannot be built with only one execution mode.

## Enterprise pattern

### 1. Developer mode: interactive debugging
Use this when building the first version of an agent.

Best use cases:

- prompt tuning
- tool debugging
- session flow verification
- tracing how the agent is reasoning

Good pattern:

- turn on the developer UI
- inspect the trace
- verify prompts and tool calls
- fix instructions before production work

### 2. Test mode: CLI-based validation
Use this when validating a scripted workflow.

Best use cases:

- automated smoke tests
- regression checks
- CI validation
- repeated prompt testing

Good pattern:

- keep a stable golden input set
- assert expected outputs for known scenarios
- test tool calls and state transitions

### 3. Service mode: API runtime
Use this when the agent is integrated into a business application.

Best use cases:

- internal portal
- workflow automation backend
- customer-facing support assistant
- API-driven orchestrator

Good pattern:

- expose a controlled API boundary
- capture session IDs and user IDs
- standardize auth and logging
- deploy behind proper infrastructure security controls

## Common ambiguous customer scenarios

### Scenario A: “We want an AI support assistant”
This usually requires:

- API server mode for business integration
- session tracking for multi-turn support conversations
- logs and traceability for support investigations
- tool access to ticket data or knowledge systems

Suggested module lineage:

- [Module 05](../module05-running-agents/README.md)
- [Module 06](../module06-programmatic-execution/README.md)
- [Module 08](../module08-intro-to-tools/README.md)
- [Module 12](../module12-built-in-tools-grounding/README.md)

### Scenario B: “We need a quick demo for our stakeholders”
This usually requires:

- `uv run adk web`
- interactive testing
- trace view for live walkthroughs

Good design decision:

- do not over-architect the demo
- prove the flow quickly
- then convert the working pattern into production code

### Scenario C: “We need to embed this in our enterprise app”
This usually requires:

- API server mode
- persistent sessions
- proper auth and security
- controlled access to internal resources

This is where the runtime strategy becomes critical.

## Production-ready design principles

### 1. Separate developer experience from production runtime
Do not treat local interactive tools as the production architecture. They are useful for learning and debugging, but production requires a service boundary.

### 2. Treat traceability as a first-class requirement
The trace view is not just for debugging. In customer systems, it helps with:

- issue analysis
- prompt review
- root-cause debugging
- policy and compliance audits

### 3. Plan for sessions and continuity
Every conversation needs a way to preserve context. That is why user IDs and session IDs matter in real-world systems.

### 4. Decide on runtime before writing business logic
A common mistake is to code the agent logic before deciding how it will be used. The execution model shapes the architecture.

## Reusable enterprise template

A practical pattern for enterprise teams:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
# Conceptual pattern for enterprise agent runtime
# 1. Build agent logic
# 2. Wrap in App
# 3. Create runner
# 4. Use user_id and session_id for state
# 5. Run via async programmatic flow
# 6. Log, trace, and evaluate result
```

This is the same pattern you see later in Module 06 and beyond, but the value of Module 05 is recognizing when to use local debugging, CLI testing, and API execution modes.

## Related modules and interlinking

This module connects to several larger patterns:

- [Module 06: Programmatic execution](../module06-programmatic-execution/README.md) — the core Python runtime pattern behind real agent services
- [Module 07: Multimodal input](../module07-multimodal-and-images/README.md) — extends the runtime to visual inputs
- [Module 08: Intro to tools](../module08-intro-to-tools/README.md) — adds action-taking capabilities
- [Module 12: Grounding and retrieval](../module12-built-in-tools-grounding/README.md) — adds knowledge access
- [Module 13.5: Firestore persistence](../module13_5-firestore-persistence/README.md) — adds persistent sessions and memory
- [Module 35: Deployment agent runtime](../module35-deployment-agent-runtime/README.md) — production deployment patterns

## Anti-patterns to avoid

### Anti-pattern 1: Using local debugging tools as the final architecture
The developer UI is excellent for testing, but it is not the production deployment shape.

### Anti-pattern 2: Ignoring session design
If you do not think about user and session identity, your agent becomes inconsistent across interactions.

### Anti-pattern 3: Building the agent without a testing workflow
Without a CLI/test loop, it becomes difficult to remain confident as the application evolves.

### Anti-pattern 4: Treating runtime mode as an afterthought
The runtime mode affects design decisions, not just tooling choices.

## The agent-friendly checklist

When using Copilot, Codex, Claude Code, or a custom engineering agent, this module should inform the following decisions:

- choose the right runtime mode for the use case
- keep local tooling for debugging and validation
- separate dev-time and production-time patterns
- model sessions carefully
- instrument and trace before production rollout
- validate with narrow but realistic prompts and scenarios

## Practical customer takeaway

If a customer says: "Build us an AI assistant," the enterprise answer is not just "create an agent." It is:

- decide the execution model
- decide the conversation model
- decide how the assistant will access tools/data
- decide how it will be observed and controlled
- decide how it will be deployed and audited

## Official ADK / Google references

Use the official Google and ADK documentation as the current source of truth when updating runtime, CLI, or deployment guidance:

- ADK documentation home: https://google.github.io/adk-docs/
- ADK agent and runtime concepts: https://google.github.io/adk-docs/agents/
- ADK workflows and execution model: https://google.github.io/adk-docs/workflows/
- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Vertex AI generative AI docs: https://cloud.google.com/vertex-ai/generative-ai/docs

These references should be checked alongside this playbook whenever the framework evolves or when customer environments require a production-ready runtime decision.

Module 05 is the point where execution strategy becomes part of the architecture.

## Summary

This module is where you stop thinking of an agent as a demo and start thinking of it as a runtime system. The real engineering skill is not just running a model; it is choosing the correct execution path for the problem, then validating and scaling that path across the enterprise.

This is the foundation for the larger ADK architecture story that continues into the next modules.

## Official ADK / Google references

- ADK documentation home: https://google.github.io/adk-docs/
- ADK agent/runtime concepts: https://google.github.io/adk-docs/agents/
- ADK workflows and execution model: https://google.github.io/adk-docs/workflows/
- Gemini API overview: https://ai.google.dev/gemini-api/docs
- Vertex AI generative AI docs: https://cloud.google.com/vertex-ai/generative-ai/docs

These references should be used as the canonical source for runtime guidance, runtime modes, and any future ADK updates to the developer and service execution model.

---

## Related roadmap

- [Enterprise ADK Playbook Index](../enterprise-adk-roadmap.md)
- [Module 06: Programmatic Execution](../module06-programmatic-execution/README.md)
- [Module 07: Multimodal and Image Processing](../module07-multimodal-and-images/README.md)
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

