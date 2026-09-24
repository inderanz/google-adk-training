import os
from functools import cached_property

from google.adk import Agent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Structured Output Schema (Carried over from Module 4)
# ---------------------------------------------------------------------------
class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str


# ---------------------------------------------------------------------------
# Resilient Model Subclass for Cloud Production (Gemini)
# ---------------------------------------------------------------------------
class ResilientGemini(Gemini):
    """
    Production-ready Gemini subclass with connection pooling and retry policies.
    """

    @cached_property
    def api_client(self) -> Client:
        return Client(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    max_delay=10,
                    exp_base=2.0,
                    jitter=0.5,
                )
            ),
        )


# ---------------------------------------------------------------------------
# Model Selection Logic (Environment-Driven)
# ---------------------------------------------------------------------------
if os.getenv("USE_LOCAL_MODEL") == "1":
    # Local Inference Stack (MLX-LM, Ollama, vLLM, LM Studio)
    # 1. Prefix 'openai/' instructs LiteLLM to speak OpenAI wire protocol.
    # 2. 'api_base' routes requests to the local server (default: http://127.0.0.1:8000/v1).
    # 3. 'api_key' satisfies client validation for local unauthenticated servers.
    local_url = os.getenv("LOCAL_MODEL_URL", "http://127.0.0.1:8000/v1")
    local_model = os.getenv("LOCAL_MODEL_NAME", "default_model")

    model_to_use = LiteLlm(
        model=f"openai/{local_model}",
        api_base=local_url,
        api_key="local-only",
        timeout=90,
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
else:
    # Production Cloud Model
    model_to_use = ResilientGemini(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))


# ---------------------------------------------------------------------------
# Root Agent Definition
# ---------------------------------------------------------------------------
root_agent = Agent(
    name="support_analyzer_agent",
    model=model_to_use,
    description="An agent that categorizes customer support tickets and extracts sentiment.",
    instruction="""
      You are an expert customer support analyzer. Your task is to:
      1. Determine the category of the user's issue ("billing", "technical", or "general").
      2. Analyze the sentiment of the message ("positive", "negative", or "neutral").
      3. Write a concise, 1-sentence summary of the user's issue.

      IMPORTANT: Respond ONLY with a JSON object matching the requested schema (SupportAnalysis).
      This JSON will be validated and saved to session state at `output_key`.
    """,
    output_schema=SupportAnalysis,
    output_key="last_ticket_analysis",
)
