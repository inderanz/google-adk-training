---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 1 Solution: Exploring the ADK Ecosystem

## Goal

This solution provides a summary of the key resources you should have explored during the lab.

---

### 💡 FDE & Instructor Hint: Steering AI Assistants (Antigravity)

When exploring the ADK ecosystem or asking **Antigravity** to explain ADK architectural components, use this **Module 01 Master Steering Prompt**:

> **Master Antigravity Steering Prompt Template (Module 01 - ADK Architecture):**
> *"You are an expert Google ADK 2.0 Forward-Deployed Engineer. Explain the Google Agent Development Kit (ADK) architecture and project setup following ADK 2.0 standards:*
> 1. *Focus on the ADK 2.0 component model: `Agent` nodes, `Runner` execution engine, `SessionService` state isolation, and `ArtifactService` file storage.*
> 2. *Emphasize that ADK 2.0 uses asynchronous event streams via `runner.run_async(...)` yielding `Event` objects.*
> 3. *Reference official Google ADK documentation links (https://google.github.io/adk-docs/) and modern `google.adk` imports.*
> 4. *Avoid legacy 1.x concepts like `.candidates` or manual HTTP wrappers."*

---

### 1. Official Documentation

The primary source for all information related to the Google Agent Development Kit.

*   [About the ADK](https://google.github.io/adk-docs/get-started/about)
*   [Installation Guide](https://google.github.io/adk-docs/get-started/installation)
*   [Quickstart Tutorial](https://google.github.io/adk-docs/get-started/quickstart)
*   [Agent](https://google.github.io/adk-docs/agents/llm-agents)
*   [Built-in Tools](https://google.github.io/adk-docs/tools/built-in-tools)
*   [Function Tools](https://google.github.io/adk-docs/tools/function-tools)

***Scavenger Hunt Answer:***
> The `contributing/samples/core/hello_world` sample doesn't include a standalone `main.py` script. Instead, `README.md`'s "Running and Inspecting the Agent Programmatically" section shows the entry-point pattern: an `InMemoryRunner` is created around the agent, a session is created via `runner.session_service.create_session(...)`, and the agent is actually run by iterating `async for event in runner.run_async(user_id=..., session_id=..., new_message=...)`. So the key entry point is the `Runner`'s `run_async()` method, not a `main()` function.

### 2. Official Code Repositories

The source code, examples, and issue trackers for the ADK.

*   **ADK Python Repository:** [https://github.com/google/adk-python](https://github.com/google/adk-python)
*   **Hello World Example:** [https://github.com/google/adk-python/tree/main/contributing/samples/core/hello_world](https://github.com/google/adk-python/tree/main/contributing/samples/core/hello_world)

### 3. Community and Support

*   **GitHub Issues:** For bug reports and feature requests.
*   **GitHub Discussions:** For questions, ideas, and community interaction.

By familiarizing yourself with these resources, you have built a strong foundation for the rest of this course.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module01-intro-to-ai-agents-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

