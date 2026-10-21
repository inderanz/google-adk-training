"""Create one fictional development case without overwriting an existing case."""

import asyncio

from google.cloud import firestore

from bank_review.repository import get_client
from bank_review.sessions import DEMO_USER_ID


async def seed() -> None:
    reference = get_client().collection("review_cases").document("CASE-001")
    await reference.create({
        "assigned_analyst_id": DEMO_USER_ID,
        "borrower_name": "Acme Robotics (fictional training company)",
        "documents": {"financial_statements": False, "ownership_register": False},
        "version": 1,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }, timeout=10, retry=None)
    print("Created fictional CASE-001. Existing documents are never overwritten.")


if __name__ == "__main__":
    asyncio.run(seed())
