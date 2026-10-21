---
sidebar_position: 2
title: "Lab 13.5: From a Bank Request to Durable State"
---

# Lab 13.5: Build a Review Assistant That Can Resume Tomorrow

**What you are practising:** Durable sessions and separate business records in ADK (Agent Development Kit). Before coding, read the [module learning preview](./README.md#before-you-begin-what-this-module-teaches) for the real-world use case, Google platform connection and expected outcomes.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## 1. Write the problem before writing Python

### Read this as a bank employee's task

A bank analyst is checking which documents have arrived for a business loan application. The review may take several days. The analyst needs to close the application today and continue tomorrow without losing the conversation or the checklist.

In this course, an analyst is the employee who gathers and checks information for a review. Picture a business banking team preparing for a company meeting. The bank, company and records are fictional.

> Let me reopen the same conversation tomorrow. Show the current checklist for my assigned case, and let me record that a document has arrived. If someone else changed the record, tell me before replacing their update.

| What you need to understand first | This exercise's answer |
|---|---|
| What information starts the task? | A case ID and, when recording receipt, the document name and the version last read. |
| What should the employee receive? | The current checklist, or confirmation that the requested receipt was recorded. Starting a new conversation must not erase the business checklist. |
| What should happen when it cannot be completed? | An unassigned user gets no case details. An outdated update returns a conflict so the analyst can read the new version first. |

### New words, explained using this task

| Term | Meaning here |
|---|---|
| Persistence | Saving information so it remains after the application stops. |
| Session | One conversation, identified separately from the bank case. |
| Transaction | A database operation that checks and commits related changes together. |
| Version | A number used to detect whether the record changed since it was read. |

The next technical table connects these requirements to ADK objects and checks. Read one row at a time: the employee's need comes first, then the coding choice, then the result that would show it works.


Write a five-line specification:

1. **User:** an authenticated analyst assigned to a case.
2. **Read:** the latest checklist for that case.
3. **Write:** mark one supported document as received.
4. **Remember:** conversation events and a `last_case_id` hint.
5. **Never:** accept caller identity from the model, infer loan approval, or overwrite a stale record.

The exercise supports `financial_statements` and `ownership_register`. It records receipt only; it does not inspect uploaded files. The supplied CLI uses the fictional identity `analyst-demo`. A production application's login and identity binding must replace that teaching shortcut.

**Checkpoint:** Why are “the conversation remembers CASE-001” and “CASE-001's current checklist is correct” different acceptance criteria?

## 2. Convert the specification into a development plan

Use the same approach for a new customer's request.

| English phrase | Coding concept | File |
|---|---|---|
| “Continue tomorrow” | A persistent ADK session service | `bank_review/sessions.py` |
| “Same conversation” | Retrieve the returned session ID with the same application/user | `run_agent.py` |
| “Current checklist” | Read a Firestore document | `bank_review/repository.py` |
| “Assigned analyst” | Compare stored assignment to trusted context identity | `summarize_case` |
| “Record receipt” | A narrow ADK function tool | `bank_review/tools.py` |
| “No lost updates” | Version comparison inside a transaction | `mark_in_transaction` |
| “Explain the result” | Model instructions and structured tool statuses | `bank_review/agent.py` |

Read the [overview's architecture and contract](./README.md) first. Attempt each exercise before comparing with the [annotated solution](./lab-solution.md). The executable reference remains available so you can isolate one concept at a time.

## 3. Set up a practice copy

Copy the entire sibling `example/` directory into a separate practice workspace. Run all following commands from that copied directory.

```text
example/
├── pyproject.toml             # Direct dependencies and optional managed extra
├── uv.lock                    # Reproducible resolution
├── .env.example               # Configuration template
├── session_probe.py           # No-model restart experiment
├── seed_case.py               # Create one fictional Firestore document
├── run_agent.py               # One agent turn per process
├── bank_review/
│   ├── __init__.py
│   ├── sessions.py            # Built-in service selection
│   ├── repository.py          # Firestore operations
│   ├── tools.py               # ADK business tools
│   └── agent.py               # Model instructions and tool registration
└── tests/
    └── test_persistence.py
```

Use Python 3.12+ and `uv`:

```bash
uv sync --locked
uv run --locked python --version
uv run --locked python -m unittest discover -s tests -v
```

`uv sync` creates this project's virtual environment. `--locked` prevents an unnoticed change to the dependency resolution. The dependency list includes `google-adk[db]`, the official Firestore client, and `sqlalchemy[asyncio]`. The last extra supplies `greenlet`, required by the SQLAlchemy async integration in the tested environment.

The 26 offline tests need no Gemini credentials or Firestore server. They use real ADK and SQLite, with mocked Firestore calls. Passing them does not prove cloud permissions or distributed transaction behavior.

## 4. Learn the minimum Python vocabulary

| Syntax | Read it in plain English |
|---|---|
| `def name(...):` | Define a function to call later |
| `async def name(...):` | Define a coroutine that may wait for I/O |
| `await operation()` | Wait for that asynchronous operation to finish |
| `asyncio.run(main())` | Start an event loop for this command-line program |
| `{"status": "ok"}` | A dictionary with a key and value |
| `data.get("version")` | Read a key, returning `None` if absent |
| `data["version"]` | Read a required key; absence raises `KeyError` |
| `value: str` | A type hint; it does not enforce the runtime type |
| `dict[str, object]` | A dictionary whose values can have different Python types |
| `return` | Finish the function now |
| `try / except / finally` | Run work, handle named failures, and clean up |
| `from .tools import ...` | Import from another module in the same package |
| `@cache` | Decorate a function so repeated identical calls reuse its result |

`await` does not automatically make writes durable or atomic. It only waits for the called operation. Durability comes from the storage service; atomicity comes from the transaction boundary.

## 5. Prove persistence before introducing a model

Open `bank_review/sessions.py`. Its local branch uses the built-in service:

```python
from google.adk.sessions import DatabaseSessionService

service = DatabaseSessionService(
    db_url="sqlite+aiosqlite:///./review_sessions.db"
)
```

Read the URL in parts: `sqlite` is the database; `aiosqlite` is the async driver; `./review_sessions.db` is a file in the current working directory. The constructor creates the service object; operations initialize/use its storage.

Now run:

```bash
uv run --locked python session_probe.py write
```

Copy the returned `session_id`, then run a **new command**:

```bash
uv run --locked python session_probe.py read --session-id YOUR_RETURNED_SESSION_ID
```

Use the actual returned ID, not the placeholder. Both commands must run from the same directory against the same configured database. You should recover:

- `last_case_id` equal to `CASE-001`;
- `review_step` equal to `paused`;
- two events with different `id` values and the same `invocation_id`.

These are two separate operating-system processes. The second cannot retrieve the first process's RAM. This proves persistence to the SQLite file, not resilience of a deployed cloud application.

### Break down creation and retrieval

The create operation follows this shape:

```python
async def start_review(service):
    session = await service.create_session(
        app_name="bank_review",
        user_id="analyst-demo",
        state={"last_case_id": "CASE-001"},
    )
    return session.id
```

- `service` is a dependency passed into the function.
- `create_session` is ADK's API, so you do not write your own session schema.
- `app_name` identifies the application and `user_id` identifies its user.
- `state` supplies initial session values.
- `await` waits for creation to complete.
- `session.id` is the returned identifier to keep for resumption.

Retrieval requires that identity tuple again:

```python
async def resume_review(service, session_id):
    return await service.get_session(
        app_name="bank_review",
        user_id="analyst-demo",
        session_id=session_id,
    )
```

**Exercise S1:** In a practice copy of `build_session_service`, implement the SQLite branch from these concepts. Make an unknown backend raise `ValueError`; never quietly switch to in-memory storage.

**Checkpoint:** Why would changing the current directory make the default relative SQLite URL appear to “lose” a session? Why would a SQLite file inside a disposable Cloud Run container be insufficient?

## 6. Understand the event that saves a state change

Open `session_probe.py`. The program creates an event for each checkpoint using:

```python
from google.adk.events import Event, EventActions

def checkpoint_event(invocation_id, step):
    return Event(
        author="checkpoint_demo",
        invocation_id=invocation_id,
        actions=EventActions(state_delta={"review_step": step}),
    )
```

`Event` represents one history item. `EventActions` carries associated actions, including changed state. `state_delta` contains the updated keys, not a replacement of every stored value.

The probe calls `await service.append_event(session=session, event=event)`. In a normal agent turn, the **Runner** handles event persistence; tools should update `ToolContext.state` rather than manually append a duplicate event.

`author` here names a demo component. It is not proof of an authenticated human. Neither event IDs nor timestamps are cryptographic signatures.

**Exercise S2:** Before inspecting the output, predict how many events survive when two events share an invocation ID. Run the supplied test and explain why storing both under that ID in a custom database would be a bug.

**Exercise S3:** Locate the test that edits `session.state` directly and reloads it. Explain why an arbitrary edit to a retrieved dictionary does not call the persistence API.

## 7. Design the Firestore document from the business nouns

One case is one document at `review_cases/CASE-001`:

```json
{
  "assigned_analyst_id": "analyst-demo",
  "borrower_name": "Acme Robotics (fictional training company)",
  "documents": {
    "financial_statements": false,
    "ownership_register": false
  },
  "version": 1
}
```

The seed script also sets `updated_at` using Firestore's server timestamp.

- `review_cases` is the fixed collection.
- `CASE-001` is the document identifier.
- `documents` is a nested map, not a subcollection.
- `version` is the application's integer revision, initially 1.
- `assigned_analyst_id` is written by the trusted case-setup process.

No session ID appears in this path. A case can outlive a conversation. Different authorized applications can use the same business record without sharing one ADK conversation.

### Understand the read

Open `read_case` in `repository.py`:

```python
async def read_snapshot(client, case_id):
    reference = client.collection("review_cases").document(case_id)
    snapshot = await reference.get(timeout=10, retry=None)
    return snapshot.to_dict()
```

This teaching fragment leaves authorization to its caller; the actual implementation immediately calls `summarize_case`.

A document reference is an address. Constructing it does not fetch data. `get` makes the service call; a snapshot represents the returned document at read time. `to_dict` produces ordinary Python data, or `None` when the document does not exist.

The application uses the official `firestore.AsyncClient`; the synchronous SDK inside `async def` would still block while performing its synchronous work.

**Exercise F1:** Implement `summarize_case`. First reject missing or differently assigned cases using the same `not_found` response. Then validate the name, positive integer version, and actual Boolean checklist fields. Return only the approved fields.

**Checkpoint:** Why does Python's `isinstance(True, int)` return true? The reference uses `type(version) is int` to reject Boolean versions.

## 8. Translate “do not overwrite another update” into a transaction

Imagine the analyst read version 1. Another authorized process changed the record to version 2 before the analyst's update arrived. The update must not silently apply an assumption based on version 1.

Implement this decision order in `mark_in_transaction`:

```text
Read the current document inside the transaction.
Check assignment and document shape.
If this flag is already true, return already_received without writing.
If the version differs, return conflict without writing.
Otherwise queue the flag, next version, and timestamp together.
Return the new public record; the SDK wrapper commits before the caller gets it.
```

The check for an already-true flag intentionally precedes the version comparison. A repeated receipt request can return the current record without writing, even if it supplies the old version.

Google's transaction wrapper is used this way:

```python
from google.cloud import firestore

async def execute_receipt(client, reference, case_id, user_id, document_name, version):
    from bank_review.repository import mark_in_transaction

    commit_receipt = firestore.async_transactional(mark_in_transaction)
    return await commit_receipt(
        client.transaction(max_attempts=3),
        reference,
        case_id,
        user_id,
        document_name,
        version,
    )
```

- `mark_in_transaction` is passed as a function object, without calling it.
- `async_transactional` supplies Google's transaction/retry mechanism.
- `client.transaction(max_attempts=3)` constructs the transaction context.
- `transaction.update(...)` queues a write; it is **not awaited**.
- The wrapper commits queued writes and can rerun the body on eligible conflicts.
- Do not send email, call Gemini, or change `ToolContext.state` inside the transaction body: retries could repeat those side effects.

**Exercise F2:** Implement the body, then run the conflict, duplicate, and unauthorized-update tests. Explain which tests mock Firestore and which cloud guarantees still need an emulator or staging project.

**Checkpoint:** If the network times out after a commit, can you safely tell the analyst “nothing changed”? Explain the re-read recovery path. This operation is a no-op on repeated receipt flags; it is not a general exactly-once payment design.

## 9. Put the business functions behind ADK tools

In `get_review_case`, the model provides a case ID. ADK supplies `ToolContext`:

```python
from google.adk.tools import ToolContext

def remember_case_hint(case_id: str, tool_context: ToolContext) -> None:
    tool_context.state["last_case_id"] = case_id
```

This miniature fragment explains the assignment only. The actual tool validates and authorizes a read **before** setting the hint.

`tool_context.user_id` comes from the application's invocation context. It is not a tool argument chosen by Gemini. That still requires a trusted application: accepting arbitrary `user_id` values from an unauthenticated HTTP request would defeat this design.

**Exercise T1:** Reimplement `get_review_case` with validation, a call to `repository.read_case`, safe errors, and the state hint after success.

**Exercise T2:** Reimplement `mark_document_received`. Allow only the two document names and a positive integer version. Forward the context's user ID. Update the hint after `ok` or `already_received`, never after a conflict or denial.

**Checkpoint:** Why must the tool return `not_found` for both an absent case and an inaccessible case? Why does the state contain an ID instead of a second authoritative checklist?

## 10. Register the tools and run one turn at a time

Read `agent.py` and `run_agent.py`. The agent defines reasoning instructions and capabilities. The Runner receives the session service:

```python
from google.adk import Runner

def make_runner(agent, service):
    return Runner(
        agent=agent,
        app_name="bank_review",
        session_service=service,
    )
```

Passing the service into the Runner is dependency injection: choose a supported implementation without rewriting the agent's business tools.

The CLI:

1. Builds the selected service.
2. Creates a session or retrieves the supplied ID.
3. Refuses to silently replace a missing requested session.
4. Builds a `types.Content` user message.
5. Iterates `runner.run_async(...)` until the turn completes.
6. Prints final text and closes local database resources.

Creating a `root_agent` alone does not configure the session service used by a separate server. Use the supplied CLI for this lab; launching an unrelated default `adk web` server does not automatically reuse `build_session_service`.

## 11. Connect Firestore using a development environment

Choose one path. Both use synthetic data. These steps were not executed against a live cloud database during the review.

### Option A: Firestore emulator

Install the supported Google Cloud CLI and Java runtime required by the [official emulator instructions](https://docs.cloud.google.com/firestore/native/docs/emulator). Start the emulator in one terminal:

```bash
gcloud emulators firestore start --host-port=127.0.0.1:8080
```

In the practice terminal:

```bash
export GOOGLE_CLOUD_PROJECT=demo-bank-persistence
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
uv run --locked python seed_case.py
```

Keep the emulator running while restarting the Python application. Its default storage is in memory: restarting the emulator loses the fixture. It does not emulate production IAM or establish production durability.

### Option B: Google Cloud Firestore

Use an approved development project and Firestore Native mode database. Configure ADC with `gcloud auth application-default login`. Have the platform owner enable services and grant appropriately scoped permissions.

Create `.env` from `.env.example` in the practice copy, replacing placeholders. Preserve existing configuration. Remove `FIRESTORE_EMULATOR_HOST` from the process and file when using the real database; otherwise the SDK still targets the emulator.

```bash
uv run --locked --env-file .env python seed_case.py
```

This writes one fictional document and can incur cloud charges. `create` refuses to overwrite an existing document; a repeated seed produces an already-exists error. Do not “fix” that by replacing it with a destructive overwrite.

The Python server SDK uses IAM and bypasses Firestore Security Rules. Collection paths do not create authorization by themselves. Read the [playbook's identity design](./enterprise-playbook.md).

## 12. Demonstrate a real conversation restart

A Gemini conversation additionally needs an approved model, endpoint, and credentials even if Firestore uses the emulator. Populate `GEMINI_MODEL`, `GOOGLE_GENAI_USE_ENTERPRISE`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION` for the approved cloud project. For mixed cloud-model/emulator testing, the emulator is addressed by its host variable; seed its fixture under the same project ID your tool will use.

```bash
uv run --locked --env-file .env python run_agent.py "Read CASE-001 and tell me which documents are outstanding."
```

Copy the printed session ID. The process exits after its turn.

```bash
uv run --locked --env-file .env python run_agent.py "The financial statements arrived. Record their receipt for CASE-001." --session-id YOUR_RETURNED_SESSION_ID
```

Run another new process with that ID and ask for the current checklist. Then omit `--session-id` to start a new conversation and ask for `CASE-001` again. The conversation is new; the Firestore case persists independently.

Inspect actual tool calls and Firestore values. Expected behavior is not a recorded evaluation result.

## 13. Switch the session backend to Google's managed service

The reference has a second provider branch using `VertexAiSessionService`. It selects an existing authorized Agent Runtime resource; it does not provision that resource.

```bash
uv sync --locked --extra managed
```

Set in the practice configuration:

```text
SESSION_BACKEND=managed
GOOGLE_CLOUD_AGENT_ENGINE_LOCATION=YOUR_SESSION_RESOURCE_LOCATION
GOOGLE_CLOUD_AGENT_ENGINE_ID=YOUR_AGENT_RUNTIME_RESOURCE_ID
```

Keep the model location and session-resource location separate. Use the resource's ID for the configured project/location. Follow [Agent Platform Sessions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions) for project setup and access.

Run the no-model probe first:

```bash
uv run --locked --extra managed --env-file .env python session_probe.py write
uv run --locked --extra managed --env-file .env python session_probe.py read --session-id YOUR_RETURNED_SESSION_ID
```

Then run the agent CLI with the same `--extra managed --env-file .env` options. IDs from the SQLite store do not automatically exist in the managed service; start a new managed session and retain its returned ID.

The built-in provider implements the session contract. Do not add a custom Firestore event store simply to make this backend selection work.

## 14. Evaluate behavior and failure recovery

Record results rather than copying an expected-output transcript. For each scenario retain the input, tool activity, stored before/after values, final answer, and pass/fail decision.

| Scenario | Expected evidence |
|---|---|
| Reopen the same conversation in a new process | Same identity/session ID and retained events |
| New conversation, same accessible case | Current Firestore checklist despite new session history |
| Unknown or unassigned case | No borrower details returned |
| Only borrower name supplied | Ask for case ID; no guessed entity mapping |
| Stale version | `conflict`; no stale write |
| Repeat an already-received flag | No extra version increment |
| Storage unavailable | No invented success; re-read after recovery |
| Another process updates the case | Agent reports refreshed data, not old conversation facts |
| Stored borrower name contains an instruction | Treat it as data; no extra capability or identity change |
| User requests loan approval | Explain the limited capability; no approval claim |

The offline tests establish code contracts. Firestore emulator/staging checks establish observed storage behavior. Live Gemini evaluations establish observed agent behavior. They answer different questions.

For a production model evaluation, use ADK's evaluation tooling with controlled fixtures and model/judge versions. Reset only disposable test cases between mutation scenarios. Do not benchmark Memory Bank extraction against a document read and declare one a replacement for the other.

## 15. Finish with a customer handover

Submit:

- A requirement-to-design table with your assumptions.
- An explanation of every function and the storage it touches.
- Actual restart and conflict-test evidence, labeled by environment.
- A plan for trusted authentication, per-case authorization, retention, recovery, and deployment.
- A list of what remains untested.

**Transfer exercise:** a customer wants several analysts to collaborate on a fraud case and then freeze an account. Identify the changed authorization model, version policy, and approval boundary. The receipt tool's no-op retry behavior is not sufficient for the account-freeze action.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module13_5-firestore-persistence-lab -->
