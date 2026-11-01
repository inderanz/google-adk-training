---
sidebar_position: 4
title: "Module 34 Enterprise Playbook: Remote MCP Server Operations"
---

# Module 34 Enterprise Playbook: Remote MCP Server Security & Scaling

The integration architect needs this result: A scalable, secure remote Model Context Protocol (MCP) server running on Google Cloud Run that handles concurrent agent connections, externalizes shared state, protects tool invocations with OAuth 2.0 / OIDC tokens, and maintains low latency.

Read the [plain-English task and term explanations](./README.md) before reviewing the implementation details.

## 1. Remote MCP Architecture & Transport Patterns

While local MCP tools rely on `stdio` subprocess transport, enterprise-scale MCP services communicate over HTTP/SSE (`StreamableHTTP` or Server-Sent Events) across distributed cloud instances.

| Architecture Concern | Production Practice | Implementation Mechanism |
|---|---|---|
| Server Concurrency | Stateless ASGI Service | FastMCP service mounted via `mcp.streamable_http_app()`, served by Uvicorn with concurrency up to 80 requests/container. |
| Session & State Externalization | Remote Cache / Durable Store | Never store cart or conversation state in local container memory or volatile `/tmp`. Use Redis (Memorystore) or Firestore indexed by `mcp-session-id`. |
| Transport Security | Authenticated Cloud Run Service | Require authentication (`--no-allow-unauthenticated`). Client agents pass Google OIDC ID tokens in the `Authorization: Bearer <token>` header. |
| Tool Schema Governance | Versioned OpenAPI / MCP tools | Pin tool definitions and input schemas using Pydantic models with strict typing and runtime validation. |

## 2. Remote MCP Request & Authentication Flow

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```mermaid
sequenceDiagram
    autonumber
    participant Agent as ADK Agent (Cloud Run / Client)
    participant Auth as Google Cloud IAM (STS)
    participant MCP as Remote MCP Server (Cloud Run)
    participant Store as Memorystore / Firestore

    Agent->>Auth: Request OIDC Identity Token for MCP Service URL
    Auth-->>Agent: Return signed Google OIDC token
    Agent->>MCP: POST /mcp with Bearer Token & Mcp-Session-Id
    MCP-->>MCP: Verify OIDC Token & extract Session ID
    MCP->>Store: Fetch current session state
    Store-->>MCP: Return state
    MCP->>Store: Update state with tool execution result
    MCP-->>Agent: Return tool execution payload
```

## 3. Production Hardening Checklist

1. **Session Timeout & Eviction:** Configure Time-to-Live (TTL) on session keys in Redis/Firestore (e.g., 2 hours) to prevent unbounded memory growth.
2. **Error Handling & Sanitization:** Ensure the MCP server never leaks internal stack traces or connection strings in tool response payloads; return structured error objects.
3. **Keepalive & Reconnects:** Configure client `StreamableHTTPConnectionParams` with connection pooling, retries, and exponential backoff.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module34-enterprise-playbook -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

