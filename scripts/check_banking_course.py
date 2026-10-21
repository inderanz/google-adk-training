"""Check the local teaching sources for Modules 13.5–26 without cloud calls.

Run from the repository root with `uv run --no-project python
scripts/check_banking_course.py`. This checks consistency, not agent quality.
The per-module unittest and live-service commands remain separate checks.
"""
import ast
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
TRAINING = ROOT / "training"
MODULE = re.compile(r"module(13_5|14|1[5-9]|2[0-6](?:_5)?)-")


def main() -> None:
    errors = []
    documents = sources = references = 0
    versions = set()
    modules = sorted(path for path in TRAINING.iterdir() if MODULE.match(path.name))
    for module in modules:
        example = module / "example"
        project = tomllib.loads((example / "pyproject.toml").read_text())
        lock = tomllib.loads((example / "uv.lock").read_text())
        version = next(p["version"] for p in lock["package"] if p["name"] == "google-adk")
        versions.add(version)
        dependencies = project["project"]["dependencies"]
        for extra in project["project"].get("optional-dependencies", {}).values():
            dependencies += extra
        for dependency in dependencies:
            if dependency.startswith("google-adk") and not dependency.endswith("==" + version):
                errors.append(f"{module.name}: ADK declaration differs from lock")
        readme = (module / "README.md").read_text()
        if version not in readme:
            errors.append(f"{module.name}: README does not name locked ADK version")
        # Orient learners before the story or implementation. Keeping this
        # visible contract prevents future edits from burying the lesson topic.
        opening = re.search(r"^## .+$", readme, re.M)
        if opening is None or opening[0] != "## Before you begin: what this module teaches":
            errors.append(f"{module.name}: missing opening learning preview")
        else:
            preview = re.split(r"^## ", readme[opening.end():], maxsplit=1, flags=re.M)[0]
            for label in ("**ADK concept:", "**Where you would use this in real work.",
                          "**Connection to Gemini Enterprise Agent Platform and Google Cloud.",
                          "**By the end, you should be able to:"):
                if label not in preview:
                    errors.append(f"{module.name}: learning preview missing {label}")
        for source in example.rglob("*.py"):
            if ".venv" not in source.parts:
                ast.parse(source.read_text(), filename=str(source))
                sources += 1
        for document in module.glob("*.md"):
            documents += 1
            content = document.read_text()
            # Exclude examples: a URL inside a code fence is not a document link.
            prose = re.sub(r"```.*?```", "", content, flags=re.S)
            for href in re.findall(r"\]\(([^)]+)\)", prose):
                if href.startswith(("https:", "http:", "mailto:", "#")):
                    continue
                target = href.split("#")[0]
                if target and not (document.parent / target).exists():
                    errors.append(f"{document.relative_to(ROOT)}: missing link {href}")
            if document.name != "lab-solution.md":
                continue
            # File-labelled solution sections promise a complete source listing.
            for section in re.split(r"(?=^## )", content, flags=re.M):
                heading = section.splitlines()[0] if section else ""
                labels = re.findall(r"`([^`]+)`", heading)
                if not labels:
                    continue
                label = labels[-1]
                candidates = [example / label]
                if not candidates[0].is_file():
                    candidates = [p for p in example.rglob(label) if ".venv" not in p.parts]
                if len(candidates) != 1 or not candidates[0].is_file():
                    continue
                block = re.search(r"```[^\n]*\n(.*?)\n```", section, re.S)
                if block:
                    references += 1
                    if block[1].strip() != candidates[0].read_text().strip():
                        errors.append(f"{document.relative_to(ROOT)}: source differs for {label}")
    if len(modules) != 16 or len(versions) != 1:
        errors.append(f"Expected 16 modules with one ADK baseline; found {len(modules)}, {versions}")

    # The capstone packages teaching snapshots so deployment has no imports
    # from sibling lessons. Check that those visible copies have not drifted.
    capstone = TRAINING / "module26-callbacks/example"
    copies = {
        "module23-artifacts/example/bank_review/tools.py": "pack_store.py",
        "module25-observability/example/bank_review/telemetry.py": "telemetry.py",
        "module25_5-rai-safety-plugins/example/bank_review/safety.py": "safety.py",
    }
    for origin, target in copies.items():
        if (TRAINING / origin).read_text() != (capstone / "bank_review" / target).read_text():
            errors.append(f"Capstone source drift: {target}")
    repository = (TRAINING / "module13_5-firestore-persistence/example/bank_review/repository.py").read_text()
    read_only = repository.split("\n\nasync def mark_in_transaction", 1)[0].strip()
    if read_only != (capstone / "bank_review/case_repository.py").read_text().strip():
        errors.append("Capstone source drift: case_repository.py")
    gate = (TRAINING / "module24-evaluation/example/check_eval.py").read_text()
    expected = gate.replace("eval/cases.evalset.json", "eval/capstone.evalset.json").replace(
        "eval/eval_config.json", "eval/capstone_config.json")
    if expected != (capstone / "check_capstone_eval.py").read_text():
        errors.append("Capstone source drift: check_capstone_eval.py")

    print(f"Checked {len(modules)} modules, {documents} documents, {sources} Python files, "
          f"{references} full-file source listings; ADK {', '.join(sorted(versions))}.")
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: learning previews, syntax, declared ADK pins, relative file links, "
          "solution listings and reused sources.")
    print("Not checked here: anchor links, rendered diagrams, model quality, cloud IAM or deployment.")


if __name__ == "__main__":
    main()
