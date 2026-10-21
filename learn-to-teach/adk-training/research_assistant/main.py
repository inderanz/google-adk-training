"""Programmatic Multi-Agent Pipeline for Adverse Media Screening.
"""Programmatic Execution & Grounding Metadata Extraction.

Executes adverse_media_agent and risk_analyst_agent in sequence.
Builds on Module 6 (InMemoryRunner) to capture full citation lineage under
Federal Reserve SR 11-7 model risk management guidelines.
"""

import asyncio
from agent import adverse_media_agent, risk_analyst_agent
from agent import market_intelligence_agent
from google.adk.events import Event
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel, Field

# ============================================================================
# 1. TYPED AUDIT SCHEMAS (PEP 585 / PEP 604)
# ============================================================================

async def run_agent(agent, app_name: str, message_text: str) -> str:
    """Execute an ADK agent node programmatically via InMemoryRunner."""
    runner = InMemoryRunner(agent=agent, app_name=app_name)

class GroundedSource(BaseModel):
    """Source URL and publication title extracted from grounding metadata."""

    title: str = Field(description="Web page or publication title")
    url: str = Field(description="Canonical URL of cited source")


class GroundedAuditReport(BaseModel):
    """Audit-compliant intelligence report with full citation lineage."""

    entity_name: str
    briefing_text: str
    search_queries: list[str] = Field(
        default_factory=list,
        description="Autonomous search queries executed by Gemini",
    )
    sources: list[GroundedSource] = Field(
        default_factory=list,
        description="Authoritative web sources cited in the response",
    )


# ============================================================================
# 2. METADATA EXTRACTION LOGIC
# ============================================================================


def extract_grounding_audit(
    entity_name: str, final_text: str, event: Event
) -> GroundedAuditReport:
    """Extract search queries and cited URLs from an ADK Event's grounding metadata."""
    """Extract search queries and cited URLs from an ADK Event grounding metadata."""
    queries: list[str] = []
    sources: list[GroundedSource] = []

    if event.grounding_metadata:
        # 1. Extract dynamic search queries formulated by Gemini
        if event.grounding_metadata.web_search_queries:
            queries = list(event.grounding_metadata.web_search_queries)

        # 2. Extract retrieved web chunks and canonical URLs
        if event.grounding_metadata.grounding_chunks:
            for chunk in event.grounding_metadata.grounding_chunks:
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


async def run_grounded_research(entity_name: str) -> GroundedAuditReport:
    """Execute the grounded agent programmatically via InMemoryRunner."""
    app_name = "adverse_intelligence_app"
    runner = InMemoryRunner(agent=market_intelligence_agent, app_name=app_name)

    session_id = f"audit_{entity_name.lower().replace(' ', '_')}"
    await runner.session_service.create_session(
        app_name=app_name, user_id="risk_officer", session_id="session_01"
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

    async for event in runner.run_async(
        user_id="risk_officer",
        session_id="session_01",
        user_id="credit_analyst_01",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=message_text)],
            parts=[types.Part.from_text(text=prompt)],
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(part.text for part in event.content.parts if part.text)
        if event.is_final_response():
            last_final_event = event
            if event.content and event.content.parts:
                final_text = "".join(
                    part.text for part in event.content.parts if part.text
                )

    return final_text
    if last_final_event is None:
        raise RuntimeError("No final response event received from agent.")

    return extract_grounding_audit(entity_name, final_text, last_final_event)

async def screen_borrower(company_name: str):
    print(f"\n🔍 [PHASE 1] Investigating adverse news for: {company_name}...")
    research_output = await run_agent(
        adverse_media_agent,
        "adverse_media_app",
        f"Investigate adverse media, litigation, and regulatory enforcement for {company_name}.",
    )
    print("\n--- GROUNDED RESEARCH FINDINGS ---")
    print(research_output)

    print(f"\n⚖️ [PHASE 2] Synthesizing compliance risk report...")
    final_briefing = await run_agent(
        risk_analyst_agent,
        "risk_analyst_app",
        f"Borrower: {company_name}\n\nResearch Findings:\n{research_output}",
    )
    print("\n--- FINAL ADVERSE MEDIA BRIEFING ---")
    print(final_briefing)
async def main():
    entity = "Acme Industrial Corp"
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
    asyncio.run(screen_borrower("Acme Industrial Corp"))
    asyncio.run(main())
