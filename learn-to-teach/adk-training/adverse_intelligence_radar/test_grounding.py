"""Automated unit test suite verifying grounded agent configuration,
metadata extraction parsing, and boundary conditions.

Compatible with unittest, pytest, and direct execution.
"""

import unittest
from agent import market_intelligence_agent
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai import types
from main import GroundedAuditReport, GroundedSource, extract_grounding_audit


class TestGroundingRadar(unittest.TestCase):
    """Test suite for Market & Adverse Intelligence Grounded Agent."""

    def test_agent_configuration(self):
        """Verify market_intelligence_agent properties and tool assignment."""
        self.assertEqual(market_intelligence_agent.name, "market_intelligence_agent")
        self.assertEqual(market_intelligence_agent.model, "gemini-2.5-flash")

        # Verify google_search is properly registered in tools
        self.assertIn(google_search, market_intelligence_agent.tools)
        # Verify the coexistence boundary: only search tools are permitted
        self.assertEqual(len(market_intelligence_agent.tools), 1)

    def test_metadata_extraction_parsing(self):
        """Verify that GroundingMetadata fields are accurately parsed into GroundedAuditReport."""
        # 1. Construct synthetic grounding metadata matching the Gemini schema
        mock_metadata = types.GroundingMetadata(
            web_search_queries=[
                "Acme Corp SEC litigation 2026",
                "Acme Industrial EPA penalties",
            ],
            grounding_chunks=[
                types.GroundingChunk(
                    web=types.GroundingChunkWeb(
                        title="SEC Litigation Release No. 25100",
                        uri="https://sec.gov/litigation/releases/2026/lr25100.htm",
                    )
                ),
                types.GroundingChunk(
                    web=types.GroundingChunkWeb(
                        title="EPA Enforcement Compliance Docket",
                        uri="https://epa.gov/enforcement/acme-ohio-docket",
                    )
                ),
            ],
        )

        # 2. Wrap in an ADK Event object
        mock_event = Event(
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text="Briefing text content.")],
            ),
            grounding_metadata=mock_metadata,
        )

        # 3. Execute extraction logic
        report = extract_grounding_audit(
            entity_name="Acme Industrial Corp",
            final_text="Briefing text content.",
            event=mock_event,
        )

        # 4. Assert correctness
        self.assertIsInstance(report, GroundedAuditReport)
        self.assertEqual(report.entity_name, "Acme Industrial Corp")
        self.assertEqual(report.briefing_text, "Briefing text content.")
        self.assertEqual(len(report.search_queries), 2)
        self.assertEqual(report.search_queries[0], "Acme Corp SEC litigation 2026")
        self.assertEqual(len(report.sources), 2)
        self.assertEqual(report.sources[0].title, "SEC Litigation Release No. 25100")
        self.assertIn("sec.gov", report.sources[0].url)

    def test_empty_grounding_metadata_handling(self):
        """Verify graceful fallback when no grounding metadata is present (e.g. direct answer)."""
        mock_event = Event(
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text="Direct answer with no search.")],
            ),
            grounding_metadata=None,
        )

        report = extract_grounding_audit(
            entity_name="Generic LLC",
            final_text="Direct answer with no search.",
            event=mock_event,
        )

        # Ensure graceful fallback: empty lists, zero runtime exceptions
        self.assertEqual(report.entity_name, "Generic LLC")
        self.assertEqual(report.search_queries, [])
        self.assertEqual(report.sources, [])

    def test_pydantic_schema_validation(self):
        """Verify type safety of GroundedSource model."""
        source = GroundedSource(
            title="Reuters Legal News",
            url="https://reuters.com/legal/article-123",
        )
        self.assertEqual(source.title, "Reuters Legal News")
        self.assertTrue(source.url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()

