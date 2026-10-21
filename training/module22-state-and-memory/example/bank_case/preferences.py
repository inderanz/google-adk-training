"""A preference has a small explicit vocabulary and contains no case facts."""
from google.adk.events import Event, EventActions
from google.genai import types

FORMATS = {"concise", "detailed"}


def preference_event(review_format: str) -> Event:
    # Only an explicitly allowed preference becomes a persistent state change.
    if review_format not in FORMATS:
        raise ValueError("Review format must be concise or detailed")
    return Event(
        author="preference_service",
        content=types.Content(role="user", parts=[types.Part.from_text(
            text=f"My bank review explanation preference is {review_format}."
        )]),
        actions=EventActions(state_delta={"user:review_format": review_format}),
    )


async def save_preference(sessions, memory, session, review_format):
    # Commit exact state first; a later memory failure must not be described as a rolled-back preference.
    event = preference_event(review_format)
    # Commit the authoritative preference first, through the session service.
    await sessions.append_event(session=session, event=event)
    # Send only the validated preference event, not the case conversation.
    # If this fails the preference remains saved; this is not a transaction.
    await memory.add_events_to_memory(
        app_name=session.app_name, user_id=session.user_id,
        events=[event], session_id=session.id,
    )
