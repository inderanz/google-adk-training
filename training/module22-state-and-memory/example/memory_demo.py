"""Prove two-session recall locally, or exercise an existing managed provider."""
import asyncio
import json
from bank_case.preferences import save_preference
from bank_case.services import APP_NAME, DEMO_USER, memory_service, session_service


async def main():
    sessions = session_service()
    memory = memory_service()
    try:
        first = await sessions.create_session(app_name=APP_NAME, user_id=DEMO_USER)
        await save_preference(sessions, memory, first, "concise")
        second = await sessions.create_session(app_name=APP_NAME, user_id=DEMO_USER)
        recalled = await memory.search_memory(
            app_name=APP_NAME, user_id=DEMO_USER, query="review explanation preference"
        )
        other_user = await memory.search_memory(
            app_name=APP_NAME, user_id="other-analyst", query="review explanation preference"
        )
        print(json.dumps({"different_sessions": first.id != second.id,
                          "current_preference": second.state.get("user:review_format"),
                          "recalled": len(recalled.memories),
                          "other_user_memories": len(other_user.memories)}))
    finally:
        await sessions.close()


if __name__ == "__main__":
    asyncio.run(main())
