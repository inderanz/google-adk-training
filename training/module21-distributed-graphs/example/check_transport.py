"""Run with the loopback server active; makes no model or cloud API calls."""
import unittest
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import run_once


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_a2a_round_trip(self):
        events = await run_once(build_agent(), SAMPLE)
        text = "\n".join(
            part.text for event in events if event.content
            for part in event.content.parts or [] if part.text
        )
        # This asserts a deterministic server response, not LLM phrasing.
        self.assertIn("CASE-001: checklist complete=False", text)
        self.assertIn("Synthetic evidence only; no credit approval.", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
