import asyncio
import logging
from dotenv import load_dotenv
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from agent import root_agent

logging.getLogger("google.adk").setLevel(logging.WARNING)
load_dotenv()  # Load environment variables from .env file

app = App(name="support_analyzer_app", root_agent=root_agent)
runner = InMemoryRunner(app=app)

async def main():
    print("--- User A (Alice) ---")
    events_a = await runner.run_debug("Hello, I got overcharged $50.", user_id="Alice")

    for event in events_a:
        if event.is_final_response:
            print(f"DEBUG: Alice's JSON: {event.content.parts[0].text}")

    print("\n--- User B (Bob) ---")
    await runner.run_debug("My wifi is not working.", user_id="Bob")

if __name__ == "__main__":
    asyncio.run(main())