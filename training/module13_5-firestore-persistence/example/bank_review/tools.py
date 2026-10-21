"""Small ADK tools: validate arguments, use trusted identity, report results."""

import logging
import re

from google.adk.tools import ToolContext
from google.api_core.exceptions import GoogleAPIError, RetryError
from google.auth.exceptions import GoogleAuthError

from . import repository

logger = logging.getLogger(__name__)
CASE_ID_PATTERN = r"CASE-[0-9]{3,12}"
BOUNDARY_ERRORS = (GoogleAPIError, RetryError, GoogleAuthError, TimeoutError, KeyError, ValueError)


def valid_case_id(case_id: str) -> bool:
    return isinstance(case_id, str) and re.fullmatch(CASE_ID_PATTERN, case_id) is not None


def unavailable(error: Exception) -> dict[str, str]:
    logger.warning("case_store_unavailable", extra={"error_type": type(error).__name__})
    return {"status": "unavailable", "message": "Case storage needs operator attention."}


async def get_review_case(case_id: str, tool_context: ToolContext) -> dict[str, object]:
    """Read the current checklist for an accessible case; ask for a missing case ID."""
    if not valid_case_id(case_id):
        return {"status": "invalid_input", "message": "Use a case ID such as CASE-001."}
    try:
        result = await repository.read_case(case_id, tool_context.user_id)
    except BOUNDARY_ERRORS as error:
        return unavailable(error)
    if result["status"] == "ok":
        # A navigation hint, not a second copy of the authoritative checklist.
        tool_context.state["last_case_id"] = case_id
    return result


async def mark_document_received(
    case_id: str,
    document_name: str,
    expected_version: int,
    tool_context: ToolContext,
) -> dict[str, object]:
    """Record receipt only when the analyst explicitly requests it.

    Read the case first and pass its version. Receipt does not verify contents
    or approve credit. Only financial_statements and ownership_register apply.
    """
    if (
        not valid_case_id(case_id)
        or document_name not in repository.DOCUMENT_NAMES
        or type(expected_version) is not int
        or expected_version < 1
    ):
        return {"status": "invalid_input", "message": "Provide a valid case, document and version."}
    try:
        result = await repository.mark_received(
            case_id, tool_context.user_id, document_name, expected_version
        )
    except BOUNDARY_ERRORS as error:
        return unavailable(error)
    if result["status"] in ("ok", "already_received"):
        tool_context.state["last_case_id"] = case_id
    return result
