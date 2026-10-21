---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 18 enterprise playbook

## Start from the bank’s requirement

> Always check the documents. Add the specialist check only for cases above the agreed threshold. Tell me which checks actually ran.

The employee needs this result: A list containing the required checklist result and, when applicable, the exposure-check result. A check that was skipped must not be described as completed. A failed required check must remain visible.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: bounded dynamic work

A customer may ask to “check every subsidiary.” Translate that into an authorized source of subsidiary IDs, a maximum item count, per-item contracts, concurrency limits and an explicit partial-failure policy. Do not hand an unbounded list to a model or use model-created URLs as execution targets.

Read-only children can often be retried under a bounded policy. State-changing children require idempotency and outcome reconciliation. If a child times out after a write, repeating the entire dynamic node may duplicate work unless the destination service enforces the operation key.

Treat the parent’s elapsed deadline and each child’s timeout as different budgets. Capture scheduled check names, case/version correlation, attempts and failure category. Avoid logging full financial documents to explain which branch ran.

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
| Use exactly the threshold amount | Only the checklist child runs. |
| Increase by one cent | Both checklist and exposure children run. |
| Use an invalid case ID | Validation stops the request before any child is scheduled. |
| Replace a child with a controlled failure in a copy | A success result must not silently omit the failed required check. |

## Explain the native Google integration

ADK owns child scheduling and events. Real read-only children can call Google-backed evidence adapters. Agent Runtime hosting and durable Sessions remain separate configuration; @node alone does not deploy or persist the application.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Extend the requirement to a bounded list of subsidiaries. Define authorization per subsidiary, maximum item count, concurrency budget and whether one failed child invalidates the whole pack.

## Evidence available in this revision

3 offline tests passed, including real ADK dynamic scheduling on both sides of the threshold. External retries and durable human approval are design extensions, not implemented by this fixture.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 17 selected a single destination. This module schedules a variable set of known checks. Module 19 will let a conversational coordinator consult advisory specialists.

[Previous module](../module17-structured-routing/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module19-collaborative-teams/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: “Always” places checklist outside the if. “Only above the threshold” puts exposure inside it. “A bounded list of checks” means the callables are developer-defined; no model-generated import or function name is accepted.

Then assign: Before implementing resumability, write an interruption matrix: before child, after child, before external commit, after commit with lost response. Give each external write a destination-enforced idempotency key; do not claim resume verification from the ordinary lab run.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [Dynamic workflows](https://adk.dev/graphs/dynamic/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Resume agents](https://adk.dev/runtime/resume/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
