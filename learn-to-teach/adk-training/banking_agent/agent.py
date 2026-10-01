from google.adk import Agent
from .tools.banking import (
    set_customer_preference,
    get_customer_profile,
    submit_loan_application,
    update_loan_draft,
)

root_agent = Agent(
    name="banking_agent",
    model="gemini-2.5-flash",
    description="An enterprise banking assistant capable of caching customer preferences and processing multi-turn loan applications.",
    instruction="""
You are a professional enterprise retail banking assistant.

Tool Steering Rules:
1. Use 'set_customer_preference' whenever the user mentions language or branch preferences.
2. Use 'get_customer_profile' when the user asks about their stored profile, account info, or preferences.
3. Use 'update_loan_draft' turn-by-turn as the user provides loan details (name, income, amount, tenure).
   - After updating, check 'missing_fields' in the response and politely ask the user for the next missing detail.
4. Use 'submit_loan_application' ONLY when all details are captured AND the user explicitly confirms submission.

Maintain a polite, secure, and professional tone at all times.

""",
    tools=[
        set_customer_preference,
        get_customer_profile,
        update_loan_draft,
        submit_loan_application,
    ],
)
