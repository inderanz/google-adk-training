---
sidebar_position: 2
title: "Challenge Lab: Enterprise Core Banking OpenAPI Integration"
---

import Setup from '../_setup-snippet.mdx';

# Lab 11: Enterprise Core Banking OpenAPI Integration Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.
**Learning Checkpoint:** Review the [Module 11 Concepts](./README.md) before starting. In this lab, you transition from writing custom Python tool functions to enterprise **Zero-Adapter OpenAPI Synthesis** using Google ADK 2.0's **`OpenAPIToolset`**.

## 🏛️ Enterprise Scenario: Apex Global Financial Services
---

You are a **Google Forward-Deployed Engineer (FDE)** assigned to **Apex Global Financial Services**. The bank is modernizing its wealth management platform and wants to equip financial advisors with an AI Assistant capable of interacting with their **Core Banking Gateway**.
## 🎯 Lab Objectives

Rather than manually writing custom Python HTTP `requests` boilerplate for hundreds of REST endpoints, Apex Bank mandates **Zero-Adapter OpenAPI Synthesis**. They have provided an OpenAPI 3.0 specification for their Core Banking API, covering two critical endpoints:
1. **Account Balance Inquiry (`GET /v1/accounts/{account_id}/balance`)** – Retrieves real-time ledger balance and currency for a customer account.
2. **Intra-Bank Wire Transfer (`POST /v1/transfers`)** – Submits a high-value money transfer between accounts.
By completing this challenge lab, you will:
1. **Author an Enterprise OpenAPI 3.0 Contract:** Define an OpenAPI specification dictionary with precise `operationId` descriptors for banking endpoints.
2. **Synthesize Automated Gemini Tools:** Use ADK 2.0's `OpenAPIToolset` to convert REST path definitions into executable Gemini `FunctionDeclaration` objects.
3. **Overcome the Intranet DNS Wall:** Implement an in-memory transport mock via `httpx.MockTransport` and `httpx_client_factory` to test private intranet hostnames (`api.apexbank.internal`) without DNS crashes.
4. **Wire the OpenAPI Toolset to an Agent Node:** Connect the synthesized toolset to Gemini 2.5 Flash.
5. **Programmatically Verify REST Tool Execution:** Write an automated test harness using `InMemoryRunner` verifying both `GET` balance inquiries and `POST` wire transfers.

Your objective is to complete the OpenAPI specification dictionary and integrate it using ADK 2.0's **`OpenAPIToolset`** to equip your agent with automated REST capabilities.

---

## 📋 Plain English Requirements to Technical Spec
## Step 1: Environment & Project Setup

| Enterprise Banking Requirement | OpenAPI 3.0 Field Mapping | Expected ADK Tool Name (`operationId`) |
|---|---|---|
| *"Query customer balance by account ID."* | `GET /v1/accounts/{account_id}/balance` | `get_account_balance` |
| *"Submit wire transfer with source, target, amount, currency, and note."* | `POST /v1/transfers` | `execute_wire_transfer` |
<Setup/>

---
### 1. Initialize the Workspace
Create a clean directory for your wealth advisor agent project:

## 🚀 Hands-On Challenge
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
mkdir -p wealth_advisor
cd wealth_advisor
```

### Step 1: Create the Agent Project
### 2. Configure Environment Variables
Create a `.env` file in `wealth_advisor/`:

<Setup/>
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

1. **Create the agent project:**
   ```shell
   uv run adk create wealth_advisor
   cd wealth_advisor
   ```
   > **Note:** Select **"Other models (fill later)"** if prompted, as we will configure the model explicitly as `gemini-2.5-flash` in `agent.py`.
### 3. Initialize Project Files
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
touch agent.py
touch run_verification.py
```

2. **Verify API Credentials:** Ensure your `.env` contains your Gemini API key or Vertex AI credentials.

---

### Step 2: Implement the OpenAPI Specification & Agent Node
## Step 2: Implement the OpenAPI Specification & Agent Node (`agent.py`)

Open `agent.py` in `wealth_advisor`. Replace its contents with the starter skeleton below and complete all `TODO` sections.
Open `agent.py`. Your challenge is to complete the OpenAPI 3.0 specification dictionary, configure the in-memory mock transport, and instantiate `OpenAPIToolset`.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
# In agent.py
"""
agent.py
Wealth Advisor Agent powered by Zero-Adapter OpenAPI Synthesis in ADK 2.0.
"""
import json
import httpx
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# TODO 1: COMPLETE THE CORE BANKING OPENAPI 3.0 SPECIFICATION
# TODO 1: DEFINE THE CORE BANKING OPENAPI 3.0 SPECIFICATION
# ============================================================================
# Critical Rule: `operationId` dictates the tool name exposed to Gemini.
# - GET /v1/accounts/{account_id}/balance -> operationId: "get_account_balance"
# - POST /v1/transfers -> operationId: "execute_wire_transfer"
# Critical Rules:
# 1. `operationId` is mandatory: it becomes the exact tool name exposed to Gemini.
# 2. Provide rich parameter descriptions to guide Gemini on required values.

CORE_BANKING_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Apex Core Banking API",
        "description": "Enterprise REST Gateway for balance inquiry and wire transfers.",
        "title": "Apex Core Banking REST Gateway",
        "description": "Enterprise microservice gateway for account balance inquiries and wire transfers.",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://api.apexbank.internal/v1"}],
    "paths": {
        "/accounts/{account_id}/balance": {
            "get": {
                # TODO: Define operationId ("get_account_balance")
                # TODO: Define summary and description
                # TODO: Define path parameter "account_id" (type: string, required: True, in: "path")
                # TODO: Define responses (200 OK)
                # TODO: 1. Set operationId to "get_account_balance"
                # TODO: 2. Set summary: "Retrieve current ledger balance for a customer account."
                # TODO: 3. Define path parameter "account_id" (in: "path", required: True, schema: {"type": "string"})
                # TODO: 4. Define 200 OK response with properties: account_id, available_balance, currency
            }
        },
        "/transfers": {
            "post": {
                # TODO: Define operationId ("execute_wire_transfer")
                # TODO: Define summary and description
                # TODO: Define requestBody with JSON schema:
                #       - source_account_id (string, required)
                #       - target_account_id (string, required)
                #       - amount (number, required)
                #       - currency (string, required)
                #       - reference_note (string, optional)
                # TODO: Define responses (201 Created)
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
# TODO 2: SYNTHESIZE OPENAPI TOOLSET
# TODO 2: IMPLEMENT IN-MEMORY MOCK TRANSPORT (DNS DEFENSE)
# ============================================================================
# Convert the spec dictionary to a JSON string and instantiate OpenAPIToolset.
# Because https://api.apexbank.internal/v1 is an intranet URL, macOS/Linux will fail
# with [Errno 8] ConnectError unless intercepted in-memory via httpx.MockTransport.

# spec_json_str = json.dumps(...)
# banking_toolset = OpenAPIToolset(spec_str=..., spec_str_type="json")
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
# TODO 3: DEFINE WEALTH ADVISOR AGENT NODE
# TODO 3: SYNTHESIZE OPENAPI TOOLSET
# ============================================================================
# Construct the Agent using model="gemini-2.5-flash" and attach banking_toolset.
# 1. Serialize CORE_BANKING_SPEC to JSON string using json.dumps()
# 2. Instantiate OpenAPIToolset with httpx_client_factory returning an AsyncClient
#    configured with httpx.MockTransport(mock_banking_handler)

# root_agent = Agent(
#     name="wealth_advisor_agent",
#     model="gemini-2.5-flash",
#     description="...",
#     instruction="...",
#     tools=[...]
# banking_toolset = OpenAPIToolset(
#     spec_str=...,
#     spec_str_type="json",
#     httpx_client_factory=lambda: httpx.AsyncClient(
#         transport=httpx.MockTransport(mock_banking_handler)
#     )
# )


# ============================================================================
# TODO 4: DEFINE ROOT AGENT NODE
# ============================================================================
# 1. Name: "wealth_advisor_agent"
# 2. Model: "gemini-2.5-flash"
# 3. Instruction: direct the agent to use get_account_balance for balance queries
#    and execute_wire_transfer for money transfers.
# 4. Tools: [banking_toolset]

root_agent = None  # Replace with Agent(...)
```

> [!TIP]
> **Enterprise Tip (Handling Internal Hostnames & `ConnectError`):**
> Because `https://api.apexbank.internal/v1` is a private intranet domain, your local operating system cannot resolve it via public DNS (raising `ConnectError: [Errno 8]`).
> To test your agent locally without real network dependencies, Google FDEs inject an in-memory transport mock via `httpx_client_factory` and `httpx.MockTransport`. Check the [Lab Solution](/google-adk-training/module11-openapi-tools/lab-solution) for the complete pattern!
---

## Step 3: Programmatic Verification Harness (`run_verification.py`)

Open `run_verification.py` and implement the automated test suite using `InMemoryRunner`:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
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
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        if event.is_final_response():
            print(f"AGENT RESPONSE:\n{event.content.parts[0].text}\n")


async def main():
    print("Initializing ADK InMemoryRunner with OpenAPI Toolset...")
    app = App(name="wealth_advisor_app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id="wealth_adviser_vip",
        session_id="session_openapi_01"
    )

    # Test Case 1: Balance Inquiry (GET /accounts/{account_id}/balance)
    await execute_query(
        runner,
        session.id,
        "What is the available balance for account ACC-88392?"
    )

    # Test Case 2: Intra-Bank Wire Transfer (POST /transfers)
    await execute_query(
        runner,
        session.id,
        "Please transfer $5,000 USD from ACC-88392 to ACC-99102 with reference note 'Q3 Portfolio Balancing'."
    )


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Step 3: Run and Test Your Agent
## Step 4: Execute & Validate

1. **Start the agent interactive CLI:**
   ```bash
   uv run adk run .
   ```
Run the programmatic test harness:

2. **Test Banking Queries:**
   * *"Check the current account balance for account `ACC-88392`."*
   * *"Transfer \$5,000 USD from `ACC-88392` to `ACC-99102` with reference note 'Q3 Portfolio Balancing'."*
<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
uv run python run_verification.py
```

3. **Inspect Logs:** Observe how ADK automatically maps user intent to the synthesized `get_account_balance` and `execute_wire_transfer` tools based on the OpenAPI `operationId` definitions.
### Expected Validation Output Criteria
1. **Balance Inquiry Query:** The agent must invoke `get_account_balance` with `account_id="ACC-88392"` and report an available balance of **\$24,500.75 USD**.
2. **Wire Transfer Query:** The agent must invoke `execute_wire_transfer` with the correct JSON payload and confirm transaction ID **`TX-WIRE-99201`** with status **`SETTLED`**.
3. **Hermetic In-Memory Execution:** Both requests must succeed instantly without any `ConnectError [Errno 8]` DNS crashes.

---

## 🧪 Self-Reflection Questions
## Self-Reflection Questions

1. **Why is `operationId` the most critical field in an OpenAPI path definition when using `OpenAPIToolset`?**
2. **How does `OpenAPIToolset` prevent schema mismatch errors during POST requests compared to manual dictionary parsing?**
3. **In enterprise banking, why should authentication headers (e.g. OAuth Bearer tokens) be handled at the HTTP transport layer rather than included as arguments in LLM prompts?**
1. **Why `operationId` Matters:** What happens if an endpoint in your OpenAPI spec omits `operationId`? How does this impact Gemini's ability to call the tool?
2. **Transport Security:** Why is injecting `Authorization: Bearer <token>` via `httpx_client_factory` fundamentally more secure than instructing Gemini in the system prompt to pass an API key?
3. **Spec Whitelisting:** If a bank provides a 2,000-endpoint OpenAPI specification, why must you filter the dictionary before passing it to `OpenAPIToolset`?

---

### 🕵️ Hidden Solution 🕵️
### 🕵️ Hidden Solution Hint 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
Stuck or need to verify your implementation? Base64-decode the hint below:

`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTEtb3BlbmFwaS10b29scy9sYWItc29sdXRpb24=`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module11-openapi-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module11-openapi-tools-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- OpenAPI 3.0 Specification: https://spec.openapis.org/oas/v3.0.3
- **Google ADK OpenAPI Tools:** https://adk.dev/tools-custom/openapi-tools/
- **OpenAPI 3.0.3 Specification:** https://spec.openapis.org/oas/v3.0.3
- **Google Gemini API Function Calling:** https://ai.google.dev/gemini-api/docs/function-calling
- **HTTPX MockTransport:** https://www.python-httpx.org/advanced/transports/
