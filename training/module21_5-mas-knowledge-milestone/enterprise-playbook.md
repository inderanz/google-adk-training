---
sidebar_position: 4
title: "Enterprise Banking Playbook"
---

# Module 21.5 enterprise playbook

## Start from the bank’s requirement

> Show us the smallest application that completes the required checks and explains the next step. Tell us which parts are working examples and which still need a real bank-system connection.

The employee needs this result: A working preparation example plus an explanation of why each operation and service is needed. A missing source connection must remain an open task; adding more agents does not supply the missing data.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


## Assessment rubric

| Area | Points | Evidence required |
|---|---|---|
| Customer understanding | 20 | User, outcome, exclusions and measurable acceptance conditions |
| Architecture choice | 20 | Alternatives and a reason for each execution/service boundary |
| Contracts and control | 20 | Typed inputs, provenance, ordered rules and bounded work |
| Identity and failure design | 20 | Verified principal, case authorization, timeout and uncertain-outcome handling |
| Verification and teaching | 20 | Reproducible run, negative tests, live-eval plan and a clear explanation |

Target at least 80/100 with no critical boundary violation. This is a teaching rubric, not a regulatory certification. A critical violation includes trusting a model-supplied identity, treating memory as credit evidence, or claiming a failed/unknown operation succeeded.

## Suggested architecture decision

Start with authenticated ingress, a trusted case adapter, static required checks, an explicit route and an analyst-facing result. Add Gemini for explanation only if it helps users, with grounded inputs and evaluated outputs. Use the persistent session provider from Module 13.5. Keep the case record in its system of record.

If document operations needs independent deployment, put that adapter behind an authenticated Google Cloud service and the A2A interface from Module 21. Keep the local business contract stable. If all components share ownership and release cadence, retain an in-process boundary.

## Review questions and expected reasoning

Why not let the coordinator choose required checks? Because an instruction is not a deterministic scheduling guarantee. Why not make all work sequential? Independent read-only checks may overlap, though consistency still needs design. Why not distribute every agent? Service ownership and isolation must justify network complexity. Why not call an accepted memo “approved”? The gate checks preparation quality, not lending authority.

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
| Remove the model from an exact threshold calculation | The result remains correct and the design becomes easier to verify. |
| Make explanations optional | Required collection and routing must still complete without an LLM. |
| Move one check to a remote service on paper | Add identity, timeout, schema and reconciliation requirements. |
| Change the case state during collection | Explain how versions or a fresh read prevent a stale decision. |

## Explain the native Google integration

The runnable baseline is ADK. The customer architecture composes authorized Firestore/BigQuery adapters, Gemini where useful, and native session/memory services where required; the guide identifies which pieces are implemented versus planned.

Use the [shared customer integration specification](../module15-intro-to-multi-agent-systems/fde-learning-guide.md#a-concrete-integration-boundary-after-module-215) to identify the exact earlier-course adapters and missing bank-owned fields. Keep ADK control logic, managed hosting and business data services as separate responsibilities.

**Review challenge:** Present a change-impact review for a new policy version, new data owner and unavailable model. Show which contracts and tests change and which architecture boundaries stay stable.

## Evidence available in this revision

3 offline tests passed, including real ADK execution for the four routing scenarios. The milestone is an executable architecture baseline plus a design assessment, not a deployed banking system.

Reviewed on **3 October 2026** against **google-adk 2.11.0** and its installed public APIs. Examples require Python 3.12+ and were exercised with **Python 3.14.7**. Python 3.14.8 is the current stable patch release; it was not the local test interpreter. Use the supplied lockfile for the verified dependency resolution, and repeat the checks before upgrading.

Sources: [ADK release](https://pypi.org/project/google-adk/2.11.0/) and [Python 3.14.8 release](https://www.python.org/downloads/release/python-3148/). “Current” is dated verification, not a promise that a dependency will never change.

## Continue the story

Modules 15–21 introduced choices. This milestone combines and justifies them. Module 22 adds personalized continuity while keeping preferences separate from authoritative case facts.

[Previous module](../module21-distributed-graphs/README.md) · [Lab](./lab.md) · [Solution](./lab-solution.md) · [Enterprise playbook](./enterprise-playbook.md) · [Next module](../module22-state-and-memory/README.md)

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: Start with what the bank must guarantee. Add a model for language work, a service boundary for independent ownership and persistence for required continuity. Each addition needs a specific requirement and a failure contract.

Then assign: Change the customer brief to require a sanctioned ledger amount. Identify the missing adapter and entitlement contract before changing the route; a new fixture field does not complete that integration.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

## Official sources

- [ADK workflow options](https://adk.dev/workflows/)
- [Graph routes](https://adk.dev/graphs/routes/)
- [ADK safety and security](https://adk.dev/safety/)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->

## Continue with the integrated customer exercise

The [integrated banking lab](../module26-callbacks/integrated-lab.md) connects the authorized Firestore read, deterministic next step, versioned artifacts, Gemini explanation, evaluation, logging and Model Armor in one App. Complete its live and deployed checkpoints after the isolated lesson. Its scope excludes an unimplemented ledger adapter and credit approval.
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

