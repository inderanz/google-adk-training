---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 11: Enterprise Core Banking OpenAPI Integration Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.

## 🏛️ Enterprise Scenario: Apex Global Financial Services

You are a **Google Forward-Deployed Engineer (FDE)** assigned to **Apex Global Financial Services**. The bank is modernizing its wealth management platform and wants to equip financial advisors with an AI Assistant capable of interacting with their **Core Banking Gateway**.

Rather than manually writing custom Python HTTP `requests` boilerplate for hundreds of REST endpoints, Apex Bank mandates **Zero-Adapter OpenAPI Synthesis**. They have provided an OpenAPI 3.0 specification for their Core Banking API, covering two critical endpoints:
1. **Account Balance Inquiry (`GET /v1/accounts/{account_id}/balance`)** – Retrieves real-time ledger balance and currency for a customer account.
2. **Intra-Bank Wire Transfer (`POST /v1/transfers`)** – Submits a high-value money transfer between accounts.

Your objective is to complete the OpenAPI specification dictionary and integrate it using ADK 2.0's **`OpenAPIToolset`** to equip your agent with automated REST capabilities.

---

## 📋 Plain English Requirements to Technical Spec

| Enterprise Banking Requirement | OpenAPI 3.0 Field Mapping | Expected ADK Tool Name (`operationId`) |
|---|---|---|
| *"Query customer balance by account ID."* | `GET /v1/accounts/{account_id}/balance` | `get_account_balance` |
| *"Submit wire transfer with source, target, amount, currency, and note."* | `POST /v1/transfers` | `execute_wire_transfer` |

---

## 🚀 Hands-On Challenge

### Step 1: Create the Agent Project

<Setup/>

1. **Create the agent project:**
   ```shell
   uv run adk create wealth_advisor
   cd wealth_advisor
   ```
   > **Note:** Select **"Other models (fill later)"** if prompted, as we will configure the model explicitly as `gemini-2.5-flash` in `agent.py`.

2. **Verify API Credentials:** Ensure your `.env` contains your Gemini API key or Vertex AI credentials.

---

### Step 2: Implement the OpenAPI Specification & Agent Node

Open `agent.py` in `wealth_advisor`. Replace its contents with the starter skeleton below and complete all `TODO` sections.

```python
# In agent.py
import json
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# TODO 1: COMPLETE THE CORE BANKING OPENAPI 3.0 SPECIFICATION
# ============================================================================
# Critical Rule: `operationId` dictates the tool name exposed to Gemini.
# - GET /v1/accounts/{account_id}/balance -> operationId: "get_account_balance"
# - POST /v1/transfers -> operationId: "execute_wire_transfer"

CORE_BANKING_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Apex Core Banking API",
        "description": "Enterprise REST Gateway for balance inquiry and wire transfers.",
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
            }
        },
    },
}

# ============================================================================
# TODO 2: SYNTHESIZE OPENAPI TOOLSET
# ============================================================================
# Convert the spec dictionary to a JSON string and instantiate OpenAPIToolset.

# spec_json_str = json.dumps(...)
# banking_toolset = OpenAPIToolset(spec_str=..., spec_str_type="json")

# ============================================================================
# TODO 3: DEFINE WEALTH ADVISOR AGENT NODE
# ============================================================================
# Construct the Agent using model="gemini-2.5-flash" and attach banking_toolset.

# root_agent = Agent(
#     name="wealth_advisor_agent",
#     model="gemini-2.5-flash",
#     description="...",
#     instruction="...",
#     tools=[...]
# )
```

> [!TIP]
> **Enterprise Tip (Handling Internal Hostnames & `ConnectError`):**
> Because `https://api.apexbank.internal/v1` is a private intranet domain, your local operating system cannot resolve it via public DNS (raising `ConnectError: [Errno 8]`).
> To test your agent locally without real network dependencies, Google FDEs inject an in-memory transport mock via `httpx_client_factory` and `httpx.MockTransport`. Check the [Lab Solution](/google-adk-training/module11-openapi-tools/lab-solution) for the complete pattern!

---

### Step 3: Run and Test Your Agent

1. **Start the agent interactive CLI:**
   ```bash
   uv run adk run .
   ```

2. **Test Banking Queries:**
   * *"Check the current account balance for account `ACC-88392`."*
   * *"Transfer \$5,000 USD from `ACC-88392` to `ACC-99102` with reference note 'Q3 Portfolio Balancing'."*

3. **Inspect Logs:** Observe how ADK automatically maps user intent to the synthesized `get_account_balance` and `execute_wire_transfer` tools based on the OpenAPI `operationId` definitions.

---

## 🧪 Self-Reflection Questions

1. **Why is `operationId` the most critical field in an OpenAPI path definition when using `OpenAPIToolset`?**
2. **How does `OpenAPIToolset` prevent schema mismatch errors during POST requests compared to manual dictionary parsing?**
3. **In enterprise banking, why should authentication headers (e.g. OAuth Bearer tokens) be handled at the HTTP transport layer rather than included as arguments in LLM prompts?**

---

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
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
