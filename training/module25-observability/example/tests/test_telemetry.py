import asyncio
import unittest
from bank_review.agent import build_app
from support import ScriptedModel, call, text, invoke, results


class TelemetryTests(unittest.IsolatedAsyncioTestCase):
    async def test_failure_is_recovered_as_unavailable(self):
        model = ScriptedModel(replies=[call("read_checklist", case_id="CASE-001", simulate_outage=True), text("Incomplete")])
        with self.assertLogs("bank_review.operations", level="INFO") as logs:
            events, _, _ = await invoke(build_app(model))
        self.assertEqual(results(events)[0]["status"], "unavailable")
        self.assertTrue(any(record.json_fields["outcome"] == "exception" for record in logs.records))
        self.assertNotIn("Synthetic dependency timeout", "".join(logs.output))

    async def test_concurrent_invocations_have_distinct_correlation(self):
        from bank_review.telemetry import ReviewTelemetry
        # One shared plugin, separate invocations. No global error counter exists.
        plugin = ReviewTelemetry()
        from types import SimpleNamespace
        contexts = [SimpleNamespace(invocation_id=name, agent_name="review") for name in ["run-a", "run-b"]]
        tool = SimpleNamespace(name="read_checklist")
        with self.assertLogs("bank_review.operations", level="INFO") as logs:
            await asyncio.gather(*[plugin.after_tool_callback(tool=tool, tool_args={}, tool_context=ctx, result={"status": "ok"}) for ctx in contexts])
        rows = [record.json_fields for record in logs.records]
        self.assertEqual({row["invocation_id"] for row in rows}, {"run-a", "run-b"})
        self.assertTrue(all(set(row) == {"event", "invocation_id", "agent", "tool", "outcome"} for row in rows))
