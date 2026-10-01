---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 9: Building a "Calculator" Agent Challenge

## Goal

In this lab, you will build an agent that can perform deterministic calculations. You will create custom Python function tools, handle edge cases defensively, and integrate them into an ADK 2.0 agent node.

---

### Step 1: Create the Project and File Structure

<Setup/>

1. **Create the agent project:**
   ```bash
   uv run adk create calculator_agent
   cd calculator_agent
   ```

2. **Set up authentication:**
   Create a `.env` file in your `calculator_agent` directory and add your `GOOGLE_API_KEY`:
   ```bash
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Create the tools package:**
   Organizing tool code in a dedicated module keeps your agent architecture modular and clean:
   ```bash
   mkdir tools
   touch tools/__init__.py
   touch tools/calculator.py
   ```

---

### Step 2: Implement the Tool Functions

Open `tools/calculator.py` and implement the tool functions. Pay close attention to docstrings and type hints—they define the schema contract that Gemini inspects.

#### Part A: Core Arithmetic Tools
Implement the basic arithmetic functions with defensive error handling for division:

```python
# In tools/calculator.py


def add(a: float, b: float) -> dict:
    """Adds two numbers together.

    Use this tool when the user asks to find the sum of two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    # TODO: Calculate the sum of a and b.
    # Return a dictionary: {"status": "success", "result": a + b}
    pass


def subtract(a: float, b: float) -> dict:
    """Subtracts the second number from the first number.

    Use this tool when the user asks to find the difference between two numbers.

    Args:
        a: The first number.
        b: The second number to subtract.
    """
    # TODO: Calculate the difference (a - b).
    # Return a dictionary: {"status": "success", "result": a - b}
    pass


def multiply(a: float, b: float) -> dict:
    """Multiplies two numbers together.

    Use this tool when the user asks to find the product of two numbers.

    Args:
        a: The first number.
        b: The second number to multiply.
    """
    # TODO: Calculate the product (a * b).
    # Return a dictionary: {"status": "success", "result": a * b}
    pass


def divide(a: float, b: float) -> dict:
    """Divides the first number by the second number.

    Use this tool when the user asks to divide one number by another.

    Args:
        a: The numerator.
        b: The denominator.
    """
    # TODO: Implement defensive error handling!
    # If b == 0, DO NOT let Python raise ZeroDivisionError.
    # Return: {"status": "error", "message": "Cannot divide by zero."}
    # Otherwise, return: {"status": "success", "result": a / b}
    pass
```

#### Part B: Enterprise Real-World Challenge (GST Invoicing)
In enterprise AI consulting, clients rely on tools to calculate financial numbers deterministically instead of letting the LLM hallucinate math.

Add a GST tax calculation tool to `tools/calculator.py`:

```python
def calculate_gst_invoice(amount: float, tax_rate_percent: float = 18.0) -> dict:
    """Calculates an itemized GST invoice including CGST, SGST, and the total payable amount.

    Use this tool whenever a user asks to calculate GST, tax, or an invoice total for a purchase.

    Args:
        amount: The base pre-tax amount in rupees (INR) or currency.
        tax_rate_percent: The GST tax slab percentage (defaults to 18.0%).
    """
    # TODO: Calculate tax amounts:
    # 1. Total GST = amount * (tax_rate_percent / 100.0)
    # 2. CGST (Central GST) = Total GST / 2.0
    # 3. SGST (State GST) = Total GST / 2.0
    # 4. Total Payable = amount + Total GST
    # Return a structured dictionary with these itemized values.
    pass
```

> [!TIP]
> **Pydantic Best Practice:** While dictionaries work for basic tools, in production ADK agents you should return **Pydantic models** (`BaseModel`) for strict type validation. See `lab-solution.md` for the Pydantic implementation.

---

### Step 3: Configure the Agent Node

Create `agent.py` and register your functions using the ADK 2.0 **`Agent`** class:

```python
# In agent.py
from google.adk import Agent
from .tools.calculator import (
    add,
    subtract,
    multiply,
    divide,
    calculate_gst_invoice,
)

root_agent = Agent(
    name="calculator_agent",
    model="gemini-2.5-flash",
    description="A deterministic calculation assistant for arithmetic and GST billing.",
    instruction="""
You are a helpful and precise calculator assistant.
When the user asks you to perform an arithmetic calculation or calculate a GST invoice, you MUST use the appropriate tool.
Always state the calculated result clearly.
If a tool returns an error (such as division by zero), explain the problem politely without crashing.
If the user asks something unrelated to math or billing, politely decline.
""",
    # TODO: Register all 5 imported tool functions in this list:
    tools=[
        # add your functions here
    ],
)
```

---

### Step 4: Test and Verify the Agent

#### 1. Interactive Terminal Mode
Start the agent using the ADK CLI:

```bash
uv run adk run .
```

Test across each capability:
* **Addition:** `"What is 42.5 + 118.3?"`
* **Multiplication:** `"Multiply 15 by 3"`
* **Defensive Error Test:** `"What is 10 divided by 0?"` $\rightarrow$ Verify the agent politely explains that division by zero is impossible without crashing!
* **Enterprise GST Invoicing:** `"Calculate the GST bill for an order of ₹25,000 at 18% tax"` $\rightarrow$ Verify it breaks down CGST, SGST, and the total bill.
* **Out-of-Scope Refusal:** `"What is the capital of France?"` $\rightarrow$ Verify it politely declines as instructed.

#### 2. Visual Trace Inspection
To visually confirm that Gemini generated the `FunctionCall` and your Python function returned the `FunctionResponse`:

```bash
uv run adk web .
```
Open your browser at `http://localhost:8000`, send a calculation prompt, and click the **Trace** tab to inspect the tool execution events.

---

### Having Trouble?

If you get stuck, you can find the complete, working code and configuration in the `lab-solution.md` file.

### Lab Summary

You have successfully built an agent with custom capabilities:
* Organized tool code cleanly into a dedicated Python module.
* Wrote well-defined Python functions with type hints and docstrings to serve as LLM tool contracts.
* Implemented defensive error handling to prevent runtime crashes.
* Imported and registered your custom tools directly into the ADK 2.0 `Agent` node.
* Tested agent reasoning and verified execution traces via the terminal and Web UI.

### Self-Reflection Questions
1. The docstring for each function is critical. What do you think would happen if you removed the docstrings from your calculator functions? Would the agent still be able to use them?
2. Why is it a good practice to return a dictionary or Pydantic model with a `status` key from a tool function, especially for operations that can fail (like division)?
3. How would you add a new tool to this agent, for example, a function to calculate compound interest? What steps would you need to take?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDktaW50cm8tY3VzdG9tLWZ1bmN0aW9uLXRvb2xzL2xhYi1zb2x1dGlvbg==`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module09-intro-custom-function-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module09-intro-custom-function-tools-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts
