---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 17 enterprise playbook

## Start from the bank’s requirement

> If documents are missing, tell me to collect them first. Otherwise, tell me whether the case needs specialist review or standard review. Do not describe either route as loan approval.

The employee needs this result: Exactly one next step: collect documents, specialist review or standard review. Malformed input is rejected. An unexpected routing label goes to manual checking.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: policy is versioned code or configuration

Record the policy identifier and effective version alongside the selected route. A route trace should explain which facts and rule version produced it. Keep policy updates under the bank’s change process. Do not let a retrieved document or user message rewrite the routing table.

Separate three decisions: who may access the case, what facts are authoritative, and which workflow step follows those facts. Authentication/IAM answer the first, the case and ledger services answer the second, and this router answers the third.

If a handler later writes to Cloud Tasks, Pub/Sub or a case API, add an application idempotency key tied to case version and intended action. ADK events and workflow routes do not provide exactly-once execution of an external business operation. A timeout after a write is an uncertain outcome until the destination is checked.

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
| Incomplete checklist and maximum allowed amount | Document collection wins because its rule comes first. |
| Complete checklist at and one cent above the threshold | The two requests select different analyst queues. |
| Change one emitted label in a copy | The default handler sends it to manual triage; it must not look like normal review. |
| Put an approval field in the request | The input schema rejects the extra field. |

## Explain the native Google integration

The route is native ADK control flow. Bank policy and current case facts remain outside the model. A Pub/Sub or case-queue write would be a separate authorized operation; emitting next_step does not perform it.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Add a policy-version field and propose migration behavior for sessions started under an older rule set. Explain how the audit record identifies the actual applied rule.

## Evidence available in this revision

3 offline tests passed, including a real ADK run for all four decision-table scenarios and strict input checks. No live queue or credit-decision service is connected.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 16 collected evidence. This module chooses a step from fixed rules. Module 18 will schedule a varying set of checks without hiding business logic inside a prompt.

[Previous module](../module16-static-orchestration/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module18-dynamic-orchestration/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: Translate “missing documents first” into the first if. Translate “above” into >, including a boundary case at equality. The fallback represents an unrecognized control label, not permission to guess the bank policy.

Then assign: Add a policy version and effective date to an authoritative input contract. Show how a change from above to at-least affects both the condition and its boundary test.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [ADK graph routing](https://adk.dev/graphs/routes/)
- [Structured graph data](https://adk.dev/graphs/data-handling/)
- [Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

