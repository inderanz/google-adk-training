"""Exercise native ADK composition; service transports are controlled fixtures."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch
from bank_review.capstone import build_capstone
from bank_review import case_repository
from verify_capstone import verify
from support import ScriptedModel, call, text, invoke, results


class Inspector:
    def __init__(self, decision="allow"):
        self.decision = decision

    async def inspect(self, text, response=False):
        return self.decision

    async def close(self):
        pass


class CapstoneTests(unittest.IsolatedAsyncioTestCase):
    def record(self):
        return {"assigned_analyst_id": "analyst-a", "borrower_name": "Acme",
                "version": 7, "documents": {"financial_statements": True,
                                           "ownership_register": False}}

    async def execute(self, reader, user="analyst-a", case_id="CASE-001"):
        model = ScriptedModel(replies=[call("prepare_case", case_id=case_id), text("Review required")])
        with patch("bank_review.case_repository.read_case", new=reader):
            return await invoke(build_capstone(model, Inspector()), user=user)

    async def test_authorized_record_is_preserved_in_exact_artifact(self):
        # Reuse the actual repository authorization/shape function, replacing only I/O.
        async def read(case_id, user):
            return case_repository.summarize_case(self.record(), case_id, user)
        events, session, store = await self.execute(read)
        result = results(events)[0]
        self.assertEqual(result["next_step"], "collect_documents")
        self.assertEqual(result["case_version"], 7)
        self.assertEqual(result["decision_owner"], "human_analyst")
        scope = dict(app_name="bank_review", user_id="analyst-a", session_id=session.id)
        source = await store.load_artifact(**scope, filename=result["pack"]["source"]["filename"],
                                           version=result["pack"]["source"]["version"])
        saved = json.loads(source.inline_data.data)
        self.assertEqual(saved["case_version"], 7)
        self.assertEqual(saved["observed_at"], result["observed_at"])
        self.assertEqual(result["pack"]["source"]["version"], 0)
        self.assertIn("last_review_invocation", session.state)
        # Exercise the deployed-report readback algorithm with real saved objects.
        # Only its GCS transport is replaced here; a live GCS result is separate.
        report = {"cases": [{"id": "allowed", "user_id": "analyst-a",
                  "session_id": session.id,
                  "events": [event.model_dump(mode="json") for event in events]}]}
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.json"
            report_path.write_text(json.dumps(report))
            with patch.dict(os.environ, {"ARTIFACT_BUCKET": "fixture"}), patch(
                    "verify_capstone.GcsArtifactService", return_value=store):
                verified = await verify(str(report_path))
                self.assertEqual(verified["status"], "verified_from_gcs")


    async def test_denied_user_writes_no_artifacts(self):
        async def read(case_id, user):
            return case_repository.summarize_case(self.record(), case_id, user)
        events, session, store = await self.execute(read, user="another-user")
        self.assertEqual(results(events)[0]["status"], "not_found")
        self.assertEqual(await store.list_artifact_keys(app_name="bank_review",
                         user_id="another-user", session_id=session.id), [])

    async def test_unavailable_and_unknown_do_not_become_success(self):
        reader = AsyncMock(side_effect=TimeoutError())
        events, _, _ = await self.execute(reader)
        self.assertEqual(results(events)[0]["status"], "unavailable")
        reader.reset_mock()
        events, _, _ = await self.execute(reader, case_id="CASE-999")
        self.assertEqual(results(events)[0]["status"], "not_found")
        reader.assert_not_awaited()

    async def test_blocked_input_never_reads_case(self):
        reader = AsyncMock(side_effect=AssertionError("Database must not be reached"))
        with patch("bank_review.case_repository.read_case", new=reader):
            events, session, _ = await invoke(build_capstone(ScriptedModel(replies=[]), Inspector("block")),
                                              prompt="synthetic blocked content")
        reader.assert_not_awaited()
        self.assertNotIn("synthetic blocked content", session.model_dump_json())

    async def test_complete_checklist_routes_only_to_human_review(self):
        record = self.record()
        record["documents"]["ownership_register"] = True
        async def read(case_id, user):
            return case_repository.summarize_case(record, case_id, user)
        events, _, _ = await self.execute(read)
        self.assertEqual(results(events)[0]["next_step"], "human_review")
        self.assertEqual(results(events)[0]["missing_documents"], [])
