"""Change the synthetic case inputs without editing the implementation."""
import argparse
import asyncio
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import display, run_once

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a fictional CASE-001 scenario")
    parser.add_argument("--requested-cents", type=int, default=SAMPLE["requested_cents"])
    parser.add_argument("--documents-complete", action="store_true")
    args = parser.parse_args()
    # Copy the fixture; do not mutate a shared dictionary between runs.
    payload = SAMPLE | {"requested_cents": args.requested_cents,
                        "documents_complete": args.documents_complete}
    agent = build_agent()
    display(asyncio.run(run_once(agent, payload)))
