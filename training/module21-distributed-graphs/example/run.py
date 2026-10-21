import asyncio
from bank_case.agent import build_agent
from bank_case.contracts import SAMPLE
from runtime import display, run_once

if __name__ == "__main__":
    display(asyncio.run(run_once(build_agent(), SAMPLE)))
