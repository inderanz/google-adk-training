"""
agent.py
Sovereign Horizon Bank - Adverse Media & Reputational Risk Radar Agents.
Implements two-tier sequential composition to respect Gemini API tool boundaries.
"""

from google.adk import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="researcher_agent",
    model="gemini-3.5-flash",
    model="gemini-2.5-flash",
    instruction="You are a research assistant that can answer questions and provide information on a wide range of topics. You have access to a Google Search tool to help you find information online.",
    description="You are a research assistant that can answer questions and provide information on a wide range of topics. You have access to a Google Search tool to help you find information online.",
    tools=[google_search],
)
try:
    from researcher_agent.tools.risk_scoring import classify_adverse_risk
except ImportError:
    from tools.risk_scoring import classify_adverse_risk

# ============================================================================
# TIER 1: WEB GROUNDING SPECIALIST (BUILT-IN TOOLS ONLY)
# ============================================================================
# google_search is executed in Google's managed environment.
# Crucial Rule: Do NOT add custom function tools to this agent!
adverse_media_agent = Agent(
    name="adverse_media_researcher",
    model="gemini-2.5-flash",
    description="Autonomous investigative agent for adverse news and litigation screening.",
    instruction="""
You are an expert investigative corporate risk researcher at Sovereign Horizon Bank.
When given a corporate borrower name, use google_search to investigate:
1. Active regulatory investigations (SEC, DOJ, EPA, FTC, OCC).
2. Major commercial lawsuits or breach of contract disputes.
3. Executive fraud, embezzlement, or criminal indictments.
4. International trade or sanctions watchlist notices.

Synthesize all discovered facts with explicit dates and news source names.
If no negative information is found, explicitly confirm that no adverse signals were detected.
""",
    tools=[google_search]
)

# ============================================================================
# TIER 2: COMPLIANCE RISK ANALYST (CUSTOM TOOLS ONLY)
# ============================================================================
# Ingests grounded research text and executes deterministic Pydantic scoring.
risk_analyst_agent = Agent(
    name="compliance_risk_analyst",
    model="gemini-2.5-flash",
    description="Compliance officer node assessing reputational risk severity.",
    instruction="""
You are a Senior Credit & Compliance Risk Officer at Sovereign Horizon Bank.
The user will provide a company name and research findings retrieved from web grounding.

Execution Protocol:
1. Call `classify_adverse_risk` with the company name and research findings.
2. Based on the returned report, synthesize a formal "🏛️ ADVERSE MEDIA COMPLIANCE BRIEFING" containing:
   - Company Name & Overall Risk Rating (LOW_RISK, ELEVATED, or UNACCEPTABLE)
   - Credit Committee Recommendation (APPROVE, CONDITIONAL_REVIEW, or DECLINE)
   - Key Adverse Findings & Citations
   - Compliance Officer Next Actions
""",
    tools=[classify_adverse_risk]
)

# Root agent export for ADK CLI
root_agent = adverse_media_agent