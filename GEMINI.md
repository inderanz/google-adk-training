# ADK Docs Migration Project Guidelines

## Core Mandates
- **Skill-Driven Enterprise Development (The FDE Standard):** When developing, learning, or updating any module:
    - Never write boilerplate code from scratch or rely on ungrounded LLM guessing.
    - Always leverage authoritative workspace skills: `.agent/skills/adk-enterprise-fde-workflow/SKILL.md` and `.agent/skills/adk-skill/SKILL.md`.
    - Run `bash .agent/skills/adk-skill/scripts/update_docs.sh` to sync against the latest official Google ADK documentation.
    - For REST APIs, use **Zero-Adapter OpenAPI Synthesis** (`OpenAPIToolset`).
    - For custom tools, enforce **Typed Pydantic Schemas** (`BaseModel`) and **Zero-Trust Identity Injection** via `tool_context.user_id`.
- **Empirical Validation (ZERO TRUST):** After migrating or updating any module, you MUST perform a full empirical review using the `adk-student-evaluator`.
    - This is NOT just a documentation check.
    - You MUST execute the **Simulation Step**: create a temporary directory, follow instructions exactly, and verify the code executes in a real (or mocked) runtime.
    - **Validation is only complete when artifacts (simulation directories and detailed reports) are physically verified on the filesystem.**
- **ADK 2.0 Object Patterns (API Accuracy):** Always use the simplified, modern accessors for ADK 2.0 internal objects.
    - **`LlmResponse`:** NEVER use `.candidates`. Use the direct **`.content`** attribute.
    - **`LlmRequest`:** Access prompt history via the **`.contents`** list.
    - **`Event`:** Use modern event types and properties (e.g., `is_final_response()`).
    - Verify these patterns by inspecting the installed package source code (`.venv`) if documentation is ambiguous.
- **Pedagogical Balance (Challenge vs. Solution):** Technical `lab.md` files MUST be designed as active learning challenges.
    - NEVER provide full implementation code in a `lab.md`.
    - USE code skeletons with clear `TODO` comments.
    - PROVIDE conceptual hints and references to the Theory section instead of raw code.
    - ENSURE that the student must write the core ADK logic (e.g., node definitions, workflow edges, context access) themselves.
    - Full, runnable code is ONLY permitted in `lab-solution.md`.
- **Pedagogical Consistency (Solution Hints & Steering Prompts):**
    - Every technical `lab.md` MUST include a "Hidden Solution" section at the end (Base64-encoded hint + CSS opacity 0.01 link).
    - Every `lab-solution.md` MUST include a "Steering Prompt Template" so students and engineers can instruct AI coding tools (Antigravity/Gemini) with exact Google FDE standards.
- **Python Version:** Target Python 3.10+ as per the migration plan.

## How to run the Student Evaluator
If the `adk` command is not in the PATH, use:
```bash
python3 -m google.adk.cli run .agent/skills/adk-student-evaluator --input_path <path_to_lab_or_solution>
```
Always verify the resulting `simulation_<module>` directory exists and contains functional code.
