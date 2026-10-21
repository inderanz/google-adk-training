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


class ServerTests(unittest.TestCase):
    def test_only_validated_case_fields_leave_specialist(self):
        from bank_case.server import review_checklist
        result = review_checklist(CaseRequest.model_validate(SAMPLE))
        self.assertEqual(set(result.output), {"case_id", "documents_complete", "source"})

    def test_remote_proxy_constructs_without_a_network_call(self):
        self.assertEqual(build_agent().name, "remote_checklist_client")
