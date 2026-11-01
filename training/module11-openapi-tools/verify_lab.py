#!/usr/bin/env python3
"""verify_lab.py - Fast-Path Validation Script for Module 11 (OpenAPI Tools).

Run this script to verify your OpenAPI toolset implementation before running full tests:
    python verify_lab.py
"""

import os
import sys


def print_status(check_name: str, passed: bool, hint: str = ""):
    badge = "✅ [PASS]" if passed else "❌ [FAIL]"
    print(f"{badge} {check_name}")
    if not passed and hint:
        print(f"   👉 HINT: {hint}\n")


def verify_module11():
    print("=" * 70)
    print(" 🛠️  ADK MODULE 11: OPENAPI TOOLSET FAST-PATH VERIFICATION HARNESS")
    print("=" * 70)
    print("Evaluating OpenAPI 3.0 specification synthesis and tool generation...\n")

    target_file = sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None
    if not target_file:
        for candidate in ["agent.py", "wealth_advisor/agent.py"]:
            if os.path.exists(candidate):
                target_file = candidate
                break

    if not target_file:
        print_status(
            "File Existence Check",
            False,
            "Could not find 'agent.py'. Ensure you are in your project folder.",
        )
        sys.exit(1)

    print_status(f"Found target file: '{target_file}'", True)

    with open(target_file, "r") as f:
        code = f.read()

    print("\n--- [TIER 1: THE APPRENTICE - Core OpenAPI Synthesis] ---")
    has_spec = "CORE_BANKING_SPEC" in code or "openapi" in code
    print_status(
        "OpenAPI 3.0 Specification Object",
        has_spec,
        "Define CORE_BANKING_SPEC dictionary containing 'openapi': '3.0.0'.",
    )

    has_balance_path = "/accounts/{account_id}/balance" in code
    print_status(
        "Balance Inquiry Path Definition",
        has_balance_path,
        "Include '/accounts/{account_id}/balance' under 'paths' in your spec.",
    )

    has_balance_op_id = "get_account_balance" in code
    print_status(
        "Mandatory operationId ('get_account_balance')",
        has_balance_op_id,
        "Set operationId: 'get_account_balance'. ADK uses operationId as the Gemini tool name!",
    )

    has_toolset_init = "OpenAPIToolset(" in code
    print_status(
        "OpenAPIToolset Instantiation",
        has_toolset_init,
        "Synthesize tools using: OpenAPIToolset(spec_str=json.dumps(CORE_BANKING_SPEC), spec_str_type='json')",
    )

    has_agent = "Agent(" in code or "LlmAgent(" in code
    has_tools = "tools=" in code
    tier1_passed = has_spec and has_balance_path and has_balance_op_id and has_toolset_init and has_agent and has_tools
    print_status(
        "Tier 1 Agent Configuration",
        has_agent and has_tools,
        "Attach the banking toolset to your agent: Agent(..., tools=[banking_toolset]).",
    )

    print("\n--- [TIER 2: THE ENTERPRISE FDE - Production Hardening] ---")
    has_transfers = "/transfers" in code and "execute_wire_transfer" in code
    print_status(
        "Wire Transfer Endpoint & operationId",
        has_transfers,
        "Add POST '/transfers' with operationId: 'execute_wire_transfer' and requestBody schema.",
    )

    has_mock_transport = "MockTransport" in code or "httpx_client_factory" in code
    print_status(
        "In-Memory Mock Transport (DNS Defense)",
        has_mock_transport,
        "Private domains (api.apexbank.internal) fail in local dev. Inject httpx.MockTransport via httpx_client_factory.",
    )

    print("\n" + "=" * 70)
    if tier1_passed and has_transfers and has_mock_transport:
        print("🏆 FULL ENTERPRISE PASS! Both Tier 1 (Core) and Tier 2 (FDE) checks succeeded.")
        print("Run your programmatic verification test harness:")
        print("   python run_verification.py")
    elif tier1_passed:
        print("🎉 TIER 1 PASSED! You have successfully mastered basic OpenAPI synthesis.")
        print("To complete the full enterprise challenge, complete the Tier 2 items above.")
    else:
        print("⚠️  Tier 1 checks failed. Resolve the hints above and re-run:")
        print("   python verify_lab.py")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    verify_module11()
