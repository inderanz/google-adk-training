---
sidebar_position: 2
title: "Challenge Lab"
---

import Setup from '../_setup-snippet.mdx';

# Lab 8: Creating a "Researcher" Agent with Google Search Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Goal
Your task is to build and configure an action-taking agent equipped with tools. This lab offers a **Dual-Track Learning Experience**:
* **Track A (Live Cloud Grounding):** Connect Gemini to live Google Search using the built-in `google_search` tool on Vertex AI.
* **Track B (Local Zero-Cost Function Tool):** Build a deterministic company filing research tool using standard Python functions and test it locally with zero cloud API costs.

---

## Track A: Live Research Agent with Google Search Grounding (Cloud Track)

In this track, you equip Gemini with Google's native Search Grounding capability to answer real-time questions with live web citations.

<Setup/>

### Step 1: Initialize Project Directory & Environment

1. **Create the agent project:**
   ```shell
   uv run adk create researcher_agent
   cd researcher_agent
   ```
2. **Configure Cloud Credentials (`.env`):**
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=your_actual_gcp_project_id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```
   > [!IMPORTANT]
   > `google_search` grounding requires the Vertex AI API (`aiplatform.googleapis.com`) enabled on your Google Cloud project.

### Step 2: Implement the Agent (`agent.py`)

Open `agent.py` and implement the researcher agent using the starter skeleton below:

```python
# In agent.py
from google.adk.agents import Agent
from google.adk.tools import google_search

# TODO: Define the root_agent node
# 1. Set model to "gemini-3.5-flash"
# 2. Add explicit instructions detailing WHEN to invoke search
# 3. Add google_search to tools list
root_agent = Agent(
    name="researcher_agent",
    model="gemini-3.5-flash",
    instruction="""You are an expert market and news research assistant.
    Always use the `google_search` tool to look up current events, breaking news,
    or recent regulatory updates. Cite your sources clearly in your response.""",
    tools=[google_search],
)
```

### Step 3: Run & Verify

1. Run the agent in the ADK Dev UI:
   ```shell
   uv run adk web
   ```
2. Ask a current event question: *"Who won the most recent Super Bowl or FIFA World Cup?"*
3. Open the **"Trace"** view in the Dev UI to inspect the `groundingMetadata` and web source URLs.

---

## Track B: Deterministic Research Tool with Python Functions (Local / Offline Track)

If you are developing locally without an active GCP billing account, or wish to understand how Python function signatures translate into OpenAPI schemas, complete Track B!

### Step 1: Implement the Custom Filing Lookup Tool (`filing_agent.py`)

Create `filing_agent.py` in your project folder. Complete the `# TODO` items:

```python
"""Track B: Deterministic Local Tool Demonstration without GCP Dependencies."""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()


# 1. Define the Python Tool Function
def lookup_sec_filing(ticker: str, filing_type: str = "10-K") -> dict:
    """Retrieves corporate regulatory filings and financial metrics.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'GOOGL', 'AAPL', 'MSFT'). Required.
        filing_type (str, optional): The SEC filing type ('10-K', '10-Q', '8-K'). Defaults to '10-K'.

    Returns:
        dict: A structured dictionary containing filing status, revenue, and core risk factors.
    """
    mock_filings = {
        "GOOGL": {
            "revenue": "$307.4B",
            "net_income": "$73.8B",
            "status": "Clean Audit",
            "ai_investment": "$48B",
        },
        "AAPL": {
            "revenue": "$383.3B",
            "net_income": "$97.0B",
            "status": "Clean Audit",
            "flagship_product": "iPhone",
        },
    }
    data = mock_filings.get(
        ticker.upper(),
        {"error": f"Ticker '{ticker}' not found in SEC EDGAR repository."},
    )
    return {"ticker": ticker.upper(), "filing_type": filing_type, "data": data}


# TODO: 2. Create the Agent Node
# - Wrap lookup_sec_filing with FunctionTool
# - Instruct the agent to use lookup_sec_filing for financial disclosures
filing_agent = Agent(
    name="filing_researcher",
    model="gemini-3.5-flash",
    instruction="""You are a Wall Street equity research analyst.
    Use `lookup_sec_filing` to retrieve corporate financial records.
    Synthesize factual responses strictly based on the tool's output.""",
    tools=[FunctionTool(lookup_sec_filing)],
)


async def main():
    # 3. Register on App and execute locally
    app = App(name="sec_research_app", root_agent=filing_agent)
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name=app.name, user_id="analyst_1", session_id="s1"
    )

    query = "What was the revenue and AI investment reported in Alphabet's (GOOGL) latest 10-K filing?"
    print(f"User: {query}\n")

    async for event in runner.run_async(
        user_id="analyst_1",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        ),
    ):
        # TODO: Observe how the ADK reports tool calls and final responses
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Observe Function Calling in the Terminal
### Step 2: Fast-Path Pre-Flight Verification

Before running the full interactive agent, verify your tool definition and type signatures with the automated pre-flight checker:

```bash
python verify_lab.py
```

This tests:
1. Python function type annotations (`ticker: str -> dict`) needed for OpenAPI schema generation.
2. Docstring quality for Gemini tool selection.
3. ADK agent node instantiation and tool attachment.

If any check fails, the tool gives you an immediate, copy-pasteable fix!

### Step 3: Observe Function Calling in the Terminal

Run `python filing_agent.py`. Notice how:
1. Gemini inspects the question and selects `lookup_sec_filing(ticker='GOOGL', filing_type='10-K')`.
2. The ADK runtime runs the Python code and hands the JSON data back to Gemini.
3. Gemini outputs: *"According to Alphabet's (GOOGL) latest 10-K filing, the company reported $307.4B in revenue and $48B in AI infrastructure investments..."*

---

## Self-Reflection Questions
1. **Model vs. Tool Separation:** Why does the LLM never execute the Python function directly? What security catastrophe would occur if the LLM ran arbitrary code on your server?
2. **Schema Ingestion:** How does Gemini know that `ticker` is a required string while `filing_type` is optional? Where does this metadata originate?
3. **Live Search vs. Custom Tool:** In what scenarios would an enterprise prefer Google Search grounding over internal custom tools, and vice versa?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMDgtaW50cm8tdG8tdG9vbHMvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module08-intro-to-tools/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module08-intro-to-tools-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

