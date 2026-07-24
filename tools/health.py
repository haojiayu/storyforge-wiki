#!/usr/bin/env python3
"""Deterministic structural health checks for Novel World Wiki."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"

STUB_THRESHOLD_CHARS = 120
META_EXCLUDE = {"index.md", "log.md", "lint-report.md", "health-report.md"}


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def all_pages() -> list[Path]:
    return [p for p in WIKI_DIR.rglob("*.md") if p.name not in META_EXCLUDE]


def strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        idx = content.find("\n---", 3)
        if idx != -1:
            return content[idx + 4 :].strip()
    return content.strip()


def empty_or_stub(pages: list[Path]) -> list[dict]:
    out = []
    for p in pages:
        body = strip_frontmatter(read_file(p))
        if len(body) < STUB_THRESHOLD_CHARS:
            out.append(
                {
                    "path": str(p.relative_to(REPO_ROOT)),
                    "body_bytes": len(body),
                    "status": "empty" if len(body) == 0 else "stub",
                }
            )
    return sorted(out, key=lambda item: item["body_bytes"])


def parse_index_links(index_content: str) -> set[str]:
    return set(re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", index_content))


def index_sync(pages: list[Path]) -> dict:
    index_links = parse_index_links(read_file(INDEX_FILE))
    index_paths = {(WIKI_DIR / rel).resolve() for rel in index_links if rel != "overview.md"}
    disk_paths = {p.resolve() for p in pages if p.name != "overview.md"}
    return {
        "in_index_not_on_disk": [str(p.relative_to(REPO_ROOT)) for p in sorted(index_paths - disk_paths) if REPO_ROOT in p.parents],
        "on_disk_not_in_index": [str(p.relative_to(REPO_ROOT)) for p in sorted(disk_paths - index_paths)],
    }


def log_coverage() -> list[str]:
    log = read_file(LOG_FILE).lower()
    tracked_dirs = {"sources", "chapters"}
    missing = []
    for page in all_pages():
        if page.parent.name not in tracked_dirs:
            continue
        key = page.stem.lower().replace("-", " ")
        if key not in log:
            missing.append(str(page.relative_to(REPO_ROOT)))
    return missing


def run_health() -> dict:
    pages = all_pages()
    return {
        "date": date.today().isoformat(),
        "total_pages": len(pages),
        "empty_or_stub": empty_or_stub(pages),
        "index_sync": index_sync(pages),
        "log_coverage_missing": log_coverage(),
    }


def format_report(results: dict) -> str:
    lines = [
        f"# 世界观 Wiki 健康报告 — {results['date']}",
        "",
        f"共扫描 {results['total_pages']} 个页面。",
        "",
        f"## 空页/存根（{len(results['empty_or_stub'])}）",
    ]
    if results["empty_or_stub"]:
        for item in results["empty_or_stub"]:
            lines.append(f"- `{item['path']}` （{item['status']}，{item['body_bytes']} 字节）")
    else:
        lines.append("- 无")
    lines.append("")
    stale = results["index_sync"]["in_index_not_on_disk"]
    missing = results["index_sync"]["on_disk_not_in_index"]
    lines.append(f"## 索引同步（{len(stale) + len(missing)}）")
    lines.append("### 索引失效")
    lines.extend([f"- `{item}`" for item in stale] or ["- 无"])
    lines.append("### 索引缺失")
    lines.extend([f"- `{item}`" for item in missing] or ["- 无"])
    lines.append("")
    lines.append(f"## 日志覆盖缺口（{len(results['log_coverage_missing'])}）")
    lines.extend([f"- `{item}`" for item in results["log_coverage_missing"]] or ["- 无"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行确定性健康检查")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = run_health()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = format_report(results)
        print(report)
        if args.save:
            out = WIKI_DIR / "health-report.md"
            out.write_text(report, encoding="utf-8")
            print(f"\n已保存：{out.relative_to(REPO_ROOT)}")
