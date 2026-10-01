# verify_setup.py - Environment verification script for Google ADK 2.0

# asyncio provides support for asynchronous programming, allowing non-blocking I/O operations (like calling LLM APIs).
import asyncio

# os provides access to operating system dependent functionality and environment variables.
import os

# warnings enables managing runtime warning messages emitted by Python or third-party libraries.
import warnings

# load_dotenv reads key-value pairs from a local .env file and sets them as environment variables (e.g., API keys).
from dotenv import load_dotenv

# Agent is the core building block representing an intelligent worker configured with instructions, a model, and tools.
from google.adk import Agent

# App encapsulates agents, configurations, and workflows into a deployable application unit.
from google.adk.apps import App

# InMemoryRunner executes agent apps locally in-memory for testing, debugging, and development.
from google.adk.runners import InMemoryRunner

# Pedagogical Note for Learners:
# 1. Automatic Function Calling (AFC) advisory: Under-the-hood, the google-genai SDK emits an advisory warning
#    when generate_content is called with default AFC settings in a single-turn verification script.
#    In production CLI/verification utilities, we silence non-actionable upstream SDK warnings.
warnings.filterwarnings(
    "ignore",
    message="Direct use of automatic function calling.*",
    category=UserWarning,
)


# Define the asynchronous entry point for our verification logic
async def main():
    # Load environment variables from .env file so the Google SDK can discover GOOGLE_API_KEY or GCP settings
    load_dotenv()

    # Pedagogical Note for Enterprise Authentication (ADC):
    # When using Application Default Credentials (ADC) with gcloud, Google Cloud requires a quota project
    # so Vertex AI knows which billing account/quota to charge. If GOOGLE_CLOUD_PROJECT is set but
    # GOOGLE_CLOUD_QUOTA_PROJECT is not, we automatically align them to avoid 429 quota warnings.
    if os.getenv("GOOGLE_CLOUD_PROJECT") and not os.getenv(
        "GOOGLE_CLOUD_QUOTA_PROJECT"
    ):
        os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = os.environ["GOOGLE_CLOUD_PROJECT"]

    # Print status message indicating start of verification checks
    print("🔍 Testing ADK 2.0 Environment...")

    # Wrap initialization and execution in a try-block to catch and report runtime or configuration errors
    try:
        # Step 1: Define an agent with a name, the target Gemini model, and a system instruction
        agent = Agent(
            # Unique identifier for the agent within the application
            name="verify_agent",
            # The foundation model to use for inference (Gemini 2.5/3.5 Flash)
            model="gemini-3.5-flash",
            # System prompt directing the agent's behavior and required response
            instruction="Respond with: 'ADK 2.0 is Ready!'",
        )

        # Step 2: Package the agent into an App instance as the root agent
        app = App(name="verify_app", root_agent=agent)

        # Step 3: Instantiate an in-memory runner to orchestrate and execute turns with the app
        runner = InMemoryRunner(app=app)

        # Step 4: Run a single turn using run_debug, sending a test prompt with a session user identifier
        print("🚀 Connecting to LLM...")
        events = await runner.run_debug("Hello!", user_id="test_user")

        # Flag to track whether the expected final response event was received from the agent
        ready = False
        # Iterate over all execution events generated during the run turn
        for event in events:
            # Check if this event contains the agent's completed final response (as opposed to intermediate events)
            if event.is_final_response():
                # Extract and print the generated text content from the first part of the response payload
                print(f"✅ Agent Response: {event.content.parts[0].text}")
                # Set the flag to True indicating successful interaction with the model
                ready = True

        # Check completion flag and output final verification status
        if ready:
            # Confirms all credentials, ADK packages, and LLM connectivity are functioning properly
            print("\n🎉 SETUP COMPLETE! You are running ADK 2.0.")
        else:
            # Reached if events finished without emitting a final response
            print("\n❌ Failed to get a final response from the agent.")

    # Catch missing or incompatible package errors (e.g. outdated google-adk version)
    except ImportError as e:
        print(f"❌ Version Error: {e}")
        print("Ensure you installed google-adk>=2.1.0")
    # Catch any other runtime exceptions (e.g., missing API key, network failure, model 404)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


# Standard Python boilerplate to run the main async function when executed directly from the terminal
if __name__ == "__main__":
    # Start the asyncio event loop and run main() to completion
    asyncio.run(main())
