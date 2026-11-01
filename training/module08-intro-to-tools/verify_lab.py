#!/usr/bin/env python3
"""verify_lab.py - Fast-Path Validation Script for Module 08 (Intro to Tools).

Run this script to verify your lab implementation before running full tests:
    python verify_lab.py
"""

import inspect
import os
import sys


def print_status(check_name: str, passed: bool, hint: str = ""):
    badge = "✅ [PASS]" if passed else "❌ [FAIL]"
    print(f"{badge} {check_name}")
    if not passed and hint:
        print(f"   👉 HINT: {hint}\n")


def verify_module08():
    print("=" * 65)
    print(" 🛠️  ADK MODULE 08: FAST-PATH VERIFICATION HARNESS")
    print("=" * 65)
    print("Checking your implementation against Google ADK production standards...\n")

    # Step 1: Detect lab file
    target_file = sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None
    if not target_file:
        for candidate in ["filing_agent.py", "agent.py", "researcher_agent/agent.py"]:
            if os.path.exists(candidate):
                target_file = candidate
                break

    if not target_file:
        print_status(
            "File Existence Check",
            False,
            "Could not find 'filing_agent.py' or 'agent.py'. Ensure you are in your project directory.",
        )
        sys.exit(1)

    print_status(f"Target file found: '{target_file}'", True)

    # Step 2: Read source code for AST / static checks
    with open(target_file, "r") as f:
        source_code = f.read()

    # Step 3: Check Tool Definition
    has_func = "def lookup_sec_filing" in source_code or "lookup_" in source_code
    print_status(
        "Tool Function Definition",
        has_func,
        "Define a Python function named 'lookup_sec_filing' for Track B.",
    )

    # Step 4: Check Type Annotations (Critical for ADK OpenAPI Schema generation)
    has_ticker_type = "ticker: str" in source_code
    has_return_type = "-> dict" in source_code
    type_hints_passed = has_ticker_type and has_return_type
    print_status(
        "Type Annotations Contract",
        type_hints_passed,
        "ADK generates OpenAPI schemas from Python type hints! Ensure signature is: "
        "'def lookup_sec_filing(ticker: str, filing_type: str = \"10-K\") -> dict:'",
    )

    # Step 5: Check Docstring (Critical for Gemini Tool Selection)
    has_docstring = '"""' in source_code or "'''" in source_code
    print_status(
        "Docstring Grounding (Tool Manual)",
        has_docstring,
        "Gemini uses function docstrings to decide when to call the tool. Add a detailed triple-quoted docstring.",
    )

    # Step 6: Check Agent Node Instantiation
    has_agent = "Agent(" in source_code
    print_status(
        "ADK Agent Node Instantiation",
        has_agent,
        "Instantiate your agent using: Agent(name='...', model='gemini-2.5-flash', tools=[...])",
    )

    # Step 7: Check Tool Registration
    has_tools_list = "tools=" in source_code
    print_status(
        "Tool Attachment to Agent",
        has_tools_list,
        "Pass your tool function to the agent's tools parameter: 'tools=[lookup_sec_filing]'.",
    )

    print("\n" + "-" * 65)
    all_passed = has_func and type_hints_passed and has_docstring and has_agent and has_tools_list

    if all_passed:
        print("🎉 EXCELLENT WORK! All static assertions passed successfully.")
        print("You are ready to run the interactive agent or full automated tests:")
        print("   uv run python filing_agent.py")
        print("=" * 65)
    else:
        print("⚠️  Some checks failed. Please address the hints above and re-run:")
        print("   python verify_lab.py")
        print("=" * 65)
        sys.exit(1)


if __name__ == "__main__":
    verify_module08()
