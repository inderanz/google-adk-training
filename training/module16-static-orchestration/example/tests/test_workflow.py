import unittest
from pydantic import ValidationError
from bank_case.contracts import CaseRequest, SAMPLE
from bank_case.agent import build_agent
from runtime import run_once


class ContractTests(unittest.TestCase):
    def test_rejects_untrusted_types_and_extra_fields(self):
        for change in ({"requested_cents": True}, {"requested_cents": 1.5},
                       {"requested_cents": 0}, {"requested_cents": 100_000_001},
                       {"documents_complete": "yes"}, {"case_id": "OTHER"},
                       {"approved": True}):
            with self.subTest(change=change), self.assertRaises(ValidationError):
                CaseRequest.model_validate(SAMPLE | change)

    def test_contract_accepts_documented_limits(self):
        for amount in (1, 20_000_000, 20_000_001, 100_000_000):
            self.assertEqual(CaseRequest.model_validate(SAMPLE | {"requested_cents": amount}).requested_cents, amount)

class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_join_contains_both_independent_results(self):
        events = await run_once(build_agent(), SAMPLE)
        result = [e.output for e in events if e.output is not None][-1]
        self.assertEqual(len(result["evidence"]), 2)
        self.assertFalse(result["evidence"][0]["documents_complete"])
        self.assertTrue(result["evidence"][1]["specialist_review"])

    def test_mismatched_case_is_not_combined(self):
        from bank_case.agent import combine
        with self.assertRaises(ValueError):
            combine({"document_check": {"case_id": "A"}, "exposure_check": {"case_id": "B"}})
