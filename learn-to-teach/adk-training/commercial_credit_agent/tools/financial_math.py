"""
tools/financial_math.py
Deterministic Financial Calculation Tools for Commercial Credit Underwriting.
Guarantees zero arithmetic hallucinations by executing ratios in Python runtime.
"""

from typing import List
from pydantic import BaseModel, Field

# ============================================================================
# 1. TYPED PYDANTIC RETURN SCHEMAS
# ============================================================================

class DscrResult(BaseModel):
    """Result of Debt Service Coverage Ratio (DSCR) calculation."""
    dscr_ratio: float = Field(..., description="Calculated DSCR ratio (NOI / Total Debt Service)")
    is_compliant: bool = Field(..., description="True if ratio meets bank covenant threshold (>= 1.25x)")
    threshold: float = Field(default=1.25, description="Bank policy covenant threshold")
    assessment: str = Field(..., description="Qualitative rating: STRONG, COMPLIANT, BORDERLINE, or DEFICIT")


class DebtToEbitdaResult(BaseModel):
    """Result of Debt-to-EBITDA leverage calculation."""
    leverage_ratio: float = Field(..., description="Calculated leverage ratio (Total Debt / EBITDA)")
    is_compliant: bool = Field(..., description="True if leverage is below maximum ceiling (<= 3.5x)")
    max_threshold: float = Field(default=3.5, description="Maximum permitted leverage ratio")
    assessment: str = Field(..., description="Qualitative rating: CONSERVATIVE, ACCEPTABLE, or OVERLEVERAGED")


class CovenantEvaluationResult(BaseModel):
    """Consolidated credit policy and covenant compliance evaluation."""
    overall_status: str = Field(..., description="Final decision: PASS, BORDERLINE_SENIOR_REVIEW, or DECLINE")
    is_approved: bool = Field(..., description="True if eligible for Credit Committee submission")
    requires_senior_officer_review: bool = Field(..., description="True if borderline DSCR requires HITL sign-off")
    dscr: float = Field(..., description="Evaluated DSCR")
    debt_to_ebitda: float = Field(..., description="Evaluated Debt-to-EBITDA")
    violations: List[str] = Field(default_factory=list, description="List of policy violations or covenant breaches")
    credit_memo_summary: str = Field(..., description="Executive summary for the Credit Committee")


# ============================================================================
# 2. DETERMINISTIC CALCULATION TOOLS (ADK 2.0 COMPLIANT)
# ============================================================================

def calculate_dscr(net_operating_income: float, total_debt_service: float) -> DscrResult:
    """Calculate the Debt Service Coverage Ratio (DSCR).

    Formula: Net Operating Income (NOI) / Annual Debt Service.
    Bank Covenant Policy: Minimum 1.25x for standard commercial facilities.
    """
    if total_debt_service <= 0:
        return DscrResult(
            dscr_ratio=999.0,
            is_compliant=True,
            assessment="STRONG: Zero debt service obligations."
        )

    ratio = round(net_operating_income / total_debt_service, 2)

    if ratio >= 1.40:
        rating = "STRONG: Robust cash flow buffer exceeding covenant."
    elif ratio >= 1.25:
        rating = "COMPLIANT: Satisfies minimum covenant requirement."
    elif ratio >= 1.15:
        rating = "BORDERLINE: Requires Senior Credit Officer risk exception review."
    else:
        rating = "DEFICIT: Insufficient cash flow to service debt."

    return DscrResult(
        dscr_ratio=ratio,
        is_compliant=(ratio >= 1.25),
        assessment=rating
    )


def calculate_debt_to_ebitda(total_debt: float, ebitda: float) -> DebtToEbitdaResult:
    """Calculate the corporate leverage ratio (Total Debt / EBITDA).

    Bank Covenant Policy: Maximum 3.5x leverage ceiling.
    """
    if ebitda <= 0:
        return DebtToEbitdaResult(
            leverage_ratio=999.0,
            is_compliant=False,
            assessment="OVERLEVERAGED: Negative or zero operating EBITDA."
        )

    ratio = round(total_debt / ebitda, 2)

    if ratio <= 2.5:
        rating = "CONSERVATIVE: Low leverage, well below policy ceiling."
    elif ratio <= 3.5:
        rating = "ACCEPTABLE: Compliant with maximum leverage covenant."
    else:
        rating = "OVERLEVERAGED: Breaches maximum policy ceiling."

    return DebtToEbitdaResult(
        leverage_ratio=ratio,
        is_compliant=(ratio <= 3.5),
        assessment=rating
    )


def evaluate_covenant_policy(
    dscr: float,
    debt_to_ebitda: float,
    current_ratio: float = 1.3,
    watchlist_flag: bool = False,
    restricted_industry: bool = False
) -> CovenantEvaluationResult:
    """Evaluate financial metrics and negative risk signals against bank credit covenants."""
    violations = []

    # Hard Policy Rejection 1: Restricted Industry
    if restricted_industry:
        violations.append("Borrower operates in an ineligible or restricted industry.")
        return CovenantEvaluationResult(
            overall_status="DECLINE",
            is_approved=False,
            requires_senior_officer_review=False,
            dscr=dscr,
            debt_to_ebitda=debt_to_ebitda,
            violations=violations,
            credit_memo_summary="DECLINE: Application rejected due to restricted industry exclusion."
        )

    # Hard Policy Rejection 2: Watchlist Flag
    if watchlist_flag:
        violations.append("Borrower is currently on internal Watchlist or Special Assets monitor.")
        return CovenantEvaluationResult(
            overall_status="DECLINE",
            is_approved=False,
            requires_senior_officer_review=False,
            dscr=dscr,
            debt_to_ebitda=debt_to_ebitda,
            violations=violations,
            credit_memo_summary="DECLINE: Borrower is active on the Special Assets Watchlist."
        )

    # Financial Covenant Checks
    if dscr < 1.15:
        violations.append(f"DSCR of {dscr}x severely breaches minimum covenant of 1.25x.")
    if debt_to_ebitda > 3.5:
        violations.append(f"Debt-to-EBITDA of {debt_to_ebitda}x exceeds maximum leverage of 3.5x.")
    if current_ratio < 1.2:
        violations.append(f"Current Ratio of {current_ratio}x is below liquidity requirement of 1.2x.")

    # Status Determination
    if violations:
        return CovenantEvaluationResult(
            overall_status="DECLINE",
            is_approved=False,
            requires_senior_officer_review=False,
            dscr=dscr,
            debt_to_ebitda=debt_to_ebitda,
            violations=violations,
            credit_memo_summary=f"DECLINE: Covenant violations detected: {'; '.join(violations)}"
        )

    # Borderline DSCR Check (Human-in-the-Loop Checkpoint)
    if 1.15 <= dscr < 1.25:
        return CovenantEvaluationResult(
            overall_status="BORDERLINE_SENIOR_REVIEW",
            is_approved=False,
            requires_senior_officer_review=True,
            dscr=dscr,
            debt_to_ebitda=debt_to_ebitda,
            violations=["DSCR (1.15x - 1.25x) is in borderline exception range."],
            credit_memo_summary="CONDITIONAL_REVIEW: Borderline DSCR requires Senior Credit Officer exception approval."
        )

    # Clean Approval
    return CovenantEvaluationResult(
        overall_status="PASS",
        is_approved=True,
        requires_senior_officer_review=False,
        dscr=dscr,
        debt_to_ebitda=debt_to_ebitda,
        violations=[],
        credit_memo_summary="APPROVE_FOR_COMMITTEE: All debt covenants and leverage tests fully compliant."
    )
