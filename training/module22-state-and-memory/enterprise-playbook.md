---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 22 enterprise playbook

## Start from the bank’s requirement

> Remember whether I prefer concise or detailed explanations. Use that preference in a later conversation. Still read current case records when I ask whether a document has arrived.

The employee needs this result: The saved preference in a new conversation, with separately retrieved past context when available. An old memory must not override the current setting or be used as proof of document receipt.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: separate exact preferences and probabilistic recall

Use exact state or a dedicated preference record for settings that must be current. Use managed Memory Bank when semantic retrieval of selected past context is valuable. Keep case status, balances, policy and approvals in their authoritative services. Retrieval relevance is not proof of truth or authority.

## Native managed configuration

An existing Agent Runtime resource must have Memory Bank configured before the provider can use it. Enable only the memory topics needed for the customer purpose. Topic customization controls extraction behavior; it is not a guaranteed redaction or data-loss-prevention boundary. Minimize submitted events first, then apply the bank’s data controls.

The model may use a supported global endpoint while sessions and Memory Bank require a supported resource region. Keep GOOGLE_CLOUD_LOCATION separate from GOOGLE_CLOUD_AGENT_ENGINE_LOCATION. The SDK class retains the VertexAiMemoryBankService name; do not invent a replacement class to match product branding.

## Identity, lifecycle and operational controls

Derive user and tenant scope from authentication before creating a session or querying memory. The fixture user string is not production identity. Define how user IDs remain stable across channels and how tenant boundaries map to application/resource boundaries; never accept another customer’s user_id from the model.

Define consent/purpose, correction, retention and deletion for preferences, sessions, memory and source records independently. Deleting a session does not establish that all derived managed memories disappeared. Verify the provider’s lifecycle operations and complete deletion checks against each store.

Track ingestion failures, ingestion-to-retrieval delay, empty recall, stale recall and cross-user leakage tests. If a preference update succeeds but memory ingestion fails, keep the authoritative update and retry ingestion using an explicit durable operation record. Reusing an event ID is useful correlation, not a universal exactly-once guarantee across providers.

Evaluate conflicting preferences, malicious remembered instructions, revoked access and outdated case facts. Never interpret a memory entry as permission to call a banking tool. Logs should contain operation identifiers and failure categories rather than raw customer conversations by default.

## Translate the prototype into a customer implementation

| Concern | Concrete implementation decision | Acceptance evidence |
|---|---|---|
| Identity | Authenticate ingress; derive caller/tenant context in trusted code | Wrong-user and wrong-tenant requests are denied |
| Business truth | Use authorized case and ledger adapters | Freshness, provenance and record version are preserved |
| Hosting | Choose supported Agent Runtime or Cloud Run based on ownership and operations | Staging deployment and recovery checks on the chosen target |
| Persistence | Use a native ADK provider suitable for the environment | Restart and concurrent-session behavior tested |
| Secrets | Workload identity and Secret Manager where a secret is needed | No credentials in prompts, source or normal logs |
| Failure | Bound calls; report failure/unknown outcomes; reconcile writes | Timeout and duplicate-operation scenarios tested |
| Quality | Evaluate grounded explanations and capability selection | Recorded per-case results, including held-out cases |
| Operations | Cloud Logging/Trace with deliberate data capture policy | Case correlation, error categories and access controls verified |

Reuse the authorized Firestore case pattern from Module 13.5 and bounded evidence adapters from Module 14. Do not replace them with prompt-only access checks. The standalone examples isolate this module’s concept; their fixture values must be replaced with authorized records before customer use.

Keep a release record containing the dependency lock, model version/configuration, rule/contract versions, test results, evaluation results and known limitations. Google-native components reduce custom infrastructure work, but do not certify a solution’s security, compliance or business correctness.

## Failure and acceptance review

| Scenario | Required reasoning |
| --- | --- |
| Create a second session for the same user | It sees the current durable preference and can recall local memory within the same process. |
| Create another user or app | Neither state nor memory should expose the first user’s preference. |
| Restart both local providers | SQLite retains the preference; in-memory recall is empty. |
| Force memory ingestion to fail | The saved preference remains; the failure must not be described as a rolled-back transaction. |
| Recall stale preference text | The assistant must prefer current exact state over old memory. |

## Explain the native Google integration

The local path uses native ADK DatabaseSessionService and InMemoryMemoryService. The optional managed path uses VertexAiMemoryBankService with an existing Memory Bank-enabled resource. Managed Sessions configuration is taught in Module 13.5; Firestore still owns checklist truth.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Specify correction and deletion across session state, managed memories and source records. Design an ingestion failure retry record and prove that a recalled malicious instruction cannot grant access to a banking tool.

## Evidence available in this revision

7 offline tests passed using real ADK SQLite and in-memory memory providers, including new-session recall, user/app isolation, provider restart, minimal ingestion, partial failure and LoadMemoryTool execution through Runner with a scripted model. Managed Memory Bank and live Gemini recall were not executed.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 13.5 established durable conversations and authoritative case records. Modules 15–21.5 built the review flow. This module personalizes continuity; Module 23 will manage generated files as artifacts rather than storing large documents in state or memory.

[Previous module](../module21_5-mas-knowledge-milestone/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module23-artifacts/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: “Remember my explicit setting” requires exact durable state. “Recall relevant past context” motivates memory retrieval. “Do not rewrite bank facts” keeps checklist reads in the authorized case service even when memory contains a conflicting statement.

Then assign: Design deletion across the exact preference, source events and managed memories. Document what a successful delete from each service establishes and how stale retrieved context is handled.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [ADK state scopes](https://adk.dev/sessions/state/)
- [ADK memory services and tools](https://adk.dev/sessions/memory/)
- [Google cross-session memory recipe](https://github.com/google/adk-samples/tree/main/core/python/cross-session-memory)
- [Session rewind](https://adk.dev/sessions/session/rewind/)
- [Memory Bank setup](https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/set-up)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

