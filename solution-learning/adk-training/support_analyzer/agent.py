import os
from functools import cached_property

from pydantic import BaseModel
from google.adk import Agent
from google.adk.models import Gemini
from google.genai import Client, types

try:
    from google.adk.models.lite_llm import LiteLlm
except ImportError:
    LiteLlm = None

# Defne the structured output schema
class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str

# Resilient model subclass
class ResilientGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(
           project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
           location="global",
           http_options=types.HttpOptions(
               retry_options=types.HttpRetryOptions(
                   max_attempts=5,  # Maximum number of retry attempts
                   initial_delay=1,  # Initial delay in milliseconds
                   max_delay=10,  # Maximum delay in milliseconds
                   exp_base=2,  # Exponential backoff base
                   jitter=0.5,
                )
            ),
        )

if os.getenv("USE_LOCAL_MODE") == "1":
    if LiteLlm is None:
        raise ImportError(
            "LiteLLM support requires the optional package: "
            "pip install 'google-adk[extensions]'"
        )
    model_to_use = LiteLlm(model="ollama_chat/mistral-7b-instruct")
else:
    model_to_use = ResilientGemini(model="gemini-3.5-flash")
# Define the root agent with adk 2.0 structured features
root_agent = Agent(
    name="support_analyzer",
    model="gemini-3.5-flash",
    description="An agent that categorizes customer support tickets and extracts sentiment.",
    instruction="""
       You are an expert customer support analyzer. Your task is to:
      1. Determine the category of the user's issue ("billing", "technical", or "general").
      2. Analyze the sentiment of the message ("positive", "negative", or "neutral").
      3. Write a concise, 1-sentence summary of the user's issue.   
      You MUST respond only with a JSON object matching the requested schema. Do not try to solve their problem.
    """,
    output_schema=SupportAnalysis,
    output_key="last_ticket_analysis"  # This key will be used to store the structured output in the agent's memory
)