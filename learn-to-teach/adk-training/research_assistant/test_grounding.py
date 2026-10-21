"""Automated test suite verifying deterministic risk scoring models,
severity classification logic, and edge cases.
"""Automated unit test suite verifying grounded agent configuration,
metadata extraction parsing, and boundary conditions.

Compatible with pytest, unittest, and direct Python execution.
Compatible with unittest, pytest, and direct execution.
"""

from tools.risk_scoring import (
    AdverseFinding,
    AdverseMediaReport,
    classify_adverse_risk,
)
import unittest
from agent import market_intelligence_agent
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai import types
from main import GroundedAuditReport, GroundedSource, extract_grounding_audit


def test_clean_borrower_low_risk():
    """Test that borrowers with no adverse news receive LOW_RISK rating."""
    findings = (
        "Acme Clean Energy has reported strong quarterly growth with zero"
        " pending lawsuits, EPA citations, or regulatory inquiries."
    )
    report = classify_adverse_risk("Acme Clean Energy", findings)
    assert report.overall_risk_level == "LOW_RISK"
    assert report.is_eligible_for_credit is True
    assert report.compliance_officer_review_required is False
    assert "CLEAN" in report.executive_summary
class TestGroundingRadar(unittest.TestCase):
    """Test suite for Market & Adverse Intelligence Grounded Agent."""

    def test_agent_configuration(self):
        """Verify market_intelligence_agent properties and tool assignment."""
        self.assertEqual(market_intelligence_agent.name, "market_intelligence_agent")
        self.assertEqual(market_intelligence_agent.model, "gemini-2.5-flash")

def test_elevated_risk_litigation():
    """Test that commercial lawsuits trigger ELEVATED rating with review requirement."""
    findings = (
        "Global Logistics Inc is currently facing a civil breach of contract"
        " lawsuit and paid an EPA fine in 2025."
    )
    report = classify_adverse_risk("Global Logistics Inc", findings)
    assert report.overall_risk_level == "ELEVATED"
    assert report.is_eligible_for_credit is True
    assert report.compliance_officer_review_required is True
    assert len(report.findings) == 1
    assert report.findings[0].severity == "ELEVATED"
        # Verify google_search is properly registered in tools
        self.assertIn(google_search, market_intelligence_agent.tools)
        # Verify the coexistence boundary: only search tools are permitted
        self.assertEqual(len(market_intelligence_agent.tools), 1)

    def test_metadata_extraction_parsing(self):
        """Verify that GroundingMetadata fields are accurately parsed into GroundedAuditReport."""
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

def test_critical_risk_fraud_sanctions():
    """Test that fraud or criminal indictments trigger UNACCEPTABLE rating and decline."""
    findings = (
        "Former CEO of Zenith Financial was indicted for wire fraud and"
        " international sanctions evasion by the DOJ."
    )
    report = classify_adverse_risk("Zenith Financial", findings)
    assert report.overall_risk_level == "UNACCEPTABLE"
    assert report.is_eligible_for_credit is False
    assert report.compliance_officer_review_required is True
    assert len(report.findings) == 1
    assert report.findings[0].severity == "CRITICAL"
    assert "DECLINE" in report.executive_summary
        mock_event = Event(
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text="Briefing text content.")],
            ),
            grounding_metadata=mock_metadata,
        )

        report = extract_grounding_audit(
            entity_name="Acme Industrial Corp",
            final_text="Briefing text content.",
            event=mock_event,
        )

def test_pydantic_schema_validation():
    """Test strict validation on AdverseFinding model."""
    finding = AdverseFinding(
        headline="SEC Accounting Investigation",
        source_domain="sec.gov",
        risk_category="REGULATORY",
        severity="CRITICAL",
    )
    assert finding.source_domain == "sec.gov"
    assert finding.severity == "CRITICAL"
        self.assertIsInstance(report, GroundedAuditReport)
        self.assertEqual(report.entity_name, "Acme Industrial Corp")
        self.assertEqual(report.briefing_text, "Briefing text content.")
        self.assertEqual(len(report.search_queries), 2)
        self.assertEqual(report.search_queries[0], "Acme Corp SEC litigation 2026")
        self.assertEqual(len(report.sources), 2)
        self.assertEqual(report.sources[0].title, "SEC Litigation Release No. 25100")
        self.assertIn("sec.gov", report.sources[0].url)

    def test_empty_grounding_metadata_handling(self):
        """Verify graceful fallback when no grounding metadata is present."""
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
    test_clean_borrower_low_risk()
    test_elevated_risk_litigation()
    test_critical_risk_fraud_sanctions()
    test_pydantic_schema_validation()
    print("All tests passed successfully!")
    unittest.main()
