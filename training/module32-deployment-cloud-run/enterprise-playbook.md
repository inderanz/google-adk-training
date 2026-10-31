---
sidebar_position: 4
title: "Module 32 Enterprise Playbook: Cloud Run Agent Operations"
---

# Module 32 Enterprise Playbook: Serverless Containerization & Cloud Run Operations

The enterprise DevOps engineer needs this result: A hardened, observable Cloud Run container deployment for ADK agents that delivers rapid cold-starts (under 3 seconds), zero idle cost, secure secret injection via Secret Manager, and strict VPC service perimeter compliance.

Read the [plain-English task and term explanations](./README.md) before reviewing the implementation details.

## 1. Cloud Run Operational Specifications

Deploying an ADK agent to Cloud Run requires configuring container concurrency, CPU allocation, memory limits, and security perimeters.

| Operational Area | Production Standard | Implementation Reference |
|---|---|---|
| Container Base Image | Distroless or `python:3.11-slim` | Multi-stage build; compile wheels in builder, copy only binaries to final runtime image. Minimize attack surface. |
| CPU Allocation | `cpu-allocation: always` vs `throttled` | Use `throttled` (CPU only during request processing) for conversational bots. Use `always` if performing background session flushes or async queue consumption. |
| Concurrency Tuning | Concurrency: 40–80 requests/instance | ADK agents make async I/O calls to Gemini and tools. Concurrency of 40–80 maximizes throughput per container instance without thread starvation. |
| Memory Sizing | Minimum 1 GiB per instance | ADK runtime and fast API wrappers require ~256MB base; set 1–2 GiB to accommodate large multimodal payloads and JSON buffers. |
| Secret Injection | Secret Manager integration | Pass secrets as environment variables via `--set-secrets` rather than baking into images or passing in build arguments. |

## 2. Cloud Run Zero-Trust Architecture

```mermaid
flowchart LR
    Client["Client / Web UI"] --> Ingress["Cloud Run Ingress<br/>(HTTPS / Cloud Armor)"]
    subgraph VPC_SC["VPC Service Controls Perimeter"]
        Ingress --> Container["ADK Agent Container<br/>(python:3.11-slim)"]
        Container --> SM["Google Secret Manager<br/>(API keys & credentials)"]
        Container --> Vertex["Vertex AI Gemini API<br/>(Private Google Access)"]
        Container --> Storage["Cloud Storage / Firestore<br/>(Durable Session Store)"]
    end
```

## 3. Deployment & Reliability Verification

1. **Cold-Start Optimization:** Pre-compile Python bytecode with `python -m compileall` in the Dockerfile and defer heavy tool imports until first invocation if not needed at startup.
2. **Graceful Shutdown:** Handle `SIGTERM` signals emitted by Cloud Run during instance scale-down; allow running tool executions up to 10 seconds to flush telemetry before process termination.
3. **IAM Least Privilege:** Assign the Cloud Run service a dedicated Service Account with only `roles/aiplatform.user` and `roles/secretmanager.secretAccessor`.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module32-enterprise-playbook -->
