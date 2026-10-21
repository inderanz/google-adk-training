---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 16 enterprise playbook

## Start from the bank’s requirement

> Do both checks every time. Show me the combined result only after both finish. Make sure both results belong to the same case.

The employee needs this result: One result containing both completed checks, with their source labels. A failed check or mismatched case ID must not become a complete-looking result.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: required collection belongs in code

Keep compulsory evidence collection deterministic. Use a Gemini agent after validated collection if the customer needs a readable explanation. Give that agent a structured output schema and retain source identifiers; text generation must not reinterpret “missing evidence” as “approved.”

A real parallel design needs a consistency contract. For example, require both results to carry the same case version or re-read after a conflicting update. Two successful HTTP responses are not proof of a coherent business snapshot. Decide whether a partial pack is acceptable; if it is, mark each missing result explicitly and prohibit progression to a decision step.

Measure the two branch latencies, join wait, end-to-end latency and source failures. Parallelism can reduce elapsed time when independent I/O overlaps, but introduces fan-out load. Bound concurrency at the service and workflow layers, and retain provider-specific timeouts. Never attach an unbounded number of customer records to one prompt.

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
| Set the amount to 20,000,000 cents | The exposure result is false at the boundary; it becomes true one cent above. |
| Set documents_complete to "false" | Validation rejects the string instead of interpreting it as a boolean. |
| Supply mismatched case IDs directly to combine | The contract test proves the pack is rejected. |
| Make one check fail in a copy | No successful combined pack should be produced; inspect how the failure is surfaced. |

## Explain the native Google integration

ADK runs the graph. Module 13.5 supplies the Firestore checklist pattern, and Module 14 supplies a bounded BigQuery profile pattern for an expanded evidence pack. A real requested amount still needs a bank-owned source; this lab does not fetch a ledger.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Design a partial-result policy and a consistency rule for two real services. Decide whether the pack can be displayed, routed or only marked incomplete when one source is unavailable.

## Evidence available in this revision

4 offline tests passed using the real ADK graph runtime, including both joined results, strict boundaries and mismatched-case rejection. The fixture does not call Firestore or a ledger.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 15 separated roles. This module makes required collection explicit. Module 17 will use the collected facts to select the next review step.

[Previous module](../module15-intro-to-multi-agent-systems/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module17-structured-routing/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: “Both” creates two required operations. “Independent” permits fan-out. “Only after” creates a join. “Same case” creates the comparison in combine. Those four phrases explain the graph and the guard before any SDK import is chosen.

Then assign: Compare graph output passing with template SequentialAgent/ParallelAgent composition. Templates are appropriate for fixed agent arrangements; the graph makes these function-node inputs and named joins explicit.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [Graph routes and joins](https://adk.dev/graphs/routes/)
- [Graph data handling](https://adk.dev/graphs/data-handling/)
- [Supported workflow choices](https://adk.dev/workflows/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
