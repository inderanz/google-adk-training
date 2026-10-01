"""
openapi/spec.py
Sovereign Horizon Core Banking OpenAPI 3.0 Specification.
Defines REST endpoints for borrower credit limits and risk profiles.
"""

CORE_BANKING_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Sovereign Horizon Core Banking Gateway",
        "description": "Enterprise REST Gateway for corporate credit limits, risk ratings, and compliance.",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "https://api.sovereignbank.internal/v1",
            "description": "Core Banking Production Gateway"
        }
    ],
    "paths": {
        # Endpoint 1: Exposure & Credit Facility Limit
        "/borrowers/{tax_id}/exposure": {
            "get": {
                "operationId": "get_borrower_exposure",
                "summary": "Retrieve existing credit facilities and utilized exposure",
                "description": "Queries the Core Ledger for approved limit, drawn balance, and available headroom.",
                "parameters": [
                    {
                        "name": "tax_id",
                        "in": "path",
                        "required": True,
                        "description": "Corporate borrower tax identification number or EIN",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful exposure retrieval",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "borrower_tax_id": {"type": "string"},
                                        "company_name": {"type": "string"},
                                        "existing_credit_limit": {"type": "number"},
                                        "current_utilized_balance": {"type": "number"},
                                        "available_headroom": {"type": "number"},
                                        "currency": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        # Endpoint 2: Borrower Risk Profile & KYC
        "/borrowers/{tax_id}/risk-profile": {
            "get": {
                "operationId": "get_borrower_risk_profile",
                "summary": "Retrieve borrower risk tier and KYC compliance status",
                "description": "Returns internal risk tier, watchlist flag, and restricted industry status.",
                "parameters": [
                    {
                        "name": "tax_id",
                        "in": "path",
                        "required": True,
                        "description": "Corporate borrower tax identification number",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful risk profile retrieval",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "borrower_tax_id": {"type": "string"},
                                        "risk_tier": {"type": "string"},
                                        "kyc_status": {"type": "string"},
                                        "watchlist_flag": {"type": "boolean"},
                                        "restricted_industry": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
