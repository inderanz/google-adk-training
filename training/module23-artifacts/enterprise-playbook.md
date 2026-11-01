---
sidebar_position: 4
title: "Enterprise Integration Playbook"
---

# Enterprise playbook: Artifacts: Reproducible Banking Review Packs

## Begin with an agreed customer contract

> Save the checklist used for each report. Keep a way to find the exact saved version later, even after the case changes.

The employee needs this result: A saved checklist, report and small linking record identifying their versions. Missing or invalid source content must not produce a successful report. Failed saves may need later cleanup.

Read the [plain-English task and term explanations](./README.md#read-this-as-a-bank-employees-task) before the implementation details.


| Customer question | Decision to record |
|---|---|
| Who owns the bank facts? | Identify the authoritative repository, schema, version and access rule. |
| Who is allowed to use this capability? | Derive identity from the authenticated caller; do not trust a model-provided user_id. |
| What counts as complete? | Agree successful, incomplete, denied and unavailable outcomes separately. |
| What can leave the application? | Define content capture, inspection, artifact and evaluation-data boundaries. |
| Who accepts the pilot? | Name the business, platform and control owners and their evidence requirements. |

## Native Google responsibilities

| Responsibility | Service or API | Acceptance evidence |
|---|---|---|
| Reasoning | Gemini through the Google enterprise backend | Configured model/location and live customer-rubric results |
| Hosted execution | Gemini Enterprise Agent Platform Agent Runtime | Authenticated invocation of the exact deployed resource |
| Conversation persistence | Managed Sessions through native ADK providers | Retrieve a session after a fresh client/process |
| Review-pack storage | GcsArtifactService backed by Cloud Storage | Retrieve exact artifact versions and verify scope |
| Content inspection in 25.5 | Regional Model Armor template | Benign, match and unavailable paths measured against the real template |
| Operational evidence | Cloud Logging and Cloud Trace | Locate the deployed invocation and identify its outcome |

The [cloud lab guide](../module23-artifacts/google-cloud-lab-guide.md) supplies the configuration and native deployment/test commands. Supporting services such as Cloud Storage are Google Cloud services with their own IAM and retention settings; they are not automatically configured by naming Agent Platform.

## Module-specific acceptance evidence

| Exercise | Evidence to retain |
|---|---|
| Prepare a fresh pack | Inspect function responses and record the returned source/report/manifest versions. |
| Request source version 999 before saving it | Expect source_missing and no new report. |
| Save the same source name again | Expect a new version; retrieve both versions explicitly. |
| Load with another test user/session | Expect no access through that namespace; separately test real API authorization. |

Keep the code revision, dependency lock, resource names, timestamp, model/judge configuration and observed failures with the test report. Use synthetic data for the course. Customer data requires the agreed handling controls.

## Connect to the earlier banking modules

Replace a synthetic checklist only at the authorized repository boundary introduced in Module 13.5. Keep source status, version and ownership. Module 14’s company-profile adapter is a separate source; a case ID is not automatically a company ID. Carry the evidence references into the review pack, quality criteria and operational diagnosis. Memory from Module 22 can personalize presentation but cannot replace current bank facts.

## Operational failure and recovery

Define timeouts, bounded retries, idempotency and unknown outcomes at the actual service boundary. A timed-out write may have succeeded. A content scan cannot undo a transaction, and a log record cannot make a failed action successful. Establish who investigates failures and which evidence permits a retry.

## Advanced design review

Replace the source fixture with the authorized Module 13.5 repository adapter. Preserve its case version and observation timestamp, specify idempotency for retries, and describe how partially saved packs are reconciled.

## Handover checklist

- Demonstrate the normal request and a meaningful failure on the selected hosted resource.
- Present case-level model evaluation results, not just successful HTTP calls.
- Confirm service identities and scope restrictions with negative access tests.
- Verify stored/exported data and retention against the agreed policy.
- Identify all remaining fixtures, unimplemented adapters and unevaluated paths.
- Assign operational ownership and document rollback/recovery and resource cleanup.

## Instructor acceptance: demonstrate transfer

Ask the learner to explain this derivation without looking at the implementation: “The exact input reviewed” requires an explicit version. “Which report used it” requires a manifest. “Survive restart” selects GcsArtifactService. “Still retrieve earlier evidence” means never silently substitute latest during replay.

Then assign: Choose recovery for a report saved before a failed manifest save: permit an orphan and reconcile it, or coordinate a committed business record. Explain why neither a digest nor three successful writes creates a transaction.

Accept the explanation only when it names the native ADK execution boundary, identifies a trusted source, predicts a failure and proposes evidence that could disprove the design. A copied successful trace does not establish independent understanding.

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

