"""Sovereign Horizon Bank - Corporate Market & Adverse Intelligence Radar.

Programmatic Execution & Grounding Metadata Extraction.
Builds on Module 6 (InMemoryRunner) to capture full citation lineage under
Federal Reserve SR 11-7 model risk management guidelines.

PEDAGOGICAL ARCHITECTURE (No Black Boxes):
1. Typed Data Contracts: Pydantic schemas enforce type safety for banking databases.
2. Defensive Extraction: Null-safe navigation of GenAI GroundingMetadata.
3. Async Runner Loop: Captures streaming events and extracts from final response.
"""

import asyncio
import os
import sys
from pathlib import Path

# Automatically load .env for Vertex AI / Gemini Enterprise configuration
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    with open(_env_file, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from agent import market_intelligence_agent
from google.adk.events import Event
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel, Field

# ============================================================================
# 1. TYPED AUDIT SCHEMAS (PEP 585 / PEP 604)
# ============================================================================
# Why Pydantic instead of raw dictionaries?
# - Dicts (res["sources"][0]["url"]) cause silent KeyErrors in production.
# - Pydantic provides type hints, IDE autocomplete, and validation.
# - `Field(default_factory=list)` prevents Python's mutable default list bug.


class GroundedSource(BaseModel):
    """Source URL and publication title extracted from grounding metadata."""

    title: str = Field(description="Web page or publication title")
    url: str = Field(description="Canonical URL of cited source")


class GroundedAuditReport(BaseModel):
    """Audit-compliant intelligence report with full citation lineage."""

    entity_name: str = Field(description="Corporate entity or borrower investigated")
    briefing_text: str = Field(
        description="Synthesized human-readable intelligence report"
    )
    search_queries: list[str] = Field(
        default_factory=list,
        description="Autonomous search queries executed by Gemini",
    )
    sources: list[GroundedSource] = Field(
        default_factory=list,
        description="Authoritative web sources cited in the response",
    )


# ============================================================================
# 2. DEFENSIVE METADATA EXTRACTION LOGIC
# ============================================================================
# Why defensive coding?
# - If Gemini answers from memory without searching, `grounding_metadata` is None.
# - Direct access (event.grounding_metadata.web_search_queries) would crash with AttributeError.
# - In hybrid enterprise search, a chunk might not be a web chunk; we check `chunk.web`.


def extract_grounding_audit(
    entity_name: str, final_text: str, event: Event
) -> GroundedAuditReport:
    """Extract search queries and cited URLs from an ADK Event's grounding metadata.

    Args:
        entity_name: The company being researched.
        final_text: The synthesized briefing text from event.content.
        event: The final ADK Event containing grounding_metadata.

    Returns:
        GroundedAuditReport: Fully populated, strongly-typed audit record.
    """
    queries: list[str] = []
    sources: list[GroundedSource] = []

    # Defensive Guard 1: Check if grounding metadata exists on this turn
    if event.grounding_metadata:
        # Defensive Guard 2: Extract queries formulated by Gemini
        if event.grounding_metadata.web_search_queries:
            queries = list(event.grounding_metadata.web_search_queries)

        # Defensive Guard 3: Extract retrieved web chunks and canonical URLs
        if event.grounding_metadata.grounding_chunks:
            for chunk in event.grounding_metadata.grounding_chunks:
                # Ensure the chunk has a web component with a valid URL
                if chunk.web and chunk.web.uri:
                    sources.append(
                        GroundedSource(
                            title=chunk.web.title or "Web Reference",
                            url=chunk.web.uri,
                        )
                    )

    return GroundedAuditReport(
        entity_name=entity_name,
        briefing_text=final_text,
        search_queries=queries,
        sources=sources,
    )


# ============================================================================
# 3. ASYNC RUNNER EXECUTION
# ============================================================================
# Executes the agent programmatically via InMemoryRunner and captures the
# final response event for metadata harvesting.


async def run_grounded_research(entity_name: str) -> GroundedAuditReport:
    """Execute the grounded agent programmatically via InMemoryRunner.

    Args:
        entity_name: The borrower to screen.

    Returns:
        GroundedAuditReport with text and verified citations.
    """
    app_name = "adverse_intelligence_app"
    runner = InMemoryRunner(agent=market_intelligence_agent, app_name=app_name)

    # 1. Initialize session with clean slugified ID
    session_id = f"audit_{entity_name.lower().replace(' ', '_')}"
    await runner.session_service.create_session(
        app_name=app_name,
        user_id="credit_analyst_01",
        session_id=session_id,
    )

    prompt = (
        f"Investigate commercial borrower '{entity_name}' for regulatory"
        " enforcement actions, active lawsuits, fraud indictments, or sanctions."
    )

    final_text = ""
    last_final_event: Event | None = None

    # 2. Stream events from runner
    async for event in runner.run_async(
        user_id="credit_analyst_01",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ):
        # 3. Filter for the final response event
        # Why is_final_response()? Intermediate events contain streaming tokens.
        # Only the final event contains the consolidated text and complete metadata.
        if event.is_final_response():
            last_final_event = event
            if event.content and event.content.parts:
                final_text = "".join(
                    part.text for part in event.content.parts if part.text
                )

    if last_final_event is None:
        raise RuntimeError("No final response event received from agent.")

    # 4. Harvest metadata into structured audit report
    return extract_grounding_audit(entity_name, final_text, last_final_event)


# ============================================================================
# 4. ENTRYPOINT DEMONSTRATION & HOW TO MAKE THIS AGENT GENERIC
# ============================================================================
# PEDAGOGICAL GUIDE FOR LEARNERS & FDE CONSULTANTS:
#
# By default below, we investigate "Acme Industrial Corp" so you can run
# `uv run python main.py` immediately and verify the audit output.
#
# However, in real client projects, you will want this agent to accept ANY
# company dynamically. Here are 3 enterprise ways to make this generic:
#
# ----------------------------------------------------------------------------
# PATTERN 1: Command-Line Argument (Active by default below!)
# ----------------------------------------------------------------------------
# You can pass any borrower name directly in your terminal command:
#   uv run python main.py "Rio Tinto"
#   uv run python main.py "Commonwealth Bank of Australia"
#   uv run python main.py "Boeing"
#
# ----------------------------------------------------------------------------
# PATTERN 2: Interactive Terminal Input (Uncomment to enable prompt mode)
# ----------------------------------------------------------------------------
# If you want the script to pause and ask the credit analyst for input:
#
#   user_input = input("\n🏢 Enter borrower / company name to screen: ").strip()
#   entity = user_input if user_input else "Acme Industrial Corp"
#
# ----------------------------------------------------------------------------
# PATTERN 3: Freeform Natural Language Prompt (REST API / Webhook Integration)
# ----------------------------------------------------------------------------
# To expose this agent inside a FastAPI backend, Cloud Run microservice, or Slack bot:
# Replace the static prompt template in `run_grounded_research` with the incoming
# user message (e.g. `request.body.prompt`), allowing analysts to ask:
# "Check whether Supplier X settled any EPA wastewater citations in 2025."
# ============================================================================


async def main():
    # ------------------------------------------------------------------------
    # STEP 1: Determine the target entity (CLI argument or default)
    # ------------------------------------------------------------------------
    if len(sys.argv) > 1:
        # Dynamically accepts command line args: `uv run python main.py "Company Name"`
        entity = " ".join(sys.argv[1:]).strip()
        print(f"📌 [CLI MODE] Detected dynamic borrower argument: '{entity}'")
    else:
        # Default baseline entity for one-click testing
        entity = "Acme Industrial Corp"

    # ------------------------------------------------------------------------
    # [LEARNER EXERCISE: UNCOMMENT BELOW FOR INTERACTIVE PROMPT MODE]
    # ------------------------------------------------------------------------
    # To test interactive on-demand input, uncomment the next 3 lines:
    # prompt_input = input("\n🏢 Enter company name to investigate [Press Enter for Acme Industrial Corp]: ").strip()
    # if prompt_input:
    #     entity = prompt_input

    print(f"\n🔍 [GROUNDING RADAR] Investigating borrower: {entity}...")
    report = await run_grounded_research(entity)

    print("\n" + "=" * 60)
    print("🏛️ EXECUTIVE ADVERSE INTELLIGENCE BRIEFING")
    print("=" * 60)
    print(report.briefing_text)

    print("\n" + "=" * 60)
    print("🔎 VERIFIED CITATION LINEAGE (FED SR 11-7 AUDIT TRAIL)")
    print("=" * 60)
    print(f"Executed Search Queries ({len(report.search_queries)}):")
    for q in report.search_queries:
        print(f"  • {q}")

    print(f"\nAuthoritative Web Sources ({len(report.sources)}):")
    for src in report.sources:
        print(f"  • [{src.title}]({src.url})")


if __name__ == "__main__":
    asyncio.run(main())
