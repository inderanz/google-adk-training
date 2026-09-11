#!/usr/bin/env python3
"""Run the teacher updater across all markdown files in a target tree.

This is the operational entry point for on-demand refreshes and scheduled CI runs.
It can preview or apply updates across the entire training curriculum, and writes a
machine-readable summary of what changed.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Iterable, List

from teacher_updater import find_markdown_files, process_markdown


def iter_markdown_files(path: Path) -> List[Path]:
    files = find_markdown_files(path)
    return sorted({p.resolve() for p in files if p.exists() and p.suffix.lower() == ".md"})


def apply_updates(path: Path, annotate: bool, refs: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = process_markdown(original, do_annotate=annotate, do_refs=refs)
    if original == updated:
        return False

    bak = path.with_suffix(path.suffix + ".bak")
    if bak.exists():
        bak.unlink()
    path.replace(bak)
    bak.write_text(updated, encoding="utf-8")
    bak.replace(path)
    return True


def write_summary(summary_path: Path, changed: List[Path], total_files: int, applied: bool) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Teacher Updater Summary",
        "",
        f"Generated: {timestamp}",
        "",
        f"Files scanned: {total_files}",
        f"Files updated: {len(changed)}",
        f"Mode: {'applied' if applied else 'preview'}",
        "",
    ]

    if changed:
        lines.append("## Updated files")
        lines.extend(f"- {p.as_posix()}" for p in changed)
    else:
        lines.append("## Updated files")
        lines.append("- None")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh all training markdown files with the teacher-updater pattern.")
    parser.add_argument("--path", default="training", help="Directory or file to scan (default: training)")
    parser.add_argument("--annotate", action="store_true", default=True, help="Insert teacher notes before fenced code blocks")
    parser.add_argument("--refs", action="store_true", default=True, help="Append an Official References section when missing")
    parser.add_argument("--apply", action="store_true", help="Write the updates in-place; default is preview only")
    parser.add_argument("--summary-path", default=".github/teacher-updater/weekly-change-notes.md", help="Where to write the summary markdown")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}")
        return 1

    files = iter_markdown_files(root)
    if not files:
        print(f"No markdown files found under {root}")
        return 1

    changed: List[Path] = []
    for file_path in files:
        original = file_path.read_text(encoding="utf-8")
        updated = process_markdown(original, do_annotate=args.annotate, do_refs=args.refs)
        if original == updated:
            print(f"No changes for {file_path}")
            continue

        changed.append(file_path)
        print(f"Proposed changes for {file_path}")
        if args.apply:
            apply_updates(file_path, annotate=args.annotate, refs=args.refs)
            print(f"Applied changes to {file_path}")
        else:
            print("Preview mode — no files modified. Use --apply to write changes.")

    write_summary(Path(args.summary_path), changed, len(files), applied=args.apply)
    print(f"\nSummary written to {args.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
