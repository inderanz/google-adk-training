---
sidebar_position: 0
title: "Official Google ADK & Enterprise AI Reference Index"
---

# 📚 Official Google ADK & Enterprise AI Reference Index

Welcome to your official reference companion for the **Mastering Google ADK: From First Agent to Production** training course.

While this training curriculum gives you hands-on business scenarios, challenge labs, and enterprise architectural patterns, this index is your **authoritative source of truth**. Bookmark this page whenever you need exact Python method signatures, latest Google ADK 2.0 API releases, or official Google Cloud specifications.

---

## 🏛️ The FDE Standard: Learning Grounded in Production Truth

As a Google Principal Forward-Deployed Engineer (FDE), the most critical habit in enterprise AI engineering is **Zero-Hallucination Grounding**:
* **Never guess API parameters** — always cross-reference official SDK classes (`google.adk.Agent`, `OpenAPIToolset`, `SessionService`).
* **Design with Type Safety** — use typed Pydantic models for all tool contracts and structured outputs.
* **Inspect the Runtime Source** — verify installed signatures directly in your virtual environment:
  ```bash
  python -c "import google.adk; print(f'ADK Version: {getattr(google.adk, \"__version__\", \"2.x\")} at {google.adk.__file__}')"
  ```

---

## 🗺️ Module-to-Documentation Matrix

Use this matrix to navigate directly from what you are learning to the authoritative Google documentation:

| Learning Focus | Core Concepts & Classes | Related Modules | Official Google Documentation |
| :--- | :--- | :--- | :--- |
| **Foundations & Architecture** | `Agent`, `Runner`, `Instruction`, `Model` | **Modules 01 – 07** | [ADK Concepts & Agent Model ↗](https://google.github.io/adk-docs/agents/)<br/>[About Google ADK ↗](https://google.github.io/adk-docs/get-started/about) |
| **Tools & OpenAPI Synthesis** | `FunctionTool`, `OpenAPIToolset`, `ToolContext` | **Modules 08 – 14** | [ADK Tools & Tool Design ↗](https://google.github.io/adk-docs/tools/)<br/>[Built-in Tools & Grounding ↗](https://google.github.io/adk-docs/tools/built-in-tools) |
| **Multi-Agent Systems (MAS)** | Graphs, Static & Dynamic Routing, Collaborative Teams | **Modules 15 – 21.5** | [ADK Workflows & Orchestration ↗](https://google.github.io/adk-docs/workflows/) |
| **State, Memory & Artifacts** | `SessionService`, `session.state`, `ArtifactService` | **Modules 22 – 23** | [ADK Sessions & Memory Patterns ↗](https://google.github.io/adk-docs/sessions/) |
| **Evaluation & Quality Flywheel** | `adk eval`, LLM-as-judge, Custom Metrics | **Module 24** | [ADK Evaluation & Benchmarking ↗](https://google.github.io/adk-docs/observability/) |
| **Observability, RAI & Plugins** | Cloud Trace, BigQuery Agent Analytics, Safety Plugins | **Modules 25 – 26** | [ADK Observability & Logging ↗](https://google.github.io/adk-docs/observability/) |
| **Model Context Protocol (MCP)** | `McpToolset`, Stdio, Streamable HTTP (SSE) | **Modules 27 – 28, 34** | [ADK MCP Integration ↗](https://google.github.io/adk-docs/tools/)<br/>[Model Context Protocol Spec ↗](https://modelcontextprotocol.io/) |
| **UI Streaming & Integration** | Server-Sent Events (SSE), Streaming Run Events | **Modules 29 – 30** | [ADK Programmatic Execution ↗](https://google.github.io/adk-docs/get-started/quickstart) |
| **Enterprise Cloud Deployment** | Cloud Run, GKE, Agent Runtime, Gemini Enterprise | **Modules 31 – 36** | [Cloud Run Documentation ↗](https://cloud.google.com/run/docs)<br/>[Google Kubernetes Engine (GKE) ↗](https://cloud.google.com/kubernetes-engine/docs) |
| **Enterprise Capstone** | Aegis Incident Response & Full Production Architecture | **Modules 37 – 40** | [Google ADK Python Repository ↗](https://github.com/google/adk-python) |

---

## ⚡ Google AI & Gemini Model References

* **Gemini API Overview & SDKs:** [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
* **Gemini Models & Capabilities (Flash & Pro):** [https://ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
* **Google Search & Dynamic Grounding:** [https://ai.google.dev/gemini-api/docs/google-search](https://ai.google.dev/gemini-api/docs/google-search)
* **Google GenAI Python SDK (`google-genai`):** [https://googleapis.github.io/python-genai/](https://googleapis.github.io/python-genai/)
* **Vertex AI Enterprise Documentation:** [https://cloud.google.com/vertex-ai/generative-ai/docs](https://cloud.google.com/vertex-ai/generative-ai/docs)

---

## 🛠️ Google Cloud Infrastructure References

* **Google Cloud Storage (GCS) for Artifacts:** [https://cloud.google.com/storage/docs](https://cloud.google.com/storage/docs)
* **Firestore for Persistent Session Memory:** [https://cloud.google.com/firestore/docs](https://cloud.google.com/firestore/docs)
* **Cloud Run for Serverless Agent Hosting:** [https://cloud.google.com/run/docs](https://cloud.google.com/run/docs)
* **Cloud Logging & Cloud Trace:** [https://cloud.google.com/logging/docs](https://cloud.google.com/logging/docs)

---

## 💡 How to Use This Index as a Learner

1. **Before Starting a Module:** Scan the corresponding section in the table above to understand what Google ADK 2.0 primitives you will be using.
2. **During the Lab:** When implementing the `TODO` challenges, use the linked official guides if you need deeper clarity on method arguments or return types.
3. **Beyond the Course:** Keep this index as your ongoing enterprise desk reference when architecting and building your own agent solutions in production.
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

