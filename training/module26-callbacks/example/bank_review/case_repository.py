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

