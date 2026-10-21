"""Select adk_entry in ADK Web; TEAM_MODE chooses the teaching variant."""
import os
from bank_case.agent import build_agent, build_delegation_team

mode = os.environ.get("TEAM_MODE", "tools")
if mode not in {"tools", "single_turn", "task", "chat"}:
    raise ValueError("TEAM_MODE must be tools, single_turn, task or chat")
root_agent = build_agent() if mode == "tools" else build_delegation_team(mode=mode)
