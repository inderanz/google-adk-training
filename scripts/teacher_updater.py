#!/usr/bin/env python3
"""Teacher updater helper script.

Safe, conservative edits for module markdowns:
- inserts a Teacher's Note block before each fenced Python code block
- appends an Official References section if missing

This script operates in preview mode by default and creates .bak copies
when `--apply` is provided.
"""
import argparse
import pathlib
import re
from typing import List


TEACHER_NOTE = (
    "<!-- TEACHER_NOTE_START -->\n"
    "**Teacher's note (ADK instructor view):**\n"
    "- **Learning goal:** Explain the concept clearly from beginner to advanced, with a simple mental model first.\n"
    "- **Why it matters:** Connect the concept to real Google agentic workflows, Python engineering habits, and production-ready decisions.\n"
    "- **Version watch:** Validate against the latest official ADK / Google docs before teaching; call out deprecations or migration notes when needed.\n"
    "- **Module linkage:** Connect this idea to the previous and next modules so learners see the progression across the course.\n"
    "<!-- TEACHER_NOTE_END -->\n"
)

OFFICIAL_REFS = (
    "\n---\n\n## Official References\n\n"
    "- Google ADK docs (latest): https://google.github.io/adk-docs/\n"
    "- Google AI / Gemini docs: https://ai.google.dev/\n"
    "- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/\n"
    "- Context7 / current SDK lookup for the exact installed version and API signatures\n"
    "- Related module path: review the surrounding modules for continuity, prerequisites, and follow-on concepts\n\n"
)


def find_markdown_files(path: pathlib.Path) -> List[pathlib.Path]:
    if path.is_file() and path.suffix.lower() == ".md":
        return [path]
    files = list(path.rglob("*.md"))
    return files


def preview_changes(original: str, updated: str) -> None:
    # Show a short diff-like preview: lines added only
    orig_lines = set(original.splitlines())
    for i, line in enumerate(updated.splitlines(), 1):
        if line not in orig_lines:
            print(f"+ {i}: {line}")


def process_markdown(content: str, do_annotate: bool, do_refs: bool) -> str:
    updated = content
    if do_annotate:
        # Insert a teacher note before code fences commonly used in training docs.
        pattern = re.compile(
            r"(^|\n)(```(?:python|bash|yaml|yml|json|mermaid)[\s\S]*?```)",
            re.IGNORECASE,
        )

        def repl(m: re.Match) -> str:
            before, block = m.group(1), m.group(2)
            if before.endswith("<!-- TEACHER_NOTE_END -->"):
                return m.group(0)
            return before + TEACHER_NOTE + block

        updated = pattern.sub(repl, updated)

    if do_refs:
        if "## Official References" not in updated:
            updated = updated.rstrip() + OFFICIAL_REFS

    return updated


def process_file(path: pathlib.Path, preview: bool, apply: bool, annotate: bool, refs: bool) -> None:
    original = path.read_text(encoding="utf-8")
    updated = process_markdown(original, annotate, refs)
    if original == updated:
        print(f"No changes for {path}")
        return
    print(f"Proposed changes for {path}:")
    preview_changes(original, updated)
    if apply:
        bak = path.with_suffix(path.suffix + ".bak")
        path.replace(bak)
        bak.write_text(updated, encoding="utf-8")
        # move bak back to original filename
        bak.replace(path)
        print(f"Applied edits to {path} (backup at {bak})")
    else:
        print("Preview mode — no files modified. Use --apply to write changes.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Module directory or markdown file path")
    parser.add_argument("--preview", action="store_true", default=True, help="Show changes (default)")
    parser.add_argument("--apply", action="store_true", help="Apply changes in-place (creates .bak files)")
    parser.add_argument("--annotate", action="store_true", help="Insert teacher notes before code fences")
    parser.add_argument("--refs", action="store_true", help="Append Official References if missing")
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.exists():
        print(f"Path not found: {path}")
        raise SystemExit(1)

    md_files = find_markdown_files(path)
    if not md_files:
        print("No markdown files found in the provided path.")
        return

    for md in md_files:
        process_file(md, preview=args.preview, apply=args.apply, annotate=args.annotate, refs=args.refs)


if __name__ == "__main__":
    main()
