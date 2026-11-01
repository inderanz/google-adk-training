#!/usr/bin/env python3
"""verify_lab.py - Fast-Path Validation Script for Module 11.5 (Credit Underwriting).

Run this script to verify your underwriting tools and agent implementation before running full tests:
    python verify_lab.py
"""

import os
import sys


def print_status(check_name: str, passed: bool, hint: str = ""):
    badge = "✅ [PASS]" if passed else "❌ [FAIL]"
    print(f"{badge} {check_name}")
    if not passed and hint:
        print(f"   👉 HINT: {hint}\n")


def verify_module11_5():
    print("=" * 70)
    print(" 🛠️  ADK MODULE 11.5: CREDIT UNDERWRITING FAST-PATH VERIFICATION HARNESS")
    print("=" * 70)
    print("Evaluating financial math tools, covenant policies, and OpenAPI synthesis...\n")

    # Step 1: Check tools/financial_math.py
    math_file = sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None
    if not math_file:
        for candidate in [
            "tools/financial_math.py",
            "commercial_credit_triage/tools/financial_math.py",
        ]:
            if os.path.exists(candidate):
                math_file = candidate
                break

    if not math_file:
        print_status(
            "File Existence Check (tools/financial_math.py)",
            False,
            "Could not find 'tools/financial_math.py'. Ensure your project directory structure is set up.",
        )
        sys.exit(1)

    print_status(f"Found math tools file: '{math_file}'", True)

    with open(math_file, "r") as f:
        math_code = f.read()

    print("\n--- [TIER 1: THE APPRENTICE - Core Financial Math Tools] ---")
    has_dscr_class = "class DscrResult" in math_code
    print_status(
        "DscrResult Pydantic Model",
        has_dscr_class,
        "Define class DscrResult(BaseModel) in tools/financial_math.py with dscr_ratio and is_compliant fields.",
    )

    has_dscr_calc = "def calculate_dscr" in math_code
    print_status(
        "calculate_dscr Function Definition",
        has_dscr_calc,
        "Implement calculate_dscr(net_operating_income: float, total_debt_service: float) -> DscrResult.",
    )

    has_zero_div_guard = "total_debt_service <= 0" in math_code or "total_debt_service == 0" in math_code
    print_status(
        "ZeroDivisionError Defensive Guard",
        has_zero_div_guard,
        "Production agents must never crash on zero debt service! Add an if total_debt_service <= 0: check.",
    )

    tier1_passed = has_dscr_class and has_dscr_calc and has_zero_div_guard

    print("\n--- [TIER 2: THE ENTERPRISE FDE - Policy Engine & OpenAPI Gateway] ---")
    has_covenant = "def evaluate_covenant_policy" in math_code
    print_status(
        "Covenant Policy Decision Engine",
        has_covenant,
        "Implement evaluate_covenant_policy(...) in tools/financial_math.py with borderline review logic.",
    )

    spec_file = None
    for candidate in [
        "openapi/spec.py",
        "openapi/core_banking_openapi.json",
        "commercial_credit_triage/openapi/spec.py",
        "commercial_credit_triage/openapi/core_banking_openapi.json",
        "core_banking_openapi.json",
    ]:
        if os.path.exists(candidate):
            spec_file = candidate
            break

    has_spec = False
    if spec_file:
        with open(spec_file, "r") as f:
            spec_code = f.read()
            has_spec = (
                "get_borrower_exposure" in spec_code
                and "get_borrower_risk_profile" in spec_code
            )
    print_status(
        "Core Banking OpenAPI Spec (exposure & risk profile)",
        has_spec,
        "Define OpenAPI spec (in openapi/spec.py or openapi/core_banking_openapi.json) with operationId: get_borrower_exposure and get_borrower_risk_profile.",
    )

    agent_file = None
    for candidate in ["agent.py", "commercial_credit_triage/agent.py"]:
        if os.path.exists(candidate):
            agent_file = candidate
            break

    has_unified_agent = False
    if agent_file:
        with open(agent_file, "r") as f:
            agent_code = f.read()
            has_unified_agent = (
                "Agent(" in agent_code
                and "OpenAPIToolset(" in agent_code
                and "calculate_dscr" in agent_code
            )
    print_status(
        "Unified Multi-Tool Agent Node (Math + OpenAPI)",
        has_unified_agent,
        "In agent.py, instantiate Agent(name='commercial_credit_triage_agent', tools=[calculate_dscr, ..., openapi_toolset]).",
    )

    print("\n" + "=" * 70)
    if tier1_passed and has_covenant and has_spec and has_unified_agent:
        print("🏆 FULL ENTERPRISE PASS! Both Tier 1 (Core Math) and Tier 2 (FDE) checks succeeded.")
        print("Test your agent in the interactive CLI:")
        print("   uv run adk run .")
    elif tier1_passed:
        print("🎉 TIER 1 PASSED! You have successfully mastered deterministic financial tools.")
        print("To complete the full underwriting engine, complete the Tier 2 items above.")
    else:
        print("⚠️  Tier 1 checks failed. Address the hints above and re-run:")
        print("   python verify_lab.py")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    verify_module11_5()
