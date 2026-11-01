---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 11.6: Apigee X Gateway Security & Zero-Trust Transport Injection Challenge

> **Scope correction — 5 October 2026:** this is a local request-construction exercise, not a deployed Apigee security implementation. Read the revised [module concepts and staging acceptance matrix](./README.md) first. The solution fabricates tokens and uses an HTTP mock: neither verifies OAuth credentials nor performs mTLS. `user_id` requires an authenticated application binding; `X-Advisor-Identity` is not immutable or proof of identity. Never use the sample fallback employee in production. The separate async lock does not protect the synchronous token method. Evaluate supported managed authentication before adapting this exercise for deployment.

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.

## 🏛️ Enterprise Scenario: Apex Global Financial Services

You are a **Google Forward-Deployed Engineer (FDE)** partnering with **Apex Global Financial Services**. The bank has approved deployment of the Wealth Advisor Assistant, but the Chief Information Security Officer (CISO) and Apigee X platform team have established strict gateway entrance criteria:

1. **Zero Prompt Credential Exposure:** Under no circumstances may OAuth2 tokens, API keys, or client secrets be passed into the LLM system prompt or tool parameter declarations.
2. **Apigee X OAuth2 Enforcement:** All HTTP calls targeting Core Banking endpoints must carry a valid `Authorization: Bearer <token>` issued by the Apigee X token endpoint.
3. **API Product Entitlement:** Every request must include an `x-api-key` header matching the provisioned Apigee Developer App.
4. **Zero-Trust Caller Attribution:** The gateway requires an immutable `X-Advisor-Identity` header matching the authenticated advisor's session ID (`tool_context.user_id`).
5. **In-Memory Token Caching:** The agent must cache OAuth2 tokens in memory and refresh proactively when less than 60 seconds of validity remain, avoiding redundant round-trips to the token server.

Your objective is to implement the **`ApigeeOAuth2TokenManager`**, the dynamic **`apigee_header_provider`**, and wire them into ADK 2.0's **`OpenAPIToolset`** using active learning code skeletons.

---

## 📋 Plain English Requirements to Technical Spec

| Enterprise Banking Requirement | Architectural Mechanism | Implementation Target |
|---|---|---|
| *"Never leak credentials in LLM context."* | Zero-Trust Transport Decoupling | ADK `header_provider` injection; zero auth args in tool schemas |
| *"Acquire & cache 15-minute OAuth2 tokens."* | Asynchronous In-Memory Token Manager | `ApigeeOAuth2TokenManager` with `asyncio.Lock()` and skew buffer |
| *"Propagate caller advisor identity securely."* | Session Context Identity Bridging | `header_provider` reading `tool_context.user_id` -> `X-Advisor-Identity` |
| *"Authenticate against Apigee X Developer App."* | API Product Entitlement Header | `x-api-key` injected dynamically at the transport layer |
| *"Synthesize banking endpoints automatically."* | Zero-Adapter OpenAPI Synthesis | `OpenAPIToolset(spec_str=..., header_provider=..., httpx_client_factory=...)` |

---

## 🚀 Hands-On Challenge

### Step 1: Create the Agent Project

<Setup/>

1. **Scaffold the project directory:**
   ```shell
   uv run adk create apigee_wealth_advisor
   cd apigee_wealth_advisor
   ```

2. **Verify Environment:** Ensure your `.env` contains your Gemini API key or Vertex AI project settings.

---

### Step 2: Implement Secure Gateway Integration in `agent.py`

Open `agent.py` in `apigee_wealth_advisor`. Replace its contents with the starter skeleton below and complete all `TODO` sections.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
# In agent.py
import asyncio
import json
import time
from typing import Any, Dict, Optional
import httpx
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# TODO 1: DEFINE APIGEE X SECURED OPENAPI 3.0 SPECIFICATION
# ============================================================================
# Define the OpenAPI 3.0 specification for Apigee X Northbound Gateway.
# Endpoints required:
#   - GET /v1/accounts/{account_id}/balance  (operationId: "get_account_balance")
#   - POST /v1/transfers                      (operationId: "execute_wire_transfer")
# Security schemes required in components.securitySchemes:
#   - OAuth2 (type: "oauth2", flows: clientCredentials)
#   - ApiKeyAuth (type: "apiKey", in: "header", name: "x-api-key")

APIGEE_BANKING_SPEC: Dict[str, Any] = {
    "openapi": "3.0.3",
    "info": {
        "title": "Apex Bank Apigee X Enterprise Gateway",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://gateway.apexbank.internal/v1"}],
    "servers": [{"url": "https://gateway.syd.apexbank.com.au/v1"}],
    "paths": {
        "/accounts/{account_id}/balance": {
            "get": {
                # TODO: Add operationId: "get_account_balance"
                # TODO: Add account_id path parameter
                # TODO: Add responses (200, 401, 403)
            }
        },
        "/transfers": {
            "post": {
                # TODO: Add operationId: "execute_wire_transfer"
                # TODO: Add requestBody (source_account_id, target_account_id, amount, currency)
                # TODO: Add responses (201, 400, 401)
            }
        },
    },
    "components": {
        "securitySchemes": {
            # TODO: Define OAuth2 clientCredentials flow and ApiKeyAuth
        }
    },
}

# ============================================================================
# TODO 2: IMPLEMENT ASYNC IN-MEMORY OAUTH2 TOKEN MANAGER
# ============================================================================
# In real banking, Apigee tokens expire in 15 minutes (900 seconds).
# Requirements:
# 1. Maintain in-memory cached token and expiry timestamp.
# 2. Use asyncio.Lock() to prevent concurrent refresh races.
# 3. Refresh proactively if time_remaining < 60 seconds.

class ApigeeOAuth2TokenManager:
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self._cached_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    async def get_valid_token(self) -> str:
        # TODO: Check if current token is still valid (now + 60s < _expires_at)
        # TODO: If valid, return cached token immediately
        # TODO: If expired, acquire self._lock, re-check, and fetch a new token
        pass

# ============================================================================
# TODO 3: IMPLEMENT ADK RUNTIME HEADER PROVIDER
# ============================================================================
# ADK 2.0 invokes header_provider synchronously before every REST tool call.
# Requirements:
# 1. Obtain a valid token from token_manager.
# 2. Extract advisor user ID from readonly_context.user_id (or fallback).
# 3. Return headers dictionary with:
#    - "Authorization": f"Bearer {token}"
#    - "x-api-key": "apex-advisor-portal-key"
#    - "X-Advisor-Identity": advisor_id

def apigee_header_provider(readonly_context: Optional[ReadonlyContext] = None) -> Dict[str, str]:
    # TODO: Implement dynamic header injection
    pass

# ============================================================================
# TODO 4: SYNTHESIZE OPENAPI TOOLSET WITH TRANSPORT HOOKS
# ============================================================================
# Instantiate OpenAPIToolset passing:
#   - spec_str: serialized JSON
#   - spec_str_type: "json"
#   - header_provider: apigee_header_provider
#   - httpx_client_factory: factory providing AsyncClient (or mock emulator)

# banking_toolset = OpenAPIToolset(...)

# ============================================================================
# TODO 5: DEFINE WEALTH ADVISOR AGENT
# ============================================================================
# Construct Agent with:
#   - name="apigee_wealth_advisor"
#   - model="gemini-2.5-flash"
#   - instruction="..."
#   - tools=[banking_toolset]

# root_agent = Agent(...)
```

---

### Step 3: Run and Test Your Agent

1. **Launch the agent interactive CLI:**
   ```bash
   uv run adk run .
   ```

2. **Test Scenario Prompts:**
   * **Balance Inquiry:** `"What is the available balance for account ACC-10294?"`
   * **Wire Transfer:** `"Transfer $5,000 USD from ACC-10294 to ACC-55102 with memo 'Annual Retainer'."`

3. **Verify Zero-Trust Header Injection:**
   Observe your terminal logs. Confirm that:
   * Gemini only reasons about `account_id` and `amount`.
   * The `Authorization: Bearer` and `X-Advisor-Identity` headers were attached at the HTTP transport layer without appearing in the prompt!

---

## 🧪 Self-Reflection Questions

1. **Why is injecting OAuth2 bearer tokens in system prompts considered a high-severity vulnerability (OWASP LLM01)?**
2. **How does `asyncio.Lock()` inside `ApigeeOAuth2TokenManager` prevent the "thundering herd" problem during concurrent tool executions?**
3. **What is the difference between client-level authentication (mTLS / OAuth2 client credentials) and user-level authorization (`X-Advisor-Identity`) in a banking architecture?**

---

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMTFfNi1lbnRlcnByaXNlLWFwaWdlZS1nYXRld2F5LWF1dGgvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module11_6-enterprise-apigee-gateway-auth/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module11_6-enterprise-apigee-gateway-auth-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

