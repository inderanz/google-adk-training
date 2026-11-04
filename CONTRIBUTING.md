# How to Contribute to Google ADK Training

Thank you for your interest in contributing to the **Google ADK & Enterprise AI Agent Training** course! We welcome improvements, bug fixes, new modules, and corrections from the community.

---

## 🏛️ Scope of This Repository

This repository is the **hands-on Python developer curriculum**:
* **In Scope:** Module guides (`README.md`), challenge labs (`lab.md`), runnable solutions (`lab-solution.md`), verification harnesses (`verify_lab.py`), and sample agents.
* **Out of Scope:** Web hosting and Cloudflare infrastructure. (The live interactive reader at [gyanhq.com/adk-training](https://gyanhq.com/adk-training/) is deployed from an isolated production repository).

---

## 📐 Pedagogical & Code Standards

To maintain high learning efficacy and enterprise quality, all contributions must respect these core guidelines:

### 1. Challenge vs. Solution Separation
* **`lab.md` (Active Learning):** Must contain code skeletons with `# TODO` comments and conceptual hints. **Never paste full working code into `lab.md`**.
* **`lab-solution.md` (Reference Implementation):** Contains the complete, working, runnable code.
* Every `lab-solution.md` should include a **Google FDE Steering Prompt Template** so learners can instruct AI coding assistants accurately.

### 2. Google ADK 2.0 Standards
* **API Accuracy:** Use modern ADK 2.0 accessors (e.g., `response.content`, not `response.candidates`).
* **Tool Schemas:** Prefer typed Pydantic models (`BaseModel`) or zero-adapter OpenAPI specs (`OpenAPIToolset`).
* **Security & State:** Inject user identity securely via `tool_context.user_id`, never as an LLM argument.
* **Diagrams:** Ensure Mermaid sequence diagrams are clean and avoid nested delimiters that break parsers.

### 3. Fast-Path Verification
If you add or modify a lab, test it using the local verification script:
```bash
python3 verify_lab.py
```

---

## 🛠️ Contribution Workflow (Fork & Pull Request)

The `main` branch of this repository is protected:
* Direct pushes to `main` are disabled.
* Every change must go through a Pull Request and pass review.

### Step-by-Step Instructions

1. **Fork the Repository:**
   Click the **Fork** button at the top-right of [https://github.com/inderanz/google-adk-training](https://github.com/inderanz/google-adk-training).

2. **Clone Your Fork Locally:**
   ```bash
   git clone https://github.com/<your-username>/google-adk-training.git
   cd google-adk-training
   ```

3. **Set Up Python Environment (Python 3.10+):**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   uv pip install google-adk

   # Set your Gemini API Key
   export GEMINI_API_KEY="your-api-key"
   ```

4. **Create a Feature Branch:**
   ```bash
   git checkout -b feat/my-enhancement
   ```

5. **Make Changes & Test Locally:**
   * Test your agent code or run local verification:
     ```bash
     python3 verify_lab.py
     uv run adk web
     ```
   * Ensure no node/npm or web infrastructure files are introduced.

6. **Commit & Push to Your Fork:**
   ```bash
   git add .
   git commit -m "feat(moduleXX): concise description of improvement"
   git push origin feat/my-enhancement
   ```

7. **Open a Pull Request:**
   Go to [https://github.com/inderanz/google-adk-training](https://github.com/inderanz/google-adk-training) and click **"New Pull Request"**.
   * Detail what was modified, added, or fixed.
   * Confirm that verification scripts and lab tests pass.

---

Thank you for helping empower the next generation of AI agent builders!
