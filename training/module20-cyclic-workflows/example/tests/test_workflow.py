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

def always_incomplete(node_input: dict) -> dict:
    return {"case_id": "CASE-001", "evidence_ids": [], "summary": "Draft for review"}


def malformed(node_input: dict) -> dict:
    return {"approved": True}


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def result(self, writer=None):
        events = await run_once(build_agent(writer), SAMPLE)
        return [e.output for e in events if e.output is not None][-1]

    async def test_revises_then_accepts_only_for_human_review(self):
        result = await self.result()
        self.assertEqual(result["status"], "ready_for_human_review")
        self.assertEqual(len(result["history"]), 2)

    async def test_budget_exhaustion_has_no_accepted_memo(self):
        result = await self.result(always_incomplete)
        self.assertEqual(result["status"], "needs_manual_review")
        self.assertEqual(len(result["history"]), 3)
        self.assertNotIn("memo", result)

    async def test_malformed_output_is_manual_review(self):
        self.assertEqual((await self.result(malformed))["status"], "invalid_model_output")
