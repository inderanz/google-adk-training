"""
tools/risk_scoring.py
Deterministic Risk Scoring & Categorization Tools for Adverse Media Screening.
Ensures reputational risk evaluations are structured, auditable, and type-safe.
"""

from pydantic import BaseModel, Field

# ============================================================================
# 1. TYPED PYDANTIC RETURN SCHEMAS
# ============================================================================


class AdverseFinding(BaseModel):
    """Single adverse risk finding extracted from grounded search results."""

    headline: str = Field(
        ..., description="Short summary of the adverse event or litigation"
    )
    source_domain: str = Field(
        ..., description="Originating domain or publication (e.g. reuters.com, sec.gov)"
    )
    risk_category: str = Field(
        ..., description="LITIGATION, REGULATORY, FRAUD, SANCTIONS, or ESG"
    )
    severity: str = Field(..., description="Severity level: CRITICAL, ELEVATED, or LOW")


class AdverseMediaReport(BaseModel):
    """Consolidated adverse media and reputational risk assessment report."""

    company_name: str = Field(
        ..., description="Name of the corporate borrower investigated"
    )
    overall_risk_level: str = Field(
        ..., description="Overall risk rating: LOW_RISK, ELEVATED, or UNACCEPTABLE"
    )
    findings: list[AdverseFinding] = Field(
        default_factory=list, description="List of extracted adverse findings"
    )
    is_eligible_for_credit: bool = Field(
        ...,
        description="True if borrower has no active fraud or sanctions disqualifications",
    )
    compliance_officer_review_required: bool = Field(
        ..., description="True if elevated findings require manual officer sign-off"
    )
    executive_summary: str = Field(
        ..., description="Executive compliance briefing for the Credit Committee"
    )


# ============================================================================
# 2. DETERMINISTIC RISK EVALUATION TOOL (ADK 2.0 COMPLIANT)
# ============================================================================


def classify_adverse_risk(
    company_name: str, raw_findings_summary: str
) -> AdverseMediaReport:
    """Analyze research findings and categorize the corporate borrower's reputational risk level."""
    text_lower = raw_findings_summary.lower()
    findings = []

    # Detection patterns for critical risk
    critical_keywords = [
        "fraud",
        "indictment",
        "sanction",
        "embezzlement",
        "criminal charges",
        "sec fraud",
    ]
    elevated_keywords = [
        "lawsuit",
        "fine",
        "litigation",
        "epa violation",
        "breach of contract",
        "regulatory inquiry",
    ]

    has_critical = any(kw in text_lower for kw in critical_keywords)
    has_elevated = any(kw in text_lower for kw in elevated_keywords)

    if has_critical:
        overall_status = "UNACCEPTABLE"
        eligible = False
        review_required = True
        findings.append(
            AdverseFinding(
                headline="Severe criminal, fraud, or sanctions allegations detected",
                source_domain="verified_news_index",
                risk_category="FRAUD",
                severity="CRITICAL",
            )
        )
        memo = (
            f"DECLINE / HIGH RISK: Investigation for {company_name} uncovered severe adverse signals "
            f"(fraud/sanctions/indictments). Ineligible for automated loan approval."
        )
    elif has_elevated:
        overall_status = "ELEVATED"
        eligible = True
        review_required = True
        findings.append(
            AdverseFinding(
                headline="Civil litigation or regulatory fines on record",
                source_domain="verified_news_index",
                risk_category="REGULATORY",
                severity="ELEVATED",
            )
        )
        memo = (
            f"CONDITIONAL: {company_name} has active civil litigation or regulatory inquiries. "
            f"Requires Senior Compliance Officer review before credit facility extension."
        )
    else:
        overall_status = "LOW_RISK"
        eligible = True
        review_required = False
        memo = (
            f"CLEAN / PASS: Comprehensive web search for {company_name} revealed no material adverse media, "
            f"regulatory penalties, or disqualifying litigation."
        )

    return AdverseMediaReport(
        company_name=company_name,
        overall_risk_level=overall_status,
        findings=findings,
        is_eligible_for_credit=eligible,
        compliance_officer_review_required=review_required,
        executive_summary=memo,
    )
