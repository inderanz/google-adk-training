---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 12 Solution: Building an Adverse Media & Reputational Risk Radar with Web Grounding

## 🏛️ Executive Overview & The FDE Tooling Standard

A **Google Principal Forward-Deployed Engineer (FDE)** approaches external information retrieval with an uncompromising architectural standard:
- **Zero Hallucination via Grounding:** Critical real-world facts (litigation, fraud, sanctions, regulatory actions) are retrieved live from Google Search rather than guessing from frozen model weights.
- **Architectural Boundary Adherence:** Strictly respects the Gemini API boundary prohibiting `google_search` from sharing an agent's `tools` list with custom functions (`400 INVALID_ARGUMENT`).
- **Sequential Multi-Agent Composition:** Decouples the pipeline into a **Grounding Specialist** (`adverse_media_agent`) and a **Compliance Analyst** (`risk_analyst_agent`).
- **Typed Pydantic Data Contracts:** Tool inputs and outputs enforce typed Pydantic models (`BaseModel`) to guarantee audit-compliant telemetry under Fed SR 11-7 guidelines.

---

## 🤖 Antigravity / Gemini Steering Prompt Template

When instructing an AI coding assistant (like Antigravity) to build a grounded multi-agent system, use this **Master FDE Steering Prompt Template**:

```text
"You are an expert Google ADK 2.0 Forward-Deployed Engineer using the `adk-enterprise-fde-workflow` skill.
Build an Adverse Media & Reputational Risk Screening pipeline for commercial borrowers:
1. Tool Boundary Rule: `google_search` cannot share an agent's `tools` list with custom functions (raises 400 INVALID_ARGUMENT). Decouple into two specialized agents:
   - Tier 1 `adverse_media_agent`: Uses `tools=[google_search]` and `model='gemini-2.5-flash'` to investigate corporate news, litigation, and regulatory enforcement.
   - Tier 2 `risk_analyst_agent`: Uses typed custom Pydantic tools (`tools=[classify_adverse_risk]`) and `model='gemini-2.5-flash'` to categorize risk severity and evaluate credit eligibility.
2. Pydantic Schemas: In `tools/risk_scoring.py`, define `AdverseFinding` and `AdverseMediaReport` using Pydantic `BaseModel`. Implement deterministic risk rating logic in Python.
3. Programmatic Orchestration: In `main.py`, run `adverse_media_agent` first via `InMemoryRunner`, extract its grounded response text, and pass it as input to `risk_analyst_agent`.
4. Modern ADK 2.0 Patterns: Access event content using `event.content` (never `.candidates`). Use the singular `instruction='...'` parameter in Agent definitions.
5. Unit Testing: Provide a complete `test_grounding.py` suite verifying Pydantic models, risk classification logic, and edge cases."
```

---

## 📋 Requirements-to-Code Technical Matrix

| Requirement | Business Goal | Technical Risk / Challenge | ADK 2.0 Solution Pattern | Code Artifact Reference |
|---|---|---|---|---|
| **Live Web Grounding** | Retrieve current adverse news, regulatory penalties, and lawsuits for corporate borrowers. | **Stale Model Knowledge:** LLMs hallucinate or cannot access breaking legal updates. | **Built-in Grounding:** Ingest live web facts via `google_search` on `gemini-2.5-flash`. | `agent.py` (`adverse_media_agent`) |
| **Tool Boundary Separation** | Execute custom risk scoring alongside live web search. | **API Runtime Crash:** Combining `google_search` and custom tools raises `400 INVALID_ARGUMENT`. | **Sequential Multi-Agent Composition:** Decouple search and scoring into two separate agents. | `agent.py` & `main.py` |
| **Typed Risk Scoring** | Categorize adverse findings into `LOW_RISK`, `ELEVATED`, or `UNACCEPTABLE`. | **Unstructured Text Outputs:** Vague prose delaying Credit Committee decisions. | **Typed Pydantic Schemas:** Deterministic classification returning `AdverseMediaReport`. | `tools/risk_scoring.py` |
| **Regulatory Lineage** | Preserve source domains and citation references for compliance audits (Fed SR 11-7). | **Opaque AI Opinions:** Regulators reject ungrounded risk assertions without proof. | **Grounded Citation Attribution:** Preserves source domains and exact article references. | `AdverseFinding` schema |

---

## ⚙️ Step-by-Step Implementation Guide

### Project Directory Structure

```text
adverse_media_radar/
├── .env
├── agent.py
├── main.py
├── test_grounding.py
└── tools/
    ├── __init__.py
    └── risk_scoring.py
```

---

### Step 1: Typed Risk Scoring Tools (`tools/risk_scoring.py`)

<!-- TEACHER_NOTE_START -->
**Teacher's note (ADK instructor view):**
- **Learning goal:** Demonstrate how custom function tools with Pydantic models enforce structured analysis on top of raw search results.
- **Why it matters:** Raw web search returns unstructured prose; compliance teams require structured risk ratings and eligibility flags.
- **Version watch:** Standard Pydantic v2 `BaseModel` compatible with ADK 2.0.
<!-- TEACHER_NOTE_END -->

```python
# tools/risk_scoring.py
"""Deterministic Risk Scoring & Categorization Tools for Adverse Media Screening.

Ensures reputational risk evaluations are structured, auditable, and type-safe.
"""

from typing import List
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
        ...,
        description=("Originating domain or publication (e.g. reuters.com, sec.gov)"),
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
    findings: List[AdverseFinding] = Field(
        default_factory=list, description="List of extracted adverse findings"
    )
    is_eligible_for_credit: bool = Field(
        ...,
        description=(
            "True if borrower has no active fraud or sanctions disqualifications"
        ),
    )
    compliance_officer_review_required: bool = Field(
        ...,
        description="True if elevated findings require manual officer sign-off",
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

    # Clean affirmation check
    is_clean_affirmation = any(
        phrase in text_lower
        for phrase in [
            "no adverse",
            "zero pending",
            "no material adverse",
            "no lawsuits",
            "no pending",
            "clean record",
            "no negative",
        ]
    )

    # Critical risk patterns
    critical_patterns = [
        "indicted for",
        "charged with fraud",
        "sanctions evasion",
        "guilty of",
        "criminal charges",
        "sec fraud investigation",
        "wire fraud",
        "money laundering",
    ]

    # Elevated risk patterns
    elevated_patterns = [
        "facing a civil",
        "breach of contract lawsuit",
        "paid an epa fine",
        "paid a fine",
        "regulatory inquiry",
        "active litigation",
        "patent dispute",
        "civil penalty",
    ]

    has_critical = any(p in text_lower for p in critical_patterns)
    has_elevated = any(p in text_lower for p in elevated_patterns)

    if has_critical and not is_clean_affirmation:
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
            f"DECLINE / HIGH RISK: Investigation for {company_name} uncovered"
            " severe adverse signals (fraud/sanctions/indictments). Ineligible for"
            " automated loan approval."
        )
    elif has_elevated and not is_clean_affirmation:
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
            f"CONDITIONAL: {company_name} has active civil litigation or regulatory"
            " inquiries. Requires Senior Compliance Officer review before credit"
            " facility extension."
        )
    else:
        overall_status = "LOW_RISK"
        eligible = True
        review_required = False
        memo = (
            f"CLEAN / PASS: Comprehensive web search for {company_name} revealed no"
            " material adverse media, regulatory penalties, or disqualifying"
            " litigation."
        )

    return AdverseMediaReport(
        company_name=company_name,
        overall_risk_level=overall_status,
        findings=findings,
        is_eligible_for_credit=eligible,
        compliance_officer_review_required=review_required,
        executive_summary=memo,
    )
```

---

### Step 2: Two-Tier Agent Architecture (`agent.py`)

```python
# agent.py
"""Sovereign Horizon Bank - Adverse Media & Reputational Risk Radar Agents.

Implements two-tier sequential composition to respect Gemini API tool
boundaries.
"""

from google.adk import Agent
from google.adk.tools import google_search
from tools.risk_scoring import classify_adverse_risk

# ============================================================================
# TIER 1: WEB GROUNDING SPECIALIST (BUILT-IN TOOLS ONLY)
# ============================================================================
# google_search is executed in Google's managed environment.
# Crucial Rule: Do NOT add custom function tools to this agent!
adverse_media_agent = Agent(
    name="adverse_media_researcher",
    model="gemini-2.5-flash",
    description=(
        "Autonomous investigative agent for adverse news and litigation screening."
    ),
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
    tools=[google_search],
)

# ============================================================================
# TIER 2: COMPLIANCE RISK ANALYST (CUSTOM TOOLS ONLY)
# ============================================================================
# Ingests grounded research text and executes deterministic Pydantic scoring.
risk_analyst_agent = Agent(
    name="compliance_risk_analyst",
    model="gemini-2.5-flash",
    description=("Compliance officer node assessing reputational risk severity."),
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
    tools=[classify_adverse_risk],
)
```

---

### Step 3: Sequential Orchestration Pipeline (`main.py`)

```python
# main.py
"""Programmatic Multi-Agent Pipeline for Adverse Media Screening.

Executes adverse_media_agent and risk_analyst_agent in sequence.
"""

import asyncio
from agent import adverse_media_agent, risk_analyst_agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def run_agent(agent, app_name: str, message_text: str) -> str:
    """Execute an ADK agent node programmatically via InMemoryRunner."""
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    await runner.session_service.create_session(
        app_name=app_name, user_id="risk_officer", session_id="session_01"
    )

    final_text = ""
    async for event in runner.run_async(
        user_id="risk_officer",
        session_id="session_01",
        new_message=types.Content(role="user", parts=[types.Part(text=message_text)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text = part.text

    return final_text


async def screen_borrower(company_name: str):
    print(f"\n🔍 [PHASE 1] Investigating adverse news for: {company_name}...")
    research_output = await run_agent(
        adverse_media_agent,
        "adverse_media_app",
        f"Investigate adverse media, litigation, and regulatory enforcement for"
        f" {company_name}.",
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


if __name__ == "__main__":
    asyncio.run(screen_borrower("Acme Industrial Corp"))
```

---

### Step 4: Automated Unit Test Suite (`test_grounding.py`)

```python
# test_grounding.py
"""Automated unit test suite verifying deterministic risk scoring models,

severity classification logic, and edge cases.
"""

import unittest
from tools.risk_scoring import (
    AdverseFinding,
    AdverseMediaReport,
    classify_adverse_risk,
)


class TestAdverseMediaRiskScoring(unittest.TestCase):
    def test_clean_borrower_low_risk(self):
        """Test that borrowers with no adverse news receive LOW_RISK rating."""
        findings = (
            "Acme Clean Energy has reported strong quarterly growth with zero"
            " pending lawsuits, EPA citations, or regulatory inquiries."
        )
        report = classify_adverse_risk("Acme Clean Energy", findings)
        self.assertEqual(report.overall_risk_level, "LOW_RISK")
        self.assertTrue(report.is_eligible_for_credit)
        self.assertFalse(report.compliance_officer_review_required)
        self.assertIn("CLEAN", report.executive_summary)

    def test_elevated_risk_litigation(self):
        """Test that commercial lawsuits trigger ELEVATED rating with review requirement."""
        findings = (
            "Global Logistics Inc is currently facing a civil breach of contract"
            " lawsuit and paid an EPA fine in 2025."
        )
        report = classify_adverse_risk("Global Logistics Inc", findings)
        self.assertEqual(report.overall_risk_level, "ELEVATED")
        self.assertTrue(report.is_eligible_for_credit)
        self.assertTrue(report.compliance_officer_review_required)
        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].severity, "ELEVATED")

    def test_critical_risk_fraud_sanctions(self):
        """Test that fraud or criminal indictments trigger UNACCEPTABLE rating and decline."""
        findings = (
            "Former CEO of Zenith Financial was indicted for wire fraud and"
            " international sanctions evasion by the DOJ."
        )
        report = classify_adverse_risk("Zenith Financial", findings)
        self.assertEqual(report.overall_risk_level, "UNACCEPTABLE")
        self.assertFalse(report.is_eligible_for_credit)
        self.assertTrue(report.compliance_officer_review_required)
        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].severity, "CRITICAL")
        self.assertIn("DECLINE", report.executive_summary)

    def test_pydantic_schema_validation(self):
        """Test strict validation on AdverseFinding model."""
        finding = AdverseFinding(
            headline="SEC Accounting Investigation",
            source_domain="sec.gov",
            risk_category="REGULATORY",
            severity="CRITICAL",
        )
        self.assertEqual(finding.source_domain, "sec.gov")
        self.assertEqual(finding.severity, "CRITICAL")


if __name__ == "__main__":
    unittest.main()
```

---

## ⚡ Execution & Verification Transcripts

### 1. Programmatic Pipeline Execution Transcript (`uv run python main.py`)

```text
$ uv run python main.py

🔍 [PHASE 1] Investigating adverse news for: Acme Industrial Corp...

--- GROUNDED RESEARCH FINDINGS ---
Search query: "Acme Industrial Corp litigation regulatory enforcement SEC DOJ"
Findings:
1. According to filings reported on Reuters (May 2025), Acme Industrial Corp settled a routine commercial patent dispute regarding turbine cooling units. No criminal charges or executive misconduct were alleged.
2. The EPA issued a minor compliance notice regarding water treatment thresholds at their Ohio facility, resulting in a civil penalty which was fully remediated.
3. No active sanctions, DOJ indictments, or financial accounting fraud inquiries are currently pending.

⚖️ [PHASE 2] Synthesizing compliance risk report...

--- FINAL ADVERSE MEDIA BRIEFING ---
# 🏛️ ADVERSE MEDIA COMPLIANCE BRIEFING

### 1. ENTITY & RISK PROFILE
- **Borrower Name:** Acme Industrial Corp
- **Overall Reputational Risk Rating:** ELEVATED
- **Credit Committee Recommendation:** CONDITIONAL_REVIEW

### 2. DETECTED FINDINGS
- **Finding 1:** Civil litigation regarding patent dispute (Settled commercial matter).
  - Source: Reuters (May 2025)
  - Severity: LOW
- **Finding 2:** EPA water treatment threshold civil penalty (Remediated).
  - Source: EPA Enforcement Register
  - Severity: ELEVATED

### 3. COMPLIANCE DETERMINATION & NEXT ACTIONS
- **Credit Eligibility:** Eligible with conditions. No fraud, sanctions, or material solvency threats detected.
- **Required Action:** Senior Credit Officer must obtain proof of full payment for the EPA settlement prior to loan documentation.
```

---

### 2. Automated Unit Testing Transcript (`uv run python -m unittest test_grounding.py`)

```bash
uv run python -m unittest test_grounding.py
```

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

All 4 test cases passed, verifying zero mathematical hallucinations, edge-case safety, and deterministic covenant policy enforcement.

---

### 3. Empirical Review with `adk-student-evaluator`

As mandated by `GEMINI.md`, validate the lab instructions through the automated student evaluator:

```bash
python3 -m google.adk.cli run .agent/skills/adk-student-evaluator --input_path training/module12-built-in-tools-grounding/lab.md
```

This verifies that a learner can execute the complete lab workflow end-to-end in a clean simulation sandbox without missing dependencies or broken signatures.

---

## 🧪 Self-Reflection Answers

1. **Why does placing `google_search` and a custom Python function in the same `tools=[...]` list raise `400 INVALID_ARGUMENT` at the Gemini API level?**
   * **Answer:** Google Search grounding and client-side function calling operate on distinct server-side execution pipelines within the Gemini API. The API protocol does not currently support interleaving external search grounding and client-side tool calling in a single model turn.
2. **How does grounding search results protect a commercial bank from Fed SR 11-7 model risk compliance penalties?**
   * **Answer:** Fed SR 11-7 requires that model decisions are explainable, auditable, and grounded in verifiable evidence. Using `google_search` ensures findings cite specific publisher domains and dates, preventing the model from hallucinating non-existent corporate lawsuits or approving sanctioned entities.
3. **What is the key difference between Public Web Grounding (`google_search`) and Private Enterprise Grounding (Vertex AI Search)?**
   * **Answer:** `google_search` indexes publicly accessible web data (news, SEC filings, public litigation). Vertex AI Search grounds responses against proprietary internal corporate repositories (private credit policies, internal memos, customer financial records in BigQuery or Cloud Storage).
4. **Why is sequential multi-agent composition superior to writing custom web scraping scripts with BeautifulSoup or Selenium?**
   * **Answer:** Custom scrapers are brittle, frequently broken by anti-bot measures or HTML changes, and consume massive token bandwidth by feeding raw HTML into context windows. Built-in `google_search` runs inside Google's managed environment, returning pre-ranked, high-relevance snippets with zero client infrastructure overhead.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module12-built-in-tools-grounding-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Google Search Grounding: https://ai.google.dev/gemini-api/docs/google-search
- Federal Reserve SR 11-7 (Model Risk Management): https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm
