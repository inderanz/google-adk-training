# How to Contribute

Thank you for your interest in contributing to the **Google ADK & Enterprise AI Agent Training** course! We welcome improvements, corrections, and new content from the community.

## Code of Conduct

We expect all contributors to adhere to standard professional open-source conduct to ensure a welcoming, inclusive, and collaborative environment.

## Contribution Workflow (Fork & Pull Request)

The `main` branch of this repository is strictly protected:
* Direct pushes to `main` are disabled.
* Branch deletion and force pushes are blocked.
* Every change must go through a Pull Request and be approved by the repository owner (`@inderanz`).

### Step-by-Step Instructions

1. **Fork the Repository:**
   Click the **Fork** button at the top-right of [https://github.com/inderanz/google-adk-training](https://github.com/inderanz/google-adk-training) to create your own copy on GitHub.

2. **Clone Your Fork Locally:**
   ```bash
   git clone https://github.com/<your-username>/google-adk-training.git
   cd google-adk-training
   ```

3. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/my-enhancement
   ```

4. **Make Your Changes & Test:**
   * If modifying code or labs, test your agent code:
     ```bash
     uv run adk web
     ```
   * If modifying portal or documentation, run the test suite:
     ```bash
     cd portal && npm test
     ```

5. **Commit and Push to Your Fork:**
   ```bash
   git add .
   git commit -m "feat: description of your improvement"
   git push origin feature/my-enhancement
   ```

6. **Open a Pull Request:**
   Go to [https://github.com/inderanz/google-adk-training](https://github.com/inderanz/google-adk-training) and click **"New Pull Request"**. Compare across forks with your feature branch.
   * Provide a clear description of what was changed and why.
   * Inder Chauhan will review and approve the PR before merging into `main`.

Thank you for helping empower the next generation of AI agent builders!
