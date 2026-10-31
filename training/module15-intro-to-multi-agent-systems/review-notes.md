---
sidebar_position: 6
title: "Modules 13.5–26: Teaching Review and Verification Record"
---

# What has been reviewed, and what still needs customer evidence

Reviewed on **3 October 2026**. Scope: all 16 modules from 13.5 through 26, including 21.5 and 25.5. The review covers READMEs, guided labs, solutions, enterprise playbooks, shared guides, runnable examples, dependency locks, tests and diagrams.

The course provides a tested foundation for learning and adapting ADK patterns. It is not a certification that an unconfigured example is ready to process a bank's customer data. “Enterprise grade” must be established for a particular deployment, workload and operating team. Read the evidence below before making that claim.

## Changes from this review

| Finding | Correction | Why it matters to a learner or FDE |
|---|---|---|
| The previous baseline missed a new ADK release | Updated all examples, deployment requirements and documentation to ADK 2.11.0; refreshed their locks | The code and the explanation refer to the same tested release |
| The database-extra explanation described an older dependency issue | Explain that ADK 2.11.0 already selects SQLAlchemy's asyncio extra | Learners should not carry an obsolete workaround into customer designs |
| The memory-provider discussion omitted a new native option | Explain SqliteMemoryService and a local extension exercise, while retaining the managed Memory Bank path | A learner can distinguish persistent local retrieval from sessions and managed memory |
| Evaluation evidence could be ambiguous | Reject empty criteria, duplicate dataset IDs, duplicate metrics and non-finite thresholds in Module 24 and the capstone | An apparently passing row must not hide a missing requirement or failure |
| The capstone brief compressed several unfamiliar ideas into one paragraph | Start with an analyst's daily task, one concrete example and observable requirements | Learners can derive the implementation without already knowing the product vocabulary |
| The shared guide still described some completed later lessons as future work | Extend it to 13.5–26 and link the actual cloud and capstone paths | The banking story and service choices remain consistent across the sequence |
| Copied solution code could drift from runnable examples | Add a repository consistency checker and verify the packaged capstone copies | The example that runs must be the example that is explained |

## Software evidence

All **121 contract tests passed** on Python **3.14.7**, using each module's own locked environment with **ADK 2.11.0**. The five Modules 23–26 deployment examples also passed their **38 tests** on Python **3.11.16**. These tests use real ADK objects with scripted model replies or controlled service boundaries. They do not supply Gemini quality scores or cloud IAM evidence.

| Module | Tests | Contract exercised | Further evidence needed for a customer |
|---|---:|---|---|
| 13.5 | 26 | Session restart, state scopes, assignment checks and transaction decisions | Real Firestore contention, uncertain write recovery and managed Sessions |
| 14 | 23 | LangchainTool wiring, schema, bounded lookup and failure statuses | BigQuery access, approved source maintenance and Gemini tool choice |
| 15 | 2 | AgentTool call and return through Runner | Whether the model consults the right adviser and explains its limits |
| 16 | 4 | Required collection, join and matching case IDs | Authorized source adapters, dependency timeouts and workload measurements |
| 17 | 3 | Ordered routing and threshold boundaries | Bank-owned, versioned routing policy and real case input |
| 18 | 3 | Conditional child scheduling and bounded input | Durable interruption/resume and idempotent external operations |
| 19 | 3 | Adviser results, single-turn return and chat transfer | Multi-turn task behaviour, completeness and model quality |
| 20 | 5 | Citation gate, revision budget and incomplete outcomes | Factual quality, actual source support and live revision behaviour |
| 21 | 4 | A2A server input and proxy configuration | Hosted authentication, validated responses and durable task recovery |
| 21.5 | 3 | Integrated collection/routing on a synthetic snapshot | Approved mapping to the customer's actual systems |
| 22 | 7 | Preference persistence, memory scope and partial ingestion failure | Managed recall, correction, deletion and retrieval delay |
| 23 | 4 | Exact artifact versions and linked report/manifest | Fresh GCS readback, retention and access controls |
| 24 | 9 | EvalSet/config parsing, actual tool wiring and release gate | Real agent/judge runs, held-out scenarios and result provenance |
| 25 | 2 | Bounded metadata and visible tool failure | Exported Cloud Trace/Logging, correlation and capture settings |
| 25.5 | 7 | Inspection decisions, replacement and session-history handling | Real Model Armor allow/match/unavailable results and policy coverage |
| 26 | 16 | Callback execution, capstone scope/artifacts and evaluation gate | Hosted capstone, real services, bank identity and operational evidence |

The local HTTP checks exercise native App loading, session creation, `/run` and the deployed-result parsing logic. The A2A lab also has a real loopback transport check. These are local integration checks, not Agent Runtime deployment results. Rendering and portal-build checks validate presentation and links; they cannot prove a diagram's business assumptions.

The document checks cover **69 Markdown/MDX documents**, **129 Python files** and **122 complete source listings**. All **33 Mermaid diagrams** rendered at 390-pixel and 900-pixel widths without horizontal page overflow. The protected portal build passed. The capstone failure branch was also corrected to show that unsuccessful tool results still pass through output inspection.

## Version and API decisions

The ADK baseline is the [2.11.0 release](https://pypi.org/project/google-adk/2.11.0/). Package locks also record the resolved Google Gen AI SDK and other dependencies. [Python 3.14.8](https://www.python.org/downloads/release/python-3148/) is the current stable patch release identified during this review; the available local interpreter was 3.14.7. Do not relabel a 3.14.7 run as a 3.14.8 test.

The native deployment template still uses Python 3.11. The local interpreter does not select the hosted base image. Follow the [cloud guide](../module23-artifacts/google-cloud-lab-guide.md) and inspect the actual image and runtime settings.

ADK's A2A adapter remains marked experimental in this release. AgentTool can emit an upstream deprecation warning from its internal Runner call; the lesson uses the public AgentTool interface and supplies plugins through App where applicable. Neither warning should be hidden or confused with a statement that the A2A protocol itself is experimental.

## Teach understanding before adding complexity

Use the [learning guide](./fde-learning-guide.md#choose-your-starting-point) for foundation and experienced paths. For every lesson, ask the learner to explain the customer's task first, point to the Python rule, identify the ADK caller, predict one changed input and observe one failure. An expert should also defend why a simpler function, tool or workflow would or would not meet the requirement.

The isolated labs intentionally do not all require a model or cloud account. A deterministic rule is easier to understand when its result can be predicted exactly. The [integrated banking lab](../module26-callbacks/integrated-lab.md) then connects the authorized Firestore checklist, report artifacts, Gemini explanation, Model Armor and operational metadata. It does not pretend to implement an absent bank-ledger integration.

## Reproduce the review

From the repository root, check source/document consistency:

```bash
uv run --no-project python scripts/check_banking_course.py
```

This standard-library checker needs Python 3.11+. It checks syntax, declared ADK pins, relative file links, full solution listings and reused capstone sources. It does not contact Google Cloud or run the model. For each module, then run its documented contract command from `example/`:

```bash
uv sync --locked --python 3.11
uv run python -m unittest discover -s tests -v
```

For a customer release, additionally retain the actual live evaluation results, hosted resource and code revision, authenticated-user tests, source/service failure tests, exact artifact readback, inspected telemetry and recovery measurements. No live Google Cloud deployment or Gemini quality pass is asserted by this review. The [cloud guide](../module23-artifacts/google-cloud-lab-guide.md#record-the-result-and-clean-up-deliberately) explains how to record that evidence.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
