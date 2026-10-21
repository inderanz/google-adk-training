import json

import httpx
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

CORE_BANKING_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Apex Core Banking API",
        "description": "Enterprise REST Gateway for account balances and wire transfers.",
        "version": "1.0.0",
    },
    "servers": [
        {
            "url": "https://api.apexbank.internal/v1",
            "description": "Production Core Banking Gateway",
        }
    ],
    "paths": {
        # Endpoint 1: Balance Inquiry (GET)
        "/accounts/{account_id}/balance": {
            "get": {
                "operationId": "get_account_balance",
                "summary": "Retrieve real-time ledger balance for a customer account",
                "description": "Queries the Core Banking Ledger for available balance, ledger balance, and currency.",
                "parameters": [
                    {
                        "name": "account_id",
                        "in": "path",
                        "required": True,
                        "description": "Unique account identifier (e.g. ACC-88392)",
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful balance retrieval",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {"type": "string"},
                                        "available_balance": {"type": "number"},
                                        "currency": {"type": "string"},
                                        "status": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        # Endpoint 2: Wire Transfer Execution (POST)
        "/transfers": {
            "post": {
                "operationId": "execute_wire_transfer",
                "summary": "Submit an intra-bank wire transfer between accounts",
                "description": "Executes an immediate funds transfer from source to target account.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": [
                                    "source_account_id",
                                    "target_account_id",
                                    "amount",
                                    "currency",
                                ],
                                "properties": {
                                    "source_account_id": {
                                        "type": "string",
                                        "description": "Debited account ID",
                                    },
                                    "target_account_id": {
                                        "type": "string",
                                        "description": "Credited account ID",
                                    },
                                    "amount": {
                                        "type": "number",
                                        "description": "Transfer amount in specified currency",
                                    },
                                    "currency": {
                                        "type": "string",
                                        "description": "3-letter ISO currency code (e.g. USD, EUR)",
                                    },
                                    "reference_note": {
                                        "type": "string",
                                        "description": "Optional transfer description or memo",
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Transfer submitted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "transaction_id": {"type": "string"},
                                        "status": {"type": "string"},
                                        "timestamp": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
    },
}


def mock_banking_handler(request: httpx.Request) -> httpx.Response:
    url_str = str(request.url)
    # Mock Account Balance (GET /accounts/{account_id}/balance)
    if "/accounts/" in url_str and "/balance" in url_str:
        account_id = url_str.split("/accounts/")[1].split("/")[0]
        return httpx.Response(
            status_code=200,
            json={
                "account_id": account_id,
                "available_balance": 15420.50,
                "currency": "USD",
                "status": "ACTIVE",
            },
        )
    # Mock Wire Transfer (POST /transfers)
    elif "/transfers" in url_str:
        return httpx.Response(
            status_code=201,
            json={
                "transaction_id": "TX-99201",
                "status": "COMPLETED",
                "timestamp": "2026-10-01T12:00:00Z",
            },
        )
    return httpx.Response(status_code=404, json={"error": "Not found"})


spec_json_str = json.dumps(CORE_BANKING_SPEC, indent=2)
banking_toolset = OpenAPIToolset(
    spec_str=spec_json_str,
    spec_str_type="json",
    httpx_client_factory=lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(mock_banking_handler)
    ),
)

root_agent = Agent(
    name="banking_agent",
    model="gemini-2.5-flash",
    description="A banking agent that can perform account balance inquiries and execute wire transfers.",
    instruction="""
You are an expert Wealth Advisor Assistant at Apex Global Financial Services.
You have direct access to the Core Banking REST Gateway via synthesized tools:
- `get_account_balance`: Retrieve live balance for account ID.
- `execute_wire_transfer`: Perform intra-bank wire transfers between customer accounts.

Rules:
1. Always confirm account IDs before performing wire transfers.
2. Present monetary balances with clear currency formatting (e.g. $10,000.00 USD).
3. Provide transaction IDs upon successful wire transfer execution.
""",
    tools=[banking_toolset],
)
