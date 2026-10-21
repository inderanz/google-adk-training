---
sidebar_position: 5
title: "Banking FDE Learning Guide: Modules 13.5–26"
---

# From a bank's request to an ADK solution

Use this guide alongside Modules 13.5–26, including 21.5 and 25.5. The READMEs explain each concept; the labs build and exercise it; the solutions explain the implementation; the enterprise playbooks define the customer integration work. A passing local example establishes a learning checkpoint, not a deployed banking service.

An FDE is a forward deployed engineer: an engineer who works with the customer's business and technology teams to turn a problem into working software. In these lessons, that means asking where the facts come from, choosing a supported ADK capability, implementing the bank's rule, and collecting evidence that it works.

## Choose your starting point

Every module starts with a learning preview before the customer story. Read it to answer four questions: which ADK concept am I learning, what real task needs it, which Google platform or supporting service is involved, and what should I be able to do afterwards? ADK supplies the application framework; the preview identifies the managed services used by that particular lesson. A local framework exercise and a deployed-service exercise have different learning goals.

If you are new to Python, begin with the README's customer task, then read the lab's Python guide. You should be able to read a dictionary, call a function, follow an `if`, and explain what `return` supplies. The asynchronous lessons introduce `await` beside the operation using it. Run one checkpoint at a time; do not begin by copying the complete solution.

If you already build software, use the same customer contract but concentrate on ownership, failure and recovery. Replace one fixture with an authorized service adapter and preserve its contract. If you teach the course, ask learners to predict the outcome before executing the example, then explain one changed requirement without referring to the solution.

The completion standard is observable: **explain the rule, locate its implementation, predict a changed input, observe a failure, and adapt the pattern to a new request**. Reading every page or getting one successful answer is not the same standard. The [dated review and verification record](./review-notes.md) shows what has actually been checked.

## Read the bank's vocabulary before the technical vocabulary

A relationship manager works with the business customer. An analyst gathers and checks information for a review. A case is the bank's record of a particular review; a company is the business being reviewed. A company ID and a case ID therefore identify different things.

“Evidence” means the records used to support an answer. “Approved source” means a source the bank's responsible team has selected for that use; it does not mean an LLM has certified it. “Acceptance check” means an observation that shows whether a particular requirement was met.

The examples use everyday banking work that learners can picture, including a business banking team preparing for a company meeting. Technical terms are introduced with their ADK names and explained beside a concrete example. Keep money units exactly as defined in each code exercise; do not silently reinterpret its integer cents as rupees or lakhs.

Financial statements describe a business's financial position and performance. The ownership register identifies its owners; the exercise records receipt, not legal validity. For an Indian banking adaptation, a customer might say “₹1 lakh.” First write `currency="INR"` and define the unit: ₹100,000 is 10,000,000 paise. Only then design a currency-aware schema and obtain the bank's threshold. The supplied `requested_cents` fixture is not an INR policy or a regulatory limit.

## Start with the conversation the customer would actually have

> “Our analysts spend too much time preparing commercial-loan reviews. They open several systems, check which documents are missing, repeat explanations and ask another team for specialist input. Help them prepare a trustworthy case summary and the right next step. Keep the analyst responsible for the decision. Remember how each analyst likes information presented.”

This is a fictional customer brief for Sovereign Horizon Bank. It describes a realistic workflow, not a verified engagement or a bank policy. Our example borrower is Acme Robotics, case `CASE-001`, company `ACME-001`. The module openings follow Meera, a fictional analyst working on this review. Her name connects the teaching story; the runnable examples retain their explicitly defined synthetic user IDs.

The engineer first separates goals from unspecified details:

| Customer phrase | Clarifying question | Teaching assumption | Resulting technical requirement |
|---|---|---|---|
| “Preparing reviews takes too long” | Which activities dominate elapsed time? | Checklist collection and explanation are the learning scope | Measure collection and explanation separately |
| “Several systems” | Which system owns each fact? | Case checklist in Firestore; approved company profile in BigQuery | Keep provenance and versions; do not replace either with memory |
| “Right next step” | Who supplies the rules and exception precedence? | Missing documents first; then a fictional amount threshold | Deterministic, boundary-tested routing |
| “Specialist input” | A required check or optional advice? | Required facts are scheduled; advisory consultations are evaluated | Do not confuse model choice with mandatory execution |
| “Another team” | Separate release ownership, or only another function? | Remote ownership is introduced in Module 21 | Add A2A only when a service boundary is justified |
| “Trustworthy summary” | What evidence must it include? | Explicit source IDs and human review | Validate structure and evaluate factual support separately |
| “Remember how I like it” | Exact preference or inferred personal history? | Explicit concise/detailed setting | Durable user state; selective memory ingestion |

In customer work, record answers from the business and data owners. The teaching assumptions make the lab executable; they must not silently become customer requirements.

## Turn nouns, verbs and constraints into code

**Nouns become data contracts.** Case, amount, checklist, evidence and memo need defined fields. “Amount” needs a currency and representation; the fixture uses integer cents in one unspecified currency. “Evidence” needs an origin and observation/version information in a real system.

**Verbs become operations.** Read, collect, route, explain, revise and remember are different operations. Reading a checklist does not mark a document received. Returning `next_step="specialist_review"` does not create a queue item. Generating an explanation does not approve a loan.

**Dependencies become orchestration.** “After both checks” becomes a join. “If incomplete” becomes a branch. “Only when applicable” becomes conditional scheduling. “At most three drafts” becomes a bounded loop. “Ask another service” becomes a network contract.

**Constraints become executable checks.** Validate types at the boundary, authorize reads in trusted code, bound work, preserve evidence identifiers and distinguish failed/unknown outcomes from success. A prompt can express desired behavior; it cannot replace a service's authorization or transaction rules.

**Ambiguity becomes an explicit question or outcome.** Missing canonical case ID, unsupported intent and unavailable evidence must have defined behavior. Do not let a model fill absent bank facts merely because its response must match a schema.

## The practical development sequence

1. Write one normal request and its expected business result in plain English.
2. Add a missing-data request, a denied-access request and a dependency-failure request.
3. Name the owner of each input fact. Mark model-extracted claims separately from verified records.
4. Specify input/output fields and the failure result for each operation.
5. Implement exact validation and rules as small Python functions.
6. Choose the ADK control pattern from the dependency requirements.
7. Add Gemini only where understanding language, drafting or choosing advisory help is useful.
8. Run deterministic checks first; then evaluate real model behavior and service integrations.
9. Present the evidence and limitations to the customer before making a release decision.

This is why some labs run without Gemini: they isolate control logic that a model should not have to guess. Later stages connect those exact operations to reasoning and enterprise services.

## Follow one story, with explicit checkpoints

| Module | What the learner adds | Demonstration that earns the next step |
|---|---|---|
| [13.5](../module13_5-firestore-persistence/README.md) | Durable conversation and separate case records | Resume a conversation after restart and explain why a stale case update cannot overwrite a newer one |
| [14](../module14-third-party-tools/README.md) | Existing LangChain tools inside ADK | Trace a validated company ID through LangchainTool to the bounded lookup and back |
| [15](./README.md) | Specialist responsibilities | Explain why the coordinator calls an adviser and who answers afterwards |
| [16](../module16-static-orchestration/README.md) | Required independent evidence | Trace both returned dictionaries into the join |
| [17](../module17-structured-routing/README.md) | Ordered business rules | Predict all routes, including the exact threshold |
| [18](../module18-dynamic-orchestration/README.md) | Conditional work | Show which child did not execute and why |
| [19](../module19-collaborative-teams/README.md) | Advisory collaboration and dialogue ownership | Compare tool return, single-turn delegation and chat transfer |
| [20](../module20-cyclic-workflows/README.md) | Bounded memo correction | Explain accepted, invalid and exhausted outcomes |
| [21](../module21-distributed-graphs/README.md) | Remote service ownership | Trace discovery, request, response and failure across A2A |
| [21.5](../module21_5-mas-knowledge-milestone/README.md) | Architecture decision | Defend the simplest sufficient design and identify unimplemented integration |
| [22](../module22-state-and-memory/README.md) | Personalized continuity | Prove state persistence and memory scope without treating recollection as evidence |

The examples are separate checkpoints, not an already-integrated deployment. This lets a beginner inspect one new concept at a time and an experienced learner replace a boundary without rewriting every earlier exercise.

## Choose Google capabilities by responsibility

The course uses the code-first ADK path in Gemini Enterprise Agent Platform. ADK is the development framework; running an ADK object locally does not deploy a managed service. Agent Runtime, Sessions and Memory Bank provide different managed responsibilities. See the [official Agent Platform agents overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/agents).

| Requirement | Native capability / supporting Google service | Where the course exercises it | What is still needed for a customer |
|---|---|---|---|
| Agent reasoning and tools | ADK with Gemini through the enterprise backend | Live paths in 15, 19, 20 and 22 | Model access, region, quotas and measured quality |
| Execution order and branching | ADK Workflow, nodes, routes and joins | Local runs in 16–18, 20 and 21.5 | Real source adapters and failure budgets |
| Managed hosting | Agent Runtime | Shared cloud guide in Module 23 and Module 26 capstone | Staging deployment, identity, scaling and recovery checks |
| Conversation persistence | Managed Sessions via ADK `VertexAiSessionService` | Optional provider in Module 13.5 | Existing resource, supported region and caller scope |
| Long-term retrieval | Memory Bank via ADK `VertexAiMemoryBankService` | Optional provider in 22 | Enabled resource, minimal ingestion, recall/correction/deletion checks |
| Current case checklist | Firestore using the official Google client | Module 13.5's case repository | Approved case schema and authorization mapping |
| Reviewed company background | Existing LangChain tool adapted with ADK LangchainTool; BigQuery stores the profile | Module 14's profile adapter | Curated data, canonical IDs, provenance and permissions |
| Independently operated specialist | A2A with ADK's adapter; appropriate Google hosting | Loopback integration in 21 | Authenticated endpoint, task/session persistence and protocol testing |
| Content inspection | Model Armor through an ADK App plugin | Module 25.5 and Module 26 capstone | Configure the template, test unavailable/match outcomes and inspect persistence boundaries |
| Tracing, logs and evaluation | Google Cloud observability and native ADK evaluation | Modules 24–25 and their supplied cases | Capture policy, dashboards and recorded live results |

Firestore, BigQuery and Cloud Run are supporting Google Cloud services; they are not interchangeable names for Agent Platform components. Google-native architecture means using the appropriate supported capability, not inserting every available product into every lab.

## Follow Python from the command to the first event

When you run `uv run python run.py`, Python first imports the named modules and defines their functions/classes. It then reaches the CLI block in `run.py`. Constructing the agent graph and executing the graph are separate stages.

| Expression you will see | Plain-English meaning | What to check in this course |
|---|---|---|
| `if __name__ == "__main__":` | Run this block when this file is the program entry point | Importing the file from a test should not start the CLI |
| `parser.parse_args()` | Read the command-line arguments according to the declared options | A default fixture and an explicit learner input are distinguishable |
| `build_agent(...)` | Construct the configured object that will do the work | It returns an Agent or Workflow, not an answer |
| `asyncio.run(...)` | Start the event loop for this CLI's asynchronous work | Use it at the synchronous program boundary, not inside an already-running async function |
| `App(name=..., root_agent=...)` | Describe the application and its entry agent/workflow | An App object is not a managed deployment |
| `InMemoryRunner(app=...)` | Create ADK's local execution service with development storage | Its sessions are lost on process exit |
| `await create_session(...)` | Ask the provider to create a conversation context | App and user scopes must match later calls |
| `types.Part.from_text(...)` | Put one text value into a typed message part | A part belongs to a Content message; it is not an event by itself |
| `types.Content(role="user", parts=[...])` | Package the incoming user message | This message starts the invocation |
| `async for event in runner.run_async(...)` | Receive ADK events as execution progresses | One request can produce many tool, node and response events |
| `events.append(event)` | Retain the event in this local result list | It is separate from the SessionService's persistence behavior |
| `event.output is not None` | Check whether the event has a graph output value | Empty dictionaries and false booleans can still be valid outputs |
| `event.content.parts` | Inspect text or other message parts associated with the event | Not every event contains text, and not every text event is the final answer |
| `async with ...` / `finally` | Release resources when work finishes or fails | Runner and database lifecycles remain explicit |

The common `runtime.py` currently JSON-serializes its supplied payload. A case dictionary becomes JSON text that the Workflow input schema parses. A string prompt is JSON-encoded as a string; that adds JSON quoting but does not turn the phrase into a trusted business record. The important distinction is the contract at the receiving boundary, not whether text looks like JSON.

For exact rules, inspect Python values. For graph composition, inspect `Event.output` and route selection. For agent collaboration, inspect capability calls and responding agent. For persistence, create a fresh session/provider and read back the value. Each concept needs a different observation; “I saw a nice answer” cannot establish all four.

## A concrete integration boundary after Module 21.5

The following is an implementation specification for the integrated customer exercise, not a claim that the standalone examples already execute it:

| Step | Existing course component | Integration responsibility |
|---|---|---|
| Authenticate analyst | Deployment/API boundary | Derive analyst and tenant identifiers from verified credentials; never from the model |
| Read accessible case | Module 13.5 `bank_review.repository.read_case(case_id, user_id)` | Handle non-`ok` status before using document fields; preserve case version |
| Derive checklist status | Validated `documents` mapping | Require the expected document keys; both must be true for completeness |
| Obtain amount and company mapping | Bank-owned case/ledger adapter | Supply currency, amount, `company_id` and their version/source; these fields are **not** returned by the existing Module 13.5 repository |
| Fetch approved profile | Module 14 `get_company_profile(company_id)` | Use the canonical mapping; handle stale/missing/unavailable results, preserving source/date |
| Assemble review snapshot | Your narrow adapter | Construct the graph contract from authorized records, not directly from analyst text |
| Collect and route | Modules 16–18 / 21.5 | Apply the bank's approved, versioned rules |
| Explain or draft | Modules 19–20 | Provide bounded evidence and evaluate its use |
| Persist interaction/preferences | Native ADK service providers | Keep conversation state separate from case/ledger truth |

Do not infer `company_id` by rewriting `CASE-001` into `ACME-001`. That association belongs in an authoritative mapping. Do not calculate `all(documents.values())` on an unvalidated empty mapping: Python returns true for an empty iterable. Validate the required document set first.

Module 14's example profile function is synchronous. If an asynchronous graph calls it directly, it can block that event-loop thread. Preserve its bounded query and error behavior when choosing an asynchronous adapter or a carefully bounded thread offload; simply writing `async def` around the same blocking call does not solve the issue.

## Learn at the right depth

**Foundation learner:** complete the worked trace with pencil and paper, run the supplied scenario, explain one function without reading its comments, then change one input and predict the result. Look up each unfamiliar Python construct in the lab's explanation before moving on.

**Experienced learner:** challenge the assumption behind the pattern. Add a competing architecture, a version mismatch, a partial failure or a stale fact. Preserve the business contract while replacing one fixture with an authorized adapter. Measure the effect on reliability, latency and cost rather than using agent count as a quality metric.

**Instructor:** ask for a prediction before every run. When output surprises learners, inspect the input, event and returned data together. A correct answer copied from the solution earns less evidence of understanding than a clear explanation of why a failure path occurred.

## What a customer handover contains

Deliver the agreed requirement table, ownership diagram, versioned contracts, authorization design, runnable source, dependency lock, deterministic checks, model evaluation results, integration evidence and an operations runbook. Explain which operations are read-only, which can change a business record and what an unknown outcome means.

Completion of these modules should enable a learner to build and explain the orchestration and context patterns. Production deployment proficiency additionally requires the later evaluation, observability, safety and deployment modules plus hands-on validation in the customer's environment. No document or mock test alone establishes that every learner is ready to release a banking application.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. -->

## Continue from orchestration to a measured pilot

| Module | New responsibility | Explain before advancing |
|---|---|---|
| 23 | Preserve versioned review evidence | Trace ToolContext through the configured artifact provider |
| 24 | Evaluate outcomes and tool selection | Build one native case and interpret one actual metric result |
| 25 | Investigate execution | Correlate an invocation, tool span and bounded business outcome |
| 25.5 | Apply content-inspection policy | Distinguish inspection, replacement and persistence |
| 26 | Intercept lifecycle operations | Prove which hooks and bodies execute after replacement |

Read the [callback and plugin primer](../module25-observability/lifecycle-primer.md) before implementing Module 25's plugin. Module 26 expands that foundation with execution-control experiments.

After the isolated lessons, complete the [integrated banking lab](../module26-callbacks/integrated-lab.md). It joins the authorized Firestore checklist, deterministic next-step selection, exact artifact versions, Gemini explanation, Model Armor and operational metadata in one native ADK App. It deliberately excludes an unimplemented ledger source. The lab distinguishes software verification from the required live deployed evidence.

## Explain code by deriving it

A useful comment connects a requirement to a decision: `# Missing documents take precedence over amount.` A comment saying `# Check the if statement` merely repeats syntax. For unfamiliar syntax, explain it in the surrounding lesson and show one concrete value.

Before writing a function, write four lines: input owner; operation; output consumer; failure outcome. Then write the Python signature, implement the smallest rule, and connect the native ADK boundary. Trace values through the function before explaining its implementation to someone else.

For every new concept, complete this sentence: “ADK creates or receives ___, calls ___ when ___, and uses the returned ___ to ___.” If you cannot fill it in, revisit the execution model before adding another abstraction.
