---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 31 Solution: Choosing the Right Deployment Strategy

## Goal

Defend a runtime choice using requirements, alternatives and acceptance evidence. Several targets may be valid; a platform name alone is not a complete answer. Read the [updated concept and decision guide](./README.md) first.

## Scenario 1: the startup MVP

**A reasonable starting choice is Cloud Run** for a containerized request/response application whose limits fit the workload. The reason is reduced infrastructure operation, not a guaranteed five-minute deployment or automatic application security.

Confirm the expected concurrency, cold-start tolerance, session storage, identity and cost budget. Demonstrate an authenticated request, a denied request and recovery after instance replacement. A prototype using only in-memory sessions cannot claim durable conversations.

## Scenario 2: the government contractor

**Do not choose solely from the word FedRAMP.** Verify the current in-scope Google services, offering/region and contractual requirements with the customer's responsible teams. A platform's certification does not certify the application or remove customer controls.

Agent Runtime may fit the managed agent-hosting requirement; Cloud Run or GKE may also be relevant depending on the actual approved architecture. The deliverable is a requirements-to-control mapping and verified service scope, not a claim that only one platform is compliant. Consult the [official compliance resources](https://cloud.google.com/security/compliance).

## Scenario 3: the FinTech enterprise

**GKE is a defensible choice** when the bank already has a Kubernetes operating model and specifically needs its workload controls. Identify the required network policies, workload identity, release process, hardware and incident ownership.

Do not claim private networking or all GPU workloads are exclusive to GKE. Compare current supported Cloud Run and Agent Runtime capabilities before selecting the additional cluster responsibilities. Include a Pod-replacement and service-access test in the acceptance plan.

## Scenario 4: the university integration

**First establish the identity integration contract.** An existing identity provider or approved federation/gateway may meet the requirement. LDAP does not automatically force custom authentication code inside a FastAPI server.

If a custom application boundary is required, Cloud Run is one hosting option. Document how the user is authenticated, how that identity becomes the runtime user scope, and how sessions/resources are authorized. Evaluate token audience, expiry, revocation and denied access.

## What a complete answer contains

For each scenario, supply the requirement, selected target, one credible alternative, the reason for the choice, operational owner and acceptance evidence. Separate platform-provided controls from application responsibilities. Revisit the choice when requirements change instead of migrating merely because the application has more agents.

<!-- © 2026 Inder Chauhan (https://github.com/inderanz/google-adk-training). All rights reserved. Ref: IC-ADK-module31-production-deployment-strategies-lab-solution -->
---

## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Google AI / Gemini docs: https://ai.google.dev/
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Context7 / current SDK lookup for the exact installed version and API signatures
- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts

