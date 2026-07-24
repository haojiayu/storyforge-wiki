#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RECORD_RE = re.compile(
    r"^- Last integrated llm-upstream SHA: `(?P<sha>[0-9a-f]{40})`$",
    re.MULTILINE,
)


def read_integrated_sha(text: str) -> str:
    match = RECORD_RE.search(text)
    if not match:
        raise ValueError("UPSTREAMS.md has no valid llm-upstream SHA record")
    return match.group("sha")


def replace_integrated_sha(text: str, new_sha: str) -> str:
    if not SHA_RE.fullmatch(new_sha):
        raise ValueError("new SHA must be 40 lowercase hexadecimal characters")
    if not RECORD_RE.search(text):
        raise ValueError("UPSTREAMS.md has no valid llm-upstream SHA record")
    return RECORD_RE.sub(
        f"- Last integrated llm-upstream SHA: `{new_sha}`",
        text,
        count=1,
    )


def build_conflict_body(old_sha: str, new_sha: str, files: list[str]) -> str:
    for value in (old_sha, new_sha):
        if not SHA_RE.fullmatch(value):
            raise ValueError("conflict SHAs must be 40 lowercase hexadecimal characters")
    conflict_lines = "\n".join(f"- `{name}`" for name in sorted(set(files)))
    return (
        "## Automated upstream check found merge conflicts\n\n"
        f"- Last integrated SHA: `{old_sha}`\n"
        f"- Latest upstream SHA: `{new_sha}`\n\n"
        "### Conflicting files\n\n"
        f"{conflict_lines or '- No filenames reported'}\n\n"
        "`main` was not changed. Resolve these conflicts on a dedicated branch and "
        "submit a reviewed pull request.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    current = subparsers.add_parser("current")
    current.add_argument("--file", type=Path, required=True)

    update = subparsers.add_parser("update")
    update.add_argument("--file", type=Path, required=True)
    update.add_argument("--sha", required=True)

    conflict = subparsers.add_parser("conflict-body")
    conflict.add_argument("--old-sha", required=True)
    conflict.add_argument("--new-sha", required=True)
    conflict.add_argument("--files-file", type=Path, required=True)
    conflict.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "current":
        print(read_integrated_sha(args.file.read_text(encoding="utf-8")))
    elif args.command == "update":
        text = args.file.read_text(encoding="utf-8")
        args.file.write_text(replace_integrated_sha(text, args.sha), encoding="utf-8")
    else:
        files = args.files_file.read_text(encoding="utf-8").splitlines()
        args.output.write_text(
            build_conflict_body(args.old_sha, args.new_sha, files),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
