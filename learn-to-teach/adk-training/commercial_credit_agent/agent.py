"""
agent.py
Sovereign Horizon Bank - Commercial Credit Underwriting Triage Agent.
Integrates Pydantic mathematical tools with OpenAPI 3.0 Core Banking Gateway.
"""

from pathlib import Path

from commercial_credit_agent.tools.financial_math import (
    calculate_debt_to_ebitda,
    calculate_dscr,
    evaluate_covenant_policy,
)
try:
    from commercial_credit_agent.tools.financial_math import (
        calculate_dscr,
        calculate_debt_to_ebitda,
        evaluate_covenant_policy
    )
except ImportError:
    from tools.financial_math import (
        calculate_dscr,
        calculate_debt_to_ebitda,
        evaluate_covenant_policy
    )
from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

# ============================================================================
# 1. LOAD EXTERNAL OPENAPI SPEC FILE (PRODUCTION PATTERN)
# ============================================================================
# Rather than hardcoding specs in Python dicts, an FDE reads the external file on disk.
SPEC_PATH = Path(__file__).parent / "openapi" / "core_banking_openapi.json"
spec_str = SPEC_PATH.read_text(encoding="utf-8")

# Ingest OpenAPI 3.0 specification directly into Gemini FunctionDeclarations:
# - get_borrower_exposure
# - get_borrower_risk_profile
core_banking_toolset = OpenAPIToolset(spec_str=spec_str, spec_str_type="json")

# ============================================================================
# 2. ASSEMBLE COMMERCIAL CREDIT TRIAGE AGENT NODE
# ============================================================================
root_agent = Agent(
    name="commercial_credit_triage_agent",
    model="gemini-2.5-flash",
    description="Autonomous Credit Underwriting Triage Agent for middle-market commercial loans.",
    instruction="""
You are an expert Principal Commercial Credit Underwriting Officer at Sovereign Horizon Bank.
Your mission is to perform rigorous, auditable loan triage for credit facilities ($5M to $50M) under Fed SR 11-7 standards.

Available Tools:
1. `get_borrower_exposure`: Query core ledger for existing credit limits and current utilized balance.
2. `get_borrower_risk_profile`: Check risk tier (Prime/Moderate/Watchlist), KYC status, and restricted industries.
3. `calculate_dscr`: Compute Debt Service Coverage Ratio (Target >= 1.25x).
4. `calculate_debt_to_ebitda`: Compute corporate leverage (Target <= 3.5x).
5. `evaluate_covenant_policy`: Evaluate consolidated financial metrics against bank credit covenants.

Triage Execution Protocol:
Step 1: Inquire into borrower exposure and risk profile using the borrower's tax ID (EIN).
Step 2: If borrower is on the Watchlist or operates in a restricted industry, immediately DECLINE the application.
Step 3: Execute `calculate_dscr` and `calculate_debt_to_ebitda` using the borrower's financial figures.
Step 4: Run `evaluate_covenant_policy` to verify overall compliance.
Step 5: Synthesize a formalized Credit Committee Preliminary Assessment Memorandum in the following structured format:

---
# 🏛️ CREDIT COMMITTEE PRELIMINARY ASSESSMENT MEMORANDUM

### 1. BORROWER & FACILITY OVERVIEW
- **Borrower Tax ID (EIN):** <tax_id>
- **Company Name:** <name from exposure>
- **Existing Credit Limit:** <amount>
- **Utilized Exposure:** <amount>
- **Available Headroom:** <headroom>

### 2. RISK & REGULATORY COMPLIANCE
- **Internal Risk Tier:** <tier>
- **KYC Status:** <status>
- **Watchlist Flag:** <YES/NO>
- **Restricted Industry:** <YES/NO>

### 3. FINANCIAL COVENANT ANALYSIS
- **DSCR:** <ratio>x (Threshold: >= 1.25x) - <Assessment>
- **Debt-to-EBITDA:** <ratio>x (Threshold: <= 3.5x) - <Assessment>

### 4. RECOMMENDATION & NEXT ACTIONS
- **Action:** [APPROVE_FOR_COMMITTEE | CONDITIONAL_REVIEW | DECLINE]
- **Justification Rationale:** <detailed justification>
- **Human-in-the-Loop Conditions:** <mitigating conditions if borderline>
---
""",
    tools=[
        core_banking_toolset,
        calculate_dscr,
        calculate_debt_to_ebitda,
        evaluate_covenant_policy,
    ],
)
