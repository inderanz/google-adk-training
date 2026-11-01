---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 20 enterprise playbook

## Start from the bank’s requirement

> Draft a note for this case and include both record references. Allow at most three drafts. If it still fails the checks, tell me that manual review is needed.

The employee needs this result: A note that passed the taught case-ID and citation checks, ready for a human to review. An invalid draft or an exhausted attempt limit must not be labelled successful.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: separate improvement from authorization

The memo loop can assist an analyst; it cannot grant itself lending authority. Keep approval operations in a separately authorized service. Do not use a critic model’s “approved” token, a substring search or a polished final draft as proof of business approval.

Bound attempts, wall time, tokens and evidence size. Three iterations are a business budget, while `max_llm_calls` and model retry limits are separate technical budgets. A provider retry inside one iteration can consume additional time and cost.

For long-running revision, persist the evidence version, attempt status, feedback and accepted draft reference through durable services. On resume, recheck evidence freshness and use idempotent writes. Cancellation or session rewind cannot undo a memo already emailed or a transaction already submitted. The lab performs neither operation.

Evaluate misleading citations, contradictory evidence, instruction injection in source text, stale policy and critic/writer agreement on an incorrect statement. A second model does not automatically provide independent verification.

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
| Run the default fixture | The first attempt has a citation defect; the second reaches human review. |
| Use the always_incomplete writer | Three attempts end in needs_manual_review without an accepted memo. |
| Return malformed data | The application reports invalid_model_output. |
| Write misleading prose with both valid citations | The structural gate can pass; explain why a semantic evaluation and human review still matter. |

## Explain the native Google integration

ADK runs the bounded workflow, and the optional Gemini Agent drafts text. Durable Sessions can preserve conversation events; they do not provide a transaction that reverses an externally published memo.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Add a semantic evaluation rubric for contradicted evidence and misleading citations. Keep it separate from the exact gate, and justify whether a failing semantic check should trigger revision, human review or rejection.

## Evidence available in this revision

5 offline tests passed, including successful revision, three-attempt exhaustion and malformed output. The optional Gemini writer and semantic memo quality have not been evaluated live.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 19 composed advisory results. This module bounds revision of an evidence memo. Module 21 moves one specialist behind a real protocol boundary.

[Previous module](../module19-collaborative-teams/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module21-distributed-graphs/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: “Up to three” becomes range(1, 4). “Identify this case” becomes an equality check. “Cite both records” becomes a set comparison. “Return for manual review” becomes an explicit exhaustion status, never reuse of the last failed draft as accepted.

Then assign: Design a semantic gate for contradicted evidence. Decide whether its failure consumes a revision attempt and how the bank reviews disagreement between structural and semantic checks.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [Dynamic workflows](https://adk.dev/graphs/dynamic/)
- [Graph cycles and routes](https://adk.dev/graphs/routes/)
- [ADK evaluation criteria](https://adk.dev/evaluate/criteria/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

