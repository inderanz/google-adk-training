---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 21 enterprise playbook

## Start from the bank’s requirement

> Let our assistant ask the document team for the checklist result. If their service cannot be reached, tell the analyst that the check could not be completed.

The employee needs this result: A response from the separate service that the local application can inspect. A timeout or an unreachable service must not be reported as a completed check.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: deployment independence justifies A2A

Use Cloud Run or the supported managed Agent Runtime path when ownership and deployment requirements justify a remote specialist. Authenticate the endpoint. Cloud Run service-to-service authentication uses an identity token with the target audience; a reusable access-token snippet is not automatically interchangeable. Use official Google authentication libraries and refresh credentials correctly.

Do not ship the loopback sample with an unauthenticated public ingress. It has no end-user authorization, persistent A2A task store or production audit sink. Those are explicit acceptance items for the deployment modules, not features inferred from `to_a2a`.

Map principal, tenant, case entitlement and correlation IDs in a trusted server layer. Do not copy the caller’s entire session or credentials into an A2A message. Verify the agent card’s actual RPC targets as well as its discovery origin. Treat remote outputs as untrusted data with a versioned schema, size limit and provenance.

For writes, use an application operation ID, a durable destination-side record and a reconciliation endpoint. A2A task completion and an ADK event do not confer exactly-once banking semantics. Track discovery failure, authentication failure, timeout, invalid output and business rejection separately.

Before release, test the exact pinned client/server protocol pair, expired credentials, denied case access, cancellation, duplicate requests, restart and partially completed work. The local sample demonstrates the adapter boundary only.

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
| Inspect the card before running the client | Check the advertised endpoint and capabilities against the local server. |
| Stop the server before a call | The call fails; no successful evidence result is fabricated. |
| Send an unknown case or string boolean | The strict server-side schema must reject the request. |
| Plan a side-effecting remote task | Explain why retries require idempotency and why an HTTP timeout leaves outcome uncertainty. |

## Explain the native Google integration

The local transport uses the official ADK A2A adapter. A deployed specialist may use supported Agent Runtime or Cloud Run hosting according to the deployment requirements. Loopback Uvicorn is neither managed hosting nor production authentication.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Write a versioned remote-response contract, destination allowlist and timeout/reconciliation policy. Explain how verified user identity reaches the remote case authorization layer without entering a model-visible prompt.

## Evidence available in this revision

4 offline contract tests and 1 real loopback A2A transport test passed. The client received the deterministic checklist response through the local Uvicorn server. No model call or cloud deployment was involved; production authentication and remote recovery remain untested.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 20 bounded local iterative work. This module introduces a remote ownership boundary. Module 21.5 asks you to justify the simplest architecture for the complete case.

[Previous module](../module20-cyclic-workflows/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module21_5-mas-knowledge-milestone/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: Independent ownership motivates a service interface. Reusing a Python function would not meet independent release requirements. Use the official adapter instead of hand-writing an A2A transport; keep business authorization in the remote capability.

Then assign: Produce a correlation table from one actual request and design a response-loss scenario. Specify which operations are safe to retry and which require reconciliation.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [Expose an ADK agent through A2A](https://adk.dev/a2a/quickstart-exposing/)
- [Consume a remote agent](https://adk.dev/a2a/quickstart-consuming/)
- [Cloud Run service authentication](https://docs.cloud.google.com/run/docs/authenticating/service-to-service)
- [Official A2A SDK](https://github.com/a2aproject/a2a-python)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
