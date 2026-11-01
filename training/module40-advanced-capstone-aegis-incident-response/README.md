---
sidebar_position: 40
title: "Module 40: Advanced Capstone - Aegis Incident Response & AgentOps"
---

# Module 40: Advanced Capstone - Aegis Incident Response & AgentOps

## Before you begin: what this module teaches

**ADK concept: a distributed capstone with explicit evidence and integration limits.**

A2A connects independently running agent applications; MCP exposes tool operations; ADK callbacks/plugins observe or control execution at defined boundaries. A target architecture diagram describes a design, while a local execution trace proves only the components actually exercised. A regex mask is not managed content inspection, and a printed URL is not a stored report.

**Where you would use this in real work.**

A bank operations analyst asks for an explanation of suspicious access events and a proposed response. Investigation, drafting a response and executing a remediation are separate responsibilities. The assistant must identify which evidence supports its advice and what remains simulated.

**Connection to Gemini Enterprise Agent Platform and Google Cloud.**

The target uses Google-hosted agents, approved log retrieval, Model Armor and Google observability/storage. The lab contains simulated integrations; replacing them requires real client contracts, IAM, error handling and live acceptance evidence. Reuse Modules 23–26 rather than treating the simulations as drop-in enterprise services.

**By the end, you should be able to:**

- Label every component as implemented, simulated or proposed.
- Trace a request across agents and tools with failure outcomes.
- Define a bank handover package with evidence and unresolved integration work.

### Review this lesson through three perspectives

- **Python/ADK beginner:** Explain each boundary without assuming that three agents imply reliability.
- **Experienced engineer:** Test remote failures, unsupported evidence and repeated remediation requests.
- **Bank FDE:** Agree permitted investigation, required human approvals and the owner of each production control.

Use the [guided lab](./lab.md) to observe the mechanism, then compare with the [solution](./lab-solution.md). The banking scenario above explains how to transfer the concept; a lab using a railway, weather or shopping fixture does not implement a live bank integration.

## Theory & Architecture

### 1. The Scenario: The 2:00 AM Crisis at Meridian Financial

*It is 2:14 AM on a rainy Tuesday.*

Inside the Security Operations Center (SOC) of Meridian Global Bank, red alerts flash across the central monitoring wall. A sudden deluge of anomalous traffic is battering the core billing databases. Audit logs in BigQuery are growing by tens of thousands of rows per second.

The on-call junior analyst sits paralyzed by three competing tabs:
1. **Raw Log Ingestion:** Incomprehensible database connection dumps and SQL strings (`' OR '1'='1`).
2. **NIST & CVE Vulnerability Playbooks:** A massive 600-page internal document library detailing remediation protocols.
3. **The Incident Commander's Chat:** Executive leadership demanding an immediate risk assessment and an executive containment brief.

Manually hunting down the rogue IP address, correlating it against database clusters, researching the exact CIS remediation recipe, drafting a sanitized containment script, and uploading an executive brief would take at least 45 minutes of panic-stricken engineering.

In banking cybersecurity, **45 minutes is an eternity**. Data exfiltration happens in milliseconds.

---

### 2. The Solution: Project Aegis (The Autonomous Incident Response Pod)

To rescue the on-call team, you are going to deploy **Project Aegis**—an automated, resilient multi-agent incident response pod powered by **Google ADK 2.0**.

Instead of building a single, fragile "do-everything" prompt, you will architect three cooperative, specialized AI agents operating as an elite triage team:

```mermaid
flowchart TB
    Analyst["🚨 SOC Analyst Prompt:<br/>'Detect brute-force attacks on billing databases<br/>and generate a verified patching plan.'"]

    subgraph Aegis_Pod["Project Aegis: Distributed Multi-Agent Response Pod"]
        Coordinator["🛡️ 1. Aegis Orchestrator (Port 8000)<br/>Central Incident Dispatcher & Evaluator"]
        ThreatIntel["🕵️ 2. Threat Intel Specialist (Port 8001)<br/>A2A Server + Model Armor Sanitizer"]
        LogMCP["📦 Isolated MCP Log Server<br/>Low-level BigQuery Audit Provider"]
        Mitigator["⚙️ 3. Mitigation Specialist (Port 8003)<br/>A2A Server + RAG Playbook Search"]
    end

    Analyst --> Coordinator
    Coordinator <-->|A2A Protocol| ThreatIntel
    ThreatIntel <-->|Model Context Protocol| LogMCP
    Coordinator <-->|A2A Protocol| Mitigator
    Mitigator -.-> Brief["📄 Executive Security Brief & Patch Script"]
```

#### How the Pod Solves the Crisis in Seconds:
1. **The Orchestrator (`aegis_orchestrator`)** receives the frantic command from the analyst. It decomposes the crisis into two mission-critical phases: *Forensic Investigation* followed by *Actionable Containment*.
2. **The Threat Specialist (`threat_intel_agent`)** receives an A2A task from the orchestrator. It queries an isolated **Model Context Protocol (MCP)** audit log server, extracts the attacker's footprint (e.g. 47 brute-force attempts and an injection payload), masks private corporate IPs with simulated **Model Armor**, and measures latency through **AgentOps hooks**.
3. **The Mitigation Specialist (`mitigation_agent`)** takes the corroborated incident profile from the orchestrator, queries NIST remediation playbooks via simulated **Vertex AI Search (RAG)**, drafts an automated firewall containment script, and uploads a signed Executive Security Brief.
4. **The Orchestrator** formats the final verified briefing and hands it back to the analyst, ready for human sign-off.

---

### 3. A Word of Confidence: From Scavenger Hunt to Distributed Multi-Agent Mastery

If you are feeling intimidated by terms like *A2A (Agent-to-Agent)*, *MCP (Model Context Protocol)*, and *AgentOps Callbacks*, pause for a moment and look back at your journey:
* In **Module 01**, you began with zero code—just exploring the vocabulary of AI agents.
* In **Modules 08–14**, you mastered Tools, Pydantic schemas, and external API connectors.
* In **Modules 15–21.5**, you graduated from simple bots to multi-agent static and dynamic coordination graphs.
* In **Modules 22–30**, you grounded agents with state, evaluation benchmarks, callbacks, and native MCP servers.
* In **Modules 31–39.5**, you explored production containerization on Cloud Run, GKE, and progressive skills.

**Module 40 is not a foreign mountain.** It is simply the joyful convergence of everything you have already mastered. Everything in this lab runs **100% locally on your machine with zero cloud costs and zero billing setup**.

The local exercise uses simulated Google services (Model Armor regex, static playbook strings, mock GCS URLs) so you can focus entirely on the core architectural breakthrough: **coordinating independent agent microservices over HTTP with production-grade telemetry.**

---

## The Three Cooperative Agents & AgentOps

### 1. Threat Intelligence Agent (A2A Server, runs locally)
Acts as an automated log investigator and threat hunter.
*   **MCP Log Hunting:** Connects to a real local **MCP server** — a lightweight stand-in for a hosted BigQuery MCP server — to query simulated security audit logs, login attempts, and injection attempts. You built a server just like it in Module 28.
*   **Data Masking (simulated Model Armor):** Prior to outputting threat details, it masks sensitive internal IP addresses using a local regex, standing in for a call to the real **Model Armor** API.
*   **AgentOps Metrics (real hooks, simulated export):**
    *   Real `before_model_callback`/`after_model_callback` hooks measure model-call latency.
    *   The hooks print what a real system would export to Cloud Logging and Cloud Trace — the hook mechanism is real ADK, the export destination is simulated.

### 2. Aegis Orchestrator Agent (Orchestrator, runs locally)
The central dispatch system for SOC analysts.
*   **Coordination:** It acts as an A2A client that calls the Threat Intelligence and Mitigation agents as `AgentTool`-wrapped remote agents — while delegation through `sub_agents` has a different mode-dependent contract. A transfer is not universally permanent; local and remote mode support must be checked separately (Module 19). `AgentTool` gives proper call-and-return semantics, so the orchestrator stays in control across both hops and can combine their results into one final answer.
*   **Command Scope:** Understands commands like:
    *   *"Detect any brute-force attacks on our billing databases and generate patching plans."*
    *   *"Remediate recent SQL injection risks in the mid-market segment logs."*
*   **Reliability:** Uses `RemoteA2aAgent(..., use_legacy=False)` to opt into ADK's reliability-fixed A2A executor (see Module 21), avoiding known streaming-mode message-duplication bugs.

### 3. Mitigation & Patching Agent (A2A Server, runs locally)
Compiles security advisories and automated patch scripts.
*   **Playbook Search (simulated RAG):** A tool function stands in for a Vertex AI Search (RAG) query over CIS Controls, NIST playbooks, and company-approved remediation standards.
*   **Briefing & Simulated GCS Upload:** Generates an executive security advisory and returns a simulated signed GCS URL, standing in for a real PDF render + Cloud Storage upload.

---

## AgentOps Deep-Dive: System Observability in Production

Implementing multi-agent systems in production requires robust **AgentOps** practices to track system performance, debug failures, and monitor costs:

1.  **Distributed Trace Propagation:**
    A2A agents communicate over HTTP. To see a unified timeline of a request, a production system propagates trace contexts across agent boundaries using standard W3C Trace Context headers. This links the user chat span to every downstream tool call and remote agent hop in a single trace tree. (This lab doesn't wire up real trace export — see "Going Further" below.)
2.  **Telemetry Hooks:**
    ADK 2.0's real hook mechanism is `before_model_callback` and `after_model_callback`, passed as constructor arguments to `Agent(...)` (the same pattern you used in Module 26). This lab uses them to measure and print:
    *   **LLM Latency:** Time taken by the model to generate responses.
    *   **AgentOps events:** A line simulating what a real export to Cloud Logging/Cloud Trace would send.

    A production system would keep the exact same callback signatures and replace the `print()` calls with real OpenTelemetry SDK calls.

### Going Further: Wiring Up the Real Services

Each simulated piece identifies an integration task. Real services require credentials, contracts, error handling and evaluation; replacing a function body alone is not sufficient:
*   **Model Armor:** follow Module 25.5's explicit allow/block/unavailable policy and persistence boundaries. A regex mask and managed inspection are different contracts.
*   **Vertex AI Search (RAG):** replace `search_remediation_playbooks`'s fixed string with a real Vertex AI Search query, or an MCP server wrapping one, following the same `McpToolset` pattern already used for BigQuery.
*   **GCS Upload:** replace the simulated URL in `build_and_upload_mitigation_brief` with a real PDF render and a Cloud Storage upload (directly, or via another local MCP server built the same way as `bigquery_mock_server.py`).
*   **Real observability:** configure the supported native ADK exporter and verify cross-service trace propagation. Add bounded domain observations where needed; do not recreate all native spans in callbacks. Module 25 explains the distinction.
*   **Real deployment:** once the pieces above are real, deploy the three agents the same way you learned in Modules 32-35 (Cloud Run for the two A2A servers, Agent Runtime for the orchestrator).
*   **Agent Skills for the playbooks:** `search_remediation_playbooks` is currently a plain function returning a fixed string. Module 39.5's Skills pattern (`SkillToolset` + `load_skill_from_dir`) is arguably a better fit than a hand-written RAG query for this: bundle each CIS/NIST playbook as its own Skill, with the remediation steps living in the Skill's `references/` folder, loaded via Progressive Disclosure only when the Mitigation Agent actually needs that specific playbook instead of always in context.

## Continue the course story

Previous: [Module 39.5](../module39_5-agent-skills/README.md) · Next: [Review the complete journey](../learning-journey.md) · [See how the concepts build](../learning-journey.md)

Before continuing, explain one input, one ADK execution boundary and one failure outcome from this module. Use the next chapter to add a new customer requirement, not merely another component.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module40-advanced-capstone-aegis-incident-response-README -->
---


## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

