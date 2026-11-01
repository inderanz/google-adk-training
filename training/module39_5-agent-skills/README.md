---
sidebar_position: 39.5
title: "Module 39.5: Agent Skills"
---

# Module 39.5: Enhancing Agents with Skills

## Before you begin: what this module teaches

**ADK concept: skills, progressive disclosure and execution permissions.**

A skill packages instructions and optional references/scripts. Progressive disclosure exposes brief discovery information first, then loads detailed content when selected. SkillToolset supplies the supported access tools. A reference teaches a procedure; a tool or code executor performs an operation. Loading a skill must not silently expand the user's authorization.

**Where you would use this in real work.**

The bank has several approved procedures, but loading every manual into every prompt makes simple questions harder to handle. The assistant should load the relevant procedure when needed, while keeping operation permissions explicit.

**Connection to Gemini Enterprise Agent Platform and Google Cloud.**

Use ADK's supported skill interfaces with pinned versions and reviewed content. Script execution needs a deliberate supported sandbox and identity; UnsafeLocalCodeExecutor is not a customer isolation boundary. A remote skill registry also needs provenance, access and lifecycle controls.

**By the end, you should be able to:**

- Distinguish discovery metadata, loaded instructions, references and executable capabilities.
- Explain the skill directory and its required frontmatter.
- Evaluate whether selecting the right skill leads to correct authorized behavior.

### Review this lesson through three perspectives

- **Python/ADK beginner:** Trace when a reference is loaded instead of assuming it is always in context.
- **Experienced engineer:** Test conflicting instructions, stale versions and unavailable references.
- **Bank FDE:** Ask who approves procedures, scripts and updates and how a withdrawn skill is removed.

Use the [guided lab](./lab.md) to observe the mechanism, then compare with the [solution](./lab-solution.md). The banking scenario above explains how to transfer the concept; a lab using a railway, weather or shopping fixture does not implement a live bank integration.

## Draw the execution boundary

Illustrative progressive disclosure. Model selection must be evaluated, and tool access stays explicit.

```mermaid
flowchart TB
  A[Request and skill metadata] --> B[Select relevant skill]
  B --> C[Load instructions]
  C --> D[Read needed references]
  D --> E[Use only authorized capabilities]
```

## Theory

### 1. The Scenario: The Bloated 400-Tool Support Bot at Horizon Telecom

*Consider this classic architectural breakdown at enterprise scale.*

Horizon Telecom built an ambitious AI assistant to support 15,000 corporate agents and retail stores. The team started enthusiastically:
- They added tools for SIM provisioning.
- They added tools for broadband diagnostics.
- They added tools for corporate billing adjustments, eSIM swaps, roaming packs, and 5G network towers.
- Each time a department joined, their 20-page Standard Operating Procedure (SOP) was pasted into the agent's system prompt.

By month six, disaster struck:
1. **Context Window Suffocation:** The agent's base system prompt swelled past **180,000 tokens** before a single customer even typed "hello".
2. **First-Token Latency Crisis:** Every prompt took 14 seconds just to process the static prompt tokens.
3. **Severe Tool Confusion:** When a user asked: *"Can you help reset my device PIN?"*, the LLM got confused between the 40 different reset tools and called `factory_reset_cellular_tower_node()`.

The team attempted to fix this with more prompt engineering, but it was impossible: **you cannot dump an entire enterprise's operating manuals into a single agent prompt.**

```mermaid
flowchart TD
    subgraph Monolithic_Bloat["❌ The Monolithic Trap (180k Tokens)"]
        M1["Root Prompt Loaded with 400 Tools<br/>& 20 Enterprise Manuals"] --> M2["Massive 14s Latency<br/>Skyrocketing Token Bills"]
        M2 --> M3["💥 Tool Confusion & Hallucinations"]
    end

    subgraph Progressive_Disclosure["✅ Enterprise Agent Skills (Under 1k Tokens)"]
        S1["Lightweight Root Agent<br/>(Only loads skill name & description)"] --> S2{"User Intent Match?<br/>'Device PIN Reset'"}
        S2 -- Dynamic Load --> S3["Load 'pin-reset-skill'<br/>(Reads SKILL.md on-demand)"]
        S3 --> S4["Deterministic Script Execution<br/>Isolated & Sandboxed"]
        S4 --> S5["🚀 Instant Latency & Zero Tool Confusion"]
    end
```

---

### 2. The Solution: Agent Skills & Progressive Disclosure

To resolve this crisis, Google ADK introduced **Agent Skills**—a standardized framework for packaging and delivering on-demand procedural intelligence.

A **Skill** is not a simple Python function; it is a self-contained, versioned operational package containing:
1. **`SKILL.md` (Metadata + Instructions):** 
   - **Frontmatter (`name`, `description`):** The only part loaded initially. It tells the agent *when* the skill is relevant.
   - **Markdown Body:** The exact procedural step-by-step instructions, loaded into context *only when the skill is invoked*.
2. **`references/` (Domain Knowledge):** Auxiliary schemas, error codes, and style guides that the agent reads dynamically using file-reading tools if needed.
3. **`scripts/` (Deterministic Code):** Production-grade Python scripts that run deterministic operations (like calculating complex taxes or validating cryptographic signatures) instead of asking the LLM to write code from scratch.
4. **`additional_tools`:** Native Python functions bundled specifically with that skill.

#### How Progressive Disclosure Works in Production:
* **Stage 1 (Discovery):** The agent knows only that `pin-reset-skill` exists (~50 tokens).
* **Stage 2 (Activation):** When the user asks about PINs, the agent invokes `load_skill("pin-reset-skill")`. The ADK framework loads `SKILL.md` into the conversation.
* **Stage 3 (Execution):** The agent executes the prescribed SOP, optionally invoking scripts via a secure `code_executor`.
* **Stage 4 (Unload):** When the task completes, the skill's instructions do not permanently bloat subsequent unrelated questions.

---

### 3. Enterprise Fleet Governance: Corporate Skill Registries

In enterprise environments (such as Gemini Enterprise or banking platforms), organizations manage thousands of skills across disparate engineering squads. Rather than hardcoding paths on local filesystems, enterprises maintain **Centralized Skill Registries**:
* **Corporate GitHub/GitLab Repositories:** Skills are maintained under version control with PR reviews and automated linting.
* **Semantic Discovery (`search_skills`):** Agents execute vector semantic search against the enterprise skill catalog to discover relevant skills dynamically.
* **Sandboxed Execution:** In production, scripts are never executed via `UnsafeLocalCodeExecutor`. They run inside isolated Google Cloud Run containers or gVisor sandboxes with strict network boundaries.

```python
import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor

# 1. Load a skill from a local directory
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

# 2. Create a Toolset to manage the skills and any extra tools they need
# WARNING: UnsafeLocalCodeExecutor allows the agent to run the scripts/ folder
# locally. Do not use in untrusted production environments!
my_skill_toolset = SkillToolset(
    skills=[weather_skill],
    additional_tools=[get_current_humidity_tool], 
    code_executor=UnsafeLocalCodeExecutor(),
)

# 3. Give the entire toolset to the Agent
agent = Agent(
    model="gemini-3.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    tools=[my_skill_toolset]
)
```

**Production Alternative**: `UnsafeLocalCodeExecutor` is for learning only. For production, ADK offers sandboxed executors that isolate execution outside your own process — e.g. `GkeCodeExecutor` (runs code in a dedicated GKE pod) or `AgentEngineSandboxCodeExecutor` (a managed sandbox on Agent Runtime). Both require their respective infrastructure already provisioned, so they're mentioned here as a pointer rather than a lab exercise.

### The Structure of a Skill Directory

When you use `load_skill_from_dir`, the ADK expects a specific directory layout:

```text
my-skill/
├── SKILL.md           <-- Required: YAML frontmatter (name/desc) + Markdown body
├── scripts/           <-- Optional: Executable code (Python, Bash, etc.)
├── references/        <-- Optional: Documentation for the agent to read
└── assets/            <-- Optional: Files used in the output (templates, etc.)
```

The skill's frontmatter `name` must be lowercase kebab-case (letters, digits, hyphens — no underscores) and match its containing directory name exactly, or `load_skill_from_dir` will reject it.

### Going Further: The Skill Registry (Preview)

Everything above loads skills from your local filesystem — fine for a handful of skills you wrote yourself. In an enterprise setting with hundreds or thousands of skills shared across teams, ADK offers a **Skill Registry** (currently a Preview feature) that lets an agent discover and load skills on demand from a remote catalog instead of bundling them all upfront.

You connect it by passing a registry (e.g. `GCPSkillRegistry` from `google.adk.integrations.skill_registry`) to your `SkillToolset`. ADK then automatically injects two extra tools for the agent: `search_skills(query)` to find relevant skills semantically, and `load_skill(skill_name)` to pull one in only when needed — the same Progressive Disclosure idea, just applied to a catalog instead of a local folder. Locally loaded skills always take priority over registry ones with the same name. This is beyond the scope of this lab, but worth knowing about if you're designing a skill strategy for a larger organization.

### Key Takeaways
- **Skills** are modular packages containing instructions, references, and scripts to teach an agent complex domain knowledge.
- They prevent context bloat via **Progressive Disclosure**—loading detailed instructions only when the skill is activated.
- In ADK 2.0, you load skills from a directory using `load_skill_from_dir()`.
- You provide skills to an Agent by bundling them inside a `SkillToolset`, which handles the activation and execution logic.

## Continue the course story

Previous: [Module 39](../module39-plugins/README.md) · Next: [Module 40](../module40-advanced-capstone-aegis-incident-response/README.md) · [See how the concepts build](../learning-journey.md)

Before continuing, explain one input, one ADK execution boundary and one failure outcome from this module. Use the next chapter to add a new customer requirement, not merely another component.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module39_5-agent-skills-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

