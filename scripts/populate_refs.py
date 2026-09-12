#!/usr/bin/env python3
"""Populate canonical Official References into module README files.

This script finds markdown files under a given path and replaces or inserts
the `## Official References` section with a curated, canonical set of links.
It operates in preview mode by default and writes changes when --apply is set.
"""
import argparse
import pathlib
from typing import List


CANONICAL_REFS = """
## Official References

- Google ADK docs (latest): https://google.github.io/adk-docs/
- Gemini API (multimodal): https://ai.google.dev/gemini-api/docs
- Google GenAI Python SDK reference: https://googleapis.github.io/python-genai/
- Vertex AI generative guidance: https://cloud.google.com/vertex-ai/generative-ai
- Cloud Vision and OCR: https://cloud.google.com/vision

"""


def find_readme_files(path: pathlib.Path) -> List[pathlib.Path]:
    files = list(path.rglob("README.md"))
    # include module README.md and top-level README in training dir
    return files


def replace_refs(content: str) -> str:
    if "## Official References" in content:
        # remove existing section
        parts = content.split("## Official References", 1)
        prefix = parts[0]
        # drop everything after header until the next top-level section or EOF
        suffix = parts[1]
        # find next top-level header '## ' occurrence
        idx = suffix.find('\n## ')
        if idx != -1:
            new_content = prefix + CANONICAL_REFS + suffix[idx+1:]
        else:
            new_content = prefix + CANONICAL_REFS
        return new_content
    else:
        return content.rstrip() + "\n\n" + CANONICAL_REFS


def preview_changes(orig: str, updated: str) -> None:
    orig_lines = orig.splitlines()
    upd_lines = updated.splitlines()
    for i, (o, u) in enumerate(zip(orig_lines, upd_lines), 1):
        if o != u:
            print(f"Line {i} change: \n- {o}\n+ {u}\n")


def process_file(path: pathlib.Path, apply: bool) -> None:
    content = path.read_text(encoding="utf-8")
    updated = replace_refs(content)
    if content == updated:
        print(f"No refs change: {path}")
        return
    print(f"Updating refs in {path}")
    if apply:
        bak = path.with_suffix(path.suffix + ".bak")
        path.replace(bak)
        bak.write_text(updated, encoding="utf-8")
        bak.replace(path)
        print(f"Applied refs to {path} (backup at {bak})")
    else:
        preview_changes(content, updated)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    p = pathlib.Path(args.path)
    if not p.exists():
        print(f"Path not found: {p}")
        raise SystemExit(1)
    files = find_readme_files(p)
    if not files:
        print("No README.md files found")
        return
    for f in files:
        process_file(f, apply=args.apply)


if __name__ == "__main__":
    main()
