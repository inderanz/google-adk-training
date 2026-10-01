import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import callback_logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from callback_logging import log_query_to_model, log_model_response
from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin

# Sample tool for the geo validator
def validate_location(location: str) -> dict:
    """Validates if a given location is a real geographical place."""
    # Dummy logic for the sake of the lab
    valid_places = ["Paris", "Tokyo", "New York", "London"]
    is_valid = any(place.lower() in location.lower() for place in valid_places)
    return {"location": location, "valid": is_valid}

class LoggingPlugin(BasePlugin):
    """A plugin that logs queries and responses using Cloud Logging callbacks."""
    def __init__(self, name: str = 'logging_plugin'):
        super().__init__(name)

    async def on_agent_prompt_callback(self, *, agent, prompt, **kwargs):
        # We hook into the prompt callback to log queries
        log_query_to_model(str(prompt))

    async def on_agent_response_callback(self, *, agent, response, **kwargs):
        # We hook into the response callback to log responses
        log_model_response(str(response))

# Create the agent
geo_agent = Agent(
    name="geo_validator",
    model="gemini-3.5-flash",
    instruction="You are a geographic assistant. Validate the locations provided by the user.",
    tools=[validate_location],
)

# Create the app with the plugin
app = App(
    name="geo_validator_app",
    root_agent=geo_agent,
    plugins=[LoggingPlugin()]
)

if __name__ == "__main__":
    # Test run
    print("Running geo_validator test...")
    asyncio.run(app.run("Is Tokyo a valid location?"))
