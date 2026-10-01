import asyncio
import logging

from agent import root_agent
from dotenv import load_dotenv

# --- Step 1: ADK and Google GenAI Imports ---
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

# Suppress verbose debug logs from network clients
logging.getLogger("google.adk").setLevel(logging.WARNING)

load_dotenv()

# --- Step 2: Infrastructure Initialization ---
# The App encapsulates the agent with an application name
app = App(name="ticket_processing_app", root_agent=root_agent)

# The Runner orchestrates session state and execution
runner = InMemoryRunner(app=app)


def build_ticket_payload(
    ticket_id: str, priority: str, user_description: str
) -> types.Content:
    """
    Constructs a strongly-typed multi-part Content object for an enterprise ticket.
    """
    # Create the structured metadata header part
    part_header = types.Part.from_text(
        text=f"[TICKET_METADATA] ID: {ticket_id} | Priority: {priority}"
    )

    # Create the main user description part
    part_body = types.Part.from_text(text=f"[USER_DESCRIPTION] {user_description}")

    # Assemble into a Content turn with role="user"
    return types.Content(
        role="user",
        parts=[part_header, part_body],
    )


async def main() -> None:
    user_id = "fde_operator_01"

    # --- Step 5: Explicit Session Creation ---
    # Create the session explicitly in the SessionService before streaming
    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id=user_id,
    )
    print(f"Initialized active session: {session.id} for operator: {user_id}\n")

    # --- Step 6: Build the Typed Payload ---
    ticket_payload = build_ticket_payload(
        ticket_id="INC-9941",
        priority="HIGH",
        user_description="Our database replica is out of sync and billing jobs are failing.",
    )

    print("Agent Response Stream: ", end="", flush=True)

    # --- Step 7: Stream with run_async ---
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=ticket_payload,
    ):
        # --- Step 8: Safe Defensive Inspection ---
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)

        if event.is_final_response():
            print("\n\n[Turn Complete: Final response verified]")


if __name__ == "__main__":
    asyncio.run(main())
