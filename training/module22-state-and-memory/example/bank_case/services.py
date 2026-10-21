"""Use ADK's providers instead of building another session or memory store."""
import os
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import DatabaseSessionService

APP_NAME = "bank_case"
DEMO_USER = "analyst-demo"  # Replace with verified caller identity in a server.


def session_service():
    # Choose the native persistence provider; scope prefixes alone do not provide durability.
    return DatabaseSessionService(db_url=os.environ.get(
        "SESSION_DB_URL", "sqlite+aiosqlite:///./analyst_sessions.db"
    ))


def memory_service():
    # Select retrieval independently from session storage; their restart behavior is different.
    backend = os.environ.get("MEMORY_BACKEND", "local")
    if backend == "local":
        return InMemoryMemoryService()
    if backend == "managed":
        from google.adk.memory import VertexAiMemoryBankService
        return VertexAiMemoryBankService(
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ["GOOGLE_CLOUD_AGENT_ENGINE_LOCATION"],
            agent_engine_id=os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"],
        )
    raise ValueError("MEMORY_BACKEND must be local or managed")
