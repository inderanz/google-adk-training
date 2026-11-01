---
sidebar_position: 5
title: "Google Cloud Lab Setup and Deployed Verification: Modules 23–26"
---

# Run and verify the banking labs on Google services

The cloud exercises use Gemini Enterprise Agent Platform Agent Runtime and managed Sessions, Gemini through the enterprise backend, Cloud Storage artifacts, Google Cloud observability, and Model Armor for Module 25.5. The bank records remain synthetic so learners can inspect complete traces without handling real customer documents.

Three different claims require three different demonstrations:

| Execution path | Where the agent code runs | What it establishes |
|---|---|---|
| `unittest` contract tests | Local Python process with scripted replies | Python contracts and ADK integration behavior |
| `run.py` | Local Python process calling real Google services | Model/service integration with managed persistence |
| `check_deployed.py` | Sends requests to an existing Agent Runtime deployment | Behavior of the hosted application and its configured services |

Do not label the second path a deployed test. Do not label a scripted model reply a passing Gemini evaluation. Save the evidence appropriate to each claim.

## Confirm the customer and platform choices

Use a dedicated development project with billing and approved access. Record the project, deployment region, Gemini model/location, artifact bucket, runtime service identity and, for Module 25.5, the full Model Armor template resource name. The model location, runtime region, bucket location and inspection region are separate choices that must satisfy the customer's residency requirements.

These labs do not infer deployment authorization from whichever project happens to be selected in `gcloud`. Use the approved project explicitly. Existing resources are preferable for the course; provisioning an enterprise environment belongs in reviewed infrastructure code. See the [official Agent Runtime setup](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/setup) and [deployment guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/deploy-an-agent).

| Principal or resource | Required responsibility | Check before the lab |
|---|---|---|
| Local developer identity | Invoke permitted models/services and selected runtime | Application Default Credentials and project access |
| Runtime workload identity | Call Gemini, persist sessions and access the lab artifact bucket | Approved service identity and narrowly scoped permissions |
| Deployment identity | Build/deploy the container and use the selected runtime identity | Platform deployment permissions; separate from end-user authorization |
| Artifact bucket | Store versioned review-pack artifacts | Bucket access, location, retention and lifecycle policy |
| Model Armor template | Define the inspection policy | Supported region, enabled filters and template invocation permission |
| Telemetry destinations | Store operational observations | Writer permissions, reader access, retention and content-capture policy |

The native ADK HTTP server's `user_id` is a scope parameter. It is not proof of an authenticated bank employee's identity. A production front door must derive tenant/user scope from verified identity and prevent callers from selecting another person's scope. The supplied checker uses unique synthetic test users under an authorized development caller.

## Configure a real-service run

From the selected module's `example/` directory:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv sync --locked --python 3.11
cp .env.example .env
gcloud auth application-default login
```

Edit `.env`. Do not commit it. These are resource/configuration values, not downloaded keys:

| Variable | Example shape | Purpose |
|---|---|---|
| `GOOGLE_GENAI_USE_ENTERPRISE` | `true` | Select the enterprise model backend |
| `GOOGLE_CLOUD_PROJECT` | Your development project ID | Project for the selected services |
| `GOOGLE_CLOUD_LOCATION` | A location supported by the configured model | Gemini endpoint location |
| `GEMINI_MODEL` | A model available to this project | Agent model; the sample preserves the existing 3.5 Flash default |
| `ADK_MAX_LLM_CALLS` | `8` | Native default model-call budget, including the deployed API path |
| `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS` | `false` | Disable ADK span message-content capture |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | `NO_CONTENT` | Disable content capture for the corresponding Python GenAI instrumentation |
| `AGENT_RUNTIME_LOCATION` | A supported region | Managed Sessions location for the local real-service runner |
| `AGENT_ENGINE_ID` | Existing runtime/resource ID | Managed Sessions parent used by `run.py` |
| `ARTIFACT_BUCKET` | Bucket name without `gs://` | GCS artifact provider |
| `MODEL_ARMOR_TEMPLATE` | `projects/P/locations/L/templates/T` | Existing regional inspection template for 25.5 |

If a runtime does not yet exist, deploy the package in the next section first, then use its returned ID for the local managed-session exercise. Do not invent an ID or silently replace managed Sessions with in-memory storage to make the command pass.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python run.py "Prepare CASE-001 for human review."
```

The CLI prints the managed session ID and ADK events. Repeat with `--session-id` to continue that conversation. The local deadline is 90 seconds and the model-call limit is eight. The synthetic user scope is fixed for this CLI; it is not a customer authentication implementation.

The supplied deployment environment also sets the native `ADK_MAX_LLM_CALLS` default to eight. Confirm it is present on the hosted resource. The CLI's 90-second Python deadline is not automatically a server deadline; the deployed checker bounds its own HTTP wait, which cannot undo or guarantee cancellation of server-side work. Configure and test the hosted deadline and retry policy separately. Message-capture settings do not control every possible log sink or completion-upload integration; inspect the actual exported data.

ADC is suitable for a developer workstation. Hosted workloads use their configured service identity. Do not embed an AI Studio key or export a service-account private key to follow this lab.

## Deploy the reviewed package to Agent Runtime

The source package exports both `app` and `root_agent`. Current ADK loading recognizes the App, which preserves plugin registration. The application name matches the directory: `bank_review`. All lesson implementation files and deployment requirements live inside that package; the CLI/test helpers stay outside it.

The native ADK command retains the API name `agent_engine`; the managed product is called Agent Runtime. The existing resource/API terminology is not a reason to replace supported imports with invented renamed modules.

The pinned ADK 2.11.0 CLI currently generates a `python:3.11-slim` base image. It does not inherit your local Python 3.14 interpreter. These examples therefore declare Python 3.11+ compatibility and are checked on both 3.11.16 and 3.14.7. Review the generated image and its resolved patch release. If your platform standard requires a different Python base image, use the supported custom-container deployment path with an explicitly reviewed Dockerfile and repeat the same checks; do not imply that a local interpreter flag changes the native deployment template.

After completing the module's local checks and live quality review, prepare an approved development deployment. The deployment command reads `.env` inside the agent package, whereas the local runner command explicitly reads the parent `.env`:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
cp .env bank_review/.env
uv run adk deploy agent_engine \
  --project YOUR_DEVELOPMENT_PROJECT \
  --region YOUR_RUNTIME_REGION \
  --display_name banking-module-23 \
  --artifact_service_uri gs://YOUR_DEDICATED_LAB_BUCKET \
  --otel_to_cloud \
  bank_review
```

Use the appropriate module number in the display name. Review the deployment identity and runtime identity using your platform team's configuration; the example above does not claim to configure least-privilege IAM by itself. The native CLI accepts `--agent_engine_config_file` for supported runtime configuration. Consult the current deployment schema before adding a custom service account, network or scaling setting.

The deployed ADK runtime discovers its managed Sessions environment. Do not pass `memory://` for sessions or artifacts in this deployment. The explicit artifact URI selects the GCS provider. The package's requirements pin the lesson's ADK and Model Armor dependencies; the deployment tool can add its own required runtime dependency. Review generated build inputs and retain deployment metadata with the tested code revision.

The native CLI may override the model-location environment during deployment based on its configuration. Inspect the deployed settings and choose a model supported at the resulting endpoint. A successful local `global` model call does not establish availability in a different runtime region.

The command creates or updates a real billable resource. Retain the returned resource name. For an intentional update use the documented `--agent_engine_id` flag with the existing resource; omitting it can create another deployment. Keep each module's checkpoint distinguishable during testing, since all packages use the same ADK app name.

`--otel_to_cloud` enables the native telemetry path and sets the current runtime telemetry flag. Avoid deprecated `--trace_to_cloud`, `--staging_bucket`, `AF_TRACE_TO_CLOUD` and copied flags from older tutorials. Confirm behavior with `uv run adk deploy agent_engine --help` for the pinned version.

## Verify the actual hosted application

From that module's `example/` directory:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python check_deployed.py \
  --resource projects/PROJECT/locations/REGION/reasoningEngines/RUNTIME_ID
```

The checker validates the resource-name format and derives Google's regional HTTPS endpoint. `google.auth.default` supplies credentials to `AuthorizedSession`; tokens are not printed or written into the report. It creates a managed test session through the deployed ADK surface and posts a typed user message to `/run` through Agent Runtime's authenticated HTTP passthrough. It uses non-streaming execution deliberately.

The native passthrough endpoint is distinct from the `:streamQuery` adapter and A2A endpoint. Use the contract that the deployed application actually exposes. See the [official ADK runtime usage guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-an-adk-agent).

`deployed-cases.json` declares the prompts and expected control/tool outcomes. `deployment-results.json` records the returned events and sessions. A failed assertion or HTTP failure exits unsuccessfully; inspect the report and error. An outcome assertion is not a semantic quality metric. Review the corresponding rubric and the observed answer as well.

| Module | Additional deployed evidence beyond the checker |
|---|---|
| 23 | Reopen the session with a fresh client; load the exact source/report/manifest versions from GCS and compare their references. |
| 24 | Run the representative customer dataset against the hosted version; retain per-case scores and failures, plus the exact resource/code/model configuration. |
| 25 | Find the checked invocation in Cloud Logging and Cloud Trace, including the outage outcome. Verify capture settings. |
| 25.5 | Test an approved synthetic template match and a controlled inspection failure; inspect stored session history as well as the visible response. |
| 26 | Observe valid/invalid tool arguments and the before-model replacement; inspect state-only events and retained message parts. |

For Module 23, use the native `GcsArtifactService.load_artifact` with `app_name="bank_review"`, the exact checker user/session, filename and version. Do not reconstruct a raw GCS object path from assumptions about the provider's internal layout. The checker report must retain the test user alongside the session to support this readback.

Module 23 supplies the complete readback program and explains it in the lab:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --env-file .env python verify_pack.py deployment-results.json
```

It creates a fresh GCS client, loads the manifest version returned by the deployed tool, loads the exact source/report versions referenced by that manifest, and verifies the source digest. Its success is separate evidence from the hosted HTTP check.

## Run live quality evaluation

Every module includes native ADK cases and an explicit judge configuration:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv sync --locked --extra eval
uv run --env-file .env adk eval bank_review eval/cases.evalset.json \
  --config_file_path eval/eval_config.json --print_detailed_results
```

This invokes the local application with real model/judge calls; it is not an evaluation of the deployed resource. The evaluator supplies its own execution/session setup. Keep that result separate from deployed integration evidence. The judge model is specified in the config file; `GEMINI_MODEL` alone does not change it.

For hosted quality evaluation, use a supported deployed-agent evaluation interface, for example the Agents CLI `eval generate --url ... --app-name bank_review` flow with its own documented dataset schema, then grade the resulting traces. Do not pass native ADK EvalSet JSON to a differently shaped interface and assume compatibility. Alternatively, retain the deployed checker transcripts and have the bank's reviewers score the same explicit rubric; record these as human-reviewed deployed results. See the [Agents CLI evaluation documentation](https://github.com/google/agents-cli).

## Diagnose configuration failures in order

| Symptom | First check | Correct interpretation |
|---|---|---|
| Missing environment variable | Edited `.env` and correct `--env-file` location | Setup incomplete, not a model failure |
| 401/403 | Caller/runtime identity, resource permissions, enabled API | An access failure; do not grant broad owner roles to bypass it |
| Model not found | Model ID and actual deployed endpoint location | Availability/configuration issue |
| Session not found | App, user, session and managed resource scope | A different scope is not the same conversation |
| Missing artifact | Exact scope, filename and version | Never substitute latest without an explicit requirement |
| Inspection unavailable | Template region, permissions, timeout and result status | No clean inspection verdict was established |
| No cloud telemetry | Export configuration, runtime identity and destination | A local log line is not proof of export |

## Record the result and clean up deliberately

For each experiment record the code/dependency revision, resource and service regions, model and judge configuration, template policy when relevant, expected outcome, actual outcome and evidence location. Report unrun checks as unrun. Separate fixture-contract passes, live model quality, Google-service integration and hosted-runtime verification.

Delete disposable test sessions and deployments according to the development project's policy. Apply artifact/log retention through the approved infrastructure configuration. Do not delete a shared bucket, template or runtime merely because one lab has finished. Resource cleanup is a deliberate operation, not an unreviewed step hidden inside the checker.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

