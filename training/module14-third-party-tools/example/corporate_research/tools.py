"""Validate a narrow business request and return bounded, cited evidence."""

from datetime import UTC, date, datetime
import json
import logging
import re

from google.api_core.exceptions import GoogleAPIError, RetryError
from google.auth.exceptions import GoogleAuthError

from .repository import fetch_profile

logger = logging.getLogger(__name__)

COMPANY_ID_PATTERN = r"[A-Z][A-Z0-9-]{2,31}"
MAX_SUMMARY_CHARS = 2_000
MAX_OUTPUT_BYTES = 16_000
MAX_AGE_DAYS = 90
REQUIRED_FIELDS = (
    "company_id", "company_name", "summary", "source_uri", "reviewed_on"
)


def get_company_profile(company_id: str) -> dict[str, str | bool]:
    """Read an approved company background profile, not live news or credit advice.

    Args:
        company_id: Canonical uppercase company ID, for example ACME-001.
            Ask the analyst for the ID if it is unknown; do not invent one.

    Returns:
        A status and, on success, bounded evidence with its source and review date.
    """
    # A type hint describes an input; this check enforces the business contract.
    if not isinstance(company_id, str):
        return {"status": "invalid_input", "message": "Provide a company ID."}
    if re.fullmatch(COMPANY_ID_PATTERN, company_id) is None:
        return {"status": "invalid_input", "message": "Use a canonical company ID."}

    try:
        record = fetch_profile(company_id)
    except (GoogleAPIError, RetryError, TimeoutError) as exc:
        # Do not include exception messages, SQL, credentials, or company IDs.
        logger.warning("profile_lookup_failed", extra={"error_type": type(exc).__name__})
        return {"status": "unavailable", "message": "The profile service is unavailable."}
    except (KeyError, ValueError, GoogleAuthError) as exc:
        logger.error("profile_configuration_failed", extra={"error_type": type(exc).__name__})
        return {"status": "unavailable", "message": "The profile service needs operator attention."}

    if record is None:
        return {"status": "not_found", "message": "No approved profile was found."}

    # Fail visibly on bad source data; never substitute invented profile fields.
    for field in REQUIRED_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            return {"status": "invalid_record", "message": "The stored profile is incomplete."}
    if record["company_id"] != company_id:
        return {"status": "invalid_record", "message": "The stored profile has a mismatched ID."}
    if len(record["company_name"]) > 200 or len(record["source_uri"]) > 1_000:
        return {"status": "invalid_record", "message": "The stored metadata exceeds its limits."}

    try:
        reviewed_on = date.fromisoformat(record["reviewed_on"])
    except ValueError:
        return {"status": "invalid_record", "message": "The review date is invalid."}
    age_days = (datetime.now(UTC).date() - reviewed_on).days
    if age_days < 0:
        return {"status": "invalid_record", "message": "The review date is in the future."}
    if age_days > MAX_AGE_DAYS:
        return {
            "status": "stale",
            "message": "Request a refreshed profile before using this evidence.",
            "source_uri": record["source_uri"],
            "reviewed_on": record["reviewed_on"],
        }

    # An explicit field list prevents unrelated columns from reaching the model.
    result = {
        "status": "ok",
        "company_id": company_id,
        "company_name": record["company_name"],
        "summary": record["summary"][:MAX_SUMMARY_CHARS],
        "source_uri": record["source_uri"],
        "reviewed_on": record["reviewed_on"],
        "truncated": len(record["summary"]) > MAX_SUMMARY_CHARS,
    }
    # Characters, UTF-8 bytes, and model tokens are different measures.
    encoded = json.dumps(result, ensure_ascii=False).encode("utf-8")
    if len(encoded) > MAX_OUTPUT_BYTES:
        return {"status": "invalid_record", "message": "The profile exceeds the output budget."}
    return result
