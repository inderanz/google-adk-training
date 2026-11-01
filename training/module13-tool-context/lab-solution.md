---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 13 Solution: Understanding ToolContext Through a Drawdown Tool

## Goal and version baseline

Build a **simulated** commercial credit drawdown tool for Sovereign Horizon Bank. By the end, you should be able to explain where a tool gets its arguments, how ADK supplies runtime context, when confirmation happens, how state changes are recorded, and how a tool requests an agent handoff.

**Reviewed on 2 October 2026:** the latest stable release is [Google ADK 2.10.0](https://pypi.org/project/google-adk/2.10.0/). The examples below use its public Python APIs and modern Python syntax compatible with the training project's Python 3.12+ requirement. The repository currently locks ADK 2.9.2; an installed version and the latest published version are different things. Check your environment with:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --no-sync python -c "import sys; from importlib.metadata import version; print(sys.version); print('google-adk', version('google-adk'))"
```

This is a teaching simulation: it changes session data and produces a demo receipt. It does not send money, authenticate bank officers, verify covenants, or implement a bank ledger.

| Learning objective | What you will be able to explain |
|---|---|
| Runtime identity | Why `tool_context.user_id` is separate from model-supplied arguments |
| Conditional HITL | How a predicate decides whether `FunctionTool` requests confirmation |
| Session state | Why reading a value and assigning a changed value are different operations |
| Agent handoff | How `transfer_to_agent` selects a registered supervisor |
| Tool output | What `skip_summarization` controls and what a client must render |

## What needed correction in the earlier example

- **Deprecated typing alias:** `typing.Dict` is deprecated in favor of `dict`. The `typing` module itself, `Any`, and `Optional` are not deprecated; `T | None` is the modern spelling of `Optional[T]`. The unused imports are removed. See [Python's typing reference](https://docs.python.org/3/library/typing.html#deprecated-aliases).
- **Unused abstractions:** the unrelated investment function and unused Pydantic receipt class distracted from this lesson. Pydantic is supported; a class that is never constructed validates nothing.
- **Supported ADK APIs:** `ToolContext`, `state.setdefault()`, and `actions.transfer_reason` are supported in ADK 2.10.0. We use an explicit state read and assignment to make the data flow easier to follow. See the release's [State implementation](https://github.com/google/adk-python/blob/v2.10.0/src/google/adk/sessions/state.py) and [EventActions fields](https://github.com/google/adk-python/blob/v2.10.0/src/google/adk/events/event_actions.py).
- **Incorrect guarantees:** a runtime user ID is not proof of authentication; a session-state update is not an atomic banking transaction; confirmation alone does not enforce two different approvers.
- **Incomplete validation:** negative amounts could increase the balance. We now validate positive integer cents and keep all balance arithmetic exact.
- **Misleading output and tests:** a fabricated Fedwire reference is not a settlement receipt, and calling a function directly does not test its ADK confirmation wrapper.

## Implementation and guided explanation

### 1. The Stateful & Action-Steering Tool: `commercial_drawdown/tools/drawdown.py`

Read the function in this order: **validate → identify the caller → read the balance → reject, hand off, or update → return a result**.

The model supplies `facility_id`, `amount_cents`, and `disbursement_purpose`. ADK supplies `tool_context`. The function returns text, while the context carries state changes and instructions for the runtime. These are three separate responsibilities.

**Money convention:** `amount_cents` is an integer. For example, USD 75,000.00 is `7_500_000` cents, and USD 0.01 is `1` cent. This replaces the earlier `amount: float` interface; update callers accordingly. Integer arithmetic avoids binary floating-point rounding in the balance. Python also provides [Decimal](https://docs.python.org/3/library/decimal.html) for decimal arithmetic, but this lesson only needs whole cents.

**Scope:** this example supports one demo facility, `FAC-7700`, with a USD 10,000,000 starting balance per session. Restricting the facility prevents an arbitrary model-supplied ID from silently receiving a new credit line.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Simulate a drawdown while teaching ADK context, state, and actions."""

from uuid import uuid4

from google.adk.tools import ToolContext

# Constants give business rules names. Underscores make large numbers readable.
DEMO_FACILITY_ID = "FAC-7700"
INITIAL_CREDIT_CENTS = 10_000_000 * 100
CONFIRMATION_THRESHOLD_CENTS = 250_000 * 100
COMMITTEE_THRESHOLD_CENTS = 1_000_000 * 100


def format_usd(cents: int) -> str:
    """Format non-negative integer cents without floating-point arithmetic."""
    dollars, remaining_cents = divmod(cents, 100)
    return f"${dollars:,}.{remaining_cents:02d}"


def requires_dual_control(
    facility_id: str,
    amount_cents: int,
    disbursement_purpose: str,
    tool_context: ToolContext,
) -> bool:
    """Return whether this request needs the lab's confirmation checkpoint."""
    # ADK passes the tool's arguments, so this signature matches execute_drawdown.
    # Invalid amounts go to the tool's validation instead of requesting approval.
    return (
        type(amount_cents) is int
        and amount_cents >= CONFIRMATION_THRESHOLD_CENTS
    )


def execute_drawdown(
    facility_id: str,
    amount_cents: int,
    disbursement_purpose: str,
    tool_context: ToolContext,
) -> str:
    """Simulate a drawdown from the FAC-7700 demo credit facility.

    Args:
        facility_id: Demo facility identifier; must be FAC-7700.
        amount_cents: Positive whole USD cents; 7500000 means USD 75,000.00.
        disbursement_purpose: Business reason for this drawdown.

    Returns:
        A rejection, escalation notice, or simulated receipt.
    """
    # 1. Validate before changing state. Type hints do not enforce business rules.
    if type(amount_cents) is not int or amount_cents <= 0:
        return "[REJECTED] amount_cents must be a positive integer."
    if facility_id != DEMO_FACILITY_ID:
        return "[REJECTED] This lab supports only facility FAC-7700."
    if not disbursement_purpose.strip():
        return "[REJECTED] Provide a disbursement purpose."

    # 2. Read runtime identity. Never invent an identity when it is missing.
    officer_id = tool_context.user_id
    if not officer_id:
        return "[REJECTED] The application must supply a user ID."

    # 3. Read session state. get() supplies a default without storing it.
    facility_balance = tool_context.state.get(
        "available_credit_cents", INITIAL_CREDIT_CENTS
    )

    # 4. Reject insufficient credit before considering a committee handoff.
    if amount_cents > facility_balance:
        return (
            f"[REJECTED] Requested {format_usd(amount_cents)} exceeds "
            f"available credit of {format_usd(facility_balance)}."
        )

    # 5. Request a handoff without deducting credit or recording a drawdown.
    if amount_cents > COMMITTEE_THRESHOLD_CENTS:
        reason = "The request exceeds the USD 1,000,000 local authority limit."
        tool_context.actions.transfer_to_agent = "credit_committee_supervisor"
        tool_context.actions.transfer_reason = reason
        return f"[ESCALATED] {reason} No funds have been disbursed."

    # 6. Calculate new values locally before assigning them to ADK state.
    new_balance = facility_balance - amount_cents
    transaction_id = f"DEMO-{uuid4()}"
    entry = {
        "transaction_id": transaction_id,
        "facility_id": facility_id,
        "amount_cents": amount_cents,
        "purpose": disbursement_purpose,
        "requested_by": officer_id,
    }

    # Copy the existing list so append() does not mutate the stored list in place.
    drawdown_log = list(tool_context.state.get("drawdown_log", []))
    drawdown_log.append(entry)

    # Top-level assignments let ADK record the changed values in its state delta.
    tool_context.state["available_credit_cents"] = new_balance
    tool_context.state["drawdown_log"] = drawdown_log

    # 7. Skip the calling agent's LLM summary of this successful tool result.
    tool_context.actions.skip_summarization = True

    return (
        "[COMPLETED] SIMULATED DRAWDOWN — NO MONEY MOVED\n"
        f"Demo reference: {transaction_id}\n"
        f"Facility: {facility_id}\n"
        f"Amount: {format_usd(amount_cents)} USD\n"
        f"Remaining credit: {format_usd(new_balance)} USD\n"
        f"Requested by: {officer_id}\n"
        f"Purpose: {disbursement_purpose}"
    )
```

#### A. Imports, constants, and the formatting helper

`from uuid import uuid4` imports one function from Python's standard library. Calling it produces a random identifier; the `DEMO-` prefix labels its purpose. It is a receipt reference, not a payment-network ID or a mechanism for preventing duplicate transactions.

`from google.adk.tools import ToolContext` imports ADK's public tool-context name. Keep this documented import rather than reaching into private SDK internals.

The four uppercase names are **constants by convention**: names that this program does not reassign. Python does not make uppercase variables immutable. `250_000 * 100` multiplies dollars by 100 to obtain cents; underscores do not change a number's value.

`def format_usd(cents: int) -> str:` defines a function accepting an integer and returning text. Type hints describe the intended contract. The indented lines form its body, and the triple-quoted string is its docstring.

`divmod(cents, 100)` returns two values: whole dollars and leftover cents. The two names on the left unpack those values. In the f-string, braces insert expressions; `:,` adds thousands separators, and `:02d` pads the cents to two digits. Thus `format_usd(12345)` returns `"$123.45"`. This helper formats money; it does not change stored balances.

#### B. The confirmation predicate: a question with a Boolean answer

A **predicate** is a function that answers yes or no. `-> bool` describes a return value of `True` or `False`.

The signature deliberately accepts all four tool parameters. Only `amount_cents` affects this rule, but ADK passes the tool's prepared arguments when evaluating the predicate. Explicit names make that contract visible without introducing `**kwargs`. Both synchronous and asynchronous predicates are supported; ordinary `def` is sufficient because this function does no asynchronous work. See the release's [FunctionTool implementation](https://github.com/google/adk-python/blob/v2.10.0/src/google/adk/tools/function_tool.py).

`type(amount_cents) is int` checks for an actual integer. This also excludes `True` and `False`, which Python otherwise treats as integer-like values. `and` stops evaluating if its left side is false, so the comparison only runs for an integer. `>=` includes the boundary: exactly USD 250,000 requires confirmation.

This predicate neither asks a human nor executes a drawdown. Section 2 passes it to `FunctionTool`, which handles the confirmation checkpoint. Calling `execute_drawdown(...)` directly bypasses that wrapper. Use the wrapped tool in the agent.

#### C. Function arguments, validation, and early returns

`str` means text; `int` means a whole number. The model-facing docstring explains the business arguments and units. ADK supplies the annotated `tool_context` parameter at runtime and excludes it from the tool's model-facing parameter schema.

The first three `if` statements reject an invalid amount, an unsupported facility, or a blank purpose. `strip()` removes surrounding whitespace; `not` is true when the remaining string is empty. Each `return` exits the function immediately, so rejected requests cannot reach the balance update.

Read the operators literally: `=` assigns a value, `!=` means “not equal,” `<=` means “less than or equal,” and `or` accepts either condition. Thus the first guard rejects an amount if it has the wrong type **or** is zero or negative. The second guard rejects a facility ID that does not equal the demo ID.

Type hints and the tool schema help describe inputs. The positive-amount check is still necessary: an integer such as `-100` has the right type but violates the business rule.

#### D. Identity: what the runtime supplies

`officer_id = tool_context.user_id` assigns the current session's user ID to a local variable. It is not an argument the model chooses for this tool.

The hosting application must authenticate its caller and associate the verified identity with the ADK session. A development UI's user ID is not automatically a verified bank officer, and this example performs no facility-level authorization. A fallback such as `"OFFICER-SESSION-7740"` would hide missing identity; the early return makes that missing prerequisite visible.

#### E. Reading state, checking the balance, and handing off

`state.get("available_credit_cents", INITIAL_CREDIT_CENTS)` reads the stored balance. On the first successful drawdown, it uses the demo starting balance. The fallback is only a local value until the later assignment writes the new balance.

The balance check comes first. A USD 15 million request is rejected against USD 10 million of credit. A USD 2.5 million request has enough demo credit, but exceeds the local authority limit, so it takes the next branch.

`actions.transfer_to_agent` names the destination; `actions.transfer_reason` records an explanation. Assigning these fields does not call the supervisor immediately. The runtime processes the actions attached to the tool response. Section 2 registers the matching agent in the hierarchy.

The escalation branch returns before either state assignment. Its result is a request for review, not an approved drawdown. We do not set `skip_summarization` here: the supervisor still needs to respond. Registering a supervisor does not give it authority or a tool to release money.

#### F. Writing state and recording history

`new_balance = facility_balance - amount_cents` calculates an integer result locally. The braces in `entry = {...}` create a dictionary: each string key labels one value in the simulated history record. `requested_by` records the caller, not a separately authenticated approver.

`state.get("drawdown_log", [])` reads the history or supplies an empty list. `list(...)` creates a new list, and `append(entry)` adds one record to it. We do not modify any earlier record.

The two `state[key] = value` lines explicitly assign the new balance and history. ADK tracks these changes in an event's **state delta**, meaning the changed state entries. The runner and configured session service handle persistence. Copying and reassigning collections makes the change visible; simply appending to a retrieved nested list is not the pattern to teach. See [ADK state management](https://adk.dev/sessions/state/).

A session can remember values across turns. Durability across process restarts depends on its session service. These two assignments provide neither a database transaction nor protection against concurrent withdrawals. The next persistence module builds on this distinction.

#### G. Returning a receipt and controlling summarization

`skip_summarization = True` tells ADK to skip the calling agent's LLM summary of the function response. It does not itself create a text message in every client.

The parenthesized strings form one return value. Adjacent strings join together, `\n` inserts a newline, and each f-string inserts a calculated value. The client must read the function-response event and render its result to display this receipt. A client that only displays `part.text` can miss it. Consult [ADK events](https://adk.dev/events/) when building that client.

Only the success branch uses this flag. Rejections can receive a conversational explanation, and escalations can continue to the supervisor. None of these actions certifies regulatory compliance.

#### Trace one request before running it

For a request of USD 75,000.00, the model supplies `amount_cents=7_500_000`. The predicate returns `False`. The tool reads the starting `1_000_000_000` cents, subtracts `7_500_000`, assigns `992_500_000` cents, adds one history entry, and returns a receipt showing USD 9,925,000.00.

For USD 500,000.00, the predicate returns `True`. Execution pauses for confirmation. Approval allows the tool to run; rejection prevents the function body from running. The later balance and committee checks still apply after approval.

For USD 2,500,000.00, confirmation happens first because the lab's rule includes all amounts at or above USD 250,000. After approval, the tool requests a supervisor handoff and leaves the balance and drawdown history unchanged.

### 2. Wire the tool into `commercial_drawdown/agent.py`

This configuration uses the original drawdown example's model setting. The supervisor can discuss the simulated request; it has no disbursement tool.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Register the drawdown tool and its supervisor."""

from google.adk import Agent
from google.adk.tools import FunctionTool

from .tools.drawdown import execute_drawdown, requires_dual_control

credit_committee_supervisor = Agent(
    name="credit_committee_supervisor",
    model="gemini-2.5-flash",
    instruction=(
        "Review escalated requests in this drawdown simulation. "
        "Explain what information a human credit committee would need. "
        "Do not claim that funds moved, covenants were verified, "
        "or a human committee approved the request."
    ),
)

secure_drawdown_tool = FunctionTool(
    func=execute_drawdown,
    require_confirmation=requires_dual_control,
)

root_agent = Agent(
    name="loan_officer_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Help users with simulated FAC-7700 drawdowns. "
        "Use execute_drawdown for a requested drawdown. "
        "Pass amounts as integer USD cents: USD 75,000.00 is 7500000 cents. "
        "Ask for a purpose if it is missing. "
        "Never claim that this simulation moves real money."
    ),
    tools=[secure_drawdown_tool],
    sub_agents=[credit_committee_supervisor],
)
```

`FunctionTool` wraps the function. Passing `requires_dual_control` **without parentheses** supplies the function itself; ADK calls it later using each request's arguments. The names `func=` and `require_confirmation=` are keyword arguments.

`tools=[...]` registers the wrapped tool, while `sub_agents=[...]` registers the supervisor. Square brackets make Python lists. The supervisor's `name` must match the transfer destination exactly. `root_agent` is the entry point ADK loads.

The confirmation flow is: evaluate predicate → request confirmation if needed → resume with approval or rejection → execute only if allowed. This feature is still marked **experimental** in the [official confirmation guide](https://adk.dev/tools-custom/confirmation/). The retained name `requires_dual_control` expresses the lab's business motivation; the code implements one confirmation checkpoint. Actual dual control requires the application to verify distinct authorized initiator and approver identities.

Use this package layout within your Python project:

```text
commercial_drawdown/
    __init__.py
    agent.py
    tools/
        __init__.py
        drawdown.py
    test_drawdown.py
```

Put `from . import agent` in `commercial_drawdown/__init__.py`; leave `tools/__init__.py` empty. If following the open practice tree, this package belongs under `secure_finance/`. Run the commands below from the directory containing `commercial_drawdown/`.

### 3. Verify the wrapper with real ADK context objects

A plain dictionary mock can conceal SDK mistakes. This small harness uses ADK's actual `ToolContext`, session, and `FunctionTool`. It makes no model calls and requires no API key.

Save it as `commercial_drawdown/test_drawdown.py`:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""Check deterministic tool behavior without calling an LLM."""

import asyncio

from google.adk import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
from google.adk.tools.tool_confirmation import ToolConfirmation

from .tools.drawdown import execute_drawdown, requires_dual_control


async def check_case(
    amount_cents: int,
    confirmed: bool | None,
    expected: str,
) -> None:
    # Use a fresh session so each scenario starts with the same demo credit.
    service = InMemorySessionService()
    session = await service.create_session(
        app_name="drawdown_lab",
        user_id="learner",
    )
    invocation = InvocationContext(
        invocation_id="test-invocation",
        agent=Agent(name="test_agent", model="gemini-2.5-flash"),
        session=session,
        session_service=service,
    )

    # None = no answer yet; False = rejected; True = approved.
    confirmation = None
    if confirmed is not None:
        confirmation = ToolConfirmation(confirmed=confirmed)

    context = ToolContext(
        invocation_context=invocation,
        function_call_id="test-call",
        tool_confirmation=confirmation,
    )
    tool = FunctionTool(
        func=execute_drawdown,
        require_confirmation=requires_dual_control,
    )
    result = await tool.run_async(
        args={
            "facility_id": "FAC-7700",
            "amount_cents": amount_cents,
            "disbursement_purpose": "Supplier payment",
        },
        tool_context=context,
    )

    # Test the wrapper, not just a separately calculated predicate.
    if expected == "pending":
        assert "requires confirmation" in result["error"]
        assert context.actions.requested_tool_confirmations
    elif expected == "declined":
        assert "rejected" in result["error"]
    else:
        assert expected in result

    if expected == "[COMPLETED]":
        assert context.state["available_credit_cents"] == (
            1_000_000_000 - amount_cents
        )
        assert len(context.state["drawdown_log"]) == 1
        assert context.actions.skip_summarization is True
        assert "available_credit_cents" in context.actions.state_delta
        assert context.actions.transfer_to_agent is None
    else:
        assert context.actions.state_delta == {}

    if expected == "[ESCALATED]":
        assert context.actions.transfer_to_agent == "credit_committee_supervisor"
        assert context.actions.transfer_reason

    print(f"PASS: {amount_cents} cents, confirmation={confirmed}: {expected}")


async def main() -> None:
    await check_case(7_500_000, None, "[COMPLETED]")
    await check_case(24_999_999, None, "[COMPLETED]")
    await check_case(25_000_000, None, "pending")
    await check_case(50_000_000, False, "declined")
    await check_case(50_000_000, True, "[COMPLETED]")
    await check_case(100_000_000, True, "[COMPLETED]")
    await check_case(100_000_001, True, "[ESCALATED]")
    await check_case(250_000_000, None, "pending")
    await check_case(250_000_000, True, "[ESCALATED]")
    await check_case(1_500_000_000, True, "[REJECTED]")
    await check_case(0, None, "[REJECTED]")
    await check_case(-1, None, "[REJECTED]")


if __name__ == "__main__":
    asyncio.run(main())
```

`async def` defines a coroutine, and `await` waits for an asynchronous operation. Here they are needed for ADK session creation and tool execution, even though our business function is synchronous. `asyncio.run(main())` starts the event loop. The `__name__` condition runs the checks when this module is executed.

`bool | None` means three possible states: approved, rejected, or unanswered. The `is not None` check matters: `if confirmed:` would accidentally treat rejection like a missing answer. Each `assert` stops the harness if its condition is false.

Run it with:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run --no-sync python -m commercial_drawdown.test_drawdown
```

The harness checks confirmation gating, threshold boundaries, rejection, state changes, and requested handoff actions. It does not run the event loop of a complete agent conversation, persist events through a runner, verify a UI dialog, or prove that a supervisor actually executes.

**Validation recorded on 2 October 2026:** all 12 cases passed with Python 3.14.7 / ADK 2.10.0 and with the project's Python 3.12.14 / ADK 2.9.2. No live model or UI test was performed.

For a model-backed exercise, use your existing model credentials and run `uv run --no-sync adk web .`. Select `commercial_drawdown`, start a new session per scenario, and compare the trace with these predictions:

| Request in USD | Confirmation | Expected result after approval, if needed |
|---|---|---|
| 75,000.00 | No | Demo credit falls to 9,925,000.00 |
| 249,999.99 | No | Completes |
| 250,000.00 | Yes | Completes only after approval |
| 500,000.00, then reject | Yes | Function body does not execute |
| 1,000,000.00 | Yes | Completes; escalation uses `>`, not `>=` |
| 1,000,000.01 | Yes | Supervisor handoff; no balance deduction |
| 15,000,000.00 | Yes | Rejected for insufficient demo credit |
| Zero or negative | No | Rejected; no state writes |

Inspect the tool response for the receipt, the event's state delta for changed entries, and the subsequent event author for the supervisor. Confirmation and receipt presentation depend on the client; do not infer that a missing text bubble means the tool did not run.

## Apply the concepts yourself

Before editing, predict the effect; then run the relevant check.

1. Change the confirmation threshold to USD 100,000. Which boundary tests need to change, and why should the function body stay the same?
2. Make two successful USD 75,000 requests in one session. Predict a remaining balance of USD 9,850,000 and two history entries. Explain why starting a new session resets this demo.
3. Add a second demo facility. Decide how to keep its balance separate and reject unknown IDs before writing code.
4. Explain why replacing the wrapper with `tools=[execute_drawdown]` removes the confirmation checkpoint.
5. Remove `skip_summarization` temporarily and compare events. Identify the extra model response rather than relying only on the UI's appearance.

**Instructor checkpoint:** ask the learner to explain one complete request using the code, including which lines do not execute on rejection or escalation. They should distinguish model arguments, runtime identity, stored state, runtime actions, and returned text.

The preceding tools modules established how an agent calls a function. This module adds runtime context and control flow. The following persistence module examines where state is stored. A real banking implementation would additionally need authenticated facility access, distinct approver verification, transactional balance updates, retry protection, and a payment service; those properties are not supplied by this demo.

## Official references

- [ADK 2.10.0 release](https://pypi.org/project/google-adk/2.10.0/)
- [ADK function tools](https://adk.dev/tools-custom/function-tools/)
- [ADK action confirmation](https://adk.dev/tools-custom/confirmation/)
- [ADK session state](https://adk.dev/sessions/state/)
- [ADK events and actions](https://adk.dev/events/)
- [Python functions and control flow](https://docs.python.org/3/tutorial/controlflow.html)
- [Python data structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python formatted strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals)

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module13-tool-context-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

