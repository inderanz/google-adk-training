---
sidebar_position: 2
title: "Challenge Lab: Building an Enterprise Custom Tool Agent"
---

import Setup from '../_setup-snippet.mdx';

# Lab 9: Building an Enterprise Custom Tool Agent

**Learning Checkpoint:** Review the [Module 09 Concepts](./README.md) before starting. In this lab, you transition from consumer AI prompt-engineering to enterprise systems engineering by building deterministic, type-safe custom function tools for Google ADK 2.0.

---

## 🎯 Lab Objectives

By completing this challenge lab, you will:
1. **Design Type-Safe Tool Contracts:** Write custom Python functions with strict type hints and Google-style docstrings parsed into OpenAPI 3.0 schemas.
2. **Implement Defensive Error Trapping:** Prevent unhandled runtime exceptions (such as `ZeroDivisionError`) from crashing the ADK runner.
3. **Build Enterprise Billing Logic:** Create a specialized GST tax invoicing tool that computes itemized tax breakdowns deterministically.
4. **Register Tools in an ADK Agent Node:** Wire your custom functions into an ADK 2.0 `Agent` instance.
5. **Programmatically Verify Execution:** Execute test prompts using `InMemoryRunner` to observe and validate tool call events and responses.

---

## Step 1: Environment & Project Setup

<Setup/>

### 1. Initialize the Workspace
Create a clean directory for your calculator agent project:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
mkdir -p calculator_agent/tools
cd calculator_agent
```

### 2. Configure Environment Variables
Create a `.env` file in `calculator_agent/`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Initialize Package Structure
Ensure Python recognizes your tools directory as a package:

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```bash
touch tools/__init__.py
touch tools/calculator.py
touch agent.py
touch run_verification.py
```

---

## Step 2: Implement Custom Tools (`tools/calculator.py`)

Open `tools/calculator.py`. Your task is to complete the tool functions below. 

> [!IMPORTANT]
> **Pedagogical Challenge:**
> Do not write arbitrary code. Follow the **5 Anatomical Principles** from the Theory section:
> 1. Use explicit type hints for all arguments.
> 2. Include comprehensive Google-style docstrings describing the tool's purpose and parameter meanings.
> 3. Implement defensive guard clauses so that no operation ever raises an unhandled Python exception.
> 4. Return structured dictionaries with status indicators (`"success"` or `"error"`).

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""
tools/calculator.py
Enterprise custom function tools for arithmetic and tax calculation.
"""
from typing import Dict, Any


def add(a: float, b: float) -> Dict[str, Any]:
    """Adds two floating-point numbers together.

    Use this tool when the user asks to find the sum of two numbers.

    Args:
        a: The first number (addend).
        b: The second number (addend).

    Returns:
        A dictionary with 'status' and the computed 'result'.
    """
    # TODO: Calculate the sum of a and b.
    # Return: {"status": "success", "result": a + b}
    pass


def subtract(a: float, b: float) -> Dict[str, Any]:
    """Subtracts the second number from the first number.

    Use this tool when the user asks to find the difference between two numbers.

    Args:
        a: The starting number (minuend).
        b: The number to subtract (subtrahend).

    Returns:
        A dictionary with 'status' and the computed 'result'.
    """
    # TODO: Calculate the difference (a - b).
    # Return: {"status": "success", "result": a - b}
    pass


def multiply(a: float, b: float) -> Dict[str, Any]:
    """Multiplies two numbers together.

    Use this tool when the user asks to find the product of two numbers.

    Args:
        a: The first factor.
        b: The second factor.

    Returns:
        A dictionary with 'status' and the computed 'result'.
    """
    # TODO: Calculate the product (a * b).
    # Return: {"status": "success", "result": a * b}
    pass


def divide(a: float, b: float) -> Dict[str, Any]:
    """Divides the first number by the second number with defensive error handling.

    Use this tool when the user asks to divide one number by another.

    Args:
        a: The numerator (dividend).
        b: The denominator (divisor).

    Returns:
        A dictionary with 'status', 'result', or an error 'message'.
    """
    # TODO: Implement defensive error trapping!
    # If b == 0, DO NOT allow Python to raise ZeroDivisionError.
    # Return: {"status": "error", "message": "Division by zero is undefined."}
    # Otherwise, return: {"status": "success", "result": a / b}
    pass


def calculate_gst_invoice(
    amount: float, tax_rate_percent: float = 18.0
) -> Dict[str, Any]:
    """Calculates an itemized GST invoice including CGST, SGST, and the total payable amount.

    Use this tool whenever a user asks to calculate GST, sales tax, or an invoice total.
    Never guess or approximate tax calculations without calling this tool.

    Args:
        amount: The base pre-tax amount in currency units (must be positive).
        tax_rate_percent: The applicable GST tax percentage slab (defaults to 18.0).

    Returns:
        A dictionary with itemized tax components (base_amount, cgst, sgst, total_gst, total_payable).
    """
    # TODO: Guard against negative amounts or tax rates
    # If amount < 0 or tax_rate_percent < 0:
    #     Return: {"status": "error", "message": "Amount and tax rate must be non-negative."}

    # TODO: Compute itemized tax:
    # 1. total_gst = round(amount * (tax_rate_percent / 100.0), 2)
    # 2. cgst = round(total_gst / 2.0, 2)
    # 3. sgst = round(total_gst / 2.0, 2)
    # 4. total_payable = round(amount + total_gst, 2)

    # TODO: Return structured dictionary with:
    # 'status': 'success',
    # 'base_amount': amount,
    # 'tax_rate_percent': tax_rate_percent,
    # 'cgst': cgst,
    # 'sgst': sgst,
    # 'total_gst': total_gst,
    # 'total_payable': total_payable
    pass
```

---

## Step 3: Configure the Agent Node (`agent.py`)

Open `agent.py`. Wire your custom tool functions into an ADK 2.0 `Agent` instance.

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.
- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.
- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.
- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.
<!-- TEACHER_NOTE_END -->
```python
"""
agent.py
Root agent definition binding custom tools to Gemini 2.5 Flash.
"""
from google.adk import Agent
from tools.calculator import (
    add,
    subtract,
    multiply,
    divide,
    calculate_gst_invoice,
)

# TODO: Complete the root_agent definition:
# 1. Set name to "calculator_agent"
# 2. Set model to "gemini-2.5-flash"
# 3. Write strict instructions commanding the agent to:
#    - ALWAYS invoke the corresponding tool for math and tax calculations.
#    - NEVER calculate numbers internally.
#    - Explain errors gracefully if a tool returns status="error".
# 4. Register all 5 imported tool functions in the tools list.

root_agent = Agent(
    name="calculator_agent",
    model="gemini-2.5-flash",
    description="Deterministic arithmetic and tax billing agent.",
    instruction="""
# TODO: Write system instruction following the guidelines above
""",
    tools=[
        # TODO: Add your 5 functions here
    ],
)
```

---

## Step 4: Programmatic Verification (`run_verification.py`)

In production agent development, relying solely on manual chat is insufficient. You must write automated programmatic verification scripts that test the agent against edge cases.

Open `run_verification.py` and implement the test runner using ADK's `InMemoryRunner`:

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
Programmatic test runner verifying tool calling and error trapping.
"""
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from google.genai import types
from agent import root_agent

load_dotenv()


async def run_test_case(runner: InMemoryRunner, session_id: str, prompt: str):
    print(f"\n--- User Query: {prompt} ---")
    tool_invoked = False

    async for event in runner.run_async(
        user_id="test_engineer",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        # TODO: Inspect event to verify if a tool was executed
        # Hint: check if event has content or tool call information
        
        # Check if this is the final agent response
        if event.is_final_response():
            response_text = event.content.parts[0].text
            print(f"Agent Response:\n{response_text}")


async def main():
    # 1. Create ADK App and Runner
    app = App(name="calculator_app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    # 2. Initialize a test session
    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id="test_engineer",
        session_id="test_session_01"
    )

    # 3. Test Cases to Verify:
    # Test A: Basic Arithmetic
    await run_test_case(runner, session.id, "What is 42.5 + 118.3?")

    # Test B: Defensive Zero Division
    await run_test_case(runner, session.id, "What is 100 divided by 0?")

    # Test C: Enterprise GST Calculation
    await run_test_case(runner, session.id, "Calculate the GST invoice for an order of Rs. 15,000 at 18% tax.")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 5: Execute & Validate

Run the programmatic test script:

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

### Expected Output Criteria
1. **Arithmetic Query (`42.5 + 118.3`):** The final answer must state `160.8`.
2. **Defensive Error Query (`100 / 0`):** The agent must politely inform the user that division by zero is undefined, **without raising any Python exception or crashing**.
3. **GST Invoicing Query (`Rs. 15,000 @ 18%`):** The response must itemize:
   - Base Amount: Rs. 15,000.00
   - CGST (9%): Rs. 1,350.00
   - SGST (9%): Rs. 1,350.00
   - Total GST (18%): Rs. 2,700.00
   - Total Payable: Rs. 17,700.00

---

## Self-Reflection Questions

1. **Docstring Impact:** What happens if you remove the `Args:` section from `calculate_gst_invoice`? How does this alter the generated OpenAPI schema?
2. **Exception vs. Soft Error:** Why does returning `{"status": "error", "message": "..."}` allow Gemini to recover, whereas `raise ZeroDivisionError()` terminates the agent turn?
3. **Pydantic Migration:** Why would an enterprise engineering team replace raw Python dictionaries with Pydantic `BaseModel` classes for tool return types?

---

### 🕵️ Hidden Solution Hint 🕵️

Stuck or need to verify your implementation? Base64-decode the hint below:

`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDktaW50cm8tY3VzdG9tLWZ1bmN0aW9uLXRvb2xzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module09-intro-custom-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

---

## Official References

- **Google ADK Custom Tools:** https://adk.dev/tools-custom/
- **Google ADK Function Tools:** https://adk.dev/tools-custom/function-tools/
- **Google Gemini API Function Calling:** https://ai.google.dev/gemini-api/docs/function-calling
