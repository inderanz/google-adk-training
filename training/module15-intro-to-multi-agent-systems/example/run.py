"""Choose a real prompt; credentials are needed only after argument parsing."""
import argparse
import asyncio
import os
from bank_case.agent import build_agent
from runtime import display, run_once

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask about fictional bank review preparation")
    parser.add_argument("prompt", nargs="?", default="Explain how to prepare CASE-001 for review.")
    args = parser.parse_args()
    if not os.environ.get("GEMINI_MODEL"):
        raise SystemExit("Load .env using: uv run --env-file .env python run.py")
    agent = build_agent()
    display(asyncio.run(run_once(agent, args.prompt)))
