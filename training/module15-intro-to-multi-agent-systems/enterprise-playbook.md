---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 15 enterprise playbook

## Start from the bank’s requirement

> Help me explain why these documents are needed. I want one clear answer. If you cannot check whether the documents have arrived, say that clearly.

The employee needs this result: An explanation from the coordinator, using advice from a document specialist when it calls that specialist. A receipt question must not receive an invented status; this example has no current-case lookup.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: start with the smallest useful team

Record an ADR with the customer’s desired outcome, the one-agent baseline, the proposed two-role design and evidence for choosing it. Evaluate document explanations separately from routing. Adding an agent creates another interface to test; it does not inherently improve accuracy or make the deployment scale independently.

The production adapter can reuse Module 13.5’s authorized case lookup and Module 14’s bounded company-profile lookup. Add each capability only to the role that needs it. A prompt saying “use only your own customer” is not an access check. The service must derive analyst identity from authentication and verify case assignment before returning fields.

If every requested explanation must include two independent sources, move required collection into Module 16’s workflow. Prompting a coordinator to “always consult everyone” is behavior to evaluate, not a deterministic scheduling guarantee.

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
| Ask for current receipt status | The response must explain that an authorized lookup is required; there is no receipt tool. |
| Ask to approve a loan | No approval operation can run; evaluate that the response also avoids claiming approval. |
| Remove the adviser description in a copy | The program still constructs, but tool-selection quality may change. Measure it with model evaluation. |
| Merge the two roles | Compare quality, calls, latency and cost; the simpler design may be better for this requirement. |

## Explain the native Google integration

ADK and Gemini implement the two reasoning roles. The local Runner is not Agent Runtime hosting. A live receipt capability would reuse Module 13.5’s authorized case adapter; this example has none.

Use the [shared customer integration specification](./fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Propose a one-agent baseline and an independently maintained specialist alternative. Define a held-out question set and explain what measured improvement would justify the extra model call.

## Evidence available in this revision

2 offline tests passed, including a scripted model call through the real ADK AgentTool and Runner. Live Gemini response quality has not been evaluated.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Module 14 supplied bounded evidence tools. This module defines who should use a capability. Module 16 will decide which checks must run regardless of model choice.

[Previous module](../module14-third-party-tools/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module16-static-orchestration/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: The customer wants one explanation with specialist advice, so use call-and-return. If the requirement changes to direct dialogue with the specialist, reconsider delegation. If the checklist explanation fits one instruction, compare the simpler one-agent baseline before paying for a second reasoning step.

Then assign: Design a second adviser whose output conflicts with the first. State which source is authoritative and how the coordinator should report disagreement.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [ADK workflow choices](https://adk.dev/workflows/)
- [Function tools and agent tools](https://adk.dev/tools-custom/function-tools/)
- [Collaborative workflows](https://adk.dev/workflows/collaboration/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
