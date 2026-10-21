---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 19 enterprise playbook

## Start from the bank’s requirement

> Use the relevant specialists to help explain how to prepare this case. Give me one answer, and keep any statements about what the specialists cannot verify.

The employee needs this result: A coordinator response that combines the consulted specialists’ advice and preserves their limitations. If a required consultation is missing, record that as a behaviour failure or choose a workflow that forces the consultation.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Architecture decision: flexible advice versus required evidence

Use collaborative teams for bounded advisory work where model-selected consultation is acceptable. Use deterministic orchestration for compulsory banking checks. A combined design can collect required evidence in a graph and then use a coordinator to explain it.

Measure more than final wording. Record selected adviser, result validity, omissions, duplicate calls, token use and elapsed time. An attractive final answer can hide that an adviser never ran. Evaluate valid alternative call orders instead of demanding an arbitrary sequence.

Version specialist contracts together with their evaluation cases. If an adviser gains a live case tool, revisit identity propagation, data minimization and prompt-injection tests. An output schema ensures field shape; it does not prove that a recommendation follows policy or that the source was authorized.

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
| Ask for a full preparation explanation | Evaluate that both advisers are consulted and limitations survive synthesis. |
| Ask only why ownership evidence is needed | Evaluate whether the selected consultation is appropriate; do not force an unrelated exact tool order. |
| Compare --mode single_turn and --mode chat | Inspect the selected delegation/transfer capability and the final responding agent. |
| Require a compulsory two-source evidence pack | Explain why Module 16 provides a stronger scheduling guarantee than this coordinator prompt. |

## Explain the native Google integration

ADK supplies AgentTool and delegation modes; Gemini supplies reasoning. Current case facts would come from authorized Google-backed adapters. Agent Platform hosting, shared memory and service IAM are not automatically created by sub_agents.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Replace optional consultation with compulsory collection in a design variant. Compare control guarantees, number of model calls, error handling and evidence completeness. Explain when each design is appropriate.

## Evidence available in this revision

3 offline tests passed, covering two explicit AgentTool calls, a single-turn delegation that returns to the coordinator, and a chat transfer whose specialist responds. All model replies are scripted fixtures. Live consultation quality remains unevaluated.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Modules 16–18 controlled required work in code. This module introduces flexible advisory consultation. Module 20 will bound attempts when a generated memo needs revision.

[Previous module](../module18-dynamic-orchestration/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module20-cyclic-workflows/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: One combined explanation suggests a coordinator receiving notes. A sustained conversation with an expert suggests delegation. Mandatory evidence collection belongs in deterministic scheduling even if the final explanation uses advisers.

Then assign: Supply a valid structured note with an unsupported assertion. Design a quality criterion that rejects it despite schema success.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [Collaborative workflows and modes](https://adk.dev/workflows/collaboration/)
- [Agent tools](https://adk.dev/tools-custom/function-tools/)
- [Remote A2A consumption](https://adk.dev/a2a/quickstart-consuming/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
