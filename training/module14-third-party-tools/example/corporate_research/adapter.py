"""Main lesson: adapt a LangChain company lookup for use by an ADK agent."""

from google.adk.integrations.langchain import LangchainTool
from langchain_core.tools import StructuredTool

from .tools import get_company_profile

# Represent the existing team-owned function as a LangChain tool. In a real
# project this object may already be supplied by another package or team.
legacy_tool = StructuredTool.from_function(
    func=get_company_profile,
    name="get_company_profile",
    description="Read an approved profile by canonical company ID.",
    return_direct=False,
)
# ADK needs its own tool interface; this wrapper supplies that interface.
# It reuses the callable and does not start a second agent framework.
adapted_tool = LangchainTool(tool=legacy_tool)
