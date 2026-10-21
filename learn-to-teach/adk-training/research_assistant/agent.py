"""Sovereign Horizon Bank - Corporate Market & Adverse Intelligence Radar Agent.

Equipped with Google Search Grounding for real-time due diligence.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

# ============================================================================
# GROUNDED RESEARCH AGENT CONFIGURATION
# ============================================================================
# Google Search Grounding is a built-in server-side tool in Gemini 2.0+.
# Note: google_search CANNOT share an agent's tools list with custom function tools!
market_intelligence_agent = Agent(
    name="market_intelligence_agent",
    model="gemini-2.5-flash",
    description=(
        "Autonomous corporate intelligence researcher with live Google Search"
        " grounding."
    ),
    instruction="""
You are a Senior Corporate Intelligence Analyst at Sovereign Horizon Bank.
When investigating a commercial borrower or corporate entity:
1. Perform targeted searches for active regulatory enforcement (SEC, DOJ, EPA, FTC, OCC),
   commercial lawsuits, breach of contract claims, executive fraud, or trade sanctions.
2. Structure your briefing with:
   - Entity Name & Investigation Date
   - Regulatory & Litigation Findings (with dates and source names)
   - Operational or Leadership Risk Indicators
   - Overall Compliance Risk Assessment (LOW_RISK, ELEVATED, or UNACCEPTABLE)
3. If no adverse news, legal dockets, or regulatory fines are detected, clearly
   confirm that a comprehensive search revealed no material adverse signals.
""",
    tools=[google_search],
)

# Root agent export for ADK CLI discovery (e.g. `adk run .` or `adk web .`)
root_agent = market_intelligence_agent
