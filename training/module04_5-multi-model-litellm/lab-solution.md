---
sidebar_position: 7
title: "Lab Solution"
---

# Lab 4.5 Solution: Professional Model Configuration, Resiliency & Portability

## Goal

In this lab, you learned how to transition from simple string-based model selection to a professional, enterprise-grade configuration using `Gemini` subclasses and `LiteLlm` abstractions -- while keeping the Module 4 structured-output contract (`SupportAnalysis`, `output_schema`, `output_key`) fully intact. The model-resiliency features and the structured-output feature are independent and layer on top of each other cleanly.

### `support_analyzer/agent.py`

Here is the complete code implementing the resilient subclass and the multi-model fallback logic, built on top of the `SupportAnalysis` schema from Module 4:


```python
import os
from functools import cached_property
from pydantic import BaseModel
from google.adk import Agent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types

# ---------------------------------------------------------------------------
# Teaching-oriented comments: This file demonstrates a production-ready pattern
# for selecting and configuring LLM backends while preserving a stable
# structured-output contract for downstream code. Read the comments as a
# narrative: why each piece exists, and how to adapt it when requirements
# change in plain English.
# ---------------------------------------------------------------------------

# Structured output schema (carried over from Module 4)
# Analogy: Think of this schema as the "interface" or API contract between
# the agent and the rest of your system. The agent must always return JSON
# that matches this shape so downstream code can depend on it deterministically.
class SupportAnalysis(BaseModel):
    # category: which bucket the ticket belongs to
    category: str
    # sentiment: simple polarity label for quick prioritization
    sentiment: str
    # summary: a one-sentence human-readable explanation
    summary: str


# ------------------
# Resilient model subclass
# ------------------
# Why subclass? In production you often need to centralize cross-cutting
# concerns (retries, regions, credentials). Subclassing keeps those details
# in one place so all agents share the same safe defaults.
class ResilientGemini(Gemini):
        """
        Production-ready Gemini subclass.

        Teaching notes:
        - Centralizes client construction so you don't forget retry policies.
        - Use environment variables to keep secrets/config out of source code.
        - Use `cached_property` to build the client once per agent instance and reuse it.

            What `cached_property` does (plain English): the first time the
            `api_client` attribute is accessed the method runs and its return
            value is stored on the instance. Subsequent accesses return the
            stored (cached) object instead of rebuilding it.

            Benefits:
                - avoids repeated expensive setup (authentication handshakes,
                    TLS negotiation, or constructing heavy SDK objects), which
                    reduces latency and resource use.
                - keeps a single, consistent client instance per agent, which
                    simplifies connection pooling and observability.

            When to use:
                - for idempotent, long-lived resources such as HTTP clients,
                    database connectors, or SDK wrappers that are safe to reuse.

            When not to use / caveats:
                - avoid when the resource must refresh often (rotating credentials,
                    per-request differing config) — in those cases use a factory
                    or explicit refresh logic instead.
                - `cached_property` caches on a per-instance basis; if you need a
                    global singleton across processes, use a different pattern.
        """

    @cached_property
    def api_client(self) -> Client:
        # Build the low-level Gemini/GenAI client with production defaults.
        # If a future requirement needs a different region or extra headers,
        # change it here once instead of everywhere in the repo.
        return Client(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="us-central1",
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    # Max seconds to wait between retry attempts
                    max_delay=10,
                    # Exponential base for backoff (2 = doubles each retry)
                    exp_base=2.0,
                    # Jitter reduces simultaneous retry storms (thundering herd)
                    jitter=0.5,
                )
            ),
        )


# ------------------
# Model selection logic (environment-driven)
# ------------------
# Plain-English requirement this satisfies:
# "I want to run this locally for development (fast loop), but use
#  the cloud model in production without changing code."
# The implementation below flips between a local lightweight LLM and the
# production Gemini client using `USE_LOCAL_MODEL` env var.
# "I want to run this against a local inference stack (e.g. MLX-LM, LM Studio,
#  vLLM, or Ollama) on my machine for zero-cost, private offline development,
#  and automatically use production Gemini in cloud deployments without code changes."
if os.getenv("USE_LOCAL_MODEL") == "1":
    # Local dev: use the LiteLLM adapter (e.g., Ollama or other local runner)
    # Benefit: fast offline iteration and reproducible behavior for demos.
    model_to_use = LiteLlm(model="ollama_chat/mistral")
    # Local inference stack via LiteLLM adapter:
    # 1. Prefix 'openai/' instructs LiteLLM to speak OpenAI wire protocol.
    # 2. 'api_base' points to your local server (default: http://127.0.0.1:8000/v1).
    # 3. 'api_key' satisfies client validation for local unauthenticated endpoints.
    # 4. 'extra_body' passes provider-specific flags (e.g., disable thinking tokens).
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
    # Production: use the resilient Gemini subclass for real traffic
    model_to_use = ResilientGemini(model="gemini-3.5-flash")
    # Production: use the resilient Gemini subclass for real cloud traffic
    model_to_use = ResilientGemini(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))


# ------------------
# Agent definition (keeps behavior and output contract stable)
# ------------------
# Key design point: `output_schema` and `output_key` are part of the agent
# contract, not the model. This decouples how you *validate* outputs (schema)
# from where the model runs (local vs cloud). That separation makes the code
# easier to reason about and test.
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
    # This enforces the structured-output contract — treat it as the agent's API.
    output_schema=SupportAnalysis,
    # Where to persist the validated result in session state for downstream use
    output_key="last_ticket_analysis",
)

# ---------------------------------------------------------------------------
# Teaching examples (how to adapt when given plain-English requirements)
# ---------------------------------------------------------------------------
# - If the customer asks "run analyses using eu-region models", change
#   `location` in ResilientGemini.api_client or add a runtime flag.
# - If you need richer sentiment (score + label), extend `SupportAnalysis`
#   with a `score: float` field and update instruction accordingly.
# - To add tool calls (e.g., lookup user account), register safe tools on
#   the agent and keep tool effects deterministic and auditable.
# ---------------------------------------------------------------------------
```

### Key Takeaways Explained

1.  **Centralization via Subclassing:** By creating `ResilientGemini`, you avoid repeating complex `HttpRetryOptions` for every agent in your codebase. If you need to change the region from `us-central1` to `global`, you only update it in one place.
2.  **The Thundering Herd Problem:** By adding `jitter=0.5`, you ensure that if multiple agent requests fail at the same time, they won't all retry at the exact same millisecond, which helps prevent overwhelming your API backend.
3.  **Environment-Driven Architecture:** Using `os.getenv("USE_LOCAL_MODEL")` makes your code highly portable. You can run it on your laptop using Ollama and then deploy it to the cloud without changing a single line of code—only the environment variables change.
3.  **Environment-Driven Architecture:** Using `os.getenv("USE_LOCAL_MODEL")` makes your code completely portable. You can run it locally against an OpenAI-compatible inference server (such as Apple-native MLX-LM, vLLM, LM Studio, or Ollama) for zero-cost, private offline development, and deploy it to Google Cloud with `ResilientGemini` in production without changing any code.
4.  **Model Configuration Is Orthogonal to Output Structure:** Notice that `output_schema` and `output_key` are set on the `Agent` itself, not on the model. This is why swapping `model_to_use` between `ResilientGemini` and `LiteLlm` has no effect on the structured-output behavior you built in Module 4 -- the agent still validates and stores the `SupportAnalysis` JSON in `last_ticket_analysis` regardless of which model backend answers the request.

---

### Practical Guide: Running Against a Local Inference Stack

If you or your team members run models locally (e.g., Apple Silicon MLX-LM, LM Studio, vLLM, or Ollama), here is the exact setup:

#### 1. Verify Your Local Inference Server
Confirm your local OpenAI-compatible server is active and serving models (default port `8000` for MLX-LM/vLLM, `1234` for LM Studio, `11434` for Ollama):
```bash
# Check available models
curl -s http://127.0.0.1:8000/v1/models

# Smoke test chat completion
curl -s -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "default_model",
    "messages": [{"role": "user", "content": "Reply with exactly: MLX ready"}],
    "temperature": 0,
    "max_tokens": 20
  }'
```

#### 2. Why the LiteLLM Configuration Looks Like This
```python
model_to_use = LiteLlm(
    model="openai/default_model",           # 'openai/' prefix instructs LiteLLM to speak OpenAI HTTP protocol
    api_base="http://127.0.0.1:8000/v1",     # Redirects calls from api.openai.com to your local loopback server
    api_key="local-only",                   # Satisfies client token checks (local servers do not authenticate)
    timeout=90,                             # Allows sufficient headroom for local GPU/Unified Memory prefill
    extra_body={
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},  # Disables reasoning tokens for direct JSON responses
    },
)
```

#### 3. Execution
Set the environment variables to activate local mode:
```bash
# Run with local inference:
USE_LOCAL_MODEL=1 \
LOCAL_MODEL_URL="http://127.0.0.1:8000/v1" \
LOCAL_MODEL_NAME="default_model" \
python -m support_analyzer.agent
```

### Self-Reflection Answers

1.  **Why is "Jitter" important in a retry policy for a high-traffic production application?**
    *   **Answer:** Without jitter, multiple failed requests would retry at the exact same intervals (e.g., exactly after 1s, 2s, 4s). In a high-traffic system, this creates "spikes" of traffic that can re-trigger rate limits or crash a recovering service. Jitter adds a random offset to each retry, spreading the load evenly over time.

2.  **What are the advantages of centralizing model configuration in a subclass instead of passing parameters to every agent instance?**
    *   **Answer:** It follows the DRY (Don't Repeat Yourself) principle. It makes the code easier to maintain, reduces the risk of configuration errors (e.g., having different retry policies in different agents), and allows for global changes (like swapping the production GCP project) to be made instantaneously across the entire system.

3.  **In which scenario would you prefer using the native `Gemini` class over the `LiteLlm` abstraction?**
    *   **Answer:** Use the native `Gemini` class when you are building a production system on Google Cloud and need the highest performance, lowest latency, and access to Gemini-specific features (like native speech config, context caching, or advanced grounding) that might not be fully mapped or supported by the general LiteLLM abstraction.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module04_5-multi-model-litellm-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

