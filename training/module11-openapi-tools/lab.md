---
sidebar_position: 2
title: "Challenge Lab: Enterprise Core Banking OpenAPI Integration"
---

import Setup from '../_setup-snippet.mdx';

# Lab 11: Enterprise Core Banking OpenAPI Integration Challenge

**Learning Checkpoint:** Review the [Module 11 Concepts](./README.md) before starting. In this lab, you transition from writing custom Python tool functions to enterprise **Zero-Adapter OpenAPI Synthesis** using Google ADK 2.0's **`OpenAPIToolset`**.

---

## 🏛️ Enterprise Scenario: Apex Global Financial Services

You are a **Google Forward-Deployed Engineer (FDE)** assigned to **Apex Global Financial Services**. The bank is modernizing its wealth management platform and wants to equip financial advisors with an AI Assistant capable of interacting with their **Core Banking Gateway**.

Rather than manually writing custom Python HTTP `requests` boilerplate for hundreds of REST endpoints, Apex Bank mandates **Zero-Adapter OpenAPI Synthesis**. They have provided an OpenAPI 3.0 specification for their Core Banking API, covering two critical endpoints:
1. **Account Balance Inquiry (`GET /v1/accounts/{account_id}/balance`)** – Retrieves real-time ledger balance and currency for a customer account.
2. **Intra-Bank Wire Transfer (`POST /v1/transfers`)** – Submits a high-value money transfer between accounts.

---

## 🧭 The Two-Tier Learning Pathway

To accommodate developers of all experience levels, this challenge is structured into two distinct, progressive tiers:

```
  ┌─────────────────────────────────────────────────────────────┐
  │ TIER 1: THE APPRENTICE (15 Mins) - Core OpenAPI Synthesis   │
  │ • Define 1 GET endpoint (/accounts/{account_id}/balance)    │
  │ • Set operationId: "get_account_balance"                   │
  │ • Synthesize OpenAPIToolset and attach to Agent             │
  │ • Verify with: python verify_lab.py                        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ TIER 2: THE ENTERPRISE FDE (45 Mins) - Production Hardening │
  │ • Add POST /transfers with complex requestBody schema       │
  │ • Overcome Intranet DNS Wall ([Errno 8]) via MockTransport  │
  │ • Inject custom httpx_client_factory into OpenAPIToolset    │
  │ • Run automated verification harness: python run_verification.py │
  └─────────────────────────────────────────────────────────────┘
```

---

## 📋 Plain English Requirements to Technical Spec

| Enterprise Banking Requirement | OpenAPI 3.0 Field Mapping | Expected ADK Tool Name (`operationId`) | Tier Level |
|---|---|---|:---:|
| *"Query customer balance by account ID."* | `GET /v1/accounts/{account_id}/balance` | `get_account_balance` | **Tier 1** |
| *"Submit wire transfer with source, target, amount, currency, and note."* | `POST /v1/transfers` | `execute_wire_transfer` | **Tier 2** |

---

## 🚀 Hands-On Challenge

### Step 1: Environment & Project Setup

<Setup/>

1. **Initialize the workspace:**
   ```bash
   mkdir -p wealth_advisor
   cd wealth_advisor
   ```

2. **Configure environment variables (`.env`):**
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   *(Or use Vertex AI credentials if testing on Google Cloud).*

3. **Initialize project files:**
   ```bash
   touch agent.py
   touch run_verification.py
   ```

---

### Step 2: Implement the OpenAPI Specification & Agent Node (`agent.py`)

Open `agent.py`. Complete the starter skeleton below:
- **Tier 1 Learners:** Complete `TODO 1A`, `TODO 2A`, and `TODO 3`.
- **Tier 2 (FDE) Learners:** Complete all `TODO` items including `TODO 1B` and `TODO 2B` (Mock Transport).

```python
# In agent.py
"""
agent.py
Wealth Advisor Agent powered by Zero-Adapter OpenAPI Synthesis in ADK 2.0.
"""

import json
import httpx
from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# TODO 1: DEFINE THE CORE BANKING OPENAPI 3.0 SPECIFICATION
# ============================================================================
# Critical Rules:
# 1. `operationId` is mandatory: it becomes the exact tool name exposed to Gemini.
# 2. Provide rich parameter descriptions to guide Gemini on required values.

CORE_BANKING_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Apex Core Banking REST Gateway",
        "description": "Enterprise microservice gateway for account balance inquiries and wire transfers.",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://api.apexbank.internal/v1"}],
    "paths": {
        # --------------------------------------------------------------------
        # [TIER 1] TODO 1A: Balance Inquiry Endpoint
        # --------------------------------------------------------------------
        "/accounts/{account_id}/balance": {
            "get": {
                # TODO: 1. Set operationId to "get_account_balance"
                # TODO: 2. Set summary: "Retrieve current ledger balance for a customer account."
                # TODO: 3. Define path parameter "account_id" (in: "path", required: True, schema: {"type": "string"})
                # TODO: 4. Define 200 OK response with schema: account_id, available_balance, currency
            }
        },
        # --------------------------------------------------------------------
        # [TIER 2] TODO 1B: Wire Transfer Endpoint
        # --------------------------------------------------------------------
        "/transfers": {
            "post": {
                # TODO: 1. Set operationId to "execute_wire_transfer"
                # TODO: 2. Set summary: "Initiate an intra-bank funds transfer between two accounts."
                # TODO: 3. Define requestBody with application/json schema requiring:
                #          - source_account (string)
                #          - destination_account (string)
                #          - amount (number)
                #          - currency (string)
                #          - reference_note (string, optional)
                # TODO: 4. Define 201 Created response with properties: transaction_id, status, amount_transferred
            }
        },
    },
}

# ============================================================================
# [TIER 2] TODO 2B: IN-MEMORY MOCK TRANSPORT (DNS DEFENSE)
# ============================================================================
# Because https://api.apexbank.internal/v1 is a private intranet domain, macOS/Linux will fail
# with [Errno 8] ConnectError unless intercepted in-memory via httpx.MockTransport.


def mock_banking_handler(request: httpx.Request) -> httpx.Response:
    """Intercepts outbound HTTP requests and returns synthetic banking responses."""
    # TODO: 1. Check if request.url.path contains "/balance":
    #          Return httpx.Response(200, json={
    #              "account_id": "ACC-88392",
    #              "available_balance": 24500.75,
    #              "currency": "USD"
    #          })
    # TODO: 2. Check if request.url.path contains "/transfers":
    #          Parse payload = json.loads(request.content)
    #          Return httpx.Response(201, json={
    #              "transaction_id": "TX-WIRE-99201",
    #              "status": "SETTLED",
    #              "amount_transferred": payload.get("amount")
    #          })
    # TODO: 3. Fallback: return httpx.Response(404, json={"error": "Not Found"})
    pass


# ============================================================================
# TODO 2A & 2B: SYNTHESIZE OPENAPI TOOLSET
# ============================================================================
# 1. Serialize CORE_BANKING_SPEC to JSON string using json.dumps()
# 2. For Tier 1: OpenAPIToolset(spec_str=..., spec_str_type="json")
# 3. For Tier 2: Add httpx_client_factory returning an AsyncClient with MockTransport:
#    httpx_client_factory=lambda: httpx.AsyncClient(
#        transport=httpx.MockTransport(mock_banking_handler)
#    )

banking_toolset = None  # Replace with OpenAPIToolset(...)


# ============================================================================
# TODO 3: DEFINE ROOT AGENT NODE
# ============================================================================
# 1. Name: "wealth_advisor_agent"
# 2. Model: "gemini-2.5-flash"
# 3. Instruction: direct the agent to use get_account_balance for balance queries
#    and execute_wire_transfer for money transfers.
# 4. Tools: [banking_toolset]

root_agent = None  # Replace with Agent(...)
```

---

### Step 3: Fast-Path Pre-Flight Validation

Before running full tests, execute the fast-path checker to verify your OpenAPI specification syntax and operation IDs:

```bash
python verify_lab.py
```

* **If you are on Tier 1:** The script will confirm that your specification syntax, `operationId: "get_account_balance"`, and `OpenAPIToolset` are valid.
* **If you are on Tier 2:** The script will additionally verify `execute_wire_transfer` and the `MockTransport` DNS defense.

---

### Step 4: Programmatic Verification Harness (`run_verification.py`)

Open `run_verification.py` and implement the automated test suite using `InMemoryRunner`:

```python
"""
run_verification.py
Automated programmatic test harness verifying OpenAPI tool synthesis and execution.
"""

import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from google.genai import types
from agent import root_agent

load_dotenv()


async def execute_query(runner: InMemoryRunner, session_id: str, prompt: str):
    print(f"\n==================================================")
    print(f"USER QUERY: {prompt}")
    print(f"==================================================")

    async for event in runner.run_async(
        user_id="wealth_adviser_vip",
        session_id=session_id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.is_final_response():
            print(f"AGENT RESPONSE:\n{event.content.parts[0].text}\n")


async def main():
    print("Initializing ADK InMemoryRunner with OpenAPI Toolset...")
    app = App(name="wealth_advisor_app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name=app.name, user_id="wealth_adviser_vip", session_id="session_openapi_01"
    )

    # Test Case 1: Balance Inquiry (GET /accounts/{account_id}/balance)
    await execute_query(
        runner, session.id, "What is the available balance for account ACC-88392?"
    )

    # Test Case 2: Intra-Bank Wire Transfer (POST /transfers)
    await execute_query(
        runner,
        session.id,
        "Please transfer $5,000 USD from ACC-88392 to ACC-99102 with reference note 'Q3 Portfolio Balancing'.",
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Run the harness:
```bash
uv run python run_verification.py
```

### Expected Validation Output Criteria
1. **Balance Inquiry Query:** The agent must invoke `get_account_balance` with `account_id="ACC-88392"` and report an available balance of **$24,500.75 USD**.
2. **Wire Transfer Query:** The agent must invoke `execute_wire_transfer` with the correct JSON payload and confirm transaction ID **`TX-WIRE-99201`** with status **`SETTLED`**.
3. **Hermetic In-Memory Execution:** Both requests must succeed instantly without any `ConnectError [Errno 8]` DNS crashes.

---

## 🧪 Self-Reflection Questions

1. **Why `operationId` Matters:** What happens if an endpoint in your OpenAPI spec omits `operationId`? How does this impact Gemini's ability to call the tool?
2. **Transport Security:** Why is injecting `Authorization: Bearer <token>` via `httpx_client_factory` fundamentally more secure than instructing Gemini in the system prompt to pass an API key?
3. **Spec Whitelisting:** If a bank provides a 2,000-endpoint OpenAPI specification, why must you filter the dictionary before passing it to `OpenAPIToolset`?

---

### 🕵️ Hidden Solution Hint 🕵️

Stuck or need to verify your implementation? Base64-decode the hint below:

`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTEtb3BlbmFwaS10b29scy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module11-openapi-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module11-openapi-tools-lab -->
---

## Official References

- **Google ADK OpenAPI Tools:** https://adk.dev/tools-custom/openapi-tools/
- **OpenAPI 3.0.3 Specification:** https://spec.openapis.org/oas/v3.0.3
- **Google Gemini API Function Calling:** https://ai.google.dev/gemini-api/docs/function-calling
- **HTTPX MockTransport:** https://www.python-httpx.org/advanced/transports/
