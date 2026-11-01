---
title: "Course-wide teaching review: three learner perspectives"
sidebar_position: 0.3
---

# Teaching review and verification scope

**Review date: 4 October 2026. Scope: all 48 numbered module READMEs, including intermediate modules, with lab navigation and targeted corrections to conflicting lab explanations.** This pass focuses on concept clarity, customer application, diagrams and continuity. It is not a fresh execution audit of every lab or a certification of a banking deployment.

The [learning journey](./learning-journey.md) provides the course story and pattern-selection guide. The [earlier Modules 13.5–26 verification record](./module15-intro-to-multi-agent-systems/review-notes.md) separately records executable contract tests and their limits. Its dated results must not be interpreted as new tests of Modules 1–40.

## Findings from the three perspectives

| Perspective | Teaching weakness | Change and reason |
|---|---|---|
| New Python/ADK learner | Framework names appeared before a concrete task; several different objects were casually called an agent. | Every opening identifies the concept, real work, platform responsibility and observable outcomes. The core sequence adds branch-desk explanations, values and Python-to-ADK mappings. |
| New Python/ADK learner | Diagrams mixed infrastructure, model internals and application behavior, or shrank long sequences into unreadable rows. | Use short vertical diagrams, explicit branch conditions and captions identifying execution versus target architecture. Remove invented model internals and misleading ledger/approval implications. |
| Experienced engineer | Model-selected calls, mandatory scheduling and delegation were described too similarly. | Distinguish call-and-return, static dependencies, route signals, dynamic child scheduling, mode-dependent delegation and bounded revision. Explain where each guarantee is enforced. |
| Experienced engineer | Some claims implied automatic truth, isolation, persistence or recovery. | Separate schemas from factual support; scope from durability; runtime identity from authentication; retry from duplicate-safe business execution. |
| Bank FDE | The next product or agent could appear to be the goal. | Start from the employee's task, data owner and failure outcome. Link the chapters as added requirements and ask for concrete acceptance evidence. |
| Bank FDE | Hosting, enterprise registration and compliance were conflated. | Separate build, evaluate, deploy, authenticate, authorize, register and operate. A platform certification does not certify an application's behavior. |

## Material technical corrections

- ADK graphs are a supported composition choice, not mandatory around every Agent. Multiple function nodes do not automatically form a multi-agent system.
- `root_agent` is a loader convention; a programmatic `App(root_agent=...)` can receive a differently named Python variable.
- Model IDs remain a valid configuration choice. Subclassing Gemini is not a required production standard, and `cached_property` is not a global singleton or connection-pooling guarantee.
- Structured output provides a shape contract; it does not establish factual truth or guarantee that every provider response succeeds.
- Runtime user IDs depend on trusted upstream authentication and must not substitute for backend record authorization.
- Expected missing data, technical failure, model repair and framework interruption require different treatment; neither “catch everything” nor “retry everything” is a universal rule.
- MCP standardizes capability access. Ordinary function tools can already be stateful; protocol sessions are not durable business records or authenticated identities.
- UI adapters are optional choices. A persisted browser session reference still needs server-side access checks.
- Cloud Run memory may survive some requests but is not guaranteed durable. Kubernetes Services are not automatically public.
- Agent Runtime hosting and registration in the Gemini Enterprise employee application are distinct steps.
- Local/remote delegation contracts differ. A handoff is not universally a permanent one-way transfer.
- Historical ADK 2.8.0 remote-context observations are labeled historical, not newly verified behavior of ADK 2.11.0.
- Simulated Model Armor, retrieval, storage and telemetry in later capstones are integration tasks, not interchangeable implementations of the managed services.

## Verification for this documentation pass

The following checks are recorded for the final edited material:

| Check | Scope and meaning |
|---|---|
| Learning coverage and local file links | 48 READMEs have an initial concept/use-case/platform/outcome preview, a concept diagram and course-story navigation. |
| Source/document consistency | The existing banking checker covers 16 modules, 69 documents, 129 Python files and 122 complete source listings; the pinned ADK baseline remains 2.11.0. |
| New complete Python examples | The Module 4.5 Gemini configuration and Module 38 retry-node factory construct successfully with the pinned installed ADK. No model request or bank service is invoked by that check. |
| MDX and portal build | The protected portal build passes with 186 pages and 48 modules. Compilation checks the site's document integration; it does not evaluate agent answers or exercise cloud IAM. |
| Diagram rendering | All 69 README Mermaid diagrams and the course-journey diagram are parsed and rendered at 390- and 900-pixel widths. Syntax/layout verification is supplemented by inspection of the compact diagrams. |

ADK's public package listing still identifies [2.11.0](https://pypi.org/project/google-adk/2.11.0/) as the latest release checked on this review date. Existing locked examples retain their verified dependencies. A conceptual update to a chapter does not silently upgrade or recertify its separate lab.

## Remaining customer and lab evidence

This pass does not claim live Gemini quality results, new cloud deployments, a complete security audit or production traffic/load testing. Those claims require the configured project, identities, source services, evaluation dataset and operating requirements.

The Module 34 file-backed cart remains an explicitly limited transport/persistence-failure experiment. It is not a durable, authorized multi-instance bank service. The lab now names the required identity, business-store, concurrency and protocol-session work. The later distributed capstones also require real integration and version-specific continuity tests before customer use.

For a release, demonstrate at least: an authorized normal request, denied user/resource access, missing/stale evidence, dependency failure, repeated or uncertain operations, required persistence across restart, complete evaluation results and observable operational recovery. Select the scenarios from the customer's actual risk and task rather than claiming a universal checklist certifies the system.

## Primary references used

- [ADK graph routes](https://adk.dev/graphs/routes/), [data handling](https://adk.dev/graphs/data-handling/) and [dynamic workflows](https://adk.dev/graphs/dynamic/), checked alongside the installed ADK source and course examples.
- [ADK collaboration](https://adk.dev/workflows/collaboration/) and [MCP tools](https://adk.dev/tools-custom/mcp-tools/).
- [MCP transport specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).
- [Agent Platform overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents), [Agent Runtime deployment](https://adk.dev/deploy/agent-runtime/) and [ADK agent registration in Gemini Enterprise](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent).
- [Cloud Run authentication](https://docs.cloud.google.com/run/docs/authenticating/overview) and [Google Cloud compliance resources](https://cloud.google.com/security/compliance).
- [Python cached_property behavior](https://docs.python.org/3/library/functools.html#functools.cached_property).
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

