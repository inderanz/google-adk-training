"""Select a built-in ADK session service; never fall back silently to RAM."""

import os

from google.adk.sessions import BaseSessionService, DatabaseSessionService

APP_NAME = "bank_review"
# A synthetic CLI identity, not an implementation of user authentication.
DEMO_USER_ID = "analyst-demo"


def build_session_service() -> BaseSessionService:
    backend = os.environ.get("SESSION_BACKEND", "sqlite")
    if backend == "sqlite":
        return DatabaseSessionService(
            db_url=os.environ.get(
                "SESSION_DB_URL", "sqlite+aiosqlite:///./review_sessions.db"
            )
        )
    if backend == "managed":
        from google.adk.sessions import VertexAiSessionService

        return VertexAiSessionService(
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ["GOOGLE_CLOUD_AGENT_ENGINE_LOCATION"],
            agent_engine_id=os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"],
        )
    raise ValueError("SESSION_BACKEND must be sqlite or managed.")


async def close_session_service(service: BaseSessionService) -> None:
    await service.flush()
    if isinstance(service, DatabaseSessionService):
        await service.close()
