"""Firestore owns the business checklist, independently of ADK sessions."""

from functools import cache
import os

from google.cloud import firestore

DOCUMENT_NAMES = ("financial_statements", "ownership_register")


@cache
def get_client() -> firestore.AsyncClient:
    # Reuse one client within this CLI process's single asyncio event loop.
    return firestore.AsyncClient(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        database=os.environ.get("FIRESTORE_DATABASE", "(default)"),
    )


def summarize_case(
    data: dict | None, case_id: str, user_id: str
) -> dict[str, object]:
    # Do not reveal whether another analyst's case exists.
    if data is None or data.get("assigned_analyst_id") != user_id:
        return {"status": "not_found", "message": "No accessible case was found."}
    name = data.get("borrower_name")
    version = data.get("version")
    documents = data.get("documents")
    if (
        not isinstance(name, str)
        or not name.strip()
        or len(name) > 200
        or type(version) is not int
        or version < 1
        or not isinstance(documents, dict)
    ):
        return {"status": "invalid_record", "message": "The case needs data-owner review."}
    for name_key in DOCUMENT_NAMES:
        if type(documents.get(name_key)) is not bool:
            return {"status": "invalid_record", "message": "The checklist is incomplete."}
    return {
        "status": "ok",
        "case_id": case_id,
        "borrower_name": name,
        "version": version,
        "documents": {key: documents[key] for key in DOCUMENT_NAMES},
    }


async def read_case(case_id: str, user_id: str) -> dict[str, object]:
    reference = get_client().collection("review_cases").document(case_id)
    snapshot = await reference.get(timeout=10, retry=None)
    return summarize_case(snapshot.to_dict(), case_id, user_id)


async def mark_in_transaction(
    transaction, reference, case_id: str, user_id: str,
    document_name: str, expected_version: int,
) -> dict[str, object]:
    snapshot = await reference.get(transaction=transaction, timeout=10, retry=None)
    result = summarize_case(snapshot.to_dict(), case_id, user_id)
    if result["status"] != "ok":
        return result
    # A repeated request for an already-true flag does not write or increment.
    if result["documents"][document_name]:
        result["status"] = "already_received"
        return result
    if result["version"] != expected_version:
        return {"status": "conflict", "message": "Read the case again before updating."}
    transaction.update(reference, {
        f"documents.{document_name}": True,
        "version": expected_version + 1,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })
    result["documents"][document_name] = True
    result["version"] = expected_version + 1
    return result


async def mark_received(
    case_id: str, user_id: str, document_name: str, expected_version: int
) -> dict[str, object]:
    client = get_client()
    reference = client.collection("review_cases").document(case_id)
    # Google's decorator retries the whole transaction on eligible contention.
    commit_receipt = firestore.async_transactional(mark_in_transaction)
    return await commit_receipt(
        client.transaction(max_attempts=3), reference,
        case_id, user_id, document_name, expected_version,
    )
