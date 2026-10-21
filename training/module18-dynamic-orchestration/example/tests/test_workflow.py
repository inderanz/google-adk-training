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
    async def test_optional_check_runs_only_when_required(self):
        for cents, expected in ((20_000_000, ["documents"]),
                                (20_000_001, ["documents", "exposure"])):
            events = await run_once(build_agent(), SAMPLE | {"requested_cents": cents})
            result = [e.output for e in events if e.output is not None][-1]
            self.assertEqual([item["check"] for item in result["checks"]], expected)
