---
sidebar_position: 7.1
title: "Module 07 Enterprise Playbook: Multimodal Agents for Real Customer Work"
---

# Module 07 Enterprise Playbook: Multimodal Agents for Real Customer Work

This module teaches a very practical enterprise skill: handling images, documents, and other non-text inputs in a production-ready ADK workflow. The current Google ADK docs emphasize that the framework is designed for production agents, not just prototypes, and that agents can grow from simple form to multi-agent or graph-based architectures as the task complexity grows.

Multimodal work is a classic forward-deployed engineering topic because customer problems often involve more than plain text: images, PDFs, screenshots, product photos, forms, and operational dashboards.

## The forward-deployed engineer lens

A forward-deployed engineer does not assume that all customer problems are text-only. In real work, the requirement is often ambiguous at first:

> "We need the system to understand product photos and summarize them for our catalog team."

Or:

> "Can we analyze receipts or scanned documents and extract key fields?"

These are not just AI prompts. They are workflow design problems:

- what is the input format?
- what model or modality should be used?
- how should the image be packaged and sent?
- what happens if the image is low-quality or unreadable?
- should the output be structured JSON, a summary, or a recommendation?

This is where multimodal ADK patterns become valuable.

## Business translation

For a customer, a vague ask like “analyze images” usually becomes a clearer system requirement such as:

- analyze product images and generate catalog descriptions
- extract text from invoices and receipts
- compare object images against a catalog
- detect defects or compliance issues in images
- classify documents or process uploaded screenshots

Module 07 is the step where those requirements become concrete ADK flows using `types.Part`, `types.Blob`, session flows, and multimodal messaging.

## Core ADK concept from Google docs

The ADK ecosystem strongly encourages expanding agents from simple text tasks to richer workflows when the task demands it. That means:

- more than plain chat
- structured multimodal prompts
- tool use around image processing or knowledge retrieval
- integration with APIs or downstream systems

This is consistent with the forward-deployed mindset: take the raw modality, package it correctly, and feed it into the workflow.

## Why multimodal design matters in enterprise systems

The main production challenge is not just sending an image to a model. It is integrating that image into the broader business workflow.

### Real-world multimodal patterns

- **Vision QA**: inspect an image and validate product defects or safety issues
- **Document understanding**: analyze scanned forms or invoices
- **Catalog generation**: turn visual product data into structured descriptions
- **Support triage**: understand screenshots, handwritten notes, or UI captures
- **Visual compliance**: compare uploaded images to policy standards

### Core design principle

The agent should not be the entire business process. The better design is:

- model interprets the image
- deterministic business logic validates the result
- downstream systems store or act on the output

## Enterprise pattern

### Pattern 1: Image classification or extraction
Use when the business problem is narrow and clear.

Example:

- identify product category from an image
- detect if a photo has a defect
- extract fields from a scanned invoice

Design:

- single multimodal agent
- narrow prompt
- structured output schema
- validation before saving data

### Pattern 2: Visual decision support assistant
Use when the agent needs to reason over both text and image content.

Example:

- customer support agent assisted by screenshots
- product advisor agent analyzing visual product details
- operational case review with image + ticket data

Design:

- multimodal prompt combining text and image
- tool access to internal customer or product data
- session continuity for context
- human review for sensitive decisions

### Pattern 3: Multi-stage multimodal workflow
Use when image understanding is only one part of the process.

Example:

- classify the image
- lookup the product in a catalog
- compare against pricing or quality rules
- generate a final recommendation or summary

This is exactly where the ADK docs emphasize moving from simple agent patterns to workflow patterns as complexity grows.

## Working model for multimodal enterprise apps

A robust multimodal ADK flow usually looks like this:

1. Receive the image or document upload
2. Detect the file type and content type
3. Convert the bytes into a `types.Part` / `types.Blob`
4. Build a multimodal `Content` message with text + image
5. Run the agent in a session
6. Validate the output structure and business rules
7. Save the result to a system of record
8. Trigger downstream actions such as alerts, catalog updates, or approvals

This is much more valuable than a one-off demo, and it reflects real forward-deployed engineering practice.

## Requirements checklist for customer conversations

When a customer says “we want AI to understand images,” ask:

- What image formats do we support?
- What is the target business outcome?
- Do we need a structured output or free-form description?
- How do we validate that the model output is correct?
- What happens if the image is missing, blurry, or unrecognizable?
- Should the system store derived metadata?
- Do we need approval for high-impact decisions?

## Guardrails for multimodal systems

### Data quality
- validate image size and type
- reject broken or corrupted files early
- normalize file formats before analysis

### Safety and policy
- avoid exposing confidential images to model workflows without review
- apply access controls to internal image sources
- ensure downstream decisions respect enterprise policy

### Observability
- log file metadata, prompt type, and output confidence-like indicators
- record which image was analyzed and when
- capture model output for debugging and evaluation

### UX and business design
- show the user a human-readable result, not only raw model text
- define when a workflow should escalate to a human reviewer

## Related modules

- [Module 05 Enterprise Playbook](../module05-running-agents/enterprise-playbook.md)
- [Module 06 Enterprise Playbook](../module06-programmatic-execution/enterprise-playbook.md)
- [Module 08 Intro to Tools](../module08-intro-to-tools/README.md)
- [Module 09 Intro to Custom Function Tools](../module09-intro-custom-function-tools/README.md)
- [Module 12 Grounding and Retrieval](../module12-built-in-tools-grounding/README.md)
- [Module 24 Evaluation](../module24-evaluation/README.md)

## Anti-patterns to avoid

### Anti-pattern 1: sending raw file paths instead of packaged content
The model needs a proper multimodal payload, not just a filename.

### Anti-pattern 2: treating image understanding as the whole solution
The image pass is usually only one stage in a larger business workflow.

### Anti-pattern 3: ignoring output validation
If the business impact is high, a free-form model description is not enough. Add a validation layer.

### Anti-pattern 4: skipping session and user context
For multimodal enterprise assistants, users often expect continuity across interactions and uploads.

## Final enterprise takeaway

Module 07 is where ADK moves from “text-only assistant” to “real-world perception and interpretation.” In customer work, that matters because many high-value tasks involve the visual layer of the business process.

A forward-deployed engineer should treat multimodal input as a workflow design problem, not just a coding trick. Package the data correctly, maintain the task context, validate output, and connect it to the real operational system behind the experience.

## Official ADK / Google references

- ADK docs home: https://google.github.io/adk-docs/
- ADK agents overview: https://google.github.io/adk-docs/agents/
- Gemini API multimodal docs: https://ai.google.dev/gemini-api/docs/multimodal
- Google AI Studio / Gemini docs: https://ai.google.dev/gemini-api/docs
- Vertex AI multimodal guidance: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal

These references should be checked when updating multimodal examples, model capabilities, or input handling guidance.

---

## Related roadmap

- [Enterprise ADK Playbook Index](../enterprise-adk-roadmap.md)
- [Module 07 README](./README.md)
