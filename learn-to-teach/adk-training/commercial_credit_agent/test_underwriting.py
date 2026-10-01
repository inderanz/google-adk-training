"""
test_underwriting.py
Automated unit test suite verifying deterministic financial calculation tools
and credit policy covenant evaluations.
"""

import unittest

from commercial_credit_agent.tools.financial_math import (
    calculate_debt_to_ebitda,
    calculate_dscr,
    evaluate_covenant_policy,
)
try:
    from commercial_credit_agent.tools.financial_math import (
        calculate_debt_to_ebitda,
        calculate_dscr,
        evaluate_covenant_policy,
    )
except ImportError:
    from tools.financial_math import (
        calculate_debt_to_ebitda,
        calculate_dscr,
        evaluate_covenant_policy,
    )


class TestCommercialUnderwritingTools(unittest.TestCase):
    def test_dscr_strong_pass(self):
        """Test robust cash flow exceeding 1.25x covenant."""
        result = calculate_dscr(
            net_operating_income=3200000, total_debt_service=2100000
        )
        self.assertEqual(result.dscr_ratio, 1.52)
        self.assertTrue(result.is_compliant)
        self.assertIn("STRONG", result.assessment)

    def test_dscr_borderline(self):
        """Test borderline DSCR (1.20x) requiring Senior Officer review."""
        result = calculate_dscr(
            net_operating_income=2400000, total_debt_service=2000000
        )
        self.assertEqual(result.dscr_ratio, 1.20)
        self.assertFalse(result.is_compliant)  # Covenant minimum is 1.25x
        self.assertIn("BORDERLINE", result.assessment)

    def test_dscr_zero_debt_service(self):
        """Test edge case where borrower has zero existing debt service."""
        result = calculate_dscr(net_operating_income=1000000, total_debt_service=0)
        self.assertEqual(result.dscr_ratio, 999.0)
        self.assertTrue(result.is_compliant)

    def test_leverage_compliant(self):
        """Test corporate leverage ratio below 3.5x maximum threshold."""
        result = calculate_debt_to_ebitda(total_debt=8000000, ebitda=3000000)
        self.assertEqual(result.leverage_ratio, 2.67)
        self.assertTrue(result.is_compliant)

    def test_leverage_overleveraged(self):
        """Test corporate leverage ratio exceeding 3.5x maximum threshold."""
        result = calculate_debt_to_ebitda(total_debt=12000000, ebitda=3000000)
        self.assertEqual(result.leverage_ratio, 4.0)
        self.assertFalse(result.is_compliant)

    def test_covenant_clean_pass(self):
        """Test complete pass across all credit covenants."""
        result = evaluate_covenant_policy(
            dscr=1.45, debt_to_ebitda=2.5, current_ratio=1.4
        )
        self.assertEqual(result.overall_status, "PASS")
        self.assertTrue(result.is_approved)
        self.assertFalse(result.requires_senior_officer_review)
        self.assertEqual(len(result.violations), 0)

    def test_covenant_borderline_escalation(self):
        """Test borderline case (DSCR 1.20x) triggering Senior Officer HITL checkpoint."""
        result = evaluate_covenant_policy(
            dscr=1.20, debt_to_ebitda=2.8, current_ratio=1.3
        )
        self.assertEqual(result.overall_status, "BORDERLINE_SENIOR_REVIEW")
        self.assertFalse(result.is_approved)
        self.assertTrue(result.requires_senior_officer_review)

    def test_covenant_watchlist_hard_decline(self):
        """Test borrower on Watchlist triggering immediate decline regardless of ratios."""
        result = evaluate_covenant_policy(
            dscr=2.0, debt_to_ebitda=1.5, watchlist_flag=True
        )
        self.assertEqual(result.overall_status, "DECLINE")
        self.assertFalse(result.is_approved)
        self.assertIn("Watchlist", result.credit_memo_summary)

    def test_covenant_restricted_industry_decline(self):
        """Test borrower in restricted industry triggering immediate decline."""
        result = evaluate_covenant_policy(
            dscr=1.8, debt_to_ebitda=1.8, restricted_industry=True
        )
        self.assertEqual(result.overall_status, "DECLINE")
        self.assertFalse(result.is_approved)
        self.assertIn("restricted industry", result.credit_memo_summary)


class TestLegacyOpenAPINormalizer(unittest.TestCase):
    def setUp(self):
        import os

        self.legacy_file = os.path.join(
            os.path.dirname(__file__), "openapi", "legacy_raw_spec.json"
        )

    def test_normalizer_populates_missing_operation_ids_and_subsets(self):
        """Test that legacy endpoints without operationIds are normalized and admin routes stripped."""
        import json

        from commercial_credit_agent.openapi.normalizer import load_and_normalize_spec
        try:
            from commercial_credit_agent.openapi.normalizer import load_and_normalize_spec
        except ImportError:
            from openapi.normalizer import load_and_normalize_spec

        clean_json_str = load_and_normalize_spec(
            self.legacy_file, allowed_path_patterns=[r"^/v1/borrowers/"]
        )
        spec = json.loads(clean_json_str)

        # 1. Verify admin/internal routes are stripped
        self.assertNotIn("/admin/purge-cache", spec["paths"])
        self.assertNotIn("/internal/system-health-dump", spec["paths"])

        # 2. Verify allowed routes remain
        self.assertIn("/v1/borrowers/{tax_id}/exposure", spec["paths"])
        self.assertIn("/v1/borrowers/{tax_id}/risk-profile", spec["paths"])

        # 3. Verify operationId was auto-generated cleanly
        exposure_op = spec["paths"][
            "v1/borrowers/{tax_id}/exposure"
            if "v1/borrowers/{tax_id}/exposure" in spec["paths"]
            else "/v1/borrowers/{tax_id}/exposure"
        ]["get"]
        self.assertEqual(exposure_op["operationId"], "get_borrower_exposure")
        self.assertTrue(exposure_op["parameters"][0]["required"])

        risk_op = spec["paths"][
            "v1/borrowers/{tax_id}/risk-profile"
            if "v1/borrowers/{tax_id}/risk-profile" in spec["paths"]
            else "/v1/borrowers/{tax_id}/risk-profile"
        ]["get"]
        self.assertEqual(risk_op["operationId"], "get_borrower_risk_profile")


if __name__ == "__main__":
    unittest.main()
