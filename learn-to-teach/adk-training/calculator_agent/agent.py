from google.adk import Agent

from .tools.calculator import (
    add,
    calculate_gst_invoice,
    divide,
    multiply,
    subtract,
)

root_agent = Agent(
    name="calculator_agent",
    model="gemini-2.5-flash",
    description="A calculator agent that can perform basic arithmetic operations and calculate GST invoices.",
    instruction="""
You are a helpful and precise calculator assistant.
When the user asks you to perform an arithmetic calculation or calculate a GST invoice, you MUST use the appropriate tool.
Always state the calculated result clearly.
If a tool returns an error (such as division by zero), explain the problem politely without crashing.
If the user asks something unrelated to math or billing, politely decline.
""",
    tools=[add, subtract, multiply, divide, calculate_gst_invoice],
)
