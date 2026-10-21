import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from google.adk.artifacts import InMemoryArtifactService
from bank_review.agent import build_app
from bank_review.tools import SOURCE_NAME, json_part
from support import ScriptedModel, call, text, invoke, results


class ArtifactTests(unittest.IsolatedAsyncioTestCase):
    async def test_readback_program_uses_report_scope_and_versions(self):
        from verify_pack import verify
        model = ScriptedModel(replies=[call("save_checklist"),
            call("create_review_pack", source_version=0), text("Fixture report ready")])
        events, session, store = await invoke(build_app(model))
        report = {"cases": [{"id": "pack", "user_id": "analyst-a", "session_id": session.id,
                             "events": [event.model_dump(mode="json") for event in events]}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"report.json"
            path.write_text(json.dumps(report))
            with patch("verify_pack.GcsArtifactService", return_value=store), patch.dict("os.environ", {"ARTIFACT_BUCKET": "fixture"}):
                result = await verify(str(path))
                self.assertEqual(result["source"]["version"], 0)
                report["cases"][0]["user_id"] = "another-user"
                path.write_text(json.dumps(report))
                with self.assertRaisesRegex(AssertionError, "manifest"):
                    await verify(str(path))

    async def test_pack_uses_exact_saved_version(self):
        model = ScriptedModel(replies=[call("save_checklist"),
            call("create_review_pack", source_version=0), text("Fixture report ready")])
        events, session, store = await invoke(build_app(model))
        outcome = results(events)[-1]
        self.assertEqual(outcome["status"], "prepared_for_human_review")
        scope = dict(app_name="bank_review", user_id="analyst-a", session_id=session.id)
        report = await store.load_artifact(**scope, filename=outcome["report"]["filename"], version=0)
        self.assertIn(b"ownership_register", report.inline_data.data)
        old = await store.load_artifact(**scope, filename=SOURCE_NAME, version=0)
        revised = json.loads(old.inline_data.data)
        revised["documents"]["ownership_register"] = True
        version = await store.save_artifact(**scope, filename=SOURCE_NAME, artifact=json_part(revised))
        self.assertEqual(version, 1)
        again = await store.load_artifact(**scope, filename=SOURCE_NAME, version=0)
        self.assertEqual(again.inline_data.data, old.inline_data.data)
        other = await store.load_artifact(**(scope | {"user_id": "analyst-b"}), filename=SOURCE_NAME)
        self.assertIsNone(other)

    async def test_missing_source_never_creates_a_pack(self):
        model = ScriptedModel(replies=[call("create_review_pack", source_version=0), text("Missing")])
        events, session, store = await invoke(build_app(model))
        self.assertEqual(results(events)[0]["status"], "source_missing")
        self.assertEqual(await store.list_artifact_keys(app_name="bank_review", user_id="analyst-a", session_id=session.id), [])

    async def test_negative_version_rejected(self):
        model = ScriptedModel(replies=[call("create_review_pack", source_version=-1), text("Invalid")])
        events, _, _ = await invoke(build_app(model))
        self.assertEqual(results(events)[0]["status"], "invalid_version")
