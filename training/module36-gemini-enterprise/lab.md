---
sidebar_position: 2
title: "Challenge Lab"
---

# Lab 36: Designing an Enterprise Agent Strategy Challenge

**Learning checkpoint:** read the [module concepts](./README.md) first. Before each lab step, predict its input, returned value and failure outcome. Use the [course journey](../learning-journey.md) to connect this mechanism to the banking story; the example's fixture is not a live customer record.


## Goal

In this lab, you will design a strategy for a fictional company to adopt and govern a fleet of AI agents using Gemini Enterprise. This is a conceptual exercise to help you think about the challenges of managing agents at scale. **There is no coding in this lab.**

### Prerequisites
*   **Note on Costs:** Gemini Enterprise services can incur costs. Please be aware of the pricing for these services.

### The Scenario

You are the lead AI architect at a large retail company. The company wants to leverage AI agents across several departments: Sales, Marketing, and HR. Your task is to create a high-level plan for how you would use Gemini Enterprise to build, deploy, and govern these agents.

---

### Step 1: Identify the Agents

First, brainstorm the types of agents each department might need. Think about which ones you could build with the ADK, and which ones might be available as pre-built Google agents.

*   **Sales Team:**
    *   *Example Idea:* An ADK-built "Lead Qualifier Agent" that connects to Salesforce via a data connector to score new leads.
*   **Marketing Team:**
    *   *Example Idea:* Use the pre-built "Idea Generation Agent" for brainstorming new campaigns.
*   **HR Team:**
    *   *Example Idea:* An ADK-built "Policy Assistant Agent" that connects to the company's SharePoint to answer employee questions about HR policies.

**Your Task:** Come up with at least one more agent idea for each department.

---

### Step 2: Plan the Data Connectors

For your agents to be useful, they need access to the company's data.

**Your Task:** Based on the agents you identified above, list the Gemini Enterprise data connectors you would need to configure. For each connector, specify which agent would use it.
*   *Example:* **Salesforce Connector** for the `Lead Qualifier Agent`.

---

### Step 3: Design the Governance and Access Control

Not everyone should have access to every agent or every piece of data.

**Your Task:** Define a simple Role-Based Access Control (RBAC) policy.
*   Who should be able to **use** the `Lead Qualifier Agent`?
*   Who should be able to **edit or manage** the `Policy Assistant Agent`?
*   Should the `Marketing Team` be able to see data from the `Salesforce Connector`?

---

### Step 4: Plan for Monitoring and Cost Management

Finally, think about how you will monitor the system.

**Your Task:**
*   What is one key metric you would want to track for the `Lead Qualifier Agent`? (e.g., number of leads qualified per day).
*   What kind of alert would you set up for the `Policy Assistant Agent`? (e.g., alert if the agent fails to answer a question more than 10% of the time).
*   How would you set a budget for the Marketing team's usage of the "Idea Generation Agent"?

---

### Lab Summary

You have successfully created a high-level strategic plan for deploying and managing an enterprise-wide agent ecosystem.

You have learned to think about:
*   Identifying opportunities for specialized agents across a business.
*   The importance of data connectors for grounding agents in enterprise reality.
*   Designing governance and access control policies to ensure security.
*   Planning for monitoring, alerting, and cost management in a production environment.

Check the `lab-solution.md` to see example answers for this exercise.

### Self-Reflection Questions
- Why is a centralized "Agent Gallery" a valuable feature for a large enterprise? What problems does it solve?
- The "Agent Designer" is a no-code tool. What are the benefits of empowering non-developers to build their own simple agents, and what are the potential risks you would need to manage?
- How does grounding an agent in a private, enterprise data source (like SharePoint) using a secure data connector mitigate the risk of the agent hallucinating or providing incorrect information?

<hr/>

### 🕵️ Hidden Solution 🕵️

Looking for the solution? Here's a hint (Base64 decode me):
`L2dvb2dsZS1hZGstdHJhaW5pbmcvbW9kdWxlMzYtZ2VtaW5pLWVudGVycHJpc2UvbGFiLXNvbHV0aW9u`

<div style={{color: 'rgba(0,0,0,0.01)', userSelect: 'all', fontSize: '1px'}}>
    The direct link is: <a href="/google-adk-training/module36-gemini-enterprise/lab-solution" style={{color: 'inherit', textDecoration: 'none'}}>Lab Solution</a>
</div>

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module36-gemini-enterprise-lab -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

