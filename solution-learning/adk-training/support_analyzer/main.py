import asyncio
import logging
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from agent import root_agent

load_dotenv()  # Load environment variables from .env file
# 1. create the app container
app = App(name="support_analyzer", root_agent=root_agent)

#2. create the runner
runner = InMemoryRunner(app=app)

async def main():
    print("---User A(Alice)---")
    events_a = await runner.run_debug("I was overcharged on my last bill and I need a refund.", user_id="Alice")
    for event in events_a:
        if event.is_final_response():
            print(f"Debug: Alice's JSON: {event.content.parts[0].text}")

    print("\n---User B(Bob)---")
    await runner.run_debug("My internet connection is down and I can't access my email.", user_id="Bob")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())