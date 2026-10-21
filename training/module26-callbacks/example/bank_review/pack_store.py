"""Create an evidence pack with exact input versions, using native ADK artifacts."""
import hashlib
import json

from google.adk.tools import ToolContext
from google.genai import types

SOURCE_NAME = "CASE-001-checklist.json"
REPORT_NAME = "CASE-001-review.md"
MANIFEST_NAME = "CASE-001-manifest.json"


def json_part(value: dict) -> types.Part:
    """Use UTF-8 bytes and an explicit media type for a portable JSON artifact."""
    # Artifacts store typed bytes, so serialize the dictionary and declare how those bytes are interpreted.
    data = json.dumps(value, sort_keys=True, indent=2).encode("utf-8")
    return types.Part.from_bytes(data=data, mime_type="application/json")


async def save_checklist(tool_context: ToolContext) -> dict:
    """Save the supplied fictional checklist; this does not read a bank system."""
    # Retain the version returned by ADK rather than predicting a version that another writer could change.
    checklist = {
        "case_id": "CASE-001",
        "source": "training-fixture:checklist-v1",
        "documents": {"financial_statements": True, "ownership_register": False},
    }
    version = await tool_context.save_artifact(
        filename=SOURCE_NAME, artifact=json_part(checklist)
    )
    return {"status": "saved", "filename": SOURCE_NAME, "version": version}


async def create_review_pack(source_version: int, tool_context: ToolContext) -> dict:
    """Build a report from one exact version; never silently switch to latest."""
    # Validate and load the requested evidence before any report save; never substitute the latest version.
    if type(source_version) is not int or source_version < 0:
        return {"status": "invalid_version"}
    source = await tool_context.load_artifact(SOURCE_NAME, version=source_version)
    if source is None:
        return {"status": "source_missing", "version": source_version}
    if not source.inline_data or source.inline_data.mime_type != "application/json":
        return {"status": "invalid_source"}
    raw = source.inline_data.data
    if not raw or len(raw) > 16_384:
        return {"status": "invalid_source"}
    try:
        case = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return {"status": "invalid_source"}
    required = {"financial_statements", "ownership_register"}
    if not isinstance(case, dict):
        return {"status": "invalid_source"}
    documents = case.get("documents")
    if (case.get("case_id") != "CASE-001" or not isinstance(documents, dict)
            or set(documents) != required
            or any(type(value) is not bool for value in documents.values())):
        return {"status": "invalid_source"}
    missing = sorted(name for name, received in documents.items() if not received)
    report = (
        "# CASE-001 review preparation\n\n"
        f"Checklist artifact: {SOURCE_NAME}, version {source_version}.\n\n"
        f"Missing documents: {', '.join(missing) if missing else 'none'}.\n\n"
        "Synthetic evidence only. A human analyst owns the credit decision.\n"
    )
    report_version = await tool_context.save_artifact(
        filename=REPORT_NAME,
        artifact=types.Part.from_bytes(data=report.encode("utf-8"), mime_type="text/markdown"),
    )
    manifest = {
        "case_id": "CASE-001",
        "source": {"filename": SOURCE_NAME, "version": source_version,
                   "sha256": hashlib.sha256(raw).hexdigest()},
        "report": {"filename": REPORT_NAME, "version": report_version},
        "status": "prepared_for_human_review",
    }
    # Save the manifest last. These saves are not one atomic transaction.
    manifest_version = await tool_context.save_artifact(
        filename=MANIFEST_NAME, artifact=json_part(manifest)
    )
    return {**manifest, "manifest_version": manifest_version}
